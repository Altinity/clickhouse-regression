from testflows.core import *
from testflows.asserts import error

from iceberg.tests.hybrid.core.common import (
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
    create_mt_mt_hybrid,
    settings_clause,
)


# Queries that exercise the four Distributed subquery stages.
STAGE_QUERIES = (
    (
        "complete",
        "SELECT id, value, date_col FROM {table} WHERE date_col = '2025-02-01' ORDER BY id",
    ),
    (
        "with_mergeable_state",
        "SELECT count() FROM {table}",
    ),
    (
        "with_mergeable_state_after_aggregation",
        "SELECT date_col, count() FROM {table} GROUP BY date_col ORDER BY date_col",
    ),
    (
        "with_mergeable_state_after_aggregation_and_limit",
        "SELECT date_col, count() FROM {table} GROUP BY date_col ORDER BY date_col LIMIT 10",
    ),
)


def _reference_wrapped(ctx, select_template):
    """Rewrite SELECT … FROM {table} against the UNION ALL reference subquery."""
    ref = (
        f"(SELECT id, value, date_col FROM {ctx['left_from']} WHERE {ctx['left_pred']} "
        f"UNION ALL "
        f"SELECT id, value, date_col FROM {ctx['right_from']} WHERE {ctx['right_pred']})"
    )
    return select_template.format(table=ref)


def _run_stages(self, ctx, settings_row):
    node = self.context.node
    clause = settings_clause(settings_row)
    for stage_name, template in STAGE_QUERIES:
        with Then(f"{stage_name}"):
            hybrid_sql = template.format(table=ctx["hybrid"]) + f" {clause}"
            ref_sql = _reference_wrapped(ctx, template) + f" {clause}"
            hybrid_out = node.query(hybrid_sql).output.strip()
            ref_out = node.query(ref_sql).output.strip()
            assert hybrid_out == ref_out, error()


@TestScenario
@Name("subquery stages prefer localhost")
def subquery_stages_prefer_localhost(self):
    """Four Distributed subquery stages with prefer_localhost_replica=1."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()
    _run_stages(self, ctx, PREFER_LOCALHOST)


@TestScenario
@Name("subquery stages force remote")
def subquery_stages_force_remote(self):
    """Four Distributed subquery stages with prefer_localhost_replica=0."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()
    _run_stages(self, ctx, FORCE_REMOTE)


@TestScenario
@Name("fingerprint prefer localhost and force remote")
def fingerprint_prefer_localhost_and_force_remote(self):
    """Full-table fingerprint matches reference for both localhost settings."""
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
                settings_row=row,
            )


@TestFeature
@Name("distributed execution")
def feature(self):
    """Distributed subquery stages and local vs remote merge paths."""
    for scenario in (
        subquery_stages_prefer_localhost,
        subquery_stages_force_remote,
        fingerprint_prefer_localhost_and_force_remote,
    ):
        Scenario(run=scenario)
