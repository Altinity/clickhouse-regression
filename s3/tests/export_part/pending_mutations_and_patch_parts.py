from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from s3.tests.export_part.steps import *
from helpers.queries import *
from s3.requirements.export_part import *
from helpers.alter import delete, update
from s3.tests.export_part import alter_wrappers


@TestScenario
def pending_mutations_allow(self):
    """Test that exporting parts with pending mutations succeeds when throw_on_pending_mutations=false."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get the original data"):
        original_data = select_all_ordered(table_name=source_table)

    with And("I start a mutation and stop merges to keep it pending"):
        delete.alter_table_delete_rows(
            table_name=source_table,
            condition="p = 1",
        )

    with When("I export parts with throw_on_pending_mutations=false"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[("export_merge_tree_part_throw_on_pending_mutations", False)],
        )

    with And("I wait for exports to complete"):
        wait_for_all_exports_to_complete()

    with Then("Export should succeed and contain original data (pre-mutation state)"):
        exported_data = select_all_ordered(table_name=s3_table_name)
        assert set(original_data) == set(exported_data), error()

    with And("After mutations complete, source should not match destination"):
        start_merges(table_name=source_table)
        wait_for_all_mutations_to_complete(table_name=source_table)
        mutated_data = select_all_ordered(table_name=source_table)
        assert set(mutated_data) != set(exported_data), error()


@TestScenario
def pending_patch_parts_allow(self):
    """Test that exporting parts with pending patch parts succeeds when throw_on_pending_patch_parts=false."""

    with Given(
        "I create a populated source table with lightweight update support and empty S3 table"
    ):
        source_table = f"source_{getuid()}"
        partitioned_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            query_settings="enable_block_number_column = 1, enable_block_offset_column = 1",
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I get the original data"):
        original_data = select_all_ordered(table_name=source_table)

    with And("I perform a lightweight UPDATE to create patch parts"):
        self.context.node.query(
            f"UPDATE {source_table} SET i = i + 1000 WHERE p = 1",
            exitcode=0,
            steps=True,
        )

    with When("I export parts with throw_on_pending_patch_parts=false"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            settings=[("export_merge_tree_part_throw_on_pending_patch_parts", False)],
        )

    with And("I wait for exports to complete"):
        wait_for_all_exports_to_complete()

    with Then("Export should succeed and contain original data (patches not applied)"):
        exported_data = select_all_ordered(table_name=s3_table_name)
        assert set(original_data) == set(exported_data), error()

    with And("After patch parts are applied, source should not match destination"):
        start_merges(table_name=source_table)
        wait_for_all_mutations_to_complete(table_name=source_table)
        patched_data = select_all_ordered(table_name=source_table)
        assert set(patched_data) != set(exported_data), error()


@TestFeature
@Name("pending mutations and patch parts")
def feature(self):
    """Check behavior of export part with pending mutations, patch parts, and outdated parts."""

    Scenario(run=pending_mutations_allow)
    Scenario(run=pending_patch_parts_allow)
