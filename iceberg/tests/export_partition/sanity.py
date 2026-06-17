"""Sanity checks for EXPORT PARTITION to Iceberg.

These scenarios are deliberately simple and fast; they verify the happy
path so that the suite catches catastrophic regressions quickly. Deeper
correctness is covered by the other modules in this package.

Every scenario runs under all three catalog modes (see ``feature.py``).
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Sanity,
    RQ_Iceberg_ExportPartition_Sanity_EmptyPartition,
    RQ_Iceberg_ExportPartition_Sanity_CrossReplicaInitiator,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
    get_partition_ids,
    count_rows,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    export_all_partitions,
    prepare_export_partition_settings,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
    as_destination_name,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Sanity("1.0"))
@Name("export single partition")
def single_partition(self, minio_root_user, minio_root_password):
    """Export one partition and verify row count and content match the source."""
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert data into two partitions"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2020), (4, 2021)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("only the 2020 partition rows land in the destination"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("data in the destination matches the source for that partition"):
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partition_where="year = 2020",
            order_by="id",
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Sanity("1.0"))
@Name("export all partitions")
def all_partitions(self, minio_root_user, minio_root_password):
    """Export every partition of the source table and verify parity."""
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert into three partitions"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2021), (4, 2022), (5, 2022)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export every partition"):
        exported = export_all_partitions(
            source_table=source_table,
            destination=destination,
        )
        assert sorted(exported) == ["2020", "2021", "2022"], error()

    with Then("the destination has the same row count as the source"):
        expected = count_rows(table_name=source_table)
        assert_destination_row_count(
            destination=destination,
            expected=expected,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("all rows match the source"):
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Sanity("1.0"))
@Name("export multiple partitions in one ALTER")
def multi_partition_alter(self, minio_root_user, minio_root_password):
    """Verify the comma-separated ``ALTER TABLE ... EXPORT PARTITION ..., EXPORT PARTITION ...`` form.

    The PR explicitly supports multiple EXPORT PARTITION commands in a single
    ALTER statement; this is the only scenario here that exercises that form
    directly instead of going through :func:`export_partition` (which uses
    one statement per partition).
    """
    node = self.context.node
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert into two partitions"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2020), (4, 2021)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    dest_name = as_destination_name(destination)

    with When("export two partitions in a single ALTER statement"):
        node.query(
            f"ALTER TABLE {source_table}\n"
            f"  EXPORT PARTITION ID '2020' TO TABLE {dest_name},\n"
            f"  EXPORT PARTITION ID '2021' TO TABLE {dest_name}",
            settings=prepare_export_partition_settings(
                self.context.catalog, None
            ),
        )

    with And("wait for both exports to complete"):
        wait_for_export_status(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            expected_status="COMPLETED",
        )
        wait_for_export_status(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
            expected_status="COMPLETED",
        )

    with Then("all source rows made it to the destination"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Sanity_EmptyPartition("1.0"))
@Name("export empty partition")
def empty_partition(self, minio_root_user, minio_root_password):
    """Exporting after a partition has been dropped from the source must still
    leave the destination consistent for the surviving partition.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert one row then drop its partition"):
        insert_data(table_name=source_table, values="(1, 2020)")
        self.context.node.query(
            f"ALTER TABLE {source_table} DROP PARTITION ID '2020' "
            f"SETTINGS mutations_sync = 2"
        )
        insert_data(table_name=source_table, values="(2, 2021)")

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("export the remaining partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
        )

    with And("destination has exactly the one row that survived"):
        assert_destination_row_count(
            destination=destination,
            expected=1,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Sanity_CrossReplicaInitiator("1.0"))
@Name("export across replicas")
def cross_replica_export(self, minio_root_user, minio_root_password):
    """Insert on replica1, trigger the EXPORT PARTITION from replica2.

    Only replicas that can see the parts (via SYNC REPLICA) should be able to
    drive the export. We also verify the status is readable from the replica
    that triggered the export.
    """
    if not hasattr(self.context, "nodes") or len(self.context.nodes) < 2:
        skip("need at least two ClickHouse replicas")

    replica1 = self.context.nodes[0]
    replica2 = self.context.nodes[1]
    table_name = f"mt_{getuid()}"

    with Given("create the replicated table on both replicas"):
        for i, node in enumerate([replica1, replica2], start=1):
            create_replicated_mergetree(
                table_name=table_name,
                columns=SIMPLE_COLUMNS,
                partition_by=SIMPLE_PARTITION_BY,
                zk_path=f"/clickhouse/tables/{table_name}",
                replica_name=f"r{i}",
                node=node,
            )

    with And("insert on replica1 and sync replica2"):
        insert_data(
            table_name=table_name,
            values="(1, 2020), (2, 2020), (3, 2021)",
            node=replica1,
        )
        replica2.query(f"SYSTEM SYNC REPLICA {table_name}")

    with And("create the Iceberg destination on replica2"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica2,
        )

    with When("export from replica2"):
        export_partition(
            source_table=table_name,
            destination=destination,
            partition_id="2020",
            node=replica2,
        )

    with Then("destination contains the two rows from the 2020 partition"):
        assert_destination_row_count(
            destination=destination,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=replica2,
        )


@TestFeature
@Name("sanity")
def feature(self, minio_root_user, minio_root_password):
    """Sanity checks for EXPORT PARTITION to Iceberg."""
    Scenario(test=single_partition, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=all_partitions, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=multi_partition_alter, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=empty_partition, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=cross_replica_export, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
