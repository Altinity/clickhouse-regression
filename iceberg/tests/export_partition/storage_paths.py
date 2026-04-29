"""Storage path / location behaviour for EXPORT PARTITION.

Covers ``write_full_path_in_iceberg_metadata`` (absolute vs.
bucket-relative ``location``), deep ``location_prefix`` round-trips,
and isolation across multiple destinations sharing one bucket.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_StoragePaths

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_WAREHOUSE_BUCKET,
    _require_no_catalog,
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


def _seed_source(minio_root_user, minio_root_password):
    """Create a ready-to-export source table with one partition (2020).

    Yields the source table name; the ``create_replicated_mergetree`` step
    takes care of cleanup.
    """
    source_table = f"mt_{getuid()}"
    with Given("create source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert one partition worth of rows"):
        insert_data(table_name=source_table, values="(1, 2020), (2, 2020)")
    return source_table


@TestScenario
@Name("full path: metadata.json location is an absolute s3:// URI")
def full_path_metadata_has_absolute_s3_uri(
    self, minio_root_user, minio_root_password
):
    """With ``write_full_path_in_iceberg_metadata = 1`` the
    ``metadata.json`` ``location`` is an absolute ``s3://`` URI.
    """
    source_table = _seed_source(minio_root_user, minio_root_password)

    with Given("create the Iceberg destination with full paths in metadata"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the single partition with full paths in metadata"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("table.location() is an s3:// URL pointing to this destination"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        location = table.location()
        expected_name = as_destination_name(destination)
        assert location.startswith("s3://"), error(
            f"Expected metadata.location to start with 's3://', got {location!r}"
        )
        assert f"/{expected_name}" in location, error(
            f"Expected metadata.location to contain the destination table name "
            f"{expected_name!r}, got {location!r}"
        )


@TestScenario
@Name("default: metadata.json location is bucket-relative (no FS scheme)")
def default_metadata_has_relative_location(
    self, minio_root_user, minio_root_password
):
    """The default ``write_full_path_in_iceberg_metadata = 0`` keeps
    ``location`` bucket-relative (no FS scheme).
    """
    source_table = _seed_source(minio_root_user, minio_root_password)

    with Given("create the Iceberg destination with defaults"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the single partition with defaults"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
        )

    with Then("table.location() does not carry an FS scheme"):
        # Under the no-catalog StaticTable path PyIceberg still returns
        # whatever ClickHouse wrote verbatim. We read the metadata JSON
        # location directly instead of going through
        # load_pyiceberg_table which may resolve; check both the
        # canonical FS prefixes to stay endpoint-agnostic.
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        location = table.location()
        for scheme in ("s3://", "http://", "https://"):
            assert not location.startswith(scheme), error(
                f"Default behaviour should keep 'location' relative; got {location!r}"
            )


@TestScenario
@Name("deep prefix hierarchy round-trips cleanly")
def deep_prefix_hierarchy(self, minio_root_user, minio_root_password):
    """A destination under a deep ``location_prefix``
    (``warehouse/a/b/c/d``) round-trips cleanly with every segment
    preserved in the metadata location.
    """
    source_table = _seed_source(minio_root_user, minio_root_password)

    deep_prefix = f"{DEFAULT_S3_WAREHOUSE_BUCKET}/a/b/c/d"

    with Given("create destination at a deep prefix"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            location_prefix=deep_prefix,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export the single partition"):
        export_partition(
            source_table=source_table,
            destination_table=as_destination_name(destination),
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("the destination round-trips source rows"):
        assert_destination_row_count(
            destination=destination,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )

    with And("metadata.location preserves every prefix segment"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            no_catalog_prefix_root="a/b/c/d",
        )
        location = table.location()
        assert "/a/b/c/d/" in location, error(
            f"Expected deep prefix to appear in location, got {location!r}"
        )


@TestScenario
@Name("multiple destinations share a bucket but stay isolated")
def multiple_destinations_share_bucket(
    self, minio_root_user, minio_root_password
):
    """Two destinations under different prefixes of the same bucket
    receive distinct data and read back only their own rows.
    """
    source_a = f"mt_a_{getuid()}"
    source_b = f"mt_b_{getuid()}"

    with Given("create two independent source tables"):
        create_replicated_mergetree(
            table_name=source_a,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
        create_replicated_mergetree(
            table_name=source_b,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("seed distinct rows into each source"):
        insert_data(table_name=source_a, values="(1, 2020), (2, 2020)")
        insert_data(table_name=source_b, values="(100, 2020), (200, 2020)")

    with And("create destination A under warehouse/a"):
        dest_a = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            location_prefix=f"{DEFAULT_S3_WAREHOUSE_BUCKET}/a",
            query_settings=FULL_PATHS_SETTING,
        )

    with And("create destination B under warehouse/b"):
        dest_b = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            location_prefix=f"{DEFAULT_S3_WAREHOUSE_BUCKET}/b",
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export source A to destination A"):
        export_partition(
            source_table=source_a,
            destination_table=as_destination_name(dest_a),
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with And("export source B to destination B"):
        export_partition(
            source_table=source_b,
            destination_table=as_destination_name(dest_b),
            partition_id="2020",
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("destination A contains only source A's rows"):
        assert_destination_row_count(
            destination=dest_a,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_a,
            destination=dest_a,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )

    with And("destination B contains only source B's rows"):
        assert_destination_row_count(
            destination=dest_b,
            expected=2,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_b,
            destination=dest_b,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            order_by="id",
        )


SCENARIOS = (
    full_path_metadata_has_absolute_s3_uri,
    default_metadata_has_relative_location,
    deep_prefix_hierarchy,
    multiple_destinations_share_bucket,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_StoragePaths("1.0"))
@Name("storage paths")
def feature(self, minio_root_user, minio_root_password):
    """Storage location and path-writing behaviour for EXPORT PARTITION.
    ``no_catalog`` only — under ``DataLakeCatalog`` the table location
    is owned by the catalog so these assertions do not transfer.
    """
    _require_no_catalog(
        "storage_paths asserts on IcebergS3-specific layout concerns "
        "(write_full_path_in_iceberg_metadata, location_prefix, "
        "bucket-relative vs s3:// URIs in metadata.json); DataLakeCatalog "
        "owns the table location so these assertions don't transfer."
    )
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
