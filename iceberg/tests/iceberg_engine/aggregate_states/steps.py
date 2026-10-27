"""Steps shared by the ``aggregate states`` suite (Altinity/ClickHouse#2680).

Tables here are written by ClickHouse itself through ``ENGINE = IcebergS3``
at ``s3://warehouse/data/<table>``, so the metadata ClickHouse writes can be
inspected on MinIO directly, registered in a catalog, or handed to an external
engine. Catalog-backed creation reuses the ``native create`` steps.
"""

import io
import json
import re

import pyarrow as pa
import pyarrow.parquet as pq
import pyiceberg.exceptions

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.s3_objects as s3


SETTING = "allow_experimental_aggregate_function_states_in_open_formats"
STATE_SETTINGS = [(SETTING, 1)]

ANNOTATION_KEY = "clickhouse.type"
PARQUET_COLUMN_TYPES_KEY = b"clickhouse.column_types"

# ``k`` and ``s`` use signed types so PyIceberg and Spark can write the same
# columns: Spark's Arrow reader rejects the UINT_64 converted type of UInt64.
COLUMNS = (
    "k Int32, "
    "u AggregateFunction(uniq, UInt64), "
    "s SimpleAggregateFunction(sum, Int64)"
)
U_TYPE = "AggregateFunction(uniq, UInt64)"
S_TYPE = "SimpleAggregateFunction(sum, Int64)"

STATES_SELECT = (
    "SELECT toInt32(number % {groups}) AS k, "
    "uniqState(toUInt64(number % 23)) AS u, "
    "sumSimpleState(toInt64(number)) AS s "
    "FROM numbers({start}, {count}) GROUP BY k"
)
EXPECTED_SELECT = (
    "SELECT toInt32(number % {groups}) AS k, "
    "uniq(toUInt64(number % 23)), "
    "sum(toInt64(number)) "
    "FROM numbers({start}, {count}) GROUP BY k ORDER BY k FORMAT TabSeparated"
)
MERGE_SELECT = (
    "SELECT k, uniqMerge(u), sum(s) FROM {source} "
    "GROUP BY k ORDER BY k FORMAT TabSeparated"
)

TABLE_URL = "http://minio:9000/warehouse/data/{table_name}/"

# clickhouse-client exits with the error code modulo 256.
UNKNOWN_TYPE = 50
SUPPORT_IS_DISABLED = 344 % 256


def feature_available(node):
    """The PR's marker: the gate setting exists only on builds with the feature."""
    # ``steps=False``: this runs at feature level, where a ``--only`` filter would
    # skip the implicit step ``node.query`` opens and the probe would never run.
    result = node.query(
        f"SELECT count() FROM system.settings WHERE name = '{SETTING}'",
        steps=False,
        no_checks=True,
    )
    return result.exitcode == 0 and result.output.strip() == "1"


def write_settings():
    """Query settings every INSERT into a ClickHouse-written table needs.

    ``write_full_path_in_iceberg_metadata`` makes every path in the metadata an
    absolute ``s3://`` URI, which PyIceberg, Spark and catalog registration need.
    """
    return [
        ("allow_insert_into_iceberg", 1),
        ("write_full_path_in_iceberg_metadata", 1),
        (SETTING, 1),
    ]


def table_prefix(table_name):
    """Bucket-relative prefix of a table created by :func:`iceberg_s3_table`."""
    return f"data/{table_name}/"


def table_location(table_name):
    return f"s3://warehouse/data/{table_name}"


def icebergs3_function(table_name, storage_settings=None, test=None):
    """``icebergS3(...)`` table function over a table at ``warehouse/data/<name>``.

    ``storage_settings`` are data lake settings given inside the call, such as
    ``iceberg_metadata_file_path``, which is not a query setting."""
    test = test or current()
    expr = (
        f"icebergS3('{TABLE_URL.format(table_name=table_name)}', "
        f"'{test.context.minio_root_user}', '{test.context.minio_root_password}'"
    )
    if storage_settings:
        expr += ", SETTINGS " + ", ".join(
            f"{key} = '{value}'" for key, value in storage_settings.items()
        )
    return expr + ")"


def merge_select(source):
    return MERGE_SELECT.format(source=source)


def expected_select(start=0, count=200, groups=2):
    return EXPECTED_SELECT.format(start=start, count=count, groups=groups)


def states_select(start=0, count=200, groups=2):
    return STATES_SELECT.format(start=start, count=count, groups=groups)


@TestStep(Given)
def iceberg_s3_table(
    self,
    table_name=None,
    columns=COLUMNS,
    partition_by=None,
    engine_setting=True,
    query_settings=None,
    node=None,
    exitcode=None,
    message=None,
):
    """``CREATE TABLE ... ENGINE = IcebergS3`` at ``warehouse/data/<table_name>``.

    ``engine_setting`` puts the gate setting into the ``SETTINGS`` clause, which
    is where the Parquet writer of an object storage table engine takes it from.
    ``query_settings`` are sent as query settings of the ``CREATE`` itself; by
    default the gate setting and ``write_full_path_in_iceberg_metadata``.

    The finaliser drops the table and removes everything under its prefix.
    """
    if node is None:
        node = self.context.node
    if table_name is None:
        table_name = f"agg_{getuid()}"
    if query_settings is None:
        query_settings = [("write_full_path_in_iceberg_metadata", 1), (SETTING, 1)]

    query = (
        f"CREATE TABLE {table_name} ({columns}) "
        f"ENGINE = IcebergS3('{TABLE_URL.format(table_name=table_name)}', "
        f"'{self.context.minio_root_user}', '{self.context.minio_root_password}')"
    )
    if partition_by:
        query += f" PARTITION BY {partition_by}"
    if engine_setting:
        query += f" SETTINGS {SETTING} = 1"

    try:
        node.query(
            query,
            settings=query_settings or None,
            exitcode=exitcode,
            message=message,
            ignore_exception=exitcode is not None or message is not None,
        )
        yield table_name
    finally:
        with Finally(f"drop {table_name} and its objects"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", no_checks=True)
            s3.delete_prefix(table_prefix(table_name))


@TestStep(Given)
def aggregating_merge_tree(self, columns=COLUMNS, name=None, node=None):
    """An ``AggregatingMergeTree`` ordered by ``k`` with the same columns."""
    if node is None:
        node = self.context.node
    if name is None:
        name = f"amt_{getuid()}"
    try:
        node.query(
            f"CREATE TABLE {name} ({columns}) ENGINE = AggregatingMergeTree ORDER BY k"
        )
        yield name
    finally:
        with Finally(f"drop {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestStep(When)
def insert_states(
    self, table_name, start=0, count=200, groups=2, settings=None, node=None
):
    """``INSERT INTO <table> SELECT`` one state per group of ``numbers(start, count)``."""
    if node is None:
        node = self.context.node
    return node.query(
        f"INSERT INTO {table_name} (k, u, s) "
        + states_select(start=start, count=count, groups=groups),
        settings=write_settings() if settings is None else settings,
    )


@TestStep(When)
def query_refused(self, query, message, settings=None, exitcode=None, node=None):
    """Run ``query`` and assert it fails with ``message`` in the output.

    The gate errors name the setting rather than share one exit code, so the
    message is the primary check and ``exitcode`` is optional.
    """
    if node is None:
        node = self.context.node
    result = node.query(query, settings=settings, no_checks=True)
    assert result.exitcode != 0, error(
        f"query was expected to fail but succeeded: {query}\n{result.output}"
    )
    if exitcode is not None:
        assert result.exitcode == exitcode, error(
            f"exit code {result.exitcode}, expected {exitcode}: {result.output}"
        )
    assert message in result.output, error(
        f"{message!r} not in the error: {result.output}"
    )
    return result


@TestStep(Then)
def assert_merge_matches(self, source, expected, settings=STATE_SETTINGS, node=None):
    """``uniqMerge(u), sum(s)`` per ``k`` over ``source`` equals the TSV in
    ``expected``, which is the output of :func:`expected_select`."""
    if node is None:
        node = self.context.node
    actual = node.query(merge_select(source), settings=settings).output
    assert actual == expected, error(f"merged:\n{actual}\nexpected:\n{expected}")


def expected_result(start=0, count=200, groups=2, node=None):
    """Output of :func:`expected_select` on the node."""
    node = node or current().context.node
    return node.query(
        expected_select(start=start, count=count, groups=groups), steps=False
    ).output


def describe(expr, settings=None, node=None):
    """``[(name, type)]`` from ``DESCRIBE`` with non-pretty type names."""
    node = node or current().context.node
    output = node.query(
        f"DESCRIBE {expr} FORMAT TSV",
        settings=[("print_pretty_type_names", 0)] + list(settings or []),
    ).output
    return [tuple(line.split("\t")[:2]) for line in output.splitlines() if line]


# ---------------------------------------------------------------------------
# Iceberg metadata on MinIO
# ---------------------------------------------------------------------------

_METADATA_VERSION = re.compile(r"^(?:v(\d+)|(\d+)-[0-9a-f-]+)[.-]")


def metadata_version(key):
    """Version number of ``v<N>[...].metadata.json`` or ``<N>-<uuid>.metadata.json``."""
    name = key.rsplit("/", 1)[-1]
    match = _METADATA_VERSION.match(name)
    assert match, error(f"unrecognised metadata file name {name}")
    return int(match.group(1) or match.group(2))


def latest_metadata_key(prefix):
    keys = s3.metadata_keys(s3.object_inventory(prefix))
    assert keys, error(f"no metadata files under {prefix}")
    return max(keys, key=metadata_version)


def read_latest_metadata(prefix):
    """``(metadata, key)`` of the highest-versioned metadata file under ``prefix``."""
    key = latest_metadata_key(prefix)
    return s3.read_json_object(key), key


def current_schema(metadata):
    schema_id = metadata["current-schema-id"]
    for schema in metadata["schemas"]:
        if schema["schema-id"] == schema_id:
            return schema
    raise AssertionError(f"schema {schema_id} not found in {metadata['schemas']}")


def fields_by_name(metadata):
    return {field["name"]: field for field in current_schema(metadata)["fields"]}


def annotations(metadata):
    """``{field name: clickhouse.type or None}`` of the current schema."""
    return {
        name: field.get(ANNOTATION_KEY)
        for name, field in fields_by_name(metadata).items()
    }


@TestStep(Then)
def assert_annotations(self, metadata, expected, where):
    """The current schema carries exactly the ``expected`` annotations.

    ``expected`` maps field name to the annotation, or ``None`` for a field
    that must carry none. ``where`` names the metadata file in the error.
    """
    actual = annotations(metadata)
    for name, value in expected.items():
        assert name in actual, error(f"field {name} missing from {where}: {actual}")
        assert actual[name] == value, error(
            f"{where}: field {name} carries {ANNOTATION_KEY}={actual[name]!r}, "
            f"expected {value!r}; all annotations: {actual}"
        )


def write_metadata_version(prefix, metadata):
    """Store ``metadata`` as the next ``v<N>.metadata.json`` under ``prefix``,
    pointing ``version-hint.text`` at it when the table has one, so a reader
    that picks the latest version reads the edited copy. Returns the key."""
    keys = s3.metadata_keys(s3.object_inventory(prefix))
    version = max(metadata_version(key) for key in keys) + 1
    key = f"{prefix}metadata/v{version}.metadata.json"
    s3.put_object_bytes(key, json.dumps(metadata).encode())
    hint = f"{prefix}metadata/version-hint.text"
    if s3.object_exists(hint):
        s3.put_object_bytes(hint, str(version).encode())
    return key


def edit_annotations(metadata, changes):
    """Copy of ``metadata`` whose current schema has the annotations in
    ``changes`` set (a value) or removed (``None``)."""
    edited = json.loads(json.dumps(metadata))
    for field in current_schema(edited)["fields"]:
        if field["name"] in changes:
            if changes[field["name"]] is None:
                field.pop(ANNOTATION_KEY, None)
            else:
                field[ANNOTATION_KEY] = changes[field["name"]]
    return edited


# ---------------------------------------------------------------------------
# Parquet footers
# ---------------------------------------------------------------------------


@TestStep(Given)
def parquet_key(self):
    """A fresh bucket-relative key for a standalone Parquet file, removed by
    the finaliser."""
    key = f"parquet/agg_{getuid()}.parquet"
    try:
        yield key
    finally:
        with Finally(f"remove {key}"):
            s3.delete_prefix(key)


def s3_function(key, structure=None, test=None):
    """``s3(...)`` table function over a Parquet object in the warehouse bucket."""
    test = test or current()
    expr = (
        f"s3('{s3.S3_NETWORK_ENDPOINT}/{s3.WAREHOUSE_BUCKET}/{key}', "
        f"'{test.context.minio_root_user}', '{test.context.minio_root_password}', "
        "'Parquet'"
    )
    if structure:
        expr += f", '{structure}'"
    return expr + ")"


def parquet_metadata(key):
    """``pyarrow.parquet.FileMetaData`` of a Parquet object in the warehouse bucket."""
    return pq.read_metadata(io.BytesIO(s3.get_object_bytes(key)))


def parquet_column_types(key):
    """Parsed ``clickhouse.column_types`` of a Parquet object, or ``None``."""
    key_value = parquet_metadata(key).metadata or {}
    raw = key_value.get(PARQUET_COLUMN_TYPES_KEY)
    return None if raw is None else json.loads(raw)


def data_file_keys(prefix):
    return sorted(
        key for key in s3.object_inventory(prefix) if key.endswith(".parquet")
    )


def parquet_column(metadata, name):
    """The ``ColumnSchema`` of the top-level leaf column ``name``."""
    for i in range(metadata.num_columns):
        column = metadata.schema.column(i)
        if column.path == name:
            return column
    raise AssertionError(f"column {name} not in the Parquet schema")


def is_plain_binary(column):
    """``BYTE_ARRAY`` with neither a ``STRING`` logical type nor ``UTF8``."""
    logical = str(column.logical_type)
    return (
        column.physical_type == "BYTE_ARRAY"
        and logical in ("None", "")
        and column.converted_type in ("NONE", None)
    )


# ---------------------------------------------------------------------------
# External engines
# ---------------------------------------------------------------------------


def external_rows(start, count, groups=2, node=None):
    """The rows :func:`insert_states` would write for ``numbers(start, count)``,
    as ``[{"k": int, "u": bytes, "s": int}]`` for an external writer. ClickHouse
    computes the states; the external engine only stores the bytes."""
    node = node or current().context.node
    output = node.query(
        f"SELECT k, hex(u), s FROM ({states_select(start, count, groups)}) "
        "ORDER BY k FORMAT TabSeparated",
        steps=False,
    ).output
    rows = []
    for line in output.splitlines():
        k, u, s = line.split("\t")
        rows.append({"k": int(k), "u": bytes.fromhex(u), "s": int(s)})
    return rows


@TestStep(Given)
def registered_in_catalog(self, catalog, namespace, table_name, metadata_key):
    """Register a ClickHouse-written table in the PyIceberg catalog at the
    metadata file it currently has. The finaliser unregisters it; the objects
    belong to the table fixture."""
    catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
    identifier = f"{namespace}.{table_name}"
    try:
        yield catalog.register_table(
            identifier, f"s3://{s3.WAREHOUSE_BUCKET}/{metadata_key}"
        )
    finally:
        with Finally(f"unregister {identifier}"):
            try:
                catalog.drop_table(identifier)
            except pyiceberg.exceptions.NoSuchTableError:
                pass


@TestStep(When)
def pyiceberg_append_states(self, table, rows):
    """Append ``rows`` (``[{"k": int, "u": bytes, "s": int}]``) through PyIceberg,
    a commit by an engine that is not ClickHouse."""
    table.append(pa.Table.from_pylist(rows, schema=table.schema().as_arrow()))
