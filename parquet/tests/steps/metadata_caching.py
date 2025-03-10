from testflows.core import *
from parquet.tests.common import *
from s3.tests.common import *
from alter.stress.tests.tc_netem import network_packet_delay


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
    self, file_name, cluster=None, additional_setting=None, log=False
):
    """Select data from a Parquet file with metadata caching enabled on a cluster."""
    log_comment = "log_" + getuid()
    settings = f"input_format_parquet_use_metadata_cache=1, optimize_count_from_files=0, remote_filesystem_read_prefetch=0, log_comment='{log_comment}'"

    if additional_setting is not None:
        settings += f", {additional_setting}"

    start_time = time.time()
    select_parquet_from_s3_cluster(
        file_name=file_name, settings=settings, cluster=cluster
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
def check_hits_on_cluster(self, log_comment, other_nodes=None):
    """Check the number of cache hits and misses for a Parquet file on a cluster."""

    if other_nodes is None:
        other_nodes = self.context.node_list

    initiator_node = self.context.cluster.node("node1")

    initiator_node.query("SYSTEM FLUSH LOGS")
    r = f"SELECT ProfileEvents['ParquetMetaDataCacheHits'] FROM system.query_log where log_comment = '{log_comment}' AND type = 'QueryFinish' ORDER BY event_time desc FORMAT TSV;"
    hits = initiator_node.query(r)

    assert (
        "0" in hits.output.strip()
    ), f"number of hits is less than 1 and = {hits.output.strip()}"

    for node in other_nodes:
        node.query("SYSTEM FLUSH LOGS")
        hits = node.query(r)
        assert (
            "1" in hits.output.strip()
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
