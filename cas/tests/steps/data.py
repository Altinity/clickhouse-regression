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
    """Insert deterministic rows into ``p`` and ``i``, leaving extra DEFAULT columns alone."""
    if node is None:
        node = self.context.node

    for partition in partitions:
        node.query(
            f"INSERT INTO {table_name} (p, i) SELECT {partition}, number "
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
    seed=None,
):
    """Insert rows carrying a large incompressible payload.

    ``randomString`` does not compress and does not deduplicate against other
    rows, so the resulting blob bodies are roughly ``rows * payload_bytes``.
    That is what makes a byte re-upload distinguishable from a relink.

    With ``seed`` the payload is built from ``cityHash64`` words instead, so
    the same arguments write the same bytes again.
    """
    if node is None:
        node = self.context.node

    if seed is None:
        payload = f"randomString({payload_bytes})"
    else:
        payload = (
            "arrayStringConcat(arrayMap(word -> reinterpretAsFixedString("
            f"cityHash64({seed}, number + {id_offset}, word)), "
            f"range(intDiv({payload_bytes}, 8))))"
        )

    node.query(
        f"INSERT INTO {table_name} "
        f"SELECT {partition}, number + {id_offset}, {payload} "
        f"FROM numbers({rows})"
    )


@TestStep(When)
@Name("insert payload batches")
def insert_cas_payload_batches(self, table_name, batches, rows=64, node=None):
    """Run ``batches`` payload inserts with disjoint ``i`` ranges, one part each."""
    for batch in range(batches):
        insert_cas_payload_rows(
            table_name=table_name, rows=rows, id_offset=batch * rows, node=node
        )
