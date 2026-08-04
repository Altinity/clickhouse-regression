from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Lifecycle_ExportThenWatermark,
    RQ_ClickHouse_Hybrid_Lifecycle_OverlapDiscipline,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    WATERMARK,
    assert_hybrid_matches_reference,
    fingerprint_sql,
    settings_clause,
)
from iceberg.tests.hybrid.core.insert_routing import insert_sql
from iceberg.tests.hybrid.lifecycle.common import (
    ADVANCED_LEFT,
    ADVANCED_RIGHT,
    ADVANCED_WATERMARK,
    create_exportable_hot_segment,
    create_hybrid_remote_iceberg,
    create_iceberg_cold_destination,
    create_or_replace_hybrid,
    export_partitions_matching,
)


def _cold_row_count(watermark=WATERMARK):
    return sum(1 for _, _, date_ in ALL_ROWS if date_ < watermark)


def _hot_row_count(watermark=WATERMARK):
    return sum(1 for _, _, date_ in ALL_ROWS if date_ >= watermark)


@TestScenario
@Name("export then advance static watermark")
def export_then_advance_watermark(self, minio_root_user, minio_root_password):
    """EXPORT cold partitions → advance static W → delete hot range → verify."""
    node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)

    with Given("exportable hot MergeTree with full dataset"):
        hot = create_exportable_hot_segment()

    with And("empty Iceberg cold destination"):
        ice = create_iceberg_cold_destination(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("create Hybrid remote(hot) + Iceberg at initial watermark"):
        ctx = create_hybrid_remote_iceberg(hot_table=hot, iceberg_destination=ice)

    with When(f"EXPORT partitions with date_col < '{WATERMARK}'"):
        export_partitions_matching(
            source_table=hot,
            destination=ice,
            where=RIGHT_PREDICATE,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_rows=_cold_row_count(),
        )

    with Then("Hybrid fingerprint matches exclusive reference at initial W"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=ctx["left_from"],
            right_from=ctx["right_from"],
            left_pred=ctx["left_pred"],
            right_pred=ctx["right_pred"],
            settings_row=PREFER_LOCALHOST,
        )

    with And("INSERT through Hybrid lands on hot only"):
        new_row = (50, 500, "2025-07-01")
        node.query(insert_sql(ctx["hybrid"], new_row), exitcode=0)
        hot_count = node.query(
            f"SELECT count() FROM {hot} WHERE id = 50"
        ).output.strip()
        ice_count = node.query(
            f"SELECT count() FROM {ctx['right_from']} WHERE id = 50 {clause}"
        ).output.strip()
        assert hot_count == "1", error()
        assert ice_count == "0", error()

    with When(f"EXPORT partitions newly cold under '{ADVANCED_WATERMARK}'"):
        # Rows that become cold with the advanced watermark and were still on
        # the hot side of the initial watermark (e.g. 2025-02-01).
        export_partitions_matching(
            source_table=hot,
            destination=ice,
            where=f"{LEFT_PREDICATE} AND {ADVANCED_RIGHT}",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_rows=_cold_row_count(ADVANCED_WATERMARK),
        )

    with And("CREATE OR REPLACE Hybrid with advanced watermark"):
        create_or_replace_hybrid(
            hybrid_name=ctx["hybrid"],
            left_tf=ctx["left_tf"],
            left_pred=ADVANCED_LEFT,
            right_tf=ctx["right_tf"],
            right_pred=ADVANCED_RIGHT,
        )

    with And("delete exported range from hot only after watermark advanced"):
        node.query(
            f"ALTER TABLE {hot} DELETE WHERE {ADVANCED_RIGHT}",
            settings=[("mutations_sync", 1)],
        )

    with Then("SHOW CREATE reflects the advanced watermark"):
        show = node.query(f"SHOW CREATE TABLE {ctx['hybrid']}").output
        assert ADVANCED_WATERMARK in show, error()
        assert f"date_col >= '{WATERMARK}'" not in show, error()

    with And("fingerprint matches exclusive reference at advanced W"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=hot,
            right_from=ctx["right_from"],
            left_pred=ADVANCED_LEFT,
            right_pred=ADVANCED_RIGHT,
            settings_row=PREFER_LOCALHOST,
        )

    with And("no gaps: Hybrid row count equals distinct dataset plus insert"):
        expected = len(ALL_ROWS) + 1  # + INSERT (50, ...)
        count = node.query(
            f"SELECT count() FROM {ctx['hybrid']} {clause}"
        ).output.strip()
        assert count == str(expected), error()

    with And("hot segment retains only the advanced hot range"):
        hot_left = node.query(
            f"SELECT count() FROM {hot} WHERE {ADVANCED_LEFT}"
        ).output.strip()
        hot_cold = node.query(
            f"SELECT count() FROM {hot} WHERE {ADVANCED_RIGHT}"
        ).output.strip()
        assert hot_cold == "0", error()
        assert int(hot_left) == _hot_row_count(ADVANCED_WATERMARK) + 1, error()


@TestScenario
@Name("overlap discipline export before delete")
def overlap_discipline_export_before_delete(
    self, minio_root_user, minio_root_password
):
    """Deleting the cold range from hot before advancing W leaves a Hybrid gap."""
    node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)

    with Given("exportable hot MergeTree and empty Iceberg"):
        hot = create_exportable_hot_segment()
        ice = create_iceberg_cold_destination(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("EXPORT cold partitions and create Hybrid"):
        export_partitions_matching(
            source_table=hot,
            destination=ice,
            where=RIGHT_PREDICATE,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_rows=_cold_row_count(),
        )
        ctx = create_hybrid_remote_iceberg(hot_table=hot, iceberg_destination=ice)

    with And("incorrectly delete cold range from hot while W still covers ice"):
        # Cold rows remain visible via Iceberg; deleting hot cold data is fine
        # at the *initial* W. The gap appears when W advances without export.
        node.query(
            f"ALTER TABLE {hot} DELETE WHERE {RIGHT_PREDICATE}",
            settings=[("mutations_sync", 1)],
        )

    with Then("at initial W, Hybrid is still complete via Iceberg"):
        assert_hybrid_matches_reference(
            hybrid_table=ctx["hybrid"],
            left_from=hot,
            right_from=ctx["right_from"],
            left_pred=LEFT_PREDICATE,
            right_pred=RIGHT_PREDICATE,
            settings_row=PREFER_LOCALHOST,
        )

    with When("advance W without exporting the newly cold Feb partition"):
        create_or_replace_hybrid(
            hybrid_name=ctx["hybrid"],
            left_tf=ctx["left_tf"],
            left_pred=ADVANCED_LEFT,
            right_tf=ctx["right_tf"],
            right_pred=ADVANCED_RIGHT,
        )

    with Then("Hybrid has a gap versus the full dataset"):
        hybrid_count = int(
            node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        )
        assert hybrid_count < len(ALL_ROWS), error(
            f"expected gap after advancing W without export, got count={hybrid_count}"
        )


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Lifecycle_ExportThenWatermark("1.0"),
    RQ_ClickHouse_Hybrid_Lifecycle_OverlapDiscipline("1.0"),
)
@Name("export then watermark")
def feature(self, minio_root_user, minio_root_password):
    """EXPORT PARTITION then advance static Hybrid watermark (overlap discipline)."""
    self.context.catalog = "no"

    for scenario in (
        export_then_advance_watermark,
        overlap_discipline_export_before_delete,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
