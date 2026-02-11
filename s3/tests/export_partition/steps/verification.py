from testflows.core import *
from testflows.asserts import error
from helpers.queries import *
from .export_operations import export_partitions


@TestStep(Then)
def source_matches_destination(
    self,
    source_table,
    destination_table,
    source_node=None,
    destination_node=None,
    partition=None,
    source_data=None,
    destination_data=None,
    order_by="p, i",
):
    """Check that source and destination table data matches."""

    if source_node is None:
        source_node = self.context.node
    if destination_node is None:
        destination_node = self.context.node

    for attempt in retries(timeout=35, delay=3):
        with attempt:
            if source_data is None:
                source_data = select_all_ordered(
                    table_name=source_table,
                    node=source_node,
                    identifier=partition,
                    order_by=order_by,
                )
            if destination_data is None:
                destination_data = select_all_ordered(
                    table_name=destination_table,
                    node=destination_node,
                    identifier=partition,
                    order_by=order_by,
                )
            assert source_data == destination_data, error()


@TestStep(When)
def export_and_verify_columns(
    self,
    table_name,
    s3_table_name,
    insert_query,
    order_by,
    columns,
    description="columns",
):
    """Helper function to export partitions and verify data matches."""
    with By("inserting data into the source table"):
        self.context.node.query(insert_query, use_file=True)

    with And("exporting partitions to the S3 table"):
        export_partitions(
            source_table=table_name,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And(f"verifying {description} exported to S3 matches source"):
        column_list = ", ".join(columns)
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    node=self.context.node,
                    identifier=column_list,
                    order_by=order_by,
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    node=self.context.node,
                    identifier=column_list,
                    order_by=order_by,
                )
                assert source_data == destination_data, error()
