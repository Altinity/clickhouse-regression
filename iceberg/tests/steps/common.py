from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations

from helpers.common import getuid


@TestStep(Given)
def create_row_policy(
    self,
    name=None,
    on_clause=None,
    using_clause=None,
    as_clause=None,
    to_clause=None,
    node=None,
):
    """Create a row policy."""
    if name is None:
        name = f"row_policy_{getuid()}"

    if node is None:
        node = self.context.node

    query = f"CREATE ROW POLICY {name}"

    if on_clause:
        query += f" ON {on_clause}"

    if using_clause:
        query += f" USING {using_clause}"

    if as_clause:
        query += f" AS {as_clause}"

    if to_clause:
        query += f" TO {to_clause}"

    try:
        node.query(query)
        yield name

    finally:
        with Finally("drop row policy"):
            node.query(f"DROP ROW POLICY IF EXISTS {name} ON {on_clause}")
