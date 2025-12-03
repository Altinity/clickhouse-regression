from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *
import helpers.config.config_d as config_d


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
def system_events_and_part_log(self):
    """Check part exports are logged correctly in both system.events and system.part_log."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I read the initial logged export events"):
        initial_events = get_export_events(node=self.context.node)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with And("I read the final logged export events and part log"):
        final_events = get_export_events(node=self.context.node)
        part_log = get_part_log(node=self.context.node)

    with Then("I check that the number of part exports is correct"):
        assert (
            final_events["PartsExports"] - initial_events["PartsExports"] == 5
        ), error()

    with And("I check that the part log contains the correct parts"):
        parts = get_parts(table_name=source_table, node=self.context.node)
        for part in parts:
            assert part in part_log, error()


@TestOutline(Scenario)
@Examples(
    "duplicate_policy, duplicate_count, failure_count",
    [
        ("overwrite", 0, 0),
        ("error", 5, 5),
        ("skip", 5, 0),
    ],
)
@Requirements(
    RQ_ClickHouse_ExportPart_Idempotency("1.0"),
    RQ_ClickHouse_ExportPart_Settings_FileAlreadyExistsPolicy("1.0"),
)
def duplicate_logging(self, duplicate_policy, duplicate_count, failure_count):
    """Check duplicate exports are logged correctly in system.events."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I read the initial export events"):
        initial_events = get_export_events(node=self.context.node)

    with When("I try to export the parts twice"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            settings=[
                ("export_merge_tree_part_file_already_exists_policy", duplicate_policy)
            ],
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("Check logs for correct number of duplicate and failed exports"):
        final_events = get_export_events(node=self.context.node)
        assert (
            final_events["PartsExportDuplicated"]
            - initial_events["PartsExportDuplicated"]
            == duplicate_count
        ), error()
        assert (
            final_events["PartsExportFailures"] - initial_events["PartsExportFailures"]
            == failure_count
        ), error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPart_Metrics_Export("1.0"),
)
def system_exports_and_metrics(self):
    """Check that system.exports table tracks export operations before they complete."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=20000,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow down the network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("I check that system.exports and system.metrics contain some parts"):
        exports = get_system_exports(node=self.context.node)
        assert get_num_active_exports(node=self.context.node) > 0, error()
        assert len(exports) > 0, error()
        assert [source_table, s3_table_name] in exports, error()

    with And(
        "I verify that system.exports and system.metrics are empty after exports complete"
    ):
        wait_for_all_exports_to_complete()
        assert len(get_system_exports(node=self.context.node)) == 0, error()
        assert get_num_active_exports(node=self.context.node) == 0, error()


@TestOutline(Scenario)
@Examples(
    "background_move_pool_size",
    [
        (1,),
        (8,),
        (16,),
    ],
)
@Requirements(RQ_ClickHouse_ExportPart_ServerSettings_BackgroundMovePoolSize("1.0"))
def background_move_pool_size(self, background_move_pool_size):
    """Check that background_move_pool_size server setting controls the number of threads used for exporting parts."""

    with Given(f"I set background_move_pool_size to {background_move_pool_size}"):
        config_d.create_and_add(
            entries={"background_move_pool_size": f"{background_move_pool_size}"},
            config_file="background_move_pool_size.xml",
            node=self.context.node,
        )

    with And("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100000,
            number_of_parts=10,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow down the network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("I check that the number of threads used for exporting parts is correct"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                exports = get_system_exports(node=self.context.node)
                assert len(exports) == background_move_pool_size, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ServerSettings_MaxBandwidth("1.0"))
def max_bandwidth(self):
    """Check that the max bandwidth setting limits the bandwidth used for exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I record the average duration of the exports"):
        wait_for_all_exports_to_complete(table_name=source_table)
        flush_log(table_name="system.part_log")
        avg_duration_unlimited_bandwidth = get_average_export_duration(
            table_name=source_table
        )

    with When("I set the max bandwidth to 512 bytes per second"):
        config_d.create_and_add(
            entries={"max_exports_bandwidth_for_server": "512"},
            config_file="max_bandwidth.xml",
            node=self.context.node,
        )

    with And("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I record the duration of the export"):
        wait_for_all_exports_to_complete(table_name=source_table)
        flush_log(table_name="system.part_log")
        avg_duration_limited_bandwidth = get_average_export_duration(
            table_name=source_table
        )

    with Then(
        "I check that the duration of the export with restricted bandwidth is more than 10 times greater"
    ):
        assert (
            avg_duration_limited_bandwidth > avg_duration_unlimited_bandwidth * 10
        ), error()


@TestFeature
@Name("system monitoring")
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
def feature(self):
    """Check system monitoring of export events."""

    Scenario(run=system_events_and_part_log)
    Scenario(run=duplicate_logging)
    Scenario(run=system_exports_and_metrics)
    Scenario(run=background_move_pool_size)
    Scenario(run=max_bandwidth)
