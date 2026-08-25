import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from soak.rng import splitmix64

class FaultTarget(str, Enum):
    CH1 = "ch1"
    CH2 = "ch2"
    BOTH = "both"
    RUSTFS = "rustfs"

class FaultAction(str, Enum):
    KILL = "kill"        # docker kill -s KILL (hard crash)
    RESTART = "restart"  # docker restart
    PAUSE = "pause"      # docker pause + unpause after duration (short freeze, 5..60s)
    # A LONG freeze of ONE replica (docker pause = cgroup freezer = SIGSTOP-equivalent for the whole
    # container; unpause = SIGCONT), held past the mount-lease TTL (30s) + GC fence margin (ttl/2=15s)
    # so the frozen replica's lease EXPIRES and the peer's GC leader fences it out. On unfreeze the
    # replica must detect the fence and self-remount (recovery path: project_ca_p31_mount_fence_recovery).
    # Never applied to BOTH replicas (the cluster must stay recoverable) or to RustFS.
    FREEZE_LONG = "freeze_long"

@dataclass(frozen=True)
class Fault:
    t_offset: int        # seconds from run start
    target: FaultTarget
    action: FaultAction
    duration_s: int      # for PAUSE: how long paused; for KILL: downtime before auto-restart

def _default_containers():
    """Resolve chaos targets from CA_SOAK_* env (helpers.cluster bridge) with upstream defaults."""
    import os
    return {
        FaultTarget.CH1: os.environ.get("CA_SOAK_NODE1_CONTAINER", "ca-soak-ch1-1"),
        FaultTarget.CH2: os.environ.get("CA_SOAK_NODE2_CONTAINER", "ca-soak-ch2-1"),
        FaultTarget.RUSTFS: os.environ.get("CA_SOAK_RUSTFS_CONTAINER", "ca-soak-rustfs1-1"),
    }

_TARGETS = [FaultTarget.CH1, FaultTarget.CH2, FaultTarget.BOTH, FaultTarget.RUSTFS]
# FREEZE_LONG is NOT in the uniform action pick: it is a rarer (~1/6) deterministic UPGRADE applied
# after the base pick (below), so the common fault mix stays kill/restart/short-pause and the cluster
# is not frozen for most of the run.
_ACTIONS = [FaultAction.KILL, FaultAction.RESTART, FaultAction.PAUSE]

def generate_chaos_schedule(seed: int, duration_s: int, mean_interval_s: int):
    """Deterministic fault schedule from a seed. Poisson-ish inter-arrival via splitmix64. Bounded so
    the cluster always stays recoverable (never a long simultaneous KILL of BOTH replicas).

    RustFS faults are scoped to GRACEFUL actions (`RESTART`/`PAUSE`) only — never `KILL`. This is a
    deliberate scoping of the chaos surface, not a workaround for a CA defect. See [[B145]]: a hard
    `docker kill -s KILL` of the RustFS container injects a transient post-restart read-visibility
    window (a `blobs/` key briefly returns `499 NoSuchKey` on the INSERT-dedup read path) that is an
    object-store recovery artifact of the `1.0.0-beta.8` test backend, NOT a CA durability defect.
    The decisive durability probe (write N objects -> `docker kill -s KILL` rustfs -> restart ->
    re-list/read-back) showed RustFS does NOT lose acked objects on a hard kill (0 acked-but-lost
    across 5 runs incl. continuous-write-mid-kill and kill-during-recovery), and the B145 capture had
    `fsck dangling=0` (no referenced blob was permanently missing) — both confirming the 499 was
    transient visibility, not loss. CA crash-recovery is about a ClickHouse SERVER crashing over a
    durable-enough store, so CH replicas KEEP `KILL`. The remaining open question — whether CA can
    reference a blob before the store has DURABLY acked it (an ordering bug) — cannot be cleanly
    tested against this beta store and must be re-tested against a crash-durable store
    (real S3 / MinIO-with-fsync); tracked as a B145 follow-up. The remap is deterministic: a
    RustFS+KILL slot becomes RustFS+RESTART, preserving schedule length/timing."""
    faults = []
    t = 0
    i = 0
    while True:
        r = splitmix64(seed ^ (i * 0x9E3779B1))
        # inter-arrival in [0.3, 1.7] * mean (deterministic, no floats-from-clock)
        gap = (mean_interval_s * (30 + (r % 140))) // 100
        t += max(1, gap)
        if t >= duration_s:
            break
        r2 = splitmix64(r)
        target = _TARGETS[(r2 >> 3) % len(_TARGETS)]
        action = _ACTIONS[(r2 >> 7) % len(_ACTIONS)]
        dur = 5 + ((r2 >> 11) % 56)   # 5..60s
        if target == FaultTarget.RUSTFS and action == FaultAction.KILL:
            # B145: never hard-kill the (non-crash-durable-for-this-purpose) test object store; a
            # graceful restart lets RustFS flush. Deterministic downgrade KILL -> RESTART.
            action = FaultAction.RESTART
        if target == FaultTarget.BOTH and action == FaultAction.KILL:
            dur = min(dur, 60)        # safety bound
        # Rare (~1/6) UPGRADE to a long single-replica freeze, held past the mount-lease TTL so the
        # frozen replica is GC-fenced and must self-remount on unfreeze. Must hit exactly ONE ClickHouse
        # replica: never BOTH (the cluster must stay recoverable — a peer keeps the shard live and does
        # the fencing), never RustFS (freezing the store is a different fault class). Duration 60..90s
        # reliably exceeds mount_lease_ttl (30s) + GC fence margin (ttl/2 = 15s).
        if ((r2 >> 9) % 6) == 0:
            action = FaultAction.FREEZE_LONG
            target = FaultTarget.CH1 if ((r2 >> 13) & 1) == 0 else FaultTarget.CH2
            dur = 60 + ((r2 >> 17) % 31)   # 60..90s
        faults.append(Fault(t_offset=t, target=target, action=action, duration_s=dur))
        i += 1
    return faults

def _containers(target: FaultTarget):
    mapping = _default_containers()
    if target == FaultTarget.BOTH:
        return [mapping[FaultTarget.CH1], mapping[FaultTarget.CH2]]
    return [mapping[target]]

def _is_running(container: str) -> bool:
    """Return True iff the container is in 'running' state."""
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Status}}", container],
        capture_output=True, text=True, timeout=30)
    return r.returncode == 0 and r.stdout.strip() == "running"


# helpers.cluster's start_clickhouse pidfile. Probe must be aliveness (`kill -0`), not existence:
# docker restart/kill keeps the writable layer, and a SIGKILLed server does not unlink its pidfile.
# An existence-only probe no-ops after every CH fault and leaves the container serverless
# (see Altinity/ClickHouse#2233, clickhouse-regression port).
_PIDFILE = "/tmp/clickhouse-server.pid"
_ALIVE_PROBE = f"test -f {_PIDFILE} && kill -0 $(cat {_PIDFILE}) 2>/dev/null"


def _server_alive(container: str) -> bool:
    """True iff clickhouse-server's pidfile names a live process in `container`."""
    probe = subprocess.run(
        ["docker", "exec", container, "bash", "-c", _ALIVE_PROBE],
        capture_output=True, timeout=30)
    return probe.returncode == 0


def _ensure_clickhouse_daemon(container: str):
    """After docker start/restart of a helpers.cluster node (entrypoint is `tail -f /dev/null`),
    bring clickhouse-server back with the same pidfile contract Cluster.start_clickhouse uses.

    No-op when a *live* server is already present (upstream compose entrypoint starts it).
    Must not treat a stale pidfile as alive — that is the regression-port phase-2 false pass
    that left both replicas answering docker-proxy resets with no server behind them."""
    if _server_alive(container):
        return
    subprocess.run(
        ["docker", "exec", container, "bash", "-c", f"rm -f {_PIDFILE}"],
        capture_output=True, timeout=30)
    started = subprocess.run(
        [
            "docker", "exec", container, "bash", "-c",
            "clickhouse server --config-file=/etc/clickhouse-server/config.xml"
            " --log-file=/var/log/clickhouse-server/clickhouse-server.log"
            " --errorlog-file=/var/log/clickhouse-server/clickhouse-server.err.log"
            f" --pidfile={_PIDFILE} --daemon",
        ],
        capture_output=True, timeout=60)
    if started.returncode != 0:
        err = (started.stderr or started.stdout or b"").decode("utf-8", "replace")
        raise RuntimeError(
            f"failed to start clickhouse-server in {container}: rc={started.returncode} {err}"
        )
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if _server_alive(container):
            return
        time.sleep(0.5)
    raise RuntimeError(
        f"clickhouse-server in {container} did not become alive after daemon start "
        f"(pidfile={_PIDFILE})"
    )


def apply_fault(fault: Fault):
    """Execute a fault via docker. Thin wrapper; the driver schedules these. KILL is followed by a
    `docker start` after duration_s (so the node recovers); PAUSE is unpause after duration_s.

    After `docker start`, polls until the container is in 'running' state (up to 30s) so the caller's
    `wait_healthy` polling starts from a known container-running baseline."""
    cs = _containers(fault.target)
    if fault.action == FaultAction.KILL:
        for c in cs:
            subprocess.run(["docker", "kill", "-s", "KILL", c], capture_output=True)
        time.sleep(fault.duration_s)
        for c in cs:
            subprocess.run(["docker", "start", c], capture_output=True)
        # Wait for container to reach 'running' state before returning
        for c in cs:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if _is_running(c):
                    break
                time.sleep(2)
            if fault.target != FaultTarget.RUSTFS:
                _ensure_clickhouse_daemon(c)
    elif fault.action == FaultAction.RESTART:
        for c in cs:
            subprocess.run(["docker", "restart", c], capture_output=True)
            if fault.target != FaultTarget.RUSTFS:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    if _is_running(c):
                        break
                    time.sleep(2)
                _ensure_clickhouse_daemon(c)
    elif fault.action in (FaultAction.PAUSE, FaultAction.FREEZE_LONG):
        # Both freeze the container via the cgroup freezer (docker pause = SIGSTOP-equivalent for all
        # tasks; unpause = SIGCONT). FREEZE_LONG differs only in duration (held past the mount-lease TTL
        # to force a fence-out), so the mechanics are identical.
        for c in cs:
            subprocess.run(["docker", "pause", c], capture_output=True)
        time.sleep(fault.duration_s)
        for c in cs:
            subprocess.run(["docker", "unpause", c], capture_output=True)
