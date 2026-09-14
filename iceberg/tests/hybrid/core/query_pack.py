from testflows.core import *

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_QueryShapes,
    RQ_ClickHouse_Hybrid_CorrectnessVsUnion,
)

from iceberg.tests.hybrid.core.common import (
    PREFER_LOCALHOST,
    FORCE_REMOTE,
    assert_hybrid_matches_reference,
    create_mt_mt_hybrid,
    settings_clause,
)


def _run_queries(self, ctx, settings_row):
    hybrid = ctx["hybrid"]
    left = ctx["left_from"]
    right = ctx["right_from"]
    left_pred = ctx["left_pred"]
    right_pred = ctx["right_pred"]

    cases = [
        ("full scan", ""),
        ("hot-only filter", "date_col >= '2025-02-01'"),
        ("cold-only filter", "date_col < '2025-01-01'"),
        ("equality", "id = 1"),
        ("range", "value BETWEEN 100 AND 300"),
        ("in list", "id IN (1, 3, 4)"),
    ]

    for name, where in cases:
        with Then(f"{name}"):
            assert_hybrid_matches_reference(
                hybrid_table=hybrid,
                left_from=left,
                right_from=right,
                left_pred=left_pred,
                right_pred=right_pred,
                where=where,
                settings_row=settings_row,
            )

    node = self.context.node
    clause = settings_clause(settings_row)

    with Then("GROUP BY date_col"):
        hybrid_out = node.query(
            f"SELECT date_col, count(), sum(value) FROM {hybrid} "
            f"GROUP BY date_col ORDER BY date_col {clause}"
        ).output.strip()
        ref_out = node.query(
            f"SELECT date_col, count(), sum(value) FROM ("
            f"SELECT id, value, date_col FROM {left} WHERE {left_pred} "
            f"UNION ALL "
            f"SELECT id, value, date_col FROM {right} WHERE {right_pred}"
            f") GROUP BY date_col ORDER BY date_col {clause}"
        ).output.strip()
        assert hybrid_out == ref_out

    with Then("ORDER BY id LIMIT 2"):
        hybrid_out = node.query(
            f"SELECT id, value, date_col FROM {hybrid} ORDER BY id LIMIT 2 {clause}"
        ).output.strip()
        ref_out = node.query(
            f"SELECT id, value, date_col FROM ("
            f"SELECT id, value, date_col FROM {left} WHERE {left_pred} "
            f"UNION ALL "
            f"SELECT id, value, date_col FROM {right} WHERE {right_pred}"
            f") ORDER BY id LIMIT 2 {clause}"
        ).output.strip()
        assert hybrid_out == ref_out


@TestScenario
@Name("select where group by prefer localhost")
def select_where_group_by_prefer_localhost(self):
    """SELECT/WHERE/GROUP BY/LIMIT vs UNION ALL with prefer_localhost_replica=1."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()
    _run_queries(self, ctx, PREFER_LOCALHOST)


@TestScenario
@Name("select where group by force remote")
def select_where_group_by_force_remote(self):
    """SELECT/WHERE/GROUP BY/LIMIT vs UNION ALL with prefer_localhost_replica=0."""
    with Given("MT+MT Hybrid"):
        ctx = create_mt_mt_hybrid()
    _run_queries(self, ctx, FORCE_REMOTE)


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_QueryShapes("1.0"),
    RQ_ClickHouse_Hybrid_CorrectnessVsUnion("1.0"),
)
@Name("queries")
def feature(self):
    """Basic Hybrid queries vs UNION ALL reference."""
    for scenario in (
        select_where_group_by_prefer_localhost,
        select_where_group_by_force_remote,
    ):
        Scenario(run=scenario)
