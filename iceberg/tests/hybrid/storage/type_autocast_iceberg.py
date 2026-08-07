from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table
from helpers.datatypes import UInt64, UInt32, Int64, Int32, Date

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_AutoCast,
    RQ_ClickHouse_Hybrid_TypeSeams,
)

from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)
from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)

from iceberg.tests.hybrid.core.common import (
    LEFT_PREDICATE,
    RIGHT_PREDICATE,
    PREFER_LOCALHOST,
    AUTO_CAST,
    cluster_all_tf,
    create_mergetree_segment,
    settings_clause,
    values_sql,
)



MISMATCH_ROWS = (
    (1, 100, "2025-02-01"),
    (2, 200, "2025-06-15"),
    (3, 300, "2024-06-01"),
    (4, 400, "2025-01-01"),
)


@TestStep(Given)
def create_uint_int_iceberg_hybrid(
    self,
    minio_root_user,
    minio_root_password,
    left_id_type,
    right_id_sql_type,
    hybrid_id_type,
    left_id_sql_type,
):
    """cluster(MT) with unsigned id + IcebergS3 with signed id + Hybrid head."""
    self.context.catalog = "no"
    node = self.context.node

    left_cols = [
        Column(name="id", datatype=left_id_type),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]
    hybrid_cols = [
        Column(name="id", datatype=hybrid_id_type),
        Column(name="value", datatype=Int32()),
        Column(name="date_col", datatype=Date()),
    ]

    with By("create MergeTree hot segment with unsigned id"):
        left = create_mergetree_segment(
            cluster="all",
            seed_all_nodes=False,
            columns=left_cols,
            rows=MISMATCH_ROWS,
        )

    iceberg_columns_sql = f"id {right_id_sql_type}, value Int32, date_col Date"

    with By("create IcebergS3 cold segment with signed id and seed rows"):
        iceberg = create_iceberg_s3_destination(
            columns=iceberg_columns_sql,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(
            destination=iceberg,
            values=values_sql(MISMATCH_ROWS),
        )

    hybrid = f"hybrid_{getuid()}"
    left_tf = cluster_all_tf(left)

    with By("create Hybrid with signed id head type"):
        create_table(
            name=hybrid,
            engine=(
                f"Hybrid({left_tf}, {LEFT_PREDICATE}, {iceberg}, {RIGHT_PREDICATE})"
            ),
            columns=hybrid_cols,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    return {
        "hybrid": hybrid,
        "left": left,
        "right": iceberg,
        "left_from": left_tf,
        "right_from": iceberg,
        "left_id_sql_type": left_id_sql_type,
    }


@TestScenario
@Name("UInt64 vs Int64 Iceberg auto cast on")
def uint64_vs_int64_iceberg_auto_cast_on(self, minio_root_user, minio_root_password):
    """Auto-cast bridges UInt64 MT and Int64 Iceberg."""
    node = self.context.node

    with Given("mismatched UInt64/Int64 Hybrid over Iceberg"):
        ctx = create_uint_int_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            left_id_type=UInt64(),
            right_id_sql_type="Int64",
            hybrid_id_type=Int64(),
            left_id_sql_type="UInt64",
        )

    clause = settings_clause(AUTO_CAST)

    with Then("count matches exclusive reference"):
        h = node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        assert h == "4", error()

    with And("sum(id) matches casted reference"):
        hybrid_sum = node.query(
            f"SELECT sum(id) FROM {ctx['hybrid']} {clause}"
        ).output.strip()
        ref_sum = node.query(
            f"SELECT sum(id) FROM ("
            f"SELECT toInt64(id) AS id FROM {ctx['left_from']} WHERE {LEFT_PREDICATE} "
            f"UNION ALL "
            f"SELECT id FROM {ctx['right_from']} WHERE {RIGHT_PREDICATE}"
            f") {clause}"
        ).output.strip()
        assert hybrid_sum == ref_sum, error()


@TestScenario
@Name("UInt64 vs Int64 Iceberg auto cast off")
def uint64_vs_int64_iceberg_auto_cast_off(self, minio_root_user, minio_root_password):
    """Without auto-cast, mismatch should error or still be correct if coerced."""
    node = self.context.node

    with Given("mismatched UInt64/Int64 Hybrid over Iceberg"):
        ctx = create_uint_int_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            left_id_type=UInt64(),
            right_id_sql_type="Int64",
            hybrid_id_type=Int64(),
            left_id_sql_type="UInt64",
        )

    clause = settings_clause(PREFER_LOCALHOST)

    with When("query Hybrid with auto-cast disabled"):
        r = node.query(
            f"SELECT count() FROM {ctx['hybrid']} {clause}",
            no_checks=True,
        )

    with Then("error or correct casted count"):
        if r.exitcode == 0:
            casted = node.query(
                f"SELECT count() FROM ("
                f"SELECT toInt64(id) AS id, value, date_col "
                f"FROM {ctx['left_from']} WHERE {LEFT_PREDICATE} "
                f"UNION ALL "
                f"SELECT id, value, date_col FROM {ctx['right_from']} "
                f"WHERE {RIGHT_PREDICATE}"
                f") {clause}"
            ).output.strip()
            assert r.output.strip() == casted, error()
        else:
            assert r.exitcode != 0, error()


@TestScenario
@Name("UInt32 vs Int32 Iceberg auto cast on")
def uint32_vs_int32_iceberg_auto_cast_on(self, minio_root_user, minio_root_password):
    """Auto-cast bridges UInt32 MT and Int32 Iceberg."""
    node = self.context.node

    with Given("mismatched UInt32/Int32 Hybrid over Iceberg"):
        ctx = create_uint_int_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            left_id_type=UInt32(),
            right_id_sql_type="Int32",
            hybrid_id_type=Int32(),
            left_id_sql_type="UInt32",
        )

    clause = settings_clause(AUTO_CAST)

    with Then("count is 4"):
        h = node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        assert h == "4", error()


@TestScenario
@Name("uniq across UInt64 Int64 Iceberg with auto cast")
def uniq_across_uint64_int64_iceberg(self, minio_root_user, minio_root_password):
    """uniq/uniqExact across MT↔Iceberg type seam with auto-cast on."""
    node = self.context.node

    with Given("mismatched UInt64/Int64 Hybrid over Iceberg"):
        ctx = create_uint_int_iceberg_hybrid(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            left_id_type=UInt64(),
            right_id_sql_type="Int64",
            hybrid_id_type=Int64(),
            left_id_sql_type="UInt64",
        )

    clause = settings_clause(AUTO_CAST)
    ref = (
        f"(SELECT toInt64(id) AS id FROM {ctx['left_from']} WHERE {LEFT_PREDICATE} "
        f"UNION ALL "
        f"SELECT id FROM {ctx['right_from']} WHERE {RIGHT_PREDICATE})"
    )

    with Then("uniq(id) matches reference"):
        h = node.query(f"SELECT uniq(id) FROM {ctx['hybrid']} {clause}").output.strip()
        r = node.query(f"SELECT uniq(id) FROM {ref} {clause}").output.strip()
        assert h == r, error()

    with And("uniqExact(id) matches reference"):
        h = node.query(
            f"SELECT uniqExact(id) FROM {ctx['hybrid']} {clause}"
        ).output.strip()
        r = node.query(f"SELECT uniqExact(id) FROM {ref} {clause}").output.strip()
        assert h == r, error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_AutoCast("1.0"),
    RQ_ClickHouse_Hybrid_TypeSeams("1.0"),
)
@Name("type autocast iceberg")
def feature(self, minio_root_user, minio_root_password):
    """Type mismatch on cluster(MT)+IcebergS3 with auto-cast on/off + uniq."""
    self.context.catalog = "no"

    for scenario in (
        uint64_vs_int64_iceberg_auto_cast_on,
        uint64_vs_int64_iceberg_auto_cast_off,
        uint32_vs_int32_iceberg_auto_cast_on,
        uniq_across_uint64_int64_iceberg,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
