"""Map Delta log types to ClickHouse types.

Each scenario writes one table with ``deltalake`` and registers that log
schema in Unity. ``deltaLake()`` and the catalog, with
``use_unity_catalog_v2`` off, must return the same rows. ``SHOW CREATE``
on the catalog table uses the ClickHouse type. On 26.10 and newer the
catalog read is repeated with the v2 flag.

``timestamp_ntz`` and ``void`` are not in this module. Both need a table
feature this writer path does not turn on.
"""

import json
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

import pyarrow as pa
import requests
from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version
from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_Decimal,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_Nested,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_Nulls,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_PrimitiveTypes,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_Unsupported,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_Varchar,
)
from delta_lake.tests.steps import (
    column,
    commit_delta_table,
    create_database,
    create_delta_table,
    get_object,
    list_keys,
    put_object,
    register_delta_table,
)
from delta_lake.tests.steps.access import function_call
from delta_lake.tests.steps.catalog import UC_CATALOG, UC_URL

VIRTUAL_COLUMNS = {"_path", "_file", "_size", "_time", "_etag"}

# Length that used to throw on the catalog path: Unsupported DeltaLake type: varchar(256).
LONG_VARCHAR = "a" * 300

INTEGER_TYPES = [
    ("text", "String"),
    ("long_value", "Int64"),
    ("int_value", "Int32"),
    ("short_value", "Int16"),
    ("byte_value", "Int8"),
]

FLOAT_TYPES = [
    ("f", "Float32"),
    ("d", "Float64"),
    ("flag", "Bool"),
]

TEMPORAL_TYPES = [
    ("day", "Date32"),
    ("ts", "DateTime64(6)"),
]

# Precision boundaries for the three Parquet decimal layouts, plus scale 0 and scale = precision.
# decimal(1,0) and decimal(9,2) are INT32. decimal(10,2) and decimal(18,0) are INT64.
# decimal(19,1), decimal(38,10), decimal(38,0), and decimal(38,38) are fixed bytes.
DECIMAL_FIELDS = (
    ("d1", 1, 0),
    ("d9", 9, 2),
    ("d10", 10, 2),
    ("d18", 18, 0),
    ("d19", 19, 1),
    ("d38", 38, 10),
    ("d380", 38, 0),
    ("d3838", 38, 38),
)

DECIMAL_ROWS = (
    (
        "-9",
        "-9999999.99",
        "-99999999.99",
        "-999999999999999999",
        "-999999999999999999.9",
        "-9999999999999999999999999999.9999999999",
        "-99999999999999999999999999999999999999",
        "-0.99999999999999999999999999999999999999",
    ),
    (
        "9",
        "9999999.99",
        "99999999.99",
        "999999999999999999",
        "999999999999999999.9",
        "9999999999999999999999999999.9999999999",
        "99999999999999999999999999999999999999",
        "0.99999999999999999999999999999999999999",
    ),
)

DECIMAL_TYPES = [
    (name, f"Decimal({precision}, {scale})")
    for name, precision, scale in DECIMAL_FIELDS
]

NESTED_TYPES = [
    (
        "person",
        "Tuple(id Int64, name Nullable(String), inner Tuple(flag Bool))",
    ),
    ("nums", "Array(Nullable(Int32))"),
    ("nums_nn", "Array(Int32)"),
    ("kv", "Map(String, Nullable(Int64))"),
    ("kv_nn", "Map(String, Int64)"),
    (
        "nested",
        "Tuple(tags Array(Nullable(String)), attrs Map(String, Nullable(Int32)))",
    ),
]

VARCHAR_TYPES = [
    ("v1", "String"),
    ("v32", "String"),
    ("v256", "String"),
    ("c1", "String"),
    ("c10", "String"),
]

VARCHAR_OVERRIDES = {
    "v1": "varchar(1)",
    "v32": "varchar(32)",
    "v256": "varchar(256)",
    "c1": "char(1)",
    "c10": "char(10)",
}


def norm(text):
    return "".join(text.split())


def delta_source(table, access_key, secret_key):
    """``deltaLake(url, key, secret)`` with format and structure omitted."""
    return function_call("deltaLake", table.http_url, access_key, secret_key)


def unity_type_name(delta_type):
    if isinstance(delta_type, dict):
        return {"struct": "STRUCT", "array": "ARRAY", "map": "MAP"}[delta_type["type"]]
    if delta_type.startswith("decimal("):
        return "DECIMAL"
    if delta_type.startswith("varchar(") or delta_type.startswith("char("):
        return "STRING"
    return {
        "string": "STRING",
        "long": "LONG",
        "integer": "INT",
        "short": "SHORT",
        "byte": "BYTE",
        "float": "FLOAT",
        "double": "DOUBLE",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "timestamp": "TIMESTAMP",
        "binary": "BINARY",
        "variant": "STRING",
    }[delta_type]


def decimal_precision_scale(delta_type):
    if not isinstance(delta_type, str) or not delta_type.startswith("decimal("):
        return 0, 0
    precision, scale = delta_type[len("decimal(") : -1].split(",")
    return int(precision), int(scale)


def columns_from_fields(fields):
    columns = []
    for field in fields:
        delta_type = field["type"]
        precision, scale = decimal_precision_scale(delta_type)
        type_text = delta_type if isinstance(delta_type, str) else delta_type["type"]
        columns.append(
            column(
                field["name"],
                unity_type_name(delta_type),
                type_text,
                delta_type,
                nullable=field.get("nullable", True),
                precision=precision,
                scale=scale,
                type_json=json.dumps(field, separators=(",", ":")),
            )
        )
    return columns


def log_fields(self, table):
    """Fields from the latest metadata action in the Delta log."""
    prefix = f"{table.prefix}/_delta_log/"
    fields = None
    for key in list_keys(prefix=prefix):
        if not key.endswith(".json"):
            continue
        for line in get_object(key=key).splitlines():
            if not line:
                continue
            metadata = json.loads(line).get("metaData")
            if metadata and "schemaString" in metadata:
                fields = json.loads(metadata["schemaString"])["fields"]
    assert fields is not None, error(f"no schema in {prefix}")
    return fields


def write_table(self, data):
    """Write an Arrow table and leave Unity registration to the caller."""
    return create_delta_table(columns=(), data=data, register=False)


def register_log(self, table, type_overrides=None):
    """Register the log schema. ``type_overrides`` replaces catalog type names."""
    overrides = type_overrides or {}
    fields = []
    for field in log_fields(self, table):
        field = deepcopy(field)
        if field["name"] in overrides:
            field["type"] = overrides[field["name"]]
        fields.append(field)
    return register_delta_table(table=table, columns=columns_from_fields(fields))


def stored_type_json(table, name):
    response = requests.get(
        f"{UC_URL}/tables/{UC_CATALOG}.{table.namespace}.{table.name}",
        timeout=30,
    )
    response.raise_for_status()
    for spec in response.json()["columns"]:
        if spec["name"] == name:
            return spec.get("type_json") or spec.get("typeJson") or ""
    raise AssertionError(f"column {name} is not registered")


def set_log_type(self, table, column_name, delta_type):
    """Replace one field type in the log. The Parquet file stays as written."""
    prefix = f"{table.prefix}/_delta_log/"
    changed = False
    for key in list_keys(prefix=prefix):
        if not key.endswith(".json"):
            continue
        lines = []
        file_changed = False
        for line in get_object(key=key).splitlines():
            if not line:
                continue
            action = json.loads(line)
            metadata = action.get("metaData")
            if metadata and "schemaString" in metadata:
                schema = json.loads(metadata["schemaString"])
                for field in schema["fields"]:
                    if field["name"] == column_name:
                        field["type"] = delta_type
                        file_changed = True
                metadata["schemaString"] = json.dumps(schema)
            lines.append(json.dumps(action))
        if file_changed:
            put_object(key=key, body=("\n".join(lines) + "\n").encode())
            changed = True
    assert changed, error(f"no field {column_name} under {prefix}")


def column_types(node, source):
    result = node.query(f"DESCRIBE TABLE {source} FORMAT JSONEachRow")
    found = []
    for line in result.output.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        row = json.loads(line)
        if row["name"] in VIRTUAL_COLUMNS:
            continue
        found.append((row["name"], norm(row["type"])))
    return found


def assert_types(node, source, expected):
    found = column_types(node, source)
    wanted = [(name, norm(type_name)) for name, type_name in expected]
    assert found == wanted, error(f"{found}\n!=\n{wanted}")


def assert_show_create(node, database, table, expected):
    result = node.query(f"SHOW CREATE TABLE {database}.{table.identifier}")
    show = norm(result.output)
    for name, type_name in expected:
        token = norm(f"`{name}`{type_name}")
        assert token in show, error(result.output)


def select_lines(node, source, selected, order_by):
    order = f" ORDER BY {order_by}" if order_by else ""
    result = node.query(
        f"SELECT {selected} FROM {source}{order} FORMAT TabSeparated"
    )
    return result.output.splitlines()


def assert_catalog(node, database, table, selected, order_by, expected_lines, expected_types):
    catalog = f"{database}.{table.identifier}"
    assert_show_create(node, database, table, expected_types)
    assert_types(node, catalog, expected_types)
    catalog_rows = select_lines(node, catalog, selected, order_by)
    assert catalog_rows == expected_lines, error(catalog_rows)


def check_readers(self, table, selected, order_by, expected_lines, expected_types):
    """Read through ``deltaLake()``, Unity, and Unity v2 on 26.10 and newer."""
    node = self.context.node
    source = delta_source(
        table,
        self.context.rustfs_access_key,
        self.context.rustfs_secret_key,
    )

    with When("deltaLake reads the log schema"):
        assert_types(node, source, expected_types)
        function_rows = select_lines(node, source, selected, order_by)
        assert function_rows == expected_lines, error(function_rows)

    with When("Unity without use_unity_catalog_v2 reads the same types"):
        database = create_database(unity_v2=False)
        assert_catalog(
            node, database, table, selected, order_by, expected_lines, expected_types
        )

    if check_clickhouse_version(">=26.10")(self):
        with When("Unity v2 reports the same types"):
            database = create_database(unity_v2=True)
            assert_catalog(
                node,
                database,
                table,
                selected,
                order_by,
                expected_lines,
                expected_types,
            )


def integer_table():
    schema = pa.schema(
        [
            pa.field("text", pa.string(), nullable=False),
            pa.field("long_value", pa.int64(), nullable=False),
            pa.field("int_value", pa.int32(), nullable=False),
            pa.field("short_value", pa.int16(), nullable=False),
            pa.field("byte_value", pa.int8(), nullable=False),
        ]
    )
    return pa.table(
        {
            "text": ["", "mid", "top"],
            "long_value": [-9223372036854775808, 0, 9223372036854775807],
            "int_value": [-2147483648, 0, 2147483647],
            "short_value": [-32768, 0, 32767],
            "byte_value": [-128, 0, 127],
        },
        schema=schema,
    )


def float_table():
    schema = pa.schema(
        [
            pa.field("f", pa.float32(), nullable=False),
            pa.field("d", pa.float64(), nullable=False),
            pa.field("flag", pa.bool_(), nullable=False),
        ]
    )
    return pa.table(
        {
            "f": pa.array([-1.25, 0.0, 0.5], pa.float32()),
            "d": pa.array([-1.25, 0.0, 0.5], pa.float64()),
            "flag": [False, False, True],
        },
        schema=schema,
    )


def temporal_table():
    schema = pa.schema(
        [
            pa.field("day", pa.date32(), nullable=False),
            pa.field("ts", pa.timestamp("us", tz="UTC"), nullable=False),
        ]
    )
    return pa.table(
        {
            "day": [
                datetime(1969, 12, 31, tzinfo=timezone.utc).date(),
                datetime(1970, 1, 1, tzinfo=timezone.utc).date(),
                datetime(2024, 2, 29, tzinfo=timezone.utc).date(),
            ],
            "ts": [
                datetime(1969, 12, 31, 23, 59, 59, 1, tzinfo=timezone.utc),
                datetime(1970, 1, 1, tzinfo=timezone.utc),
                datetime(2020, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc),
            ],
        },
        schema=schema,
    )


def decimal_table():
    schema = pa.schema(
        [
            pa.field(name, pa.decimal128(precision, scale), nullable=False)
            for name, precision, scale in DECIMAL_FIELDS
        ]
    )
    names = [name for name, _, _ in DECIMAL_FIELDS]
    rows = [
        {name: Decimal(text) for name, text in zip(names, texts)}
        for texts in DECIMAL_ROWS
    ]
    return pa.Table.from_pylist(rows, schema=schema)


def binary_table():
    schema = pa.schema([pa.field("bin", pa.binary(), nullable=False)])
    return pa.table(
        {"bin": pa.array([b"", b"\x00", b"a\x00b", b"\xff\xfe"], pa.binary())},
        schema=schema,
    )


def nullable_long_table():
    schema = pa.schema([pa.field("n", pa.int64(), nullable=True)])
    return pa.table({"n": pa.array([42, None], pa.int64())}, schema=schema)


def missing_column_tables():
    first = pa.schema([pa.field("present", pa.int64(), nullable=True)])
    second = pa.schema(
        [
            pa.field("present", pa.int64(), nullable=True),
            pa.field("added", pa.int64(), nullable=True),
        ]
    )
    original = pa.table({"present": pa.array([10, 20], pa.int64())}, schema=first)
    added = pa.table(
        {
            "present": pa.array([30], pa.int64()),
            "added": pa.array([7], pa.int64()),
        },
        schema=second,
    )
    return original, added


def nested_table():
    person = pa.struct(
        [
            pa.field("id", pa.int64(), nullable=False),
            pa.field("name", pa.string(), nullable=True),
            pa.field(
                "inner",
                pa.struct([pa.field("flag", pa.bool_(), nullable=False)]),
                nullable=False,
            ),
        ]
    )
    nested = pa.struct(
        [
            pa.field(
                "tags",
                pa.list_(pa.field("item", pa.string(), nullable=True)),
                nullable=False,
            ),
            pa.field(
                "attrs",
                pa.map_(pa.string(), pa.field("value", pa.int32(), nullable=True)),
                nullable=False,
            ),
        ]
    )
    schema = pa.schema(
        [
            pa.field("person", person, nullable=False),
            pa.field(
                "nums",
                pa.list_(pa.field("item", pa.int32(), nullable=True)),
                nullable=False,
            ),
            pa.field(
                "nums_nn",
                pa.list_(pa.field("item", pa.int32(), nullable=False)),
                nullable=False,
            ),
            pa.field(
                "kv",
                pa.map_(pa.string(), pa.field("value", pa.int64(), nullable=True)),
                nullable=False,
            ),
            pa.field(
                "kv_nn",
                pa.map_(pa.string(), pa.field("value", pa.int64(), nullable=False)),
                nullable=False,
            ),
            pa.field("nested", nested, nullable=False),
        ]
    )
    return pa.Table.from_pylist(
        [
            {
                "person": {"id": 1, "name": "a", "inner": {"flag": True}},
                "nums": [1, None, -2],
                "nums_nn": [1, 2],
                "kv": [("k", 1), ("z", None)],
                "kv_nn": [("a", -5)],
                "nested": {"tags": ["x", None], "attrs": [("n", 1), ("m", None)]},
            },
            {
                "person": {"id": 2, "name": None, "inner": {"flag": False}},
                "nums": [],
                "nums_nn": [],
                "kv": [],
                "kv_nn": [],
                "nested": {"tags": [], "attrs": []},
            },
        ],
        schema=schema,
    )


def varchar_table():
    schema = pa.schema(
        [
            pa.field("v1", pa.string(), nullable=False),
            pa.field("v32", pa.string(), nullable=False),
            pa.field("v256", pa.string(), nullable=False),
            pa.field("c1", pa.string(), nullable=False),
            pa.field("c10", pa.string(), nullable=False),
        ]
    )
    return pa.table(
        {
            "v1": ["hello", ""],
            "v32": ["short", ""],
            "v256": [LONG_VARCHAR, ""],
            "c1": ["YZ", ""],
            "c10": ["hi", ""],
        },
        schema=schema,
    )


def variant_table():
    schema = pa.schema([pa.field("label", pa.string(), nullable=False)])
    return pa.table({"label": ["should-not-return"]}, schema=schema)


@TestScenario
@Name("integers")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_PrimitiveTypes("1.0"))
def integers(self):
    """Map non-nullable string, long, integer, short, and byte.

    The string is empty and then non-empty. Each integer is its minimum,
    zero, and its maximum.
    """
    with Given("a Delta table of string and integer limits"):
        table = write_table(self, integer_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="text, long_value, int_value, short_value, byte_value",
        order_by="text",
        expected_lines=[
            "\t-9223372036854775808\t-2147483648\t-32768\t-128",
            "mid\t0\t0\t0\t0",
            "top\t9223372036854775807\t2147483647\t32767\t127",
        ],
        expected_types=INTEGER_TYPES,
    )


@TestScenario
@Name("floats")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_PrimitiveTypes("1.0"))
def floats(self):
    """Map non-nullable float, double, and boolean.

    The numbers are zero, a positive fraction, and a negative fraction.
    The booleans are true and false.
    """
    with Given("a Delta table of float, double, and boolean"):
        table = write_table(self, float_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="f, d, flag",
        order_by="f",
        expected_lines=[
            "-1.25\t-1.25\tfalse",
            "0\t0\tfalse",
            "0.5\t0.5\ttrue",
        ],
        expected_types=FLOAT_TYPES,
    )


@TestScenario
@Name("date and timestamp")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_PrimitiveTypes("1.0"))
def date_and_timestamp(self):
    """Map non-nullable date and timestamp.

    Dates are the day before the epoch, the epoch, and a leap day.
    Timestamps are one microsecond before the epoch, the epoch, and
    2020-01-02 03:04:05.123456 UTC. The comparison is the UTC instant.
    """
    with Given("a Delta table of date and timestamp"):
        table = write_table(self, temporal_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="toString(day), toUnixTimestamp64Micro(ts)",
        order_by="day",
        expected_lines=[
            "1969-12-31\t-999999",
            "1970-01-01\t0",
            "2024-02-29\t1577934245123456",
        ],
        expected_types=TEMPORAL_TYPES,
    )


@TestScenario
@Name("decimal")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_Decimal("1.0"))
def decimals(self):
    """Map decimal(p, s) at the precision and scale boundaries.

    Each column holds its negative full value and its positive full value.
    """
    with Given("a Delta table of decimal columns"):
        table = write_table(self, decimal_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    selected = ", ".join(name for name, _, _ in DECIMAL_FIELDS)
    check_readers(
        self,
        table,
        selected=selected,
        order_by="d1",
        expected_lines=["\t".join(row) for row in DECIMAL_ROWS],
        expected_types=DECIMAL_TYPES,
    )


@TestScenario
@Name("binary")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_PrimitiveTypes("1.0"))
def binary(self):
    """Map non-nullable binary to String.

    The values are empty, a zero byte, a zero byte between letters, and
    bytes above 127.
    """
    with Given("a Delta table of binary values"):
        table = write_table(self, binary_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="hex(bin)",
        order_by="hex(bin)",
        expected_lines=["", "00", "610062", "FFFE"],
        expected_types=[("bin", "String")],
    )


@TestScenario
@Name("nulls")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_Nulls("1.0"))
def nulls(self):
    """A nullable long is Nullable(Int64) and returns NULL.

    A column added in a later commit is NULL on rows whose file does not
    store that column.
    """
    with Given("a nullable long with one value and one null"):
        table = write_table(self, nullable_long_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="n",
        order_by="n NULLS LAST",
        expected_lines=["42", "\\N"],
        expected_types=[("n", "Nullable(Int64)")],
    )

    with Given("a file written before the added column existed"):
        original, added = missing_column_tables()
        evolved = write_table(self, original)
        commit_delta_table(table=evolved, data=added, schema_mode="merge")

    with And("Unity registration of the evolved log"):
        register_log(self, evolved)

    check_readers(
        self,
        evolved,
        selected="present, added",
        order_by="present",
        expected_lines=["10\t\\N", "20\t\\N", "30\t7"],
        expected_types=[
            ("present", "Nullable(Int64)"),
            ("added", "Nullable(Int64)"),
        ],
    )


@TestScenario
@Name("nested")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_Nested("1.0"))
def nested(self):
    """Map struct, array, and map, including one level of nesting.

    Array elements are Nullable when containsNull is true, and not when it
    is false. Map values follow valueContainsNull. Map keys stay non-nullable.
    A struct keeps field names and the nullability of each field.
    """
    with Given("a Delta table of struct, array, and map columns"):
        table = write_table(self, nested_table())

    with And("Unity registration taken from the log"):
        register_log(self, table)

    check_readers(
        self,
        table,
        selected="person, nums, nums_nn, kv, kv_nn, nested",
        order_by="person.id",
        expected_lines=[
            "(1,'a',(true))\t[1,NULL,-2]\t[1,2]\t{'k':1,'z':NULL}\t{'a':-5}\t(['x',NULL],{'n':1,'m':NULL})",
            "(2,NULL,(false))\t[]\t[]\t{}\t{}\t([],{})",
        ],
        expected_types=NESTED_TYPES,
    )


@TestScenario
@Name("varchar")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_Varchar("1.0"))
def varchar(self):
    """Unity calls a string column varchar(n) or char(n). ClickHouse reads String.

    The log type stays string. Lengths are 1, 32, and 256 for varchar, and
    1 and 10 for char. Values are shorter than the length, longer than it,
    and empty. The length does not pad or truncate them.
    """
    with Given("a Delta table whose log type is string"):
        table = write_table(self, varchar_table())

    with And("Unity type_json names varchar and char"):
        register_log(self, table, type_overrides=VARCHAR_OVERRIDES)

    with Then("the catalog stored those type names"):
        for name, delta_type in VARCHAR_OVERRIDES.items():
            stored = stored_type_json(table, name)
            assert delta_type in stored, error(stored)

    check_readers(
        self,
        table,
        selected="v1, v32, v256, c1, c10",
        order_by="v32",
        expected_lines=[
            "\t\t\t\t",
            f"hello\tshort\t{LONG_VARCHAR}\tYZ\thi",
        ],
        expected_types=VARCHAR_TYPES,
    )


@TestScenario
@Name("variant")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_Unsupported("1.0"))
def variant(self):
    """A log type of variant fails the read and the error names variant.

    The Parquet file is still a string. No row from that file comes back.
    """
    node = self.context.node

    with Given("a string table whose log type was rewritten to variant"):
        table = write_table(self, variant_table())
        set_log_type(self, table, "label", "variant")

    with And("Unity registration of that log type"):
        register_log(self, table)

    source = delta_source(
        table,
        self.context.rustfs_access_key,
        self.context.rustfs_secret_key,
    )
    readers = [source]

    with When("Unity without use_unity_catalog_v2 is opened"):
        database = create_database(unity_v2=False)
        readers.append(f"{database}.{table.identifier}")

    if check_clickhouse_version(">=26.10")(self):
        with And("Unity v2 is opened"):
            database = create_database(unity_v2=True)
            readers.append(f"{database}.{table.identifier}")

    for source in readers:
        with Then(f"the read of {source} fails and names variant"):
            result = node.query(
                f"SELECT label FROM {source} FORMAT TabSeparated",
                no_checks=True,
                retry_count=0,
            )
            assert result.exitcode != 0, error(result.output)
            assert "variant" in result.output.lower(), error(result.output)
            assert "should-not-return" not in result.output, error(result.output)


@TestFeature
@Name("delta schema")
def feature(self):
    """Delta Lake type mapping through deltaLake() and Unity."""
    Scenario(test=integers)()
    Scenario(test=floats)()
    Scenario(test=date_and_timestamp)()
    Scenario(test=decimals)()
    Scenario(test=binary)()
    Scenario(test=nulls)()
    Scenario(test=nested)()
    Scenario(test=varchar)()
    Scenario(test=variant)()
