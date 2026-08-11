"""Shared helpers for Hybrid engine core tests."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table
from helpers.datatypes import Int32, Date


# Exclusive date watermark used by most scenarios.
WATERMARK = "2025-01-15"
LEFT_PREDICATE = f"date_col >= '{WATERMARK}'"
RIGHT_PREDICATE = f"date_col < '{WATERMARK}'"

# Controlled dataset spanning both sides of the watermark.
ALL_ROWS = (
    (1, 100, "2025-02-01"),  # hot
    (2, 200, "2025-06-15"),  # hot
    (3, 300, "2024-06-01"),  # cold
    (4, 400, "2025-01-01"),  # cold
)

COLUMNS = [
    Column(name="id", datatype=Int32()),
    Column(name="value", datatype=Int32()),
    Column(name="date_col", datatype=Date()),
]

COLUMNS_SQL = "id Int32, value Int32, date_col Date"

# Execution settings (see hybrid_testing_matrix.md §4.4).
PREFER_LOCALHOST = {
    "prefer_localhost_replica": 1,
    "serialize_query_plan": 0,
    "hybrid_table_auto_cast_columns": 0,
}
FORCE_REMOTE = {
    "prefer_localhost_replica": 0,
    "serialize_query_plan": 0,
    "hybrid_table_auto_cast_columns": 0,
}
AUTO_CAST = {
    "prefer_localhost_replica": 1,
    "serialize_query_plan": 0,
    "hybrid_table_auto_cast_columns": 1,
}


def values_sql(rows=ALL_ROWS):
    return ", ".join(f"({id_}, {value}, '{date_}')" for id_, value, date_ in rows)


def settings_clause(*rows, extra=None):
    """Build a trailing SETTINGS clause for SELECT-like queries; always enable_analyzer=1."""
    return "SETTINGS " + ", ".join(
        f"{k} = {v}" for k, v in settings_list(*rows, extra=extra)
    )


def settings_list(*rows, extra=None):
    """Settings as a list of (name, value) for node.query(..., settings=...)."""
    merged = {"enable_analyzer": 1}
    for row in rows:
        if row:
            merged.update(row)
    if extra:
        merged.update(extra)
    return list(merged.items())


def remote_tf(table_name):
    return f"remote('localhost', currentDatabase(), '{table_name}')"


def cluster_all_tf(table_name):
    return f"cluster('all', currentDatabase(), '{table_name}')"


def fingerprint_sql(from_expr):
    """Stable aggregate fingerprint for correctness vs reference."""
    return (
        "SELECT count(), coalesce(sum(id), 0), coalesce(sum(value), 0), "
        "groupBitXor(cityHash64(id, value, toString(date_col))) "
        f"FROM {from_expr}"
    )


def reference_from_sql(
    left_from, right_from, left_pred=LEFT_PREDICATE, right_pred=RIGHT_PREDICATE
):
    return (
        f"(SELECT id, value, date_col FROM {left_from} WHERE {left_pred} "
        f"UNION ALL "
        f"SELECT id, value, date_col FROM {right_from} WHERE {right_pred})"
    )


@TestStep(Then)
def assert_hybrid_matches_reference(
    self,
    hybrid_table,
    left_from,
    right_from,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
    where="",
    settings_row=None,
    node=None,
):
    """Hard-assert Hybrid fingerprint equals UNION ALL reference."""
    if node is None:
        node = self.context.node

    where_sql = f" WHERE {where}" if where else ""
    clause = settings_clause(settings_row)

    hybrid_q = fingerprint_sql(f"{hybrid_table}{where_sql}") + f" {clause}"
    ref_q = (
        fingerprint_sql(
            reference_from_sql(left_from, right_from, left_pred, right_pred) + where_sql
        )
        + f" {clause}"
    )

    with By("query Hybrid fingerprint"):
        hybrid_out = node.query(hybrid_q).output.strip()

    with By("query reference fingerprint"):
        ref_out = node.query(ref_q).output.strip()

    with By(f"compare Hybrid={hybrid_out!r} vs reference={ref_out!r}"):
        assert hybrid_out == ref_out, error()


@TestStep(Given)
def create_mergetree_segment(
    self,
    name=None,
    columns=None,
    rows=ALL_ROWS,
    node=None,
    cluster=None,
    seed_all_nodes=False,
):
    """Create a MergeTree segment and insert controlled rows."""
    if node is None:
        node = self.context.node
    if name is None:
        name = f"mt_{getuid()}"
    if columns is None:
        columns = COLUMNS

    create_table(
        name=name,
        engine="MergeTree",
        columns=columns,
        order_by="(date_col, id)",
        partition_by="toYYYYMM(date_col)",
        cluster=cluster,
        node=node,
    )

    insert = f"INSERT INTO {name} (id, value, date_col) VALUES {values_sql(rows)}"
    if seed_all_nodes and cluster is not None:
        for n in self.context.nodes:
            n.query(insert)
    else:
        node.query(insert)

    return name


@TestStep(Given)
def create_mt_mt_hybrid(
    self,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
    left_tf_fn=remote_tf,
    right_tf_fn=remote_tf,
    rows=ALL_ROWS,
    cluster=None,
    seed_all_nodes=False,
    hybrid_name=None,
    node=None,
):
    """Two MergeTree segments + Hybrid head. Returns a context dict."""
    if node is None:
        node = self.context.node
    if hybrid_name is None:
        hybrid_name = f"hybrid_{getuid()}"

    left_name = create_mergetree_segment(
        rows=rows, cluster=cluster, seed_all_nodes=seed_all_nodes, node=node
    )
    right_name = create_mergetree_segment(
        rows=rows, cluster=cluster, seed_all_nodes=seed_all_nodes, node=node
    )

    left_tf = left_tf_fn(left_name)
    right_tf = right_tf_fn(right_name)

    create_table(
        name=hybrid_name,
        engine=f"Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
        columns=COLUMNS,
        settings=[("allow_experimental_hybrid_table", 1)],
        node=node,
    )

    return {
        "hybrid": hybrid_name,
        "left": left_name,
        "right": right_name,
        "left_tf": left_tf,
        "right_tf": right_tf,
        "left_pred": left_pred,
        "right_pred": right_pred,
        "left_from": left_name,
        "right_from": right_name,
    }
