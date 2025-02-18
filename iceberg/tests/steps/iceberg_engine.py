from testflows.core import *

from helpers.common import getuid

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
    namespace,
    s3_access_key_id,
    s3_secret_access_key,
    database_name=None,
    node=None,
    rest_catalog_url="http://rest:8181/v1",
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
    self,
    database_name,
    namespace,
    table_name,
    node=None,
    columns="*",
    user="default",
    password="",
    exitcode=None,
    message=None,
):
    if node is None:
        node = self.context.node

    result = node.query(
        f"SELECT {columns} FROM {database_name}.\\`{namespace}.{table_name}\\` FORMAT TabSeparated",
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
