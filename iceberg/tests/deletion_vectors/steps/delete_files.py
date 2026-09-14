"""Synthesize v2-style delete files (equality deletes and Parquet position
deletes) next to writer-produced deletion vectors.

No writer available in this environment produces equality-delete files
(Spark writes deletion vectors on v3, pyiceberg 0.9 rewrites data files),
and a *superseded* position-delete file coexisting with a newer deletion
vector cannot be forced through Spark either — so the coexistence
requirements are exercised by writing the delete Parquet file directly and
appending a manifest entry cloned from the live deletion-vector entry (which
keeps partition data and sequence numbers consistent with the snapshot).
"""

import copy
import io

import pyarrow as pa
import pyarrow.parquet as pq

from testflows.core import *

from helpers.common import getuid

from iceberg.tests.deletion_vectors.steps import manifest
from iceberg.tests.deletion_vectors.steps import s3_objects

# Iceberg reserved field ids of position-delete file columns
POS_DELETE_FILE_PATH_FIELD_ID = 2147483546
POS_DELETE_POS_FIELD_ID = 2147483545

# data_file stats fields that describe the original file and must not be
# carried over onto a synthesized delete file entry
STATS_FIELDS = (
    "column_sizes",
    "value_counts",
    "null_value_counts",
    "nan_value_counts",
    "lower_bounds",
    "upper_bounds",
    "key_metadata",
    "split_offsets",
    "sort_order_id",
    "first_row_id",
)


def _field(name, pa_type, field_id):
    return pa.field(
        name,
        pa_type,
        nullable=False,
        metadata={b"PARQUET:field_id": str(field_id).encode()},
    )


def _write_parquet(schema, columns):
    out = io.BytesIO()
    pq.write_table(pa.Table.from_pydict(columns, schema=schema), out)
    return out.getvalue()


def _append_delete_entry(namespace, table_name, data_file_overrides):
    """Append a delete-file entry cloned from the live deletion-vector entry
    with ``data_file`` fields replaced by *data_file_overrides*. The clone
    is inserted immediately after the template entry itself, so unrelated
    delete entries in the same manifest are never touched."""
    dv_entries = manifest.find_dv_entries(namespace=namespace, table_name=table_name)
    assert dv_entries, "fixture must already have a deletion vector"
    template_key = dv_entries[0]["manifest_key"]
    template = copy.deepcopy(dv_entries[0]["entry"])

    # identify the template entry in the rewrite pass before its clone's
    # data_file fields are replaced below
    template_file_path = template["data_file"]["file_path"]
    template_offset = template["data_file"]["content_offset"]

    data_file = template["data_file"]
    for field in STATS_FIELDS:
        if field in data_file:
            data_file[field] = None
    data_file["referenced_data_file"] = None
    data_file["content_offset"] = None
    data_file["content_size_in_bytes"] = None
    data_file.update(data_file_overrides)

    appended = []

    def mutator(entry):
        if (
            not appended
            and manifest.is_dv_entry(entry)
            and entry["data_file"]["file_path"] == template_file_path
            and entry["data_file"]["content_offset"] == template_offset
        ):
            appended.append(True)
            return [entry, template]
        return entry

    manifest.mutate_manifest_entries(
        namespace=namespace,
        table_name=table_name,
        mutator=mutator,
        content=manifest.MANIFEST_LIST_DELETES,
        only_manifest_key=template_key,
    )
    # a silent no-append would make the supersession scenario pass without
    # exercising anything (its expected rows are identical either way)
    assert appended, "template deletion-vector entry not found during the rewrite"


@TestStep(When)
def add_equality_delete(self, namespace, table_name, ids, column="id", field_id=1):
    """Add an equality-delete file removing rows whose *column* value is in
    *ids* (applies to data files with a lower data sequence number)."""
    schema = pa.schema([_field(column, pa.int64(), field_id)])
    data = _write_parquet(schema, {column: list(ids)})

    key = f"{s3_objects.table_prefix(namespace, table_name)}/data/eq-delete-{getuid()}.parquet"
    s3_objects.put_object_bytes(key, data)

    _append_delete_entry(
        namespace,
        table_name,
        {
            "content": manifest.EQUALITY_DELETES_CONTENT,
            "file_path": f"s3://{s3_objects.WAREHOUSE_BUCKET}/{key}",
            "file_format": "PARQUET",
            "record_count": len(ids),
            "file_size_in_bytes": len(data),
            "equality_ids": [field_id],
        },
    )


@TestStep(When)
def add_position_delete(self, namespace, table_name, data_file_path, positions):
    """Add a Parquet position-delete file marking *positions* of
    *data_file_path*. On a data file that also has a deletion vector, the
    v3 supersession rule says this file must be ignored."""
    schema = pa.schema(
        [
            _field("file_path", pa.string(), POS_DELETE_FILE_PATH_FIELD_ID),
            _field("pos", pa.int64(), POS_DELETE_POS_FIELD_ID),
        ]
    )
    data = _write_parquet(
        schema,
        {
            "file_path": [data_file_path] * len(positions),
            "pos": sorted(positions),
        },
    )

    key = f"{s3_objects.table_prefix(namespace, table_name)}/data/pos-delete-{getuid()}.parquet"
    s3_objects.put_object_bytes(key, data)

    _append_delete_entry(
        namespace,
        table_name,
        {
            "content": manifest.POSITION_DELETES_CONTENT,
            "file_path": f"s3://{s3_objects.WAREHOUSE_BUCKET}/{key}",
            "file_format": "PARQUET",
            "record_count": len(positions),
            "file_size_in_bytes": len(data),
            "equality_ids": None,
        },
    )


def first_data_file_path(namespace, table_name):
    """Full URI of the referenced data file of the single deletion-vector
    entry — the file both delete formats must target in coexistence tests.
    Asserts there is exactly one entry so the target is unambiguous."""
    dv_entries = manifest.find_dv_entries(namespace=namespace, table_name=table_name)
    assert (
        len(dv_entries) == 1
    ), f"expected exactly one deletion-vector entry, found {len(dv_entries)}"
    return dv_entries[0]["entry"]["data_file"]["referenced_data_file"]
