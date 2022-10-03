import time

from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_DiskSpace("1.0"))
def disk_space(self, node=None):
    """Check that clickhouse does not greatly increase table size after lightweight delete."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the table",
        description="100 partitions 1 part block_size=10000",
    ):
        insert(
            table_name=table_name,
            partitions=100,
            parts_per_partition=1,
            block_size=1000,
            settings=[("mutations_sync", "2")],
        )

    with When("I measure table size on disk"):
        size_on_disk_before_deletions = int(
            node.query(
                f"select sum(bytes_on_disk) from system.parts where table = '{table_name}'"
            ).output
        )

    with When("I perform a lot of deletes"):
        for i in range(30):
            for j in range(20):
                delete(
                    table_name=table_name,
                    condition=f"id = {i} and x = {j}",
                    settings=[],
                )

    with Then("I check table size on disk does not increased a lot"):
        size_on_disk_after_deletions = int(
            node.query(
                f"select sum(bytes_on_disk) from system.parts where table = '{table_name}' and active"
            ).output
        )
        assert size_on_disk_after_deletions < 2 * size_on_disk_before_deletions, error()


@TestFeature
@Name("disk space")
def feature(self, node="clickhouse1"):
    """Check that clickhouse does not greatly increase table size after lightweight delete."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
