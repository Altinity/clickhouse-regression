"""Iceberg partition-key compatibility gate (Altinity/ClickHouse#2074).

Note on data-type widening on read-back: Iceberg's ``timestamp`` type
is microsecond-precision. ``DateTime`` and ``DateTime64(N<6)`` written
by ClickHouse are read back as ``DateTime64(6)``, so byte-compares of
``SELECT * ... FORMAT TabSeparated`` between source and destination
would spuriously differ on the trailing ``.000000``. The
:func:`_iceberg_readback_compare_columns` helper normalises the source
side to the Iceberg readback type before the compare, mirroring the
same pattern used in :mod:`iceberg.tests.export_partition.datatypes`
(``select_expr="id, year, toDateTime64(v, 6) AS v"``).

Extends ``partition_compatibility.py`` (same-transform structural match)
with the PR #2074 behaviour: the gate no longer requires source and
destination ``PARTITION BY`` to be byte-identical. It accepts when
either the per-column structural fast path proves the pairing is safe
(matching transform + arg + column type), or the dynamic single-value
proof over the exported partition's ``[min, max]`` shows every source
row lands in exactly one destination bucket (monotonic transforms
only; ``bucket[N]`` is always rejected on the dynamic path;
``Nullable`` is always rejected on the dynamic path).

Blueprint: ``iceberg_partition_key_compatibility_test_plan.md``.
"""

import re

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms,
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection,
)
from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    first_partition_id,
    insert_data,
    require_replicated_source,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    count_partition_export_rows,
    get_exception_count,
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    _require_no_catalog,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_data_files,
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_source_and_destination_match,
    count_rows_in_destination,
)

BAD_ARGUMENTS = 36
_LOSSY_CAST_OPT_IN = ("export_merge_tree_part_allow_lossy_cast", 1)


def _minio_credentials():
    """Return ``(user, password)`` stashed on the feature context."""
    ctx = current().context
    return ctx.minio_root_user, ctx.minio_root_password


def _parse_columns_ddl(columns_ddl):
    """Parse ``"name1 Type1, name2 Type2, ..."`` into ``[(name, type), ...]``,
    respecting nested parentheses in types like ``Nullable(Int32)`` and
    ``DateTime64(6, 'UTC')``."""
    result = []
    depth = 0
    current = []
    for ch in columns_ddl:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            spec = "".join(current).strip()
            name, _, ch_type = spec.partition(" ")
            result.append((name.strip(), ch_type.strip()))
            current = []
        else:
            current.append(ch)
    if current:
        spec = "".join(current).strip()
        name, _, ch_type = spec.partition(" ")
        result.append((name.strip(), ch_type.strip()))
    return result


def _iceberg_readback_cast_expr(name, ch_type):
    """Return the expression to use in a compare-SELECT so ``name``
    matches what Iceberg returns on read-back.

    Iceberg ``timestamp`` is microsecond-precision: ``DateTime`` and
    ``DateTime64(N<6)`` widen to ``DateTime64(6)`` (preserving TZ arg
    when present). Nullable wraps are peeled and re-applied via the
    function's own automatic Nullable propagation. Every other type is
    assumed to round-trip verbatim, so ``name`` is returned bare.
    """
    m = re.match(r"^Nullable\((.+)\)$", ch_type)
    inner = m.group(1) if m else ch_type

    if inner == "DateTime":
        return f"toDateTime64({name}, 6) AS {name}"
    m = re.match(r"^DateTime\(('[^']*')\)$", inner)
    if m:
        return f"toDateTime64({name}, 6, {m.group(1)}) AS {name}"
    m = re.match(r"^DateTime64\((\d+)(?:,\s*('[^']*'))?\)$", inner)
    if m:
        precision, tz = int(m.group(1)), m.group(2)
        if precision < 6:
            if tz:
                return f"toDateTime64({name}, 6, {tz}) AS {name}"
            return f"toDateTime64({name}, 6) AS {name}"
    return name


def _iceberg_readback_compare_columns(columns_ddl):
    """Build a SELECT expression that normalises source rows to the
    Iceberg readback type, so ``FORMAT TabSeparated`` byte-compares
    between source and destination cleanly."""
    return ", ".join(
        _iceberg_readback_cast_expr(name, ch_type)
        for name, ch_type in _parse_columns_ddl(columns_ddl)
    )


def _run_accept(
    columns,
    source_partition_by,
    dest_partition_by,
    values,
    dest_columns=None,
    dest_extra_settings=None,
    export_extra_settings=None,
    verify_row_equality=True,
    manifest_expected=None,
    order_by="tuple()",
    compare_columns="*",
):
    """End-to-end accept: create source and destination, export the
    first partition, wait for ``COMPLETED``, then round-trip source
    rows against the destination.

    ``dest_columns`` overrides the destination column DDL when the
    Nullability, type or column list must differ from the source.

    ``dest_extra_settings`` and ``export_extra_settings`` are forwarded
    to the Iceberg destination ``SETTINGS`` clause and to the
    ``EXPORT PARTITION`` query settings respectively.

    When ``manifest_expected`` is set, additionally asserts that each
    Iceberg partition-spec field's manifest value equals the given
    ClickHouse expression evaluated over the source rows.
    """
    minio_root_user, minio_root_password = _minio_credentials()
    source_table = f"mt_{getuid()}"
    dest_columns = dest_columns if dest_columns is not None else columns

    with Given("create source ReplicatedMergeTree with the partition key"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=source_partition_by,
        )

    with And("insert seed rows so the partition exists"):
        insert_data(table_name=source_table, values=values)

    with And("look up the partition id that was produced"):
        partition_id = first_partition_id(table_name=source_table)

    with And("create Iceberg destination with the paired partition spec"):
        destination = create_iceberg_destination(
            columns=dest_columns,
            partition_by=dest_partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            extra_settings=dest_extra_settings,
        )

    with Then("EXPORT PARTITION completes without error"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
            extra_settings=export_extra_settings,
        )

    if verify_row_equality:
        effective_compare_columns = (
            _iceberg_readback_compare_columns(dest_columns)
            if compare_columns == "*"
            else compare_columns
        )
        with And("source and destination rows match after the export"):
            assert_source_and_destination_match(
                source_table=source_table,
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                order_by=order_by,
                columns=effective_compare_columns,
            )

    if manifest_expected is not None:
        with And("manifest partition tuple equals dest transform on data"):
            _assert_manifest_partition_values(
                destination=destination,
                source_table=source_table,
                expected_expressions=manifest_expected,
            )


def _run_reject(
    columns,
    source_partition_by,
    dest_partition_by,
    values,
    dest_columns=None,
    expect_substrings=("BAD_ARGUMENTS",),
    dest_extra_settings=None,
    export_extra_settings=None,
):
    """End-to-end reject: same shape as :func:`_run_accept` but expects
    the synchronous compatibility gate to reject with exit code 36 and
    every substring in ``expect_substrings`` present in the server
    error output. Also asserts nothing was scheduled in the export
    status system table (the reject is synchronous, not just a
    background failure)."""
    minio_root_user, minio_root_password = _minio_credentials()
    source_table = f"mt_{getuid()}"
    dest_columns = dest_columns if dest_columns is not None else columns

    with Given("create source ReplicatedMergeTree with the partition key"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=source_partition_by,
        )

    with And("insert seed rows so the partition exists"):
        insert_data(table_name=source_table, values=values)

    with And("look up the partition id that was produced"):
        partition_id = first_partition_id(table_name=source_table)

    with And("create Iceberg destination with the incompatible partition spec"):
        destination = create_iceberg_destination(
            columns=dest_columns,
            partition_by=dest_partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            extra_settings=dest_extra_settings,
        )

    with Then("EXPORT PARTITION is rejected synchronously"):
        result = export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
            exitcode=BAD_ARGUMENTS,
            message=expect_substrings[0],
            wait_for_completion=False,
            extra_settings=export_extra_settings,
        )

    with And("every expected substring appears in the reject output"):
        for substring in expect_substrings:
            assert substring in result.output, error(
                f"expected {substring!r} in reject output, got: {result.output}"
            )

    with And("no rows were scheduled in the export status system table"):
        scheduled = count_partition_export_rows(
            source_table=source_table,
            partition_id=partition_id,
            destination=destination,
        )
        assert scheduled == 0, error(
            f"expected 0 scheduled export rows for a synchronous reject, "
            f"got {scheduled}"
        )


def _assert_manifest_partition_values(
    destination,
    source_table,
    expected_expressions,
    partition_where=None,
):
    """Cross-check the Iceberg manifest partition tuple against
    destination-transform values re-computed on the source.

    ``expected_expressions`` is a list of ClickHouse SQL expressions,
    one per position in the destination partition spec. For each
    expression the DISTINCT set of values on the source is compared to
    the DISTINCT set of ``data_file.partition[i]`` values across every
    data file in the current snapshot. Catches manifest-stamping bugs
    where row data is correct but the partition tuple is wrong (e.g.
    commit reads a stale part's ``min``).
    """
    minio_root_user, minio_root_password = _minio_credentials()
    node = current().context.node

    with By("loading the Iceberg destination via pyiceberg"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        spec = table.spec()
        spec_field_count = len(spec.fields)

    assert spec_field_count == len(expected_expressions), error(
        f"expected_expressions has {len(expected_expressions)} entries "
        f"but destination partition spec has {spec_field_count} fields"
    )

    with And("collecting partition tuples from every manifest entry"):
        data_files = get_data_files(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert data_files, error(
            "no data files in current snapshot — nothing to verify"
        )

        manifest_values_per_field = [set() for _ in range(spec_field_count)]
        for data_file in data_files:
            part_rec = data_file.partition
            for i in range(spec_field_count):
                manifest_values_per_field[i].add(part_rec[i])

    for i, expr in enumerate(expected_expressions):
        with And(f"comparing manifest field {i} against '{expr}'"):
            where_clause = f" WHERE {partition_where}" if partition_where else ""
            expected_output = node.query(
                f"SELECT DISTINCT {expr} FROM {source_table}{where_clause}"
            ).output
            expected_set = {
                _coerce_manifest_value(row.strip())
                for row in expected_output.splitlines()
                if row.strip()
            }
            actual_set = {
                _coerce_manifest_value(v) for v in manifest_values_per_field[i]
            }
            assert actual_set == expected_set, error(
                f"manifest partition field {i} mismatch: expected "
                f"{expected_set!r}, got {actual_set!r} "
                f"(source expression: {expr!r})"
            )


def _coerce_manifest_value(value):
    """Normalise ``int``/``str``/``bytes`` to a canonical string form so
    the set comparison in :func:`_assert_manifest_partition_values` is
    apples-to-apples between pyiceberg's typed returns and
    ``clickhouse-client``'s text output."""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return value.hex()
    if isinstance(value, str):
        return value
    return str(value)


def _enable_failpoint(name, node):
    """Enable a ClickHouse ONCE failpoint."""
    node.query(f"SYSTEM ENABLE FAILPOINT {name}")


def _disable_failpoint(name, node):
    """Best-effort ``SYSTEM DISABLE FAILPOINT`` for ``Finally`` blocks."""
    node.query(f"SYSTEM DISABLE FAILPOINT {name}")


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_dynamic_todate_to_day(self):
    """``toDate`` source partition rows on one day: ``day`` on the
    destination is single-valued over ``[min, max]`` — dynamic proof
    accepts."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toDate(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 18:30:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_dynamic_toyyyymm_to_month(self):
    """``toYYYYMM`` source partition stays inside one calendar month —
    ``month`` on the destination is constant across ``[min, max]``."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        dest_partition_by="toMonthNumSinceEpoch(event_time)",
        values="(1, '2024-03-05 00:00:00'), (2, '2024-03-25 12:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_dynamic_startofhour_to_hour(self):
    """Source partition anchored to one hour — ``hour`` destination is
    trivially constant across ``[min, max]``."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toStartOfHour(event_time)",
        dest_partition_by="toRelativeHourNum(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 08:59:59')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_dynamic_compound_finer_to_day(self):
    """Compound source ``(day, country)`` -> destination ``day``: the
    per-column subset check accepts because destination columns are a
    subset of source columns."""
    _run_accept(
        columns="id Int64, event_time DateTime, country String",
        source_partition_by="(toDate(event_time), country)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 08:00:00', 'US'), (2, '2024-03-20 18:30:00', 'US')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_structural_reversed_column_order(self):
    """Per-column structural fast path is order-independent: matching
    is by column name, the destination tuple order is what the manifest
    stamps."""
    _run_accept(
        columns="id Int64, year Int32, region String",
        source_partition_by="(year, region)",
        dest_partition_by="(region, year)",
        values="(1, 2020, 'EU')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_structural_destination_key_is_subset(self):
    """Destination key is a strict subset of the source key on the same
    column — dropped column is guaranteed constant across the source
    partition already, per-column fast path accepts."""
    _run_accept(
        columns="id Int64, year Int32, region String",
        source_partition_by="(year, region)",
        dest_partition_by="year",
        values="(1, 2020, 'EU')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_coarser_source_spans_days(self):
    """Month-granular source partition holding rows on several days
    forces destination ``day`` to yield different values — dynamic
    proof rejects on ``event_time`` split."""
    _run_reject(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-05 00:00:00'), (2, '2024-03-25 12:00:00')",
        expect_substrings=("BAD_ARGUMENTS", "event_time"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_bucket_requires_structural_match(self):
    """``bucket[N]`` is a non-monotonic hash: even when every source
    row hashes to the same bucket, only the structural fast path can
    prove bucket safety — dynamic proof always rejects."""
    _run_reject(
        columns="id Int64, k Int64",
        source_partition_by="k",
        dest_partition_by="icebergBucket(8, k)",
        values="(1, 42), (2, 42)",
        expect_substrings=("BAD_ARGUMENTS", "k"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_startofmonth_to_month(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toStartOfMonth(event_time)",
        dest_partition_by="toMonthNumSinceEpoch(event_time)",
        values="(1, '2024-03-05 00:00:00'), (2, '2024-03-25 12:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_yyyymmdd_to_day(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMMDD(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 00:00:00'), (2, '2024-03-20 23:59:59')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_startofday_to_day(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toStartOfDay(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 00:00:00'), (2, '2024-03-20 23:59:59')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_toyear_to_year(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-01-15 00:00:00'), (2, '2024-11-30 12:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_startofyear_to_year(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toStartOfYear(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-01-15 00:00:00'), (2, '2024-11-30 12:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_day_to_month(self):
    """Finer source (day) folds trivially into coarser destination
    (month) via dynamic proof."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toDate(event_time)",
        dest_partition_by="toMonthNumSinceEpoch(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 22:30:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_day_to_year(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toDate(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 22:30:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_hour_to_day(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toStartOfHour(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 08:59:59')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_month_to_year(self):
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYYYYMM(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-03-05 00:00:00'), (2, '2024-03-25 12:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_year_to_day_single_day_dynamic(self):
    """Structural check would reject (year partition can span 365
    days), but this specific partition happens to hold rows on a
    single day — dynamic proof accepts."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 22:30:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_year_source_spans_months(self):
    """Year source partition with rows in different months: destination
    ``month`` splits — reject."""
    _run_reject(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        dest_partition_by="toMonthNumSinceEpoch(event_time)",
        values="(1, '2024-03-15 00:00:00'), (2, '2024-08-01 00:00:00')",
        expect_substrings=("BAD_ARGUMENTS", "event_time"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_year_source_spans_days(self):
    _run_reject(
        columns="id Int64, event_time DateTime",
        source_partition_by="toYear(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-15 00:00:00'), (2, '2024-03-16 00:00:00')",
        expect_substrings=("BAD_ARGUMENTS", "event_time"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_week_source_spans_days(self):
    """Week-of-Monday source partition with rows on two different
    weekdays: ``day`` splits — reject."""
    _run_reject(
        columns="id Int64, event_time DateTime",
        source_partition_by="toMonday(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-18 00:00:00'), (2, '2024-03-20 00:00:00')",
        expect_substrings=("BAD_ARGUMENTS", "event_time"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_wide_source_subset_destination(self):
    """Six-column table with a three-column source key ``(day, region,
    tenant)`` exports to a two-column destination key ``(day, region)``
    — the per-column structural fast path accepts every source
    partition."""
    _run_accept(
        columns=(
            "id Int64, event_time DateTime, region String, tenant Int32, "
            "v1 Float64, v2 String"
        ),
        source_partition_by="(toDate(event_time), region, tenant)",
        dest_partition_by="(toRelativeDayNum(event_time), region)",
        values=(
            "(1, '2024-03-20 08:00:00', 'EU', 7, 1.0, 'a'), "
            "(2, '2024-03-20 18:30:00', 'EU', 7, 2.0, 'b')"
        ),
        order_by="id",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_destination_column_not_in_source_key(self):
    """Destination adds ``region`` which is not in the source partition
    key — the gate cannot dynamically prove single-valuedness for a
    column it has no ``min/max`` guarantees on."""
    _run_reject(
        columns="id Int64, event_time DateTime, region String",
        source_partition_by="toDate(event_time)",
        dest_partition_by="(toRelativeDayNum(event_time), region)",
        values=(
            "(1, '2024-03-20 08:00:00', 'EU'), " "(2, '2024-03-20 18:30:00', 'US')"
        ),
        expect_substrings=("BAD_ARGUMENTS", "region"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_bucket_source_column_type_change(self):
    """``bucket[N]`` is structural-only — the source column type must
    equal the destination column type. Here the destination widens
    ``key`` from ``Int64`` to ``String`` (Iceberg's ``bucket`` transform
    requires a bare column reference in the spec, so the type change
    is expressed via the column DDL rather than a wrapping function).
    The Int64->String cast is not ``canBeSafelyCast`` either, which
    reinforces the reject even under the lossy-cast opt-in path."""
    _run_reject(
        columns="id Int64, key Int64",
        dest_columns="id Int64, key String",
        source_partition_by="icebergBucket(16, key)",
        dest_partition_by="icebergBucket(16, key)",
        values="(1, 42), (2, 42)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_truncate_source_column_type_change(self):
    """``truncate[N]`` on integers is a numeric floor; on strings it is
    a byte-wise prefix. Type change is expressed by widening the
    destination column from ``Int64`` to ``String`` (Iceberg's spec
    requires a bare column reference in the transform). Values ``120``
    / ``129`` fall in the same integer bucket but map to distinct
    3-char strings; the destination ``truncate[10]`` splits them.
    Int64->String is also a lossy cast without the opt-in."""
    _run_reject(
        columns="id Int64, key Int64",
        dest_columns="id Int64, key String",
        source_partition_by="icebergTruncate(10, key)",
        dest_partition_by="icebergTruncate(10, key)",
        values="(1, 120), (2, 129)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_timezone_mismatch_spans_dest_days(self):
    """Two rows on the same Tokyo day (2024-03-05) fall on two UTC days
    (2024-03-04 and 2024-03-05). Destination day-transform runs in UTC
    and yields two buckets — reject."""
    _run_reject(
        columns="id Int64, event_time DateTime('UTC')",
        source_partition_by="toRelativeDayNum(event_time, 'Asia/Tokyo')",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-04 16:00:00'), (2, '2024-03-05 10:00:00')",
        dest_extra_settings=["iceberg_partition_timezone = 'UTC'"],
        expect_substrings=("BAD_ARGUMENTS", "event_time"),
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_timezone_match_structural(self):
    """Matching effective TZ (UTC on both sides): structural fast path
    accepts without touching dynamic proof."""
    _run_accept(
        columns="id Int64, event_time DateTime('UTC')",
        source_partition_by="toRelativeDayNum(event_time, 'UTC')",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 00:00:00'), (2, '2024-03-20 22:00:00')",
        dest_extra_settings=["iceberg_partition_timezone = 'UTC'"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_timezone_mismatch_dynamic_proof_folds(self):
    """Source uses ``Asia/Tokyo`` TZ, destination is UTC. Structural
    fast path fails on the TZ mismatch — but both rows happen to land
    on the same UTC day and the same Tokyo day, so dynamic proof
    accepts."""
    _run_accept(
        columns="id Int64, event_time DateTime('UTC')",
        source_partition_by="toRelativeDayNum(event_time, 'Asia/Tokyo')",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 02:00:00'), (2, '2024-03-20 10:00:00')",
        dest_extra_settings=["iceberg_partition_timezone = 'UTC'"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_nullable_structural_non_null_rows(self):
    """Both sides identity-partition on the same ``Nullable(Int32)``
    column. Rows are non-null; structural fast path accepts."""
    _run_accept(
        columns="id Int64, year Nullable(Int32)",
        source_partition_by="year",
        dest_partition_by="year",
        values="(1, 2020), (2, 2020)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_nullable_structural_null_only_partition(self):
    """A source partition containing only ``NULL`` rows: structural
    match still applies because both sides agree the ``NULL`` bucket is
    its own destination partition."""
    _run_accept(
        columns="id Int64, year Nullable(Int32)",
        source_partition_by="year",
        dest_partition_by="year",
        values="(1, NULL), (2, NULL)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_nullability_change_source_to_destination(self):
    """Source column is ``Int32``, destination is ``Nullable(Int32)``.
    Nullability change requires an exact structural type match and
    dynamic proof always rejects Nullable destinations."""
    _run_reject(
        columns="id Int64, year Int32",
        dest_columns="id Int64, year Nullable(Int32)",
        source_partition_by="year",
        dest_partition_by="year",
        values="(1, 2020)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_nullable_column_dynamic_proof(self):
    """Source ``toYear`` (``UInt16``) vs destination ``toYearNumSinceEpoch``
    (``Int32`` epoch-relative). Neither transform family nor column
    type matches structurally; dynamic proof would fold ``[min, max]``
    but the column is ``Nullable`` — dynamic proof always rejects."""
    _run_reject(
        columns="id Int64, event_time Nullable(DateTime)",
        source_partition_by="toYear(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-03-20 00:00:00'), (2, '2024-06-20 00:00:00')",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_lossy_truncate_int64_to_int32_with_opt_in(self):
    """Source ``val`` is ``Int64``, destination is ``Int32``. Values
    fit in ``Int32`` (no wrap) and fold to the same
    ``truncate[1000000]`` bucket — dynamic proof accepts with the lossy
    opt-in."""
    _run_accept(
        columns="id Int64, val Int64",
        dest_columns="id Int64, val Int32",
        source_partition_by="icebergTruncate(10, val)",
        dest_partition_by="icebergTruncate(1000000, val)",
        values="(1, 100), (2, 109)",
        export_extra_settings=[_LOSSY_CAST_OPT_IN],
        order_by="id",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_lossy_uint64_to_int64_identity_with_opt_in(self):
    """``UInt64 -> Int64`` is widening on the value axis but the upper
    half of ``UInt64`` doesn't fit, so ``canBeSafelyCast`` still flags
    it as lossy. With the opt-in and identical rows the dynamic proof
    folds to one bucket."""
    _run_accept(
        columns="id Int64, retention UInt64",
        dest_columns="id Int64, retention Int64",
        source_partition_by="retention",
        dest_partition_by="retention",
        values="(1, 30), (2, 30), (3, 30)",
        export_extra_settings=[_LOSSY_CAST_OPT_IN],
        order_by="id",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_lossy_cast_wraps_within_partition_range(self):
    """Source ``val`` is ``Int64`` with values ``100`` and ``200`` that
    both fit in ``Int8``, but ``Int8`` wraps at ``128`` — the cast is
    non-monotonic across ``[100, 200]`` so the gate rejects even with
    the opt-in."""
    _run_reject(
        columns="id Int64, val Int64",
        dest_columns="id Int64, val Int8",
        source_partition_by="icebergTruncate(1000, val)",
        dest_partition_by="icebergTruncate(100, val)",
        values="(1, 100), (2, 200)",
        export_extra_settings=[_LOSSY_CAST_OPT_IN],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0")
)
def reject_lossy_cast_without_opt_in_setting(self):
    """Same setup as ``accept_lossy_truncate_int64_to_int32_with_opt_in``
    but without the ``export_merge_tree_part_allow_lossy_cast`` opt-in:
    proves the setting is a real gate, not a no-op."""
    _run_reject(
        columns="id Int64, val Int64",
        dest_columns="id Int64, val Int32",
        source_partition_by="icebergTruncate(10, val)",
        dest_partition_by="icebergTruncate(1000000, val)",
        values="(1, 100), (2, 109)",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def manifest_day_transform_matches_source_rows(self):
    """Iceberg ``day`` bucket value in the manifest must equal
    ``toRelativeDayNum(event_time)`` computed on the exported source
    rows."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toDate(event_time)",
        dest_partition_by="toRelativeDayNum(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 18:30:00')",
        manifest_expected=["toRelativeDayNum(event_time)"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def manifest_day_source_year_dest_matches_source_rows(self):
    """Coarser destination transform: manifest must store the *year*
    transform value, not the source's ``toDate`` value."""
    _run_accept(
        columns="id Int64, event_time DateTime",
        source_partition_by="toDate(event_time)",
        dest_partition_by="toYearNumSinceEpoch(event_time)",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 22:30:00')",
        manifest_expected=["toYearNumSinceEpoch(event_time)"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def manifest_month_transform_matches_source_rows(self):
    """Structural fast-path accept plus manifest verification: Iceberg
    ``month`` bucket must equal ``toMonthNumSinceEpoch`` on the
    exported rows."""
    _run_accept(
        columns="id Int64, event_date Date",
        source_partition_by="toMonthNumSinceEpoch(event_date)",
        dest_partition_by="toMonthNumSinceEpoch(event_date)",
        values="(1, '2024-03-05'), (2, '2024-03-25')",
        manifest_expected=["toMonthNumSinceEpoch(event_date)"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def manifest_identity_type_change_uint16_to_string(self):
    """Identity's type-relaxed fast path with a ``UInt16 -> String``
    cast on the destination: the manifest field must store the cast
    value (``'2024'`` as ``String``), not the source's raw
    ``UInt16``."""
    _run_accept(
        columns="id Int64, year UInt16",
        dest_columns="id Int64, year String",
        source_partition_by="year",
        dest_partition_by="year",
        values="(1, 2024), (2, 2024)",
        export_extra_settings=[_LOSSY_CAST_OPT_IN],
        manifest_expected=["toString(year)"],
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def manifest_multicolumn_identity_uint64_widening(self):
    """Two-field destination spec: both ``event_date`` (identity Date)
    and ``retention`` (identity ``Int64`` after ``UInt64`` widening)
    must appear in the manifest tuple with destination-cast values."""
    _run_accept(
        columns="id Int64, event_date Date, retention UInt64",
        dest_columns="id Int64, event_date Date, retention Int64",
        source_partition_by="(event_date, retention)",
        dest_partition_by="(event_date, retention)",
        values="(1, '2024-03-20', 30), (2, '2024-03-20', 30)",
        export_extra_settings=[_LOSSY_CAST_OPT_IN],
        manifest_expected=["event_date", "toInt64(retention)"],
        order_by="id",
    )


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def commit_uses_exported_parts_after_optimize_race(self):
    """Wedge the commit with ``export_partition_commit_always_throw``
    after data files are written, race an ``INSERT + OPTIMIZE`` that
    turns the exported part into ``Outdated``, then release the
    failpoint. The commit must stamp the manifest from the originally
    exported rows (2024-03-20 only), not the merged part's ``min``
    (2024-03-05).
    """
    require_replicated_source(
        "arms an EXPORT PARTITION failpoint and races an OPTIMIZE — "
        "plain MergeTree parts do not go through the "
        "getPartitionSourceBlockForIcebergCommit path that PR #2074 fixes"
    )
    node = self.context.node
    minio_root_user, minio_root_password = _minio_credentials()
    failpoint = "export_partition_commit_always_throw"
    partition_id = "202403"

    source_table = f"mt_{getuid()}"
    columns = "id Int64, event_date Date"

    with Given("create source ReplicatedMergeTree with toYYYYMM partitioning"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by="toYYYYMM(event_date)",
        )

    with And("insert 2 rows on 2024-03-20 (both in the 202403 partition)"):
        insert_data(
            table_name=source_table,
            values="(1, '2024-03-20'), (2, '2024-03-20')",
        )

    with And("create Iceberg destination partitioned by day"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by="toRelativeDayNum(event_date)",
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    try:
        with And(f"arm the {failpoint} failpoint on the source node"):
            _enable_failpoint(failpoint, node=node)

        with When("kick off EXPORT PARTITION ID '202403' without waiting"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
                wait_for_completion=False,
            )

        with And("wait for the commit to fail at least once under the failpoint"):
            for attempt in retries(timeout=120, delay=1):
                with attempt:
                    exception_count = get_exception_count(
                        source_table=source_table,
                        partition_id=partition_id,
                        destination=destination,
                    )
                    assert exception_count >= 1, error(
                        f"expected exception_count >= 1 while the failpoint "
                        f"is armed, got {exception_count}"
                    )

        with And("insert an earlier-day row into the same source partition"):
            insert_data(
                table_name=source_table,
                values="(3, '2024-03-05')",
            )

        with And("optimize the two parts into one spanning both days"):
            node.query(
                f"OPTIMIZE TABLE {source_table} PARTITION ID '{partition_id}' FINAL"
            )

        with And(f"disable {failpoint} so the commit can succeed"):
            _disable_failpoint(failpoint, node=node)

        with Then("EXPORT PARTITION eventually reaches COMPLETED"):
            wait_for_export_status(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
                expected_status="COMPLETED",
                timeout=180,
            )

        with And("destination contains exactly the 2 originally-exported rows"):
            row_count = count_rows_in_destination(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert row_count == 2, error(
                f"expected 2 rows (the originally exported 2024-03-20 pair), "
                f"got {row_count}"
            )

        with And(
            "manifest partition value stamps 2024-03-20, NOT the merged-part "
            "min (2024-03-05)"
        ):
            expected_day = int(
                node.query(
                    "SELECT toRelativeDayNum(toDate('2024-03-20'))"
                ).output.strip()
            )
            forbidden_day = int(
                node.query(
                    "SELECT toRelativeDayNum(toDate('2024-03-05'))"
                ).output.strip()
            )
            data_files = get_data_files(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert data_files, error("no data files in the current snapshot")
            for df in data_files:
                assert df.partition[0] == expected_day, error(
                    f"manifest partition value on {df.file_path} = "
                    f"{df.partition[0]}, expected {expected_day} "
                    f"(toRelativeDayNum('2024-03-20'))"
                )
                assert df.partition[0] != forbidden_day, error(
                    f"manifest partition value on {df.file_path} equals the "
                    f"forbidden merged-part min {forbidden_day} "
                    f"(toRelativeDayNum('2024-03-05')) — the commit read the "
                    f"stale min instead of the exported rows"
                )
    finally:
        with Finally(f"ensure {failpoint} is disabled"):
            try:
                _disable_failpoint(failpoint, node=node)
            except Exception:
                pass


@TestScenario
@Requirements(
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0")
)
def accept_destination_partition_transform_with_timezone_literal(self):
    """PR #2074 fixes a ``std::variant`` mis-access (``Bad get``) in
    ``Iceberg::getPartitionField`` when the destination ``PARTITION BY``
    holds a String literal (an explicit timezone). This scenario
    exercises the path end-to-end: CREATE TABLE must succeed, the
    export must accept, and the round-trip must be lossless."""
    _run_accept(
        columns="id Int64, event_time DateTime('UTC')",
        source_partition_by="toRelativeDayNum(event_time, 'UTC')",
        dest_partition_by="toRelativeDayNum(event_time, 'UTC')",
        values="(1, '2024-03-20 08:00:00'), (2, '2024-03-20 18:30:00')",
    )


@TestSuite
def equivalence_gate(self):
    """Dynamic single-value proof: source transform differs from
    destination but the exported partition is single-valued under the
    destination transform (or explicitly not, for reject cases)."""
    Scenario(run=accept_dynamic_todate_to_day)
    Scenario(run=accept_dynamic_toyyyymm_to_month)
    Scenario(run=accept_dynamic_startofhour_to_hour)
    Scenario(run=accept_dynamic_compound_finer_to_day)
    Scenario(run=accept_structural_reversed_column_order)
    Scenario(run=accept_structural_destination_key_is_subset)
    Scenario(run=reject_coarser_source_spans_days)
    Scenario(run=reject_bucket_requires_structural_match)


@TestSuite
def granularity_matrix(self):
    """Temporal ladder: finer source transforms into equal-or-coarser
    destination transforms accept; coarser-into-finer with actual
    span reject."""
    Scenario(run=accept_startofmonth_to_month)
    Scenario(run=accept_yyyymmdd_to_day)
    Scenario(run=accept_startofday_to_day)
    Scenario(run=accept_toyear_to_year)
    Scenario(run=accept_startofyear_to_year)
    Scenario(run=accept_day_to_month)
    Scenario(run=accept_day_to_year)
    Scenario(run=accept_hour_to_day)
    Scenario(run=accept_month_to_year)
    Scenario(run=accept_year_to_day_single_day_dynamic)
    Scenario(run=reject_year_source_spans_months)
    Scenario(run=reject_year_source_spans_days)
    Scenario(run=reject_week_source_spans_days)


@TestSuite
def multicolumn_subset(self):
    """Destination partition columns must be a subset of source
    columns; otherwise the gate rejects."""
    Scenario(run=accept_wide_source_subset_destination)
    Scenario(run=reject_destination_column_not_in_source_key)


@TestSuite
def bucket_transform(self):
    """Bucket structural correctness beyond the same-transform accept
    covered by ``partition_compatibility.py``."""
    Scenario(run=reject_bucket_source_column_type_change)


@TestSuite
def truncate_transform(self):
    """Truncate structural correctness beyond the same-transform accept
    covered by ``partition_compatibility.py``."""
    Scenario(run=reject_truncate_source_column_type_change)


@TestSuite
def timezone_semantics(self):
    """Timezone-sensitive transforms: match-TZ accepts structurally,
    mismatch rejects on split, mismatch with cooperative data accepts
    via dynamic proof."""
    Scenario(run=reject_timezone_mismatch_spans_dest_days)
    Scenario(run=accept_timezone_match_structural)
    Scenario(run=accept_timezone_mismatch_dynamic_proof_folds)


@TestSuite
def nullable_partition_columns(self):
    """Nullable partition columns are only reachable from Iceberg
    destinations (hive rejects them at CREATE TABLE). Rule: exact
    structural match accepts; dynamic proof always rejects."""
    Scenario(run=accept_nullable_structural_non_null_rows)
    Scenario(run=accept_nullable_structural_null_only_partition)
    Scenario(run=reject_nullability_change_source_to_destination)
    Scenario(run=reject_nullable_column_dynamic_proof)


@TestSuite
def lossy_cast(self):
    """Lossy cast dynamic accept requires the
    ``export_merge_tree_part_allow_lossy_cast`` opt-in and monotonicity
    over the exported ``[min, max]``."""
    Scenario(run=accept_lossy_truncate_int64_to_int32_with_opt_in)
    Scenario(run=accept_lossy_uint64_to_int64_identity_with_opt_in)
    Scenario(run=reject_lossy_cast_wraps_within_partition_range)
    Scenario(run=reject_lossy_cast_without_opt_in_setting)


@TestSuite
def manifest_metadata_verification(self):
    """For each accept, the Iceberg manifest partition tuple must
    equal the destination transform evaluated over the exported rows —
    not the source's own partition id, not the source transform's
    value on the min row."""
    Scenario(run=manifest_day_transform_matches_source_rows)
    Scenario(run=manifest_day_source_year_dest_matches_source_rows)
    Scenario(run=manifest_month_transform_matches_source_rows)
    Scenario(run=manifest_identity_type_change_uint16_to_string)
    Scenario(run=manifest_multicolumn_identity_uint64_widening)


@TestSuite
def commit_correctness(self):
    """Between "gate accepts" and "commit writes metadata", concurrent
    INSERT + OPTIMIZE must not corrupt the stamped partition value —
    the commit finds exported parts by name across Active + Outdated."""
    Scenario(run=commit_uses_exported_parts_after_optimize_race)


@TestSuite
def timezone_literal_ddl(self):
    """Regression guard for the ``Bad get`` crash when the destination
    ``PARTITION BY`` holds a String literal (an explicit timezone)."""
    Scenario(run=accept_destination_partition_transform_with_timezone_literal)


@TestFeature
@Name("partition key compatibility")
def feature(self, minio_root_user, minio_root_password):
    """PR #2074 partition-key compatibility gate on the Iceberg side.

    Restricted to ``no_catalog`` because catalog mode widens
    ``Date``/``DateTime`` on read-back and would mask the transform
    matrix this module targets."""
    _require_no_catalog(
        "partition-key compatibility is a CH-side surface; catalog mode "
        "widens Date/DateTime on read-back and makes the transform matrix "
        "trigger INCOMPATIBLE_COLUMNS even when the spec is correct"
    )

    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    Feature(run=equivalence_gate)
    Feature(run=granularity_matrix)
    Feature(run=multicolumn_subset)
    Feature(run=bucket_transform)
    Feature(run=truncate_transform)
    Feature(run=timezone_semantics)
    Feature(run=nullable_partition_columns)
    Feature(run=lossy_cast)
    Feature(run=manifest_metadata_verification)
    Feature(run=commit_correctness)
    Feature(run=timezone_literal_ddl)
