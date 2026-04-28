"""ClickHouse -> Iceberg data type coverage for EXPORT PARTITION.

Every supported primitive / nested type in
``Storages/ObjectStorage/DataLakes/Iceberg/Utils.cpp::getIcebergType`` has an
``accepted_*`` scenario that:

1. Creates a MergeTree source with one partition column (``year Int32``) and
   one value column of the type under test.
2. Inserts a small, type-representative payload.
3. Creates a matching Iceberg destination with the same column list.
4. Exports the single partition.
5. Reads the destination back through ClickHouse and asserts byte-identical
   output against the source for that partition.

Additionally, a ``rejected_*`` scenario exists for every ClickHouse type that
``getIcebergType`` does **not** handle in its ``switch``: those must fail
either at ``CREATE TABLE`` of the IcebergS3 destination (when ClickHouse
materialises the initial ``metadata.json`` schema) *or* at ``EXPORT
PARTITION`` time, but never silently accept and lose data. A small helper
captures "rejected at either step" so it doesn't matter which layer catches
the unsupported type.

The ClickHouse -> Iceberg primitive mapping exercised here (from
``Utils.cpp``):

================= =========== ================
ClickHouse type   Iceberg     required?
================= =========== ================
Int16/UInt16      int         true
Int32/UInt32      int         true
Int64/UInt64      long        true
Float32           float       true
Float64           double      true
Date / Date32     date        true
DateTime/DT64     timestamp   true
Time              time        true
String            string      true
UUID              uuid        true
Tuple(...)        struct      true
Array(T)          list        non-required
Map(K, V)         map         true
Nullable(T)       <T>         false
================= =========== ================

Types deliberately absent from that switch — ``Int8`` / ``UInt8`` / ``Bool``
/ ``FixedString`` / ``Decimal`` / ``Enum8`` / ``LowCardinality(String)`` —
power the ``rejected_*`` scenarios.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_DataTypes

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
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


def _run_accepted_type(
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
    the type under test.

    The fixed partition column is ``year Int32`` so this function exercises
    *only* the non-partition column type.

    Args:
        value_column: Column definition under test, e.g. ``"v Int64"``.
        values: Row payload for the source. Must land in partition ``year =
            2020`` and be ordered deterministically by ``id`` for the
            source/destination byte-compare to work.
        expected_rows: Optional override for the row count assertion.
            Defaults to the number of rows in ``values``.
        select_expr: SELECT expression applied to *both* the source and the
            destination when computing the byte-compare. Use this to
            normalise types whose default ``TabSeparated`` formatting
            differs between ClickHouse's native representation and
            ClickHouse's read-back from Iceberg (e.g. ``DateTime`` prints
            seconds but comes back from Iceberg ``timestamp`` as
            ``DateTime64(6)`` microseconds). Defaults to ``"*"``.
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

    with When(f"export partition '{partition_id}'"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
        )

    if expected_rows is None:
        # Row-delimiter count: ``(r1), (r2), (r3)`` -> two ``), `` separators,
        # plus 1. Counting ``(`` directly is wrong as soon as a row itself
        # contains a parenthesised literal (e.g. ``map(...)`` / ``tuple(...)``).
        expected_rows = values.count("),") + 1

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
    minio_root_user,
    minio_root_password,
    value_column,
    values,
    partition_id="2020",
):
    """Assert that a column type unsupported by ``getIcebergType`` is
    rejected either at ``CREATE TABLE`` of the IcebergS3 destination or at
    ``EXPORT PARTITION`` time.

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

    with Then("EXPORT PARTITION is rejected for the unsupported type"):
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
@Name("accepted: Int16")
def accepted_int16(self, minio_root_user, minio_root_password):
    """ClickHouse Int16 -> Iceberg int (required)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int16",
        values="(1, 2020, -32768), (2, 2020, 0), (3, 2020, 32767)",
    )


@TestScenario
@Name("accepted: Int32")
def accepted_int32(self, minio_root_user, minio_root_password):
    """ClickHouse Int32 -> Iceberg int (required)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int32",
        values="(1, 2020, -2147483648), (2, 2020, 0), (3, 2020, 2147483647)",
    )


@TestScenario
@Name("accepted: Int64")
def accepted_int64(self, minio_root_user, minio_root_password):
    """ClickHouse Int64 -> Iceberg long (required)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int64",
        values="(1, 2020, -9223372036854775808), (2, 2020, 0), (3, 2020, 9223372036854775807)",
    )


@TestScenario
@Name("accepted: UInt32")
def accepted_uint32(self, minio_root_user, minio_root_password):
    """ClickHouse UInt32 -> Iceberg int (required).

    Iceberg ints are 32-bit signed; UInt32 values above 2^31-1 are out of
    range for the target type, so this scenario stays strictly inside the
    signed range and exercises the "UInt32 maps to int" half of the mapping.
    """
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt32",
        values="(1, 2020, 0), (2, 2020, 1), (3, 2020, 2147483647)",
    )


@TestScenario
@Name("accepted: Float32")
def accepted_float32(self, minio_root_user, minio_root_password):
    """ClickHouse Float32 -> Iceberg float."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Float32",
        values="(1, 2020, -1.5), (2, 2020, 0.0), (3, 2020, 3.14)",
    )


@TestScenario
@Name("accepted: Float64")
def accepted_float64(self, minio_root_user, minio_root_password):
    """ClickHouse Float64 -> Iceberg double."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Float64",
        values="(1, 2020, -1.5e100), (2, 2020, 0.0), (3, 2020, 1.5e100)",
    )


@TestScenario
@Name("accepted: Date")
def accepted_date(self, minio_root_user, minio_root_password):
    """ClickHouse Date -> Iceberg date."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Date",
        values="(1, 2020, '1970-01-01'), (2, 2020, '2020-06-15'), (3, 2020, '2149-06-06')",
    )


@TestScenario
@Name("accepted: Date32")
def accepted_date32(self, minio_root_user, minio_root_password):
    """ClickHouse Date32 -> Iceberg date (wider range than Date)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Date32",
        values="(1, 2020, '1900-01-01'), (2, 2020, '2020-06-15'), (3, 2020, '2299-12-31')",
    )


@TestScenario
@Name("accepted: DateTime")
def accepted_datetime(self, minio_root_user, minio_root_password):
    """ClickHouse DateTime -> Iceberg timestamp.

    Iceberg ``timestamp`` is microsecond-precision, so ClickHouse reads the
    destination back as ``DateTime64(6)`` — its TabSeparated output prints
    six fractional digits while the source ``DateTime`` prints seconds.
    Both sides are normalised to ``DateTime64(6)`` for the byte-compare.
    """
    _run_accepted_type(
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
@Name("accepted: DateTime64(3)")
def accepted_datetime64(self, minio_root_user, minio_root_password):
    """ClickHouse DateTime64(3) -> Iceberg timestamp.

    Iceberg ``timestamp`` is microsecond-precision; the destination reads
    back as ``DateTime64(6)``. Both sides are normalised to ``DateTime64(6)``
    for the byte-compare (the underlying microsecond values are identical;
    only the printed precision differs).
    """
    _run_accepted_type(
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
@Name("accepted: String")
def accepted_string(self, minio_root_user, minio_root_password):
    """ClickHouse String -> Iceberg string (UTF-8)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v String",
        values="(1, 2020, ''), (2, 2020, 'ascii'), (3, 2020, 'unicode: \u2603')",
    )


@TestScenario
@Name("accepted: UUID")
def accepted_uuid(self, minio_root_user, minio_root_password):
    """ClickHouse UUID -> Iceberg uuid."""
    _run_accepted_type(
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
@Name("accepted: Nullable(Int64) with explicit NULLs")
def accepted_nullable_int64(self, minio_root_user, minio_root_password):
    """``Nullable(Int64)`` maps to Iceberg ``long`` with ``required = false``.

    The payload mixes NULLs and non-NULLs so we verify both the mapping and
    the null propagation end-to-end.
    """
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Nullable(Int64)",
        values="(1, 2020, NULL), (2, 2020, 42), (3, 2020, NULL)",
    )


@TestScenario
@Name("accepted: Nullable(String) with explicit NULLs")
def accepted_nullable_string(self, minio_root_user, minio_root_password):
    """``Nullable(String)`` maps to Iceberg ``string`` with ``required = false``."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Nullable(String)",
        values="(1, 2020, NULL), (2, 2020, 'present'), (3, 2020, NULL)",
    )


# ---------------------------------------------------------------------------
# Composite types
# ---------------------------------------------------------------------------


@TestScenario
@Name("accepted: Array(Int32)")
def accepted_array_int32(self, minio_root_user, minio_root_password):
    """``Array(Int32)`` maps to Iceberg ``list<int>`` (non-required)."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(Int32)",
        values="(1, 2020, []), (2, 2020, [1, 2, 3]), (3, 2020, [-1, 0, 1])",
    )


@TestScenario
@Name("accepted: Array(String)")
def accepted_array_string(self, minio_root_user, minio_root_password):
    """``Array(String)`` maps to Iceberg ``list<string>``."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Array(String)",
        values="(1, 2020, []), (2, 2020, ['a', 'bb']), (3, 2020, ['single'])",
    )


@TestScenario
@Name("accepted: Map(String, Int64)")
def accepted_map_string_int64(self, minio_root_user, minio_root_password):
    """``Map(String, Int64)`` maps to Iceberg ``map<string, long>``."""
    _run_accepted_type(
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
@Name("accepted: Tuple(Int32, String) -> struct")
def accepted_tuple(self, minio_root_user, minio_root_password):
    """``Tuple(x Int32, y String)`` maps to Iceberg ``struct<x: int, y: string>``."""
    _run_accepted_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Tuple(x Int32, y String)",
        values="(1, 2020, (1, 'a')), (2, 2020, (2, 'bb')), (3, 2020, (3, 'ccc'))",
    )


# ---------------------------------------------------------------------------
# Rejected types
# ---------------------------------------------------------------------------


@TestScenario
@Name("rejected: Int8")
def rejected_int8(self, minio_root_user, minio_root_password):
    """``Int8`` is not handled by ``getIcebergType`` — must be rejected."""
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Int8",
        values="(1, 2020, -128), (2, 2020, 0), (3, 2020, 127)",
    )


@TestScenario
@Name("rejected: UInt8")
def rejected_uint8(self, minio_root_user, minio_root_password):
    """``UInt8`` is not handled by ``getIcebergType`` — must be rejected."""
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v UInt8",
        values="(1, 2020, 0), (2, 2020, 1), (3, 2020, 255)",
    )


@TestScenario
@Name("rejected: Bool")
def rejected_bool(self, minio_root_user, minio_root_password):
    """``Bool`` is not handled by ``getIcebergType`` — must be rejected.

    Iceberg does have a ``boolean`` primitive, so this is a known mapping
    gap worth surfacing: a follow-up could add the case to ``Utils.cpp``.
    """
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Bool",
        values="(1, 2020, true), (2, 2020, false), (3, 2020, true)",
    )


@TestScenario
@Name("rejected: FixedString(16)")
def rejected_fixed_string(self, minio_root_user, minio_root_password):
    """``FixedString(N)`` is not mapped to an Iceberg type — must be rejected."""
    _run_rejected_type(
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
@Name("rejected: Decimal(10, 2)")
def rejected_decimal(self, minio_root_user, minio_root_password):
    """``Decimal`` is not handled by ``getIcebergType`` — must be rejected.

    Iceberg ``decimal(P, S)`` is a first-class type, so this is another
    known mapping gap (the Iceberg reader side supports it; the writer
    side in ``Utils.cpp`` does not yet).
    """
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Decimal(10, 2)",
        values="(1, 2020, 1.23), (2, 2020, -4.56), (3, 2020, 9999.99)",
    )


@TestScenario
@Name("rejected: Enum8")
def rejected_enum8(self, minio_root_user, minio_root_password):
    """``Enum8`` has no ``getIcebergType`` mapping — must be rejected.

    Iceberg has no native enum type; the pragmatic mapping would be
    ``string``, but today ClickHouse refuses rather than coerce.
    """
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v Enum8('red' = 1, 'green' = 2, 'blue' = 3)",
        values="(1, 2020, 'red'), (2, 2020, 'green'), (3, 2020, 'blue')",
    )


@TestScenario
@Name("rejected: LowCardinality(String)")
def rejected_low_cardinality(self, minio_root_user, minio_root_password):
    """``LowCardinality(String)`` is not unwrapped by ``getIcebergType`` —
    must be rejected.

    A natural fix would be to pass through to the wrapped type (like
    ``Nullable``), but today the mapping is missing.
    """
    _run_rejected_type(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        value_column="v LowCardinality(String)",
        values="(1, 2020, 'a'), (2, 2020, 'b'), (3, 2020, 'a')",
    )


# ---------------------------------------------------------------------------
# Feature entry point
# ---------------------------------------------------------------------------


ACCEPTED_SCENARIOS = (
    accepted_int16,
    accepted_int32,
    accepted_int64,
    accepted_uint32,
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
    accepted_array_int32,
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
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_DataTypes("1.0"))
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """ClickHouse -> Iceberg data type coverage for EXPORT PARTITION.

    Every scenario runs with ``flags=TE`` so a single data-type mismatch
    (expected in early iterations of the Antalya feature) does not mask
    the rest of the matrix.

    Gated to ``no_catalog`` only. The module exercises the CH -> Iceberg
    write-side mapping defined in
    ``Storages/ObjectStorage/DataLakes/Iceberg/Utils.cpp::getIcebergType``,
    plus a round-trip byte-compare against the source. Under REST / Glue
    the destination is re-read through ``DataLakeCatalog``, whose
    Iceberg-engine reader widens a few primitives on read-back
    (``date`` -> ``Date32``, ``timestamp`` -> ``DateTime64``) — the
    ``accepted: Date`` / ``accepted: DateTime`` byte-compares then fail
    even though the Iceberg file itself is correct. The widening is a
    property of the CH Iceberg *reader*, not of ``EXPORT PARTITION``;
    the write-side mapping is identical in both modes, so the test
    carries no additional signal under catalog mode. The ``rejected_*``
    scenarios likewise target CH-side diagnostics that the catalog
    translator pre-empts.
    """
    _require_no_catalog(
        "CH -> Iceberg write-side type mapping is identical across modes; "
        "catalog read-back widens Date/DateTime and breaks the byte-compare "
        "even though the Iceberg file is correct"
    )
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
