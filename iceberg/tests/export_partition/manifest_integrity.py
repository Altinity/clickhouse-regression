"""Iceberg metadata / manifest integrity after EXPORT PARTITION.

PyIceberg-based validators that independently verify the metadata
ClickHouse commits (snapshot list, summary, partition spec, column
stats, data-file paths, external-reader round-trip), catching
regressions that ClickHouse would not notice reading back its own files.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_ManifestIntegrity_SnapshotChain,
    RQ_Iceberg_ExportPartition_ManifestIntegrity_PartitionSpec,
    RQ_Iceberg_ExportPartition_ManifestIntegrity_ColumnStats,
    RQ_Iceberg_ExportPartition_ManifestIntegrity_PathLayout,
    RQ_Iceberg_ExportPartition_ManifestIntegrity_ExternalReader,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    count_rows,
    create_replicated_mergetree,
    first_partition_id,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_WAREHOUSE_BUCKET,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    assert_column_stats_present,
    assert_file_paths_under_prefix,
    assert_manifest_spec_matches_partition,
    assert_snapshot_advanced,
    assert_snapshot_row_count,
    assert_value_counts_sum_to,
    get_data_files,
    get_snapshots,
    load_pyiceberg_table,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

# Required for any scenario that walks the manifest list or fetches data
# files via PyIceberg: without absolute ``s3://`` URLs in the metadata
# (table ``location`` and ``data_file.file_path``), PyArrowFileIO treats
# the bucket-relative paths as local files and fails. Must be set on both
# CREATE TABLE and EXPORT PARTITION; ``storage_paths.py`` covers both
# modes deliberately.
FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_SnapshotChain("1.0"))
@Name("each export advances the snapshot list by one")
def snapshot_advances_per_export(self, minio_root_user, minio_root_password):
    """Two sequential exports of distinct partitions -> two snapshots."""
    source_table = f"mt_{getuid()}"

    with Given("create a source table with two partitions"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2021), (4, 2021)",
        )

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with When("export the first partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("exactly one snapshot exists"):
        snapshots_before = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots_before) == 1, error(
            f"Expected 1 snapshot after first export, got {len(snapshots_before)}"
        )

    with When("export the second partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
        )

    with Then("snapshot count advanced by one"):
        snapshots_after = get_snapshots(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert len(snapshots_after) == len(snapshots_before) + 1, error(
            f"Expected {len(snapshots_before) + 1} snapshots after second export, "
            f"got {len(snapshots_after)}"
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_SnapshotChain("1.0"))
@Name("snapshot summary total-records matches exported row count")
def snapshot_summary_records_match(self, minio_root_user, minio_root_password):
    """``summary['total-records']`` equals the number of rows exported."""
    source_table = f"mt_{getuid()}"
    values = "(1, 2020), (2, 2020), (3, 2020), (4, 2020), (5, 2020)"

    with Given("create source table with a single partition of 5 rows"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(table_name=source_table, values=values)

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("current snapshot summary reports 5 total-records"):
        assert_snapshot_advanced(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_snapshot_row_count(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected=5,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_PartitionSpec("1.0"))
@Name("partition spec references source columns")
def manifest_partition_spec_matches_source(
    self, minio_root_user, minio_root_password
):
    """The Iceberg partition spec's source columns match ``PARTITION BY``."""
    source_table = f"mt_{getuid()}"
    columns = "id Int64, year Int32, region String"
    partition_by = "(year, region)"

    with Given("create source table partitioned by (year, region)"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=columns,
            partition_by=partition_by,
        )
        insert_data(table_name=source_table, values="(1, 2023, 'EU')")

    with And("look up the partition id"):
        partition_id = first_partition_id(table_name=source_table)

    with And("create the Iceberg destination with matching spec"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id=partition_id,
        )

    with Then("partition spec source columns are exactly [year, region]"):
        assert_manifest_spec_matches_partition(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_source_columns=["year", "region"],
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_ColumnStats("1.0"))
@Name("data files have all required column stats")
def column_stats_are_populated(self, minio_root_user, minio_root_password):
    """Every data file has non-empty ``column_sizes`` /
    ``null_value_counts`` / ``lower_bounds`` / ``upper_bounds``.
    ``value_counts`` is covered separately (currently XFail).
    """
    source_table = f"mt_{getuid()}"

    with Given("create source table and insert a partition"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2020)",
        )

    with And("create the Iceberg destination with full paths in metadata"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the partition with full paths in metadata"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("every data file has all four statistic kinds populated"):
        assert_column_stats_present(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_ColumnStats("1.0"))
@Name("value_counts across data files sum to source row count")
def value_counts_sum_to_row_count(self, minio_root_user, minio_root_password):
    """Per-column ``value_counts`` summed across data files equal the
    exported row count. Currently XFail (``IcebergWrites.cpp`` leaves
    ``value_counts`` null); flips to pass once it's populated.
    """
    source_table = f"mt_{getuid()}"

    with Given("create source table and insert a partition of 7 rows"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(
            table_name=source_table,
            values=(
                "(1, 2020), (2, 2020), (3, 2020), (4, 2020), "
                "(5, 2020), (6, 2020), (7, 2020)"
            ),
        )

    with And("confirm the source really has 7 rows in partition 2020"):
        expected_rows = count_rows(table_name=source_table, where="year = 2020")
        assert expected_rows == 7, error()

    with And("create the Iceberg destination with full paths in metadata"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the partition with full paths in metadata"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("each column's value_counts sum to 7"):
        assert_value_counts_sum_to(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_total=expected_rows,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_PathLayout("1.0"))
@Name("data file paths live under the table prefix")
def data_file_paths_under_table_prefix(
    self, minio_root_user, minio_root_password
):
    """Every ``data_file.file_path`` starts with the table's storage
    location (absolute ``s3://`` URI per the Iceberg spec). Currently
    XFail: ``MultipleFileWriter::startNewFile`` writes
    ``path_in_storage`` instead of ``path_in_metadata``.
    """
    source_table = f"mt_{getuid()}"

    with Given("create source table and insert a partition"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020)")

    with And("create the Iceberg destination with full paths in metadata"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the partition with full paths in metadata"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with And("look up the Iceberg table location"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        expected_prefix = table.location()
        if not expected_prefix.endswith("/"):
            expected_prefix += "/"

    with Then(f"all data file paths begin with {expected_prefix}"):
        assert_file_paths_under_prefix(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_prefix=expected_prefix,
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_ManifestIntegrity_ExternalReader("1.0"))
@Name("external iceberg reader round-trips exported data")
def external_reader_round_trips_exported_data(
    self, minio_root_user, minio_root_password
):
    """PyIceberg (a non-ClickHouse reader) can scan the destination and
    materialise the exported rows.

    Currently XFail: EXPORT PARTITION writes Parquet without Iceberg
    field-ids and IcebergS3 tables do not set
    ``schema.name-mapping.default``, so strict readers (PyIceberg) cannot
    map physical columns to the table schema. On older builds that still
    write bucket-relative ``data_file.file_path`` URIs, the same scenario
    may instead fail at FileIO open with ``FileNotFoundError``.
    """
    source_table = f"mt_{getuid()}"
    expected_values = [(1, 2020), (2, 2020), (3, 2020)]
    values_sql = ", ".join(f"({id_}, {year})" for id_, year in expected_values)

    with Given("create source table and insert a known partition"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        insert_data(table_name=source_table, values=values_sql)

    with And("create the Iceberg destination with full paths in metadata"):
        # write_full_path_in_iceberg_metadata = 1 is required infrastructure:
        # without it the manifest-list pointer in metadata.json is also
        # bucket-relative and PyIceberg fails before we ever reach a
        # data_file.file_path. We want the failure to be about the data
        # files, not the manifest list.
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the partition with full paths in metadata"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with And("load the destination via PyIceberg (external reader)"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("PyIceberg can scan the table and materialise the rows"):
        try:
            arrow_table = table.scan().to_arrow()
        except ValueError as exc:
            msg = str(exc)
            if "field-ids" not in msg and "name-mapping.default" not in msg:
                raise
            assert False, error(
                "External reader (PyIceberg) could not map exported Parquet "
                "columns to the Iceberg table schema. EXPORT PARTITION writes "
                "Parquet without Iceberg field-ids, and IcebergS3 "
                "destinations do not set table property "
                "schema.name-mapping.default. Underlying error: "
                f"{type(exc).__name__}: {exc}"
            )
        except (FileNotFoundError, OSError) as exc:
            offending = [df.file_path for df in get_data_files(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )]
            assert False, error(
                f"External reader (PyIceberg) failed to open a data file "
                f"written by EXPORT PARTITION. This is the user-visible "
                f"effect of data_file.file_path being bucket-relative "
                f"instead of an absolute URI — FileIO dispatch falls back "
                f"to the local filesystem. Underlying error: "
                f"{type(exc).__name__}: {exc}. "
                f"data_file.file_path values in this snapshot: {offending!r}"
            )

    with And("scanned rows match the exported rows exactly"):
        rows = arrow_table.sort_by("id").to_pylist()
        observed = [(row["id"], row["year"]) for row in rows]
        assert observed == expected_values, error(
            f"PyIceberg scan returned the wrong rows. "
            f"Expected {expected_values!r}, got {observed!r}"
        )


SCENARIOS = (
    snapshot_advances_per_export,
    snapshot_summary_records_match,
    manifest_partition_spec_matches_source,
    column_stats_are_populated,
    value_counts_sum_to_row_count,
    data_file_paths_under_table_prefix,
    external_reader_round_trips_exported_data,
)


@TestFeature
@Name("manifest integrity")
def feature(self, minio_root_user, minio_root_password):
    """Iceberg manifest and metadata correctness after EXPORT PARTITION."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
