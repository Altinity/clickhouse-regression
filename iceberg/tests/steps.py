from testflows.core import *

import pyiceberg
from pyiceberg.catalog import load_catalog

from helpers.common import getuid

S3_ACCESS_KEY_ID = "minio"
S3_SECRET_ACCESS_KEY = "minio123"
CATALOG_TYPE = "rest"


@TestStep(Given)
def create_catalog(
    self,
    uri,
    name="rest_catalog",
    s3_endpoint="http://localhost:9002",
    s3_access_key_id=S3_ACCESS_KEY_ID,
    s3_secret_access_key=S3_SECRET_ACCESS_KEY,
    catalog_type=CATALOG_TYPE,
):
    catalog = load_catalog(
        name,
        **{
            "uri": uri,
            "type": catalog_type,
            "s3.endpoint": s3_endpoint,
            "s3.access-key-id": s3_access_key_id,
            "s3.secret-access-key": s3_secret_access_key,
        },
    )

    return catalog


@TestStep(Given)
def create_namespace(self, catalog, namespace):
    try:
        catalog.create_namespace(namespace)
    except pyiceberg.exceptions.NamespaceAlreadyExistsError:
        note("Namespace already exists")
    except Exception as e:
        note(f"An unexpected error occurred: {e}")
        raise


@TestStep(Given)
def drop_iceberg_table(self, catalog, namespace, table_name):
    table_list = catalog.list_tables(namespace)
    for table in table_list:
        if table[0] == namespace and table[1] == table_name:
            note("Dropping table")
            catalog.drop_table(f"{namespace}.{table_name}")


@TestStep(Given)
def create_iceberg_table(
    self,
    catalog,
    namespace,
    table_name,
    schema,
    location,
    partition_spec,
    sort_order=None,
):
    table = catalog.create_table(
        identifier=f"{namespace}.{table_name}",
        schema=schema,
        location=location,
        sort_order=sort_order,
        partition_spec=partition_spec,
    )
    return table


@TestStep(Then)
def read_data_with_s3_table_function(
    self, endpoint, s3_access_key_id, s3_secret_access_key, node=None, columns="*"
):
    if node is None:
        node = self.context.node

    node.query(
        f"SELECT * FROM s3('{endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
    )


@TestStep
def drop_database(self, database_name=None, node=None):
    if node is None:
        node = self.context.node

    if database_name is None:
        database_name = "database_" + getuid()

    node.query(f"DROP DATABASE IF EXISTS {database_name}")
    return database_name


@TestStep(Given)
def create_experimental_iceberg_database(
    self,
    namespace,
    database_name=None,
    node=None,
    rest_catalog_url="http://rest:8181/v1",
    s3_access_key_id=S3_ACCESS_KEY_ID,
    s3_secret_access_key=S3_SECRET_ACCESS_KEY,
    catalog_type=CATALOG_TYPE,
    storage_endpoint="http://minio:9000/warehouse",
):
    if node is None:
        node = self.context.node

    if database_name is None:
        database_name = "iceberg_database_" + getuid()

    node.query(
        f"""
            SET allow_experimental_database_iceberg=true;
            CREATE DATABASE {database_name}
            ENGINE = Iceberg('{rest_catalog_url}', '{s3_access_key_id}', '{s3_secret_access_key}')
            SETTINGS catalog_type = '{catalog_type}', storage_endpoint = '{storage_endpoint}', warehouse = '{namespace}';
        """
    )

    return database_name


@TestStep(Then)
def read_data_from_clickhouse_iceberg_table(
    self, database_name, namespace, table_name, node=None, columns="*"
):
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM {database_name}.\`{namespace}.{table_name}\`"
    )
    return result


@TestStep(Then)
def show_create_clickhouse_iceberg_table(
    self, database_name, namespace, table_name, node=None
):
    if node is None:
        node = self.context.node

    result = node.query(
        f"SHOW CREATE TABLE {database_name}.\`{namespace}.{table_name}\`"
    )
    return result


@TestStep(Then)
def read_data_with_icebergS3_table_function(
    self,
    storage_endpoint,
    node=None,
    columns="*",
    s3_access_key_id=S3_ACCESS_KEY_ID,
    s3_secret_access_key=S3_SECRET_ACCESS_KEY,
):
    if node is None:
        node = self.context.node

    node.query(
        f"SELECT {columns} FROM icebergS3('{storage_endpoint}', '{s3_access_key_id}', '{s3_secret_access_key}')"
    )
