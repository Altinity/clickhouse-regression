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
def create_parquet_on_s3(self, file_name, columns, compression_type=None):
    """Create a Parquet file on S3."""

    if compression_type is None:
        compression_type = "NONE"

    full_path = self.context.uri + file_name + ".Parquet"

    table = create_table(
        name=file_name,
        engine=f"S3('{full_path}', '{self.context.access_key_id}', '{self.context.secret_access_key}', 'Parquet', '{compression_type.lower()}')",
        columns=columns,
    )

    return table


@TestStep(Given)
def create_s3_parquet_all_datatypes(self, file_name, compression_type=None):
    """Create a Parquet file with all supported data types."""
    columns = generate_all_column_types(include=parquet_test_columns())
    file = create_parquet_on_s3(
        file_name=file_name, columns=columns, compression_type=compression_type
    )

    file.insert_test_data()


@TestStep(Given)
def create_s3_parquet_basic_numeric_datatypes(self, file_name, compression_type=None):
    """Create a Parquet file with basic numeric data types."""
    columns = generate_all_basic_numeric_column_types()
    file = create_parquet_on_s3(
        file_name=file_name, columns=columns, compression_type=compression_type
    )

    file.insert_test_data()


@TestStep(Given)
def create_s3_parquet_common_datatypes(self, file_name, compression_type=None):
    """Create a Parquet file with common data types."""
    columns = common_columns()
    file = create_parquet_on_s3(
        file_name=file_name, columns=columns, compression_type=compression_type
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
def multiple_parquet_files_with_all_datatypes(self, number_of_files):
    """Create multiple Parquet files with all supported data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_all_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name)
        join()

    return file_names


@TestStep(Given)
def multiple_parquet_files_with_common_datatypes(self, number_of_files):
    """Create multiple Parquet files with common data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_common_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name)
        join()

    return file_names


@TestStep(Given)
def multiple_parquet_files_with_basic_numeric_datatypes(self, number_of_files):
    """Create multiple Parquet files with basic numeric data types."""
    file_names = [f"file_{getuid()}" for _ in range(number_of_files)]

    with Pool(4) as pool:
        for name in file_names:
            By(
                test=create_s3_parquet_basic_numeric_datatypes,
                parallel=True,
                executor=pool,
            )(file_name=name)
        join()

    return file_names


@TestStep(Given)
def multiple_parquet_files_with_all_map_datatypes(self, number_of_files):
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
def select_parquet_with_metadata_caching(self, file_name, log_comment=None):

    settings = "input_format_parquet_use_metadata_cache=1"

    if log_comment is not None:
        settings += f", log_comment='{log_comment}'"

    select_parquet_from_s3(file_name=file_name, settings=settings)


@TestStep(Then)
def check_hits(self, log_comment, node=None):
    """Check the number of cache hits and misses for a Parquet file."""
    if node is None:
        node = self.context.node

    r = f"SELECT ProfileEvents['ParquetMetaDataCacheHits'] FROM system.query_log where log_comment = '{log_comment}' AND type = 'QueryFinish' ORDER BY event_time desc LIMIT 1;"

    return node.query(r)


@TestStep(When)
def select_parquet_metadata_from_s3(self, file_name, node=None):
    """Select metadata from a Parquet file on S3."""

    if node is None:
        node = self.context.node

    return select_parquet_from_s3(
        file_name=file_name, node=node, type="ParquetMetadata"
    )
