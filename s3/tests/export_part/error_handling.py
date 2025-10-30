from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from helpers.queries import *
from s3.requirements.export_part import *


@TestScenario
def invalid_part_name(self):
    """Check that exporting a non-existent part returns the correct error."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
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
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
            parts=[invalid_part_name],
            exitcode=1,
        )

    with Then("I should see an error related to the invalid part name"):
        assert results[0].exitcode == 233, error()
        assert (
            f"Unexpected part name: {invalid_part_name}" in results[0].output
        ), error()


@TestScenario
def duplicate_exports(self):
    """Check duplicate exports are ignored and not exported again."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I try to export the parts twice"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("The source and destination tables should still be the same"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_Restrictions_SameTable("1.0"))
def same_table(self):
    """Check exporting parts where source and destination tables are the same."""

    with Given("I create a populated source table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )

    with When("I try to export parts to itself"):
        results = export_parts(
            source_table="source",
            destination_table="source",
            node=self.context.node,
            exitcode=1,
        )

    with Then("I should see an error related to same table exports"):
        assert results[0].exitcode == 36, error()
        assert (
            "Exporting to the same table is not allowed" in results[0].output
        ), error()


@TestScenario
def local_table(self):
    """Test exporting parts to a local table."""

    with Given("I create a populated source table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
        )

    with And("I create an empty local table"):
        partitioned_merge_tree_table(
            table_name="destination",
            partition_by="p",
            columns=default_columns(),
            stop_merges=True,
            populate=False,
        )

    with When("I export parts to the local table"):
        results = export_parts(
            source_table="source",
            destination_table="destination",
            node=self.context.node,
            exitcode=1,
        )

    with Then("I should see an error related to local table exports"):
        assert results[0].exitcode == 48, error()
        assert (
            "Destination storage MergeTree does not support MergeTree parts or uses unsupported partitioning"
            in results[0].output
        ), error()


# TODO different partition key


@TestFeature
@Name("error handling")
@Requirements(RQ_ClickHouse_ExportPart_FailureHandling("1.0"))
def feature(self):
    """Check correct error handling when exporting parts."""

    Scenario(run=invalid_part_name)
    Scenario(run=duplicate_exports)
    Scenario(run=same_table)
    Scenario(run=local_table)
