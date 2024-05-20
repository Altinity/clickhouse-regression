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

        r += " FORMAT TabSeparated"

        if settings is not None:
            r += f" SETTINGS {settings}"

        output = node.query(r)

    return output
