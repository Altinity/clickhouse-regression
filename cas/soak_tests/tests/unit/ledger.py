from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import BARRIER_TYPES, OpType, generate_ledger


@TestScenario
@Name("ledger is reproducible")
def ledger_is_reproducible(self):
    with When("I generate two ledgers with the same seed"):
        a = generate_ledger(seed=7, n_ops=200)
        b = generate_ledger(seed=7, n_ops=200)
    with Then("they match, and a different seed does not"):
        assert a == b, error()
        assert generate_ledger(seed=8, n_ops=200) != a, error()


@TestScenario
@Name("op ids are dense and ordered")
def op_ids_are_dense_and_ordered(self):
    with When("I generate 50 ops"):
        ops = generate_ledger(seed=1, n_ops=50)
    with Then("op_id is 0..49"):
        assert [o.op_id for o in ops] == list(range(50)), error()


@TestScenario
@Name("targets both replicas and has all types")
def targets_both_replicas_and_has_all_types(self):
    with When("I generate 500 ops"):
        ops = generate_ledger(seed=3, n_ops=500)
    with Then("both replica targets and mutation types appear"):
        assert {o.target for o in ops} == {0, 1}, error()
        kinds = {o.type for o in ops}
        assert OpType.INSERT in kinds, error()
        assert OpType.UPDATE in kinds, error()
        assert OpType.DELETE in kinds, error()
        n_trunc = sum(1 for o in ops if o.type == OpType.TRUNCATE)
        assert 0 <= n_trunc <= 10, error()


@TestScenario
@Name("barrier types are mutations")
def barrier_types_are_mutations(self):
    assert BARRIER_TYPES == (
        OpType.UPDATE,
        OpType.DELETE,
        OpType.TRUNCATE,
        OpType.DROP_PARTITION,
    ), error()
    assert OpType.INSERT not in BARRIER_TYPES, error()
    assert OpType.OPTIMIZE not in BARRIER_TYPES, error()


@TestFeature
@Name("ledger")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
