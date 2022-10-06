from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Load_Zookeeper("1.0"))
def load_zookeeper(self):
    """Check that clickhouse do not create huge transactions in zookeeper during lightweight delete operations."""

    table_name = getuid()

    with Given("I have replicated table"):
        create_replicated_table(table_name=table_name)

    with When("I insert data into replicated table"):
        insert_replicated(
            table_name=table_name,
            partitions=100,
            parts_per_partition=1,
            block_size=1000,
        )

    name = "clickhouse2"
    self.context.node = node = self.context.cluster.node(name)

    with When("I check data is inserted on second node"):
        for attempt in retries(delay=1, timeout=30):
            with attempt:
                r = node.query(f"select count(*) from {table_name}")
                assert int(r.output) == 100000, error()

    name = "clickhouse1"
    self.context.node = node = self.context.cluster.node(name)
    try:
        node.query("SYSTEM STOP REPLICATION QUEUES")

        with When(
            "I perform a lot of deletes and wait mutations are in replication queue"
        ):
            for i in range(10):
                for j in range(200):
                    delete(
                        table_name=table_name,
                        condition=f"id = {i} and x = {j}",
                        settings=[],
                    )
            time.sleep(10)

    finally:
        node.query("SYSTEM START REPLICATION QUEUES")

    name = "clickhouse2"
    self.context.node = node = self.context.cluster.node(name)
    with Then("I delete on second node takes a little time"):
        for attempt in retries(delay=1, timeout=30):
            with attempt:
                r = node.query(f"select count(*) from {table_name}")
                assert int(r.output) == 100000 - 2000, error()


@TestFeature
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_EventualConsistency("1.0"))
@Name("zookeeper load")
def feature(self):
    """Check that clickhouse do not create huge transactions in zookeeper during lightweight delete operations."""

    table_engine = "ReplicatedMergeTree"

    self.context.table_engine = table_engine
    for scenario in loads(current_module(), Scenario):
        scenario()
