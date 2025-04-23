from testflows.core import *

from helpers.common import getuid, check_clickhouse_version

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

    node.query(query)

    return database_name


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
    exitcode=None,
    message=None,
    format="TabSeparated",
):
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM {database_name}.\\`{namespace}.{table_name}\\` ORDER BY {order_by} FORMAT {format}",
        settings=[("user", user), ("password", f"{password}")],
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
def create_table_with_iceberg_engine_from_config(
    self,
    table_name=None,
    node=None,
    config_name="iceberg_conf",
    filename="data",
    allow_dynamic_metadata_for_data_lakes=False,
):
    """Create table with Iceberg table engine with named collection
    config_name(iceberg_conf) in config.xml."""
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = "iceberg_table_" + getuid()

    settings = ""
    if allow_dynamic_metadata_for_data_lakes:
        settings = "SETTINGS allow_dynamic_metadata_for_data_lakes = true"

    node.query(
        f"""
        CREATE TABLE {table_name} 
        ENGINE=IcebergS3({config_name}, filename = '{filename}')
        {settings}
        """
    )

    return table_name


@TestStep(Given)
def create_named_collection(self, name=None, dict={}, node=None):
    """Create named collection from dictionary."""
    if node is None:
        node = self.context.node

    if name is None:
        name = "named_collection_" + getuid()

    params = ""

    for key, value in dict.items():
        params += f"{key} = '{value}', "

    node.query(f"CREATE NAMED COLLECTION {name} AS {params[:-2]}")

    return name


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
