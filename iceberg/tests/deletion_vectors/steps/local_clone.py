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
* ``*.puffin`` — footer rebuild rewriting each blob's
  ``referenced-data-file`` property (the reader cross-checks it against the
  manifest entry's data file path); the blob region stays byte-identical so
  the manifest-declared ``content_offset`` / ``content_size_in_bytes``
  remain valid;
* data files — copied verbatim.

The rewritten tree is staged in a host temporary directory and transferred
into the container with a single ``docker cp`` — pushing file content
through the node's interactive shell is not an option, its pty chokes on
long command lines.
"""

import copy
import io
import json
import os
import struct
import subprocess
import tempfile

import fastavro

from testflows.core import *

from helpers.common import getuid

from iceberg.tests.deletion_vectors.steps import puffin as puffin_steps
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
    fastavro.writer(
        out, reader.writer_schema, records, codec=reader.codec, metadata=metadata
    )
    return out.getvalue()


def _rewrite_locations_in_puffin(data, old_location, new_location):
    """Rewrite ``referenced-data-file`` blob properties in a Puffin footer.

    Only the footer is rebuilt; the leading magic and the blob region are
    kept byte-identical so every manifest-declared blob offset stays
    correct. The footer flags are preserved (Spark writes the footer
    payload uncompressed, which parsing already relies on)."""
    footer = puffin_steps.parse_puffin_footer(data)
    for blob in footer.get("blobs", []):
        properties = blob.get("properties") or {}
        referenced = properties.get("referenced-data-file")
        if referenced:
            properties["referenced-data-file"] = referenced.replace(
                old_location, new_location
            )

    old_payload_size = struct.unpack("<I", data[-12:-8])[0]
    blob_region = data[: len(data) - old_payload_size - 16]
    new_payload = json.dumps(footer).encode("utf-8")
    return (
        blob_region
        + puffin_steps.PUFFIN_MAGIC
        + new_payload
        + struct.pack("<I", len(new_payload))
        + data[-8:-4]  # original footer flags
        + puffin_steps.PUFFIN_MAGIC
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
    container_id = node.cluster.node_container_id(node=node.name)

    try:
        with By("staging the rewritten table tree on the host"):
            with tempfile.TemporaryDirectory(prefix="dv_local_") as staging:
                for key in s3_objects.list_keys(table.prefix):
                    data = s3_objects.get_object_bytes(key)
                    relative = key[len(table.prefix) :].lstrip("/")

                    if key.endswith(".metadata.json"):
                        text = data.decode("utf-8").replace(old_location, local_dir)
                        data = text.encode("utf-8")
                    elif key.endswith(".avro"):
                        data = _rewrite_locations_in_avro(data, old_location, local_dir)
                    elif key.endswith(".puffin"):
                        data = _rewrite_locations_in_puffin(
                            data, old_location, local_dir
                        )

                    destination = os.path.join(staging, relative)
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    with open(destination, "wb") as f:
                        f.write(data)

                with By("copying it into the node with docker cp"):
                    node.command(f"mkdir -p {local_dir}", exitcode=0)
                    subprocess.run(
                        ["docker", "cp", f"{staging}/.", f"{container_id}:{local_dir}"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    node.command(f"chmod -R a+rX {local_dir}", exitcode=0)

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
