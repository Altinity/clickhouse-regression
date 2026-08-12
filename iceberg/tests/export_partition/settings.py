"""Per-setting behaviour tests for EXPORT PARTITION.

Settings already exercised elsewhere (``write_full_path_in_iceberg_metadata``
in ``storage_paths``; ``force_export`` / ``manifest_ttl`` in
``transactions``; ``allow_experimental_export_merge_tree_partition`` and
``export_merge_tree_partition_max_retries`` upstream) are not re-tested here.

``export_merge_tree_part_schema_mismatch_mode`` (Altinity/ClickHouse#2111)
is covered under the ``schema mismatch mode`` sub-feature.
"""

import io

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Settings_ParquetCompression,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.casting import (
    _lossy_cast_rejection_expectation,
)
from iceberg.tests.export_partition.steps.common import (
    create_export_source_table,
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.export_status import (
    count_partition_export_rows,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_WAREHOUSE_BUCKET,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    HOST_MINIO_ENDPOINT,
    get_data_files,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"
NUMBER_OF_COLUMNS_DOESNT_MATCH = 20

SCHEMA_MISMATCH_MODE = "export_merge_tree_part_schema_mismatch_mode"
MODE_STRICT = "strict"
MODE_IGNORE_EXTRA = "ignore_extra_source_columns_by_position"

# Required whenever this module drives PyIceberg through ``get_data_files`` /
# ``load_pyiceberg_table`` in the no-catalog case. Without it, the manifest
# list path written into ``metadata.json`` is bucket-relative, and PyIceberg's
# default IO tries to resolve it on the local filesystem, which fails with
# FileNotFoundError. Individual ``data_file.file_path`` entries in the
# manifests are still written bucket-relative regardless of this setting —
# see ``_parse_s3_file_path`` below.
FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


def _seed_source(values="(1, 2020), (2, 2020), (3, 2020)"):
    """Create a ReplicatedMergeTree with one partition (2020) and seed rows."""
    source_table = f"mt_{getuid()}"
    with Given("create source ReplicatedMergeTree"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert partitioned values"):
        insert_data(table_name=source_table, values=values)
    return source_table


def _seed_source_with_columns(columns, values):
    """Create an export source with an explicit column list and seed rows."""
    source_table = f"mt_{getuid()}"
    with Given(f"create source with columns {columns}"):
        create_export_source_table(
            table_name=source_table,
            columns=columns,
            partition_by=SIMPLE_PARTITION_BY,
        )
    with And("insert partitioned values"):
        insert_data(table_name=source_table, values=values)
    return source_table


def _read_parquet_compression_codecs(
    bucket,
    key,
    minio_root_user,
    minio_root_password,
    endpoint_url=HOST_MINIO_ENDPOINT,
):
    """Return the set of compression codecs used across all column chunks
    of the given parquet object.
    """
    import boto3
    import pyarrow.parquet as pq

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=minio_root_user,
        aws_secret_access_key=minio_root_password,
    )
    body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    parquet_file = pq.ParquetFile(io.BytesIO(body))
    meta = parquet_file.metadata

    codecs = set()
    for rg in range(meta.num_row_groups):
        row_group = meta.row_group(rg)
        for col in range(row_group.num_columns):
            codecs.add(row_group.column(col).compression)
    return codecs


def _parse_s3_file_path(file_path, expected_bucket):
    """Split an Iceberg ``data_file.file_path`` into ``(bucket, key)``,
    accepting both ``s3://...`` and bucket-relative forms (the latter is
    what ``write_full_path_in_iceberg_metadata`` writes for data files).
    """
    if file_path.startswith("s3://"):
        without_scheme = file_path[len("s3://") :]
        bucket, _, key = without_scheme.partition("/")
        assert bucket == expected_bucket, error(
            f"Expected bucket {expected_bucket!r}, got {bucket!r} in {file_path!r}"
        )
        return bucket, key

    # Bucket-relative: strip any leading slash and assume the destination
    # lives in the default warehouse bucket.
    key = file_path.lstrip("/")
    assert key, error(f"Empty object key parsed from data_file path {file_path!r}")
    return expected_bucket, key


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Settings_ParquetCompression("1.0"))
@Name("output_format_parquet_compression_method flows to data files")
def parquet_compression_method_flows_to_data_files(
    self, minio_root_user, minio_root_password
):
    """``output_format_parquet_compression_method`` set on ``ALTER ...
    EXPORT PARTITION`` reaches the Parquet writer (codec inspected via
    pyarrow). Currently XFail: the export-task settings allowlist drops
    format settings before ``getFormatSettings`` runs.
    """
    source_table = _seed_source()

    compressions = (("zstd", "ZSTD"), ("snappy", "SNAPPY"))

    for ch_codec, parquet_codec in compressions:
        with Given(f"create a dedicated Iceberg destination for {ch_codec}"):
            # write_full_path_in_iceberg_metadata = 1 so PyIceberg can follow
            # the manifest-list pointer in metadata.json via S3 (see the
            # FULL_PATHS_SETTING docstring). It does not influence the
            # compression codec under test.
            destination = create_iceberg_destination(
                columns=SIMPLE_COLUMNS,
                partition_by=SIMPLE_PARTITION_BY,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                query_settings=FULL_PATHS_SETTING,
            )

        with When(f"export partition 2020 with {ch_codec} compression"):
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id="2020",
                extra_settings=FULL_PATHS_SETTING
                + [
                    ("output_format_parquet_compression_method", ch_codec),
                ],
            )

        with Then(
            f"every column chunk of every {ch_codec} data file uses " f"{parquet_codec}"
        ):
            data_files = get_data_files(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
            assert data_files, error(
                f"No data files found in destination for codec {ch_codec}"
            )

            observed = set()
            for data_file in data_files:
                bucket, key = _parse_s3_file_path(
                    data_file.file_path, DEFAULT_S3_WAREHOUSE_BUCKET
                )
                observed |= _read_parquet_compression_codecs(
                    bucket=bucket,
                    key=key,
                    minio_root_user=minio_root_user,
                    minio_root_password=minio_root_password,
                )

            # pyarrow reports codec names in upper-case. We compare
            # case-insensitively to avoid coupling the test to that
            # convention.
            normalised = {c.upper() for c in observed}
            assert normalised == {parquet_codec}, error(
                f"Expected every column to use {parquet_codec!r}, "
                f"got {sorted(observed)!r}"
            )


# ---------------------------------------------------------------------------
# export_merge_tree_part_schema_mismatch_mode (Altinity/ClickHouse#2111)
# ---------------------------------------------------------------------------


@TestScenario
@Name("strict rejects extra source columns")
def schema_mismatch_strict_rejects_extra_source(
    self, minio_root_user, minio_root_password
):
    """``strict`` (default) requires equal column counts: source with a
    trailing extra column is rejected with ``NUMBER_OF_COLUMNS_DOESNT_MATCH``.
    """
    source_table = _seed_source_with_columns(
        columns="id Int64, year Int32, extra String",
        values="(1, 2020, 'foo'), (2, 2020, 'bar'), (3, 2020, 'baz')",
    )

    with Given("create Iceberg destination with fewer columns"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("EXPORT PARTITION is rejected under strict mode"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[(SCHEMA_MISMATCH_MODE, MODE_STRICT)],
            exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
            message="NUMBER_OF_COLUMNS",
            wait_for_completion=False,
        )

    with And("no export status row is recorded"):
        count = count_partition_export_rows(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
        )
        assert count == 0, error(
            f"Expected no status row after synchronous rejection, got {count}"
        )


@TestScenario
@Name("ignore extra source columns by position drops trailing columns")
def schema_mismatch_ignore_extra_source_drops_trailing(
    self, minio_root_user, minio_root_password
):
    """``ignore_extra_source_columns_by_position`` allows a wider source: the
    trailing extra columns are dropped and the positional prefix is exported.
    """
    source_table = _seed_source_with_columns(
        columns="id Int64, year Int32, extra String",
        values="(1, 2020, 'foo'), (2, 2020, 'bar'), (3, 2020, 'baz')",
    )

    with Given("create Iceberg destination with the shared column prefix"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export under ignore_extra_source_columns_by_position"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[(SCHEMA_MISMATCH_MODE, MODE_IGNORE_EXTRA)],
        )

    with Then("destination has all source rows and matching id, year values"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year",
            order_by="id",
        )


@TestScenario
@Name("strict rejects extra destination columns")
def schema_mismatch_strict_rejects_extra_destination(
    self, minio_root_user, minio_root_password
):
    """``strict`` rejects a destination that has more columns than the source."""
    source_table = _seed_source_with_columns(
        columns=SIMPLE_COLUMNS,
        values="(1, 2020), (2, 2020)",
    )

    with Given("create Iceberg destination with an extra column"):
        destination = create_iceberg_destination(
            columns="id Int64, year Int32, extra String",
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("EXPORT PARTITION is rejected under strict mode"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[(SCHEMA_MISMATCH_MODE, MODE_STRICT)],
            exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
            message="NUMBER_OF_COLUMNS",
            wait_for_completion=False,
        )

    with And("destination remains empty"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Name("ignore extra source columns by position rejects extra destination columns")
def schema_mismatch_ignore_extra_rejects_extra_destination(
    self, minio_root_user, minio_root_password
):
    """``ignore_extra_source_columns_by_position`` only relaxes the
    source-has-more direction; destination-has-more is still rejected.
    """
    source_table = _seed_source_with_columns(
        columns=SIMPLE_COLUMNS,
        values="(1, 2020), (2, 2020)",
    )

    with Given("create Iceberg destination with an extra column"):
        destination = create_iceberg_destination(
            columns="id Int64, year Int32, extra String",
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then(
        "EXPORT PARTITION is still rejected under ignore_extra_source_columns_by_position"
    ):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[(SCHEMA_MISMATCH_MODE, MODE_IGNORE_EXTRA)],
            exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
            message="NUMBER_OF_COLUMNS",
            wait_for_completion=False,
        )

    with And("no export status row is recorded"):
        count = count_partition_export_rows(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
        )
        assert count == 0, error(
            f"Expected no status row after synchronous rejection, got {count}"
        )

    with And("destination remains empty"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestScenario
@Name("ignore extra source columns by position still rejects type mismatch")
def schema_mismatch_ignore_extra_rejects_type_mismatch(
    self, minio_root_user, minio_root_password
):
    """Dropping trailing extras must not bypass cast validation on the kept
    positional prefix. Source ``id Int64`` vs destination ``id Int32`` is a
    lossy cast and is rejected even under
    ``ignore_extra_source_columns_by_position``.
    """
    source_table = _seed_source_with_columns(
        columns="id Int64, year Int32, extra String",
        values="(1, 2020, 'foo'), (2, 2020, 'bar')",
    )

    with Given("create Iceberg destination with a narrowing id type"):
        destination = create_iceberg_destination(
            columns="id Int32, year Int32",
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    rejection_exitcode, rejection_message = _lossy_cast_rejection_expectation(self)

    with Then("EXPORT PARTITION is rejected for the prefix type mismatch"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
            extra_settings=[(SCHEMA_MISMATCH_MODE, MODE_IGNORE_EXTRA)],
            exitcode=rejection_exitcode,
            message=rejection_message,
            wait_for_completion=False,
        )

    with And("no export status row is recorded"):
        count = count_partition_export_rows(
            source_table=source_table,
            partition_id="2020",
            destination=destination,
        )
        assert count == 0, error(
            f"Expected no status row after synchronous rejection, got {count}"
        )

    with And("destination remains empty"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


SCHEMA_MISMATCH_SCENARIOS = (
    schema_mismatch_strict_rejects_extra_source,
    schema_mismatch_ignore_extra_source_drops_trailing,
    schema_mismatch_strict_rejects_extra_destination,
    schema_mismatch_ignore_extra_rejects_extra_destination,
    schema_mismatch_ignore_extra_rejects_type_mismatch,
)

SCENARIOS = (parquet_compression_method_flows_to_data_files,)


@TestFeature
@Name("settings")
def feature(self, minio_root_user, minio_root_password):
    """Behaviour of each export_merge_tree_partition_* setting."""
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Feature("schema mismatch mode"):
        for scenario in SCHEMA_MISMATCH_SCENARIOS:
            Scenario(test=scenario, flags=TE)(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
