from testflows.core import *
from testflows.asserts import error
from helpers.queries import *


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
                    table_name=source_table, node=source_node, identifier=partition
                )
            if destination_data is None:
                destination_data = select_all_ordered(
                    table_name=destination_table,
                    node=destination_node,
                    identifier=partition,
                )
            assert source_data == destination_data, error()
