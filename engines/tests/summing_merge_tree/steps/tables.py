from testflows.core import *

from helpers.create import create_summing_merge_tree_table


@TestStep(Given)
def create_summing_test_table(self, table_name, columns_to_sum=None):
    """Create a SummingMergeTree table with the standard test schema
    used across the SummingMergeTree scenarios: columns (v, p, c) of UInt64,
    partitioned by ``p`` and ordered by ``v``.
    """
    create_summing_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "v", "type": "UInt64"},
            {"name": "p", "type": "UInt64"},
            {"name": "c", "type": "UInt64"},
        ],
        partition_by="p",
        order_by="v",
        columns_to_sum=columns_to_sum,
    )
