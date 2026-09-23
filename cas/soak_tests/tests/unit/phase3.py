from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.chaos import FaultAction, FaultTarget
from cas.soak_tests.oracle.ledger import Op, OpType, generate_ledger
from cas.soak_tests.oracle.phase3 import (
    GB,
    METRICS_INTERVAL_S,
    _THROTTLE_MAX,
    compute_throttle,
    demote_dense_mutations,
    metrics_interval_for,
    parse_duration,
    phase3_chaos_schedule,
    phase3_op_permitted,
)
from cas.soak_tests.oracle.schedule import StageKind, stage_plan


@TestScenario
@Name("parse duration suffixes")
def parse_duration_suffixes(self):
    assert parse_duration("600") == 600, error()
    assert parse_duration(600) == 600, error()
    assert parse_duration("600s") == 600, error()
    assert parse_duration("90m") == 5400, error()
    assert parse_duration("24h") == 86400, error()
    assert parse_duration("1d") == 86400, error()
    assert parse_duration("2h") == 7200, error()


@TestScenario
@Name("parse duration empty raises")
def parse_duration_empty_raises(self):
    raised = False
    try:
        parse_duration("")
    except (ValueError, KeyError):
        raised = True
    assert raised, error()


@TestScenario
@Name("metrics interval caps at production 60s")
def metrics_interval_caps_at_production_60s(self):
    assert metrics_interval_for(24 * 3600) == METRICS_INTERVAL_S == 60, error()


@TestScenario
@Name("metrics interval scales down for short runs")
def metrics_interval_scales_down_for_short_runs(self):
    iv = metrics_interval_for(600)
    assert 5 <= iv <= 60, error()
    assert 600 // iv >= 25, error()
    assert metrics_interval_for(60) == 5, error()


@TestScenario
@Name("throttle unknown pool fail closed when budget set")
def throttle_unknown_pool_fail_closed_when_budget_set(self):
    assert compute_throttle(None, 40 * GB, current_sleep_s=0.0) == _THROTTLE_MAX, error()
    assert compute_throttle(None, 40 * GB, current_sleep_s=0.25) == _THROTTLE_MAX, error()


@TestScenario
@Name("throttle unknown pool passthrough when no budget")
def throttle_unknown_pool_passthrough_when_no_budget(self):
    assert compute_throttle(None, None, current_sleep_s=0.25) == 0.25, error()
    assert compute_throttle(10 * GB, None, current_sleep_s=0.1) == 0.1, error()
    assert compute_throttle(None, 0, current_sleep_s=0.3) == 0.3, error()


@TestScenario
@Name("throttle bands")
def throttle_bands(self):
    budget = 40 * GB
    assert compute_throttle(int(0.5 * budget), budget, current_sleep_s=0.0) == 0.0, error()
    assert compute_throttle(int(0.80 * budget), budget, current_sleep_s=0.0) == 0.05, error()
    assert compute_throttle(int(0.95 * budget), budget, current_sleep_s=0.0) == 0.25, error()
    assert compute_throttle(int(1.10 * budget), budget, current_sleep_s=0.0) == 1.0, error()


@TestScenario
@Name("throttle monotone in pressure")
def throttle_monotone_in_pressure(self):
    budget = 40 * GB
    vals = [
        compute_throttle(int(f * budget), budget, current_sleep_s=0.0)
        for f in (0.1, 0.8, 0.95, 1.2)
    ]
    assert vals == sorted(vals), error()


def _op(t):
    return Op(op_id=1, type=t, target=0, param=0)


@TestScenario
@Name("op gating per stage")
def op_gating_per_stage(self):
    plan = {s.kind: s for s in stage_plan(3600)}
    warmup = plan[StageKind.WARMUP]
    assert phase3_op_permitted(_op(OpType.INSERT), warmup), error()
    assert not phase3_op_permitted(_op(OpType.OPTIMIZE), warmup), error()
    assert not phase3_op_permitted(_op(OpType.UPDATE), warmup), error()
    assert not phase3_op_permitted(_op(OpType.TRUNCATE), warmup), error()

    mut = plan[StageKind.MUTATIONS]
    assert phase3_op_permitted(_op(OpType.UPDATE), mut), error()
    assert phase3_op_permitted(_op(OpType.DELETE), mut), error()
    assert not phase3_op_permitted(_op(OpType.TRUNCATE), mut), error()

    cliff = plan[StageKind.CLIFF]
    assert phase3_op_permitted(_op(OpType.TRUNCATE), cliff), error()
    assert phase3_op_permitted(_op(OpType.DROP_PARTITION), cliff), error()

    gc = plan[StageKind.GC_CHECKPOINT]
    for t in OpType:
        assert not phase3_op_permitted(_op(t), gc), error(
            f"{t} should be blocked in GC checkpoint"
        )


@TestScenario
@Name("chaos schedule confined to window and has converge restart")
def chaos_schedule_confined_to_window_and_has_converge_restart(self):
    plan = stage_plan(3600)
    sched = phase3_chaos_schedule(20260613, plan, chaos_interval_s=90)
    chaos = next(s for s in plan if s.kind == StageKind.CHAOS)
    converge = next(s for s in plan if s.kind == StageKind.CONVERGE)
    assert all(f.t_offset >= chaos.t_start for f in sched), error()
    restarts = [
        f
        for f in sched
        if f.target == FaultTarget.BOTH
        and f.action == FaultAction.RESTART
        and f.t_offset >= converge.t_start
    ]
    assert restarts, error("expected a converge both-replica restart")


@TestScenario
@Name("chaos schedule is deterministic")
def chaos_schedule_is_deterministic(self):
    plan = stage_plan(1800)
    assert phase3_chaos_schedule(7, plan, 90) == phase3_chaos_schedule(7, plan, 90), error()


def _mk(types):
    return [Op(op_id=i, type=t, target=0, param=0) for i, t in enumerate(types)]


@TestScenario
@Name("demote keeps first mutation then spaces")
def demote_keeps_first_mutation_then_spaces(self):
    led = _mk(
        [OpType.UPDATE, OpType.UPDATE, OpType.DELETE, OpType.INSERT, OpType.DELETE]
    )
    out = demote_dense_mutations(led, min_ops_between_mutations=3)
    kinds = [o.type for o in out]
    assert kinds == [
        OpType.UPDATE,
        OpType.OPTIMIZE,
        OpType.OPTIMIZE,
        OpType.INSERT,
        OpType.DELETE,
    ], error()


@TestScenario
@Name("demote preserves op ids and nonmutations")
def demote_preserves_op_ids_and_nonmutations(self):
    led = _mk([OpType.INSERT, OpType.TRUNCATE, OpType.UPDATE, OpType.OPTIMIZE])
    out = demote_dense_mutations(led, min_ops_between_mutations=100)
    assert [o.op_id for o in out] == [0, 1, 2, 3], error()
    assert [o.type for o in out] == [
        OpType.INSERT,
        OpType.TRUNCATE,
        OpType.UPDATE,
        OpType.OPTIMIZE,
    ], error()


@TestScenario
@Name("demote disabled is identity")
def demote_disabled_is_identity(self):
    led = generate_ledger(123, 500)
    assert demote_dense_mutations(led, 0) == list(led), error()


@TestScenario
@Name("demote is deterministic and sparser")
def demote_is_deterministic_and_sparser(self):
    led = generate_ledger(20260613, 2000)
    a = demote_dense_mutations(led, 80)
    b = demote_dense_mutations(led, 80)
    assert a == b, error()
    raw_mut = sum(1 for o in led if o.type in (OpType.UPDATE, OpType.DELETE))
    kept_mut = sum(1 for o in a if o.type in (OpType.UPDATE, OpType.DELETE))
    assert kept_mut < raw_mut, error()
    last = None
    for o in a:
        if o.type in (OpType.UPDATE, OpType.DELETE):
            if last is not None:
                assert o.op_id - last >= 80, error()
            last = o.op_id


@TestFeature
@Name("phase3")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
