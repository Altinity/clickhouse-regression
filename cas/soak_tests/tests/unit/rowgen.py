from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import (
    MAX_BLOCK,
    NBUCKETS,
    SHARED_CONTENT,
    insert_rids,
    row_for_rid,
)


@TestScenario
@Name("row is deterministic")
def row_is_deterministic(self):
    with Then("the same seed and rid produce the same row"):
        assert row_for_rid(seed=1, rid=12345) == row_for_rid(seed=1, rid=12345), error()


@TestScenario
@Name("row_fp is immutable identity")
def row_fp_is_immutable_identity(self):
    with When("I generate a row"):
        r = row_for_rid(seed=1, rid=999)
    with Then("row_fp is stable, 64-bit, and bucket is rid mod NBUCKETS"):
        assert r["row_fp"] == row_for_rid(seed=1, rid=999)["row_fp"], error()
        assert 0 <= r["row_fp"] < 2**64, error()
        assert r["bucket"] == 999 % NBUCKETS, error()


@TestScenario
@Name("shared content dedups")
def shared_content_dedups(self):
    with When("I pick two rids that share bucket and content slot"):
        r1 = row_for_rid(seed=5, rid=10)
        r2 = row_for_rid(seed=5, rid=10 + SHARED_CONTENT * NBUCKETS)
    with Then("payload bytes match"):
        assert r1["bucket"] == r2["bucket"], error()
        assert r1["payload"] == r2["payload"], error()


@TestScenario
@Name("insert rids unique and bounded")
def insert_rids_unique_and_bounded(self):
    with When("I expand op_id 3 into 10 rids"):
        rids = insert_rids(op_id=3, n=10)
    with Then("they are unique and packed by MAX_BLOCK"):
        assert rids == [3 * MAX_BLOCK + j for j in range(10)], error()
        assert len(set(rids)) == 10, error()


@TestFeature
@Name("rowgen")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
