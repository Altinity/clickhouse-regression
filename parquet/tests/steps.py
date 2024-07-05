from testflows.core import *


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
