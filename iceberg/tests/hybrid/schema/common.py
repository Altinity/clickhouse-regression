"""Shared helpers for Hybrid schema-variety / operational Phase 5 tests."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.hybrid.core.common import (
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    remote_tf,
    settings_clause,
)


def fingerprint_expr(from_expr, hash_list="*"):
    """Stable hash fingerprint over ``hash_list`` expressions on ``from_expr``.

    ``hash_list`` is evaluated in the outer SELECT (e.g. ``toString(amount)``),
    so ``from_expr`` must expose the underlying column names — do not pre-project
    the same transforms in a subquery without aliases.
    """
    return (
        "SELECT count(), "
        f"groupBitXor(cityHash64({hash_list})) "
        f"FROM {from_expr}"
    )


def exclusive_union_from(left, right, left_pred, right_pred, columns="*"):
    """Exclusive watermark reference: left ∪ right under complementary predicates."""
    return (
        f"(SELECT {columns} FROM {left} WHERE {left_pred} "
        f"UNION ALL "
        f"SELECT {columns} FROM {right} WHERE {right_pred})"
    )


@TestStep(Then)
def assert_fingerprints_equal(self, hybrid_sql, reference_sql, node=None, label=""):
    if node is None:
        node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)
    hybrid_out = node.query(hybrid_sql + f" {clause}").output.strip()
    ref_out = node.query(reference_sql + f" {clause}").output.strip()
    with By(f"compare{(' ' + label) if label else ''} Hybrid={hybrid_out!r} vs ref={ref_out!r}"):
        assert hybrid_out == ref_out, error()


@TestStep(Given)
def create_mt_pair_and_hybrid(
    self,
    columns_sql,
    order_by,
    left_values,
    right_values,
    left_pred=LEFT_PREDICATE,
    right_pred=RIGHT_PREDICATE,
    partition_by="toYYYYMM(date_col)",
):
    """Two MergeTree segments + Hybrid(remote, remote) with the given schema."""
    node = self.context.node
    left = f"mt_left_{getuid()}"
    right = f"mt_right_{getuid()}"
    hybrid = f"hybrid_{getuid()}"

    for name, values in ((left, left_values), (right, right_values)):
        node.query(
            f"CREATE TABLE {name} ({columns_sql}) "
            f"ENGINE = MergeTree ORDER BY {order_by} "
            f"PARTITION BY {partition_by}"
        )
        node.query(f"INSERT INTO {name} VALUES {values}")

    left_tf = remote_tf(left)
    right_tf = remote_tf(right)
    node.query(
        f"CREATE TABLE {hybrid} ({columns_sql}) "
        f"ENGINE = Hybrid({left_tf}, {left_pred}, {right_tf}, {right_pred})",
        settings=[("allow_experimental_hybrid_table", 1)],
    )

    return {
        "hybrid": hybrid,
        "left": left,
        "right": right,
        "left_tf": left_tf,
        "right_tf": right_tf,
        "left_pred": left_pred,
        "right_pred": right_pred,
    }
