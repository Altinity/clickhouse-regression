"""Insert helpers for CAS scenarios."""

from testflows.core import *


@TestStep(When)
def insert_cas_partitions(
    self,
    table_name,
    partitions=(1, 2, 3),
    rows_per_partition=10,
    node=None,
):
    """Insert deterministic rows into the given partitions."""
    if node is None:
        node = self.context.node

    for partition in partitions:
        node.query(
            f"INSERT INTO {table_name} SELECT {partition}, number "
            f"FROM numbers({rows_per_partition})"
        )


@TestStep(When)
@Name("insert rows with an incompressible payload")
def insert_cas_payload_rows(
    self,
    table_name,
    rows=64,
    payload_bytes=16384,
    partition=1,
    node=None,
    id_offset=0,
):
    """Insert rows carrying a large incompressible payload.

    ``randomString`` does not compress and does not deduplicate against other
    rows, so the resulting blob bodies are roughly ``rows * payload_bytes``.
    That is what makes a byte re-upload distinguishable from a relink.
    """
    if node is None:
        node = self.context.node

    node.query(
        f"INSERT INTO {table_name} "
        f"SELECT {partition}, number + {id_offset}, "
        f"randomString({payload_bytes}) "
        f"FROM numbers({rows})"
    )
