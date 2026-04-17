"""Iceberg metadata / manifest integrity after EXPORT PARTITION.

These scenarios drive the PyIceberg-based validators in
:mod:`steps.manifest_validation`. They independently verify the metadata
files ClickHouse commits, catching regressions that the ClickHouse reader
would not notice when reading back its own files.

Scenarios:

* :func:`snapshot_advances_per_export` - each successful export appends
  exactly one snapshot.
* :func:`snapshot_summary_records_match` - ``summary.total-records`` on the
  current snapshot matches the number of rows written.
* :func:`manifest_partition_spec_matches_source` - the table's partition
  spec references the same source columns (in order) that the source table
  was partitioned by.
* :func:`column_stats_are_populated` - every data file has populated
  ``value_counts``, ``null_value_counts``, ``lower_bounds`` and
  ``upper_bounds`` (without these, predicate push-down silently breaks).
* :func:`value_counts_sum_to_row_count` - per-column ``value_counts``
  summed across data files equal the source row count.
* :func:`data_file_paths_under_table_prefix` - every data file path lives
  under the expected IcebergS3 prefix.
"""

from testflows.core import *
from testflows.asserts import error

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
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    assert_column_stats_present,
    assert_file_paths_under_prefix,
    assert_manifest_spec_matches_partition,
    assert_snapshot_advanced,
    assert_snapshot_row_count,
    assert_value_counts_sum_to,
    get_snapshots,
    load_pyiceberg_table,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

# Scenarios that walk the manifest list / fetch data files via PyIceberg need
# ClickHouse to write absolute ``s3://`` URLs into the Iceberg metadata. The
# default is ``write_full_path_in_iceberg_metadata = 0`` which stores paths
# relative to the bucket; when PyIceberg's StaticTable (no-catalog mode) reads
# those, PyArrowFileIO treats them as local paths and fails.
#
# The setting is consulted at TWO separate queries:
#
# 1. ``CREATE TABLE ... ENGINE = IcebergS3(...)`` - decides what goes into the
#    ``location`` field of the initial ``metadata.json``.
#    (see ClickHouse: IcebergMetadata.cpp, ``location_path`` branch).
# 2. ``ALTER TABLE ... EXPORT PARTITION`` - reads ``location`` from metadata
#    and uses it as the prefix for every path it writes (manifest list,
#    manifest entries, data files).
#    (see ClickHouse: IcebergWrites.cpp, ``FileNamesGenerator`` branch).
#
# Both need the setting enabled; enabling only the second leaves ``location``
# unset to ``s3://...`` and everything still resolves against a local path.
# Scenarios that only read fields from ``metadata.json`` (snapshot list,
# summary, spec) work without this override. ``storage_paths.py`` is where
# both modes are exercised deliberately.
FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


@TestScenario
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
    dest_name = as_destination_name(destination)

    with When("export the first partition"):
        export_partition(
            source_table=source_table,
            destination_table=dest_name,
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
            destination_table=dest_name,
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
            destination_table=as_destination_name(destination),
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
            destination_table=as_destination_name(destination),
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
@Name("data files have all required column stats")
def column_stats_are_populated(self, minio_root_user, minio_root_password):
    """Each data file has non-empty column_sizes / null_value_counts / bounds.

    ``value_counts`` is covered by a separate (currently XFail) scenario —
    the current ClickHouse EXPORT PARTITION implementation does not write
    it; see ``assert_column_stats_present`` and
    ``value_counts_sum_to_row_count`` for details.
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
            destination_table=as_destination_name(destination),
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
@Name("value_counts across data files sum to source row count")
def value_counts_sum_to_row_count(self, minio_root_user, minio_root_password):
    """Per-column value_counts over all data files equal the exported row count.

    End-to-end numeric correctness check for ``value_counts``: if
    ClickHouse writes bad statistics, predicate push-down breaks silently
    at read time.

    Currently registered as XFail in ``regression.py`` — the EXPORT
    PARTITION write path in ``IcebergWrites.cpp`` populates
    ``column_sizes`` / ``null_value_counts`` / ``lower_bounds`` /
    ``upper_bounds`` but never ``value_counts`` (the field is declared in
    the Avro schema but left null). The scenario will flip to a pass
    automatically once ClickHouse starts writing ``value_counts``.
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
            destination_table=as_destination_name(destination),
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
@Name("data file paths live under the table prefix")
def data_file_paths_under_table_prefix(
    self, minio_root_user, minio_root_password
):
    """Every ``data_file.file_path`` starts with the table's storage location.

    Per the Iceberg spec the ``file_path`` field on a manifest entry is a
    "Location URI with FS scheme", and with
    ``write_full_path_in_iceberg_metadata = 1`` ClickHouse correctly sets
    the table ``location`` in ``metadata.json`` to an absolute
    ``s3://<bucket>/<prefix>/`` URI — we reuse that as the expected prefix
    so this scenario is catalog-mode-agnostic.

    Currently registered as XFail in ``regression.py``:
    ``MultipleFileWriter.cpp`` (``startNewFile``) pushes
    ``filename.path_in_storage`` into ``data_file_names``, which ends up
    in the manifest entry's ``file_path``. The spec (and the sibling
    ``location`` field) require the URI form from
    ``filename.path_in_metadata`` — without it, Iceberg clients (PyIceberg,
    Spark, Trino) that rely on the scheme to pick a FileIO will mis-route
    reads. Scenario flips to pass as soon as ClickHouse writes the full
    URI there.
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
            destination_table=as_destination_name(destination),
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


SCENARIOS = (
    snapshot_advances_per_export,
    snapshot_summary_records_match,
    manifest_partition_spec_matches_source,
    column_stats_are_populated,
    value_counts_sum_to_row_count,
    data_file_paths_under_table_prefix,
)


@TestFeature
@Name("manifest integrity")
def feature(self, minio_root_user, minio_root_password):
    """Iceberg manifest and metadata correctness after EXPORT PARTITION."""
    for scenario in SCENARIOS:
        Scenario(test=scenario)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
