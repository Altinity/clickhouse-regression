import json

from helpers.common import *
from testflows.core import define
from key_value.requirements.requirements import *


ascii_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ascii_num = "0123456789"
ascii_punctuation_marks = "!\"#$%&'()*+,-./:;>=<?@[\\]^_`{|}~"

noise = ascii_punctuation_marks + ascii_num

parsed_noise = (
    ascii_punctuation_marks.replace("\\", "\\\\")
    .replace('"', '\\"')
    .replace("`", "\\`")
    .replace("'", "\\'")
)

noise_without_quotation_mark = noise.replace('"', "")

parsed_noise_without_quotation_mark = (
    noise_without_quotation_mark.replace("\\", "\\\\")
    .replace('"', '\\"')
    .replace("`", "\\`")
    .replace("'", "\\'")
)


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
def insert(self, table_name, x, y, node=None, use_file=True):
    """Insert data into the table"""
    if node is None:
        node = self.context.node

    node.query(f"INSERT INTO {table_name} VALUES ({x}, '{y}')", use_file=use_file)


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
def check_constant_input(self, input, output=None, params="", exitcode=0, node=None):
    """Check that clickhouse parseKeyValue function support constant input."""

    if node is None:
        node = self.context.node
    if params != "":
        params = ", " + params
    with Then("I check parseKeyValue function returns correct value"):
        if exitcode != 0:
            node.query(
                f"SELECT extractKeyValuePairs({input}{params})",
                use_file=True,
                exitcode=exitcode,
            )
        else:
            r = node.query(
                f"SELECT extractKeyValuePairs({input}{params})", use_file=True
            )
            assert r.output == output, error()
