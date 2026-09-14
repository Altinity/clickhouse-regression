#!/usr/bin/env python3
"""Bring up a clickhouse-regression docker-compose env without running tests.

Mirrors helpers.cluster.Cluster: sets CLICKHOUSE_TESTS_* vars, builds the
clickhouse-regression image, runs docker-compose, and starts clickhouse-server
inside each ClickHouse container (compose entrypoint is `tail -f /dev/null`).

Usage:
    compose_env.py up --dir cas --clickhouse docker://...
    compose_env.py client --dir cas
    compose_env.py down --dir cas
    compose_env.py list
"""
from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


ENV_DIR_RE = re.compile(r"^.+_env(_arm64)?$")
SKIP_SERVICES = {"all_services_ready"}

DEFAULT_MINIO_USER = "admin"
DEFAULT_MINIO_PASSWORD = "password"
DEFAULT_ZOOKEEPER_VERSION = "3.8.4"


def cpu_arch() -> str:
    arch = platform.processor() or platform.machine() or ""
    if arch in ("arm", "arm64", "aarch64"):
        return "aarch64"
    return arch or "x86_64"


def find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "helpers" / "cluster.py").is_file():
            return candidate
    sys.exit("could not find clickhouse-regression root (helpers/cluster.py)")


REPO_ROOT = find_repo_root()


def is_env_dir(path: Path) -> bool:
    return bool(ENV_DIR_RE.match(path.name)) and (path / "docker-compose.yml").is_file()


def iter_env_dirs() -> list[Path]:
    found = []
    for compose in REPO_ROOT.rglob("docker-compose.yml"):
        parent = compose.parent
        if is_env_dir(parent):
            found.append(parent)
    return sorted(found)


def find_configs_dir(env_dir: Path) -> Path:
    """Suite directory that Cluster would use as configs_dir / CLICKHOUSE_TESTS_DIR."""
    found_configs = None
    p = env_dir.parent
    while p != p.parent and p != REPO_ROOT.parent:
        if found_configs is None and (p / "configs").is_dir():
            found_configs = p
        if (p / "regression.py").is_file() or list(p.glob("*regression*.py")):
            return found_configs or p
        p = p.parent
    if found_configs is not None:
        return found_configs
    return env_dir.parent


def apply_arch_suffix(env_dir: Path) -> Path:
    if cpu_arch() != "aarch64":
        return env_dir
    if env_dir.name.endswith("_arm64"):
        return env_dir
    arm = env_dir.with_name(env_dir.name + "_arm64")
    if arm.is_dir():
        return arm
    return env_dir


def resolve_env_dir(token: str | None) -> Path:
    """Resolve suite name, env folder, or cwd to an env directory."""
    cwd = Path.cwd().resolve()

    if not token:
        if is_env_dir(cwd):
            return apply_arch_suffix(cwd)
        name = cwd.name
        for candidate in (cwd / f"{name}_env", cwd / f"{name}_env_arm64"):
            if is_env_dir(candidate):
                return apply_arch_suffix(candidate)
        sys.exit(
            "not inside an env folder or suite directory; pass --dir "
            "(e.g. cas, cas/cas_env, iceberg)"
        )

    raw = Path(token).expanduser()
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend(
            [
                (cwd / raw).resolve(),
                (REPO_ROOT / raw).resolve(),
            ]
        )
        if "/" not in token and "\\" not in token:
            candidates.extend(
                [
                    REPO_ROOT / token / f"{token}_env",
                    REPO_ROOT / token / f"{token}_env_arm64",
                ]
            )

    seen: set[Path] = set()
    for cand in candidates:
        if cand in seen:
            continue
        seen.add(cand)
        if is_env_dir(cand):
            return apply_arch_suffix(cand)
        if cand.is_dir():
            name = cand.name
            for nested in (cand / f"{name}_env", cand / f"{name}_env_arm64"):
                if is_env_dir(nested):
                    return apply_arch_suffix(nested)

    sys.exit(f"could not resolve env folder from {token!r}")


def compose_services(compose_file: Path) -> list[str]:
    """Top-level service names from a compose YAML (no docker-compose required)."""
    services: list[str] = []
    in_services = False
    for line in compose_file.read_text().splitlines():
        if not in_services:
            if re.match(r"^services:\s*(#.*)?$", line):
                in_services = True
            continue
        if line and not line[0].isspace() and not line.startswith("#"):
            break
        match = re.match(r"^  ([A-Za-z0-9][A-Za-z0-9_-]*):\s*(#.*)?$", line)
        if match:
            name = match.group(1)
            if name not in SKIP_SERVICES:
                services.append(name)
    return services


def nodes_from_services(services: list[str]) -> dict[str, tuple[str, ...]]:
    clickhouse = tuple(s for s in services if s.startswith("clickhouse"))
    zookeeper = tuple(s for s in services if s.startswith("zookeeper"))
    nodes: dict[str, tuple[str, ...]] = {"clickhouse": clickhouse}
    if zookeeper:
        nodes["zookeeper"] = zookeeper
    return nodes


def parse_kv(items: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items or []:
        if "=" not in item:
            sys.exit(f"expected KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        out[key] = value
    return out


def compose_environ(
    args: argparse.Namespace, configs_dir: Path
) -> dict[str, str]:
    extra = parse_kv(getattr(args, "set_kv", None))
    if getattr(args, "use_keeper", False):
        extra.setdefault("CLICKHOUSE_TESTS_COORDINATOR", "keeper")
    env = {
        "COMPOSE_HTTP_TIMEOUT": "600",
        "CLICKHOUSE_TESTS_DIR": str(configs_dir),
        "CLICKHOUSE_TESTS_COORDINATOR": extra.get(
            "CLICKHOUSE_TESTS_COORDINATOR", "zookeeper"
        ),
        "CLICKHOUSE_TESTS_ZOOKEEPER_VERSION": extra.get(
            "CLICKHOUSE_TESTS_ZOOKEEPER_VERSION", DEFAULT_ZOOKEEPER_VERSION
        ),
        "CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME": extra.get(
            "CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME", "placeholder"
        ),
        "CLICKHOUSE_TESTS_KEEPER_DOCKER_IMAGE": extra.get(
            "CLICKHOUSE_TESTS_KEEPER_DOCKER_IMAGE",
            extra.get("CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME", "placeholder"),
        ),
        "CLICKHOUSE_TESTS_SERVER_BIN_PATH": extra.get(
            "CLICKHOUSE_TESTS_SERVER_BIN_PATH", ""
        ),
        "CLICKHOUSE_TESTS_KEEPER_BIN_PATH": extra.get(
            "CLICKHOUSE_TESTS_KEEPER_BIN_PATH", ""
        ),
        "CLICKHOUSE_TESTS_BASE_OS": extra.get("CLICKHOUSE_TESTS_BASE_OS", ""),
        "CLICKHOUSE_TESTS_BASE_OS_NAME": extra.get(
            "CLICKHOUSE_TESTS_BASE_OS_NAME", "clickhouse"
        ),
        "MINIO_ROOT_USER": extra.get("MINIO_ROOT_USER", DEFAULT_MINIO_USER),
        "MINIO_ROOT_PASSWORD": extra.get(
            "MINIO_ROOT_PASSWORD", DEFAULT_MINIO_PASSWORD
        ),
    }
    env.update(extra)
    return env


def compose_argv(env_dir: Path, compose_file: str, args: list[str]) -> list[str]:
    return [
        "docker-compose",
        "--log-level",
        "ERROR",
        "--ansi",
        "never",
        "--project-directory",
        str(env_dir),
        "--file",
        str(env_dir / compose_file),
        *args,
    ]


def run_compose(
    env_dir: Path,
    compose_file: str,
    args: list[str],
    environ: dict[str, str],
    check: bool = True,
) -> subprocess.CompletedProcess:
    merged = os.environ.copy()
    merged.update(environ)
    proc = subprocess.run(compose_argv(env_dir, compose_file, args), env=merged)
    if check and proc.returncode != 0:
        sys.exit(proc.returncode)
    return proc


def target_from_args(args: argparse.Namespace) -> tuple[Path, Path, str]:
    env_dir = resolve_env_dir(getattr(args, "dir", None))
    configs_dir = (
        Path(args.configs_dir).resolve()
        if getattr(args, "configs_dir", None)
        else find_configs_dir(env_dir)
    )
    compose_file = getattr(args, "file", None) or "docker-compose.yml"
    if not (env_dir / compose_file).is_file():
        sys.exit(f"compose file not found: {env_dir / compose_file}")
    return env_dir, configs_dir, compose_file


def first_clickhouse(env_dir: Path, compose_file: str, service: str | None) -> str:
    if service:
        return service
    clickhouses = [
        s
        for s in compose_services(env_dir / compose_file)
        if s.startswith("clickhouse")
    ]
    if not clickhouses:
        sys.exit(f"no clickhouse* service in {env_dir / compose_file}")
    return clickhouses[0]


def env_token(args: argparse.Namespace, env_dir: Path) -> str:
    if args.dir:
        return args.dir
    try:
        return str(env_dir.relative_to(REPO_ROOT))
    except ValueError:
        return str(env_dir)


def cmd_list(_args: argparse.Namespace) -> None:
    arch = cpu_arch()
    suffix = "_arm64" if arch == "aarch64" else ""
    rows = []
    for path in iter_env_dirs():
        rel = path.relative_to(REPO_ROOT)
        marker = ""
        if suffix and path.name.endswith(suffix):
            marker = "  [this host]"
        elif not suffix and not path.name.endswith("_arm64"):
            marker = "  [this host]"
        rows.append(f"{rel}{marker}")
    print("\n".join(rows))


def cmd_down(args: argparse.Namespace) -> None:
    env_dir, configs_dir, compose_file = target_from_args(args)
    run_compose(
        env_dir,
        compose_file,
        ["down", "-v", "--remove-orphans", "--timeout", "60"],
        compose_environ(args, configs_dir),
    )


def cmd_client(args: argparse.Namespace) -> None:
    env_dir, configs_dir, compose_file = target_from_args(args)
    service = first_clickhouse(env_dir, compose_file, args.service)
    run_compose(
        env_dir,
        compose_file,
        ["exec", service, "clickhouse", "client"],
        compose_environ(args, configs_dir),
    )


def default_clickhouse_path() -> str | None:
    env_path = os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH")
    if env_path:
        return env_path
    if Path("/usr/bin/clickhouse").exists():
        return "/usr/bin/clickhouse"
    return None


def check_package_arch(clickhouse_path: str) -> None:
    """Fail fast if a .deb URL/path is the wrong CPU architecture for this host."""
    host = cpu_arch()
    text = clickhouse_path.lower()
    package_arch = None
    if re.search(r"(?:^|[_/-])(?:arm64|aarch64)(?:[_./-]|$)", text):
        package_arch = "aarch64"
    elif re.search(r"(?:^|[_/-])(?:amd64|x86_64)(?:[_./-]|$)", text):
        package_arch = "x86_64"
    if package_arch is None or package_arch == host:
        return
    want = "amd64" if host == "x86_64" else "arm64"
    sys.exit(
        f"--clickhouse package is {package_arch}, this host is {host}. "
        f"Use the {want} build (e.g. build_amd_release / *_amd64.deb, "
        f"or build_arm_release / *_arm64.deb)."
    )


def cmd_up(args: argparse.Namespace) -> None:
    env_dir, configs_dir, compose_file = target_from_args(args)
    clickhouse_path = args.clickhouse or default_clickhouse_path()
    if not clickhouse_path:
        sys.exit("pass --clickhouse (docker://image, .deb/.tgz, or binary path)")
    check_package_arch(clickhouse_path)

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from testflows.core import Module, current

    from helpers.cluster import Cluster

    extra = parse_kv(args.set_kv)
    extra.setdefault("MINIO_ROOT_USER", DEFAULT_MINIO_USER)
    extra.setdefault("MINIO_ROOT_PASSWORD", DEFAULT_MINIO_PASSWORD)
    if args.use_keeper:
        extra["CLICKHOUSE_TESTS_COORDINATOR"] = "keeper"

    services = compose_services(env_dir / compose_file)
    cluster_nodes = nodes_from_services(services)

    saved_argv = sys.argv
    sys.argv = [saved_argv[0]]
    try:
        with Module("compose-up"):
            if args.clickhouse_version:
                current().context.clickhouse_version = args.clickhouse_version
            cluster = Cluster(
                local=True,
                clickhouse_path=clickhouse_path,
                as_binary=args.as_binary,
                base_os=args.base_os,
                keeper_path=args.keeper,
                zookeeper_version=args.zookeeper_version,
                use_keeper=args.use_keeper,
                configs_dir=str(configs_dir),
                docker_compose_project_dir=str(env_dir),
                docker_compose_file=compose_file,
                nodes=cluster_nodes,
                environ=extra,
                reuse_env=args.reuse_env,
                rm_instances_files=not args.reuse_env,
            )
            cluster.up()
    finally:
        sys.argv = saved_argv

    script = Path(__file__).resolve()
    token = env_token(args, env_dir)
    print()
    print("Cluster is up (left running; tests were not executed).")
    print(f"  env:       {cluster.docker_compose_project_dir}")
    print(f"  configs:   {configs_dir}")
    print(f"  instances: {configs_dir / '_instances'}")
    if cluster_nodes.get("clickhouse"):
        print(f"  nodes:     {', '.join(cluster_nodes['clickhouse'])}")
    print()
    print("Interactive client:")
    print(f"  {script} client --dir {token}")
    print()
    print("Tear down:")
    print(f"  {script} down --dir {token}")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dir",
        metavar="ENV",
        help="suite name or env folder (cas, cas/cas_env). Omit when cwd is the suite/env dir",
    )
    parser.add_argument(
        "--configs-dir",
        help="override CLICKHOUSE_TESTS_DIR (defaults to the suite directory)",
    )
    parser.add_argument(
        "--file",
        default="docker-compose.yml",
        help="compose file name inside the env folder (default: docker-compose.yml)",
    )
    parser.add_argument(
        "--set",
        dest="set_kv",
        action="append",
        metavar="KEY=VALUE",
        help="extra environment variable (repeatable)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Start a clickhouse-regression env-folder compose cluster without "
            "running regression.py, then open clickhouse client."
        )
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_up = sub.add_parser("up", help="build image, compose up, start ClickHouse")
    add_common_args(p_up)
    p_up.add_argument(
        "--clickhouse",
        "--clickhouse-binary-path",
        dest="clickhouse",
        default=os.getenv("CLICKHOUSE_TESTS_SERVER_BIN_PATH"),
        help="docker://image, package URL/path, or binary (same as regression.py)",
    )
    p_up.add_argument("--clickhouse-version", default=None)
    p_up.add_argument("--base-os", default=None)
    p_up.add_argument("--as-binary", action="store_true")
    p_up.add_argument("--keeper", default=None)
    p_up.add_argument("--zookeeper-version", default=None)
    p_up.add_argument("--use-keeper", action="store_true")
    p_up.add_argument(
        "--reuse-env",
        action="store_true",
        help="do not recreate containers or wipe _instances if already up",
    )
    p_up.set_defaults(func=cmd_up)

    p_down = sub.add_parser("down", help="docker-compose down -v --remove-orphans")
    add_common_args(p_down)
    p_down.set_defaults(func=cmd_down)

    p_client = sub.add_parser(
        "client", help="interactive clickhouse client on a node (default clickhouse1)"
    )
    add_common_args(p_client)
    p_client.add_argument(
        "-s",
        "--service",
        default=None,
        help="clickhouse* service (default: first clickhouse* node)",
    )
    p_client.set_defaults(func=cmd_client)

    p_list = sub.add_parser("list", help="list *_env / *_env_arm64 folders")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
