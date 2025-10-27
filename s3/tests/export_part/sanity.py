from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from helpers.create import *


@TestScenario
def mismatched_columns(self):
    """Test exporting parts when source and destination tables have mismatched columns."""

    with Given("I create a source table and S3 table with different columns"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(simple=True),
            stop_merges=True,
            populate=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, simple_columns=False
        )

    with When("I export parts to the S3 table"):
        results = export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
            exitcode=1,
        )

    with Then("I should see an error related to mismatched columns"):
        assert results[0].exitcode == 122, error()
        assert "Tables have different structure" in results[0].output, error()


@TestScenario
def basic_table(self):
    """Test exporting parts of a basic table."""

    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(simple=True),
            stop_merges=True,
            populate=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, simple_columns=True
        )

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestScenario
def empty_table(self):
    """Test exporting parts from an empty table."""

    with Given("I create empty source and S3 tables"):
        partitioned_merge_tree_table(
            table_name="empty_source",
            partition_by="p",
            columns=default_columns(simple=True),
            stop_merges=False,
            populate=False,
        )
        s3_table_name = create_s3_table(
            table_name="empty_s3", create_new_bucket=True, simple_columns=True
        )

    with When("I export parts to the S3 table"):
        export_parts(
            source_table="empty_source",
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(
            table_name="empty_source", node=self.context.node
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with Then("They should be empty"):
        assert source_data == "", error()
        assert destination_data == "", error()


@TestFeature
@Name("sanity")
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=empty_table)
    Scenario(run=basic_table)
    Scenario(run=mismatched_columns)
