from testflows.core import *
from testflows.asserts import error
import helpers.config.config_d as config_d
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.common import getuid
from helpers.queries import *
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    export_partitions,
    get_partitions,
    source_matches_destination,
    wait_for_export_to_complete,
)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Settings_AllowExperimental("1.0"))
def export_setting(self):
    """Check that the export setting is settable when exporting partitions."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and 2 empty S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
        )
        s3_table_name1 = create_s3_table(table_name="s3_1", create_new_bucket=True)
        s3_table_name2 = create_s3_table(table_name="s3_2", create_new_bucket=True)

    with When("I export partitions to the first S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name1,
            node=self.context.node,
        )

    with And("I export partitions to the second S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name2,
            node=self.context.node,
        )

    with And("I read data from all tables"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data1 = select_all_ordered(
            table_name=s3_table_name1, node=self.context.node
        )
        destination_data2 = select_all_ordered(
            table_name=s3_table_name2, node=self.context.node
        )

    with Then("All tables should have the same data"):
        assert source_data == destination_data1, error()
        assert source_data == destination_data2, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SchemaCompatibility("1.0"))
def mismatched_columns(self):
    """Test exporting partitions when source and destination tables have mismatched columns."""

    source_table = f"source_{getuid()}"
    with Given("I create a source table and S3 table with different columns"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with When("I export partitions to the S3 table"):
        results = export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            exitcode=1,
            check_export=False,
        )

    with Then("I should see an error related to mismatched columns"):
        assert results[0].exitcode == 122, error()
        assert "Tables have different structure" in results[0].output, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_S3("1.0"))
def basic_table(self):
    """Test exporting partitions of a basic table."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = partitioned_replicated_merge_tree_table(
            table_name=f"source_{getuid()}",
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
        )
        s3_table = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_EmptyPartition("1.0"))
def empty_table(self):
    """Test exporting partitions from an empty table."""

    source_table = f"source_{getuid()}"
    with Given("I create empty source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            populate=False,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be empty"):
        assert source_data == [], error()
        assert destination_data == [], error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_PartitionKeyTypes("1.0"))
def no_partition_by(self):
    """Test exporting partitions when the source table has no PARTITION BY type."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="tuple()",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, partition_by="tuple()"
        )

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_PartitionContent("1.0"))
def wide_and_compact_parts(self):
    """Check that exporting partitions with both wide and compact parts is supported."""

    source_table = f"source_{getuid()}"
    with Given("I create a source table with wide and compact parts"):
        create_replicated_partitioned_table_with_compact_and_wide_parts(
            table_name=source_table
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_LargePartitions("1.0"))
def large_export(self):
    """Test exporting partitions with many parts."""

    source_table = f"source_{getuid()}"
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            number_of_parts=100,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def replicated_partition_exports_local_mode_peer_replica(self):
    """Altinity/ClickHouse#1500: local system.replicated_partition_exports on a peer replica.

    With ``export_merge_tree_partition_system_table_prefer_remote_information = 0``,
    the table is served from local state. A replica that did not run the ALTER must
    still list COMPLETED exports after another replica finishes the export.
    """

    source_table = f"source_{getuid()}"
    initiator = self.context.node
    peer = self.context.node2
    with Given("I create a populated source table and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)
        partitions = get_partitions(table_name=source_table, node=initiator)

    select_settings = [
        ("export_merge_tree_partition_system_table_prefer_remote_information", "0"),
    ]

    with When("I export partitions from the first replica"):

        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=initiator,
        )

    with Then(
        "the second replica sees COMPLETED rows in system.replicated_partition_exports "
        "when preferring local information"
    ):
        for partition in partitions:
            for attempt in retries(timeout=120, delay=2):
                with attempt:
                    r = peer.query(
                        "SELECT count() FROM system.replicated_partition_exports WHERE "
                        f"source_table = '{source_table}' AND partition_id = '{partition}' "
                        "AND status = 'COMPLETED'",
                        settings=select_settings,
                        exitcode=0,
                    )
                    assert int(r.output.strip()) >= 1, error()

    with And("data still matches on the initiator"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
            source_node=initiator,
            destination_node=initiator,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_Concurrency("1.0"),
    RQ_ClickHouse_ExportPartition_ServerSettings_BackgroundMovePoolSize("1.0"),
)
def partition_export_tight_pool_lock_inside_task(self):
    """Altinity/ClickHouse#1499: scheduler slot counter matches successful schedules.

    ``ExportPartitionTaskScheduler`` increments ``scheduled_exports_count`` only after a
    part-level export is actually queued. With ``background_move_pool_size=2`` and
    ``export_merge_tree_partition_lock_inside_the_task=1``, transient
    ``scheduleMoveTask`` failures are likely while many parts are pending; counting
    failures toward the cap would under-schedule within the same scheduler run and
    can stall throughput until a later tick.
    """

    source_table = f"source_{getuid()}"

    with Given(
        "I cap background move threads and create a multi-partition source table"
    ):
        config_d.create_and_add(
            entries={"background_move_pool_size": "2"},
            config_file="background_move_pool_size_pr1499.xml",
            node=self.context.node,
        )
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
            number_of_partitions=6,
            number_of_parts=4,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When(
        "I export all partitions with lock_inside_the_task (stresses the scheduler)"
    ):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            settings=[("export_merge_tree_partition_lock_inside_the_task", "1")],
        )

    with Then("all partition data is exported successfully"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestFeature
@Name("sanity")
@Requirements(RQ_ClickHouse_ExportPartition_Settings_AllowExperimental("1.0"))
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=empty_table)
    Scenario(run=basic_table)
    Scenario(run=replicated_partition_exports_local_mode_peer_replica)
    Scenario(run=partition_export_tight_pool_lock_inside_task)
    Scenario(run=no_partition_by)
    Scenario(run=mismatched_columns)
    Scenario(run=wide_and_compact_parts)
    if self.context.stress:
        Scenario(run=large_export)
