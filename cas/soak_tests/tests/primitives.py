from testflows.core import *

import time

from cas.soak_tests.oracle import Model, Op, OpType
from cas.soak_tests.steps.checkpoint import (
    pool_is_clean,
    quiesce,
    replicas_match_model,
    run_cas_fsck,
    run_cas_gc_dryrun,
)
from cas.soak_tests.steps.table import soak_table
from cas.soak_tests.steps.workload import insert_block


def ins(op_id, n):
    return Op(op_id, OpType.INSERT, 0, n - 1)


@TestScenario
@Name("insert matches model then fsck and dryrun are clean")
def insert_matches_model_then_pool_is_clean(self):
    seed = 1
    n = 3
    # Wall-clock base so MergeTree TTL (90 minutes) does not expire the rows immediately.
    base_time = int(time.time())
    with Given("a soak table on storage_policy ca"):
        table = soak_table()
        model = Model(seed=seed, base_time=base_time)

    with When("I INSERT a 3-row block on replica 1 and apply it to the model"):
        insert_block(
            table=table,
            seed=seed,
            op_id=0,
            n=n,
            base_time=base_time,
            settings="SETTINGS async_insert=0",
        )
        model.apply(ins(0, n))

    with When("I quiesce both replicas"):
        now = quiesce(table=table)

    with Then("both replicas match the model"):
        replicas_match_model(table=table, model=model, now=now)

    with When("I run cas-fsck --detail and cas-gc-dryrun"):
        fsck = run_cas_fsck(detail=True)
        dryrun = run_cas_gc_dryrun()

    with Then("dangling is 0, stale_edge is clean, dryrun is a subset of pipeline keys"):
        pool_is_clean(fsck_result=fsck, dryrun_result=dryrun, detail=True)


@TestFeature
@Name("primitives")
def feature(self):
    """Live checkpoint primitives on a tiny CAS table. Not a soak."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
