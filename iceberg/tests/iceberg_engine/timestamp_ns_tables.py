"""Build Iceberg tables that reproduce nanosecond timestamp pruning bugs.

PyIceberg 0.9 cannot write Iceberg v3 ``timestamp_ns``. These helpers write
epoch nanoseconds as ``long`` (or real microseconds as ``timestamp``), then
rewrite the table objects in place:

* ``timestamp_ns`` — Parquet becomes ``timestamp[ns]`` and the Iceberg schema
  says ``timestamp_ns``. Manifest min/max bytes stay the original nanosecond
  ticks. Identity partition values stay Avro longs.
* customer bounds — the schema stays Iceberg ``timestamp`` (microseconds) and
  the Parquet stays ``timestamp[us]``, but lower/upper bound bytes are
  multiplied by 1000 so they look like nanoseconds.
* far-future bounds — upper bounds are replaced with spec-correct
  microsecond sentinels (Spark ``9999-12-31``, ClickHouse ``DateTime64`` max
  ``2299-12-31``) while the lower bound stays a 2024 microsecond value.
"""

import copy
import io
import json
import struct
from datetime import datetime, timezone

import fastavro
import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import NestedField, Schema
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import IdentityTransform
from pyiceberg.types import IntegerType, LongType, TimestampType

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.s3_objects as s3


# Epoch nanoseconds and the matching UTC wall time. The last three digits
# differ so a reader that truncates to microseconds collapses distinct rows.
ROWS = [
    (1704067200123456789, 1, "2024-01-01 00:00:00.123456789"),
    (1710504000000000001, 2, "2024-03-15 12:00:00.000000001"),
    (1719791999999999999, 3, "2024-06-30 23:59:59.999999999"),
    (1767205845111111111, 4, "2025-12-31 18:30:45.111111111"),
]

NS_COLUMN_NAMES = ("ts", "value")
BOUND_FIELD_IDS = {1, 2}

CLICKHOUSE_S3_ENDPOINT = "http://minio:9000"


def utc_micros(dt):
    """Integer microseconds from the Unix epoch."""
    delta = dt - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (
        delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
    )


# Spec-correct Iceberg ``timestamp`` microseconds in the ambiguous band
# (1e16, 1e18]. Treating them as nanoseconds over-prunes.
SPARK_TIMESTAMP_SENTINEL_US = utc_micros(
    datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
)
DATETIME64_MAX_US = utc_micros(
    datetime(2299, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
)


def clickhouse_url(location):
    """``s3://warehouse/data/t`` → ``http://minio:9000/warehouse/data/t/``."""
    assert location.startswith("s3://"), location
    return f"{CLICKHOUSE_S3_ENDPOINT}/{location[len('s3://'):].rstrip('/')}/"


def _prefix(location):
    return s3.prefix_from_uri(location)


def _keys(location):
    return s3.list_keys(_prefix(location))


def long_schema():
    return Schema(
        NestedField(field_id=1, name="ts", field_type=LongType(), required=False),
        NestedField(field_id=2, name="value", field_type=LongType(), required=False),
        NestedField(field_id=3, name="id", field_type=IntegerType(), required=False),
    )


def timestamp_schema():
    return Schema(
        NestedField(field_id=1, name="ts", field_type=TimestampType(), required=False),
        NestedField(
            field_id=2, name="value", field_type=TimestampType(), required=False
        ),
        NestedField(field_id=3, name="id", field_type=IntegerType(), required=False),
    )


def _identity_spec():
    return PartitionSpec(
        PartitionField(
            source_id=1,
            field_id=1000,
            transform=IdentityTransform(),
            name="ts",
        )
    )


def _arrow_long_row(ts_ns, row_id):
    return pa.Table.from_pydict(
        {
            "ts": pa.array([ts_ns], type=pa.int64()),
            "value": pa.array([ts_ns], type=pa.int64()),
            "id": pa.array([row_id], type=pa.int32()),
        }
    )


def _arrow_timestamp_table():
    micros = [ts_ns // 1000 for ts_ns, _row_id, _utc in ROWS]
    ids = [row_id for _ts_ns, row_id, _utc in ROWS]
    column = pa.array(micros, type=pa.timestamp("us"))
    return pa.Table.from_pydict(
        {
            "ts": column,
            "value": column,
            "id": pa.array(ids, type=pa.int32()),
        }
    )


@TestStep(Given)
def write_nanosecond_long_table(
    self, minio_root_user, minio_root_password, partitioned
):
    """One data file per row. ``partitioned`` uses identity on ``ts``.

    Yields the table ``s3://`` location. The caller patches it before reading.
    """
    namespace = f"ns_{getuid()}"
    table_name = f"tsns_{getuid()}"
    location = f"s3://warehouse/data/{table_name}"

    try:
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            clean_up_minio_bucket=False,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=long_schema(),
            location=location,
            partition_spec=_identity_spec() if partitioned else PartitionSpec(),
            sort_order=SortOrder(),
            format_version="2",
        )

        identifier = f"{namespace}.{table_name}"
        for ts_ns, row_id, _utc in ROWS:
            table.append(_arrow_long_row(ts_ns, row_id))
            table = catalog.load_table(identifier)

        location = table.location().rstrip("/")
        assert table_name in location, error(location)
        parquet = [key for key in _keys(location) if key.endswith(".parquet")]
        assert len(parquet) == len(ROWS), error(parquet)
        yield location
    finally:
        with Finally(f"delete objects under {location}"):
            s3.delete_prefix(s3.prefix_from_uri(location))


@TestStep(Given)
def write_microsecond_timestamp_table(self, minio_root_user, minio_root_password):
    """One unpartitioned file of Iceberg ``timestamp`` (microseconds)."""
    namespace = f"ns_{getuid()}"
    table_name = f"tsus_{getuid()}"
    location = f"s3://warehouse/data/{table_name}"

    try:
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            clean_up_minio_bucket=False,
        )
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=timestamp_schema(),
            location=location,
            partition_spec=PartitionSpec(),
            sort_order=SortOrder(),
            format_version="2",
        )
        table.append(_arrow_timestamp_table())
        table = catalog.load_table(f"{namespace}.{table_name}")

        location = table.location().rstrip("/")
        assert table_name in location, error(location)
        parquet = [key for key in _keys(location) if key.endswith(".parquet")]
        assert len(parquet) == 1, error(parquet)
        yield location
    finally:
        with Finally(f"delete objects under {location}"):
            s3.delete_prefix(s3.prefix_from_uri(location))


def _upgrade_long_to_timestamp_ns(obj, iceberg_type):
    if isinstance(obj, dict):
        if obj.get("name") in NS_COLUMN_NAMES and obj.get("type") == "long":
            obj["type"] = iceberg_type
        for value in obj.values():
            _upgrade_long_to_timestamp_ns(value, iceberg_type)
    elif isinstance(obj, list):
        for value in obj:
            _upgrade_long_to_timestamp_ns(value, iceberg_type)


def _meta_text(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8")
    return value


def _upgrade_avro_metadata(metadata, iceberg_type):
    for key in ("schema", "iceberg.schema"):
        raw = metadata.get(key)
        if raw is None:
            continue
        parsed = json.loads(_meta_text(raw))
        _upgrade_long_to_timestamp_ns(parsed, iceberg_type)
        metadata[key] = json.dumps(parsed, separators=(",", ":"))
    return metadata


def _read_avro(data):
    reader = fastavro.reader(io.BytesIO(data))
    records = [copy.deepcopy(record) for record in reader]
    metadata = {
        name: value
        for name, value in reader.metadata.items()
        if not str(name).startswith("avro.")
    }
    return records, reader.writer_schema, metadata, reader.codec


def _write_avro(records, schema, metadata, codec):
    out = io.BytesIO()
    encoded = {key: _meta_text(value) for key, value in metadata.items()}
    fastavro.writer(out, schema, records, codec=codec, metadata=encoded)
    return out.getvalue()


def _rewrite_parquet(data):
    """Cast ``ts`` / ``value`` int64 columns to ``timestamp[ns]``, keeping field ids."""
    table = pq.read_table(io.BytesIO(data))
    fields = []
    arrays = []
    changed = False
    for field in table.schema:
        column = table.column(field.name)
        if field.name in NS_COLUMN_NAMES and pa.types.is_int64(field.type):
            column = column.cast(pa.timestamp("ns"))
            field = pa.field(
                field.name,
                column.type,
                nullable=field.nullable,
                metadata=field.metadata,
            )
            changed = True
        fields.append(field)
        arrays.append(column)
    if not changed:
        return data, False
    out = io.BytesIO()
    pq.write_table(pa.Table.from_arrays(arrays, schema=pa.schema(fields)), out)
    rewritten = pq.ParquetFile(io.BytesIO(out.getvalue())).schema_arrow
    for name in NS_COLUMN_NAMES:
        field_type = rewritten.field(name).type
        assert pa.types.is_timestamp(field_type) and field_type.unit == "ns", (
            name,
            field_type,
        )
    return out.getvalue(), True


def _bound_bytes(raw):
    if isinstance(raw, (bytes, bytearray)) and len(raw) == 8:
        return raw
    return None


def _visit_bounds(data_file, field_name, transform):
    bounds = data_file.get(field_name)
    updated = 0
    if isinstance(bounds, dict):
        items = list(bounds.items())
        for key, value in items:
            try:
                column_id = int(key)
            except (TypeError, ValueError):
                continue
            if column_id not in BOUND_FIELD_IDS or _bound_bytes(value) is None:
                continue
            new_value = transform(value)
            if new_value != value:
                bounds[key] = new_value
                updated += 1
    elif isinstance(bounds, list):
        for item in bounds:
            if not isinstance(item, dict) or "value" not in item:
                continue
            try:
                column_id = int(item.get("key", item.get("field_id")))
            except (TypeError, ValueError):
                continue
            if (
                column_id not in BOUND_FIELD_IDS
                or _bound_bytes(item["value"]) is None
            ):
                continue
            new_value = transform(item["value"])
            if new_value != item["value"]:
                item["value"] = new_value
                updated += 1
    return updated


def _scale_us_to_ns(raw):
    value = struct.unpack("<q", raw)[0]
    return struct.pack("<q", value * 1000)


def _set_micros(micros):
    def transform(_raw):
        return struct.pack("<q", micros)

    return transform


def _data_files(records):
    for record in records:
        if not isinstance(record, dict):
            continue
        data_file = record.get("data_file")
        if isinstance(data_file, dict):
            yield data_file
        elif "lower_bounds" in record or "upper_bounds" in record:
            yield record


def _sync_file_sizes(records, parquet_sizes):
    for data_file in _data_files(records):
        path = data_file.get("file_path")
        if not path:
            continue
        key = s3.key_from_uri(path)
        if key in parquet_sizes:
            data_file["file_size_in_bytes"] = parquet_sizes[key]


def _patch_avro(location, mutate_records, iceberg_type=None, parquet_sizes=None):
    avro_keys = [key for key in _keys(location) if key.endswith(".avro")]
    assert avro_keys, error(f"no avro under {location}")
    rewritten = {}
    for key in avro_keys:
        records, schema, metadata, codec = _read_avro(s3.get_object_bytes(key))
        if iceberg_type:
            metadata = _upgrade_avro_metadata(metadata, iceberg_type)
        mutate_records(records)
        if parquet_sizes:
            _sync_file_sizes(records, parquet_sizes)
        payload = _write_avro(records, schema, metadata, codec)
        rewritten[key] = {
            "payload": payload,
            "records": records,
            "schema": schema,
            "metadata": metadata,
            "codec": codec,
        }

    for key, item in rewritten.items():
        records = item["records"]
        if not records or "manifest_path" not in records[0]:
            continue
        changed = False
        for record in records:
            manifest_key = s3.key_from_uri(record["manifest_path"])
            manifest = rewritten.get(manifest_key)
            if manifest is None:
                continue
            length = len(manifest["payload"])
            if record.get("manifest_length") != length:
                record["manifest_length"] = length
                changed = True
        if changed:
            item["payload"] = _write_avro(
                records, item["schema"], item["metadata"], item["codec"]
            )

    for key, item in rewritten.items():
        s3.put_object_bytes(key, item["payload"])


def patch_long_columns_to_timestamp_ns(location, iceberg_type="timestamp_ns"):
    """Turn ``long`` nanosecond columns into ``iceberg_type`` and ``timestamp[ns]``."""
    keys = _keys(location)
    parquet_sizes = {}
    rewritten_parquet = 0
    for key in keys:
        if not key.endswith(".parquet"):
            continue
        payload, changed = _rewrite_parquet(s3.get_object_bytes(key))
        if changed:
            s3.put_object_bytes(key, payload)
            parquet_sizes[key] = len(payload)
            rewritten_parquet += 1
    assert rewritten_parquet == len(ROWS), error(rewritten_parquet)

    upgraded_metadata = 0
    for key in keys:
        if not key.endswith(".metadata.json"):
            continue
        meta = json.loads(s3.get_object_bytes(key))
        _upgrade_long_to_timestamp_ns(meta, iceberg_type)
        s3.put_object_bytes(
            key, json.dumps(meta, separators=(",", ":")).encode("utf-8")
        )
        upgraded_metadata += 1
    assert upgraded_metadata > 0, error(location)

    def mutate(_records):
        return None

    _patch_avro(
        location,
        mutate,
        iceberg_type=iceberg_type,
        parquet_sizes=parquet_sizes,
    )


def patch_timestamp_bounds_us_to_ns(location):
    """Multiply Iceberg ``timestamp`` lower/upper bounds by 1000."""
    scaled = 0

    def mutate(records):
        nonlocal scaled
        for data_file in _data_files(records):
            scaled += _visit_bounds(data_file, "lower_bounds", _scale_us_to_ns)
            scaled += _visit_bounds(data_file, "upper_bounds", _scale_us_to_ns)

    _patch_avro(location, mutate)
    assert scaled > 0, error(f"no timestamp bounds scaled under {location}")


def patch_timestamp_upper_bound(location, micros):
    """Replace Iceberg ``timestamp`` upper bounds with ``micros``."""

    updated = 0

    def mutate(records):
        nonlocal updated
        for data_file in _data_files(records):
            updated += _visit_bounds(data_file, "upper_bounds", _set_micros(micros))

    _patch_avro(location, mutate)
    assert updated > 0, error(f"no timestamp upper bounds patched under {location}")
