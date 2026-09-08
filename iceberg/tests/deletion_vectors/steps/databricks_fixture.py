"""The authentic Databricks UniForm table whose deletion vector is a Delta
``.bin`` object.

Every other Delta scenario in this suite *crafts* its containers: the harness
writes the version byte and the blob itself. That leaves one blind spot no
amount of crafting can cover — if our writer and ClickHouse's reader shared
the same misreading of the format, the crafted tests would agree with each
other and pass. This table is the one input the harness did not write. It is
the customer table from the upstream fix (Altinity/ClickHouse#2271), carried
here byte for byte under ``../fixtures/databricks_uniform_v3``.

Databricks writes Iceberg metadata under ``_iceberg/metadata/`` while data
files and deletion vectors sit on the parent table root, and every path in the
metadata is an absolute URI into the customer's own bucket. Installing the
table therefore means uploading the tree to the test warehouse with
``_iceberg/metadata`` flattened to ``metadata/`` and every Databricks URI
rewritten onto the new location, which is the same preparation upstream's own
integration test performs.

The bytes are never regenerated: the ``.bin``, the Parquet data file and the
Avro manifests are the customer's. Only path strings change.

One consequence is worth stating up front, because it looks like a bug the
first time it is noticed: this blob is *not* byte-comparable with one our
writer builds for the same positions. Databricks run-length-encodes the
roaring containers and the harness does not, so the same 1000 positions are
251 bytes here and 2040 there. Both are valid roaring — which makes this
fixture the only place in the suite where the run-encoded form is decoded at
all.
"""

import gzip
import json
import pathlib

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.manifest as manifest_steps
import iceberg.tests.deletion_vectors.steps.puffin as puffin_steps
import iceberg.tests.deletion_vectors.steps.common as common

FIXTURE_DIR = (
    pathlib.Path(__file__).parent.parent / "fixtures" / "databricks_uniform_v3"
)

DV_BIN_NAME = "deletion_vector_3d169d0e-b938-4854-8cca-d9d38949f1b0.bin"
DATA_FILE_NAME = "jk/part-00000-c0585bde-5e01-4bc7-b94d-2e5639a05e68.c000.zstd.parquet"

# table root the customer's Databricks workspace wrote into every path
DATABRICKS_TABLE_PREFIX = (
    "s3://ttd-unity-useast/env=test/__unitystorage/catalogs/"
    "c137d337-b630-4388-b072-9dc88ee567d6/tables/c771d2d4-eac8-401b-b26d-232b2b8fae5a"
)

# what the table contains: 10000 rows with Id "1".."10000", then
# DELETE WHERE cast(Id as int) <= 1000 recorded as 1000 positions in the .bin
TOTAL_ROWS = 10000
DELETED_ROWS = 1000
FIRST_LIVE_ID = 1001
LIVE_ROWS = TOTAL_ROWS - DELETED_ROWS

# The manifest entry as Databricks wrote it, asserted on install. The
# customer's Delta transaction log describes the same object as
# ``{"offset": 1, "sizeInBytes": 243, "cardinality": 1000}`` — Delta measures
# only the envelope's length-prefixed body while Iceberg's
# ``content_size_in_bytes`` also covers the 4-byte length prefix and the 4-byte
# CRC around it, which is the ``+ 8`` in the reader's size check.
DECLARED_FORMAT = "PUFFIN"
DECLARED_CONTENT_OFFSET = 1
DECLARED_CONTENT_SIZE = 251
DV_BIN_SIZE = DECLARED_CONTENT_SIZE + 1

# Databricks serialized these 1000 positions with run-length-encoded roaring
# containers, in 251 bytes. The harness' own writer encodes the very same
# positions as array containers, in 2040 — both valid roaring, so the two are
# not byte-comparable and this fixture is the only place in the suite where
# ClickHouse has to decode the run-encoded form.
# Offset of the serial cookie inside the blob: 4-byte length prefix, 4-byte
# deletion-vector magic, 4-byte bitmap count, 8-byte high key.
ROARING_COOKIE_OFFSET = 20
ROARING_SERIAL_COOKIE_WITH_RUNS = 12347


def rewrite_paths(value, new_prefix):
    """Repoint one Databricks path (or every path nested in a record) at
    *new_prefix*, flattening the ``_iceberg`` metadata directory.

    Databricks keeps the Iceberg metadata in a ``_iceberg`` subdirectory but
    writes data files to the parent, so the table ``location`` is the
    subdirectory while the data paths are above it. Flattening metadata to
    ``metadata/`` and pointing ``location`` at the parent puts both under one
    root, which is what lets a plain ``icebergS3(url)`` resolve them.
    """
    if isinstance(value, str):
        rewritten = value.replace(DATABRICKS_TABLE_PREFIX, new_prefix)
        rewritten = rewritten.replace("/_iceberg/metadata", "/metadata")
        if rewritten.endswith("/_iceberg"):
            return rewritten[: -len("/_iceberg")]
        return rewritten
    if isinstance(value, list):
        return [rewrite_paths(item, new_prefix) for item in value]
    if isinstance(value, dict):
        return {key: rewrite_paths(item, new_prefix) for key, item in value.items()}
    return value


@TestStep(Given)
def databricks_uniform_table(self, namespace=None, table_name=None):
    """Upload the Databricks UniForm fixture as a fresh table and return it.

    The table exists only as objects: nothing registers it with the REST
    catalog, which is exactly how ClickHouse meets a customer table through
    ``icebergS3(url)``. It is still registered for suite teardown — cleanup
    treats a table the catalog does not know as already dropped and removes
    its objects.
    """
    namespace = namespace or f"dv_{getuid()}"
    table_name = table_name or f"table_{getuid()}"

    registry = getattr(self.context, "spark_created_tables", None)
    if registry is not None:
        registry.append((namespace, table_name))

    prefix = s3_objects.table_prefix(namespace, table_name)
    new_prefix = f"s3://{s3_objects.WAREHOUSE_BUCKET}/{prefix}"

    with By("uploading the deletion vector and the data file unchanged"):
        s3_objects.put_object_bytes(
            f"{prefix}/{DV_BIN_NAME}", (FIXTURE_DIR / DV_BIN_NAME).read_bytes()
        )
        s3_objects.put_object_bytes(
            f"{prefix}/{DATA_FILE_NAME}", (FIXTURE_DIR / DATA_FILE_NAME).read_bytes()
        )

    with And("uploading the metadata chain with Databricks paths rewritten"):
        for source in sorted((FIXTURE_DIR / "_iceberg" / "metadata").iterdir()):
            key = f"{prefix}/metadata/{source.name}"
            if source.name.endswith(".gz.metadata.json"):
                metadata = json.loads(gzip.decompress(source.read_bytes()))
                rewritten = json.dumps(
                    rewrite_paths(metadata, new_prefix), separators=(",", ":")
                )
                s3_objects.put_object_bytes(
                    key, gzip.compress(rewritten.encode("utf-8"))
                )
            else:
                # upload first, then rewrite through the suite's own Avro
                # round-trip so the writer schema, file metadata and codec
                # survive exactly as they do for a Spark-written manifest
                s3_objects.put_object_bytes(key, source.read_bytes())
                records, schema, metadata, codec = manifest_steps.read_avro(key)
                manifest_steps.write_avro(
                    key,
                    [rewrite_paths(record, new_prefix) for record in records],
                    schema,
                    metadata,
                    codec,
                )

    table = common.DVTable(namespace, table_name)

    with And("verifying the fixture is the Databricks layout it claims to be"):
        assert_fixture_layout(table=table)

    return table


@TestStep(Then)
def assert_fixture_layout(self, table):
    """The installed table still has the properties that make it a
    regression test for the Delta container.

    Path rewriting must not have touched the bytes, and the entry must still
    be the customer's odd combination — ``file_format = PUFFIN`` over an
    object that is not a Puffin file. If any of this drifted, a passing read
    below would prove nothing about ``.bin`` support.
    """
    dv_bytes = s3_objects.get_object_bytes(f"{table.prefix}/{DV_BIN_NAME}")

    assert len(dv_bytes) == DV_BIN_SIZE, error(
        f"deletion vector object is {len(dv_bytes)} bytes, "
        f"expected the customer's {DV_BIN_SIZE}"
    )
    assert dv_bytes[:1] == b"\x01", error(
        f"expected a Delta format version byte 0x01, got {dv_bytes[:4].hex()}"
    )
    assert dv_bytes[:4] != b"PFA1", error("fixture object is a Puffin file")

    entries = manifest_steps.find_dv_entries(table.namespace, table.table_name)
    assert len(entries) == 1, error(
        f"expected exactly one live deletion-vector entry, found {len(entries)}"
    )

    data_file = entries[0]["entry"]["data_file"]
    assert data_file["file_format"] == DECLARED_FORMAT, error(
        f"entry declares file_format {data_file['file_format']}, "
        f"expected the Databricks {DECLARED_FORMAT}"
    )
    assert data_file["content_offset"] == DECLARED_CONTENT_OFFSET, error(
        f"entry declares content_offset {data_file['content_offset']}, "
        f"expected {DECLARED_CONTENT_OFFSET} (past the version byte)"
    )
    assert data_file["content_size_in_bytes"] == DECLARED_CONTENT_SIZE, error(
        f"entry declares content_size_in_bytes "
        f"{data_file['content_size_in_bytes']}, expected {DECLARED_CONTENT_SIZE}"
    )
    assert data_file["record_count"] == DELETED_ROWS, error(
        f"entry declares {data_file['record_count']} deleted positions, "
        f"expected {DELETED_ROWS}"
    )
    assert data_file["file_path"].endswith(DV_BIN_NAME), error(
        f"entry points at {data_file['file_path']}, expected the .bin object"
    )

    blob = dv_bytes[
        DECLARED_CONTENT_OFFSET : DECLARED_CONTENT_OFFSET + DECLARED_CONTENT_SIZE
    ]
    positions = puffin_steps.dv_positions_of_payload(blob)
    assert len(positions) == DELETED_ROWS, error(
        f"the blob carries {len(positions)} positions, expected {DELETED_ROWS}"
    )

    cookie = int.from_bytes(
        blob[ROARING_COOKIE_OFFSET : ROARING_COOKIE_OFFSET + 2], "little"
    )
    assert cookie == ROARING_SERIAL_COOKIE_WITH_RUNS, error(
        f"the bitmap's serial cookie is {cookie}, expected "
        f"{ROARING_SERIAL_COOKIE_WITH_RUNS} — this fixture is the suite's only "
        f"run-encoded bitmap and the whole point is that no crafted blob "
        f"produces one"
    )
