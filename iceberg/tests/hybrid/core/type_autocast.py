from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table
from helpers.datatypes import UInt64, Int64, Int32, Date

from iceberg.tests.hybrid.core.common import (
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    AUTO_CAST,
    remote_tf,
    settings_clause,
    values_sql,
)


# Same logical values; unsigned on left, signed on right (Iceberg-like seam).
MISMATCH_ROWS = (
    (1, 100, "2025-02-01"),
    (2, 200, "2025-06-15"),
    (3, 300, "2024-06-01"),
    (4, 400, "2025-01-01"),
)


@TestScenario
@Name("UInt64 vs Int64 with auto cast on")
def uint64_vs_int64_auto_cast_on(self):
    """hybrid_table_auto_cast_columns=1 bridges UInt64 / Int64 across segments."""
    node = self.context.node

    left_cols = [
        Column(name="id", datatype=UInt64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]
    right_cols = [
        Column(name="id", datatype=Int64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]
    hybrid_cols = [
        Column(name="id", datatype=Int64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]

    left = f"left_{getuid()}"
    right = f"right_{getuid()}"
    hybrid = f"hybrid_{getuid()}"

    with Given("left MergeTree with UInt64 id"):
        create_table(
            name=left,
            engine="MergeTree",
            columns=left_cols,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        node.query(
            f"INSERT INTO {left} (id, value, date_col) VALUES {values_sql(MISMATCH_ROWS)}"
        )

    with And("right MergeTree with Int64 id"):
        create_table(
            name=right,
            engine="MergeTree",
            columns=right_cols,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        node.query(
            f"INSERT INTO {right} (id, value, date_col) VALUES {values_sql(MISMATCH_ROWS)}"
        )

    with And("Hybrid head typed as Int64 id"):
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({remote_tf(left)}, {LEFT_PREDICATE}, "
                f"{remote_tf(right)}, {RIGHT_PREDICATE})"
            ),
            columns=hybrid_cols,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    clause = settings_clause(AUTO_CAST)

    with Then("SELECT count works with auto-cast enabled"):
        count = node.query(f"SELECT count() FROM {hybrid} {clause}").output.strip()
        assert count == "4", error()

    with And("sum(id) matches exclusive reference with casts"):
        hybrid_sum = node.query(
            f"SELECT sum(id) FROM {hybrid} {clause}"
        ).output.strip()
        ref_sum = node.query(
            f"SELECT sum(id) FROM ("
            f"SELECT toInt64(id) AS id FROM {left} WHERE {LEFT_PREDICATE} "
            f"UNION ALL "
            f"SELECT id FROM {right} WHERE {RIGHT_PREDICATE}"
            f") {clause}"
        ).output.strip()
        assert hybrid_sum == ref_sum, error()


@TestScenario
@Name("UInt64 vs Int64 with auto cast off")
def uint64_vs_int64_auto_cast_off(self):
    """Without auto-cast, UInt64/Int64 mismatch should error or still be correct if coerced."""
    node = self.context.node

    left_cols = [
        Column(name="id", datatype=UInt64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]
    right_cols = [
        Column(name="id", datatype=Int64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]
    hybrid_cols = [
        Column(name="id", datatype=Int64()),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]

    left = f"left_{getuid()}"
    right = f"right_{getuid()}"
    hybrid = f"hybrid_{getuid()}"

    with Given("mismatched UInt64 / Int64 segments and Hybrid Int64 head"):
        create_table(
            name=left,
            engine="MergeTree",
            columns=left_cols,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        node.query(
            f"INSERT INTO {left} (id, value, date_col) VALUES {values_sql(MISMATCH_ROWS)}"
        )
        create_table(
            name=right,
            engine="MergeTree",
            columns=right_cols,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        node.query(
            f"INSERT INTO {right} (id, value, date_col) VALUES {values_sql(MISMATCH_ROWS)}"
        )
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({remote_tf(left)}, {LEFT_PREDICATE}, "
                f"{remote_tf(right)}, {RIGHT_PREDICATE})"
            ),
            columns=hybrid_cols,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    clause = settings_clause(PREFER_LOCALHOST)

    with When("query Hybrid with auto-cast disabled"):
        r = node.query(
            f"SELECT count() FROM {hybrid} {clause}",
            no_checks=True,
        )

    with Then("either errors or does not return the auto-cast success count alone as proof"):
        # Prefer error; if the engine coerces somehow, still require exitcode or note.
        if r.exitcode == 0:
            # Document unexpected success for triage; still compare to casted reference.
            casted = node.query(
                f"SELECT count() FROM ("
                f"SELECT toInt64(id) AS id, value, date_col FROM {left} WHERE {LEFT_PREDICATE} "
                f"UNION ALL "
                f"SELECT id, value, date_col FROM {right} WHERE {RIGHT_PREDICATE}"
                f") {clause}"
            ).output.strip()
            # If it works without auto-cast, results must still be correct.
            assert r.output.strip() == casted, error()
        else:
            assert r.exitcode != 0, error()


@TestFeature
@Name("type autocast")
def feature(self):
    """Type mismatch across segments with hybrid_table_auto_cast_columns on/off."""
    for scenario in (uint64_vs_int64_auto_cast_on, uint64_vs_int64_auto_cast_off):
        Scenario(run=scenario)
