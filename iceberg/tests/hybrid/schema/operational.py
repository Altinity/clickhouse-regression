"""Operational drills: Iceberg unreachable + EXPORT lag with static watermarks."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_Operational_UnreachableCold,
    RQ_ClickHouse_Hybrid_Operational_ExportLag,
)

from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)

from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS_SQL,
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    WATERMARK,
    remote_tf,
    settings_clause,
    values_sql,
)
from iceberg.tests.hybrid.lifecycle.common import (
    create_exportable_hot_segment,
    create_hybrid_remote_iceberg,
    create_iceberg_cold_destination,
    export_partitions_matching,
)


@TestScenario
@Name("iceberg unreachable hot-only query")
def iceberg_unreachable_hot_only(self, minio_root_user, minio_root_password):
    """After dropping the Iceberg segment, hot-only filters still succeed."""
    self.context.catalog = "no"
    node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)

    with Given("Hybrid remote(MT) + IcebergS3 with mirrored data"):
        left = f"mt_{getuid()}"
        node.query(
            f"CREATE TABLE {left} ({COLUMNS_SQL}) "
            f"ENGINE = MergeTree ORDER BY (date_col, id) "
            f"PARTITION BY toYYYYMM(date_col)"
        )
        node.query(
            f"INSERT INTO {left} (id, value, date_col) VALUES {values_sql(ALL_ROWS)}"
        )
        ice = create_iceberg_s3_destination(
            columns=COLUMNS_SQL,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(destination=ice, values=values_sql(ALL_ROWS))

        hybrid = f"hybrid_{getuid()}"
        left_tf = remote_tf(left)
        node.query(
            f"CREATE TABLE {hybrid} ({COLUMNS_SQL}) "
            f"ENGINE = Hybrid({left_tf}, {LEFT_PREDICATE}, {ice}, {RIGHT_PREDICATE})",
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    with When("drop the Iceberg cold segment"):
        node.query(f"DROP TABLE {ice} SYNC")

    with Then("hot-only WHERE still returns hot rows"):
        count = node.query(
            f"SELECT count() FROM {hybrid} "
            f"WHERE date_col >= '{WATERMARK}' {clause}"
        ).output.strip()
        expected = str(sum(1 for _, _, d in ALL_ROWS if d >= WATERMARK))
        assert count == expected, error()

    with And("full scan that needs the cold segment fails or returns a gap"):
        result = node.query(
            f"SELECT count() FROM {hybrid} {clause}",
            no_checks=True,
        )
        # Product may error on missing segment or return only hot rows.
        if result.exitcode == 0:
            assert int(result.output.strip()) < len(ALL_ROWS), error(
                "expected a gap when Iceberg segment is gone"
            )
        else:
            note(f"full scan failed as expected: {result.output[:200]}")


@TestScenario
@Name("export lag leaves cold gap until export")
def export_lag_cold_gap(self, minio_root_user, minio_root_password):
    """With empty Iceberg, Hybrid exclusive W omits cold rows until EXPORT fills ice."""
    self.context.catalog = "no"
    node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)

    with Given("exportable hot MT with full dataset and empty Iceberg"):
        hot = create_exportable_hot_segment()
        ice = create_iceberg_cold_destination(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        ctx = create_hybrid_remote_iceberg(hot_table=hot, iceberg_destination=ice)

    with Then("before EXPORT, Hybrid count is only the hot band"):
        count = int(
            node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        )
        hot_n = sum(1 for _, _, d in ALL_ROWS if d >= WATERMARK)
        assert count == hot_n, error(f"expected hot-only {hot_n}, got {count}")

    with When("EXPORT cold partitions into Iceberg"):
        cold_n = sum(1 for _, _, d in ALL_ROWS if d < WATERMARK)
        export_partitions_matching(
            source_table=hot,
            destination=ice,
            where=RIGHT_PREDICATE,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_rows=cold_n,
        )

    with Then("after EXPORT, Hybrid covers the full exclusive dataset"):
        count = int(
            node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        )
        assert count == len(ALL_ROWS), error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_Operational_UnreachableCold("1.0"),
    RQ_ClickHouse_Hybrid_Operational_ExportLag("1.0"),
)
@Name("operational")
def feature(self, minio_root_user, minio_root_password):
    """EXPORT lag and Iceberg-unreachable drills with static watermarks."""
    for scenario in (
        iceberg_unreachable_hot_only,
        export_lag_cold_gap,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
