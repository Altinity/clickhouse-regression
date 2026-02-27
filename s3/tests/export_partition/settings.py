import random

from testflows.combinatorics import CoveringArray
from testflows.core import *

from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
    minio_storage_configuration,
)


@TestCheck
def export_with_settings(
    self,
    export_max_retries=None,
    export_manifest_ttl=None,
    export_force_export=None,
    export_overwrite_file=None,
    export_file_already_exists_policy=None,
    parquet_row_group_size=None,
    parquet_row_group_size_bytes=None,
    parquet_data_page_size=None,
    parquet_batch_size=None,
    parquet_parallel_encoding=None,
    parquet_use_custom_encoder=None,
    parquet_compression=None,
    parquet_version=None,
    parquet_string_as_string=None,
    parquet_write_page_index=None,
    parquet_write_checksums=None,
    s3_max_threads=None,
    s3_max_download_threads=None,
    s3_max_connections=None,
    s3_request_timeout_ms=None,
    s3_max_single_part_upload_size=None,
    s3_min_upload_part_size=None,
    s3_upload_part_size_multiply_factor=None,
    s3_upload_part_size_multiply_parts_count_threshold=None,
    min_insert_block_size_rows=None,
    min_insert_block_size_bytes=None,
    parts_to_delay_insert=None,
    max_parts_in_total=None,
    max_partitions_per_insert_block=None,
):
    """Test EXPORT PARTITION with a specific combination of settings."""

    source_table = f"source_{getuid()}"

    with Given("create source and S3 tables"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=3,
            number_of_parts=2,
            columns=default_columns(simple=False, partition_key_type="Int8"),
            cluster="replicated_cluster",
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False, partition_key_type="Int8"),
        )

    with When("export partitions"):
        settings = [("allow_experimental_export_merge_tree_part", "1")]

        if export_max_retries is not None:
            settings.append(
                ("export_merge_tree_partition_max_retries", str(export_max_retries))
            )
        if export_manifest_ttl is not None:
            settings.append(
                ("export_merge_tree_partition_manifest_ttl", str(export_manifest_ttl))
            )
        if export_force_export is not None:
            settings.append(
                ("export_merge_tree_partition_force_export", str(export_force_export))
            )
        if export_overwrite_file is not None:
            settings.append(
                (
                    "export_merge_tree_part_overwrite_file_if_exists",
                    str(export_overwrite_file),
                )
            )
        if export_file_already_exists_policy is not None:
            settings.append(
                (
                    "export_merge_tree_part_file_already_exists_policy",
                    export_file_already_exists_policy,
                )
            )
        if parquet_row_group_size is not None:
            settings.append(
                ("output_format_parquet_row_group_size", str(parquet_row_group_size))
            )
        if parquet_row_group_size_bytes is not None:
            settings.append(
                (
                    "output_format_parquet_row_group_size_bytes",
                    str(parquet_row_group_size_bytes),
                )
            )
        if parquet_data_page_size is not None:
            settings.append(
                ("output_format_parquet_data_page_size", str(parquet_data_page_size))
            )
        if parquet_batch_size is not None:
            settings.append(
                ("output_format_parquet_batch_size", str(parquet_batch_size))
            )
        if parquet_parallel_encoding is not None:
            settings.append(
                (
                    "output_format_parquet_parallel_encoding",
                    str(parquet_parallel_encoding),
                )
            )
        if parquet_use_custom_encoder is not None:
            settings.append(
                (
                    "output_format_parquet_use_custom_encoder",
                    str(parquet_use_custom_encoder),
                )
            )
        if parquet_compression is not None:
            settings.append(
                ("output_format_parquet_compression_method", parquet_compression)
            )
        if parquet_version is not None:
            settings.append(("output_format_parquet_version", parquet_version))
        if parquet_string_as_string is not None:
            settings.append(
                (
                    "output_format_parquet_string_as_string",
                    str(parquet_string_as_string),
                )
            )
        if parquet_write_page_index is not None:
            settings.append(
                (
                    "output_format_parquet_write_page_index",
                    str(parquet_write_page_index),
                )
            )
        if parquet_write_checksums is not None:
            settings.append(
                ("output_format_parquet_write_checksums", str(parquet_write_checksums))
            )
        if s3_max_threads is not None:
            settings.append(("max_threads", str(s3_max_threads)))
        if s3_max_download_threads is not None:
            settings.append(("max_download_threads", str(s3_max_download_threads)))
        if s3_max_connections is not None:
            settings.append(("s3_max_connections", str(s3_max_connections)))
        if s3_request_timeout_ms is not None:
            settings.append(("s3_request_timeout_ms", str(s3_request_timeout_ms)))
        if s3_max_single_part_upload_size is not None:
            settings.append(
                ("s3_max_single_part_upload_size", str(s3_max_single_part_upload_size))
            )
        if s3_min_upload_part_size is not None:
            settings.append(("s3_min_upload_part_size", str(s3_min_upload_part_size)))
        if s3_upload_part_size_multiply_factor is not None:
            settings.append(
                (
                    "s3_upload_part_size_multiply_factor",
                    str(s3_upload_part_size_multiply_factor),
                )
            )
        if s3_upload_part_size_multiply_parts_count_threshold is not None:
            settings.append(
                (
                    "s3_upload_part_size_multiply_parts_count_threshold",
                    str(s3_upload_part_size_multiply_parts_count_threshold),
                )
            )
        if min_insert_block_size_rows is not None:
            settings.append(
                ("min_insert_block_size_rows", str(min_insert_block_size_rows))
            )
        if min_insert_block_size_bytes is not None:
            settings.append(
                ("min_insert_block_size_bytes", str(min_insert_block_size_bytes))
            )
        if parts_to_delay_insert is not None:
            settings.append(("parts_to_delay_insert", str(parts_to_delay_insert)))
        if max_parts_in_total is not None:
            settings.append(("max_parts_in_total", str(max_parts_in_total)))
        if max_partitions_per_insert_block is not None:
            settings.append(
                (
                    "max_partitions_per_insert_block",
                    str(max_partitions_per_insert_block),
                )
            )

        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
            settings=settings,
        )

    with Then("verify tables match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestSketch(Scenario)
@Flags(TE)
@Requirements(
    RQ_ClickHouse_ExportPartition_Settings_AllowExperimental("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_MaxRetries("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_ManifestTTL("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_ForceExport("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_OverwriteFile("1.0"),
)
def export_partition_settings_combinations(self, strength=2):
    """Test combinations of EXPORT PARTITION specific settings.

    Uses covering array with strength 2 (pairwise) to ensure all pairs of
    parameter values appear at least once, significantly reducing the number
    of test cases compared to exhaustive testing.
    """

    parameters = {
        "export_max_retries": [1, 3, 5],
        "export_manifest_ttl": [60, 180, 360],
        "export_force_export": [0, 1],
        "export_overwrite_file": [0, 1],
        "export_file_already_exists_policy": ["skip", "error", "overwrite"],
    }

    with And(
        f"using covering array with strength {strength} to decrease the number of combinations"
    ):
        covering_array = CoveringArray(parameters, strength=strength)

    with Pool(16) as executor:
        for i, test_case in enumerate(covering_array):
            Combination(
                name=f"export_settings_{i}",
                test=export_with_settings,
                executor=executor,
                parallel=True,
            )(**test_case)
        join()


@TestSketch(Scenario)
@Flags(TE)
def parquet_settings_combinations(self, strength=2):
    """Test combinations of Parquet file write settings.

    Uses covering array with strength 2 (pairwise) to ensure all pairs of
    parameter values appear at least once.
    """

    parameters = {
        "parquet_row_group_size": [100000, 1000000, 5000000],
        "parquet_row_group_size_bytes": [100000000, 536870912, 1073741824],
        "parquet_data_page_size": [65536, 1048576, 4194304],
        "parquet_batch_size": [8192, 65536, 262144],
        "parquet_parallel_encoding": [0, 1],
        "parquet_use_custom_encoder": [0, 1],
        "parquet_compression": ["none", "lz4", "snappy", "zstd"],
        "parquet_version": ["1.0", "2.latest"],
        "parquet_string_as_string": [0, 1],
        "parquet_write_page_index": [0, 1],
        "parquet_write_checksums": [0, 1],
    }

    with And(
        f"using covering array with strength {strength} to decrease the number of combinations"
    ):
        covering_array = CoveringArray(parameters, strength=strength)

    with Pool(16) as executor:
        for i, test_case in enumerate(covering_array):
            Combination(
                name=f"parquet_settings_{i}",
                test=export_with_settings,
                executor=executor,
                parallel=True,
            )(**test_case)
        join()


@TestSketch(Scenario)
@Flags(TE)
def s3_settings_combinations(self, strength=2):
    """Test combinations of S3 settings.

    Uses covering array with strength 2 (pairwise) to ensure all pairs of
    parameter values appear at least once.
    """

    parameters = {
        "s3_max_threads": [1, 4, 8],
        "s3_max_download_threads": [1, 2, 4],
        "s3_max_connections": [1, 10, 25],
        "s3_request_timeout_ms": [1000, 30000, 60000],
        "s3_max_single_part_upload_size": [67108864, 268435456, 1073741824],
        "s3_min_upload_part_size": [5242880, 16777216, 67108864],
        "s3_upload_part_size_multiply_factor": [1, 2, 4],
        "s3_upload_part_size_multiply_parts_count_threshold": [10, 100, 1000],
    }

    with And(
        f"using covering array with strength {strength} to decrease the number of combinations"
    ):
        covering_array = CoveringArray(parameters, strength=strength)

    with Pool(16) as executor:
        for i, test_case in enumerate(covering_array):
            Combination(
                name=f"s3_settings_{i}",
                test=export_with_settings,
                executor=executor,
                parallel=True,
            )(**test_case)
        join()


@TestSketch(Scenario)
@Flags(TE)
def parts_partitions_settings_combinations(self, strength=2):
    """Test combinations of settings affecting parts and partitions.

    Uses covering array with strength 2 (pairwise) to ensure all pairs of
    parameter values appear at least once.
    """

    parameters = {
        "min_insert_block_size_rows": [0, 1048576, 2097152],
        "min_insert_block_size_bytes": [0, 268402944, 536805888],
        "parts_to_delay_insert": [0, 100, 300],
        "max_parts_in_total": [0, 1000, 10000],
        "max_partitions_per_insert_block": [1, 10, 100],
    }

    with And(
        f"using covering array with strength {strength} to decrease the number of combinations"
    ):
        covering_array = CoveringArray(parameters, strength=strength)

    with Pool(16) as executor:
        for i, test_case in enumerate(covering_array):
            Combination(
                name=f"parts_settings_{i}",
                test=export_with_settings,
                executor=executor,
                parallel=True,
            )(**test_case)
        join()


@TestSketch(Scenario)
@Flags(TE)
def all_settings_combined(self, strength=3):
    """Test combinations of all settings together with strength 3.

    Uses covering array with strength 3 to ensure all 3-way interactions
    between parameter values appear at least once.
    """

    parameters = {
        "export_max_retries": [1, 5],
        "export_manifest_ttl": [60, 360],
        "export_force_export": [0, 1],
        "export_overwrite_file": [0, 1],
        "export_file_already_exists_policy": ["skip", "overwrite"],
        "parquet_row_group_size": [100000, 1000000],
        "parquet_compression": ["lz4", "zstd"],
        "parquet_parallel_encoding": [0, 1],
        "parquet_write_page_index": [0, 1],
        "s3_max_threads": [1, 8],
        "s3_max_connections": [1, 25],
        "s3_max_single_part_upload_size": [67108864, 1073741824],
        "min_insert_block_size_rows": [0, 1048576],
        "max_parts_in_total": [0, 10000],
    }

    with And(
        f"using covering array with strength {strength} to decrease the number of combinations"
    ):
        covering_array_obj = CoveringArray(parameters, strength=strength)
        covering_array = list(covering_array_obj)

    if not self.context.stress and len(covering_array) > 200:
        with And("limit test count"):
            covering_array = random.sample(covering_array, 200)
            note(f"Limited to {len(covering_array)} tests in non-stress mode")

    with Pool(16) as executor:
        for i, test_case in enumerate(covering_array):
            Combination(
                name=f"all_settings_{i}",
                test=export_with_settings,
                executor=executor,
                parallel=True,
            )(**test_case)
        join()


@TestFeature
@Name("settings")
@Requirements(
    RQ_ClickHouse_ExportPartition_Settings_AllowExperimental("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_MaxRetries("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_ManifestTTL("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_ForceExport("1.0"),
    RQ_ClickHouse_ExportPartition_Settings_OverwriteFile("1.0"),
)
def feature(self):
    """Test all possible settings combinations for EXPORT PARTITION using covering arrays."""

    with Given("setup MinIO storage"):
        minio_storage_configuration(restart=True)

    Scenario(test=export_partition_settings_combinations)(strength=2)
    Scenario(test=parquet_settings_combinations)(strength=2)
    Scenario(test=s3_settings_combinations)(strength=2)
    Scenario(test=parts_partitions_settings_combinations)(strength=2)
    Scenario(test=all_settings_combined)(strength=3)
