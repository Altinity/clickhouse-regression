from testflows.core import *
from parquet.tests.common import *
from s3.tests.common import *
from alter.stress.tests.tc_netem import network_packet_delay

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
    # "allow_experimental_database_materialized_postgresql=1",
    # "allow_experimental_dynamic_type=1",
    # "allow_experimental_full_text_index=1",
    # "allow_experimental_funnel_functions=1",
    # "allow_experimental_hash_functions=1",
    # "allow_experimental_inverted_index=1",
    # "allow_experimental_join_condition=1",
    # "allow_experimental_json_type=1",
    # "allow_experimental_kafka_offsets_storage_in_keeper=1",
    # "allow_experimental_kusto_dialect=1",
    # "allow_experimental_live_view=1",
    # "allow_experimental_materialized_postgresql_table=1",
    # "allow_experimental_nlp_functions=1",
    # "allow_experimental_object_type=1",
    # "allow_experimental_parallel_reading_from_replicas=1",
    # "allow_experimental_prql_dialect=1",
    # "allow_experimental_query_deduplication=1",
    # "allow_experimental_shared_set_join=1",
    # "allow_experimental_statistics=1",
    # "allow_experimental_time_series_table=1",
    # "allow_experimental_ts_to_grid_aggregate_function=1",
    # "allow_experimental_variant_type=1",
    # "allow_experimental_vector_similarity_index=1",
]


@TestStep(Given)
def set_delay_on_a_node(self, node=None):
    """Set a delay on a network node."""

    if node is None:
        node = self.context.node

    network_packet_delay(node=node)


@TestStep(Given)
def set_delay_on_minio_node(self):
    """Set a delay on the MinIO node."""
    set_delay_on_a_node(node=self.context.cluster.node("minio"))


@TestStep(Given)
def create_parquet_on_s3(self, file_name, columns, compression_type=None, cluster=None):
    """Create a Parquet file on S3."""

    if compression_type is None:
        compression_type = "NONE"

    full_path = self.context.uri + file_name + ".Parquet"

    table = create_table(
        name=file_name,
        engine=f"S3('{full_path}', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        columns=columns,
        cluster=cluster,
    )

    return table


@TestStep(Given)
def create_parquet_on_s3_with_hive_partition(
    self, file_name, columns, compression_type=None, cluster=None
):
    if compression_type is None:
        compression_type = "NONE"

    full_path = self.context.uri + file_name + ".Parquet"

    table = create_table(
        name=file_name,
        engine=f"S3('{full_path}', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        columns=columns,
        cluster=cluster,
    )


@TestStep(Given)
def create_s3_parquet_all_datatypes(
    self, file_name, compression_type=None, row_count=10, cluster=None
):
    """Create a Parquet file with all supported data types."""
    columns = generate_all_column_types(include=parquet_test_columns())
    file = create_parquet_on_s3(
        file_name=file_name,
        columns=columns,
        compression_type=compression_type,
        cluster=cluster,
    )

    file.insert_test_data(row_count=row_count)


@TestStep(Given)
def create_s3_parquet_basic_numeric_datatypes(
    self, file_name, compression_type=None, cluster=None
):
    """Create a Parquet file with basic numeric data types."""
    columns = generate_all_basic_numeric_column_types()
    file = create_parquet_on_s3(
        file_name=file_name,
        columns=columns,
        compression_type=compression_type,
        cluster=cluster,
    )

    file.insert_test_data()


@TestStep(Given)
def create_s3_parquet_common_datatypes(
    self, file_name, compression_type=None, cluster=None
):
    """Create a Parquet file with common data types."""
    columns = common_columns()
    file = create_parquet_on_s3(
        file_name=file_name,
        columns=columns,
        compression_type=compression_type,
        cluster=cluster,
    )

    file.insert_test_data()


@TestStep(Given)
def create_s3_parquet_all_map_datatypes(self, file_name, compression_type=None):
    """Create a Parquet file with all supported map data types."""
    columns = generate_all_map_column_types()
    file = create_parquet_on_s3(
        file_name=file_name, columns=columns, compression_type=compression_type
    )

    file.insert_test_data()


@TestStep(Given)
def create_multiple_parquet_files_with_all_datatypes(
    self, number_of_files, cluster=None
):
    """Create multiple Parquet files with all supported data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_all_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name, cluster=cluster)
        join()

    return file_names


@TestStep(Given)
def create_multiple_parquet_files_with_common_datatypes(
    self, number_of_files=10, cluster=None
):
    """Create multiple Parquet files with common data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_common_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name, cluster=cluster)
        join()

    return file_names


@TestStep(Given)
def create_multiple_parquet_files_with_basic_numeric_datatypes(
    self, number_of_files=10, cluster=None
):
    """Create multiple Parquet files with basic numeric data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_basic_numeric_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name, cluster=cluster)
        join()

    return file_names


@TestStep(Given)
def create_parquet_files_in_different_paths(
    self, path_1, path_2, number_of_files=10, cluster=None
):
    """Create multiple Parquet files in different paths."""

    file_names_1 = [f"{path_1}/file_{getuid()}" for _ in range(number_of_files)]
    file_names_2 = [f"{path_2}/file_{getuid()}" for _ in range(number_of_files)]
    all_file_names = file_names_1 + file_names_2

    with Pool(4) as pool:
        for name_1 in file_names_1:
            By(
                test=create_s3_parquet_common_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name_1, cluste=cluster)
        for name_2 in file_names_2:
            By(
                test=create_s3_parquet_common_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name_2, cluster=cluster)
        join()

    return all_file_names


@TestStep(Given)
def create_multiple_parquet_files_with_all_map_datatypes(self, number_of_files):
    """Create multiple Parquet files with all supported map data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_all_map_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name)
        join()

    return file_names


@TestStep(Given)
def create_parquet_file_with_hive_partition(self, node=None, compression_type="NONE"):
    """Create a Parquet file with Hive partition."""
    file_name = "parquet_" + getuid()
    full_path = (
        self.context.uri
        + "event_date={event_date|yyyy-MM-dd}/region={region}/data_{uuid}"
        + ".Parquet"
    )
    if node is None:
        node = self.context.node

    create_table_query = (
        f"CREATE TABLE {file_name} (`event_date` Date, `region` String, `value` Float64) "
        f"ENGINE = S3('{full_path}', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}') "
        f"PARTITION BY (event_date, region) "
        f"ORDER BY (event_date, region)"
    )
    node.query(create_table_query)

    insert_data_query = (
        f"INSERT INTO {file_name} (event_date, region, value) VALUES "
        f"('2024-10-31', 'us-east-1', 123.45), "
        f"('2024-10-31', 'eu-central-1', 678.90), "
        f"('2024-11-01', 'us-east-1', 42.00)"
    )
    node.query(insert_data_query)


@TestStep(Given)
def create_parquet_file_with_bloom_filter(self):
    """Create a Parquet file with bloom filter."""
    upload_file_to_s3(
        file_src=f"../data/bloom/multi_column_bloom.gz.parquet",
        file_dest=f"data/parquet/multi_column_bloom.gz.parquet",
    )

    return "multi_column_bloom.gz.parquet"


@TestStep(When)
def select_parquet_from_s3(
    self,
    file_name,
    statement="*",
    node=None,
    type="Parquet",
    condition=None,
    settings=None,
    output_format=None,
):
    """Select data from a Parquet file on S3."""

    # FROM s3(s3_conn, filename='test_03262_*', format=Parquet)

    if node is None:
        node = self.context.node

    r = f"SELECT {statement} FROM s3('{self.context.uri}{file_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', '{type}')"

    if condition is not None:
        r += rf" {condition}"

    if output_format is None:
        output_format = "TabSeparated"

    r += rf" FORMAT {output_format}"

    if settings is not None:
        r += f" SETTINGS {settings}"

    return node.query(r)


@TestStep(When)
def select_parquet_from_s3_cluster(
    self,
    file_name,
    statement="*",
    node=None,
    type="Parquet",
    condition=None,
    settings=None,
    output_format=None,
    cluster=None,
):
    """Select data from a Parquet file on S3."""

    if cluster is None:
        cluster = "replicated_cluster"

    if node is None:
        node = self.context.node

    r = f"SELECT {statement} FROM s3Cluster('{cluster}','{self.context.uri}{file_name}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', '{type}')"

    if condition is not None:
        r += rf" {condition}"

    if output_format is None:
        output_format = "TabSeparated"

    r += rf" FORMAT {output_format}"

    if settings is not None:
        r += f" SETTINGS {settings}"

    return node.query(r)


@TestStep(When)
def join_parquet_from_s3_cluster(
    self,
    file_name1,
    file_name2,
    statement1="*",
    statement2="*",
    node=None,
    type="Parquet",
    condition1=None,
    condition2=None,
    settings=None,
    output_format=None,
    cluster=None,
):
    """Join data from two Parquet files on S3."""

    if cluster is None:
        cluster = "replicated_cluster"

    if node is None:
        node = self.context.node

    # Retrieve column names from file_name1
    column_query = f"SELECT name FROM system.columns WHERE table = '{file_name1}'"
    columns_result = node.query(column_query)
    columns = [row[0] for row in columns_result.result_rows]

    # Select a random column name
    join_column = random.choice(columns)

    query1 = f"SELECT {statement1} FROM s3Cluster('{cluster}','{self.context.uri}{file_name1}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', '{type}')"
    query2 = f"SELECT {statement2} FROM s3Cluster('{cluster}','{self.context.uri}{file_name2}.Parquet', '{self.context.access_key_id}', '{self.context.secret_access_key}', '{type}')"

    if condition1 is not None:
        query1 += rf" {condition1}"

    if condition2 is not None:
        query2 += rf" {condition2}"

    join_query = f"SELECT * FROM ({query1}) AS t1 JOIN ({query2}) AS t2 ON t1.{join_column} = t2.{join_column}"

    if output_format is None:
        output_format = "TabSeparated"

    join_query += rf" FORMAT {output_format}"

    if settings is not None:
        join_query += f" SETTINGS {settings}"

    return node.query(join_query)


@TestStep(When)
def select_parquet_with_metadata_caching(self, file_name, log_comment=None):
    """Select data from a Parquet file with metadata caching enabled."""

    log_comment = "log_" + getuid()
    settings = f"input_format_parquet_use_metadata_cache=1, optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}'"

    start_time = time.time()

    select_parquet_from_s3(file_name=file_name, settings=settings)
    execution_time = time.time() - start_time

    return execution_time


@TestStep(When)
def select_parquet_with_metadata_caching_from_cluster(
    self, file_name, cluster=None, additional_setting=None, condition=None
):
    """Select data from a Parquet file with metadata caching enabled on a cluster."""
    log_comment = "log_" + getuid()
    settings = f"input_format_parquet_use_metadata_cache=1, optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}'"

    if additional_setting is not None:
        settings += f", {additional_setting}"

    start_time = time.time()
    select_parquet_from_s3_cluster(
        file_name=file_name, settings=settings, cluster=cluster, condition=condition
    )
    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(When)
def select_parquet_with_metadata_caching_with_join(
    self, file_name1, file_name2, condition=None, additional_setting=False
):
    """Select data from a Parquet file with metadata caching enabled."""

    log_comment = "log_" + getuid()
    settings = f"input_format_parquet_use_metadata_cache=1, optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}'"

    if additional_setting:
        settings += f", {additional_setting}"

    start_time = time.time()

    join_parquet_from_s3_cluster(
        file_name1=file_name1,
        file_name2=file_name2,
        settings=settings,
        condition1=condition,
        condition2=condition,
    )
    execution_time = time.time() - start_time

    return execution_time, log_comment


@TestStep(Then)
def check_hits(self, log_comment, node=None):
    """Check the number of cache hits and misses for a Parquet file."""
    if node is None:
        node = self.context.node

    node.query("SYSTEM FLUSH LOGS")

    r = f"SELECT ProfileEvents['ParquetMetaDataCacheHits'] FROM system.query_log where log_comment = '{log_comment}' AND type = 'QueryFinish' ORDER BY event_time desc FORMAT TSV;"
    hits = node.query(r)

    assert (
        "1" in hits.output.strip()
    ), f"number of hits is less than 1 and = {hits.output.strip()}"


@TestStep(Then)
def check_hits_on_cluster(self, log_comment, initiator_node=None, other_nodes=None):
    """Check the number of cache hits and misses for a Parquet file on a cluster."""

    if other_nodes is None:
        other_nodes = self.context.node_list

    if initiator_node is None:
        initiator_node = self.context.swarm_initiator

    initiator_node.query("SYSTEM FLUSH LOGS")
    r = f"SELECT ProfileEvents['ParquetMetaDataCacheHits'] FROM system.query_log where log_comment = '{log_comment}' AND type = 'QueryFinish' ORDER BY event_time desc FORMAT TSV;"
    hits = initiator_node.query(r)

    assert (
        "0" in hits.output.strip()
    ), f"number of hits is less than 1 and = {hits.output.strip()}"

    for node in other_nodes:
        for retry in retries(count=10, delay=2):
            with retry:
                node.query("SYSTEM FLUSH LOGS")
                hits = node.query(r)
                assert (
                    int(hits.output.strip()) > 0
                ), f"number of hits is less than 1 and = {hits.output.strip()}"


@TestStep(Then)
def check_misses(self, log_comment, node=None):
    """Check the number of cache hits and misses for a Parquet file."""
    if node is None:
        node = self.context.node

    node.query("SYSTEM FLUSH LOGS")

    r = f"SELECT ProfileEvents['ParquetMetaDataCacheMisses'] FROM system.query_log where log_comment = '{log_comment}' AND type = 'QueryFinish' ORDER BY event_time desc FORMAT TSV;"

    return node.query(r)


@TestStep(Then)
def assert_hits(self, file_name, log_comment):
    """Assert the number of cache hits and misses for a Parquet file."""

    with By("selecting data from a Parquet file with metadata caching"):
        select_parquet_with_metadata_caching(
            file_name=file_name, log_comment=log_comment
        )

    with And("checking the number of cache hits"):
        hits = check_hits(log_comment=log_comment)
        assert hits >= 1, f"Expected 1 hit, got {hits}"


@TestStep(When)
def select_parquet_metadata_from_s3(
    self, file_name, node=None, log_comment=None, caching=False, statement="*"
):
    """Select metadata from a Parquet file on S3."""

    if caching:
        settings = "input_format_parquet_use_metadata_cache=1, optimize_count_from_files=0, remote_filesystem_read_prefetch=0"
    else:
        settings = None

    if node is None:
        node = self.context.node

    if log_comment is not None:
        settings += f", log_comment='{log_comment}'"

    start_time = time.time()
    parquet = select_parquet_from_s3(
        file_name=file_name,
        node=node,
        type="ParquetMetadata",
        settings=settings,
        statement=statement,
    )
    execution_time = time.time() - start_time

    return parquet, execution_time
