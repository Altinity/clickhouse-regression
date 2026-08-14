"""Avro manifest / manifest-list rewriting for the corruption harness.

Iceberg metadata is a chain: table metadata JSON → manifest list (Avro) →
manifests (Avro) → data / delete files. The error-handling requirements
need internally inconsistent metadata (negative record counts, duplicate
deletion-vector entries, out-of-bounds blob locations, ...), which no real
writer will produce — so these steps download the Avro objects a Spark
commit wrote, mutate entries with fastavro, and upload them back **to the
same keys**, keeping the rest of the chain intact.

All rewrites preserve the embedded writer schema, file metadata and codec,
except where a defect explicitly requires a schema tweak (e.g. making
``record_count`` nullable so an entry can lack it).
"""

import copy
import io

import fastavro

from testflows.core import *

from iceberg.tests.deletion_vectors.steps import puffin
from iceberg.tests.deletion_vectors.steps import s3_objects

DATA_CONTENT = 0
POSITION_DELETES_CONTENT = 1
EQUALITY_DELETES_CONTENT = 2

# manifest_list entry field ``content`` values
MANIFEST_LIST_DATA = 0
MANIFEST_LIST_DELETES = 1


def read_avro(key):
    """Read an Avro object → (records, writer_schema, metadata, codec)."""
    reader = fastavro.reader(io.BytesIO(s3_objects.get_object_bytes(key)))
    records = [copy.deepcopy(record) for record in reader]
    metadata = {
        name: value
        for name, value in reader.metadata.items()
        if not name.startswith("avro.")
    }
    return records, reader.writer_schema, metadata, reader.codec


def write_avro(key, records, schema, metadata, codec):
    """Serialize records with the given schema/metadata/codec and upload."""
    out = io.BytesIO()
    fastavro.writer(out, schema, records, codec=codec, metadata=metadata)
    s3_objects.put_object_bytes(key, out.getvalue())
    return len(out.getvalue())


def _sync_manifest_length(namespace, table_name, manifest_key, new_length):
    """Update ``manifest_length`` of *manifest_key* in the current
    snapshot's manifest list after the manifest was rewritten in place."""
    list_key = s3_objects.manifest_list_key(namespace, table_name)
    records, schema, metadata, codec = read_avro(list_key)
    for record in records:
        if s3_objects.key_from_uri(record["manifest_path"]).endswith(manifest_key):
            record["manifest_length"] = new_length
    write_avro(list_key, records, schema, metadata, codec)


def manifest_keys(namespace, table_name, content=None):
    """Manifest object keys of the current snapshot, optionally filtered by
    manifest-list ``content`` (0 = data manifests, 1 = delete manifests)."""
    list_key = s3_objects.manifest_list_key(namespace, table_name)
    records, _, _, _ = read_avro(list_key)
    keys = []
    for record in records:
        if content is None or record.get("content", MANIFEST_LIST_DATA) == content:
            keys.append(s3_objects.key_from_uri(record["manifest_path"]))
    return keys


def is_dv_entry(entry):
    """True for a live deletion-vector manifest entry (a position-delete
    entry whose file is a Puffin file)."""
    data_file = entry["data_file"]
    return data_file.get("content") == POSITION_DELETES_CONTENT and data_file[
        "file_path"
    ].endswith(".puffin")


def find_dv_entries(namespace, table_name):
    """All live deletion-vector entries of the current snapshot.

    Returns a list of dicts: {"manifest_key", "entry"}.
    """
    found = []
    for key in manifest_keys(namespace, table_name, content=MANIFEST_LIST_DELETES):
        records, _, _, _ = read_avro(key)
        for entry in records:
            if entry["status"] != 2 and is_dv_entry(entry):  # 2 = DELETED
                found.append({"manifest_key": key, "entry": entry})
    return found


def live_data_files(namespace, table_name):
    """``data_file`` records of every live data entry in the current
    snapshot — for asserting the physical layout that position-based
    expectations depend on."""
    files = []
    for key in manifest_keys(namespace, table_name, content=MANIFEST_LIST_DATA):
        records, _, _, _ = read_avro(key)
        for entry in records:
            if entry["status"] != 2:  # 2 = DELETED
                files.append(entry["data_file"])
    return files


@TestStep(When)
def mutate_manifest_entries(
    self, namespace, table_name, mutator, content=None, only_manifest_key=None
):
    """Rewrite manifest entries of the current snapshot in place.

    Only manifests whose entries actually changed are re-uploaded, keeping
    the mutation surface limited to the defect under test.

    Args:
        mutator: function(entry) → entry | list of entries | None (drop).
            Applied to every entry of every matching manifest. Mutating the
            entry dict in place and returning it is supported.
        content: restrict to data (0) or delete (1) manifests; None = all.
        only_manifest_key: restrict the rewrite to this one manifest.
    """
    for key in manifest_keys(namespace, table_name, content=content):
        if only_manifest_key is not None and key != only_manifest_key:
            continue
        records, schema, metadata, codec = read_avro(key)
        # mutators may modify entries in place, so change detection must
        # compare against a snapshot taken before they run
        originals = copy.deepcopy(records)
        new_records = []
        for entry in records:
            result = mutator(entry)
            if result is None:
                continue
            if isinstance(result, list):
                new_records.extend(result)
            else:
                new_records.append(result)
        if new_records == originals:
            continue
        new_length = write_avro(key, new_records, schema, metadata, codec)
        _sync_manifest_length(namespace, table_name, key, new_length)


def make_data_file_field_nullable(schema, field_name):
    """Return a deep copy of a manifest schema where ``data_file.<field>``
    accepts null (used to build entries that *lack* a required field)."""
    schema = copy.deepcopy(schema)

    def visit(node):
        if isinstance(node, dict):
            if node.get("type") == "record":
                for field in node.get("fields", []):
                    if field["name"] == field_name:
                        field_type = field["type"]
                        if not (isinstance(field_type, list) and "null" in field_type):
                            field["type"] = ["null", field_type]
                            field["default"] = None
                    visit(field["type"])
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(schema)
    return schema


@TestStep(When)
def mutate_manifest_entries_with_nullable_field(
    self, namespace, table_name, field_name, mutator, content=None
):
    """Like :func:`mutate_manifest_entries` but first makes
    ``data_file.<field_name>`` nullable in the writer schema so the mutator
    may set it to None."""
    for key in manifest_keys(namespace, table_name, content=content):
        records, schema, metadata, codec = read_avro(key)
        schema = make_data_file_field_nullable(schema, field_name)
        new_records = [mutator(entry) or entry for entry in records]
        new_length = write_avro(key, new_records, schema, metadata, codec)
        _sync_manifest_length(namespace, table_name, key, new_length)


@TestStep(When)
def replace_deletion_vector(
    self,
    namespace,
    table_name,
    payload=None,
    declared_cardinality=None,
    blob_overrides=None,
    footer_blobs_mutator=None,
    entry_mutator=None,
    puffin_kwargs=None,
):
    """Replace the (single) deletion vector of a table with a synthetic one
    and keep the metadata chain consistent — except for the injected defect.

    The new Puffin file is written to the *same object key* as the original
    (no metadata JSON rewrite needed) and the manifest entry's
    ``content_offset`` / ``content_size_in_bytes`` / ``record_count`` are
    synchronized to the new blob.

    Args:
        payload: new blob bytes (from ``puffin.build_dv_payload``). None →
            keep the writer-produced Puffin file, only mutate manifests.
        declared_cardinality: value for the entry ``record_count`` and the
            footer ``cardinality`` property (default: keep entry's value).
        blob_overrides: dict merged into the footer blob descriptor
            (``type``, ``compression_codec``, ``properties``, ``offset``,
            ``length``...). ``properties`` replaces the whole dict.
        footer_blobs_mutator: function(blob_dicts) → blob_dicts, applied
            before the Puffin file is built (duplicate/drop footer entries).
        entry_mutator: function(entry) applied to the manifest entry last —
            may corrupt any field after the consistent values were set.
        puffin_kwargs: extra keyword arguments for ``puffin.build_puffin``
            (e.g. ``compress_footer`` / ``flags`` for footer-level defects).

    Returns the manifest entry dict as written.
    """
    dv_entries = find_dv_entries(namespace, table_name)
    assert (
        len(dv_entries) == 1
    ), f"expected exactly one deletion-vector entry, found {len(dv_entries)}"
    manifest_key = dv_entries[0]["manifest_key"]
    target_path = dv_entries[0]["entry"]["data_file"]["file_path"]

    written_entry = {}

    def mutator(entry):
        if not (is_dv_entry(entry) and entry["data_file"]["file_path"] == target_path):
            return entry
        data_file = entry["data_file"]
        cardinality = (
            declared_cardinality
            if declared_cardinality is not None
            else data_file["record_count"]
        )

        if payload is not None:
            blob = {
                "payload": payload,
                "properties": {
                    "referenced-data-file": data_file["referenced_data_file"],
                    "cardinality": str(cardinality),
                },
            }
            blob.update(blob_overrides or {})
            blobs = [blob]
            if footer_blobs_mutator is not None:
                blobs = footer_blobs_mutator(blobs)
            file_bytes, _ = puffin.build_puffin(blobs, **(puffin_kwargs or {}))
            s3_objects.put_object_bytes(data_file["file_path"], file_bytes)
            data_file["content_offset"] = 4
            data_file["content_size_in_bytes"] = len(payload)

        data_file["record_count"] = cardinality
        if entry_mutator is not None:
            entry_mutator(entry)
        written_entry.update(entry)
        return entry

    mutate_manifest_entries(
        namespace=namespace,
        table_name=table_name,
        mutator=mutator,
        content=MANIFEST_LIST_DELETES,
    )
    return written_entry


def read_dv_payload(namespace, table_name):
    """Bytes of the single deletion-vector blob of the current snapshot,
    sliced out of its Puffin file by the manifest-declared
    ``content_offset`` / ``content_size_in_bytes`` — for inspecting what
    the writer actually serialized."""
    entries = find_dv_entries(namespace, table_name)
    assert (
        len(entries) == 1
    ), f"expected exactly one deletion-vector entry, found {len(entries)}"
    data_file = entries[0]["entry"]["data_file"]
    blob = s3_objects.get_object_bytes(data_file["file_path"])
    offset = data_file["content_offset"]
    size = data_file["content_size_in_bytes"]
    return blob[offset : offset + size]


@TestStep(When)
def duplicate_dv_entry(self, namespace, table_name):
    """Duplicate the deletion-vector manifest entry so two live entries
    reference the same data file (MultipleVectorsError)."""

    def mutator(entry):
        if is_dv_entry(entry) and entry["status"] != 2:
            return [entry, copy.deepcopy(entry)]
        return entry

    mutate_manifest_entries(
        namespace=namespace,
        table_name=table_name,
        mutator=mutator,
        content=MANIFEST_LIST_DELETES,
    )
