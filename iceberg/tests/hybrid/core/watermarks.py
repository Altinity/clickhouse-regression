from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS,
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    WATERMARK,
    assert_hybrid_matches_reference,
    create_mergetree_segment,
    create_mt_mt_hybrid,
    fingerprint_sql,
    remote_tf,
    settings_clause,
)


@TestScenario
@Name("mutually exclusive watermarks")
def mutually_exclusive(self):
    """Exclusive predicates: no duplicates vs reference."""
    with Given("MT+MT Hybrid exclusive watermark"):
        ctx = create_mt_mt_hybrid(
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
        )

    with Then("fingerprint matches exclusive reference"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=PREFER_LOCALHOST,
        )

    with And("row count equals distinct ids in dataset"):
        count = self.context.node.query(
            f"SELECT count() FROM {ctx['hybrid']} {settings_clause(PREFER_LOCALHOST)}"
        ).output.strip()
        assert count == str(len(ALL_ROWS)), error()


@TestScenario
@Name("overlapping watermarks duplicate rows")
def overlapping_watermarks(self):
    """Overlapping predicates intentionally duplicate matching rows."""
    node = self.context.node
    # Overlap window around watermark: both segments serve Jan 2025 rows.
    left_pred = "date_col >= '2025-01-01'"
    right_pred = "date_col < '2025-02-01'"

    with Given("MT+MT Hybrid with overlapping predicates"):
        ctx = create_mt_mt_hybrid(left_pred=left_pred, right_pred=right_pred)

    clause = settings_clause(PREFER_LOCALHOST)

    with Then("Hybrid count matches overlapping UNION ALL reference"):
        hybrid_count = node.query(
            f"SELECT count() FROM {ctx['hybrid']} {clause}"
        ).output.strip()
        ref_count = node.query(
            f"SELECT count() FROM ("
            f"SELECT * FROM {ctx['left']} WHERE {left_pred} "
            f"UNION ALL "
            f"SELECT * FROM {ctx['right']} WHERE {right_pred}"
            f") {clause}"
        ).output.strip()
        assert hybrid_count == ref_count, error()

    with And("Hybrid count exceeds distinct exclusive count"):
        exclusive = node.query(
            f"SELECT count() FROM ("
            f"SELECT * FROM {ctx['left']} WHERE {LEFT_PREDICATE} "
            f"UNION ALL "
            f"SELECT * FROM {ctx['right']} WHERE {RIGHT_PREDICATE}"
            f") {clause}"
        ).output.strip()
        assert int(hybrid_count) > int(exclusive), error()


@TestScenario
@Name("create or replace moves watermark")
def create_or_replace_watermark(self):
    """CREATE OR REPLACE atomically advances the static watermark."""
    node = self.context.node

    with Given("segment tables with full dataset"):
        left = create_mergetree_segment()
        right = create_mergetree_segment()

    hybrid = f"hybrid_{getuid()}"
    left_tf = remote_tf(left)
    right_tf = remote_tf(right)
    clause = settings_clause(PREFER_LOCALHOST)

    with And("create Hybrid at initial watermark"):
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({left_tf}, {LEFT_PREDICATE}, {right_tf}, {RIGHT_PREDICATE})"
            ),
            columns=COLUMNS,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with When("capture fingerprint before replace"):
        before = node.query(fingerprint_sql(hybrid) + f" {clause}").output.strip()

    new_wm = "2025-03-01"
    new_left = f"date_col >= '{new_wm}'"
    new_right = f"date_col < '{new_wm}'"

    with And("CREATE OR REPLACE Hybrid with advanced watermark"):
        cols = ", ".join(c.full_definition() for c in COLUMNS)
        node.query(
            f"CREATE OR REPLACE TABLE {hybrid} ({cols}) "
            f"ENGINE = Hybrid({left_tf}, {new_left}, {right_tf}, {new_right})",
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with Then("SHOW CREATE reflects the new watermark"):
        show = node.query(f"SHOW CREATE TABLE {hybrid}").output
        assert new_wm in show, error()
        assert f"date_col >= '{WATERMARK}'" not in show, error()

    with And("fingerprint matches new exclusive reference"):
        assert_hybrid_matches_reference(
            hybrid_table=hybrid,
            left_from=left,
            right_from=right,
            left_pred=new_left,
            right_pred=new_right,
            settings_row=PREFER_LOCALHOST,
        )

    with And("aggregate fingerprint unchanged when both segments hold the same rows"):
        # Moving an exclusive watermark only changes which segment serves each
        # row; with mirrored segment data the Hybrid result set is identical.
        after = node.query(fingerprint_sql(hybrid) + f" {clause}").output.strip()
        assert after == before, error()


@TestFeature
@Name("watermarks")
def feature(self):
    """Static watermark exclusivity, overlap, and CREATE OR REPLACE."""
    for scenario in (
        mutually_exclusive,
        overlapping_watermarks,
        create_or_replace_watermark,
    ):
        Scenario(run=scenario)
