#!/usr/bin/env python3
"""Resolve a ClickHouse package specifier to a local executable binary path.

Supports:
  - local file path to a binary
  - http(s):// URL to a binary, .deb, or .tgz
  - docker://image[:tag]  (copies /usr/bin/clickhouse out of the image)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def _chmod_x(path: Path) -> Path:
    path.chmod(path.stat().st_mode | 0o111)
    return path


def from_local(path: str, out_dir: Path) -> Path:
    src = Path(path).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"binary not found: {src}")
    dest = out_dir / "clickhouse"
    shutil.copy2(src, dest)
    return _chmod_x(dest)


def from_url(url: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = url.rstrip("/").split("/")[-1] or "download"
    download = out_dir / name
    print(f"Downloading {url} -> {download}", flush=True)
    urllib.request.urlretrieve(url, download)
    if name.endswith(".deb"):
        return from_deb(download, out_dir)
    if name.endswith(".tgz") or name.endswith(".tar.gz"):
        return from_tgz(download, out_dir)
    dest = out_dir / "clickhouse"
    if download.name != "clickhouse":
        shutil.move(str(download), dest)
    else:
        dest = download
    return _chmod_x(dest)


def from_deb(deb_path: Path, out_dir: Path) -> Path:
    extract = out_dir / "deb_extract"
    extract.mkdir(parents=True, exist_ok=True)
    _run(["dpkg-deb", "-x", str(deb_path), str(extract)])
    candidates = list(extract.rglob("clickhouse"))
    if not candidates:
        raise FileNotFoundError(f"no clickhouse binary found in {deb_path}")
    # Prefer usr/bin/clickhouse
    preferred = [p for p in candidates if p.name == "clickhouse" and "bin" in str(p)]
    src = preferred[0] if preferred else candidates[0]
    dest = out_dir / "clickhouse"
    shutil.copy2(src, dest)
    return _chmod_x(dest)


def from_tgz(tgz_path: Path, out_dir: Path) -> Path:
    extract = out_dir / "tgz_extract"
    extract.mkdir(parents=True, exist_ok=True)
    extract_root = extract.resolve()
    with tarfile.open(tgz_path, "r:gz") as tf:
        for member in tf.getmembers():
            # Reject absolute paths and .. traversal (tar-slip).
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise RuntimeError(f"unsafe tar member path: {member.name!r}")
            dest = (extract / member.name).resolve()
            if dest != extract_root and not str(dest).startswith(str(extract_root) + os.sep):
                raise RuntimeError(f"unsafe tar member path: {member.name!r}")
        tf.extractall(extract)
    candidates = list(extract.rglob("clickhouse"))
    if not candidates:
        raise FileNotFoundError(f"no clickhouse binary found in {tgz_path}")
    preferred = [p for p in candidates if p.name == "clickhouse" and "bin" in str(p)]
    src = preferred[0] if preferred else candidates[0]
    dest = out_dir / "clickhouse"
    shutil.copy2(src, dest)
    return _chmod_x(dest)


def from_docker(spec: str, out_dir: Path) -> Path:
    # docker://image:tag
    image = spec[len("docker://") :]
    print(f"Pulling {image}", flush=True)
    _run(["docker", "pull", image])
    cid = _run(
        ["docker", "create", image], capture_output=True
    ).stdout.strip()
    try:
        dest = out_dir / "clickhouse"
        out_dir.mkdir(parents=True, exist_ok=True)
        _run(["docker", "cp", f"{cid}:/usr/bin/clickhouse", str(dest)])
        return _chmod_x(dest)
    finally:
        _run(["docker", "rm", "-f", cid], capture_output=True)


def resolve(package: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if package.startswith("docker://"):
        return from_docker(package, out_dir)
    if package.startswith(("http://", "https://")):
        return from_url(package, out_dir)
    return from_local(package, out_dir)


# ELF e_machine values (little-endian ELF)
_EM_X86_64 = 62
_EM_AARCH64 = 183

_HOST_TO_ELF = {
    "x86_64": _EM_X86_64,
    "amd64": _EM_X86_64,
    "aarch64": _EM_AARCH64,
    "arm64": _EM_AARCH64,
}

_ELF_NAME = {
    _EM_X86_64: "x86_64",
    _EM_AARCH64: "aarch64",
}


def elf_machine(path: Path) -> int | None:
    """Return ELF e_machine, or None if not a recognizable ELF."""
    with path.open("rb") as f:
        hdr = f.read(20)
    if len(hdr) < 20 or hdr[:4] != b"\x7fELF":
        return None
    return int.from_bytes(hdr[18:20], "little")


def assert_binary_matches_host(path: Path) -> None:
    """Fail fast if the ClickHouse binary cannot run on this host (e.g. arm64 on x86)."""
    host = os.uname().machine
    expected = _HOST_TO_ELF.get(host)
    if expected is None:
        print(f"WARNING: unknown host arch {host!r}; skipping binary arch check", flush=True)
        return
    machine = elf_machine(path)
    if machine is None:
        print(f"WARNING: {path} is not ELF; skipping binary arch check", flush=True)
        return
    if machine != expected:
        got = _ELF_NAME.get(machine, f"e_machine={machine}")
        want = _ELF_NAME[expected]
        raise SystemExit(
            f"ClickHouse binary arch mismatch: binary is {got}, host is {want} ({host}). "
            f"Use an amd64/x86_64 package on this machine (or arm64 on aarch64). "
            f"Without this check Jepsen would hang for many minutes waiting for Keeper/server "
            f"that never start (Exec format error)."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent.parent / "pkg"),
        help="Directory to place the resolved clickhouse binary",
    )
    args = parser.parse_args()
    path = resolve(args.package, Path(args.out_dir))
    assert_binary_matches_host(path)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
