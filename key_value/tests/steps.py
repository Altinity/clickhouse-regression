import json

from helpers.common import *
from key_value.requirements.requirements import *


def string_of_all_askii_symbols():  # todo remove after debug
    """Create string with all askii symbols with numbers from 32 to 126."""
    return "".join([chr(i) for i in range(32, 127)])


@TestStep(Given)
def create_partitioned_table(
    self,
    table_name,
    extra_table_col="",
    cluster="",
    engine="MergeTree",
    partition="PARTITION BY x",
    order="ORDER BY x",
    settings="",
    node=None,
    options="",
    column_type="String",
):
    """Create a partitioned table."""
    if node is None:
        node = self.context.node

    try:
        with Given(f"I have a table {table_name}"):
            node.query(
                f"CREATE TABLE {table_name} {cluster} (x {column_type}{extra_table_col})"
                f" Engine = {engine} {partition} {order} {options} {settings}"
            )
        yield

    finally:
        with Finally("I remove the table", flags=TE):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(When)
def insert(self, table_name, x, y, node=None):
    """Insert data into the table"""
    if node is None:
        node = self.context.node

    node.query(f'INSERT INTO {table_name} VALUES ("{x}", "{y}")')


@TestStep(When)
def optimize_table(self, table_name, final=True, node=None):
    """Force merging of some (final=False) or all parts (final=True)
    by calling OPTIMIZE TABLE.
    """
    if node is None:
        node = self.context.node

    query = f"OPTIMIZE TABLE {table_name}"
    if final:
        query += " FINAL"

    return node.query(query)


@TestStep(Then)
def check_constant_input(self, input_string, output_string=None, exitcode=0, node=None):
    """Check that clickhouse parseKeyValue function support constant input."""

    if node is None:
        node = self.context.node

    with Then("I check parseKeyValue function returns correct value"):
        if exitcode != 0:
            node.query(f"SELECT extractKeyValuePairs({input_string})", use_file=True, exitcode=exitcode)
        else:
            r = node.query(f"SELECT extractKeyValuePairs({input_string})", use_file=True)
            if ':' in output_string and ':' in r.output:
                assert json.loads(r.output.replace("'", '"')) == json.loads(output_string.replace("'", '"')), error()
            else:
                assert r.output == output_string, error()
