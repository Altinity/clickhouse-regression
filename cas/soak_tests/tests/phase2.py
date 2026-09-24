import threading

from testflows.core import *

from cas.soak_tests.oracle import Model, build_effective_ledger, generate_ledger
from cas.soak_tests.oracle.chaos import generate_chaos_schedule
from cas.soak_tests.steps.chaos import ChaosRunner
from cas.soak_tests.steps.checkpoint import green_checkpoint
from cas.soak_tests.steps.driver import Driver
from cas.soak_tests.steps.http import http_nodes_from_context
from cas.soak_tests.steps.table import soak_table


@TestScenario
@Name("chaos ledger matches model after recovery")
def chaos_ledger_matches_model_after_recovery(self):
    seed = int(getattr(self.context, "soak_seed", 1))
    ops = int(getattr(self.context, "phase1_ops", 200))
    checkpoint_every = int(getattr(self.context, "phase1_checkpoint_every", 50))
    workers = int(getattr(self.context, "phase1_workers", 6))
    chaos_seed = int(getattr(self.context, "chaos_seed", seed))
    chaos_interval = int(getattr(self.context, "chaos_interval", 90))
    max_cliffs = 2
    min_gap = max(1, ops // 4)
    duration_s = max(600, ops * 2)

    with Given("a soak table and wall-clock base_time"):
        table = soak_table()
        base_time = (
            int(
                self.context.node.query(
                    "SELECT toUnixTimestamp(now()) FORMAT TabSeparated"
                ).output.strip()
            )
            - 60
        )
        note(
            f"base_time={base_time} seed={seed} ops={ops} checkpoint_every={checkpoint_every} "
            f"chaos_seed={chaos_seed} chaos_interval={chaos_interval}"
        )
        model = Model(seed=seed, base_time=base_time)
        driver = Driver(
            http_nodes=http_nodes_from_context(self.context.nodes),
            table=table,
            model=model,
            seed=seed,
            base_time=base_time,
            workers=workers,
            transport_resilient=True,
        )

    ledger = generate_ledger(seed, ops)
    effective = build_effective_ledger(ledger, max_cliffs, min_gap)
    schedule = generate_chaos_schedule(chaos_seed, duration_s, chaos_interval)
    note(f"effective ledger: {len(effective)} ops; chaos schedule: {len(schedule)} faults")
    if schedule:
        f0 = schedule[0]
        note(
            f"first fault at t+{f0.t_offset}s {f0.target.value} {f0.action.value} "
            f"dur={f0.duration_s}s"
        )

    chaos_stop = threading.Event()
    checkpoint_active = threading.Event()
    recovery_lock = threading.Lock()
    recovery_pending = []

    def on_fault_done(fault):
        with recovery_lock:
            recovery_pending.append(fault)

    chaos = ChaosRunner(
        schedule,
        on_fault_done=on_fault_done,
        stop_event=chaos_stop,
        checkpoint_active=checkpoint_active,
        log_fn=lambda msg: print(f"[chaos] {msg}", flush=True),
    )

    def do_checkpoint(label, executed):
        checkpoint_active.set()
        try:
            green_checkpoint(
                driver=driver,
                table=table,
                model=model,
                label=f"{label} {executed}",
                phase=2,
            )
        finally:
            checkpoint_active.clear()

    def drain_recovery(executed):
        with recovery_lock:
            pending = list(recovery_pending)
            recovery_pending.clear()
        if not pending:
            return
        if chaos.error is not None:
            raise chaos.error
        note(f"RECOVERY: {len(pending)} fault window(s) completed")
        do_checkpoint("recovery checkpoint", executed)

    try:
        chaos.start()
        with When(f"I execute {len(effective)} ops under chaos"):
            executed = 0
            last_op = None
            for op in effective:
                drain_recovery(executed)
                driver.execute(op)
                last_op = op
                executed += 1
                drain_recovery(executed)
                if executed % checkpoint_every == 0:
                    do_checkpoint("checkpoint", executed)
            chaos_stop.set()
            chaos.join(timeout=30)
            drain_recovery(executed)
            if chaos.error is not None:
                raise chaos.error
            if executed == 0 or executed % checkpoint_every != 0:
                do_checkpoint("final checkpoint", executed)
        note(
            f"ABORTED-retried INSERT attempts: {driver.aborted_retries}; "
            f"transport retries: {driver.transport_retries}; "
            f"faults fired: {chaos.faults_fired}"
        )
        _ = last_op
    finally:
        chaos_stop.set()
        driver.close()


@TestFeature
@Name("phase2")
def feature(self):
    """Chaos soak: same ledger driver with deterministic docker faults."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
