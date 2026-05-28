from testflows.core import *

from engines.tests.steps import insert_values_into_table


@TestStep(When)
def insert_sample_values(self, table_name, node=None):
    """Insert the standard pair of sample rows used by the SummingMergeTree
    scenarios: ``(1, 1, 100)`` and ``(2, 2, 200)``.
    """
    insert_values_into_table(
        table_name=table_name,
        values=["(1, 1, 100)", "(2, 2, 200)"],
        node=node,
    )
