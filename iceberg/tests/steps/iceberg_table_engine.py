from testflows.core import *
from testflows.asserts import error

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


def parse_clickhouse_error(error_message, only_error_name=True):
    """Parse ClickHouse error message and return error code and message."""
    pattern = r"Code: (\d+)\. DB::Exception:.*?DB::Exception: (.*?[\.:])"

    if only_error_name:
        # Code: 59. DB::Exception: Received from localhost:9000. DB::Exception: Illegal
        # type Nullable(String) of column string_col for filter. Must be UInt8 or
        # Nullable(UInt8).. (ILLEGAL_TYPE_OF_COLUMN_FOR_FILTER) -> (59, ILLEGAL_TYPE_OF_COLUMN_FOR_FILTER)
        pattern = r"Code: (\d+)\. DB::Exception:.*?DB::Exception: .*? \(([^)]+)\)"

    match = re.search(pattern, error_message, re.DOTALL)

    if match:
        error_code = match.group(1)  # Extract error code
        error_message_main = match.group(2)  # Extract main message before ':'

        return {
            "Code": int(error_code),
            "Message": error_message_main.strip(),
        }

    return None


@TestStep(Given)
def get_select_query_result(
    self, table_name, user_name=None, no_checks=True, node=None
):
    """Helper function to execute query and return result."""
    
    settings = []

    if node is None:
        node = self.context.node

    if user_name is None:
        settings.append(("user", user_name))

    return node.query(
        f"SELECT * FROM {table_name} ORDER BY tuple(*) FORMAT TabSeparated",
        settings=settings,
        no_checks=no_checks,
    )


@TestStep(Then)
def compare_results(self, result1, result2):
    """Helper function to compare query results or exception messages."""
    if result1.exitcode == 0:
        assert result1.output == result2.output, error()
    else:
        exception1 = parse_clickhouse_error(result1.output)["Message"]
        exception2 = parse_clickhouse_error(result2.output)["Message"]
        assert exception1 == exception2, error()


@TestStep(Given)
def create_merge_tree_table(self, table_name=None, node=None):
    """Create MergeTree table."""
    if node is None:
        node = self.context.node

    if table_name is None:
        table_name = f"merge_tree_table_{getuid()}"

    try:
        node.query(
            f"""
            CREATE TABLE {table_name} (
                boolean_col Nullable(Bool), 
                long_col Nullable(Int64), 
                double_col Nullable(Float), 
                string_col Nullable(String),
                date_col Nullable(Date)
            ) 
            ENGINE = MergeTree 
            ORDER BY tuple()
            """
        )
        yield table_name

    finally:
        with Finally("drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")
