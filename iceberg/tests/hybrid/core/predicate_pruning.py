from testflows.core import *

from iceberg.tests.hybrid.core.common import (
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
    create_mt_mt_hybrid,
)


@TestScenario
@Name("where hits only hot segment")
def where_hits_only_hot_segment(self):
    """WHERE fully in hot watermark range matches hot-only reference."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()

    for label, row in (
        ("prefer localhost", PREFER_LOCALHOST),
        ("force remote", FORCE_REMOTE),
    ):
        with Then(label):
            assert_hybrid_matches_reference(
                hybrid_table=ctx["hybrid"],
                left_from=ctx["left_from"],
                right_from=ctx["right_from"],
                left_pred=ctx["left_pred"],
                right_pred=ctx["right_pred"],
                where="date_col >= '2025-06-01'",
                settings_row=row,
            )


@TestScenario
@Name("where hits only cold segment")
def where_hits_only_cold_segment(self):
    """WHERE fully in cold watermark range matches cold-only reference."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()

    for label, row in (
        ("prefer localhost", PREFER_LOCALHOST),
        ("force remote", FORCE_REMOTE),
    ):
        with Then(label):
            assert_hybrid_matches_reference(
                hybrid_table=ctx["hybrid"],
                left_from=ctx["left_from"],
                right_from=ctx["right_from"],
                left_pred=ctx["left_pred"],
                right_pred=ctx["right_pred"],
                where="date_col < '2025-01-01'",
                settings_row=row,
            )


@TestScenario
@Name("where spans both segments")
def where_spans_both_segments(self):
    """WHERE spanning the watermark draws from both segments."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()

    for label, row in (
        ("prefer localhost", PREFER_LOCALHOST),
        ("force remote", FORCE_REMOTE),
    ):
        with Then(label):
            assert_hybrid_matches_reference(
                hybrid_table=ctx["hybrid"],
                left_from=ctx["left_from"],
                right_from=ctx["right_from"],
                left_pred=ctx["left_pred"],
                right_pred=ctx["right_pred"],
                where="date_col >= '2024-01-01' AND date_col <= '2025-12-31'",
                settings_row=row,
            )


@TestFeature
@Name("predicate pruning")
def feature(self):
    """Result correctness when filters hit one or both Hybrid segments."""
    for scenario in (
        where_hits_only_hot_segment,
        where_hits_only_cold_segment,
        where_spans_both_segments,
    ):
        Scenario(run=scenario)
