from testflows.core import *

from alter.table.attach_partition.conditions import order_by


@TestStep(Given)
def parquetify(self, json_file, output_path, node=None):
    """Execute a Parquetify program for generating a Parquet file based on a json file."""
    if node is None:
        node = self.context.cluster.node("parquetify")

    node.command(f"parquetify --json {json_file} --output {output_path}")


@TestStep(Given)
def select_from_parquet(
    self,
    file_name,
    node=None,
    file_type=None,
    statement="*",
    condition=False,
    settings=None,
    format=None,
    order_by=False,
):
    """Select from a parquet file."""
    if node is None:
        node = self.context.node

    if file_type is None:
        file_type = ", Parquet"

    with By(f"selecting the data from the parquet file {file_name}"):
        r = f"SELECT {statement} FROM file('{file_name}'{file_type})"

        if condition:
            r += f" {condition}"

        if order_by:
            r += f" ORDER BY {order_by}"

        if format is None:
            format = "TabSeparated"

        r += f" FORMAT {format}"

        if settings is not None:
            r += f" SETTINGS {settings}"

        output = node.query(r)

    return output


@TestStep(Given)
def count_rows_in_parquet(self, file_name, node=None):
    """Count rows in a parquet file."""
    if node is None:
        node = self.context.node

    with Given(f"I count the rows in the parquet file {file_name}"):
        output = select_from_parquet(
            file_name=file_name, node=node, statement="count(*)"
        )

    return int(output.output.strip())
