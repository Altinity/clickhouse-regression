from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from helpers.common import getuid
from s3.requirements.export_part import *


@TestStep(Given)
def create_merge_tree_all_valid_partition_key_types(
    self, column_name, cluster=None, node=None
):
    """Create a MergeTree table with all valid partition key types."""

    if node is None:
        node = self.context.node

    with By("creating a MergeTree table with all data types"):
        table_name = f"table_{getuid()}"
        create_merge_tree_table(
            table_name=table_name,
            columns=valid_partition_key_types_columns(),
            partition_by=column_name,
            cluster=cluster,
            stop_merges=True,
        )

    with And("I insert data into the table"):
        for i in range(10):
            node.query(
                f"INSERT INTO {table_name} (int8, int16, int32, int64, uint8, uint16, uint32, uint64, date, date32, datetime, datetime64, string, fixedstring) VALUES (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, '13', '14')"
            )

    return table_name


@TestCheck
def valid_partition_key_table(self, partition_key_type):
    """Check exporting to a source table with specified valid partition key type."""

    with Given(
        f"I create a source table with valid partition key type {partition_key_type} and empty S3 table"
    ):
        table_name = create_merge_tree_all_valid_partition_key_types(
            column_name=partition_key_type,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=valid_partition_key_types_columns(),
            partition_by=partition_key_type,
        )

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(
            table_name=table_name, node=self.context.node, order_by=partition_key_type
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name,
            node=self.context.node,
            order_by=partition_key_type,
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_ClickHouse_ExportPart_PartitionKeyTypes("1.0"))
def valid_partition_key_types(self):
    """Check that all partition key data types are supported when exporting parts."""

    key_types = [datatype["name"] for datatype in valid_partition_key_types_columns()]
    valid_partition_key_table(partition_key_type=either(*key_types))


@TestFeature
@Name("datatypes")
def feature(self):
    """Check that all data types are supported when exporting parts."""

    Scenario(run=valid_partition_key_types)
