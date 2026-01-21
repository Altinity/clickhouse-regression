from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from helpers.queries import *
from s3.requirements.export_part import *
from alter.table.replace_partition.corrupted_partitions import *
from s3.tests.export_part import alter_wrappers
from helpers.alter import delete, update


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_SourcePart("1.0"))
def invalid_part_name(self):
    """Check that exporting a non-existent part returns the correct error."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I create an invalid part name"):
        invalid_part_name = "in_va_lid_part"

    with When("I try to export the invalid part"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            parts=[invalid_part_name],
            exitcode=1,
        )

    with Then("I should see an error related to the invalid part name"):
        assert results[0].exitcode == 233, error()
        assert (
            f"Unexpected part name: {invalid_part_name}" in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_SameTable("1.0"))
def same_table(self):
    """Check exporting parts where source and destination tables are the same."""

    with Given("I create a populated source table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )

    with When("I try to export parts to itself"):
        results = export_parts(
            source_table=source_table,
            destination_table=source_table,
            exitcode=1,
        )

    with Then("I should see an error related to same table exports"):
        assert results[0].exitcode == 36, error()
        assert (
            "Exporting to the same table is not allowed" in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_LocalTable("1.0"))
def local_table(self):
    """Test exporting parts to a local table."""

    with Given("I create a populated source table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )

    with And("I create an empty local table"):
        destination_table = "destination_" + getuid()

        partitioned_merge_tree_table(
            table_name=destination_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
        )

    with When("I export parts to the local table"):
        results = export_parts(
            source_table=source_table,
            destination_table=destination_table,
            exitcode=1,
        )

    with Then("I should see an error related to local table exports"):
        assert results[0].exitcode == 48, error()
        assert (
            "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning"
            in results[0].output
        ), error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Settings_AllowExperimental("1.0"))
def disable_export_setting(self):
    """Check that exporting parts without the export setting set returns the correct error."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I try to export the parts with the export setting disabled"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            exitcode=1,
            inline_settings=[("allow_experimental_export_merge_tree_part", 0)],
        )

    with Then("I should see an error related to the export setting"):
        assert results[0].exitcode == 88, error()
        assert "Exporting merge tree part is experimental" in results[0].output, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_PartitionKey("1.0"))
def different_partition_key(self):
    """Check exporting parts with a different partition key returns the correct error."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="i",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I try to export the parts"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            exitcode=1,
        )

    with Then("I should see an error related to the different partition key"):
        assert results[0].exitcode == 36, error()
        assert "Tables have different partition key" in results[0].output, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_FailureHandling_PartCorruption("1.0"))
def part_corruption(self):
    """Check that exports work correctly with corrupted parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get all parts before corruption"):
        all_parts = get_parts(table_name=source_table)
        corrupted_part = get_random_part(table_name=source_table)
        non_corrupted_parts = [p for p in all_parts if p != corrupted_part]

    with When("I apply part corruption"):
        corrupt_parts_on_table_partition(
            table_name=source_table, parts=[corrupted_part], bits_to_corrupt=1500000
        )

    with And("I attempt to export the corrupted part and expect it to fail"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            parts=[corrupted_part],
            exitcode=1,
        )

    with And("I export the non-corrupted parts and expect them to succeed"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            parts=non_corrupted_parts,
        )

    with Then("I verify that the corrupted part export failure is logged in part_log"):
        wait_for_all_exports_to_complete()
        flush_log(table_name="system.part_log")

        successful_exports = get_part_log(table_name=source_table)
        failed_exports = get_failed_part_log(table_name=source_table)

        assert corrupted_part not in successful_exports, error()
        assert corrupted_part in failed_exports, error()
        for part in non_corrupted_parts:
            assert part in successful_exports, error()


@TestOutline(Scenario)
@Examples(
    "removal_function, target_type",
    [
        (detach_part, "part"),
        (alter_table_detach_partition, "partition"),
        (drop_part, "part"),
        (alter_table_drop_partition, "partition"),
    ],
)
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_RemovedPart("1.0"))
def removed_part_or_partition(self, removal_function, target_type):
    """Check that exporting a removed part or partition returns the correct error."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            number_of_parts=5,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And(f"I get the {target_type} to remove"):
        if target_type == "part":
            target_name = get_random_part(table_name=source_table)
            part_to_export = target_name
        else:
            partition_name = get_random_partition(table_name=source_table)
            part_to_export = get_random_part(
                table_name=source_table, partition=partition_name
            )
            target_name = partition_name

    with And(f"I remove the {target_type}"):
        removal_function(
            table_name=source_table,
            **{f"{target_type}_name": target_name},
        )

    with When(f"I try to export the part from the removed {target_type}"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            parts=[part_to_export],
            exitcode=1,
        )

    with Then(f"I should see an error related to the removed {target_type}"):
        assert results[0].exitcode == 232, error()


@TestScenario
def pending_mutations(self):
    """Check that exporting parts with pending mutations throws an error by default."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I start a mutation and stop merges to keep it pending"):
        delete.alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
        )

    with When("I try to export parts with pending mutations (default settings)"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            exitcode=1,
        )

    with Then("I should see an error about pending mutations"):
        assert results[0].exitcode == 237, error()
        assert "PENDING_MUTATIONS_NOT_ALLOWED" in results[0].output, error()


@TestScenario
def pending_patch_parts(self):
    """Check that exporting parts with pending patch parts throws an error by default."""

    with Given("I create a populated source table with lightweight update support and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            query_settings="enable_block_number_column = 1, enable_block_offset_column = 1",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I perform a lightweight UPDATE to create patch parts"):
        self.context.node.query(
            f"UPDATE {source_table} SET i = i + 1000 WHERE p = 1",
            exitcode=0,
            steps=True,
        )

    with When("I try to export parts with pending patch parts (default settings)"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            exitcode=1,
        )

    with Then("I should see an error about pending patch parts"):
        assert results[0].exitcode == 237, error()
        assert "PENDING_MUTATIONS_NOT_ALLOWED" in results[0].output, error()


@TestScenario
def outdated_parts(self):
    """Check that exporting outdated parts throws an error by default."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            number_of_parts=2,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get a part name before optimizing"):
        parts_before = get_parts(table_name=source_table)
        part_to_export = parts_before[0]

    with And("I optimize the table to make parts outdated"):
        alter_wrappers.optimize_table(table_name=source_table)

    with And("I verify the part is now outdated"):
        outdated_parts = self.context.node.query(
            f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active = 0 AND name = '{part_to_export}'",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert part_to_export in outdated_parts, error()

    with When("I try to export the outdated part (default settings)"):
        results = export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            parts=[part_to_export],
            exitcode=1,
        )

    with Then("I should see an error about outdated parts"):
        assert results[0].exitcode == 36, error()
        assert "BAD_ARGUMENTS" in results[0].output, error()
        assert "export_merge_tree_part_allow_outdated_parts" in results[0].output, error()


@TestFeature
@Name("error handling")
@Requirements(RQ_ClickHouse_ExportPart_FailureHandling("1.0"))
def feature(self):
    """Check correct error handling when exporting parts."""

    Scenario(run=invalid_part_name)
    Scenario(run=same_table)
    Scenario(run=local_table)
    Scenario(run=disable_export_setting)
    Scenario(run=different_partition_key)
    Scenario(run=part_corruption)
    Scenario(run=removed_part_or_partition)
    Scenario(run=pending_mutations)
    Scenario(run=pending_patch_parts)
    Scenario(run=outdated_parts)
