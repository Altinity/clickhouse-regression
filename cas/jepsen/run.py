#!/usr/bin/env python3
"""Run CAS server Jepsen on one host with privileged Docker SSH nodes + RustFS.

Example:
  python3 cas/jepsen/run.py --package /path/to/clickhouse --minutes 5 --test-count 8
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
JEPSEN = ROOT / "jepsen.clickhouse"
PKG = ROOT / "pkg"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def ensure_compose_project() -> str:
    project = os.environ.get("COMPOSE_PROJECT_NAME", "").strip()
    if not project:
        project = f"jepsen-local-{os.getpid()}"
        os.environ["COMPOSE_PROJECT_NAME"] = project
    return project


def docker_bridge_gateway(project: str) -> str:
    network = f"{project}_jepsen-net"
    try:
        out = subprocess.check_output(
            [
                "docker",
                "network",
                "inspect",
                network,
                "-f",
                "{{(index .IPAM.Config 0).Gateway}}",
            ],
            text=True,
        ).strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass
    return "172.18.0.1"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003
        return


def start_http_server(
    directory: Path, port: int, bind_host: str = "127.0.0.1"
) -> tuple[socketserver.TCPServer, int]:
    """Serve PKG to Jepsen nodes. Bind only to bind_host (Docker bridge gateway)."""
    handler = functools.partial(QuietHandler, directory=str(directory))

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    last_err: OSError | None = None
    for candidate in [port, *range(port + 1, port + 50)]:
        try:
            httpd = ReusableTCPServer((bind_host, candidate), handler)
            break
        except OSError as e:
            last_err = e
            httpd = None  # type: ignore
    else:
        raise OSError(
            f"could not bind HTTP server on {bind_host} near port {port}: {last_err}"
        )
    import threading

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def clear_store(store_dir: Path) -> None:
    if store_dir.exists():
        print(f"Clearing previous Jepsen store at {store_dir}", flush=True)
        shutil.rmtree(store_dir)


def parse_results(store_dir: Path, expected: int) -> int:
    """Fail on :valid? false/:unknown, missing results, or count != expected."""
    results = sorted(store_dir.glob("clickhouse-server-*/20*/results.edn"))
    seen = set()
    summaries = []
    failed = passed = unknown = 0
    for path in results:
        real = path.resolve()
        if real in seen:
            continue
        seen.add(real)
        text = path.read_text(errors="replace")
        matches = list(re.finditer(r"^ :valid\?\s*(true|false|:unknown)\s*$", text, re.M))
        if not matches:
            matches = list(re.finditer(r":valid\?\s*(true|false|:unknown)", text))
        if not matches:
            continue
        val = matches[-1].group(1)
        name = path.parent.parent.name
        summaries.append(f"{name} ({path.parent.name}): valid? {val}")
        if val == "true":
            passed += 1
        elif val == "false":
            failed += 1
        else:
            unknown += 1

    print("\n=== Jepsen CAS results ===", flush=True)
    for s in summaries:
        print(s, flush=True)
    print(
        f"passed={passed} failed={failed} unknown={unknown} expected={expected}",
        flush=True,
    )
    if failed or unknown or passed != expected or not summaries:
        return 2
    return 0


def ensure_lein() -> None:
    try:
        subprocess.run(["lein", "version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise SystemExit(
            "lein is required on the control host (install Leiningen + JVM). "
            f"Detail: {e}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, help="docker://, https://, or local binary")
    parser.add_argument("--minutes", type=float, default=5, help="Per-scenario time-limit in minutes")
    parser.add_argument("--test-count", type=int, default=8)
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--rate", type=float, default=10)
    parser.add_argument("--http-port", type=int, default=8765)
    parser.add_argument("--skip-teardown", action="store_true")
    parser.add_argument("--skip-bringup", action="store_true")
    args = parser.parse_args()

    ensure_lein()
    project = ensure_compose_project()
    print(f"COMPOSE_PROJECT_NAME={project}", flush=True)
    time_limit = max(1, int(args.minutes * 60))

    binary = Path(
        subprocess.check_output(
            [
                sys.executable,
                str(SCRIPTS / "resolve_binary.py"),
                "--package",
                args.package,
                "--out-dir",
                str(PKG),
            ],
            text=True,
        )
        .strip()
        .splitlines()[-1]
    )
    print(f"Resolved binary: {binary}", flush=True)

    PKG.mkdir(parents=True, exist_ok=True)
    served = PKG / "clickhouse"
    if binary.resolve() != served.resolve():
        shutil.copy2(binary, served)
    served.chmod(served.stat().st_mode | 0o111)

    clear_store(JEPSEN / "store")

    httpd = None
    log_path = ROOT / "jepsen_run.log"
    try:
        if not args.skip_bringup:
            run(["bash", str(SCRIPTS / "bringup.sh")])
        elif not (ROOT / "nodes.txt").is_file():
            raise SystemExit("--skip-bringup requires nodes.txt from a prior bringup")

        gateway = docker_bridge_gateway(project)
        # Bind only on the Docker bridge gateway so containers can fetch the
        # binary without exposing it on all host interfaces.
        httpd_pair = start_http_server(PKG, args.http_port, bind_host=gateway)
        http_port = httpd_pair[1]
        httpd = httpd_pair[0]
        source = f"http://{gateway}:{http_port}/clickhouse"
        print(f"clickhouse-source: {source}", flush=True)

        keeper = (ROOT / "keeper.txt").read_text().strip()
        cmd = [
            "lein",
            "run",
            "server",
            "test-all",
            "--nodes-file",
            str(ROOT / "nodes.txt"),
            "--keeper",
            keeper,
            "--username",
            "root",
            "--password",
            "",
            "--ssh-private-key",
            str(ROOT / "id_rsa"),
            # Jepsen 0.3.x: --strict-host-key-checking is a boolean flag (default false).
            # Do NOT pass it; presence would force checking ON.
            "--time-limit",
            str(time_limit),
            "--concurrency",
            str(args.concurrency),
            "-r",
            str(args.rate),
            "--clickhouse-source",
            source,
            "--reuse-binary",
            "--test-count",
            str(args.test_count),
        ]
        print("+", " ".join(cmd), flush=True)
        with open(log_path, "w") as logf:
            proc = subprocess.Popen(
                cmd,
                cwd=str(JEPSEN),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                logf.write(line)
            proc.wait()
            lein_rc = proc.returncode

        parse_rc = parse_results(JEPSEN / "store", args.test_count)
        if parse_rc != 0:
            exit_code = parse_rc
        elif lein_rc != 0:
            exit_code = lein_rc
        else:
            exit_code = 0
        print(f"JEPSEN_EXIT_CODE={exit_code}", flush=True)
        return exit_code
    finally:
        if httpd is not None:
            httpd.shutdown()
        # Always attempt teardown: bringup may have partially created the stack
        # before failing (compose up happens before SSH/RustFS readiness checks).
        if not args.skip_teardown:
            subprocess.run(["bash", str(SCRIPTS / "teardown.sh")], check=False)


if __name__ == "__main__":
    sys.exit(main())
