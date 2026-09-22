from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.checker import (
    CheckpointFailure,
    compare_aggregates,
    dryrun_subset_check,
    gc_fixpoint_reached,
    is_genuine_hang,
    parse_aggregates,
    wait_for_pool_consistent,
)


def _hang(**over):
    base = dict(
        backlog_flat=True,
        active_merges=0,
        errored_queue=0,
        grace_exceeded=True,
        budget_exceeded=True,
        absolute_cap_exceeded=False,
    )
    base.update(over)
    return is_genuine_hang(**base)


@TestScenario
@Name("parse aggregates empty table")
def parse_aggregates_empty(self):
    got = parse_aggregates("0\t0\t0\t0\t0\t\\N\t\\N")
    assert got["count"] == 0, error()
    assert got["min_op"] is None and got["max_op"] is None, error()


@TestScenario
@Name("parse aggregates nonempty")
def parse_aggregates_nonempty(self):
    got = parse_aggregates("3\t10\t2\t4\t5\t0\t1")
    assert got == {
        "count": 3,
        "sum_fp": 10,
        "uniq_keys": 2,
        "sum_v": 4,
        "sum_version": 5,
        "min_op": 0,
        "max_op": 1,
    }, error()


@TestScenario
@Name("compare aggregates match")
def compare_aggregates_match(self):
    exp = {
        "count": 10,
        "sum_fp": 123,
        "uniq_keys": 9,
        "sum_v": 5,
        "sum_version": 10,
        "min_op": 0,
        "max_op": 3,
    }
    assert compare_aggregates(exp, exp, exp) is None, error()


@TestScenario
@Name("compare aggregates mismatch raises with detail")
def compare_aggregates_mismatch_raises_with_detail(self):
    exp = {
        "count": 10,
        "sum_fp": 123,
        "uniq_keys": 9,
        "sum_v": 5,
        "sum_version": 10,
        "min_op": 0,
        "max_op": 3,
    }
    got = dict(exp)
    got["count"] = 9
    try:
        compare_aggregates(exp, got, exp)
        assert False, error("expected CheckpointFailure")
    except CheckpointFailure as e:
        assert "count" in str(e) and "node1" in str(e), error()


@TestScenario
@Name("gc fixpoint two stable rounds")
def gc_fixpoint_two_stable_rounds(self):
    assert gc_fixpoint_reached([100, 90, 80, 80], stable=2) is True, error()
    assert gc_fixpoint_reached([100, 90, 80, 70], stable=2) is False, error()
    assert gc_fixpoint_reached([80], stable=2) is False, error()


@TestScenario
@Name("pool consistent waits for stable dangling zero")
def pool_consistent_waits_for_stable_dangling_zero(self):
    readings = [
        {"dangling": 3, "exit_code": 0},
        {"dangling": 0, "exit_code": 0},
        {"dangling": 0, "exit_code": 0},
    ]

    def fsck_fn():
        return readings.pop(0)

    got = wait_for_pool_consistent(
        fsck_fn, timeout_s=10, stable=2, interval_s=0, sleep_fn=lambda s: None
    )
    assert got["dangling"] == 0, error()


@TestScenario
@Name("pool consistent persistent dangling fails")
def pool_consistent_persistent_dangling_fails(self):
    clock = {"t": 0}

    def fsck_fn():
        return {"dangling": 4, "exit_code": 0}

    try:
        wait_for_pool_consistent(
            fsck_fn,
            timeout_s=1,
            stable=2,
            interval_s=1,
            sleep_fn=lambda s: clock.__setitem__("t", clock["t"] + s),
            monotonic_fn=lambda: clock["t"],
        )
        assert False, error("expected CheckpointFailure")
    except CheckpointFailure as e:
        assert "dangling=4" in str(e), error()


@TestScenario
@Name("hang flat idle is hang")
def hang_flat_idle_with_grace_and_budget_spent_is_hang(self):
    assert _hang() == (True, "idle-flat"), error()


@TestScenario
@Name("hang flat but active merge is not a hang")
def hang_flat_but_active_merge_is_not_a_hang(self):
    assert _hang(active_merges=1) == (False, ""), error()


@TestScenario
@Name("hang errored queue fails fast")
def hang_errored_queue_fails_fast_even_with_active_merge(self):
    assert _hang(active_merges=2, errored_queue=1) == (True, "errored"), error()


@TestScenario
@Name("hang progressing backlog is not a hang")
def hang_progressing_backlog_not_a_hang(self):
    assert _hang(backlog_flat=False) == (False, ""), error()


@TestScenario
@Name("hang absolute cap when idle is capped")
def hang_absolute_cap_when_idle_is_capped(self):
    assert _hang(grace_exceeded=False, budget_exceeded=False, absolute_cap_exceeded=True) == (
        True,
        "capped",
    ), error()


@TestScenario
@Name("dryrun empty no failure")
def dryrun_empty_no_failure(self):
    detail = [{"key": "pool/blobs/aa/aaa", "class": "reachable"}]
    assert dryrun_subset_check(detail, []) == 0, error()


@TestScenario
@Name("dryrun all in pipeline no failure")
def dryrun_all_in_pipeline_no_failure(self):
    detail = [
        {"key": "pool/blobs/aa/aaa", "class": "unreachable"},
        {"key": "pool/blobs/bb/bbb", "class": "pending-gc"},
        {"key": "pool/trees/cc/ccc", "class": "awaiting-gc"},
    ]
    dryrun = [
        {"key": "pool/blobs/aa/aaa"},
        {"key": "pool/blobs/bb/bbb"},
        {"key": "pool/trees/cc/ccc"},
    ]
    assert dryrun_subset_check(detail, dryrun) == 0, error()


@TestScenario
@Name("dryrun key absent from detail tolerated")
def dryrun_key_absent_from_detail_tolerated(self):
    detail = [
        {"key": "pool/blobs/aa/aaa", "class": "reachable"},
        {"key": "pool/blobs/bb/bbb", "class": "unreachable"},
    ]
    dryrun = [{"key": "pool/blobs/bb/bbb"}, {"key": "pool/blobs/cc/ccc"}]
    logs = []
    count = dryrun_subset_check(detail, dryrun, log_fn=logs.append)
    assert count == 1, error()
    assert "1 keys already deleted, pending fold" in logs[0], error()


@TestScenario
@Name("dryrun key reachable in detail fails")
def dryrun_key_reachable_in_detail_fails(self):
    detail = [
        {"key": "pool/blobs/aa/aaa", "class": "reachable"},
        {"key": "pool/blobs/bb/bbb", "class": "unreachable"},
    ]
    dryrun = [{"key": "pool/blobs/bb/bbb"}, {"key": "pool/blobs/aa/aaa"}]
    try:
        dryrun_subset_check(detail, dryrun)
        assert False, error("expected CheckpointFailure")
    except CheckpointFailure as e:
        msg = str(e)
        assert "pool/blobs/aa/aaa" in msg, error()
        assert "fsck class='reachable'" in msg, error()


@TestScenario
@Name("dryrun key unaccounted in detail fails")
def dryrun_key_unaccounted_in_detail_fails(self):
    detail = [
        {"key": "pool/blobs/aa/aaa", "class": "unaccounted"},
        {"key": "pool/blobs/bb/bbb", "class": "unreachable"},
    ]
    dryrun = [{"key": "pool/blobs/bb/bbb"}, {"key": "pool/blobs/aa/aaa"}]
    try:
        dryrun_subset_check(detail, dryrun)
        assert False, error("expected CheckpointFailure")
    except CheckpointFailure as e:
        assert "fsck class='unaccounted'" in str(e), error()


@TestFeature
@Name("checker")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
