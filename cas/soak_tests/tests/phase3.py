import threading
import time

from testflows.core import *

from cas.soak_tests.oracle import Model, OpType, generate_ledger
from cas.soak_tests.oracle.phase3 import (
    demote_dense_mutations,
    parse_duration,
    phase3_chaos_schedule,
    phase3_op_permitted,
)
from cas.soak_tests.oracle.schedule import StageKind, stage_at, stage_plan
from cas.soak_tests.steps.chaos import ChaosRunner
from cas.soak_tests.steps.checkpoint import green_checkpoint
from cas.soak_tests.steps.driver import Driver
from cas.soak_tests.steps.http import http_nodes_from_context
from cas.soak_tests.steps.table import soak_table


@TestScenario
@Name("wall-clock stages match model after converge")
def wall_clock_stages_match_model_after_converge(self):
    seed = int(getattr(self.context, "soak_seed", 1))
    workers = int(getattr(self.context, "phase1_workers", 6))
    chaos_seed = int(getattr(self.context, "chaos_seed", seed))
    chaos_interval = int(getattr(self.context, "chaos_interval", 90))
    duration_s = parse_duration(getattr(self.context, "phase3_duration", "15m"))
    min_mut_gap = int(getattr(self.context, "min_ops_between_mutations", 80))
    no_chaos = bool(getattr(self.context, "no_chaos", False))
    n_ops = max(20000, duration_s * 50)
    plan = stage_plan(duration_s)

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
            f"base_time={base_time} seed={seed} duration={duration_s}s "
            f"chaos_seed={chaos_seed} chaos_interval={chaos_interval} no_chaos={no_chaos}"
        )
        for s in plan:
            note(
                f"  stage {s.kind.value:14s} [{s.t_start:>7d}..{s.t_end:<7d})s  "
                f"inserts={s.allow_inserts} opt={s.allow_optimize} "
                f"mut={s.allow_mutations} cliffs={s.allow_cliffs} chaos={s.chaos_armed}"
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

    def gen_ledger(ledger_seed):
        return demote_dense_mutations(generate_ledger(ledger_seed, n_ops), min_mut_gap)

    ledger = gen_ledger(seed)
    n_mut = sum(1 for op in ledger if op.type in (OpType.UPDATE, OpType.DELETE))
    note(
        f"phase-3 ledger: {len(ledger)} ops available; {n_mut} mutations kept "
        f"(min_ops_between_mutations={min_mut_gap})"
    )

    schedule = [] if no_chaos else phase3_chaos_schedule(chaos_seed, plan, chaos_interval)
    note(f"phase-3 chaos schedule: {len(schedule)} faults")
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
    stage_elapsed = {"t": 0.0}

    def on_fault_done(fault):
        with recovery_lock:
            recovery_pending.append(fault)

    chaos = ChaosRunner(
        schedule,
        on_fault_done=on_fault_done,
        stop_event=chaos_stop,
        checkpoint_active=checkpoint_active,
        log_fn=lambda msg: print(f"[chaos] {msg}", flush=True),
        elapsed_fn=lambda: stage_elapsed["t"],
    )

    def do_checkpoint(label, phase):
        checkpoint_active.set()
        try:
            green_checkpoint(
                driver=driver,
                table=table,
                model=model,
                label=label,
                phase=phase,
            )
        finally:
            checkpoint_active.clear()

    def drain_recovery():
        with recovery_lock:
            pending = list(recovery_pending)
            recovery_pending.clear()
        if not pending:
            return
        if chaos.error is not None:
            raise chaos.error
        note(f"RECOVERY: {len(pending)} fault window(s) completed")
        do_checkpoint("recovery checkpoint", phase=3)

    gc_idx = next(i for i, s in enumerate(plan) if s.kind == StageKind.GC_CHECKPOINT)
    stage_index = {s.kind: i for i, s in enumerate(plan)}
    inflight_cap = max(2 * workers, 64)

    try:
        chaos.start()
        with When(f"I run a {duration_s}s staged soak"):
            t0 = time.monotonic()
            paused = 0.0
            op_iter = iter(ledger)
            prev_stage_kind = None
            gc_checkpoint_done = False
            while True:
                elapsed = time.monotonic() - t0 - paused
                stage_elapsed["t"] = elapsed
                if elapsed >= duration_s:
                    break
                stage = stage_at(plan, elapsed)

                if stage.kind != prev_stage_kind:
                    note(f"=== STAGE {stage.kind.value} at t+{elapsed:.0f}s ===")
                    prev_stage_kind = stage.kind
                if not gc_checkpoint_done and stage_index.get(stage.kind, -1) >= gc_idx:
                    ck0 = time.monotonic()
                    do_checkpoint("GC checkpoint", phase=1)
                    paused += time.monotonic() - ck0
                    gc_checkpoint_done = True

                drain_t0 = time.monotonic()
                drain_recovery()
                paused += time.monotonic() - drain_t0
                if chaos.error is not None:
                    raise chaos.error

                driver.harvest()
                if driver.inflight_count() >= inflight_cap:
                    time.sleep(0.05)
                    continue

                if stage.kind == StageKind.GC_CHECKPOINT:
                    time.sleep(0.2)
                    continue

                try:
                    op = next(op_iter)
                except StopIteration:
                    ledger = gen_ledger(seed ^ int(elapsed))
                    op_iter = iter(ledger)
                    op = next(op_iter)

                if phase3_op_permitted(op, stage):
                    driver.execute(op)

            chaos_stop.set()
            chaos.join(timeout=30)
            drain_recovery()
            if chaos.error is not None:
                raise chaos.error
            if not gc_checkpoint_done:
                do_checkpoint("GC checkpoint", phase=1)
            do_checkpoint("final converge checkpoint", phase=3)
        note(
            f"ABORTED-retried INSERT attempts: {driver.aborted_retries}; "
            f"transport retries: {driver.transport_retries}; "
            f"faults fired: {chaos.faults_fired}"
        )
    finally:
        chaos_stop.set()
        driver.close()


@TestFeature
@Name("phase3")
def feature(self):
    """Wall-clock staged soak: capability-gated ledger, chaos window, converge restart."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
