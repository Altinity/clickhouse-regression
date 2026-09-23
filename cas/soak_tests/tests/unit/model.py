from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import (
    BASE_TIME,
    MAX_BLOCK,
    TS_WINDOW,
    Model,
    Op,
    OpType,
    row_for_rid,
)


def ins(op_id, n):
    """INSERT whose param yields exactly n rows: n = 1 + (param % insert_block)."""
    return Op(op_id, OpType.INSERT, 0, n - 1)


@TestScenario
@Name("insert then aggregates")
def insert_then_aggregates(self):
    with Given("a model with a 10-row insert"):
        m = Model(seed=1)
        m.apply(ins(0, 10))
    with Then("count, fingerprint sum, and op range match the rows"):
        agg = m.aggregates(now=BASE_TIME)
        assert agg["count"] == 10, error()
        expected_fp = (
            sum(row_for_rid(1, 0 * MAX_BLOCK + j)["row_fp"] for j in range(10))
            % (2**64)
        )
        assert agg["sum_fp"] == expected_fp, error()
        assert agg["min_op"] == 0 and agg["max_op"] == 0, error()


@TestScenario
@Name("update bumps v and version not fp")
def update_bumps_v_and_version_not_fp(self):
    with Given("four inserted rows"):
        m = Model(seed=1)
        m.apply(ins(0, 4))
        before = m.aggregates(now=BASE_TIME)
    with When("I UPDATE bucket 0"):
        m.apply(Op(1, OpType.UPDATE, 0, 0))
        after = m.aggregates(now=BASE_TIME)
    with Then("identity is unchanged and counters move"):
        assert after["sum_fp"] == before["sum_fp"], error()
        assert after["count"] == before["count"], error()
        assert after["sum_v"] > before["sum_v"], error()
        assert after["sum_version"] > before["sum_version"], error()


@TestScenario
@Name("delete and truncate")
def delete_and_truncate(self):
    with Given("20 inserted rows"):
        m = Model(seed=2)
        m.apply(ins(0, 20))
    with When("I DELETE bucket 0"):
        m.apply(Op(1, OpType.DELETE, 0, 0))
    with Then("no live row is in bucket 0"):
        assert all(r["bucket"] != 0 for r in m.live_rows(now=BASE_TIME)), error()
    with When("I TRUNCATE"):
        m.apply(Op(2, OpType.TRUNCATE, 0, 0))
    with Then("the model is empty"):
        assert m.aggregates(now=BASE_TIME)["count"] == 0, error()


@TestScenario
@Name("ttl expiry")
def ttl_expiry(self):
    with Given("five rows at BASE_TIME"):
        m = Model(seed=3)
        m.apply(ins(0, 5))
        far = BASE_TIME + m.ttl_seconds + TS_WINDOW + 10
    with Then("they expire far in the future but not at base_time"):
        assert m.aggregates(now=far)["count"] == 0, error()
        assert m.aggregates(now=BASE_TIME)["count"] == 5, error()


@TestScenario
@Name("ttl ambiguity band detection")
def ttl_ambiguity_band_detection(self):
    with Given("five rows"):
        m = Model(seed=3)
        m.apply(ins(0, 5))
        expiry = BASE_TIME + 0 + m.ttl_seconds
    with Then("the band is nonempty at expiry and empty far past it"):
        assert m.ambiguous_band_nonempty(now=expiry, eps=5) is True, error()
        assert m.ambiguous_band_nonempty(now=expiry + 1000, eps=5) is False, error()


@TestScenario
@Name("ttl ambiguity band clears by advancing now")
def ttl_ambiguity_band_clears_by_advancing_now(self):
    """Checkpoint wait-out: a row's TTL boundary is fixed; advancing now past the band
    (eps + 1) makes the exact-aggregate assertion safe."""
    with Given("five rows"):
        m = Model(seed=3)
        m.apply(ins(0, 5))
        latest_expiry = max(r["ts"] + m.ttl_seconds for r in m.rows.values())
        eps = 10
    with Then("sitting on the latest expiry fills the band"):
        assert m.ambiguous_band_nonempty(now=latest_expiry, eps=eps) is True, error()
    with When("I advance now by eps + 1"):
        cleared_now = latest_expiry + (eps + 1)
    with Then("the band is empty and every row is expired"):
        assert m.ambiguous_band_nonempty(now=cleared_now, eps=eps) is False, error()
        assert m.aggregates(now=cleared_now)["count"] == 0, error()


@TestScenario
@Name("prune expired removes only expired")
def prune_expired_removes_only_expired(self):
    with Given("five rows"):
        m = Model(seed=3)
        m.apply(ins(0, 5))
    with Then("nothing is pruned at base_time"):
        assert m.prune_expired(now=BASE_TIME) == 0, error()
        assert len(m.rows) == 5, error()
    with When("I prune far past TTL"):
        far = BASE_TIME + m.ttl_seconds + TS_WINDOW + 10
        n = m.prune_expired(now=far)
    with Then("all rows are reclaimed"):
        assert n == 5, error()
        assert len(m.rows) == 0, error()


@TestScenario
@Name("prune expired does not change live view")
def prune_expired_does_not_change_live_view(self):
    with Given("two insert ops one second apart"):
        m = Model(seed=4)
        m.apply(ins(0, 8))
        m.apply(ins(1, 8))
        now = BASE_TIME + 0 + m.ttl_seconds + 1
        before = m.aggregates(now)
        n_before = len(m.rows)
    with When("I prune at a now that expires only op_id 0"):
        reclaimed = m.prune_expired(now)
        after = m.aggregates(now)
    with Then("expired rows drop and live aggregates stay identical"):
        assert reclaimed > 0 and len(m.rows) < n_before, error()
        assert after == before, error()


@TestScenario
@Name("model row carries no payload")
def model_row_carries_no_payload(self):
    with Given("three inserted rows"):
        m = Model(seed=5)
        m.apply(ins(0, 3))
    with Then("payload is dropped and count is still 3"):
        assert all("payload" not in r for r in m.rows.values()), error()
        assert m.aggregates(now=BASE_TIME)["count"] == 3, error()


@TestFeature
@Name("model")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
