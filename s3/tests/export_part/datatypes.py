from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *


@TestCheck
def configured_table(self, partition_key_type):
    with Given(f"I create a populated source table with partition key type {partition_key_type} and empty S3 table"):
        partitioned_merge_tree_table(
            table_name="source",
            partition_by="p",
            columns=default_columns(partition_key_type=partition_key_type),
            stop_merges=True,
            populate=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=default_columns(partition_key_type=partition_key_type)
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


@TestSketch(Scenario)
@Flags(TE)
def basic_partition_key_types(self):
    """Check that all partition key data types are supported when exporting parts."""

    key_types = [
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "UInt8",
        "UInt16",
        "UInt32",
        "UInt64",
        "Date",
        "DateTime",
        "DateTime64",
        "String",
        # "FixedString(1)",
    ]

    configured_table(partition_key_type=either(*key_types))


@TestFeature
@Name("datatypes")
def feature(self):
    """Check that all data types are supported when exporting parts."""

    Scenario(run=basic_partition_key_types)
