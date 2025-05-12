from testflows.core import *
from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build

import iceberg.tests.steps.catalog as catalog_steps

CATALOG_TYPE = "rest"


@TestStep
def drop_database(self, database_name, node=None):
    if node is None:
        node = self.context.node

    node.query(f"DROP DATABASE IF EXISTS {database_name}")
    return database_name


@TestStep(Given)
def create_experimental_iceberg_database(
    self,
    s3_access_key_id,
    s3_secret_access_key,
    database_name=None,
    warehouse="s3://bucket1/",
    rest_catalog_url="http://ice-rest-catalog:5000",
    catalog_type=CATALOG_TYPE,
    storage_endpoint="http://minio:9000/warehouse",
    auth_header=None,
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

    database_engine_name = (
        "Iceberg" if check_clickhouse_version("<25.3")(self) else "DataLakeCatalog"
    )
    settings = {}
    if catalog_type:
        settings["catalog_type"] = catalog_type
    if storage_endpoint:
        settings["storage_endpoint"] = storage_endpoint
    if warehouse:
        settings["warehouse"] = warehouse
    if auth_header:
        settings["auth_header"] = auth_header

    if settings:
        settings_str = ",".join(
            [f"{key} = '{value}'" for key, value in settings.items()]
        )
        settings_str = f"SETTINGS {settings_str}"

    query = f"SET allow_experimental_database_iceberg=true; "
    query += f"CREATE DATABASE {database_name} "
    query += f"ENGINE = {database_engine_name}('{rest_catalog_url}', '{s3_access_key_id}', '{s3_secret_access_key}') "
    if settings:
        query += f"{settings_str}"

    try:
        node.query(query, exitcode=exitcode, message=message)
        yield database_name

    finally:
        with Finally("drop database"):
            node.query(f"DROP DATABASE IF EXISTS {database_name}")


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
    where_clause=None,
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
        settings.append(
            ("use_iceberg_partition_pruning", use_iceberg_partition_pruning)
        )

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

    if use_iceberg_metadata_files_cache and (
        check_clickhouse_version(">=25.4")(self) or check_if_antalya_build(self)
    ):
        settings.append(
            (
                "use_iceberg_metadata_files_cache",
                use_iceberg_metadata_files_cache,
            )
        )

    query = f"SELECT {columns} FROM {database_name}.\\`{namespace}.{table_name}\\`"

    if where_clause:
        query += f" WHERE {where_clause}"
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

    result = node.query(
        f"SHOW CREATE TABLE {database_name}.\\`{namespace}.{table_name}\\`"
    )
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
            uri="http://localhost:5000/",
            catalog_type=catalog_steps.CATALOG_TYPE,
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with And("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with And(f"delete table {namespace}.{table_name} if already exists"):
        catalog_steps.drop_iceberg_table(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And(f"define schema and create {namespace}.{table_name} table"):
        catalog_steps.create_iceberg_table_with_five_columns(
            catalog=catalog, namespace=namespace, table_name=table_name
        )

    with And("create database with Iceberg engine"):
        drop_database(database_name=database_name)
        create_experimental_iceberg_database(
            database_name=database_name,
            rest_catalog_url="http://ice-rest-catalog:5000",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            catalog_type=catalog_steps.CATALOG_TYPE,
            storage_endpoint="http://minio:9000/warehouse",
        )

    return f"{database_name}.\\`{namespace}.{table_name}\\`"
