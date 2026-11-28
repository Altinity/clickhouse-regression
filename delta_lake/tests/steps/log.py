"""Write a Delta log by hand.

``deltalake`` cannot write deletion vectors, column mapping, a foreign
data format, or a reader feature ClickHouse does not implement. These
helpers upload Parquet files and JSON commits directly, so a scenario can
build exactly the snapshot it needs.

Action builders return plain dicts. ``commit`` writes one version.
"""

import io
import json
import struct
import time
import uuid
import zlib

import pyarrow as pa
import pyarrow.parquet as pq
from testflows.core import *

from helpers.common import getuid
from delta_lake.tests.steps.catalog import (
    BUCKET,
    DeltaTable,
    _credentials,
    _delete_prefix,
    put_object,
)

DV_MAGIC = 1681511377
ROARING_NO_RUN_COOKIE = 12346
Z85_CHARS = (
    "0123456789abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"
)


class HandTable(DeltaTable):
    """A Delta table whose log a scenario writes itself.

    It has the same location layout as a ``deltalake`` table, so
    ``register_delta_table`` can put it in Unity.
    """

    def log_key(self, version):
        return f"{self.prefix}/_delta_log/{version:020d}.json"


def z85_encode(data):
    """Z85 as the Delta spec uses it. The length must be a multiple of 4."""
    assert len(data) % 4 == 0, len(data)
    out = []
    for offset in range(0, len(data), 4):
        value = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk = []
        for _ in range(5):
            value, rest = divmod(value, 85)
            chunk.append(Z85_CHARS[rest])
        out.extend(reversed(chunk))
    return "".join(out)


def roaring_bitmap_array(rows):
    """Portable RoaringBitmapArray with the Delta magic, as Delta stores a DV.

    Only array containers are written, which hold up to 4096 rows per
    65536-row block. That is enough for these tests.
    """
    by_high = {}
    for row in sorted(set(rows)):
        by_high.setdefault(row >> 32, []).append(row & 0xFFFFFFFF)

    out = struct.pack("<I", DV_MAGIC)
    out += struct.pack("<q", len(by_high))
    for high, lows in sorted(by_high.items()):
        out += struct.pack("<I", high)
        out += _roaring32(lows)
    return out


def _roaring32(values):
    containers = {}
    for value in values:
        containers.setdefault(value >> 16, []).append(value & 0xFFFF)
    keys = sorted(containers)
    for key in keys:
        assert len(containers[key]) <= 4096, f"{len(containers[key])} values in one array container"
    header = struct.pack("<II", ROARING_NO_RUN_COOKIE, len(keys))
    for key in keys:
        header += struct.pack("<HH", key, len(containers[key]) - 1)
    offset = len(header) + 4 * len(keys)
    offsets = b""
    data = b""
    for key in keys:
        offsets += struct.pack("<I", offset + len(data))
        data += b"".join(struct.pack("<H", low) for low in containers[key])
    return header + offsets + data


def dv_file(bitmap):
    """A deletion vector file holding one DV. The DV starts at offset 1."""
    return (
        b"\x01"
        + struct.pack(">I", len(bitmap))
        + bitmap
        + struct.pack(">I", zlib.crc32(bitmap) & 0xFFFFFFFF)
    )


def parquet_bytes(data, field_ids=None):
    """Serialize an Arrow table. ``field_ids`` maps a column to its Parquet field id."""
    if field_ids:
        fields = []
        for field in data.schema:
            metadata = dict(field.metadata or {})
            if field.name in field_ids:
                metadata[b"PARQUET:field_id"] = str(field_ids[field.name]).encode()
            fields.append(field.with_metadata(metadata))
        data = data.cast(pa.schema(fields))
    buf = io.BytesIO()
    pq.write_table(data, buf)
    return buf.getvalue()


def protocol(reader=1, writer=2, reader_features=None, writer_features=None):
    action = {"minReaderVersion": reader, "minWriterVersion": writer}
    if reader_features is not None:
        action["readerFeatures"] = list(reader_features)
    if writer_features is not None:
        action["writerFeatures"] = list(writer_features)
    return {"protocol": action}


def field(name, type_name, nullable=True, metadata=None):
    return {
        "name": name,
        "type": type_name,
        "nullable": nullable,
        "metadata": metadata or {},
    }


def mapped_field(name, type_name, column_id, physical_name, nullable=True):
    """A field with column mapping metadata."""
    return field(
        name,
        type_name,
        nullable=nullable,
        metadata={
            "delta.columnMapping.id": column_id,
            "delta.columnMapping.physicalName": physical_name,
        },
    )


def metadata(
    fields,
    partition_columns=(),
    configuration=None,
    provider="parquet",
    table_id=None,
):
    return {
        "metaData": {
            "id": table_id or str(uuid.uuid4()),
            "format": {"provider": provider, "options": {}},
            "schemaString": json.dumps({"type": "struct", "fields": list(fields)}),
            "partitionColumns": list(partition_columns),
            "configuration": dict(configuration or {}),
            "createdTime": int(time.time() * 1000),
        }
    }


def add(path, size, partition_values=None, data_change=True, deletion_vector=None, extra=None):
    action = {
        "path": path,
        "partitionValues": dict(partition_values or {}),
        "size": size,
        "modificationTime": int(time.time() * 1000),
        "dataChange": data_change,
    }
    if deletion_vector is not None:
        action["deletionVector"] = deletion_vector
    if extra:
        action.update(extra)
    return {"add": action}


def remove(path, size=None, data_change=True, deletion_vector=None):
    action = {
        "path": path,
        "deletionTimestamp": int(time.time() * 1000),
        "dataChange": data_change,
    }
    if size is not None:
        action["size"] = size
    if deletion_vector is not None:
        action["deletionVector"] = deletion_vector
    return {"remove": action}


def commit_info(extra=None):
    info = {"timestamp": int(time.time() * 1000), "operation": "WRITE"}
    if extra:
        info.update(extra)
    return {"commitInfo": info}


@TestStep(Given)
def create_hand_table(self, access_key=None, secret_key=None):
    """Reserve a warehouse prefix for a hand-written table. Delete it later."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    table = HandTable(f"hand_{getuid()}", f"tbl_{getuid()}")
    try:
        yield table
    finally:
        with Finally(f"delete files {table.prefix}"):
            _delete_prefix(f"{table.prefix}/", access_key, secret_key)


@TestStep(When)
def upload_parquet(self, table, name, data, field_ids=None):
    """Upload ``data`` as ``name`` under the table root. Return ``(name, size)``."""
    body = parquet_bytes(data, field_ids=field_ids)
    put_object(key=f"{table.prefix}/{name}", body=body)
    return name, len(body)


@TestStep(When)
def commit(self, table, version, actions):
    """Write ``actions`` as commit ``version``."""
    body = "\n".join(json.dumps(action) for action in actions) + "\n"
    put_object(key=table.log_key(version), body=body.encode())


@TestStep(When)
def inline_dv(self, rows):
    """A deletion vector descriptor stored in the log (``storageType`` i).

    Z85 encodes 4 bytes at a time, so the bitmap is padded with zeros.
    ``sizeInBytes`` is the length before padding.
    """
    bitmap = roaring_bitmap_array(rows)
    padded = bitmap + b"\x00" * (-len(bitmap) % 4)
    return {
        "storageType": "i",
        "pathOrInlineDv": z85_encode(padded),
        "sizeInBytes": len(bitmap),
        "cardinality": len(set(rows)),
    }


@TestStep(When)
def uuid_dv(self, table, rows, prefix="ab"):
    """Upload a DV file named by UUID under the table root (``storageType`` u)."""
    bitmap = roaring_bitmap_array(rows)
    dv_id = uuid.uuid4()
    directory = f"{table.prefix}/{prefix}" if prefix else table.prefix
    put_object(key=f"{directory}/deletion_vector_{dv_id}.bin", body=dv_file(bitmap))
    return {
        "storageType": "u",
        "pathOrInlineDv": prefix + z85_encode(dv_id.bytes),
        "offset": 1,
        "sizeInBytes": len(bitmap),
        "cardinality": len(set(rows)),
    }


@TestStep(When)
def path_dv(self, table, rows, name=None):
    """Upload a DV file and point at it by absolute path (``storageType`` p)."""
    bitmap = roaring_bitmap_array(rows)
    if name is None:
        name = f"dv_{getuid()}.bin"
    key = f"{table.prefix}/{name}"
    put_object(key=key, body=dv_file(bitmap))
    return {
        "storageType": "p",
        "pathOrInlineDv": f"s3://{BUCKET}/{key}",
        "offset": 1,
        "sizeInBytes": len(bitmap),
        "cardinality": len(set(rows)),
    }
