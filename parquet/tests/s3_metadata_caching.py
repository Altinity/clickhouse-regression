from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *

from parquet.tests.steps.metadata_caching import *
from alter.stress.tests.tc_netem import network_packet_delay

PATH1 = "location_1"
PATH2 = "location_2"


@TestStep(Given)
def create_parquet_in_different_locations(self):
    """Create Parquet files in different locations."""

    return create_parquet_files_in_different_paths(path1=PATH1, path2=PATH2)


@TestStep(Given)
def create_parquet_in_different_locations_on_cluster(self):
    """Create Parquet files in different locations on a cluster."""

    return create_parquet_files_in_different_paths(
        path1=PATH1, path2=PATH2, cluster=self.context.cluster_name
    )


@TestStep(Given)
def create_multiple_parquet_files_with_common_datatypes_on_cluster(self):
    """Create multiple Parquet files with common data types on a cluster."""
    create_multiple_parquet_files_with_common_datatypes(
        cluster=self.context.cluster_name
    )


@TestStep(When)
def select_without_cache(self, file_name, statement="*"):
    """Select metadata of the Parquet file without caching the metadata."""
    parquet, without_cache = select_parquet_metadata_from_s3(
        file_name=file_name, statement=statement
    )

    return parquet, without_cache


@TestStep(When)
def select_with_cache(self, file_name, statement="*", log_comment=None):
    """Select metadata of the Parquet file with caching the metadata."""
    parquet, with_cache = select_parquet_metadata_from_s3(
        file_name=file_name, caching=True, statement=statement, log_comment=log_comment
    )

    return parquet, with_cache


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching(
        "1.0"
    )
)
def parquet_metadata_format(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()

    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )
    with When("I select metadata of the Parquet file without caching the metadata"):
        parquet, without_cache = select_without_cache(
            file_name=files[0], statement="COUNT(*)"
        )
    with And("I select metadata of the Parquet file with caching the metadata"):
        select_with_cache(file_name=files[0])
        parquet, with_cache = select_with_cache(
            file_name=files[0],
            log_comment=log_comment,
        )
    with Then("I check the number of hits in the metadata"):
        for retry in retries(count=10, delay=1):
            with retry:
                check_hits(log_comment=log_comment)

        assert (
            without_cache > with_cache
        ), f"query ran slower with caching without_cache={without_cache} with_cache={with_cache}"


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster(
        "1.0"
    ),
)
def parquet_metadata_format_on_cluster(self):
    """Check that a Parquet file can be created on S3."""
    log_comment = "test_" + getuid()
    node = self.context.node
    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )
    with When("I select metadata of the Parquet file without caching the metadata"):
        parquet, without_cache = select_parquet_metadata_from_s3(file_name=files[0])
    with And("I select metadata of the Parquet file with caching the metadata"):
        select_parquet_metadata_from_s3(file_name=files[0], caching=True)
        parquet, with_cache = select_parquet_metadata_from_s3(
            file_name=files[0], log_comment=log_comment, caching=True
        )
    with Then("I check the number of hits in the metadata"):
        for retry in retries(count=10, delay=1):
            with retry:
                check_hits_on_cluster(log_comment=log_comment)

        assert (
            without_cache > with_cache
        ), f"query ran slower with caching without_cache={without_cache} with_cache={with_cache}"


@TestCheck
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster(
        "1.0"
    )
)
def check_caching_metadata_on_multiple_nodes(
    self,
    create_parquet_files,
    additional_setting,
    statement,
    select,
    glob=None,
    condition=None,
):
    """Check to determine scenarios when metadata caching works on multiple node setup."""
    settings = random.choice(additional_setting)

    """Check to determine scenarios when metadata caching works on multiple node setup."""
    with Given("I create a parquet files on s3"):
        files = create_parquet_files()

        if glob is None:
            file_name = random.choice(files)
        else:
            file_name = glob

    with When("I select data from s3 before the metadata was cached"):
        if "join" in select.__name__:
            time_before_cache, _ = select(
                file_name1=files[0], file_name2=files[1], condition=condition
            )
        else:
            time_before_cache, _ = select(file_name=file_name, condition=condition)

    with And("I select data from s3 after the metadata was cached"):
        if "join" in select.__name__:
            time_after_cache, log_comment = select(
                file_name1=files[0],
                file_name2=files[1],
                additional_setting=settings,
                statement=statement,
                condition=condition,
            )
        else:
            time_after_cache, log_comment = select(
                file_name=file_name,
                additional_setting=settings,
                statement=statement,
                condition=condition,
            )

    with Then("I check the number of hits in the metadata"):
        check_hits_on_cluster(log_comment=log_comment)

        assert time_after_cache < time_before_cache, (
            f"query ran slower with caching time_before_cache={time_before_cache}s"
            f"time_after_cache={time_after_cache}s"
        )


@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AllSettings("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HivePartitioning(
        "1.0"
    ),
)
@TestSketch(Scenario)
def parquet_s3_caching(self):
    """Check to determine scenarios when metadata caching works and is useful."""
    settings = [
        None,
        "force_aggregation_in_order=1",
        "aggregation_memory_efficient_merge_threads=1",
        "allow_ddl=1",
        "allow_materialized_view_with_bad_select=1",
        "aggregate_functions_null_for_empty=1",
        "analyzer_compatibility_join_using_top_level_identifier=1",
        "apply_mutations_on_fly=1",
        "convert_query_to_cnf=1",
        "database_replicated_allow_heavy_create=1",
        "do_not_merge_across_partitions_select_final=1",
        "enable_optimize_predicate_expression=1",
        "enable_writes_to_query_cache=1",
        "enable_reads_from_query_cache=1",
        "engine_file_empty_if_not_exists=1",
        "engine_file_skip_empty_files=1",
        "engine_url_skip_empty_files=1",
        "fallback_to_stale_replicas_for_distributed_queries=1",
        "implicit_select=1",
        "optimize_move_to_prewhere=1",
        "optimize_move_to_prewhere_if_final=1" "asterisk_include_alias_columns=1",
        "azure_ignore_file_doesnt_exist=1",
        "azure_skip_empty_files=1",
        "azure_throw_on_zero_files_match=1" "allow_experimental_codecs=1",
        "allow_experimental_database_materialized_postgresql=1",
        "allow_experimental_dynamic_type=1",
        "allow_experimental_full_text_index=1",
        "allow_experimental_funnel_functions=1",
        "allow_experimental_hash_functions=1",
        "allow_experimental_inverted_index=1",
        "allow_experimental_join_condition=1",
        "allow_experimental_json_type=1",
        "allow_experimental_kafka_offsets_storage_in_keeper=1",
        "allow_experimental_kusto_dialect=1",
        "allow_experimental_live_view=1",
        "allow_experimental_materialized_postgresql_table=1",
        "allow_experimental_nlp_functions=1",
        "allow_experimental_object_type=1",
        "allow_experimental_parallel_reading_from_replicas=1",
        "allow_experimental_prql_dialect=1",
        "allow_experimental_query_deduplication=1",
        "allow_experimental_shared_set_join=1",
        "allow_experimental_statistics=1",
        "allow_experimental_time_series_table=1",
        "allow_experimental_ts_to_grid_aggregate_function=1",
        "allow_experimental_variant_type=1",
        "allow_experimental_vector_similarity_index=1",
    ]

    statements = either(*["*", "COUNT(*)", "COUNT(DISTINCT *)"])
    conditions = either(*[None])
    selects = either(
        *[
            select_parquet_with_metadata_caching_from_cluster,
            select_parquet_with_metadata_caching_with_join,
        ]
    )

    create_parquet = either(
        *[
            create_parquet_in_different_locations_on_cluster,
            create_multiple_parquet_files_with_common_datatypes_on_cluster,
            create_parquet_file_with_bloom_filter,
            create_parquet_file_with_hive_partition,
        ]
    )

    glob = either(*[None, "**.Parquet", "**.incorrect"])

    check_caching_metadata_on_multiple_nodes(
        create_parquet_files=create_parquet,
        additional_setting=settings,
        statement=statements,
        glob=glob,
        select=selects,
        condition=conditions,
    )


@TestFeature
@Name("s3 metadata caching")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage("1.0"))
def feature(self, node="clickhouse1", number_of_files=15):
    """Tests for parquet metadata caching for object storage."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_list = [
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]
    self.cotext.cluster_name = "replicated_cluster"
    self.context.number_of_files = number_of_files
    self.context.compression_type = "NONE"
    self.context.node = self.context.cluster.node(node)

    Scenario(run=parquet_metadata_format)
    Scenario(run=parquet_s3_caching)
