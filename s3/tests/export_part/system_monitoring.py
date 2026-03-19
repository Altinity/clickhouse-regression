from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from s3.requirements.export_part import *
from alter.stress.tests.tc_netem import *
from s3.tests.export_part import alter_wrappers
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
        initial_events = get_export_events()

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with And("I read the final logged export events and part log"):
        final_events = get_export_events()
        part_log = get_part_log()

    with Then("I check that the number of part exports is correct"):
        assert (
            final_events["PartsExports"] - initial_events["PartsExports"] == 5
        ), error()

    with And("I check that the part log contains the correct parts"):
        parts = get_parts(table_name=source_table)
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
        initial_events = get_export_events()

    with When("I try to export the parts twice"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
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
        final_events = get_export_events()
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
            number_of_values=10000,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow down the network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.5)

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )

    with Then("I check that system.exports and system.metrics contain some parts"):
        exports = get_system_exports()
        assert get_num_active_exports() > 0, error()
        assert len(exports) > 0, error()
        assert [source_table, s3_table_name] in exports, error()

    with And(
        "I verify that system.exports and system.metrics are empty after exports complete"
    ):
        wait_for_all_exports_to_complete()
        assert len(get_system_exports()) == 0, error()
        assert get_num_active_exports() == 0, error()


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
        )

    with Then("I check that the number of threads used for exporting parts is correct"):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                exports = get_system_exports()
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
            avg_duration_limited_bandwidth > avg_duration_unlimited_bandwidth * 1.5
        ), error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_Settings_MaxBytesPerFile("1.0"),
    RQ_ClickHouse_ExportPart_Settings_MaxRowsPerFile("1.0"),
)
def max_bytes_per_file_and_rows_per_file(self):
    """Check that the max bytes per file setting limits the size of the exported files."""

    with Given("I create a source table"):
        source_table = "big_table_" + getuid()
        columns = [
            {"name": "id", "type": "UInt64"},
            {"name": "data", "type": "String"},
            {"name": "year", "type": "UInt16"},
        ]
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="year",
            columns=columns,
            populate=False,
        )

    with And("I insert data to create a large table (~9MB)"):
        self.context.node.query(
            f"""
            INSERT INTO {source_table} 
            SELECT number AS id, repeat('x', 100) AS data, 2025 AS year 
            FROM numbers(4194304)
            """,
            exitcode=0,
            steps=True,
        )

    with And("I optimize the table to ensure we have only one part"):
        alter_wrappers.optimize_table(table_name=source_table)

    with And("I get the single part name"):
        big_part = get_parts(table_name=source_table)[0]

    with And("I create destination S3 tables"):
        destination_max_bytes = create_s3_table(
            table_name="max_bytes",
            create_new_bucket=True,
            columns=columns,
            partition_by="year",
        )
        destination_max_rows = create_s3_table(
            table_name="max_rows",
            create_new_bucket=True,
            columns=columns,
            partition_by="year",
        )

    with When("I export the part with max_bytes_per_file setting"):
        export_parts(
            source_table=source_table,
            destination_table=destination_max_bytes,
            parts=[big_part],
            settings=[
                ("export_merge_tree_part_max_bytes_per_file", "3500000"),
                ("output_format_parquet_row_group_size_bytes", "1000000"),
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with And("I export the part with max_rows_per_file setting"):
        export_parts(
            source_table=source_table,
            destination_table=destination_max_rows,
            parts=[big_part],
            settings=[
                ("export_merge_tree_part_max_rows_per_file", "1048576"),
            ],
        )

    with And("I wait for all exports to complete"):
        wait_for_all_exports_to_complete(table_name=source_table)

    with Then("I count files in max_bytes destination, should be 4 parquet files"):
        file_count = count_s3_files(table_name=destination_max_bytes)
        assert file_count == 4, error()

    with And("I verify hashes match between source and max_bytes destination"):
        source_matches_destination_hash(
            source_table=source_table,
            destination_table=destination_max_bytes,
        )

    with And("I count files in max_rows destination, should be 4 parquet files"):
        file_count = count_s3_files(table_name=destination_max_rows)
        assert file_count == 4, error()

    with And("I verify hashes match between source and max_rows destination"):
        source_matches_destination_hash(
            source_table=source_table,
            destination_table=destination_max_rows,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPart_Logging("1.0"),
)
def system_tables_columns(self):
    """Verify that system.exports and system.part_log contain all expected columns."""

    expected_exports_columns = {
        "source_database",
        "source_table",
        "destination_database",
        "destination_table",
        "create_time",
        "part_name",
        "query_id",
        "destination_file_paths",
        "elapsed",
        "rows_read",
        "total_rows_to_read",
        "total_size_bytes_compressed",
        "total_size_bytes_uncompressed",
        "bytes_read_uncompressed",
        "memory_usage",
        "peak_memory_usage",
    }

    expected_part_log_columns = {
        "hostname",
        "query_id",
        "event_type",
        "merge_reason",
        "merge_algorithm",
        "event_date",
        "event_time",
        "event_time_microseconds",
        "duration_ms",
        "database",
        "table",
        "table_uuid",
        "part_name",
        "partition_id",
        "partition",
        "part_type",
        "disk_name",
        "path_on_disk",
        "remote_file_paths",
        "rows",
        "size_in_bytes",
        "merged_from",
        "bytes_uncompressed",
        "read_rows",
        "read_bytes",
        "peak_memory_usage",
        "error",
        "exception",
        "ProfileEvents",
    }

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I export parts to ensure system tables are populated"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
        )
        wait_for_all_exports_to_complete(table_name=source_table)

    with And("I get actual columns for system.exports using DESCRIBE TABLE"):
        exports_columns_result = self.context.node.query(
            "DESCRIBE TABLE system.exports FORMAT TabSeparated",
            exitcode=0,
            steps=True,
        )
        actual_exports_columns = {
            line.split("\t")[0].strip()
            for line in exports_columns_result.output.strip().splitlines()
        }

    with And("I get actual columns for system.part_log using DESCRIBE TABLE"):
        part_log_columns_result = self.context.node.query(
            "DESCRIBE TABLE system.part_log FORMAT TabSeparated",
            exitcode=0,
            steps=True,
        )
        actual_part_log_columns = {
            line.split("\t")[0].strip()
            for line in part_log_columns_result.output.strip().splitlines()
        }

    with Then("I verify all expected columns exist in system.exports"):
        missing_exports_columns = expected_exports_columns - actual_exports_columns
        assert len(missing_exports_columns) == 0, error(
            f"Missing columns in system.exports: {missing_exports_columns}. "
            f"Expected: {sorted(expected_exports_columns)}, "
            f"Actual: {sorted(actual_exports_columns)}"
        )

    with And("I verify all expected columns exist in system.part_log"):
        missing_part_log_columns = expected_part_log_columns - actual_part_log_columns
        assert len(missing_part_log_columns) == 0, error(
            f"Missing columns in system.part_log: {missing_part_log_columns}. "
            f"Expected: {sorted(expected_part_log_columns)}, "
            f"Actual: {sorted(actual_part_log_columns)}"
        )


@TestFeature
@Name("system monitoring")
@Requirements(RQ_ClickHouse_ExportPart_Logging("1.0"))
def feature(self):
    """Check system monitoring of export events."""

    Scenario(run=system_events_and_part_log)
    Scenario(run=duplicate_logging)
    Scenario(run=system_exports_and_metrics)
    Scenario(run=system_tables_columns)
    Scenario(run=background_move_pool_size)
    Scenario(run=max_bandwidth)
    Scenario(run=max_bytes_per_file_and_rows_per_file)
