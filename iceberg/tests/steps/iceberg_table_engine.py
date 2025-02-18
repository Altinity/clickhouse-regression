from testflows.core import *

from helpers.common import getuid

import re


@TestStep(Given)
def create_row_policy(
    self,
    name=None,
    on_clause=None,
    using_clause=None,
    as_clause=None,
    to_clause=None,
    node=None,
):
    """Create a row policy."""
    if name is None:
        name = f"row_policy_{getuid()}"

    if node is None:
        node = self.context.node

    query = f"CREATE ROW POLICY {name}"

    if on_clause:
        query += f" ON {on_clause}"

    if using_clause:
        query += f" USING {using_clause}"

    if as_clause:
        query += f" AS {as_clause}"

    if to_clause:
        query += f" TO {to_clause}"

    try:
        node.query(query)
        yield name

    finally:
        with Finally("drop row policy"):
            node.query(f"DROP ROW POLICY IF EXISTS {name} ON {on_clause}")


@TestStep(Given)
def create_table_with_iceberg_engine(
    self,
    url,
    access_key_id,
    secret_access_key,
    table_name=None,
    node=None,
    filename="data",
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


def parse_clickhouse_error(error_message):
    # Define regex pattern to extract error code, exception type, and message
    pattern = r"Code: (\d+)\. DB::Exception:.*?DB::Exception: (.*?):"

    # Extract error code and message using regex
    match = re.search(pattern, error_message)

    if match:
        error_code = match.group(1)  # Extract error code
        error_message_main = match.group(2)  # Extract main message before ':'

        return {
            "Code": int(error_code),
            "Exception Type": "DB::Exception",
            "Message": error_message_main.strip(),
        }

    return None
