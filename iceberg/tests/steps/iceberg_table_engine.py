from testflows.core import *
from helpers.common import getuid


@TestStep(Given)
def create_table_with_iceberg_engine(
    self,
    url,
    access_key_id,
    secret_access_key,
    table_name=None,
    node=None,
    allow_dynamic_metadata_for_data_lakes=False,
):
    """Create table with Iceberg table engine."""
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = "iceberg_table_" + getuid()

    settings = ""
    if allow_dynamic_metadata_for_data_lakes:
        settings = "SETTINGS allow_dynamic_metadata_for_data_lakes = true"

    try:
        node.query(
            f"""
            CREATE TABLE {table_name} 
            ENGINE=Iceberg('{url}', '{access_key_id}', '{secret_access_key}')
            {settings}
            """
        )

        yield table_name

    finally:
        with Finally("drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


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

    try:
        node.query(
            f"""
            CREATE TABLE {table_name} 
            ENGINE=IcebergS3({config_name}, filename = '{filename}')
            {settings}
            """
        )
        return table_name

    finally:
        with Finally("drop table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")
