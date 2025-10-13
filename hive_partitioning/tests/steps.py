from testflows.core import *
from testflows.asserts import error

duckdb_data_types = [
    ("BOOLEAN", True),
    ("TINYINT", 42),
    ("SMALLINT", 32767),
    ("INTEGER", 2147483647),
    ("BIGINT", 9223372036854775807),
    ("HUGEINT", 170141183460469231731687303715884105727),
    ("UTINYINT", 255),
    ("USMALLINT", 65535),
    ("UINTEGER", 4294967295),
    ("UBIGINT", 18446744073709551615),
    ("FLOAT", 3.14159),
    ("DOUBLE", 2.718281828459045),
    ("DECIMAL", 1234.56),
    ("VARCHAR", "'Hello, DuckDB!'"),
    ("CHAR(5)", "'ABC'"),
    ("BLOB", "'\\x1E\\x1D\\x1E\\x1F'"),
    ("UUID", "'123e4567-e89b-12d3-a456-426614174000'"),
    ("DATE", "'2023-12-31'"),
    ("TIME", "'23:59:59'"),
    ("TIMESTAMP", "'2023-12-31 23:59:59'"),
    ("TIMESTAMPTZ", "'2023-12-31 23:59:59+00'"),
    ("INT[]", [1, 2, 3]),
    ("STRUCT(name VARCHAR, age INT)", {"name": "Alice", "age": 30}),
    ("MAP(VARCHAR, INT)", "map(['a', 'b'], [1, 2])"),
    ("UNION(num INT, str VARCHAR)", 42),
    ("ENUM('RED', 'GREEN', 'BLUE')", "'GREEN'"),
]

all_types_example_values = [
    ("Int8", (-128, 127, 42)),
    ("Int16", (-32768, 32767, -1000)),
    ("Int32", (-2147483648, 2147483647, 2147483647)),
    ("Int64", (-9223372036854775808, 9223372036854775807, -9223372036854775808)),
    (
        "Int128",
        (
            -170141183460469231731687303715884105728,
            170141183460469231731687303715884105727,
            10,
        ),
    ),
    (
        "Int256",
        (
            -57896044618658097711785492504343953926634992332820282019728792003956564819968,
            57896044618658097711785492504343953926634992332820282019728792003956564819967,
            -10,
        ),
    ),
    ("UInt8", (0, 255, 255)),
    ("UInt16", (0, 65535, 65535)),
    ("UInt32", (0, 4294967295, 4294967295)),
    ("UInt64", (0, 18446744073709551615, 18446744073709551615)),
    ("UInt128", (0, 340282366920938463463374607431768211455, 10)),
    (
        "UInt256",
        (
            0,
            115792089237316195423570985008687907853269984665640564039457584007913129639935,
            10,
        ),
    ),
    ("Float32", (-3.4e38, 3.4e38, 3.14159)),
    ("Float64", (-1.8e308, 1.8e308, -2.718281828459045)),
    ("Decimal32(3)", (-999999, 999999, 999.999)),
    ("Decimal64(3)", (-999999999999999, 999999999999999, 1234567823456.78)),
    (
        "Decimal128(3)",
        (-99999999999999999999999999999999999, 99999999999999999999999999999999999, 10),
    ),
    (
        "Decimal256(3)",
        (
            -9999999999999999999999999999999999999999999999999999999999999999999999999,
            9999999999999999999999999999999999999999999999999999999999999999999999999,
            10,
        ),
    ),
    ("String", ("''", f"""'{"A"*200}'""", "'Hello, ClickHouse'")),
    ("FixedString(10)", ("\x00" * 10, "\xff" * 10, "ABC\x00\x00")),
    ("Date", ("'1970-01-01'", "'2149-06-06'", "'2023-12-31'")),
    ("Date32", ("'1900-01-01'", "'2299-12-31'", "'2299-12-31'")),
    (
        "DateTime",
        ("'1970-01-01 00:00:00'", "'2106-02-07 06:28:15'", "'2025-06-09 14:30:00'"),
    ),
    (
        "DateTime64(3)",
        (
            "'1900-01-01 00:00:00'",
            "'2299-12-31 23:59:59.999'",
            "'2025-06-09 14:30:00.123'",
        ),
    ),
    (
        "UUID",
        (
            "'00000000-0000-0000-0000-000000000000'",
            "'ffffffff-ffff-ffff-ffff-ffffffffffff'",
            "'550e8400-e29b-41d4-a716-446655440000'",
        ),
    ),
    ("IPv4", ("'0.0.0.0'", "'255.255.255.255'", "'192.168.1.1'")),
    (
        "IPv6",
        (
            "'::'",
            "'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'",
            "'2001:0db8:85a3::8a2e:0370:7334'",
        ),
    ),
    ("Bool", (False, True, True)),
    (
        "Enum8('MIN_ENUM_VALUE', 'MAX_ENUM_VALUE', 'RED')",
        ("'MIN_ENUM_VALUE'", "'MAX_ENUM_VALUE'", "'RED'"),
    ),
    (
        "Enum16('MIN_ENUM_VALUE', 'MAX_ENUM_VALUE', 'LARGE')",
        ("'MIN_ENUM_VALUE'", "'MAX_ENUM_VALUE'", "'LARGE'"),
    ),
    ("Array(Int32)", ([], [1] * 100, [1, 2, 3])),
    ("Tuple(Int32, String)", ((0, ""), (999999, "Z"), (1, "a"))),
    ("Nested(x Int32, y Int32)", ([0, 0], [999999, 999999], [1, 2])),
    ("JSON", ({}, {"max_key": "max_value", "nested": {"a": 1}}, {"key": "value"})),
    (
        "Map(String, Int32)",
        ({}, {"k1": 1, "k2": 2, "k1000": 1000}, {"key1": 1, "key2": 2}),
    ),
    ("Nullable(Int)", (None, 2147483647, 42)),
    ("AggregateFunction(...)", ("min_state", "max_state", "example_state")),
    ("SimpleAggregateFunction(...)", ("min_state", "max_state", "example_state")),
    ("Nothing", ("N/A", "N/A", "N/A")),
    ("Interval", ("INTERVAL 1 SECOND", "INTERVAL 100 YEAR", "INTERVAL 1 DAY")),
    ("Point", ((0.0, 0.0), (999999.999, 999999.999), (10.5, 20.0))),
    (
        "Ring",
        (
            [(0.0, 0.0)],
            [
                (999999.999, 999999.999),
                (999999.999, 0.0),
                (0.0, 999999.999),
                (0.0, 0.0),
            ],
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)],
        ),
    ),
    (
        "Polygon",
        (
            [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]],
            [[(999999, 0), (999999, 999999), (0, 999999), (0, 0)]],
            [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
        ),
    ),
    ("Object('json')", ({}, {"max_depth": {"a": {"b": {"c": 1}}}}, {"temp": 25.5})),
]


supported_types_example_values = [
    ("Bool", (False, True, True)),
    ("Int8", (-128, 127, 42)),
    ("Int16", (-32768, 32767, -1000)),
    ("Int32", (-2147483648, 2147483647, 2147483647)),
    ("Int64", (-9223372036854775808, 9223372036854775807, -9223372036854775808)),
    (
        "Int128",
        (
            "'-170141183460469231731687303715884105728'",
            "'170141183460469231731687303715884105727'",
            "'10'",
        ),
    ),
    (
        "Int256",
        (
            "'-57896044618658097711785492504343953926634992332820282019728792003956564819968'",
            "'57896044618658097711785492504343953926634992332820282019728792003956564819967'",
            "'-10'",
        ),
    ),
    ("UInt8", (0, 255, 255)),
    ("UInt16", (0, 65535, 65535)),
    ("UInt32", (0, 4294967295, 4294967295)),
    ("UInt64", (0, 18446744073709551615, 18446744073709551615)),
    ("UInt128", ("'0'", "'340282366920938463463374607431768211455'", "'10'")),
    (
        "UInt256",
        (
            "'0'",
            "'115792089237316195423570985008687907853269984665640564039457584007913129639935'",
            "'10'",
        ),
    ),
    ("String", ("''", f"""'{"A"*200}'""", "'Hello, ClickHouse'")),
    ("FixedString(10)", ("''", f"""'{"Z"*10}'""", "'ABC'")),
    ("Date", ("'1970-01-01'", "'2149-06-06'", "'2023-12-31'")),
    (
        "DateTime",
        ("'1970-01-01 00:00:00'", "'2106-02-07 06:28:15'", "'2025-06-09 14:30:00'"),
    ),
    (
        "DateTime64",
        ("'1970-01-01 00:00:00'", "'2106-02-07 06:28:15'", "'2025-06-09 14:30:00'"),
    ),
    ("Date32", ("'1900-01-01'", "'2299-12-31'", "'2299-12-31'")),
    (
        "DateTime64(3)",
        (
            "'1900-01-01 00:00:00'",
            "'2299-12-31 23:59:59.999'",
            "'2025-06-09 14:30:00.123'",
        ),
    ),
    ("Time", ("'00:00:00'", "'23:59:59'", "'14:30:00'")),
    ("Time64(3)", ("'00:00:00'", "'23:59:59.999'", "'14:30:00.123'")),
]

unsupported_types_example_values = [
    # ("Nested(x Int32, y Int32)", ([0, 0], [999999, 999999], [1, 2])),
    ("JSON", ({}, {"max_key": "max_value", "nested": {"a": 1}}, {"key": "value"})),
    (
        "Map(String, Int32)",
        ({}, {"k1": 1, "k2": 2, "k1000": 1000}, {"key1": 1, "key2": 2}),
    ),
    ("Nullable(Int)", (None, None, None)),
    ("Object('json')", ({}, {"max_depth": {"a": {"b": {"c": 1}}}}, {"temp": 25.5})),
    ("Float32", ("'-3.4e38'", "'3.4e38'", "'3.14159'")),
    ("Float64", ("'-1.8e308'", "'1.8e308'", "'-2.718281828459045'")),
    ("Decimal32(3)", (-999999, 999999, 999.999)),
    ("Decimal64(3)", (-999999999999999, 999999999999999, 1234567823456.78)),
    (
        "Decimal128(3)",
        (-99999999999999999999999999999999999, 99999999999999999999999999999999999, 10),
    ),
    (
        "Decimal256(3)",
        (
            -9999999999999999999999999999999999999999999999999999999999999999999999999,
            9999999999999999999999999999999999999999999999999999999999999999999999999,
            10,
        ),
    ),
    (
        "UUID",
        (
            "'00000000-0000-0000-0000-000000000000'",
            "'ffffffff-ffff-ffff-ffff-ffffffffffff'",
            "'550e8400-e29b-41d4-a716-446655440000'",
        ),
    ),
    ("IPv4", ("'0.0.0.0'", "'255.255.255.255'", "'192.168.1.1'")),
    (
        "IPv6",
        (
            "'::'",
            "'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'",
            "'2001:0db8:85a3::8a2e:0370:7334'",
        ),
    ),
    (
        "Enum8('MIN_ENUM_VALUE', 'MAX_ENUM_VALUE', 'RED')",
        ("'MIN_ENUM_VALUE'", "'MAX_ENUM_VALUE'", "'RED'"),
    ),
    (
        "Enum16('MIN_ENUM_VALUE', 'MAX_ENUM_VALUE', 'LARGE')",
        ("'MIN_ENUM_VALUE'", "'MAX_ENUM_VALUE'", "'LARGE'"),
    ),
    ("Array(Int32)", ([], [1] * 100, [1, 2, 3])),
    ("Tuple(Int32, String)", ((0, ""), (999999, "Z"), (1, "a"))),
    ("Point", ((0.0, 0.0), (999999.999, 999999.999), (10.5, 20.0))),
    (
        "Ring",
        (
            [(0.0, 0.0)],
            [
                (999999.999, 999999.999),
                (999999.999, 0.0),
                (0.0, 999999.999),
                (0.0, 0.0),
            ],
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)],
        ),
    ),
    (
        "Polygon",
        (
            [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]],
            [[(999999, 0), (999999, 999999), (0, 999999), (0, 0)]],
            [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
        ),
    ),
    ("Dynamic", ("'Hello, ClickHouse'", "'Hello, ClickHouse'", "'Hello, ClickHouse'")),
]


@TestStep(Given)
def create_table(
    self,
    table_name=None,
    engine=None,
    partition_by=None,
    columns="d Int64",
    settings=None,
    modify=False,
    node=None,
    exitcode=None,
    message=None,
):
    """Create table."""
    if node is None:
        node = self.context.node

    if engine is None:
        engine = "MergeTree"

    if partition_by is None:
        partition_by = ""

    else:
        partition_by = f"PARTITION BY {partition_by}"

    if settings is None:
        settings = {}

    if table_name is None:
        table_name = "table_" + getuid()

    try:
        with Given(f"I create table {table_name}"):
            r = node.query(
                f"CREATE TABLE {table_name} ({columns}) ENGINE = {engine} {partition_by}",
                settings=settings,
                exitcode=exitcode,
                message=message,
                no_checks=True,
            )
            if exitcode is not None:
                assert r.exitcode == exitcode, error()
            if message is not None:
                assert message in r.output, error()

        yield r

    finally:
        if not modify:
            with Finally(f"I drop table {table_name}"):
                node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(When)
def insert_into_bucket_s3_funtion(
    self, bucket_path, values, type, compression_method, structure, settings, node=None
):
    """Insert into bucket using s3 function."""

    if node is None:
        node = self.context.node

    with When(f"I insert into bucket {bucket_path} using s3 function"):
        node.query(
            f"INSERT INTO s3('{bucket_path}', '{type}', '{compression_method}', '{structure}') VALUES {values}",
            settings=settings,
        )


@TestStep(When)
def insert_into_bucket_s3_function_from_table(
    self, bucket_path, type, compression_method, structure, settings, node=None
):
    """Insert into bucket using s3 function from table."""

    if node is None:
        node = self.context.node

    with When(f"I insert into bucket {bucket_path} using s3 function from table"):
        node.query(
            f"INSERT INTO s3('{bucket_path}', '{type}', '{compression_method}', '{structure}') FROM {table_name}",
            settings=settings,
        )


@TestStep(When)
def insert_into_table_values(
    self, table_name, values, settings=None, node=None, exitcode=None, message=None
):
    """Insert into table values."""

    if node is None:
        node = self.context.node

    with When(f"I insert into table {table_name} values"):
        return node.query(
            f"INSERT INTO {table_name} VALUES {values}",
            settings=settings,
            exitcode=exitcode,
            message=message,
            no_checks=True,
        )


@TestStep(When)
def insert_into_table_select(
    self, table_name, select_statement, settings=None, node=None, no_checks=False
):
    """Insert into table values from select statement."""

    if node is None:
        node = self.context.node

    with When(f"I insert into table {table_name} values"):
        return node.query(
            f"INSERT INTO {table_name} SELECT {select_statement}",
            settings=settings,
            no_checks=no_checks,
        )


@TestStep(When)
def check_select(
    self, select, query_id=None, settings=None, expected_result=None, node=None
):
    """Check select statement."""

    if node is None:
        node = self.context.node

    with When(f"I check select statement"):
        r = node.query(f"{select}", query_id=query_id, settings=settings)
        if expected_result is not None:
            assert r.output == expected_result, error()


@TestStep(When)
def get_value_from_query_log(self, query_id, column_name, node=None):
    """Get value from query log."""

    if node is None:
        node = self.context.node

    with Then(f"I get {column_name} from system.query_log table"):
        r = node.query(
            f"SELECT {column_name} FROM system.query_log WHERE query_id = '{query_id}'"
        )
        return r.output


@TestStep(When)
def get_bucket_files_list(self, filename="", node=None):
    """Get bucket files list."""

    if node is None:
        node = self.context.node

    with Then(f"I get bucket files list"):
        r = self.context.cluster.command(
            None,
            f"docker exec -it hive_partitioning_env-minio1-1 sh -c 'ls data1-1/root/data/{filename} --recursive'",
            exitcode=0,
        )
        return r.output


@TestStep(When)
def get_bucket_file_size(self, filename, node=None):
    """Get bucket file size."""

    if node is None:
        node = self.context.node

    with Then(f"I get bucket file size"):
        r = self.context.cluster.command(
            None,
            f"docker exec -it hive_partitioning_env-minio1-1 sh -c 'du -s data1-1/root/data/{filename}'",
            exitcode=0,
        )
        return int(r.output.split("\t")[0])


@TestStep(Then)
def get_bucket_file(self, file_path, node=None):
    """Get bucket file."""

    if node is None:
        node = self.context.node

    with Then(f"I get bucket file"):
        r = self.context.cluster.command(
            None,
            f"docker exec -it hive_partitioning_env-minio1-1 sh -c 'cat {file_path}'",
            exitcode=0,
        )
        return r.output


def replace_ascii_characters(string):
    if ord(string[0]) >= 128:
        return string
    else:
        new_string = ""
        for i in string:
            new_string += f"\\\\x{hex(ord(i))[2:]}"
        return new_string


def remove_unsupported_character(string, not_supported_characters):
    for i in not_supported_characters:
        if i in string:
            string = string.replace(i, "")

    return string
