from lightweight_delete.tests.steps import *
from lightweight_delete.requirements import *
from lightweight_delete.tests.alter_after_delete import (
    alter_drop_partition,
    alter_add_column,
)


@TestScenario
def concurrent_delete_attach_detach_partition_acceptance(self, node=None):
    """Check that concurrent delete and attach detach partition perform correctly with acceptance table."""

    if node is None:
        node = self.context.node

    with Given("I have an acceptance table"):
        create_acceptance_table()

    with When(
        "I insert a lot of data into the table"
    ):
        insert_into_acceptance_table(rows_number=1000000)

    partition = node.query("SELECT partition from system.parts where table = 'acceptance_table' limit 1").output

    with When("I compute expected output"):
        output1 = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT(Id = 1 and has(Ids, 2))"
        ).output

    with When("I compute expected output"):
        output2 = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT(Id = 1 and has(Ids, 2) and Date != '{partition[3:22]}')"
        ).output

    with Then(
        "I perform concurrent operations",
        description="delete odd rows and detach the third partition",
    ):
        for retry in retries(count=5):
            with retry:
                Step(
                    name="delete query",
                    test=delete_query_1_acceptance,
                    parallel=True,
                )()
                Step(
                    name="attach detach in a loop",
                    test=attach_detach_in_loop,
                    parallel=True,
                )(table_name="acceptance_table", partition_expr=f"({partition[2:22]+partition[23:-1]})", node=node, quote=False)

    with Then(
        "I check that rows are deleted",
        description="rows can be not deleted in detached partition",
    ):
        r = node.query(f"SELECT count(*) FROM acceptance_table")
        assert r.output in (output1, output2), error()


@TestScenario
def concurrent_delete_drop_partition_acceptance(self, node=None):
    """Check that concurrent delete and drop partition perform correctly with acceptance table."""

    if node is None:
        node = self.context.node

    with Given("I have an acceptance table"):
        create_acceptance_table()

    with When(
            "I insert a lot of data into the table"
    ):
        insert_into_acceptance_table(rows_number=1000000)

    partition = node.query("SELECT partition from system.parts where table = 'acceptance_table' limit 1").output

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT((Id = 1 and has(Ids, 2)) or Date = '{partition[3:22]}')"
        ).output

    with Then(
        "I perform concurrent operations",
        description="delete odd rows and drop the third partition",
    ):
        for retry in retries(count=5):
            with retry:
                Step(
                    name="delete query",
                    test=delete_query_1_acceptance,
                    parallel=True,
                )()
                Step(name="drop partition", test=alter_drop_partition, parallel=True)(
                    table_name='acceptance_table', partition_expr=f"({partition[2:22]+partition[23:-1]})", node=node, quote=False
                )

    with Then(
        "I check that rows are deleted"
    ):
        r = node.query(f"SELECT count(*) FROM acceptance_table")
        assert r.output == output, error()


@TestScenario
def concurrent_add_drop_column_and_delete(self, node=None):
    """Check that concurrent delete and add drop column perform correctly with acceptance table."""
    if node is None:
        node = self.context.node

    with Given("I have an acceptance table"):
        create_acceptance_table()

    with When(
            "I insert a lot of data into the table"
    ):
        insert_into_acceptance_table(rows_number=1000000)

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT(Id = 1 and has(Ids, 2))"
        ).output

    with Then(
        "I perform concurrent operations",
        description="delete query and add drop column",
    ):
        Step(
            name="delete query", test=delete_query_1_acceptance, parallel=True
        )()
        Step(name="add drop column", test=add_drop_column_in_loop, parallel=True)(
            table_name='acceptance_table',
            column_name="qkrq",
            column_type="Int32",
            default_expr="DEFAULT 777",
            node=node,
        )

    with Then(
        "I check that rows are deleted"
    ):
        r = node.query(f"SELECT count(*) FROM acceptance_table")
        assert r.output == output, error()


@TestScenario
def concurrent_modify_column_and_delete(self, node=None):
    """Check that concurrent delete and add drop column perform correctly with acceptance table."""
    if node is None:
        node = self.context.node

    with Given("I have an acceptance table"):
        create_acceptance_table()

    with When(
            "I insert a lot of data into the table"
    ):
        insert_into_acceptance_table(rows_number=1000000)

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT(Id = 1 and has(Ids, 2))"
        ).output

    with And("I add column to modify it in the loop"):
        alter_add_column(
            table_name='acceptance_table',
            column_name="qkrq",
            column_type="Int32",
            default_expr="DEFAULT 555",
        )

    with Then(
        "I perform concurrent operations",
        description="delete query and modify column",
    ):
        Step(
            name="delete_query", test=delete_query_1_acceptance, parallel=True
        )()
        Step(name="modify column", test=modify_column_in_loop, parallel=True)(
            table_name='acceptance_table', column_name="qkrq", node=node
        )

    with Then(
        "I check that rows are deleted"
    ):
        r = node.query(f"SELECT count(*) FROM acceptance_table")
        assert r.output == output, error()


@TestScenario
def concurrent_clear_update_and_delete(self, node=None):
    """Check that concurrent clear column update column and delete perform correctly with acceptance table."""
    if node is None:
        node = self.context.node

    with Given("I have an acceptance table"):
        create_acceptance_table()

    with When(
            "I insert a lot of data into the table"
    ):
        insert_into_acceptance_table(rows_number=1000000)

    with When("I compute expected output"):
        output = node.query(
            f"SELECT count(*) FROM acceptance_table WHERE NOT(Id = 1 and has(Ids, 2))"
        ).output

    with And("I add column to modify it in the loop"):
        alter_add_column(table_name='acceptance_table', column_name="qkrq", column_type="Int32")

    with Then(
        "I perform concurrent operations",
        description="delete query and clear and update column",
    ):
        Step(
            name="delete query", test=delete_query_1_acceptance, parallel=True
        )()
        Step(name="clear update column", test=clear_update_in_loop, parallel=True)(
            table_name='acceptance_table', column_name="qkrq", node=node
        )

    with Then("I check that rows are deleted"):
        r = node.query(f"SELECT count(*) FROM acceptance_table")
        assert r.output == output, error()


@TestFeature
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Performance_Acceptance_OnTimeDataset_DeleteQueryExecutionTime("1.0"),
)
@Name("acceptance concurrent alter and delete")
def feature(self, node="clickhouse1"):
    """Check clickhouse support concurrent lightweight delete and alter operations on acceptance table."""
    self.context.node = self.context.cluster.node(node)

    if self.context.use_alter_delete:
        xfail(
            reason="alter delete does not support concurrent mutations",
        )

    for scenario in loads(current_module(), Scenario):
        scenario()
