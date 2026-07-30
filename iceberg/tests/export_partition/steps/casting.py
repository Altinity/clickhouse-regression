"""Helpers for export casting parity tests (Altinity/ClickHouse PR 1779).

Each scenario compares ``EXPORT PARTITION`` against an ``INSERT INTO dest
SELECT * FROM source`` benchmark on twin Iceberg destinations with identical
casted schemas. Destinations are created through ClickHouse DDL
(:mod:`casting_iceberg_destination`); catalog modes use
``CREATE TABLE datalake.\\`namespace.table\\``` with Iceberg-compatible types.
"""

from dataclasses import dataclass

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, check_clickhouse_version

from iceberg.tests.export_partition.steps.common import (
    count_rows,
    create_replicated_mergetree,
    insert_data,
    resolve_first_partition_id,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.casting_iceberg_destination import (
    create_casting_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    assert_manifest_spec_matches_partition,
    assert_snapshot_row_count,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    select_from_destination,
)

BAD_ARGUMENTS = 36
INCOMPATIBLE_COLUMNS = 122
LOSSY_CAST_REJECTION_MESSAGE = "lossy cast"


def _lossy_cast_rejection_expectation(test):
    """Client exit code / message for lossy-cast rejection without the setting.

    Builds ``< 26.3.13.20001``: reject with ``BAD_ARGUMENTS`` (36) / ``lossy cast``.
    Builds ``>= 26.3.13.20001`` use ``INCOMPATIBLE_COLUMNS`` (122), matching
    ``schema_evolution.source_only_schema_drift_rejected``.
    """
    if check_clickhouse_version(">=26.3.13.20001")(test):
        return INCOMPATIBLE_COLUMNS, "INCOMPATIBLE_COLUMNS"
    return BAD_ARGUMENTS, LOSSY_CAST_REJECTION_MESSAGE


@dataclass(frozen=True)
class CastCase:
    """One source/destination column-type pair exercised positionally."""

    name: str
    source_columns: str
    dest_columns: str
    partition_by: str
    values: str
    partition_id: str = "2020"
    where_clause: str = "year = 2020"
    order_by: str = "id"
    allow_lossy_cast: bool = False
    expect_rejection: bool = False


# Integer boundaries for Iceberg-native signed destinations.
_INT32_MAX = 2147483647
_INT32_MIN = -2147483648
_INT64_MAX = 9223372036854775807
_UINT64_MAX = 18446744073709551615

# Mirrors ``canBeSafelyCast`` families whose destination DDL uses Iceberg-native
# types (signed int/long, float/double, string, date, nested list/map/struct).
# String targets cover the ``to_which_type.isString()`` escape hatch.
SAFE_CAST_CASES = (
    CastCase(
        name="Int32 widens to Int64",
        source_columns="id Int32, year Int32",
        dest_columns="id Int64, year Int64",
        partition_by="year",
        values="(1, 2020), (2, 2020)",
    ),
    CastCase(
        name="Float32 widens to Float64",
        source_columns="id Int64, year Int32, v Float32",
        dest_columns="id Int64, year Int32, v Float64",
        partition_by="year",
        values="(1, 2020, 1.5), (2, 2020, 2.5)",
        order_by="id",
    ),
    CastCase(
        name="Date casts to String",
        source_columns="id Int64, year Int32, d Date",
        dest_columns="id Int64, year Int32, d String",
        partition_by="year",
        values="(1, 2020, '2020-01-01'), (2, 2020, '2020-06-15')",
    ),
    CastCase(
        name="DateTime casts to String",
        source_columns="id Int64, year Int32, ts DateTime",
        dest_columns="id Int64, year Int32, ts String",
        partition_by="year",
        values="(1, 2020, '2020-01-01 00:00:00'), (2, 2020, '2020-06-15 12:00:00')",
    ),
    CastCase(
        name="UUID casts to String",
        source_columns="id Int64, year Int32, u UUID",
        dest_columns="id Int64, year Int32, u String",
        partition_by="year",
        values=(
            "(1, 2020, '550e8400-e29b-41d4-a716-446655440000'), "
            "(2, 2020, '6ba7b810-9dad-11d1-80b4-00c04fd430c8')"
        ),
    ),
    CastCase(
        name="Nullable(Int32) to Nullable(Int64)",
        source_columns="id Int64, year Int32, v Nullable(Int32)",
        dest_columns="id Int64, year Int32, v Nullable(Int64)",
        partition_by="year",
        values="(1, 2020, 10), (2, 2020, NULL)",
    ),
    CastCase(
        name="Array(Int32) to Array(Int64)",
        source_columns="id Int64, year Int32, tags Array(Int32)",
        dest_columns="id Int64, year Int32, tags Array(Int64)",
        partition_by="year",
        values="(1, 2020, [1, 2]), (2, 2020, [3])",
    ),
    CastCase(
        name="Map(String, Int32) to Map(String, Int64)",
        source_columns="id Int64, year Int32, props Map(String, Int32)",
        dest_columns="id Int64, year Int32, props Map(String, Int64)",
        partition_by="year",
        values="(1, 2020, map('a', 1)), (2, 2020, map('b', 2))",
    ),
    CastCase(
        name="Tuple(Int32, String) to Tuple(Int64, String)",
        source_columns="id Int64, year Int32, pair Tuple(Int32, String)",
        dest_columns="id Int64, year Int32, pair Tuple(Int64, String)",
        partition_by="year",
        values="(1, 2020, (1, 'a')), (2, 2020, (2, 'b'))",
    ),
)

LOSSY_CAST_CASES = (
    CastCase(
        name="UInt64 narrows to Int32 without allow_lossy_cast",
        source_columns="id UInt64, year UInt32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values="(4294967296, 2020)",
        expect_rejection=True,
    ),
    CastCase(
        name="UInt64 narrows to Int32 with allow_lossy_cast",
        source_columns="id UInt64, year UInt32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values="(4294967296, 2020)",
        allow_lossy_cast=True,
    ),
)

# Values outside the destination signed range must follow the same INSERT SELECT
# and EXPORT PARTITION lossy-cast rules (reject by default, truncate in lockstep
# when ``export_merge_tree_part_allow_lossy_cast = 1``).
OUT_OF_BOUNDS_CAST_CASES = (
    CastCase(
        name="Int64 above INT32_MAX rejected without allow_lossy_cast",
        source_columns="id Int64, year Int32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values=f"({_INT32_MAX + 1}, 2020)",
        expect_rejection=True,
    ),
    CastCase(
        name="Int64 above INT32_MAX with allow_lossy_cast",
        source_columns="id Int64, year Int32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values=f"({_INT32_MAX + 1}, 2020)",
        allow_lossy_cast=True,
    ),
    CastCase(
        name="Int64 below INT32_MIN rejected without allow_lossy_cast",
        source_columns="id Int64, year Int32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values=f"({_INT32_MIN - 1}, 2020)",
        expect_rejection=True,
    ),
    CastCase(
        name="Int64 below INT32_MIN with allow_lossy_cast",
        source_columns="id Int64, year Int32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values=f"({_INT32_MIN - 1}, 2020)",
        allow_lossy_cast=True,
    ),
    CastCase(
        name="UInt64 above INT64_MAX rejected without allow_lossy_cast",
        source_columns="id UInt64, year Int32",
        dest_columns="id Int64, year Int32",
        partition_by="year",
        values=f"({_INT64_MAX + 1}, 2020)",
        expect_rejection=True,
    ),
    CastCase(
        name="UInt64 above INT64_MAX with allow_lossy_cast",
        source_columns="id UInt64, year Int32",
        dest_columns="id Int64, year Int32",
        partition_by="year",
        values=f"({_INT64_MAX + 1}, 2020)",
        allow_lossy_cast=True,
    ),
    CastCase(
        name="UInt64 UINT64_MAX to Int64 with allow_lossy_cast",
        source_columns="id UInt64, year Int32",
        dest_columns="id Int64, year Int32",
        partition_by="year",
        values=f"({_UINT64_MAX}, 2020)",
        allow_lossy_cast=True,
    ),
    CastCase(
        name="Int64 boundary mix to Int32 with allow_lossy_cast",
        source_columns="id Int64, year Int32",
        dest_columns="id Int32, year Int32",
        partition_by="year",
        values=(
            f"(1, 2020), ({_INT32_MAX}, 2020), ({_INT32_MAX + 1}, 2020), "
            f"({_INT32_MIN}, 2020), ({_INT32_MIN - 1}, 2020)"
        ),
        allow_lossy_cast=True,
        order_by="id",
    ),
)


def _partition_source_columns(partition_by: str):
    """``year`` or ``(eventDate, retention)`` -> column name list."""
    stripped = partition_by.strip()
    if stripped.startswith("(") and stripped.endswith(")"):
        stripped = stripped[1:-1]
    return [part.strip() for part in stripped.split(",")]


@TestStep(When)
def insert_select_into_iceberg_destination(
    self,
    destination,
    select_query,
    node=None,
    settings=None,
    exitcode=0,
    message=None,
):
    """``INSERT INTO <iceberg> <select>`` — INSERT SELECT cast benchmark."""
    if node is None:
        node = self.context.node
    if settings is None:
        settings = [("allow_experimental_insert_into_iceberg", 1)]
    name = as_destination_name(destination)
    expect_failure = exitcode != 0 or message is not None
    node.query(
        f"INSERT INTO {name} {select_query}",
        settings=settings,
        exitcode=exitcode,
        message=message,
        ignore_exception=expect_failure,
    )


def _export_settings(allow_lossy_cast: bool):
    settings = []
    if allow_lossy_cast:
        settings.append(("export_merge_tree_part_allow_lossy_cast", 1))
    return settings


@TestStep(Then)
def assert_destinations_match(
    self,
    left_destination,
    right_destination,
    minio_root_user,
    minio_root_password,
    columns="*",
    where_clause=None,
    order_by="tuple()",
    node=None,
):
    """Byte-compare two Iceberg destinations after identical cast paths."""
    left = select_from_destination(
        destination=left_destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns=columns,
        where_clause=where_clause,
        order_by=order_by,
        node=node,
        format="TabSeparated",
    ).output.strip()
    right = select_from_destination(
        destination=right_destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns=columns,
        where_clause=where_clause,
        order_by=order_by,
        node=node,
        format="TabSeparated",
    ).output.strip()
    assert left == right, error(
        f"INSERT benchmark ({as_destination_name(left_destination)}) and "
        f"EXPORT result ({as_destination_name(right_destination)}) differ"
        + (f" WHERE {where_clause}" if where_clause else "")
        + f":\nINSERT:\n{left}\nEXPORT:\n{right}"
    )


@TestStep(When)
def run_cast_parity_case(
    self,
    case: CastCase,
    minio_root_user,
    minio_root_password,
    node=None,
):
    """INSERT SELECT benchmark vs EXPORT PARTITION on twin Iceberg tables."""
    if node is None:
        node = self.context.node

    source_table = f"cast_src_{getuid()}"
    create_replicated_mergetree(
        table_name=source_table,
        columns=case.source_columns,
        partition_by=case.partition_by,
        node=node,
    )
    insert_data(table_name=source_table, values=case.values)

    with Given("Iceberg destination for INSERT SELECT benchmark"):
        dest_insert = create_casting_iceberg_destination(
            columns=case.dest_columns,
            partition_by=case.partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with And("twin Iceberg destination for EXPORT PARTITION"):
        dest_export = create_casting_iceberg_destination(
            columns=case.dest_columns,
            partition_by=case.partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    export_settings = _export_settings(case.allow_lossy_cast)

    partition_id = (
        case.partition_id
        if case.partition_id != "2020"
        else resolve_first_partition_id(table_name=source_table, node=node)
    )

    if case.expect_rejection:
        rejection_exitcode, rejection_message = _lossy_cast_rejection_expectation(
            self
        )
        with When("EXPORT PARTITION is rejected for lossy cast without setting"):
            export_partition(
                source_table=source_table,
                destination=dest_export,
                partition_id=partition_id,
                settings=export_settings,
                exitcode=rejection_exitcode,
                message=rejection_message,
                wait_for_completion=False,
                node=node,
            )
        with And("INSERT SELECT still writes the lossily casted benchmark rows"):
            insert_select_into_iceberg_destination(
                destination=dest_insert,
                select_query=f"SELECT * FROM {source_table}",
                node=node,
            )
            expected_rows = count_rows(
                table_name=source_table,
                where=case.where_clause,
                node=node,
            )
            assert_destination_row_count(
                destination=dest_insert,
                expected=expected_rows,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                where_clause=case.where_clause,
                node=node,
            )
        return

    with When("INSERT INTO benchmark destination SELECT * FROM source"):
        insert_select_into_iceberg_destination(
            destination=dest_insert,
            select_query=f"SELECT * FROM {source_table}",
            node=node,
        )

    with And("EXPORT PARTITION into the twin destination"):
        export_partition(
            source_table=source_table,
            destination=dest_export,
            partition_id=partition_id,
            settings=export_settings,
            node=node,
        )

    expected_rows = count_rows(
        table_name=source_table,
        where=case.where_clause,
        node=node,
    )

    with Then("row counts match the seeded partition"):
        assert_destination_row_count(
            destination=dest_insert,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=case.where_clause,
            node=node,
        )
        assert_destination_row_count(
            destination=dest_export,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=case.where_clause,
            node=node,
        )

    with And("EXPORT matches the INSERT SELECT benchmark byte-for-byte"):
        assert_destinations_match(
            left_destination=dest_insert,
            right_destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=case.where_clause,
            order_by=case.order_by,
            node=node,
        )

    with And("committed snapshot metadata reflects the casted row count"):
        assert_snapshot_row_count(
            destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected=expected_rows,
        )
        assert_manifest_spec_matches_partition(
            destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_source_columns=_partition_source_columns(case.partition_by),
        )
