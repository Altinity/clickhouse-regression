"""Clone a Spark-written S3 Iceberg table onto a ClickHouse node's local
filesystem so it can be read with ``icebergLocal``.

Iceberg metadata stores absolute locations (``s3://warehouse/...``) in the
metadata JSON, the manifest list and the manifests, so a plain object copy
is unreadable locally. The clone rewrites every location to the target
directory under ``user_files`` while keeping everything else byte-identical:

* ``*.metadata.json`` — plain-text location replacement;
* manifest list / manifests — fastavro round-trip rewriting
  ``manifest_path``, ``data_file.file_path`` and
  ``data_file.referenced_data_file``;
* data / Puffin files — copied verbatim.

Files are transferred into the container through ``node.command`` with
base64 (fixture tables are small), avoiding any dependency on host mounts.
"""

import base64
import copy
import io
import json

import fastavro

from testflows.core import *

from helpers.common import getuid

from iceberg.tests.deletion_vectors.steps import s3_objects

USER_FILES_DIR = "/var/lib/clickhouse/user_files"


def _rewrite_locations_in_avro(data, old_location, new_location):
    """Rewrite path-bearing string fields in a manifest/manifest-list."""
    reader = fastavro.reader(io.BytesIO(data))
    records = [copy.deepcopy(record) for record in reader]
    metadata = {
        name: value
        for name, value in reader.metadata.items()
        if not name.startswith("avro.")
    }

    def swap(value):
        return value.replace(old_location, new_location) if value else value

    for record in records:
        if "manifest_path" in record:
            record["manifest_path"] = swap(record["manifest_path"])
        if "data_file" in record and record["data_file"] is not None:
            data_file = record["data_file"]
            data_file["file_path"] = swap(data_file["file_path"])
            if data_file.get("referenced_data_file"):
                data_file["referenced_data_file"] = swap(
                    data_file["referenced_data_file"]
                )

    out = io.BytesIO()
    fastavro.writer(out, reader.writer_schema, records, codec=reader.codec, metadata=metadata)
    return out.getvalue()


def _upload_to_node(node, path, data, chunk_size=48000):
    """Write bytes to *path* inside the node via base64 chunks."""
    node.command(f"rm -f {path}", exitcode=0)
    encoded = base64.b64encode(data).decode()
    for start in range(0, len(encoded), chunk_size):
        chunk = encoded[start : start + chunk_size]
        node.command(
            f"echo -n '{chunk}' | base64 -d >> {path}",
            exitcode=0,
        )


@TestStep(Given)
def clone_table_to_local(self, table, node=None):
    """Clone the fixture table to ``user_files`` on *node* and return the
    local table directory usable with ``icebergLocal('<dir>')``.

    The cloned directory is removed on cleanup.
    """
    if node is None:
        node = self.context.node

    local_dir = f"{USER_FILES_DIR}/dv_local_{getuid()}"
    old_location = (
        f"s3://{s3_objects.WAREHOUSE_BUCKET}/{table.namespace}/{table.table_name}"
    )

    try:
        node.command(f"mkdir -p {local_dir}/data {local_dir}/metadata", exitcode=0)

        for key in s3_objects.list_keys(table.prefix):
            data = s3_objects.get_object_bytes(key)
            relative = key[len(table.prefix) :].lstrip("/")

            if key.endswith(".metadata.json"):
                text = data.decode("utf-8").replace(old_location, local_dir)
                data = text.encode("utf-8")
            elif key.endswith(".avro"):
                data = _rewrite_locations_in_avro(data, old_location, local_dir)

            _upload_to_node(node, f"{local_dir}/{relative}", data)

        yield local_dir

    finally:
        with Finally("remove the local table clone"):
            node.command(f"rm -rf {local_dir}", exitcode=0)


@TestStep(Then)
def read_local_ids(self, local_dir, node=None, log_comment=None, settings=None):
    """Ids visible via icebergLocal on the cloned table, ordered."""
    if node is None:
        node = self.context.node

    query_settings = list(settings or [])
    if log_comment:
        query_settings.append(("log_comment", f"{log_comment}"))

    result = node.query(
        f"SELECT id FROM icebergLocal('{local_dir}') ORDER BY id FORMAT TabSeparated",
        settings=query_settings or None,
    )
    return [int(line) for line in result.output.split() if line.strip()]
