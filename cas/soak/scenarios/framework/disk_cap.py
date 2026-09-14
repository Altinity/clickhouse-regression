"""Keep the scenario suite from filling the host disk (ARM 180G, 2026-08-22).

The soak driver already has `--max-pool-gb` (throttles inserts). Scenario cards do not go through
that loop, so a single card (S13 on ARM) grew the RustFS volume to ~157 GB, `df` hit 0, and the
suite died mid-fsck.

This guard polls physical pool bytes (`du` inside the RustFS container) and host free space. On
trip it `docker compose down -v` so the next card can start. The tripped card is INCONCLUSIVE, not
FAIL — the cap is a host budget, not a CAS oracle.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

from soak.pool import pool_size

GB = 1024 ** 3
CA_SOAK_DIR = Path(__file__).resolve().parents[2]

# Defaults: soak phase-3 uses 40 GB; 25 GB free leaves room for images, logs, and OS on a 180 GB box.
DEFAULT_MAX_POOL_GB = 40.0
DEFAULT_MIN_FREE_DISK_GB = 25.0

_RUSTFS = ("ca-soak-rustfs1-1", "ca-s41-rustfs1-1")

_pause = threading.Event()
_guard: "DiskGuard | None" = None


def trip_reason(pool_bytes, free_bytes, max_pool_bytes, min_free_bytes) -> str | None:
    """Pure policy. None = under budget. A string is the trip reason."""
    if max_pool_bytes and pool_bytes is not None and pool_bytes > max_pool_bytes:
        return (f"pool {pool_bytes / GB:.1f} GB exceeds --max-pool-gb "
                f"{max_pool_bytes / GB:.1f} GB")
    if min_free_bytes and free_bytes is not None and free_bytes < min_free_bytes:
        return (f"host free {free_bytes / GB:.1f} GB is under --min-free-disk-gb "
                f"{min_free_bytes / GB:.1f} GB")
    return None


def host_free_bytes(path: str = "/") -> int:
    return shutil.disk_usage(path).free


def rustfs_pool_bytes(timeout_s: float = 20.0) -> int | None:
    """Sum physical pool bytes across soak rustfs containers. None if nothing could be probed."""
    total = 0
    any_ok = False
    saved = os.environ.get("CA_SOAK_RUSTFS_CONTAINER")
    try:
        for container in _RUSTFS:
            os.environ["CA_SOAK_RUSTFS_CONTAINER"] = container
            _, nbytes = pool_size(timeout_s=timeout_s)
            if nbytes is not None:
                total += nbytes
                any_ok = True
    finally:
        if saved is None:
            os.environ.pop("CA_SOAK_RUSTFS_CONTAINER", None)
        else:
            os.environ["CA_SOAK_RUSTFS_CONTAINER"] = saved
    return total if any_ok else None


def prune_host_logs(logs_dir: Path | None = None, *, keep_predown: int = 2,
                    keep_archive: int = 4) -> dict:
    """Drop host-side leftovers that survive `down -v`.

    `logs/prev_*` is a second copy of server logs already tarred as `_archive_*.tgz`. Predown dumps
    and archive tarballs accumulate one per card. Keeping a couple of each is enough to debug the
    card that just tripped the cap.
    """
    logs = Path(logs_dir) if logs_dir else CA_SOAK_DIR / "logs"
    removed = {"prev": 0, "predown": 0, "archive": 0}
    if not logs.is_dir():
        return removed
    for p in logs.glob("prev_*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            removed["prev"] += 1
    predown = logs / "predown"
    if predown.is_dir():
        labels = {}
        for node_dir in predown.iterdir():
            if not node_dir.is_dir():
                continue
            for child in node_dir.iterdir():
                if child.is_dir():
                    labels[child.name] = max(labels.get(child.name, 0), child.stat().st_mtime)
        stale = sorted(labels, key=labels.get)[:-keep_predown] if keep_predown else list(labels)
        for lab in stale:
            for node_dir in predown.iterdir():
                target = node_dir / lab
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                    removed["predown"] += 1
    archives = sorted(logs.glob("_archive_*.tgz"), key=lambda p: p.stat().st_mtime)
    for p in archives[:-keep_archive] if keep_archive else archives:
        try:
            p.unlink()
            removed["archive"] += 1
        except OSError:
            pass
    return removed


def paused():
    """Context manager: do not trip (or reclaim) while compose is already going down/up."""
    return _Pause()


class _Pause:
    def __enter__(self):
        _pause.set()
        return self

    def __exit__(self, *exc):
        _pause.clear()
        return False


def current() -> "DiskGuard | None":
    return _guard


def reclaim_volumes(log_fn=print) -> None:
    """Wipe ca-soak and ca-s41 volumes. Best-effort; must not raise into the watchdog thread."""
    cmds = (
        ["docker", "compose", "-p", "ca-s41", "-f", "docker-compose-s41.yml",
         "down", "-v", "--remove-orphans"],
        ["docker", "compose", "-p", "ca-soak", "-f", "docker-compose-10replicas.yml",
         "down", "-v", "--remove-orphans"],
    )
    for argv in cmds:
        log_fn(f"[disk-cap] $ {' '.join(argv)}")
        try:
            subprocess.run(argv, cwd=str(CA_SOAK_DIR), capture_output=True, text=True, timeout=180)
        except Exception as e:
            log_fn(f"[disk-cap] down raised: {e}")
    prune_host_logs()


class DiskGuard:
    """Background poll of pool size + host free space. One per suite."""

    def __init__(self, *, max_pool_gb: float, min_free_disk_gb: float,
                 interval_s: float = 20.0, log_fn=print):
        self.max_pool_bytes = int(max_pool_gb * GB) if max_pool_gb else 0
        self.min_free_bytes = int(min_free_disk_gb * GB) if min_free_disk_gb else 0
        self.interval_s = interval_s
        self.log_fn = log_fn
        self.reason = ""
        self._pending = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_trip_mono = 0.0

    def start(self) -> None:
        global _guard
        _guard = self
        self._thread = threading.Thread(target=self._loop, name="scenario-disk-cap", daemon=True)
        self._thread.start()
        self.log_fn(
            f"[disk-cap] max_pool_gb={self.max_pool_bytes / GB:.1f} "
            f"min_free_disk_gb={self.min_free_bytes / GB:.1f} interval={self.interval_s:.0f}s")

    def stop(self) -> None:
        global _guard
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval_s + 5)
        if _guard is self:
            _guard = None

    def consume_trip(self) -> str | None:
        """If the guard tripped during the current card, return the reason once."""
        if not self._pending.is_set():
            return None
        self._pending.clear()
        return self.reason or "disk/pool cap"

    def poll_once(self) -> str | None:
        if _pause.is_set():
            return None
        pool = rustfs_pool_bytes()
        free = host_free_bytes()
        reason = trip_reason(pool, free, self.max_pool_bytes, self.min_free_bytes)
        if reason:
            self._trip(reason)
        return reason

    def _trip(self, reason: str) -> None:
        now = time.monotonic()
        if now - self._last_trip_mono < 45:
            return
        self._last_trip_mono = now
        self.reason = reason
        self._pending.set()
        self.log_fn(f"[disk-cap] TRIP: {reason} — compose down -v to reclaim volumes")
        reclaim_volumes(self.log_fn)
        self.log_fn(f"[disk-cap] reclaim done; host free {host_free_bytes() / GB:.1f} GB")

    def _loop(self) -> None:
        while not self._stop.wait(self.interval_s):
            try:
                self.poll_once()
            except Exception as e:
                self.log_fn(f"[disk-cap] poll raised: {e}")
