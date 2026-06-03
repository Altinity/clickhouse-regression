"""ClickHouse -> Iceberg data type coverage for EXPORT PARTITION / EXPORT PART.

Round-trips every supported primitive / composite type in
``getIcebergType`` (``accepted_*``) and asserts every type the switch
omits is rejected at CREATE-TABLE or export time (``rejected_*``).

Runs under ``no_catalog`` (direct IcebergS3 writes) for both
``EXPORT PARTITION ID`` and ``EXPORT PART``.

ClickHouse -> Iceberg primitive mapping exercised here:
``Int16/UInt16`` / ``Int32/UInt32`` / ``Int64/UInt64`` -> ``int`` /
``int`` / ``long``; ``Float32`` / ``Float64`` -> ``float`` / ``double``;
``Date`` / ``Date32`` -> ``date``; ``DateTime`` / ``DateTime64`` ->
``timestamp``; ``Time`` -> ``time``; ``String`` -> ``string``; ``UUID``
-> ``uuid``; ``Tuple`` -> ``struct``; ``Array(T)`` -> ``list``;
``Map(K, V)`` -> ``map``; ``Nullable(T)`` -> required=false. Types
absent from the switch (``Int8`` / ``UInt8`` / ``Bool`` /
``FixedString`` / ``Decimal`` / ``Enum8`` / ``LowCardinality(String)``)
power the ``rejected_*`` scenarios.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_DataTypes_Primitives,
    RQ_Iceberg_ExportPartition_DataTypes_Nullable,
    RQ_Iceberg_ExportPartition_DataTypes_Composite,
    RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection,
    RQ_Iceberg_ExportPartition_DataTypes_ExportSurfaces,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    get_active_part_name,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_part,
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    _require_no_catalog,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


BAD_ARGUMENTS = 36


def _export_surface(self):
    """``partition_id`` (default) or ``part`` — set by :func:`feature`."""
    return getattr(self.context, "export_surface", "partition_id")


def _run_export(
    self,
    source_table,
    destination,
    partition_id,
    minio_root_user,
    minio_root_password,
    expected_rows,
    where_clause,
):
    """Dispatch to ``EXPORT PARTITION ID`` or ``EXPORT PART``."""
    surface = _export_surface(self)
    label = "EXPORT PARTITION" if surface == "partition_id" else "EXPORT PART"
    with When(f"{label} for partition '{partition_id}'"):
        if surface == "part":
            part_name = get_active_part_name(
                table_name=source_table,
                partition_id=partition_id,
            )
            export_part(
                source_table=source_table,
                part_name=part_name,
                destination=destination,
                expected_rows=expected_rows,
                where_clause=where_clause,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
        else:
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
            )


def _run_accepted_type(
    self,
    minio_root_user,
    minio_root_password,
    value_column,
    values,
    order_by="id",
    where_clause="year = 2020",
    partition_id="2020",
    expected_rows=None,
    select_expr="*",
):
    """Round-trip a partition through a destination whose value column has
    the type under test (partition column is fixed at ``year Int32``).
    ``select_expr`` lets the caller normalise type-specific
    ``TabSeparated`` formatting differences between source and Iceberg
    read-back.
    """
    columns = f"id Int64, year Int32, {value_column}"
    partition_by = "year"

    source_table = f"mt_{getuid()}"

    with Given(f"create source ReplicatedMergeTree with {value_column!r}"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=partition_by,
        )

    with And("insert the payload"):
        insert_data(table_name=source_table, values=values)

    with And("create the Iceberg destination with matching schema"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    if expected_rows is None:
        # Row-delimiter count: ``(r1), (r2), (r3)`` -> two ``), `` separators,
        # plus 1. Counting ``(`` directly is wrong as soon as a row itself
        # contains a parenthesised literal (e.g. ``map(...)`` / ``tuple(...)``).
        expected_rows = values.count("),") + 1

    _run_export(
        self,
        source_table=source_table,
        destination=destination,
        partition_id=partition_id,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        expected_rows=expected_rows,
        where_clause=where_clause,
    )

    with Then("destination row count matches the source"):
        assert_destination_row_count(
            destination=destination,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=where_clause,
        )

    with And("source and destination rows are byte-identical"):
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partition_where=where_clause,
            order_by=order_by,
            columns=select_expr,
        )


def _run_rejected_type(
    self,
    minio_root_user,
    minio_root_password,
    value_column,
    values,
    partition_id="2020",
):
    """Assert that a column type unsupported by ``getIcebergType`` is
    rejected either at ``CREATE TABLE`` of the IcebergS3 destination or at
    export time.

    The scenario tolerates rejection at either step: silent acceptance of
    an unsupported type is the only outcome that fails the scenario.
    """
    columns = f"id Int64, year Int32, {value_column}"
    partition_by = "year"

    source_table = f"mt_{getuid()}"

    with Given("create source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=partition_by,
        )

    with And("insert the payload so the partition exists"):
        insert_data(table_name=source_table, values=values)

    rejected_at_create = False
    destination = None
    try:
        with And(f"try to create Iceberg destination with {value_column!r}"):
            destination = create_iceberg_destination(
                columns=columns,
                partition_by=partition_by,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    except Exception as exc:
        rejected_at_create = True
        note(f"destination CREATE rejected {value_column!r}: {exc!s}")

    if rejected_at_create:
        return

    surface = _export_surface(self)
    export_label = (
        "EXPORT PARTITION" if surface == "partition_id" else "EXPORT PART"
    )
    with Then(f"{export_label} is rejected for the unsupported type"):
        if surface == "part":
            part_name = get_active_part_name(
                table_name=source_table,
                partition_id=partition_id,
            )
            export_part(
                source_table=source_table,
                part_name=part_name,
                destination=destination,
                exitcode=BAD_ARGUMENTS,
                message="BAD_ARGUMENTS",
                wait_for_completion=False,
            )
        else:
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
                exitcode=BAD_ARGUMENTS,
                message="BAD_ARGUMENTS",
                wait_for_completion=False,
            )


# ---------------------------------------------------------------------------
# Accepted primitives
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Int16")
def accepted_int16(self, minio_root_user, minio_root_password):
    """ClickHouse Int16 -> Iceberg int (required)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int16",
        values="(1, 2020, -32768), (2, 2020, 0), (3, 2020, 32767)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Int32")
def accepted_int32(self, minio_root_user, minio_root_password):
    """ClickHouse Int32 -> Iceberg int (required)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int32",
        values="(1, 2020, -2147483648), (2, 2020, 0), (3, 2020, 2147483647)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Int64")
def accepted_int64(self, minio_root_user, minio_root_password):
    """ClickHouse Int64 -> Iceberg long (required)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int64",
        values="(1, 2020, -9223372036854775808), (2, 2020, 0), (3, 2020, 9223372036854775807)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: UInt32")
def accepted_uint32(self, minio_root_user, minio_root_password):
    """ClickHouse UInt32 -> Iceberg int (values pinned to the signed 32-bit
    range since Iceberg ``int`` is 32-bit signed).
    """
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt32",
        values="(1, 2020, 0), (2, 2020, 1), (3, 2020, 2147483647)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: UInt16")
def accepted_uint16(self, minio_root_user, minio_root_password):
    """``UInt16`` maps to Iceberg ``int``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt16",
        values="(1, 2020, 0), (2, 2020, 65535), (3, 2020, 42)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: UInt64")
def accepted_uint64(self, minio_root_user, minio_root_password):
    """``UInt64`` maps to Iceberg ``long`` (signed).

    Currently XFail: values above ``INT64_MAX`` (row 3 uses u64 max) read
    back as ``-1`` because Iceberg ``long`` cannot represent the full
    unsigned range.
    """
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt64",
        values=(
            "(1, 2020, 0), "
            "(2, 2020, 9223372036854775807), "
            "(3, 2020, 18446744073709551615)"
        ),
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Float32")
def accepted_float32(self, minio_root_user, minio_root_password):
    """ClickHouse Float32 -> Iceberg float."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Float32",
        values="(1, 2020, -1.5), (2, 2020, 0.0), (3, 2020, 3.14)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Float64")
def accepted_float64(self, minio_root_user, minio_root_password):
    """ClickHouse Float64 -> Iceberg double."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Float64",
        values="(1, 2020, -1.5e100), (2, 2020, 0.0), (3, 2020, 1.5e100)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Date")
def accepted_date(self, minio_root_user, minio_root_password):
    """ClickHouse Date -> Iceberg date."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Date",
        values="(1, 2020, '1970-01-01'), (2, 2020, '2020-06-15'), (3, 2020, '2149-06-06')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: Date32")
def accepted_date32(self, minio_root_user, minio_root_password):
    """ClickHouse Date32 -> Iceberg date (wider range than Date)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Date32",
        values="(1, 2020, '1900-01-01'), (2, 2020, '2020-06-15'), (3, 2020, '2299-12-31')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: DateTime")
def accepted_datetime(self, minio_root_user, minio_root_password):
    """ClickHouse DateTime -> Iceberg timestamp; both sides normalised
    to ``DateTime64(6)`` for the byte-compare (Iceberg timestamps are
    microsecond-precision).
    """
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v DateTime",
        values=(
            "(1, 2020, '2020-01-01 00:00:00'), "
            "(2, 2020, '2020-06-15 12:34:56'), "
            "(3, 2020, '2020-12-31 23:59:59')"
        ),
        select_expr="id, year, toDateTime64(v, 6) AS v",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: DateTime64(3)")
def accepted_datetime64(self, minio_root_user, minio_root_password):
    """ClickHouse DateTime64(3) -> Iceberg timestamp; both sides
    normalised to ``DateTime64(6)`` for the byte-compare.
    """
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v DateTime64(3)",
        values=(
            "(1, 2020, '2020-01-01 00:00:00.000'), "
            "(2, 2020, '2020-06-15 12:34:56.789'), "
            "(3, 2020, '2020-12-31 23:59:59.999')"
        ),
        select_expr="id, year, toDateTime64(v, 6) AS v",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: String")
def accepted_string(self, minio_root_user, minio_root_password):
    """ClickHouse String -> Iceberg string (UTF-8)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v String",
        values="(1, 2020, ''), (2, 2020, 'ascii'), (3, 2020, 'unicode: \u2603')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Primitives("1.0"))
@Name("accepted: UUID")
def accepted_uuid(self, minio_root_user, minio_root_password):
    """ClickHouse UUID -> Iceberg uuid."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UUID",
        values=(
            "(1, 2020, '00000000-0000-0000-0000-000000000000'), "
            "(2, 2020, '11111111-2222-3333-4444-555555555555'), "
            "(3, 2020, 'ffffffff-ffff-ffff-ffff-ffffffffffff')"
        ),
    )


# ---------------------------------------------------------------------------
# Nullable
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Nullable("1.0"))
@Name("accepted: Nullable(Int64) with explicit NULLs")
def accepted_nullable_int64(self, minio_root_user, minio_root_password):
    """``Nullable(Int64)`` -> Iceberg ``long`` with ``required = false``;
    payload mixes NULLs and non-NULLs.
    """
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Nullable(Int64)",
        values="(1, 2020, NULL), (2, 2020, 42), (3, 2020, NULL)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Nullable("1.0"))
@Name("accepted: Nullable(String) with explicit NULLs")
def accepted_nullable_string(self, minio_root_user, minio_root_password):
    """``Nullable(String)`` maps to Iceberg ``string`` with ``required = false``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Nullable(String)",
        values="(1, 2020, NULL), (2, 2020, 'present'), (3, 2020, NULL)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Nullable("1.0"))
@Name("accepted: Nullable(UInt64)")
def accepted_nullable_uint64(self, minio_root_user, minio_root_password):
    """``Nullable(UInt64)`` preserves nulls on round-trip."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Nullable(UInt64)",
        values="(1, 2020, 0), (2, 2020, NULL), (3, 2020, 42)",
    )


# ---------------------------------------------------------------------------
# Composite types
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Array(Int32)")
def accepted_array_int32(self, minio_root_user, minio_root_password):
    """``Array(Int32)`` maps to Iceberg ``list<int>`` (non-required)."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(Int32)",
        values="(1, 2020, []), (2, 2020, [1, 2, 3]), (3, 2020, [-1, 0, 1])",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Array(UInt32)")
def accepted_array_uint32(self, minio_root_user, minio_root_password):
    """``Array(UInt32)`` maps to Iceberg ``list<int>``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(UInt32)",
        values="(1, 2020, []), (2, 2020, [0, 1, 42]), (3, 2020, [2147483647])",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Array(UInt64)")
def accepted_array_uint64(self, minio_root_user, minio_root_password):
    """``Array(UInt64)`` maps to Iceberg ``list<long>``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(UInt64)",
        values="(1, 2020, []), (2, 2020, [1, 2]), (3, 2020, [9223372036854775807])",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Array(String)")
def accepted_array_string(self, minio_root_user, minio_root_password):
    """``Array(String)`` maps to Iceberg ``list<string>``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(String)",
        values="(1, 2020, []), (2, 2020, ['a', 'bb']), (3, 2020, ['single'])",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Map(String, Int64)")
def accepted_map_string_int64(self, minio_root_user, minio_root_password):
    """``Map(String, Int64)`` maps to Iceberg ``map<string, long>``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Map(String, Int64)",
        values=(
            "(1, 2020, map('a', 1, 'b', 2)), "
            "(2, 2020, map()), "
            "(3, 2020, map('k', 42))"
        ),
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_Composite("1.0"))
@Name("accepted: Tuple(Int32, String) -> struct")
def accepted_tuple(self, minio_root_user, minio_root_password):
    """``Tuple(x Int32, y String)`` maps to Iceberg ``struct<x: int, y: string>``."""
    _run_accepted_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Tuple(x Int32, y String)",
        values="(1, 2020, (1, 'a')), (2, 2020, (2, 'bb')), (3, 2020, (3, 'ccc'))",
    )


# ---------------------------------------------------------------------------
# Rejected types
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: Int8")
def rejected_int8(self, minio_root_user, minio_root_password):
    """``Int8`` is not handled by ``getIcebergType`` — must be rejected."""
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int8",
        values="(1, 2020, -128), (2, 2020, 0), (3, 2020, 127)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: UInt8")
def rejected_uint8(self, minio_root_user, minio_root_password):
    """``UInt8`` is not handled by ``getIcebergType`` — must be rejected."""
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt8",
        values="(1, 2020, 0), (2, 2020, 1), (3, 2020, 255)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: Bool")
def rejected_bool(self, minio_root_user, minio_root_password):
    """``Bool`` is not handled by ``getIcebergType`` — must be rejected
    (Iceberg has ``boolean``, so this is a known mapping gap).
    """
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Bool",
        values="(1, 2020, true), (2, 2020, false), (3, 2020, true)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: FixedString(16)")
def rejected_fixed_string(self, minio_root_user, minio_root_password):
    """``FixedString(N)`` is not mapped to an Iceberg type — must be rejected."""
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v FixedString(16)",
        values=(
            "(1, 2020, '0123456789abcdef'), "
            "(2, 2020, 'fedcba9876543210'), "
            "(3, 2020, 'aaaaaaaaaaaaaaaa')"
        ),
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: Decimal(10, 2)")
def rejected_decimal(self, minio_root_user, minio_root_password):
    """``Decimal`` is not handled by ``getIcebergType`` — must be rejected
    (Iceberg has ``decimal``, so this is another known mapping gap).
    """
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Decimal(10, 2)",
        values="(1, 2020, 1.23), (2, 2020, -4.56), (3, 2020, 9999.99)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: Enum8")
def rejected_enum8(self, minio_root_user, minio_root_password):
    """``Enum8`` has no ``getIcebergType`` mapping — must be rejected
    (Iceberg has no native enum; ClickHouse refuses to coerce to string).
    """
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Enum8('red' = 1, 'green' = 2, 'blue' = 3)",
        values="(1, 2020, 'red'), (2, 2020, 'green'), (3, 2020, 'blue')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: LowCardinality(String)")
def rejected_low_cardinality(self, minio_root_user, minio_root_password):
    """``LowCardinality(String)`` is not unwrapped by ``getIcebergType``
    — must be rejected.
    """
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v LowCardinality(String)",
        values="(1, 2020, 'a'), (2, 2020, 'b'), (3, 2020, 'a')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_UnsupportedRejection("1.0"))
@Name("rejected: Array(LowCardinality(String))")
def rejected_array_low_cardinality_string(
    self, minio_root_user, minio_root_password
):
    """``Array(LowCardinality(String))`` is not mapped — must be rejected."""
    _run_rejected_type(
        self,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(LowCardinality(String))",
        values="(1, 2020, []), (2, 2020, ['a', 'b']), (3, 2020, ['x'])",
    )


# ---------------------------------------------------------------------------
# Feature entry point
# ---------------------------------------------------------------------------


ACCEPTED_SCENARIOS = (
    accepted_int16,
    accepted_int32,
    accepted_int64,
    accepted_uint32,
    accepted_uint16,
    accepted_uint64,
    accepted_float32,
    accepted_float64,
    accepted_date,
    accepted_date32,
    accepted_datetime,
    accepted_datetime64,
    accepted_string,
    accepted_uuid,
    accepted_nullable_int64,
    accepted_nullable_string,
    accepted_nullable_uint64,
    accepted_array_int32,
    accepted_array_uint32,
    accepted_array_uint64,
    accepted_array_string,
    accepted_map_string_int64,
    accepted_tuple,
)

REJECTED_SCENARIOS = (
    rejected_int8,
    rejected_uint8,
    rejected_bool,
    rejected_fixed_string,
    rejected_decimal,
    rejected_enum8,
    rejected_low_cardinality,
    rejected_array_low_cardinality_string,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_DataTypes_ExportSurfaces("1.0"))
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """ClickHouse -> Iceberg data types for ``EXPORT PARTITION`` and
    ``EXPORT PART`` (``no_catalog`` / direct IcebergS3 writes only).
    """
    _require_no_catalog(
        "CH -> Iceberg write-side type mapping is identical across modes; "
        "catalog read-back widens Date/DateTime and breaks the byte-compare "
        "even though the Iceberg file is correct"
    )
    for surface, surface_label in (
        ("partition_id", "export partition id"),
        ("part", "export part"),
    ):
        with Feature(surface_label):
            self.context.export_surface = surface
            with Feature("accepted"):
                for scenario in ACCEPTED_SCENARIOS:
                    Scenario(test=scenario, flags=TE)(
                        minio_root_user=minio_root_user,
                        minio_root_password=minio_root_password,
                    )
            with Feature("rejected"):
                for scenario in REJECTED_SCENARIOS:
                    Scenario(test=scenario, flags=TE)(
                        minio_root_user=minio_root_user,
                        minio_root_password=minio_root_password,
                    )
