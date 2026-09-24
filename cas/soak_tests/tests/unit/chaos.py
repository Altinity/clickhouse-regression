from testflows.core import *
from testflows.asserts import error

import threading
import time

from cas.soak_tests.oracle.chaos import (
    FaultAction,
    FaultTarget,
    generate_chaos_schedule,
)
from cas.soak_tests.steps.chaos import ChaosRunner


@TestScenario
@Name("schedule is reproducible")
def schedule_is_reproducible(self):
    a = generate_chaos_schedule(seed=9, duration_s=3600, mean_interval_s=300)
    b = generate_chaos_schedule(seed=9, duration_s=3600, mean_interval_s=300)
    assert a == b, error()
    assert generate_chaos_schedule(seed=10, duration_s=3600, mean_interval_s=300) != a, error()


@TestScenario
@Name("schedule is within duration and typed")
def schedule_is_within_duration_and_typed(self):
    s = generate_chaos_schedule(seed=1, duration_s=3600, mean_interval_s=300)
    assert all(0 <= f.t_offset < 3600 for f in s), error()
    assert all(
        isinstance(f.target, FaultTarget) and isinstance(f.action, FaultAction) for f in s
    ), error()


@TestScenario
@Name("no long kill of both replicas")
def no_long_kill_of_both_replicas(self):
    for seed in range(20):
        for f in generate_chaos_schedule(seed=seed, duration_s=7200, mean_interval_s=120):
            if f.target == FaultTarget.BOTH and f.action == FaultAction.KILL:
                assert f.duration_s <= 60, error()


@TestScenario
@Name("schedule is ordered by time")
def schedule_is_ordered_by_time(self):
    s = generate_chaos_schedule(seed=5, duration_s=3600, mean_interval_s=300)
    assert [f.t_offset for f in s] == sorted(f.t_offset for f in s), error()


@TestScenario
@Name("rustfs is never killed")
def rustfs_is_never_killed(self):
    for seed in range(50):
        for f in generate_chaos_schedule(seed=seed, duration_s=7200, mean_interval_s=120):
            if f.target == FaultTarget.RUSTFS:
                assert f.action != FaultAction.KILL, error(
                    f"RustFS fault must never be KILL (got {f.action} at t={f.t_offset})"
                )


@TestScenario
@Name("freeze long hits one replica past lease ttl")
def freeze_long_hits_one_replica_past_lease_ttl(self):
    saw = False
    for seed in range(20):
        for f in generate_chaos_schedule(seed=seed, duration_s=7200, mean_interval_s=120):
            if f.action == FaultAction.FREEZE_LONG:
                saw = True
                assert f.target in (FaultTarget.CH1, FaultTarget.CH2), error()
                assert f.duration_s > 45, error()
    assert saw, error("expected at least one FREEZE_LONG")


@TestScenario
@Name("daemon probe is aliveness not pidfile existence")
def daemon_probe_is_aliveness_not_pidfile_existence(self):
    from cas.soak_tests.steps.chaos import _ALIVE_PROBE, _PIDFILE

    assert _PIDFILE == "/tmp/clickhouse-server.pid", error()
    assert "kill -0" in _ALIVE_PROBE, error()
    assert "test -f" in _ALIVE_PROBE, error()


@TestScenario
@Name("chaos runner waits on elapsed_fn not wall clock")
def chaos_runner_waits_on_elapsed_fn_not_wall_clock(self):
    from cas.soak_tests.oracle.chaos import Fault, FaultAction, FaultTarget
    from cas.soak_tests.steps import chaos as chaos_mod

    fired = []
    original = chaos_mod.apply_fault

    def fake_apply(fault, mapping=None):
        fired.append(fault)

    chaos_mod.apply_fault = fake_apply
    try:
        clock = {"t": 0.0}
        stop = threading.Event()
        gate = threading.Event()
        done = []

        def on_done(fault):
            done.append(fault)

        runner = ChaosRunner(
            [
                Fault(
                    t_offset=50,
                    target=FaultTarget.CH1,
                    action=FaultAction.RESTART,
                    duration_s=1,
                )
            ],
            on_fault_done=on_done,
            stop_event=stop,
            checkpoint_active=gate,
            log_fn=lambda msg: None,
            elapsed_fn=lambda: clock["t"],
        )
        runner.start()
        time.sleep(0.3)
        assert fired == [], error("fault fired before elapsed_fn reached t_offset")
        clock["t"] = 50
        runner.join(timeout=5)
        assert fired and fired[0].t_offset == 50, error()
        assert done and done[0].t_offset == 50, error()
    finally:
        stop.set()
        chaos_mod.apply_fault = original
        runner.join(timeout=2)


@TestScenario
@Name("clickhouse replicas are still killed")
def clickhouse_replicas_are_still_killed(self):
    saw = False
    for seed in range(50):
        for f in generate_chaos_schedule(seed=seed, duration_s=7200, mean_interval_s=120):
            if (
                f.target in (FaultTarget.CH1, FaultTarget.CH2, FaultTarget.BOTH)
                and f.action == FaultAction.KILL
            ):
                saw = True
                break
        if saw:
            break
    assert saw, error("expected at least one ClickHouse-replica KILL")


@TestFeature
@Name("chaos")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
