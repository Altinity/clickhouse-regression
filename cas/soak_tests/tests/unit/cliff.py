from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import (
    CLIFF_TYPES,
    Op,
    OpType,
    build_effective_ledger,
    generate_ledger,
)


@TestScenario
@Name("cliff cap limits total cliffs")
def cliff_cap_limits_total_cliffs(self):
    with When("I cap a 1500-op ledger at 2 cliffs"):
        ledger = generate_ledger(seed=20260613, n_ops=1500)
        eff = build_effective_ledger(ledger, max_cliffs=2, min_ops_between_cliffs=375)
        cliffs = [op for op in eff if op.type in CLIFF_TYPES]
    with Then("at most 2 cliffs remain"):
        assert len(cliffs) <= 2, error()


@TestScenario
@Name("cliff cap is a pure function of order")
def cliff_cap_is_pure_function_of_order(self):
    with When("I apply the cap twice"):
        ledger = generate_ledger(seed=42, n_ops=500)
        a = build_effective_ledger(ledger, 2, 100)
        b = build_effective_ledger(ledger, 2, 100)
    with Then("the effective ledgers match"):
        assert a == b, error()


@TestScenario
@Name("cliff cap preserves op ids and targets")
def cliff_cap_preserves_op_ids_and_targets(self):
    with When("I build an effective ledger"):
        ledger = generate_ledger(seed=7, n_ops=300)
        eff = build_effective_ledger(ledger, 2, 75)
    with Then("only cliff types are rewritten, to OPTIMIZE"):
        assert [o.op_id for o in eff] == [o.op_id for o in ledger], error()
        for orig, e in zip(ledger, eff):
            assert e.target == orig.target and e.param == orig.param, error()
            if orig.type not in CLIFF_TYPES:
                assert e.type == orig.type, error()
            else:
                assert e.type in (orig.type, OpType.OPTIMIZE), error()


@TestScenario
@Name("cliff min gap enforced")
def cliff_min_gap_enforced(self):
    with Given("two TRUNCATEs closer than the gap"):
        ops = [
            Op(0, OpType.TRUNCATE, 0, 0),
            Op(1, OpType.INSERT, 0, 0),
            Op(2, OpType.TRUNCATE, 0, 0),
        ]
        eff = build_effective_ledger(ops, max_cliffs=2, min_ops_between_cliffs=10)
    with Then("the second cliff is demoted to OPTIMIZE"):
        assert eff[0].type == OpType.TRUNCATE, error()
        assert eff[2].type == OpType.OPTIMIZE, error()


@TestScenario
@Name("cliff demotes drop partition too")
def cliff_demotes_drop_partition_too(self):
    with Given("five DROP PARTITION ops"):
        ops = [Op(i, OpType.DROP_PARTITION, 0, 0) for i in range(5)]
        eff = build_effective_ledger(ops, max_cliffs=1, min_ops_between_cliffs=1)
    with Then("only the first remains a cliff"):
        assert eff[0].type == OpType.DROP_PARTITION, error()
        assert all(o.type == OpType.OPTIMIZE for o in eff[1:]), error()


@TestFeature
@Name("cliff")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
