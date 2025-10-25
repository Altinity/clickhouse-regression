from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *
from helpers.create import *


# TODO large data export? or maybe that should be in a different file

@TestScenario
def configured_table(self, table_engine, number_of_partitions, number_of_parts):
    """Test a specific combination of table engine, number of partitions, and number of parts."""

    with Given("I create a populated source table and empty S3 table"):
        table_engine(
            table_name="source",
            partition_by="p",
            columns=self.context.default_columns,
            stop_merges=True,
            populate=True,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(source_table="source", destination_table=s3_table_name, node=self.context.node)
    
    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(table_name=s3_table_name, node=self.context.node)
    
    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestSketch(Scenario)
@Flags(TE)
def table_combos(self):
    """Test various combinations of table engines, number of partitions, and number of parts."""

    tables = [
        partitioned_merge_tree_table,
        partitioned_replacing_merge_tree_table,
        partitioned_summing_merge_tree_table,
        # partitioned_collapsing_merge_tree_table, # Ask David if failing here is expected behaviour
        partitioned_versioned_collapsing_merge_tree_table,
        partitioned_aggregating_merge_tree_table,
        # partitioned_graphite_merge_tree_table, # Ask David about "age and precision should only grow up" error
    ]
    # TODO expand combos
    number_of_partitions = [5]
    number_of_parts = [1]

    configured_table(
        table_engine=either(*tables),
        number_of_partitions=either(*number_of_partitions),
        number_of_parts=either(*number_of_parts),
    )


@TestScenario
def basic_table(self):
    """Test exporting parts of a basic table."""
    
    with Given("I create a populated source table and empty S3 table"):
        partitioned_merge_tree_table(table_name="source", partition_by="p", columns=self.context.default_columns, stop_merges=True, populate=True)
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)
    
    with When("I export parts to the S3 table"):
        export_parts(source_table="source", destination_table=s3_table_name, node=self.context.node)
    
    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="source", node=self.context.node)
        destination_data = select_all_ordered(table_name=s3_table_name, node=self.context.node)
    
    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestScenario
def empty_table(self):
    """Test exporting parts from an empty table."""

    with Given("I create empty source and S3 tables"):
        partitioned_merge_tree_table(table_name="empty_source", partition_by="p", columns=self.context.default_columns, stop_merges=True, populate=False)
        s3_table_name = create_s3_table(table_name="empty_s3", create_new_bucket=True)

    with When("I export parts to the S3 table"):
        export_parts(source_table="empty_source", destination_table=s3_table_name, node=self.context.node)
    
    with And("I read data from both tables"):
        source_data = select_all_ordered(table_name="empty_source", node=self.context.node)
        destination_data = select_all_ordered(table_name=s3_table_name, node=self.context.node)

    with Then("They should be empty"):
        assert source_data == "", error()
        assert destination_data == "", error()


@TestFeature
@Name("sanity")
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=empty_table)
    Scenario(run=basic_table)
    Scenario(run=table_combos)