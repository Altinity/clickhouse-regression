from lightweight_delete.requirements import *
from lightweight_delete.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Backups_Mask("1.0"))
def backup_concurrent_delete(
    self, partitions=100, parts_per_partition=1, block_size=10000, node=None
):
    """Check that clickhouse keeps lightweight delete mask during backup."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the tables",
        description=f"{partitions} partitions, "
        f"{parts_per_partition} parts in each partition, block_size={block_size}",
    ):
        insert(
            table_name=table_name,
            partitions=partitions,
            parts_per_partition=parts_per_partition,
            block_size=block_size,
        )

    with When("I delete from the table"):
        delete(table_name=table_name, condition="x < 2000", settings=[])

    with When("I wait rows are deleted"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()

    with When("I create backup"):
        node.query(f"BACKUP TABLE {table_name} TO Disk('backups', '1.zip')")

    with Then("I perform back up"):
        node.query(f"drop table {table_name} sync")
        node.query(f"RESTORE TABLE {table_name} FROM Disk('backups', '1.zip')")

    with Then("I check that rows are deleted"):
        for attempt in retries(timeout=60, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()
                r = node.query(f"SELECT count(*) FROM {table_name} where x < 20")
                assert int(r.output) == 0, error()


@TestScenario
@Requirements(
    RQ_SRS_023_ClickHouse_LightweightDelete_Backups_BackupAfterLightweightDelete("1.0")
)
def backup_after_delete(
    self, partitions=100, parts_per_partition=1, block_size=10000, node=None
):
    """Check that clickhouse support using backups after lightweight delete."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the tables",
        description=f"{partitions} partitions, "
        f"{parts_per_partition} parts in each partition, block_size={block_size}",
    ):
        insert(
            table_name=table_name,
            partitions=partitions,
            parts_per_partition=parts_per_partition,
            block_size=block_size,
        )

    with When("I delete from the table"):
        delete(table_name=table_name, condition="x < 2000", settings=[])

    with When("I wait rows are deleted"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()

    with When("I create backup"):
        node.query(f"BACKUP TABLE {table_name} TO Disk('backups', '2.zip')")

    with When("I force merges to finish lightweight delete"):
        optimize_table(table_name=table_name, final=True)

    with Then("I perform back up"):
        node.query(f"drop table {table_name} sync")
        node.query(f"RESTORE TABLE {table_name} FROM Disk('backups', '2.zip')")

    with Then("I check that rows are deleted"):
        for attempt in retries(timeout=60, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()
                r = node.query(f"SELECT count(*) FROM {table_name} where x < 20")
                assert int(r.output) == 0, error()


@TestScenario
@Requirements(RQ_SRS_023_ClickHouse_LightweightDelete_Backups_BackupPartition("1.0"))
def backup_concurrent_delete_partitions(
    self, partitions=100, parts_per_partition=1, block_size=10000, node=None
):
    """Check that clickhouse support using partition backups with lightweight delete."""
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_table(table_name=table_name)

    with When(
        "I insert data into the tables",
        description=f"{partitions} partitions, "
        f"{parts_per_partition} parts in each partition, block_size={block_size}",
    ):
        insert(
            table_name=table_name,
            partitions=partitions,
            parts_per_partition=parts_per_partition,
            block_size=block_size,
        )

    with When("I delete from the table"):
        delete(table_name=table_name, condition="x < 2000", settings=[])

    with When("I wait rows are deleted"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()

    with When("I create backup"):
        node.query(f"BACKUP TABLE {table_name} TO Disk('backups', '3.zip')")

    with Then("I perform back up"):
        node.query(f"ALTER TABLE {table_name} DROP PARTITION '2'")
        node.query(
            f"RESTORE TABLE {table_name} PARTITIONS '2' FROM Disk('backups', '3.zip') SETTINGS allow_non_empty_tables=true"
        )

    with Then("I check that rows are deleted"):
        for attempt in retries(timeout=60, delay=1):
            with attempt:
                r = node.query(f"SELECT count(*) FROM {table_name}")
                assert int(r.output) == 800000, error()
                r = node.query(f"SELECT count(*) FROM {table_name} where x < 20")
                assert int(r.output) == 0, error()


@TestFeature
@Name("backup")
def feature(self, node="clickhouse1"):
    """Check that clickhouse support backups with lightweight delete."""
    self.context.node = self.context.cluster.node(node)
    self.context.table_engine = "MergeTree"
    for scenario in loads(current_module(), Scenario):
        scenario()
