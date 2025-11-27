from helpers.common import getuid
import helpers.config.config_d as config_d
from alter.stress.tests.tc_netem import *
from helpers.common import getuid
from s3.requirements.export_partition import *
from s3.tests.export_part.steps import (
    default_columns,
    partitioned_replicated_merge_tree_table,
)
from s3.tests.export_partition.steps import (
    export_partitions,
    get_partitions,
    create_s3_table,
    check_export_status,
    wait_for_export_to_start,
    wait_for_export_to_complete,
    get_export_field,
    get_source_database,
    get_destination_table,
    get_create_time,
    get_partition_id,
    get_transaction_id,
    get_source_replica,
    get_parts,
    get_parts_count,
    get_parts_to_do,
)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_appears_in_table(self):
    """Check that export operations appear in system.replicated_partition_exports table."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        Check(test=export_partitions, parallel=True)(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )
        Check(test=wait_for_export_to_start, parallel=True)(source_table=source_table)

    with Then("I check that exports appear in system.replicated_partition_exports"):
        exports_count = wait_for_export_to_complete(source_table=source_table)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_fields_populated(self):
    """Check that all fields in system.replicated_partition_exports are populated correctly."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check that source_table field is populated"):
        source_db = get_source_database(source_table=source_table)
        assert source_db.output.strip() != "", error()

    with And("I check that destination_table field is populated"):
        dest_table = get_destination_table(source_table=source_table)
        assert dest_table.output.strip() == s3_table_name, error()

    with And("I check that partition_id field is populated"):
        partition_id = get_partition_id(source_table=source_table)
        assert partition_id.output.strip() != "", error()

    with And("I check that parts field is populated"):
        parts = get_parts(source_table=source_table)
        assert parts.output.strip() != "", error()

    with And("I check that parts_count field is populated"):
        parts_count = get_parts_count(source_table=source_table)
        assert int(parts_count.output.strip()) > 0, error()

    with And("I check that create_time field is populated"):
        create_time = get_create_time(source_table=source_table)
        assert create_time.output.strip() != "", error()

    with And("I check that source_replica field is populated"):
        source_replica = get_source_replica(source_table=source_table)
        assert source_replica.output.strip() != "", error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_status_transitions(self):
    """Check that export status transitions from PENDING to COMPLETED correctly."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("I check that exports start with PENDING status"):
        wait_for_export_to_start(source_table=source_table)
        pending_count = check_export_status(status="PENDING", source_table=source_table)
        assert int(pending_count.output.strip()) > 0, error()

    with And("I check that exports transition to COMPLETED status"):
        wait_for_export_to_complete(source_table=source_table)
        completed_count = check_export_status(
            status="COMPLETED", source_table=source_table
        )
        assert int(completed_count.output.strip()) > 0, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def parts_to_do_decreases(self):
    """Check that parts_to_do decreases as parts are exported."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100000,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow down the network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=20)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check initial parts_to_do count"):
        initial_parts_to_do = get_parts_to_do(source_table=source_table)
        initial_count = int(initial_parts_to_do.output.strip())
        assert initial_count > 0, error()

    with And("I check that parts_to_do decreases as export progresses"):
        for attempt in retries(timeout=60, delay=2):
            with attempt:
                current_parts_to_do = get_parts_to_do(source_table=source_table)
                current_count = int(current_parts_to_do.output.strip())
                assert current_count < initial_count or current_count == 0, error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPartition_Concurrency("1.0"),
)
def concurrent_exports_tracking(self):
    """Check that multiple concurrent exports are tracked correctly in the table."""

    with Given("I create multiple populated source tables and empty S3 tables"):
        source_tables = []
        s3_tables = []
        for i in range(3):
            source_table = f"source_{getuid()}"
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(),
                stop_merges=True,
            )
            s3_table_name = create_s3_table(
                table_name=f"s3_{i}", create_new_bucket=(i == 0)
            )
            source_tables.append(source_table)
            s3_tables.append(s3_table_name)

    with When("I export partitions from all tables concurrently"):
        for source_table, s3_table in zip(source_tables, s3_tables):
            Step(test=export_partitions, parallel=True)(
                source_table=source_table,
                destination_table=s3_table,
                node=self.context.node,
            )
        join()

    with Then("I check that all exports appear in the table"):
        for source_table in source_tables:
            wait_for_export_to_start(source_table=source_table)
            exports_count = check_export_status(
                status="PENDING", source_table=source_table
            )
            assert int(exports_count.output.strip()) > 0, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def partition_id_matches_exported(self):
    """Check that partition_id in the table matches the exported partitions."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get the list of partitions to export"):
        partitions = get_partitions(table_name=source_table, node=self.context.node)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check that partition_id matches exported partitions"):
        all_partition_ids = get_export_field(
            field_name="partition_id",
            source_table=source_table,
            select_clause="DISTINCT partition_id",
        )
        exported_partition_ids = set(
            [
                pid.strip()
                for pid in all_partition_ids.output.strip().splitlines()
                if pid.strip()
            ]
        )

        assert len(exported_partition_ids) == len(partitions), error()
        for partition in partitions:
            assert partition in exported_partition_ids, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def parts_array_matches_table_parts(self):
    """Check that the parts array in the table matches the actual parts in the source table."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get the actual parts from the source table"):
        partitions = get_partitions(table_name=source_table, node=self.context.node)
        expected_parts = set()
        for partition in partitions:
            parts_result = self.context.node.query(
                f"SELECT name FROM system.parts WHERE table = '{source_table}' AND partition_id = '{partition}' AND active = 1",
                exitcode=0,
                steps=True,
            )
            for part in parts_result.output.strip().splitlines():
                expected_parts.add(part.strip())

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check that parts array matches expected parts"):
        all_parts_result = get_export_field(
            field_name="parts",
            source_table=source_table,
            select_clause="parts",
        )
        exported_parts_set = set()
        for line in all_parts_result.output.strip().splitlines():
            if line.strip():
                import json

                try:
                    parts_array = json.loads(line.strip())
                    if isinstance(parts_array, list):
                        exported_parts_set.update(parts_array)
                except (json.JSONDecodeError, ValueError):
                    pass

        assert len(exported_parts_set) >= len(expected_parts), error()
        for part in expected_parts:
            assert part in exported_parts_set, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def transaction_id_populated(self):
    """Check that transaction_id is populated for export operations."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check that transaction_id is populated"):
        transaction_id = get_transaction_id(source_table=source_table)
        assert transaction_id.output.strip() != "", error()


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPartition_ServerSettings_BackgroundMovePoolSize("1.0"),
)
def concurrent_exports_limit(self, background_move_pool_size):
    """Check that the number of concurrent exports is limited by background_move_pool_size."""

    with Given(f"I set background_move_pool_size to {background_move_pool_size}"):
        config_d.create_and_add(
            entries={"background_move_pool_size": f"{background_move_pool_size}"},
            config_file="background_move_pool_size.xml",
            node=self.context.node,
        )

    with And("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100000,
            number_of_parts=10,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I slow down the network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=20)

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I wait for exports to start"):
        wait_for_export_to_start(source_table=source_table)

    with Then("I check that the number of active exports is limited"):
        active_exports = get_export_field(
            field_name="COUNT(*)",
            source_table=source_table,
            select_clause="COUNT(*)",
            where_clause="status = 'PENDING' OR status = 'COMPLETED'",
        )
        active_count = int(active_exports.output.strip())
        assert active_count <= background_move_pool_size, error()


@TestFeature
@Name("system monitoring")
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def feature(self):
    """Check system monitoring of export partition operations via system.replicated_partition_exports table."""

    Scenario(run=export_appears_in_table)
    Scenario(run=export_fields_populated)
    Scenario(run=export_status_transitions)
    Scenario(run=parts_to_do_decreases)
    Scenario(run=concurrent_exports_tracking)
    Scenario(run=partition_id_matches_exported)
    Scenario(run=parts_array_matches_table_parts)
    Scenario(run=transaction_id_populated)
    Scenario(test=concurrent_exports_limit)(background_move_pool_size=1)
    Scenario(test=concurrent_exports_limit)(background_move_pool_size=4)
    Scenario(test=concurrent_exports_limit)(background_move_pool_size=8)
