import re
import math
import random
import string
import pyarrow as pa

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations
from datetime import date, timedelta
from helpers.common import getuid, check_clickhouse_version, check_if_antalya_build


random.seed(42)


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
def create_merge_tree_table_with_five_columns(self, table_name=None, node=None):
    """Create MergeTree table with five columns."""
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
                double_col Nullable(Float64), 
                string_col Nullable(String),
                date_col Nullable(Date32)
            ) 
            ENGINE = MergeTree 
            ORDER BY tuple()
            """
        )
        yield table_name

    finally:
        with Finally("drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


def random_string(length=None):
    """Generate a random string of given length."""
    if length is None:
        length = random.randint(1, 10)
    character_set = random.choice(
        [string.digits, string.ascii_letters, string.ascii_letters + string.digits]
    )
    return "".join(random.choices(character_set, k=length))


def generate_data(num_rows=100):
    data = []

    for _ in range(num_rows):
        entry = {
            "boolean_col": random.choice([True, False]),
            "long_col": random.randint(1, 5000),
            "double_col": round(random.uniform(1.0, 500.0), 2),
            "string_col": random_string(),
            "date_col": date(2020, 1, 1) + timedelta(days=random.randint(0, 1500)),
        }
        data.append(entry)

    return data


def transform_to_clickhouse_format(data):
    """Transform a list of dictionaries into a ClickHouse-compatible tuple format."""
    transformed = []
    for row in data:
        values = []
        for column_name, value in row.items():
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    values.append(f"round({value}, 2)")
                else:
                    values.append(str(value))
            elif isinstance(value, str):
                values.append(f"'{value}'")
            elif isinstance(value, date):
                values.append(f"'{value}'")
            elif isinstance(value, bool):
                values.append(str(value))
            elif isinstance(value, list):
                values.append(str(value))
            elif isinstance(value, dict):
                values.append(str(value))
            else:
                values.append(f"'{str(value)}'")
        transformed.append(f"({', '.join(values)})")

    return ", ".join(transformed)


@TestStep(Given)
def insert_same_data_to_iceberg_and_merge_tree_tables(
    self, merge_tree_table_name, iceberg_table, num_rows=100, data=None, node=None
):
    """Insert the same data into MergeTree and Iceberg tables."""
    if node is None:
        node = self.context.node

    if data is None:
        data = generate_data(num_rows=num_rows)

    with By("insert data into Iceberg table"):
        df = pa.Table.from_pylist(data)
        iceberg_table.append(df)

    with And("insert data into MergeTree table"):
        data_str = transform_to_clickhouse_format(data)
        note("Insert query:")
        note(f"INSERT INTO {merge_tree_table_name} VALUES {data_str}")
        node.query(f"INSERT INTO {merge_tree_table_name} VALUES {data_str}")


def get_all_combinations(items, max_length=None):
    """Generate all possible combinations of items up to a given length,
    output is comma-separated strings of items."""
    if max_length is None:
        max_length = len(items) + 1

    all_combinations = []
    for r in range(1, max_length + 1):
        all_combinations.extend([", ".join(combo) for combo in combinations(items, r)])
    return all_combinations


@TestStep(Given)
def get_select_query_result(
    self,
    table_name,
    select_columns="*",
    order_by="tuple(*)",
    user_name=None,
    no_checks=True,
    node=None,
    enable_filesystem_cache=True,
    filesystem_cache_name="cache_for_s3",
    format="TabSeparated",
    object_storage_cluster=None,
):
    """Helper function to execute query and return result."""

    settings = []

    if enable_filesystem_cache and check_clickhouse_version(">=24.10")(self):
        settings.append(("enable_filesystem_cache", 1))
        settings.append(("filesystem_cache_name", filesystem_cache_name))

    if node is None:
        node = self.context.node

    if user_name is not None:
        settings.append(("user", user_name))

    if object_storage_cluster:
        settings.append(("object_storage_cluster", object_storage_cluster))

    query = (
        f"SELECT {select_columns} FROM {table_name} ORDER BY {order_by} FORMAT {format}"
    )

    return node.query(
        query,
        settings=settings,
        no_checks=no_checks,
    )


@TestStep(Then)
def compare_data_in_two_tables(
    self,
    table_name1,
    table_name2,
    select_columns="*",
    order_by="tuple(*)",
    object_storage_cluster=None,
):
    """Compare data in two tables, ensuring floats are compared with math.isclose()."""
    table_name1_result = get_select_query_result(
        table_name=table_name1,
        select_columns=select_columns,
        order_by=order_by,
        object_storage_cluster=object_storage_cluster,
    ).output
    table_name2_result = get_select_query_result(
        table_name=table_name2,
        select_columns=select_columns,
        order_by=order_by,
        object_storage_cluster=object_storage_cluster,
    ).output
    assert compare_select_outputs(
        table_name1_result, table_name2_result, table_name1
    ), error()


def parse_clickhouse_error(error_message, only_error_name=True):
    """Parse ClickHouse error message and return error code and message."""
    pattern = r"Code: (\d+)\. DB::Exception:.*?DB::Exception: (.*?[\.:])"

    if only_error_name:
        # Code: 59. DB::Exception: Received from localhost:9000. DB::Exception: Illegal
        # type Nullable(String) of column string_col for filter. Must be UInt8 or
        # Nullable(UInt8).. (ILLEGAL_TYPE_OF_COLUMN_FOR_FILTER) -> (59, ILLEGAL_TYPE_OF_COLUMN_FOR_FILTER)
        pattern = r"Code: (\d+)\. DB::Exception:.*?DB::Exception: .* \(([^)]+)\)"

    match = re.search(pattern, error_message, re.DOTALL)

    if match:
        error_code = match.group(1)  # Extract error code
        error_message_main = match.group(2)  # Extract main message before ':'

        return {
            "Code": int(error_code),
            "Message": error_message_main.strip(),
        }

    return None


@TestStep(Then)
def compare_results(self, result1, result2):
    """Helper function to compare query results and exception messages."""
    if result1.exitcode == 0 and result2.exitcode == 0:
        assert result1.output == result2.output, error()
    elif result1.exitcode == 0:
        assert result1.output.strip() == "", error()
    elif result2.exitcode == 0:
        assert result2.output.strip() == "", error()
    else:
        exception1 = parse_clickhouse_error(result1.output)
        exception2 = parse_clickhouse_error(result2.output)
        assert exception1["Message"] == exception2["Message"], error()


@TestStep(When)
def grant_select(self, table_name, user_and_role_names, table_columns, node=None):
    """Define grants for users and roles."""
    if node is None:
        node = self.context.node

    try:
        node.query(
            f"GRANT SELECT({table_columns}) ON {table_name} TO {user_and_role_names}"
        )
        yield

    finally:
        with Finally("revoke select privilege"):
            node.query(
                f"REVOKE SELECT({table_columns}) ON {table_name} FROM {user_and_role_names}"
            )


@TestStep(Given)
def delete_rows_from_merge_tree_table(self, table_name, condition, node=None):
    """Delete rows from MergeTree table."""
    if node is None:
        node = self.context.node

    node.query(f"DELETE FROM {table_name} WHERE {condition}")


@TestStep(Given)
def get_random_value_from_table(self, table_name, column, number=1, node=None):
    """Get specified number of random values from a given column in a table."""
    if node is None:
        node = self.context.node

    output = []
    for _ in range(number):
        count = int(node.query(f"SELECT count(*) FROM {table_name}").output.strip())
        if count == 0:
            return None
        offset = random.randint(0, count - 1)
        result = self.context.node.query(
            f"SELECT {column} FROM {table_name} LIMIT 1 OFFSET {offset} FORMAT TabSeparated"
        )
        output.append(result.output.strip())

    return output[0] if number == 1 else output


def get_column_types(table_name):
    """Retrieve column types from using DESCRIBE TABLE query."""
    describe_query = f"DESCRIBE TABLE {table_name} FORMAT TabSeparated"
    describe_result = current().context.node.query(describe_query).output

    column_names_and_types = []
    for row in describe_result.strip().split("\n"):
        column_name, column_type = row.split("\t")[:2]
        column_names_and_types.append((column_name, column_type))

    return column_names_and_types


def parse_table_output(output, column_names_and_types):
    """Parses a tab-separated string output into a list of lists with appropriate types, ensuring correct column mapping."""
    rows = output.strip().split("\n")
    parsed_data = []

    for row in rows:
        values = row.split("\t")
        parsed_row = []
        for value, (_, col_type) in zip(values, column_names_and_types):
            if col_type.startswith("Float") or col_type.startswith("Nullable(Float"):
                try:
                    parsed_row.append(float(value))
                except ValueError:
                    parsed_row.append(value)
            elif (
                col_type.startswith("Int")
                or col_type.startswith("Nullable(Int")
                or col_type.startswith("UInt")
                or col_type.startswith("Nullable(UInt")
            ):
                try:
                    parsed_row.append(int(value))
                except ValueError:
                    parsed_row.append(value)
            else:
                parsed_row.append(value)
        parsed_data.append(parsed_row)

    return parsed_data


def compare_select_outputs(output1, output2, table_name1, rel_tol=1e-3, abs_tol=1e-3):
    """Compares two table outputs with math.isclose() only for float columns, ensuring correct column order."""

    column_names_and_types = get_column_types(table_name1)

    parsed_output1 = parse_table_output(output1, column_names_and_types)
    parsed_output2 = parse_table_output(output2, column_names_and_types)

    if len(parsed_output1) != len(parsed_output2):
        note(
            f"Row counts are not equal: {len(parsed_output1)} != {len(parsed_output2)}"
        )
        return False

    for row1, row2 in zip(parsed_output1, parsed_output2):
        if len(row1) != len(row2):
            note(row1)
            note(row2)
            note(f"Row lengths are not equal: {len(row1)} != {len(row2)}")
            return False

        for (val1, val2), (col_name, col_type) in zip(
            zip(row1, row2), column_names_and_types
        ):
            if col_type.startswith("Float") or col_type.startswith("Nullable(Float"):
                if not math.isclose(val1, val2, rel_tol=rel_tol, abs_tol=abs_tol):
                    note(
                        f"Float values are not close enough in column {col_name}: {val1} != {val2}"
                    )
                    return False
            elif val1 != val2:
                note(f"Values are not equal in column {col_name}: {val1} != {val2}")
                return False

    return True


@TestStep(Given)
def compare_iceberg_and_merge_tree_schemas(self, merge_tree_table_name, iceberg_table):
    """Compare schemas of MergeTree and Iceberg tables."""

    iceberg_clickhouse_type_mapping = {
        "Nullable(Int32)": "int",
        "Nullable(Int64)": "long",
        "Nullable(Float32)": "float",
        "Nullable(Float64)": "double",
        "Nullable(String)": "string",
        "Nullable(Date)": "date",
        "Nullable(Date32)": "date",
        "Nullable(Bool)": "boolean",
    }

    merge_tree_schema_query = self.context.node.query(
        f"DESCRIBE TABLE {merge_tree_table_name} FORMAT TabSeparated"
    ).output

    merge_tree_schema = {}
    for line in merge_tree_schema_query.strip().split("\n"):
        parts = line.split("\t")
        column_name = parts[0].strip()
        column_type = parts[1].strip()

        mapped_type = iceberg_clickhouse_type_mapping.get(column_type, column_type)
        merge_tree_schema[column_name] = mapped_type

    iceberg_schema = iceberg_table.schema()

    iceberg_columns = {
        field.name: str(field.field_type) for field in iceberg_schema.fields
    }

    note("ClickHouse MergeTree Schema (converted to Iceberg types):")
    note(merge_tree_schema)

    note("Iceberg Table Schema:")
    note(iceberg_columns)

    assert merge_tree_schema == iceberg_columns, error(
        "Schema mismatch between MergeTree and Iceberg tables!"
    )


@TestStep(Given)
def drop_all_caches(self, node=None):
    """Drop all caches. If node is not provided, drop caches in all nodes."""
    query = f"""
                SYSTEM DROP DNS CACHE;
                SYSTEM DROP CONNECTIONS CACHE;
                SYSTEM DROP MARK CACHE;
                SYSTEM DROP PRIMARY INDEX CACHE;
                SYSTEM DROP UNCOMPRESSED CACHE;
                SYSTEM DROP INDEX MARK CACHE;
                SYSTEM DROP INDEX UNCOMPRESSED CACHE;
                SYSTEM DROP MMAP CACHE;
                SYSTEM DROP QUERY CACHE;
                SYSTEM DROP COMPILED EXPRESSION CACHE;
                SYSTEM DROP FILESYSTEM CACHE;
                SYSTEM DROP PAGE CACHE;
                SYSTEM DROP SCHEMA CACHE;
                SYSTEM DROP FORMAT SCHEMA CACHE;
                SYSTEM DROP S3 CLIENT CACHE;
            """

    if check_if_antalya_build(self):
        query += "SYSTEM DROP PARQUET METADATA CACHE;"
        query += "SYSTEM DROP ICEBERG METADATA CACHE;"

    if check_clickhouse_version(">=25.3")(self):
        query += "SYSTEM DROP QUERY CONDITION CACHE;"

    if check_clickhouse_version(">=25.4")(self):
        query += "SYSTEM DROP VECTOR SIMILARITY INDEX CACHE;"
        query += "SYSTEM DROP ICEBERG METADATA CACHE;"

    if node:
        node.query(query)
    else:
        for node in self.context.nodes:
            node.query(query)
