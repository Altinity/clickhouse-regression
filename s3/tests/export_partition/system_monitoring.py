from testflows.core import *
import helpers.config.config_d as config_d
from helpers.common import getuid
from alter.stress.tests.tc_netem import *
from helpers.create import partitioned_replicated_merge_tree_table
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    export_partitions,
    get_partitions,
    create_s3_table,
    wait_for_export_to_complete,
    verify_export_fields_populated,
    verify_export_status,
    verify_parts_to_do_decreases,
    verify_exports_appear_in_table,
    verify_partition_ids_match,
    get_expected_parts_from_table,
    verify_parts_array_matches,
    verify_table_structure_has_fields,
    verify_all_fields_populated,
    verify_transaction_id_populated,
    verify_active_exports_limited,
    default_columns,
)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_appears_in_table(self):
    """Check that export operations appear in system.replicated_partition_exports table."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify exports appear in system.replicated_partition_exports"):
        wait_for_export_to_complete(source_table=source_table)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_fields_populated(self):
    """Check that all fields in system.replicated_partition_exports are populated correctly."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify fields are populated"):
        verify_export_fields_populated(
            source_table=source_table,
            s3_table_name=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def export_status_transitions(self):
    """Check that export status transitions from PENDING to COMPLETED correctly."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify exports start with PENDING status"):
        verify_export_status(source_table=source_table, status="PENDING")

    with And("verify exports transition to COMPLETED status"):
        wait_for_export_to_complete(source_table=source_table)
        verify_export_status(source_table=source_table, status="COMPLETED")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def parts_to_do_decreases(self):
    """Check that parts_to_do decreases as parts are exported."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100000,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("slow down network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=20)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify parts_to_do decreases"):
        verify_parts_to_do_decreases(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPartition_Concurrency("1.0"),
)
def concurrent_exports_tracking(self):
    """Check that multiple concurrent exports are tracked correctly in the table."""

    source_tables = []
    s3_tables = []

    with Given("create multiple source and S3 tables"):
        for i in range(3):
            source_table = f"source_{getuid()}"
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(),
                stop_merges=True,
                cluster="replicated_cluster",
            )
            s3_table_name = create_s3_table(
                table_name=f"s3_{i}", create_new_bucket=(i == 0)
            )
            source_tables.append(source_table)
            s3_tables.append(s3_table_name)

    with When("export partitions from all tables concurrently"):
        for source_table, s3_table in zip(source_tables, s3_tables):
            Step(test=export_partitions, parallel=True)(
                source_table=source_table,
                destination_table=s3_table,
                node=self.context.node,
            )
        join()

    with Then("verify all exports appear in the table"):
        for source_table in source_tables:
            verify_exports_appear_in_table(source_table=source_table)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def partition_id_matches_exported(self):
    """Check that partition_id in the table matches the exported partitions."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("get list of partitions to export"):
        partitions = get_partitions(table_name=source_table, node=self.context.node)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify partition_id matches exported partitions"):
        verify_partition_ids_match(
            source_table=source_table,
            expected_partitions=partitions,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def parts_array_matches_table_parts(self):
    """Check that the parts array in the table matches the actual parts in the source table."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("get actual parts from source table"):
        expected_parts = get_expected_parts_from_table(
            source_table=source_table,
            node=self.context.node,
        )

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify parts array matches expected parts"):
        verify_parts_array_matches(
            source_table=source_table,
            expected_parts=expected_parts,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def transaction_id_populated(self):
    """Check that transaction_id is populated for export operations."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify transaction_id is populated"):
        verify_transaction_id_populated(source_table=source_table)


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"),
    RQ_ClickHouse_ExportPartition_ServerSettings_BackgroundMovePoolSize("1.0"),
)
def concurrent_exports_limit(self, background_move_pool_size):
    """Check that the number of concurrent exports is limited by background_move_pool_size."""

    source_table = f"source_{getuid()}"

    with Given(f"set background_move_pool_size to {background_move_pool_size}"):
        config_d.create_and_add(
            entries={"background_move_pool_size": f"{background_move_pool_size}"},
            config_file="background_move_pool_size.xml",
            node=self.context.node,
        )

    with And("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_values=100000,
            number_of_parts=10,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("slow down network speed"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=20)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify number of active exports is limited"):
        verify_active_exports_limited(
            source_table=source_table,
            max_count=background_move_pool_size,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_SystemTables_Exports("1.0"))
def all_required_fields_present(self):
    """Check that system.replicated_partition_exports contains all required fields after export."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("export partitions"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("verify all required fields exist in table structure"):
        verify_table_structure_has_fields(node=self.context.node)

    with And("verify fields are populated after export"):
        verify_all_fields_populated(
            source_table=source_table,
            node=self.context.node,
        )


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
    Scenario(run=all_required_fields_present)
