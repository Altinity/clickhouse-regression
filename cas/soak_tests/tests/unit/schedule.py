from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.schedule import (
    StageKind,
    _STAGE_FRACTIONS,
    chaos_window,
    stage_at,
    stage_plan,
)


@TestScenario
@Name("fractions sum to one")
def fractions_sum_to_one(self):
    assert abs(sum(f for _, f in _STAGE_FRACTIONS) - 1.0) < 1e-9, error()


@TestScenario
@Name("plan tiles duration exactly")
def plan_tiles_duration_exactly(self):
    for dur in (600, 3600, 24 * 3600, 7, 100000):
        plan = stage_plan(dur)
        assert plan[0].t_start == 0, error()
        assert plan[-1].t_end == dur, error(
            f"final stage must reach {dur}, got {plan[-1].t_end}"
        )
        for a, b in zip(plan, plan[1:]):
            assert a.t_end == b.t_start, error()
            assert a.t_start <= a.t_end, error()


@TestScenario
@Name("plan stage order")
def plan_stage_order(self):
    kinds = [s.kind for s in stage_plan(24 * 3600)]
    assert kinds == [
        StageKind.WARMUP,
        StageKind.STEADY,
        StageKind.MUTATIONS,
        StageKind.TTL_PRESSURE,
        StageKind.GC_CHECKPOINT,
        StageKind.CHAOS,
        StageKind.CLIFF,
        StageKind.CONVERGE,
    ], error()


@TestScenario
@Name("plan is deterministic")
def plan_is_deterministic(self):
    assert stage_plan(600) == stage_plan(600), error()


@TestScenario
@Name("plan compresses 24h to 600s same shape")
def plan_compresses_24h_to_600s_same_shape(self):
    big = stage_plan(24 * 3600)
    small = stage_plan(600)
    assert [s.kind for s in big] == [s.kind for s in small], error()
    for sb, ss in zip(big, small):
        fb = (sb.t_end - sb.t_start) / (24 * 3600)
        fs = (ss.t_end - ss.t_start) / 600
        assert abs(fb - fs) < 0.05, error()


@TestScenario
@Name("capabilities are progressive")
def capabilities_are_progressive(self):
    plan = {s.kind: s for s in stage_plan(3600)}
    assert plan[StageKind.WARMUP].allow_inserts, error()
    assert not plan[StageKind.WARMUP].allow_mutations, error()
    assert not plan[StageKind.WARMUP].chaos_armed, error()
    assert plan[StageKind.MUTATIONS].allow_mutations, error()
    assert plan[StageKind.CHAOS].chaos_armed, error()
    assert plan[StageKind.CLIFF].allow_cliffs and plan[StageKind.CLIFF].chaos_armed, error()
    assert not plan[StageKind.CONVERGE].chaos_armed, error()
    assert not plan[StageKind.GC_CHECKPOINT].allow_inserts, error()


@TestScenario
@Name("only chaos and cliff arm chaos")
def only_chaos_and_cliff_arm_chaos(self):
    armed = {s.kind for s in stage_plan(3600) if s.chaos_armed}
    assert armed == {StageKind.CHAOS, StageKind.CLIFF}, error()


@TestScenario
@Name("stage_at resolves each window")
def stage_at_resolves_each_window(self):
    plan = stage_plan(3600)
    for s in plan:
        mid = (s.t_start + s.t_end) // 2
        assert stage_at(plan, mid).kind == s.kind, error()
    assert stage_at(plan, plan[1].t_start).kind == plan[1].kind, error()
    assert stage_at(plan, 999999).kind == StageKind.CONVERGE, error()
    assert stage_at(plan, 0).kind == StageKind.WARMUP, error()


@TestScenario
@Name("chaos window is chaos through cliff")
def chaos_window_is_chaos_through_cliff(self):
    plan = stage_plan(3600)
    start, end = chaos_window(plan)
    chaos = next(s for s in plan if s.kind == StageKind.CHAOS)
    cliff = next(s for s in plan if s.kind == StageKind.CLIFF)
    assert start == chaos.t_start, error()
    assert end == cliff.t_end, error()


@TestScenario
@Name("nonpositive duration raises")
def nonpositive_duration_raises(self):
    for bad in (0, -5):
        raised = False
        try:
            stage_plan(bad)
        except ValueError:
            raised = True
        assert raised, error(f"expected ValueError for duration {bad}")


@TestFeature
@Name("schedule")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
