"""Partition expression / transform compatibility between MergeTree and Iceberg.

Each scenario asserts a single source/destination ``PARTITION BY``
pairing is either accepted or rejected with ``BAD_ARGUMENTS``, so the
support matrix is visible at a glance in the test tree.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms,
    RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    first_partition_id,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    _require_no_catalog,
    create_iceberg_destination,
)


BAD_ARGUMENTS = 36


def _run_accepted_case(
    minio_root_user,
    minio_root_password,
    columns,
    source_partition_by,
    dest_partition_by,
    values,
):
    """Run an end-to-end ``EXPORT PARTITION`` against a matching
    source/destination spec and expect success.
    """
    source_table = f"mt_{getuid()}"

    with Given("create source ReplicatedMergeTree with the partition key"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=source_partition_by,
        )

    with And("insert a seed row so the partition exists"):
        insert_data(table_name=source_table, values=values)

    with And("look up the partition id that was produced"):
        partition_id = first_partition_id(table_name=source_table)

    with And("create Iceberg destination with matching partition spec"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=dest_partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("EXPORT PARTITION completes without error"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
        )


def _run_rejected_case(
    minio_root_user,
    minio_root_password,
    columns,
    source_partition_by,
    dest_partition_by,
    values,
):
    """Run ``EXPORT PARTITION`` against a mismatched source/destination
    spec and expect synchronous ``BAD_ARGUMENTS`` rejection.
    """
    source_table = f"mt_{getuid()}"

    with Given("create source ReplicatedMergeTree with the partition key"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=source_partition_by,
        )

    with And("insert a seed row so the partition exists"):
        insert_data(table_name=source_table, values=values)

    with And("look up the partition id that was produced"):
        partition_id = first_partition_id(table_name=source_table)

    with And("create Iceberg destination with mismatched partition spec"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=dest_partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("EXPORT PARTITION is rejected with BAD_ARGUMENTS"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
            exitcode=BAD_ARGUMENTS,
            message="BAD_ARGUMENTS",
            wait_for_completion=False,
        )


# ---------------------------------------------------------------------------
# Accepted partition-spec pairings
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: compound identity (year, region)")
def accepted_compound_identity(self, minio_root_user, minio_root_password):
    """Two-column identity partitioning on mixed (Int, String) columns."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32, region String",
        source_partition_by="(year, region)",
        dest_partition_by="(year, region)",
        values="(1, 2023, 'EU')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: year transform (toYearNumSinceEpoch)")
def accepted_year_transform(self, minio_root_user, minio_root_password):
    """``toYearNumSinceEpoch(Date)`` maps to the Iceberg ``year`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_date Date",
        source_partition_by="toYearNumSinceEpoch(event_date)",
        dest_partition_by="toYearNumSinceEpoch(event_date)",
        values="(1, '2020-06-15')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: month transform (toMonthNumSinceEpoch)")
def accepted_month_transform(self, minio_root_user, minio_root_password):
    """``toMonthNumSinceEpoch(Date)`` maps to the Iceberg ``month`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_date Date",
        source_partition_by="toMonthNumSinceEpoch(event_date)",
        dest_partition_by="toMonthNumSinceEpoch(event_date)",
        values="(1, '2020-06-15')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: day transform (toRelativeDayNum)")
def accepted_day_transform(self, minio_root_user, minio_root_password):
    """``toRelativeDayNum(Date)`` maps to the Iceberg ``day`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_date Date",
        source_partition_by="toRelativeDayNum(event_date)",
        dest_partition_by="toRelativeDayNum(event_date)",
        values="(1, '2020-06-15')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: hour transform (toRelativeHourNum)")
def accepted_hour_transform(self, minio_root_user, minio_root_password):
    """``toRelativeHourNum(DateTime)`` maps to the Iceberg ``hour`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_ts DateTime",
        source_partition_by="toRelativeHourNum(event_ts)",
        dest_partition_by="toRelativeHourNum(event_ts)",
        values="(1, '2020-06-15 12:00:00')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: truncate[4] on String")
def accepted_truncate(self, minio_root_user, minio_root_password):
    """``icebergTruncate(N, String)`` maps to the Iceberg ``truncate[N]`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, category String",
        source_partition_by="icebergTruncate(4, category)",
        dest_partition_by="icebergTruncate(4, category)",
        values="(1, 'clickhouse')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: bucket[8] on Int64")
def accepted_bucket(self, minio_root_user, minio_root_password):
    """``icebergBucket(N, col)`` maps to the Iceberg ``bucket[N]`` transform."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, user_id Int64",
        source_partition_by="icebergBucket(8, user_id)",
        dest_partition_by="icebergBucket(8, user_id)",
        values="(1, 42)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_AcceptedTransforms("1.0"))
@Name("accepted: compound mixed (year + bucket[16])")
def accepted_compound_mixed(self, minio_root_user, minio_root_password):
    """Mixed compound key: ``(year-transform, bucket-transform)``."""
    _run_accepted_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_date Date, user_id Int64",
        source_partition_by="(toYearNumSinceEpoch(event_date), icebergBucket(16, user_id))",
        dest_partition_by="(toYearNumSinceEpoch(event_date), icebergBucket(16, user_id))",
        values="(1, '2021-03-01', 99)",
    )


# ---------------------------------------------------------------------------
# Rejected partition-spec pairings
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: compound field order reversed")
def rejected_reversed_order(self, minio_root_user, minio_root_password):
    """``(year, region)`` on the source vs ``(region, year)`` on the destination."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32, region String",
        source_partition_by="(year, region)",
        dest_partition_by="(region, year)",
        values="(1, 2020, 'EU')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: transform vs identity on same column")
def rejected_transform_vs_identity(self, minio_root_user, minio_root_password):
    """Year-transform on the source but plain identity on the destination."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, event_date Date",
        source_partition_by="toYearNumSinceEpoch(event_date)",
        dest_partition_by="event_date",
        values="(1, '2020-01-01')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: bucket width mismatch ([8] vs [16])")
def rejected_bucket_width_mismatch(self, minio_root_user, minio_root_password):
    """Same column, same transform family, different bucket width."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, user_id Int64",
        source_partition_by="icebergBucket(8, user_id)",
        dest_partition_by="icebergBucket(16, user_id)",
        values="(1, 42)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: truncate width mismatch ([4] vs [8])")
def rejected_truncate_width_mismatch(self, minio_root_user, minio_root_password):
    """Same column, same transform family, different truncate width."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, category String",
        source_partition_by="icebergTruncate(4, category)",
        dest_partition_by="icebergTruncate(8, category)",
        values="(1, 'clickhouse')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: field-count mismatch (2 vs 1)")
def rejected_field_count_mismatch(self, minio_root_user, minio_root_password):
    """Compound source vs single-column destination."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32, region String",
        source_partition_by="(year, region)",
        dest_partition_by="year",
        values="(1, 2020, 'EU')",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: unsupported MergeTree expression (intDiv)")
def rejected_unsupported_expression(self, minio_root_user, minio_root_password):
    """Valid MergeTree expressions that have no Iceberg-transform equivalent."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32",
        source_partition_by="intDiv(year, 100)",
        dest_partition_by="year",
        values="(1, 2020)",
    )


# ---------------------------------------------------------------------------
# Key-level mismatches (simple identity cases covered in isolation)
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: different partition columns (year vs id)")
def rejected_column_mismatch(self, minio_root_user, minio_root_password):
    """Source partitioned by one column, destination by another."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32",
        source_partition_by="year",
        dest_partition_by="id",
        values="(1, 2020)",
    )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_PartitionCompatibility_MismatchRejection("1.0"))
@Name("rejected: partitioned source, unpartitioned destination")
def rejected_unpartitioned_destination(self, minio_root_user, minio_root_password):
    """Source partitioned by ``year``; Iceberg table has no partition spec."""
    _run_rejected_case(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        columns="id Int64, year Int32",
        source_partition_by="year",
        dest_partition_by="",
        values="(1, 2020)",
    )


# ---------------------------------------------------------------------------
# Feature entry point
# ---------------------------------------------------------------------------


ACCEPTED_SCENARIOS = (
    accepted_compound_identity,
    accepted_year_transform,
    accepted_month_transform,
    accepted_day_transform,
    accepted_hour_transform,
    accepted_truncate,
    accepted_bucket,
    accepted_compound_mixed,
)

REJECTED_SCENARIOS = (
    rejected_reversed_order,
    rejected_transform_vs_identity,
    rejected_bucket_width_mismatch,
    rejected_truncate_width_mismatch,
    rejected_field_count_mismatch,
    rejected_unsupported_expression,
    rejected_column_mismatch,
    rejected_unpartitioned_destination,
)


@TestFeature
@Name("partition compatibility")
def feature(self, minio_root_user, minio_root_password):
    """Partition expression compatibility between MergeTree and Iceberg.
    ``no_catalog`` only — under Ice / Glue the catalog read-back widens
    ``Date`` / ``DateTime``, masking the matrix this module wants to
    cover.
    """
    _require_no_catalog(
        "partition expression compatibility is a CH-side surface; catalog mode "
        "widens Date/DateTime on read-back and makes the transform matrix "
        "trigger INCOMPATIBLE_COLUMNS even when the spec is correct"
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
