from parquet.tests.steps.metadata_caching import *
from parquet.tests.steps.swarm import *


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
    settings_for_select = None

    check_caching_metadata_on_multiple_nodes(
        create_parquet_files=create_parquet,
        additional_setting=settings_for_select,
        statement=statements,
        glob=glob,
        select=selects,
        condition=conditions,
    )


@TestCheck
def check_swarm_parquet(
    self,
    select,
    additional_settings,
    condition,
    statement,
    file_type,
    path_glob,
    enable_filesystem_cache,
):
    """Check to determine scenarios when metadata caching works on a swarm setup."""
    setting = random.choice(additional_settings)

    with Given(
        "I select data from the parquet file without using metadata caching",
        description=f"""additional setting for a query: setting: {setting} select function: {select.__name__}, condition: {condition}, statement: {statement}, file_type: {file_type}, path_glob: {path_glob}""",
    ):

        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        initial_execution_time, log = select(
            node=self.context.swarm_initiator,
            cache_metadata=False,
            additional_settings=setting,
            statement=statement,
            condition=condition,
            file_type=file_type,
            path_glob=path_glob,
            use_filesystem_cache=enable_filesystem_cache,
        )
    with When("I select the data from parquet in iceberg"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        num_runs = self.context.num_runs
        execution_times = []

        # First run to warm up cache
        select(
            node=self.context.swarm_initiator,
            cache_metadata=True,
            additional_settings=setting,
            statement=statement,
            condition=condition,
            file_type=file_type,
            path_glob=path_glob,
            use_filesystem_cache=enable_filesystem_cache,
        )

        # Run query multiple times and collect execution times
        pause()

        for _ in range(num_runs):
            execution_time, log = select(
                node=self.context.swarm_initiator,
                cache_metadata=True,
                additional_settings=setting,
                statement=statement,
                condition=condition,
                file_type=file_type,
                path_glob=path_glob,
                use_filesystem_cache=enable_filesystem_cache,
            )
            execution_times.append(execution_time)

        # Calculate average execution time
        execution_time = sum(execution_times) / len(execution_times)
    with Then("I check that the metadata was cached"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        check_hits_on_cluster(
            log_comment=log,
            initiator_node=self.context.swarm_initiator,
            other_nodes=self.context.swarm_nodes,
        )
    with And("I check that the query ran faster with caching"):
        if file_type == "ParquetMetadata" and statement != "*":
            skip()
        note(
            f"initial_execution_time={initial_execution_time}s execution_time={execution_time}s"
        )
        assert (
            initial_execution_time > execution_time
        ), f"query ran slower with caching initial_execution_time={initial_execution_time}s execution_time={execution_time}s"


@TestSketch(Scenario)
@Flags(TE)
def swarm_combinations(self):
    """Combinations of tests for metadata caching on a swarm setup."""
    with Given("I set a delay on the minio node"):
        set_delay_on_minio_node()

    conditions = either(
        *[
            "WHERE datetime < '2017-09-12 10:35:00.000000'",  # Should skip all files as the datetime is out of min/max range
            "WHERE datetime = '2019-09-12 10:35:00.000000'",
            "WHERE datetime = toDateTime('2019-09-12 10:35:00.000000')",
            "WHERE toYYYYMMDD(datetime) = 20190912",
            "WHERE datetime IN ('2019-09-12 10:35:00.000000', '2019-09-14 10:35:00.000000', '2019-09-16 10:35:00.000000')",
            "WHERE toString(datetime) LIKE '2019-09-12%'",
        ]
    )

    statements = either(*["*", "COUNT(*)", "COUNT(DISTINCT *)", "toDate(datetime)"])

    selects = either(
        *[
            select_parquet_from_swarm_s3_cluster,
            select_parquet_from_swarm_s3,
            select_parquet_from_swarm_s3_cluster_join,
        ]
    )

    enable_filesystem_cache = either(*[True, False])

    file_type = either(*["Parquet", "ParquetMetadata"])
    path_glob = either(*["**", "datetime_day=2019-08-17"])

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
        "azure_throw_on_zero_files_match=1",
    ]

    if check_clickhouse_version(">24.12")(self):
        settings += [
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

    check_swarm_parquet(
        select=selects,
        additional_settings=settings,
        condition=conditions,
        statement=statements,
        file_type=file_type,
        path_glob=path_glob,
        enable_filesystem_cache=enable_filesystem_cache,
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_NodeStops("1.0")
)
def one_node_disconnects(self):
    """Scenario when in a swarm cluster one node disconnects, and we check that we need to cache the parquet metadata again on that node when it recovers."""
    initiator_node = self.context.swarm_initiator
    disconnect_node = self.context.swarm_nodes[0]

    with Given("I cache metadata from a parquet file"):
        select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )
        _, log = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with When("I check that the metadata was cached"):
        check_hits_on_cluster(log_comment=log, initiator_node=initiator_node)

    with And("I stop the connection to one of the swarm nodes"):
        stop_swarm_1_node()
        start_swarm_1_node()

    with Then("I check that the metadata was cached again"):
        _, log2 = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with And("I validate that the metadata is not cached"):
        hits = check_hits(log_comment=log2, node=disconnect_node, assertion=False)

        assert hits == 0, f"metadata was cached on the disconnected node hits={hits}"

        _, log3 = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

        check_hits(log_comment=log2, node=disconnect_node)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings(
        "1.0"
    )
)
def user_config_disabled(self):
    """Scenario when in a swarm cluster input_format_parquet_use_metadata_cache is disabled in user profile settings for the initiator node."""
    initiator_node = self.context.swarm_initiator

    with Given(
        "I set a new config to the antalya node that disables user setting for input_parquet_metadata_cache"
    ):
        apply_user_config_with_disabled_caching_on_antalya()

    with When("I cache metadata from a parquet file"):
        select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )
        _, log = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with Then("I check that the metadata was cached"):
        check_hits_on_cluster(log_comment=log, initiator_node=initiator_node)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings(
        "1.0"
    )
)
def user_config_caching_disabled_on_swarm_nodes(self):
    """Scenario when in a swarm cluster swarm-1 and swarm-2 clusters do not have input_metadata_caching enabled in user profile settings but are enabled in the initiator antalya node."""
    initiator_node = self.context.swarm_initiator

    with Given(
        "I set a new config to the antalya node that disables user setting for input_parquet_metadata_cache"
    ):
        apply_user_config_with_disabled_caching_on_swarm_1()
        apply_user_config_with_disabled_caching_on_swarm_2()

    with When("I cache metadata from a parquet file"):
        select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )
        _, log = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with Then("I check that the metadata was cached"):
        check_hits_on_cluster(log_comment=log, initiator_node=initiator_node)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_NodeStops("1.0")
)
def node_dies_during_query_execution(self):
    """Scenario when in a swarm cluster one node dies during query execution, and we check that the query fails."""
    initiator_node = self.context.swarm_initiator
    disconnect_node = self.context.swarm_nodes[0]

    with Given("I cache metadata from a parquet file"):
        select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )
        _, log = select_parquet_from_swarm_s3(
            node=initiator_node, statement="COUNT(*)", cache_metadata=True
        )

    with When("I check that the metadata was cached"):
        check_hits_on_cluster(log_comment=log, initiator_node=initiator_node)

    with And("I disconnect one of the swarm nodes"):
        with Pool(2) as pool:
            Then(
                test=read_from_s3_and_expect_query_fail, parallel=True, executor=pool
            )()
            Then(test=stop_initiator_node, parallel=True, executor=pool)()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MaxSize("1.0")
)
def parquet_metadata_cache_slru_eviction(self):
    """Test to validate that Parquet metadata cache uses SLRU (Segmented Least Recently Used) eviction strategy."""
    log_comment = "test_" + getuid()
    node = self.context.node

    with Given("I create a test parquet file to measure metadata size"):
        catalog = setup_iceberg()
        metadata_size = create_parquet_partitioned_by_datetime(
            catalog=catalog,
            number_of_partitions=1,  # Create minimal file to measure metadata size
        )
        note(f"Metadata size for test file: {metadata_size} bytes")

    with And("I calculate number of files needed to exceed cache size"):
        # Cache size is 1000 bytes, we want to exceed it
        num_files = (1000 // metadata_size) + 2  # Add 2 to ensure we exceed the limit
        note(f"Creating {num_files} files to exceed cache size of 1000 bytes")

    with And("I create multiple parquet files"):
        files = []
        for i in range(num_files):
            catalog = setup_iceberg()
            create_parquet_partitioned_by_datetime(
                catalog=catalog, number_of_partitions=1
            )
            # Get the file path from the catalog
            parquet_files = catalog.list_tables("iceberg")[0].scan().plan_files()
            if parquet_files:
                files.append(parquet_files[0].file_path)

    with When("I access files in a pattern to test SLRU eviction"):
        # First access pattern: fill cache
        for file_name in files:
            select_parquet_metadata_from_s3(
                file_name=file_name,
                node=node,
                caching=True,
                log_comment=f"{log_comment}_fill",
            )

        # Second access pattern: keep most recent files in cache
        for file_name in files[:-1]:
            select_parquet_metadata_from_s3(
                file_name=file_name,
                node=node,
                caching=True,
                log_comment=f"{log_comment}_keep",
            )

        # Access last file again (should be a miss since it was evicted)
        select_parquet_metadata_from_s3(
            file_name=files[-1],
            node=node,
            caching=True,
            log_comment=f"{log_comment}_miss",
        )

    with Then("I verify cache hits and misses"):
        node.query("SYSTEM FLUSH LOGS")

        # Check hits for files that should be in cache (all except last)
        for i in range(len(files) - 1):
            hits = node.query(
                f"""
                SELECT ProfileEvents['ParquetMetaDataCacheHits'] 
                FROM system.query_log 
                WHERE log_comment = '{log_comment}_keep' 
                AND query LIKE '%{files[i]}%'
                AND type = 'QueryFinish'
                ORDER BY event_time DESC 
                LIMIT 1
            """
            )
            assert (
                int(hits.output.strip()) > 0
            ), f"Expected cache hit for file {files[i]}"

        # Check misses for file that should be evicted (last file)
        misses = node.query(
            f"""
            SELECT ProfileEvents['ParquetMetaDataCacheMisses'] 
            FROM system.query_log 
            WHERE log_comment = '{log_comment}_miss' 
            AND query LIKE '%{files[-1]}%'
            AND type = 'QueryFinish'
            ORDER BY event_time DESC 
            LIMIT 1
        """
        )
        assert int(misses.output.strip()) > 0, "Expected cache miss for evicted file"


@TestScenario
def parquet_metadata_cache_clearing(self):
    """Check that clearing Parquet metadata cache works on a single node."""
    log_comment = "test_" + getuid()

    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )

    with When("I select metadata of the Parquet file without caching"):
        parquet, initial_time = select_parquet_metadata_from_s3(
            file_name=files[0], caching=True
        )

    with And("I run the query multiple times with caching enabled"):
        execution_times = []
        for i in range(10):
            parquet, execution_time = select_parquet_metadata_from_s3(
                file_name=files[0],
                caching=True,
                log_comment=f"{log_comment}_cached_{i}",
            )
            execution_times.append(execution_time)

        cached_time = execution_times[-1]  # Save the last execution time

    with And("I flush the Parquet metadata cache"):
        flush_parquet_metadata_cache()

    with Then("I verify cache was invalidated by checking query performance"):
        parquet, after_flush_time = select_parquet_metadata_from_s3(
            file_name=files[0], caching=True, log_comment=f"{log_comment}_after_flush"
        )

        assert after_flush_time > cached_time, (
            f"Query after cache flush should be slower than cached version. "
            f"Cached time: {cached_time}, After flush time: {after_flush_time}"
        )

    with And("I check that we have cache misses after cache was dropped"):
        misses = check_misses(log_comment=f"{log_comment}_after_flush")
        assert 0 in int(
            misses.output.strip()
        ), "Expected cache miss after cache was dropped"


@TestScenario
def parquet_metadata_cache_clearing_on_cluster(self):
    """Check that clearing Parquet metadata cache works on a cluster."""
    log_comment = "test_" + getuid()

    with Given("I create a parquet file on s3"):
        files = create_multiple_parquet_files_with_all_datatypes(
            number_of_files=self.context.number_of_files
        )

    with When("I select metadata of the Parquet file without caching"):
        parquet, initial_time = select_parquet_metadata_from_s3(
            file_name=files[0], caching=True
        )

    with And("I run the query multiple times with caching enabled"):
        execution_times = []
        for i in range(10):
            parquet, execution_time = select_parquet_metadata_from_s3(
                file_name=files[0],
                caching=True,
                log_comment=f"{log_comment}_cached_{i}",
            )
            execution_times.append(execution_time)

        cached_time = execution_times[-1]  # Save the last execution time

    with And("I flush the Parquet metadata cache on cluster"):
        flush_parquet_metadata_cache_on_cluster()

    with Then("I verify cache was invalidated by checking query performance"):
        parquet, after_flush_time = select_parquet_metadata_from_s3(
            file_name=files[0], caching=True, log_comment=f"{log_comment}_after_flush"
        )

        assert after_flush_time > cached_time, (
            f"Query after cache flush should be slower than cached version. "
            f"Cached time: {cached_time}, After flush time: {after_flush_time}"
        )

    with And("I check that we have cache misses after cache was dropped"):
        misses = check_misses(log_comment=f"{log_comment}_after_flush")
        assert 0 in int(
            misses.output.strip()
        ), "Expected cache miss after cache was dropped"


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage("1.0"))
def distributed(self):
    """Tests for parquet metadata caching on a distributed setup with replicated cluster of 3 nodes."""
    Scenario(run=parquet_s3_caching)
    Scenario(run=parquet_metadata_format)
    Scenario(run=parquet_metadata_format_on_cluster)
    Scenario(run=parquet_metadata_cache_slru_eviction)


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm("1.0"))
def swarm(self):
    """Tests for parquet metadata caching on a swarm setup, where clickhouse-antalya is an initiator node and clickhouse-swarm-1 and clickhouse-swarm-2 are swarm nodes on a cluster."""
    Scenario(run=swarm_combinations)
    Scenario(run=one_node_disconnects)
    Scenario(run=user_config_disabled)
    Scenario(run=user_config_caching_disabled_on_swarm_nodes)
    Scenario(run=node_dies_during_query_execution)


@TestFeature
@Name("s3 metadata caching")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage("1.0"))
def feature(
    self,
    node="clickhouse1",
    number_of_files=15,
    partitions_for_swarm=1000,
    num_runs=50,
):
    """Tests that verify Parquet metadata caching for object storage.

    Nodes:
        Distributed setup:
            - clickhouse1
            - clickhouse2
            - clickhouse3

        Swarm setup:
            - clickhouse-antalya (initiator)
            - clickhouse-swarm-1
            - clickhouse-swarm-2
    Args:
        node: The node to run tests on (default: clickhouse1)
        number_of_files: Number of parquet files to create in distributed setup.
                        For tests with different locations, this is per location.
        partitions_for_swarm: Number of partitions for parquet files in swarm environment.
    """
    # Set up distributed cluster nodes
    self.context.num_runs = num_runs
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_list = [
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    # Set up swarm cluster nodes
    self.context.swarm_initiator = self.context.cluster.node("clickhouse-antalya")
    self.context.swarm_nodes = [
        self.context.cluster.node("clickhouse-swarm-1"),
        self.context.cluster.node("clickhouse-swarm-2"),
    ]

    # Set up general test configuration
    self.context.cluster_name = "replicated_cluster"
    self.context.number_of_files = number_of_files
    self.context.compression_type = "NONE"
    self.context.node = self.context.cluster.node(node)

    # Run distributed tests
    # Scenario(run=parquet_metadata_format)
    # Scenario(run=parquet_s3_caching)
    # Feature(run=distributed)

    # Run swarm tests if on Antalya build
    if check_if_antalya_build(self):
        with Given("I setup iceberg catalog"):
            catalog = setup_iceberg()

        with And("I create a partitioned parquet file in iceberg"):
            create_parquet_partitioned_by_datetime(
                catalog=catalog, number_of_partitions=partitions_for_swarm
            )

        Feature(run=swarm)
