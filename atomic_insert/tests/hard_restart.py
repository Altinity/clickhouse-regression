import random

from atomic_insert.requirements import *
from atomic_insert.tests.steps import *
from testflows.asserts import error


@TestStep(When)
def kill_clickhouse_process(self, signal="SIGKILL", node=None):
    """Kill server using a signal."""
    if node is None:
        node = self.context.node

    with By("sending SIGKILL to clickhouse process"):
        pid = node.clickhouse_pid()
        node.command(f"kill -{signal} {pid}", exitcode=0, steps=False)

    with And("checking pid does not exist"):
        for attempt in retries(timeout=100, delay=1):
            with attempt:
                if node.command(f"ps {pid}", steps=False, no_checks=True).exitcode != 1:
                    fail("pid still alive")

    with And("deleting clickhouse server pid file"):
        node.command("rm -rf /tmp/clickhouse-server.pid", exitcode=0, steps=False)


@TestOutline
def hard_restart(
    self,
    table_engine,
    signal="SIGKILL",
    node=None,
    numbers_value=random.randint(1, 20000000),
):
    """Check that clickhouse completes atomic INSERT operation or
    leaves data in the same state after a hard restart by using signal.
    """
    if node is None:
        node = self.context.node

    uid = getuid()

    database = f"test_database{uid}"

    tables = [
        f"test_database{uid}.table_A{uid}",
        f"test_database{uid}.table_B{uid}",
        f"test_database{uid}.table_B_mv{uid}",
    ]

    with Given("I create database and core table in this database"):
        create_table(
            table_engine=table_engine,
            node=node,
            database=database,
            core_table=tables[0],
        )

    numbers = numbers_value
    numbers2 = numbers + 737

    with When(
        "I make different inserts into table and kill clickhouse server process in parallel"
    ):
        By("I make transaction insert", test=simple_transaction_insert, parallel=True)(
            core_table=tables[0], numbers=numbers, no_checks=True
        )

        By(
            name="killing clickhouse process",
            test=kill_clickhouse_process,
            parallel=True,
        )(signal=signal)

    with And("I restart server"):
        node.start_clickhouse()

    with Then("I compute expected output"):
        output1 = f"{numbers2}"
        output2 = "737"

    with Then("I check that either rows are deleted completely or data is unchanged"):
        for attempt in retries(timeout=100, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) + 737 FROM {tables[0]}")
                assert r.output in (output1, output2), error()


@TestScenario
def hard_restart_with_small_insert(self, table_engine, signal):
    """Check that small insert completes with hard reset."""
    hard_restart(table_engine=table_engine, signal=signal, node=None, numbers_value=10)


@TestScenario
def hard_restart_with_big_insert(self, table_engine, signal):
    """Check that uncompleted big insert leaves data in the same state with hard restart."""
    hard_restart(
        table_engine=table_engine, signal=signal, node=None, numbers_value=10000000
    )


@TestScenario
@Repeat(20, until="fail")
def hard_restart_with_random_insert(self, table_engine, signal):
    """Check series of random inserts work correctly with parallel hard reset."""
    hard_restart(
        table_engine=table_engine,
        signal=signal,
        node=None,
        numbers_value=random.randint(1, 20000000),
    )


@TestFeature
@Name("hard restart")
@Requirements()
def feature(self, node="clickhouse1"):
    """Check that clickhouse either finishes the atomic INSERT or return the system
    to the state before the atomic INSERT started.
    """
    self.context.node = self.context.cluster.node(node)

    self.context.engines = ["MergeTree"]
    signal = "SIGKILL"

    with Feature(f"{signal}"):
        for table_engine in self.context.engines:
            for scenario in loads(current_module(), Scenario):
                scenario(table_engine=table_engine, signal=signal)
