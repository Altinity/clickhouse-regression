import os
import iceberg.tests.steps.catalog as catalog_steps

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

CATALOG_TYPE = "rest"


@TestStep
def drop_database(self, database_name, node=None):
    if node is None:
        node = self.context.node

    node.query(f"DROP DATABASE IF EXISTS {database_name}")
    return database_name


@TestStep(Given)
def create_experimental_iceberg_database_with_rest_catalog(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    database_name=None,
    warehouse="s3://bucket1/",
    rest_catalog_url="http://ice-rest-catalog:5000",
    catalog_type=CATALOG_TYPE,
    storage_endpoint="http://minio:9000/warehouse",
    auth_header="Authorization: Bearer foo",
    cluster_name=None,
    namespaces=None,
    exitcode=None,
    message=None,
    node=None,
):
    """Create experimental iceberg database with given parameters.
    Args:
        warehouse: S3 bucket name.
        s3_access_key_id: S3 access key id.
        s3_secret_access_key: S3 secret access key.
        database_name: Name of the database to create.
        node: ClickHouse node to execute the query on.
        rest_catalog_url: URL of the REST catalog.
        catalog_type: Type of the catalog.
        storage_endpoint: Storage endpoint.
        auth_header: Authorization header.
        exitcode: Exit code of the query.
        message: Message of the query.
    Returns:
        Name of the created database.
    """
    if node is None:
        node = self.context.node

    if database_name is None:
        database_name = "iceberg_database_" + getuid()

    database_engine_name = "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
    settings = {}
    if catalog_type:
        settings["catalog_type"] = catalog_type
    if storage_endpoint:
        settings["storage_endpoint"] = storage_endpoint
    if warehouse:
        settings["warehouse"] = warehouse
    if auth_header:
        settings["auth_header"] = auth_header
    if namespaces is not None:
        settings["namespaces"] = namespaces

    if settings:
        settings_str = ",".join([f"{key} = '{value}'" for key, value in settings.items()])
        settings_str = f"SETTINGS {settings_str}"

    query = f"SET allow_experimental_database_iceberg=true; "

    query += f"CREATE DATABASE {database_name} "

    if cluster_name:
        query += f"ON CLUSTER {cluster_name} "

    query += f"ENGINE = {database_engine_name}('{rest_catalog_url}', '{s3_access_key_id}', '{s3_secret_access_key}') "

    if settings:
        query += f"{settings_str}"

    try:
        node.query(query, exitcode=exitcode, message=message)
        yield database_name

    finally:
        with Finally("drop database"):
            node.query(f"DROP DATABASE IF EXISTS {database_name}")


@TestStep(Given)
def create_experimental_iceberg_database_with_glue_catalog(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    catalog_type="glue",
    region="us-east-1",
    database_name=None,
    endpoint_url="http://localstack:4566",
    storage_endpoint="http://minio:9000/warehouse",
    cluster_name=None,
    namespaces=None,
    exitcode=None,
    message=None,
    node=None,
):
    """Create experimental glue DataLakeCatalog database with given parameters.
    Args:
        aws_access_key_id: AWS access key id.
        aws_secret_access_key: AWS secret access key.
        database_name: Name of the database to create.
        node: ClickHouse node to execute the query on.
        endpoint_url: URL of the endpoint.
        catalog_type: Type of the catalog.
        region: Region of the catalog.
        storage_endpoint: Storage endpoint.
        exitcode: Exit code of the query.
        message: Message of the query.
    Returns:
        Name of the created database.
    """
    if node is None:
        node = self.context.node

    settings = {}

    if database_name is None:
        database_name = "iceberg_database_" + getuid()

    database_engine_name = "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
    if catalog_type:
        settings["catalog_type"] = catalog_type
    if storage_endpoint:
        settings["storage_endpoint"] = storage_endpoint
    if region:
        settings["region"] = region
    if s3_access_key_id:
        settings["aws_access_key_id"] = s3_access_key_id
    if s3_secret_access_key:
        settings["aws_secret_access_key"] = s3_secret_access_key
    if namespaces is not None:
        settings["namespaces"] = namespaces

    if settings:
        settings_str = ",".join([f"{key} = '{value}'" for key, value in settings.items()])
        settings_str = f"SETTINGS {settings_str}"

    query = f"SET allow_experimental_database_glue_catalog=1; "

    query += f"CREATE DATABASE {database_name} "

    if cluster_name:
        query += f"ON CLUSTER {cluster_name} "

    query += f"ENGINE = {database_engine_name}('{endpoint_url}') "

    if settings:
        query += f"{settings_str}"

    try:
        node.query(query, exitcode=exitcode, message=message)
        yield database_name

    finally:
        with Finally("drop database"):
            node.query(f"DROP DATABASE IF EXISTS {database_name}")


@TestStep(Given)
def create_experimental_iceberg_database(
    self,
    **kwargs,
):
    if self.context.catalog == "rest":
        return create_experimental_iceberg_database_with_rest_catalog(
            **kwargs,
        )
    elif self.context.catalog == "glue":
        return create_experimental_iceberg_database_with_glue_catalog(
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported catalog type: {self.context.catalog}")


@TestStep(Given)
def create_datalakecatalog_database_with_aws_glue(
    self, database_name, region="eu-central-1", name=None
):
    """Create a datalakecatalog database with AWS Glue catalog."""
    try:
        self.context.node.query(
            f"""
                SET allow_experimental_database_glue_catalog=1;
                CREATE DATABASE {database_name}
                ENGINE = DataLakeCatalog
                SETTINGS catalog_type = 'glue', region = '{region}', aws_access_key_id = '{os.getenv('AWS_ACCESS_KEY_ID')}', aws_secret_access_key = '{os.getenv('AWS_SECRET_ACCESS_KEY')}'
                """
        )
        yield database_name

    finally:
        with Finally("drop database"):
            self.context.node.query(f"DROP DATABASE IF EXISTS {database_name}")


@TestStep(Then)
def read_data_from_clickhouse_iceberg_table(
    self,
    database_name,
    namespace,
    table_name,
    node=None,
    columns="*",
    user="default",
    password="",
    order_by="tuple()",
    group_by=None,
    where_clause=None,
    object_storage_cluster=None,
    exitcode=None,
    message=None,
    format="TabSeparated",
    log_comment=None,
    cache_parquet_metadata=False,
    use_iceberg_partition_pruning=None,
    input_format_parquet_bloom_filter_push_down=None,
    input_format_parquet_filter_push_down=None,
    use_iceberg_metadata_files_cache=None,
    use_cache_for_count_from_files="0",
    lock_object_storage_task_distribution_ms=None,
    max_threads=None,
):
    if node is None:
        node = self.context.node

    settings = []

    if user:
        settings.append(("user", user))

    if password:
        settings.append(("password", f"{password}"))

    if log_comment:
        settings.append(("log_comment", f"{log_comment}"))

    if cache_parquet_metadata:
        settings.append(("input_format_parquet_use_metadata_cache", "1"))
        settings.append(("optimize_count_from_files", "0"))
        settings.append(("remote_filesystem_read_prefetch", "0"))
        settings.append(("input_format_parquet_filter_push_down", "1"))

    if use_iceberg_partition_pruning:
        settings.append(("use_iceberg_partition_pruning", use_iceberg_partition_pruning))

    if input_format_parquet_bloom_filter_push_down:
        settings.append(
            (
                "input_format_parquet_bloom_filter_push_down",
                input_format_parquet_bloom_filter_push_down,
            )
        )

    if input_format_parquet_filter_push_down:
        settings.append(
            (
                "input_format_parquet_filter_push_down",
                input_format_parquet_filter_push_down,
            )
        )

    if use_cache_for_count_from_files:
        settings.append(
            (
                "use_cache_for_count_from_files",
                use_cache_for_count_from_files,
            )
        )

    if lock_object_storage_task_distribution_ms:
        settings.append(
            (
                "lock_object_storage_task_distribution_ms",
                lock_object_storage_task_distribution_ms,
            )
        )

    if max_threads:
        settings.append(
            (
                "max_threads",
                max_threads,
            )
        )

    if use_iceberg_metadata_files_cache and (check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self)):
        settings.append(
            (
                "use_iceberg_metadata_files_cache",
                use_iceberg_metadata_files_cache,
            )
        )

    if object_storage_cluster:
        settings.append(
            (
                "object_storage_cluster",
                object_storage_cluster,
            )
        )

    query = f"SELECT {columns} FROM {database_name}.\\`{namespace}.{table_name}\\`"

    if where_clause:
        query += f" WHERE {where_clause}"

    if group_by:
        query += f" GROUP BY {group_by}"

    if order_by:
        query += f" ORDER BY {order_by}"

    if format:
        query += f" FORMAT {format}"

    result = node.query(
        query,
        settings=settings,
        exitcode=exitcode,
        message=message,
    )
    return result


@TestStep(Then)
def show_create_table(self, database_name, namespace, table_name, node=None):
    if node is None:
        node = self.context.node

    result = node.query(f"SHOW CREATE TABLE {database_name}.\\`{namespace}.{table_name}\\`")
    return result


@TestStep(Given)
def get_iceberg_table_name(
    self,
    minio_root_user,
    minio_root_password,
    database_name=None,
    namespace=None,
    table_name=None,
):
    """Create catalog, namespace, table and database with Iceberg engine.
    Return ClickHouse table name from database with Iceberg engine."""

    if database_name is None:
        database_name = f"database_{getuid()}"

    if namespace is None:
        namespace = "namespace_" + getuid()

    if table_name is None:
        table_name = f"table_{getuid()}"

    with Given("create catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(catalog=catalog, namespace=namespace, table_name=table_name)

    with And(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("create database with Iceberg engine"):
        create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            storage_endpoint="http://minio:9000/warehouse",
        )

    return f"{database_name}.\\`{namespace}.{table_name}\\`"


@TestStep(Then)
def check_values_in_system_tables(self, table_name, database):
    """Check that values are present in system.tables table."""
    node = self.context.node

    with By("check that database is correct"):
        database_name = node.query(f"SELECT database FROM system.tables WHERE name = '{table_name}'").output.strip()
        assert database_name == database, error()

    with By("check that engine is correct"):
        engine = node.query(f"SELECT engine FROM system.tables WHERE name = '{table_name}'").output.strip()
        assert engine == "IcebergS3", error()

    with By("check that full engine is correct"):
        full_engine = node.query(f"SELECT engine_full FROM system.tables WHERE name = '{table_name}'").output.strip()
        if self.context.catalog == "rest":
            assert (
                full_engine == "Iceberg(\\'http://minio:9000/warehouse/data/\\', \\'admin\\', \\'[HIDDEN]\\')"
            ), error()
        elif self.context.catalog == "glue":
            assert full_engine == "Iceberg(\\'http://minio:9000/warehouse/data/\\')", error()
        else:
            assert False, f"Unsupported catalog type: {self.context.catalog}"

    with By("check metdata path"):
        metadata_path = node.query(
            f"SELECT metadata_path FROM system.tables WHERE name = '{table_name}'"
        ).output.strip()
        assert metadata_path == "", error()

    with By("check that total rows is correct"):
        total_rows = node.query(f"SELECT total_rows FROM system.tables WHERE name = '{table_name}'").output.strip()
        if check_clickhouse_version(">=25.5")(self):
            assert total_rows == "10", error()

    with By("check that total bytes is correct"):
        total_bytes = node.query(f"SELECT total_bytes FROM system.tables WHERE name = '{table_name}'").output.strip()
        if check_clickhouse_version(">=25.6")(self):
            assert total_bytes == "12990", error()
