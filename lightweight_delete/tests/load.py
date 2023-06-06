from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Load_Insert("1.0"),
    RQ_SRS_023_ClickHouse_LightweightDelete_Load_ExcessiveMutations("1.0"),
)
def load_inserts(self, node=None):
    """Check that clickhouse perform correctly with high insert pressure and lightweight delete."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the table",
        description="10 partitions 1 part block_size=1000",
    ):
        insert(
            table_name=table_name,
            partitions=10,
            parts_per_partition=1,
            block_size=1000,
            settings=[("mutations_sync", "2")],
        )

    # try:
    #     with When("I stop merges"):
    #         node.query("SYSTEM STOP MERGES")

    with When("I perform a lot of inserts and deletes in parallel"):
        Step(
            name="delete rows in cycle",
            test=deletes,
            parallel=True,
        )(table_name=table_name, deletes_number=100)
        Step(
            name="insert rows in cycle",
            test=inserts,
            parallel=True,
        )(table_name=table_name, inserts_number=30)

    with Then("I perform last delete"):
        delete(table_name=table_name, condition="id < 2", settings=[])

    # finally:
    #     with Finally("I resume merges"):
    #         node.query("SYSTEM START MERGES")

    with Then("I check data is correctly inserted and deleted"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) from {table_name}")
                assert r.output == "8000", error()

    with Then("I check number of mutations clickhouse created"):
        r = node.query(
            f"SELECT count(*) from system.mutations where (table = '{table_name}')"
        )
        assert int(r.output) < 105, error()


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_Merges("1.0"))
def load_merges(self, node=None):
    """Check that clickhouse perform correctly with concurrent lightweight delete and a lot of merges."""
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the table",
        description="10 partitions 1 part block_size=1000",
    ):
        insert(
            table_name=table_name,
            partitions=10,
            parts_per_partition=1,
            block_size=1000,
            settings=[("mutations_sync", "2")],
        )

    with When("I perform a lot of merges and deletes in parallel"):
        Step(
            name="delete rows in cycle",
            test=deletes,
            parallel=True,
        )(table_name=table_name, deletes_number=100)
        Step(
            name="merges in cycle",
            test=merges,
            parallel=True,
        )(table_name=table_name, merges_number=30)

    with Then("I check data is correctly inserted and deleted"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) from {table_name}")
                assert r.output == "8000", error()

    with Then("I check number of mutations clickhouse created"):
        r = node.query(
            f"SELECT count(*) from system.mutations where (table = '{table_name}')"
        )
        assert int(r.output) < 105, error()


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_ExcessiveMutations("1.0"))
def load_excessive_mutations(self, node=None):
    """Check that clickhouse do not touch parts in which lightweight delete does not delete anything."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the table",
        description="10 partitions 1 part block_size=1000",
    ):
        insert(
            table_name=table_name,
            partitions=10,
            parts_per_partition=1,
            block_size=1000,
            settings=[("mutations_sync", "2")],
        )

    # try:
    # with When("I stop merges"):
    #     node.query("SYSTEM STOP MERGES")

    with When("I perform a lot of deletes"):
        delete(
            table_name=table_name,
            condition=f"(id < 4) and (x < 500)",
            settings=[],
        )

    with Then("I check clickhouse did not create a lot of mutations"):
        r = node.query(
            f"SELECT sum(parts_to_do) from system.mutations where table = '{table_name}'"
        )
        assert int(r.output) < 5, error()

    # finally:
    #     with Finally("I resume merges"):
    #         node.query("SYSTEM START MERGES")


@TestFeature
@Name("load")
def feature(self, node="clickhouse1"):
    """Check that clickhouse perform correctly with high load."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
