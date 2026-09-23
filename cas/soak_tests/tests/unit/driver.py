import time

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle import Model, Op, OpType
from cas.soak_tests.steps.driver import Driver


class RecordingNode:
    def __init__(self, log, delay_insert=0.0):
        self.log = log
        self.delay_insert = delay_insert

    def command(self, sql, timeout=None):
        if sql.startswith("INSERT"):
            if self.delay_insert:
                time.sleep(self.delay_insert)
            self.log.append("insert_sql")
        elif sql.startswith("OPTIMIZE"):
            self.log.append("optimize_sql")
        elif sql.startswith("ALTER TABLE") and "UPDATE" in sql:
            self.log.append("update_sql")
        elif sql.startswith("ALTER TABLE") and "DELETE" in sql:
            self.log.append("delete_sql")
        elif sql.startswith("TRUNCATE"):
            self.log.append("truncate_sql")
        else:
            self.log.append(sql.split()[0])


def _driver(log, workers=2, delay_insert=0.0):
    model = Model(seed=1, base_time=1_700_000_000)
    nodes = [RecordingNode(log, delay_insert), RecordingNode(log, delay_insert)]
    return Driver(
        http_nodes=nodes,
        table="ca_soak.t",
        model=model,
        seed=1,
        base_time=1_700_000_000,
        workers=workers,
    )


def ins(op_id, n, target=0):
    return Op(op_id, OpType.INSERT, target, n - 1)


@TestScenario
@Name("insert applies model before sql")
def insert_applies_model_before_sql(self):
    log = []
    d = _driver(log)
    try:
        with When("I execute an INSERT"):
            d.execute(ins(0, 3))
        with Then("the model has the rows before drain"):
            assert d.model.aggregates(now=1_700_000_000)["count"] == 3, error()
        d.drain()
        with Then("the SQL ran"):
            assert log == ["insert_sql"], error()
    finally:
        d.close()


@TestScenario
@Name("barrier drains inserts then sql then model")
def barrier_drains_inserts_then_sql_then_model(self):
    log = []
    d = _driver(log, delay_insert=0.05)
    try:
        with When("I INSERT then UPDATE"):
            d.execute(ins(0, 4))
            d.execute(Op(1, OpType.UPDATE, 0, 0))
        with Then("insert SQL precedes the barrier SQL"):
            assert log == ["insert_sql", "update_sql"], error()
        with Then("the model has the insert and the update"):
            agg = d.model.aggregates(now=1_700_000_000)
            assert agg["count"] == 4, error()
            assert agg["sum_version"] >= 4, error()
    finally:
        d.close()


@TestScenario
@Name("optimize has no model effect")
def optimize_has_no_model_effect(self):
    log = []
    d = _driver(log)
    try:
        d.execute(ins(0, 2))
        d.drain()
        before = d.model.aggregates(now=1_700_000_000)
        with When("I OPTIMIZE"):
            d.execute(Op(1, OpType.OPTIMIZE, 0, 0))
            d.drain()
        with Then("aggregates are unchanged and SQL ran"):
            assert d.model.aggregates(now=1_700_000_000) == before, error()
            assert "optimize_sql" in log, error()
    finally:
        d.close()


@TestScenario
@Name("drop partition uses truncate sql")
def drop_partition_uses_truncate_sql(self):
    log = []
    d = _driver(log)
    try:
        d.execute(ins(0, 5))
        d.drain()
        with When("I DROP PARTITION"):
            d.execute(Op(1, OpType.DROP_PARTITION, 0, 0))
        with Then("SQL is TRUNCATE and the model is empty"):
            assert log[-1] == "truncate_sql", error()
            assert d.model.aggregates(now=1_700_000_000)["count"] == 0, error()
    finally:
        d.close()


@TestScenario
@Name("transport resilient insert reroutes")
def transport_resilient_insert_reroutes(self):
    import urllib.error

    class Flaky:
        def __init__(self, fail_first=False):
            self.fail_first = fail_first
            self.calls = 0

        def command(self, sql, timeout=None):
            self.calls += 1
            if self.fail_first and self.calls == 1:
                raise urllib.error.URLError(
                    ConnectionRefusedError(111, "Connection refused")
                )

    n0, n1 = Flaky(True), Flaky(False)
    model = Model(seed=1, base_time=1_700_000_000)
    d = Driver(
        http_nodes=[n0, n1],
        table="ca_soak.t",
        model=model,
        seed=1,
        base_time=1_700_000_000,
        workers=1,
        transport_resilient=True,
        transport_attempts=5,
    )
    try:
        with When("I INSERT while replica 0 is down"):
            d.execute(ins(0, 2))
            d.drain()
        with Then("the driver reroutes to replica 1 and the model applied once"):
            assert n0.calls >= 1 and n1.calls >= 1, error()
            assert d.model.aggregates(now=1_700_000_000)["count"] == 2, error()
            assert d.transport_retries >= 1, error()
    finally:
        d.close()


@TestFeature
@Name("driver")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
