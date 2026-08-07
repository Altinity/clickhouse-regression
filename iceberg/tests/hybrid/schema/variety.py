"""PR-scale schema variety shapes (§12.1 / §8) on Hybrid MT+MT and MT+Iceberg."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_SchemaVariety,
)

from iceberg.tests.export_partition.steps.export_operations import (
    insert_into_iceberg_destination,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)

from iceberg.tests.hybrid.core.common import (
    AUTO_CAST,
    LEFT_PREDICATE,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    remote_tf,
    settings_clause,
)
from iceberg.tests.hybrid.schema.common import (
    assert_fingerprints_equal,
    create_mt_pair_and_hybrid,
    exclusive_union_from,
    fingerprint_expr,
)


# Shared date watermark bands for variety datasets.
HOT_ROW_DATE = "2025-02-01"
COLD_ROW_DATE = "2024-06-01"


@TestScenario
@Name("financial types MT+MT")
def financial_types_mt_mt(self):
    """Decimal / FixedString / Enum8 on both MergeTree segments."""
    columns = (
        "id Int32, amount Decimal(18, 4), code FixedString(4), "
        "color Enum8('red' = 1, 'green' = 2, 'blue' = 3), date_col Date"
    )
    # Same rows on both segments; exclusive watermark still covers all ids.
    values = (
        f"(1, 12.3400, 'ABCD', 'red', '{HOT_ROW_DATE}'), "
        f"(2, 99.9900, 'WXYZ', 'blue', '{HOT_ROW_DATE}'), "
        f"(3, 1.0000, 'AAAA', 'green', '{COLD_ROW_DATE}'), "
        f"(4, 50.5000, 'BBBB', 'red', '{COLD_ROW_DATE}')"
    )

    with Given("Hybrid over financial-typed MergeTree segments"):
        ctx = create_mt_pair_and_hybrid(
            columns_sql=columns,
            order_by="(date_col, id)",
            left_values=values,
            right_values=values,
        )

    fp_cols = "id, toString(amount), code, toString(color), date_col"
    hybrid_sql = fingerprint_expr(ctx["hybrid"], fp_cols)
    ref_sql = fingerprint_expr(
        exclusive_union_from(
            ctx["left"], ctx["right"], ctx["left_pred"], ctx["right_pred"]
        ),
        fp_cols,
    )

    with Then("fingerprint matches exclusive reference"):
        assert_fingerprints_equal(
            hybrid_sql=hybrid_sql, reference_sql=ref_sql, label="financial"
        )


@TestScenario
@Name("telemetry types MT+MT")
def telemetry_types_mt_mt(self):
    """LowCardinality / DateTime64 / Map on both MergeTree segments."""
    columns = (
        "id Int32, "
        "region LowCardinality(String), "
        "ts DateTime64(3, 'UTC'), "
        "attrs Map(String, Int64), "
        "date_col Date"
    )
    values = (
        f"(1, 'us-east', '2025-02-01 10:00:00.123', {{'cpu':10,'mem':20}}, '{HOT_ROW_DATE}'), "
        f"(2, 'eu-west', '2025-06-15 11:00:00.456', {{'cpu':11}}, '{HOT_ROW_DATE}'), "
        f"(3, 'us-east', '2024-06-01 09:00:00.000', {{'mem':5}}, '{COLD_ROW_DATE}'), "
        f"(4, 'ap-south', '2025-01-01 08:00:00.001', {{'cpu':1,'mem':2}}, '{COLD_ROW_DATE}')"
    )

    with Given("Hybrid over telemetry-typed MergeTree segments"):
        ctx = create_mt_pair_and_hybrid(
            columns_sql=columns,
            order_by="(date_col, id)",
            left_values=values,
            right_values=values,
        )

    fp_cols = "id, region, toString(ts), toString(attrs), date_col"
    hybrid_sql = fingerprint_expr(ctx["hybrid"], fp_cols)
    ref_sql = fingerprint_expr(
        exclusive_union_from(
            ctx["left"], ctx["right"], ctx["left_pred"], ctx["right_pred"]
        ),
        fp_cols,
    )

    with Then("fingerprint matches exclusive reference"):
        assert_fingerprints_equal(
            hybrid_sql=hybrid_sql, reference_sql=ref_sql, label="telemetry"
        )


@TestScenario
@Name("logs types MT+MT")
def logs_types_mt_mt(self):
    """String / Array on both MergeTree segments."""
    columns = (
        "id Int32, message String, tags Array(String), date_col Date"
    )
    values = (
        f"(1, 'ok', ['a','b'], '{HOT_ROW_DATE}'), "
        f"(2, 'warn', ['b'], '{HOT_ROW_DATE}'), "
        f"(3, 'err', ['c','d'], '{COLD_ROW_DATE}'), "
        f"(4, 'ok', [], '{COLD_ROW_DATE}')"
    )

    with Given("Hybrid over log-typed MergeTree segments"):
        ctx = create_mt_pair_and_hybrid(
            columns_sql=columns,
            order_by="(date_col, id)",
            left_values=values,
            right_values=values,
        )

    fp_cols = "id, message, toString(tags), date_col"
    hybrid_sql = fingerprint_expr(ctx["hybrid"], fp_cols)
    ref_sql = fingerprint_expr(
        exclusive_union_from(
            ctx["left"], ctx["right"], ctx["left_pred"], ctx["right_pred"]
        ),
        fp_cols,
    )

    with Then("fingerprint matches exclusive reference"):
        assert_fingerprints_equal(
            hybrid_sql=hybrid_sql, reference_sql=ref_sql, label="logs"
        )


@TestScenario
@Name("iceberg-compatible nested types")
def iceberg_compatible_nested(self, minio_root_user, minio_root_password):
    """DateTime64 / Array / Map on MT + IcebergS3 (types Iceberg accepts)."""
    self.context.catalog = "no"
    node = self.context.node

    columns_sql = (
        "id Int32, "
        "ts DateTime64(3), "
        "tags Array(Int32), "
        "attrs Map(String, Int64), "
        "date_col Date"
    )
    values = (
        f"(1, '2025-02-01 10:00:00.123', [1,2], {{'k':1}}, '{HOT_ROW_DATE}'), "
        f"(2, '2025-06-15 11:00:00.456', [3], {{'k':2}}, '{HOT_ROW_DATE}'), "
        f"(3, '2024-06-01 09:00:00.000', [4,5], {{'k':3}}, '{COLD_ROW_DATE}'), "
        f"(4, '2025-01-01 08:00:00.001', [], {{'k':4}}, '{COLD_ROW_DATE}')"
    )

    left = f"mt_{getuid()}"
    with Given("MergeTree hot segment"):
        node.query(
            f"CREATE TABLE {left} ({columns_sql}) "
            f"ENGINE = MergeTree ORDER BY (date_col, id) "
            f"PARTITION BY toYYYYMM(date_col)"
        )
        node.query(f"INSERT INTO {left} VALUES {values}")

    with And("IcebergS3 cold segment with mirrored rows"):
        ice = create_iceberg_s3_destination(
            columns=columns_sql,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(destination=ice, values=values)

    hybrid = f"hybrid_{getuid()}"
    left_tf = remote_tf(left)

    with And("create Hybrid MT + Iceberg"):
        node.query(
            f"CREATE TABLE {hybrid} ({columns_sql}) "
            f"ENGINE = Hybrid({left_tf}, {LEFT_PREDICATE}, {ice}, {RIGHT_PREDICATE})",
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    # Normalize DateTime64 in the hash (Iceberg often stores us vs MT ms).
    # Do not re-alias as `ts` — hybrid_table_auto_cast_columns already emits that alias.
    hash_cols = (
        "id, toString(toDateTime64(ts, 6)), toString(tags), toString(attrs), date_col"
    )
    clause = settings_clause(PREFER_LOCALHOST, AUTO_CAST)

    with Then("Hybrid fingerprint matches exclusive reference"):
        hybrid_out = node.query(
            f"SELECT count(), groupBitXor(cityHash64({hash_cols})) "
            f"FROM {hybrid} {clause}"
        ).output.strip()
        ref_out = node.query(
            f"SELECT count(), groupBitXor(cityHash64({hash_cols})) FROM ("
            f"SELECT * FROM {left} WHERE {LEFT_PREDICATE} "
            f"UNION ALL "
            f"SELECT * FROM {ice} WHERE {RIGHT_PREDICATE}"
            f") {clause}"
        ).output.strip()
        assert hybrid_out == ref_out, error()


@TestScenario
@Name("fixedstring string seam with auto-cast")
def fixedstring_string_seam(self, minio_root_user, minio_root_password):
    """MT FixedString vs Iceberg String bridged by hybrid_table_auto_cast_columns."""
    self.context.catalog = "no"
    node = self.context.node

    left_cols = "id Int32, code FixedString(4), date_col Date"
    ice_cols = "id Int32, code String, date_col Date"
    values = (
        f"(1, 'ABCD', '{HOT_ROW_DATE}'), "
        f"(2, 'WXYZ', '{HOT_ROW_DATE}'), "
        f"(3, 'AAAA', '{COLD_ROW_DATE}'), "
        f"(4, 'BBBB', '{COLD_ROW_DATE}')"
    )
    ice_values = (
        f"(1, 'ABCD', '{HOT_ROW_DATE}'), "
        f"(2, 'WXYZ', '{HOT_ROW_DATE}'), "
        f"(3, 'AAAA', '{COLD_ROW_DATE}'), "
        f"(4, 'BBBB', '{COLD_ROW_DATE}')"
    )

    left = f"mt_{getuid()}"
    with Given("MergeTree with FixedString code"):
        node.query(
            f"CREATE TABLE {left} ({left_cols}) "
            f"ENGINE = MergeTree ORDER BY (date_col, id) "
            f"PARTITION BY toYYYYMM(date_col)"
        )
        node.query(f"INSERT INTO {left} VALUES {values}")

    with And("IcebergS3 with String code"):
        ice = create_iceberg_s3_destination(
            columns=ice_cols,
            partition_by="",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        insert_into_iceberg_destination(destination=ice, values=ice_values)

    hybrid = f"hybrid_{getuid()}"
    left_tf = remote_tf(left)
    # Hybrid header uses String so both sides cast into a common type.
    hybrid_cols = "id Int32, code String, date_col Date"

    with And("create Hybrid with String header"):
        node.query(
            f"CREATE TABLE {hybrid} ({hybrid_cols}) "
            f"ENGINE = Hybrid({left_tf}, {LEFT_PREDICATE}, {ice}, {RIGHT_PREDICATE})",
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    clause_off = settings_clause(PREFER_LOCALHOST)
    clause_on = settings_clause(AUTO_CAST)

    with Then("without auto-cast the FixedString/String seam may fail"):
        result = node.query(
            f"SELECT count() FROM {hybrid} {clause_off}",
            no_checks=True,
        )
        # Soft check: either succeeds (CH coerces) or fails — with auto-cast must succeed.
        note(f"auto_cast=0 exitcode={result.exitcode} out={result.output[:120]!r}")

    with And("with auto-cast fingerprint matches reference"):
        hybrid_out = node.query(
            f"SELECT count(), groupBitXor(cityHash64(id, code, toString(date_col))) "
            f"FROM {hybrid} {clause_on}"
        ).output.strip()
        ref_out = node.query(
            f"SELECT count(), groupBitXor(cityHash64(id, code, toString(date_col))) FROM ("
            f"SELECT id, toString(code) AS code, date_col FROM {left} WHERE {LEFT_PREDICATE} "
            f"UNION ALL "
            f"SELECT id, code, date_col FROM {ice} WHERE {RIGHT_PREDICATE}"
            f") {clause_on}"
        ).output.strip()
        assert hybrid_out == ref_out, error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_SchemaVariety("1.0"),
)
@Name("variety")
def feature(self, minio_root_user, minio_root_password):
    """Reduced-scale schema variety shapes for PR jobs."""
    for scenario in (
        financial_types_mt_mt,
        telemetry_types_mt_mt,
        logs_types_mt_mt,
    ):
        Scenario(run=scenario)

    for scenario in (
        iceberg_compatible_nested,
        fixedstring_string_seam,
    ):
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
