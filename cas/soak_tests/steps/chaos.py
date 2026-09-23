"""Docker fault applicator and background chaos thread.

Schedule generation lives in ``oracle.chaos`` (pure). This module talks to docker.
Must not import ``cas.soak``.
"""

import os
import subprocess
import threading
import time

from cas.soak_tests.oracle.chaos import FaultAction, FaultTarget

_PIDFILE = "/tmp/clickhouse-server.pid"
_ALIVE_PROBE = f"test -f {_PIDFILE} && kill -0 $(cat {_PIDFILE}) 2>/dev/null"

_DEFAULT_CONTAINERS = {
    FaultTarget.CH1: os.environ.get(
        "CA_SOAK_TESTS_NODE1_CONTAINER", "soak_tests_env-clickhouse1-1"
    ),
    FaultTarget.CH2: os.environ.get(
        "CA_SOAK_TESTS_NODE2_CONTAINER", "soak_tests_env-clickhouse2-1"
    ),
    FaultTarget.RUSTFS: os.environ.get(
        "CA_SOAK_TESTS_RUSTFS_CONTAINER", "cas_soak_tests_rustfs"
    ),
}


def _containers(target, mapping=None):
    mapping = mapping or _DEFAULT_CONTAINERS
    if target == FaultTarget.BOTH:
        return [mapping[FaultTarget.CH1], mapping[FaultTarget.CH2]]
    return [mapping[target]]


def _is_running(container):
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Status}}", container],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return r.returncode == 0 and r.stdout.strip() == "running"


def _server_alive(container):
    probe = subprocess.run(
        ["docker", "exec", container, "bash", "-c", _ALIVE_PROBE],
        capture_output=True,
        timeout=30,
    )
    return probe.returncode == 0


def _ensure_clickhouse_daemon(container):
    if _server_alive(container):
        return
    subprocess.run(
        ["docker", "exec", container, "bash", "-c", f"rm -f {_PIDFILE}"],
        capture_output=True,
        timeout=30,
    )
    started = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "bash",
            "-c",
            "clickhouse server --config-file=/etc/clickhouse-server/config.xml"
            " --log-file=/var/log/clickhouse-server/clickhouse-server.log"
            " --errorlog-file=/var/log/clickhouse-server/clickhouse-server.err.log"
            f" --pidfile={_PIDFILE} --daemon",
        ],
        capture_output=True,
        timeout=60,
    )
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
        f"clickhouse-server in {container} did not become alive after daemon start"
    )


def ensure_clickhouse_daemon(container):
    _ensure_clickhouse_daemon(container)


def apply_fault(fault, mapping=None):
    cs = _containers(fault.target, mapping)
    if fault.action == FaultAction.KILL:
        for c in cs:
            subprocess.run(["docker", "kill", "-s", "KILL", c], capture_output=True)
        time.sleep(fault.duration_s)
        for c in cs:
            subprocess.run(["docker", "start", c], capture_output=True)
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
        for c in cs:
            subprocess.run(["docker", "pause", c], capture_output=True)
        time.sleep(fault.duration_s)
        for c in cs:
            subprocess.run(["docker", "unpause", c], capture_output=True)


class ChaosRunner(threading.Thread):
    def __init__(
        self,
        schedule,
        *,
        on_fault_done,
        stop_event,
        checkpoint_active,
        log_fn=print,
        elapsed_fn=None,
    ):
        super().__init__(daemon=True, name="chaos")
        self.schedule = schedule
        self.on_fault_done = on_fault_done
        self.stop_event = stop_event
        self.checkpoint_active = checkpoint_active
        self.log_fn = log_fn
        self.elapsed_fn = elapsed_fn
        self.start_monotonic = None
        self.last_fault = None
        self.faults_fired = 0
        self.error = None

    def _elapsed(self):
        if self.elapsed_fn is not None:
            return float(self.elapsed_fn())
        return time.monotonic() - self.start_monotonic

    def run(self):
        self.start_monotonic = time.monotonic()
        try:
            for fault in self.schedule:
                while not self.stop_event.is_set():
                    elapsed = self._elapsed()
                    if elapsed >= fault.t_offset:
                        break
                    self.stop_event.wait(min(0.5, max(0.05, fault.t_offset - elapsed)))
                if self.stop_event.is_set():
                    return
                while self.checkpoint_active.is_set() and not self.stop_event.is_set():
                    self.stop_event.wait(0.5)
                if self.stop_event.is_set():
                    return
                self.log_fn(
                    f"CHAOS firing fault #{self.faults_fired + 1} at t+{fault.t_offset}s: "
                    f"{fault.target.value} {fault.action.value} dur={fault.duration_s}s"
                )
                apply_fault(fault)
                self.last_fault = fault
                self.faults_fired += 1
                self.log_fn(
                    f"CHAOS fault window complete: {fault.target.value} {fault.action.value}"
                )
                self.on_fault_done(fault)
        except Exception as e:
            self.error = e
            self.log_fn(f"CHAOS thread error: {type(e).__name__}: {e}")
