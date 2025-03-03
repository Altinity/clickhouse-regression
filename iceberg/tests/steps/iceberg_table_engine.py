from testflows.core import *

from helpers.common import getuid

import random

random.seed(42)


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
