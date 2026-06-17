"""Per-setting behaviour tests for EXPORT PARTITION.

Settings already exercised elsewhere (``write_full_path_in_iceberg_metadata``
in ``storage_paths``; ``force_export`` / ``manifest_ttl`` in
``transactions``; ``allow_experimental_export_merge_tree_partition`` and
``export_merge_tree_partition_max_retries`` upstream) are not re-tested here.
"""

import io

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Settings_ParquetCompression,
)

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
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    HOST_MINIO_ENDPOINT,
    get_data_files,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"

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
        without_scheme = file_path[len("s3://"):]
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
                extra_settings=FULL_PATHS_SETTING + [
                    ("output_format_parquet_compression_method", ch_codec),
                ],
            )

        with Then(
            f"every column chunk of every {ch_codec} data file uses "
            f"{parquet_codec}"
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
