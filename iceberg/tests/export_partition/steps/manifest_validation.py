"""PyIceberg-based validation of Iceberg metadata produced by EXPORT PARTITION.

The helpers in this module open the destination table directly through
PyIceberg (rather than through ClickHouse) so that:

* tests can assert on fields that ClickHouse does not surface (snapshot
  parents, manifest counts, partition summaries, file-level stats);
* regressions in the ClickHouse-written metadata show up even if ClickHouse
  reads back its own malformed files happily.

All helpers take the ``destination`` object returned by
:func:`steps.iceberg_destination.create_iceberg_destination` along with the
MinIO credentials, and dispatch internally:

* ``rest`` / ``glue`` modes use the ``pyiceberg_catalog`` handle attached to
  the destination dict (created by ``iceberg.tests.steps.catalog``).
* ``no_catalog`` mode scans MinIO for the newest ``*.metadata.json`` under
  the IcebergS3 table's prefix and loads it as a :class:`StaticTable`.

ClickHouse / PyIceberg interop note
-----------------------------------

For *non-empty* manifest-list and manifest-entry Avro files, the Avro C++
library used by ClickHouse strips every Iceberg-specific annotation from
the schema it embeds in the OCF header: ``field-id`` on record fields,
``element-id`` on arrays, and ``key-id`` / ``value-id`` on maps. See
``Storages/ObjectStorage/DataLakes/Iceberg/IcebergWrites.cpp`` around the
``DataFileWriter`` construction — the manual-OCF-header workaround they
ship there only covers the empty-manifest-list case.

PyIceberg's ``AvroSchemaConversion`` is strict about these and refuses to
parse schemas without them; even when the structural parse is made lenient,
PyIceberg's downstream ``resolve_reader`` matches writer and reader
schemas by **id**, so synthetic ids break resolution against PyIceberg's
hardcoded ``MANIFEST_LIST_FILE_SCHEMAS`` / ``MANIFEST_ENTRY_SCHEMAS``.

We install two complementary one-time monkey-patches at module import:

1. :func:`AvroFileHeader.get_schema` is wrapped so that, when the embedded
   Avro schema's top-level record is ``manifest_file`` or
   ``manifest_entry``, we **walk it in parallel with the matching
   canonical PyIceberg schema and inject the canonical ids into the Avro
   JSON in place (by field name / structural position) before letting
   :class:`AvroSchemaConversion` convert it**. The writer schema we
   return therefore has the *same ids* as the read schema PyIceberg uses
   internally (``MANIFEST_LIST_FILE_SCHEMAS[v]`` / ``MANIFEST_ENTRY_SCHEMAS[v]``),
   so ``resolve_reader`` can align them, *and* keeps the same field set
   and ordering as what ClickHouse actually wrote — so the binary decoder
   does not walk off the end when ClickHouse omits fields the canonical
   schema marks as optional (e.g. ``key_metadata`` on manifest lists).
2. :class:`AvroSchemaConversion` has its ``_convert_field`` /
   ``_convert_array_type`` / ``_convert_map_type`` methods wrapped to
   assign synthetic (negative, monotonically decreasing) ids when any
   Iceberg annotation is still missing after step 1. This is a safety
   net for fields that have no canonical counterpart (e.g. dynamic
   partition-spec fields inside ``data_file.partition``) and for any
   non-manifest Avro files that may flow through in the future.

Once ClickHouse learns to preserve Iceberg-spec ids both patches become
no-ops: every annotation will be present and neither code path triggers.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_WAREHOUSE_BUCKET,
    as_destination_name,
    as_pyiceberg_handle,
)


def _install_avro_schema_workarounds():
    """Install the two patches described in the module docstring.

    Idempotent: reruns (or repeat imports) do not stack patches.
    """
    import json

    from pyiceberg.avro import file as avro_file
    from pyiceberg.manifest import (
        MANIFEST_ENTRY_SCHEMAS,
        MANIFEST_LIST_FILE_SCHEMAS,
    )
    from pyiceberg.types import ListType, MapType, NestedField, StructType
    from pyiceberg.utils import schema_conversion

    # --- Patch 1: AvroSchemaConversion synthetic-id fallback ---------------

    conv_cls = schema_conversion.AvroSchemaConversion
    if not getattr(conv_cls, "_clickhouse_export_patched", False):
        next_synthetic_id = [-1_000_000]

        def _assign():
            value = next_synthetic_id[0]
            next_synthetic_id[0] -= 1
            return value

        original_convert_field = conv_cls._convert_field
        original_convert_array = conv_cls._convert_array_type
        original_convert_map = conv_cls._convert_map_type

        def patched_convert_field(self, field):
            if "field-id" not in field:
                field = dict(field)
                field["field-id"] = _assign()
            return original_convert_field(self, field)

        def patched_convert_array(self, array_type):
            if "element-id" not in array_type:
                array_type = dict(array_type)
                array_type["element-id"] = _assign()
            return original_convert_array(self, array_type)

        def patched_convert_map(self, map_type):
            if "key-id" not in map_type or "value-id" not in map_type:
                map_type = dict(map_type)
                map_type.setdefault("key-id", _assign())
                map_type.setdefault("value-id", _assign())
            return original_convert_map(self, map_type)

        conv_cls._convert_field = patched_convert_field
        conv_cls._convert_array_type = patched_convert_array
        conv_cls._convert_map_type = patched_convert_map
        conv_cls._clickhouse_export_patched = True

    # --- Patch 2: annotate Avro schema with canonical ids before converting

    header_cls = avro_file.AvroFileHeader
    if not getattr(header_cls, "_clickhouse_export_patched", False):
        canonical_by_record_name = {
            "manifest_file": MANIFEST_LIST_FILE_SCHEMAS,
            "manifest_entry": MANIFEST_ENTRY_SCHEMAS,
        }

        def _pick_canonical_version(avro_schema, versions):
            """Pick the canonical schema whose top-level field names are a
            superset of what ClickHouse wrote. ClickHouse may omit
            optional fields (e.g. ``key_metadata`` on manifest lists);
            we want the latest version that still *contains* every name
            the writer used so every writer field gets a canonical id."""
            avro_names = {f["name"] for f in avro_schema.get("fields", [])}
            best = None
            for version in sorted(versions.keys()):
                canonical = versions[version]
                canonical_names = {f.name for f in canonical.fields}
                if avro_names <= canonical_names:
                    best = canonical
            return best if best is not None else versions[max(versions.keys())]

        def _unwrap_union_type(avro_type):
            """Return the non-null branch of an Avro union ``[..., "null", ...]``.
            Passes through non-union types unchanged."""
            if isinstance(avro_type, list):
                for alt in avro_type:
                    if alt != "null":
                        return alt
                return None
            return avro_type

        def _annotate_type(avro_type, canonical_type):
            """Recurse into records / arrays / maps, injecting canonical ids
            into the Avro dict wherever they are missing. Does not mutate
            primitives or unknown canonical subtrees.

            ClickHouse encodes Iceberg ``MapType`` using Avro's "logical map"
            representation (an array of ``{key, value}`` records) rather
            than Avro's native ``map`` type. The Avro C++ library strips
            the ``logicalType: "map"`` annotation along with every
            ``field-id`` when writing, so by the time PyIceberg parses the
            embedded schema the field looks like a plain Avro array of
            records and would be converted to ``ListType`` — breaking
            alignment with the canonical reader schema's ``MapType``.

            When the canonical partner at a given position is a ``MapType``
            we therefore:

            1. inject ``logicalType: "map"`` back onto the array wrapper so
               PyIceberg's ``_convert_logical_map_type`` dispatches; and
            2. inject the canonical ``key_id`` / ``value_id`` as ``field-id``
               on the inner ``key`` / ``value`` fields, which is where
               ``_convert_logical_map_type`` reads them from.
            """
            inner = _unwrap_union_type(avro_type)
            if not isinstance(inner, dict) or canonical_type is None:
                return

            kind = inner.get("type")

            if kind == "record" and isinstance(canonical_type, StructType):
                by_name = {f.name: f for f in canonical_type.fields}
                for field_dict in inner.get("fields", []) or []:
                    cfield = by_name.get(field_dict.get("name"))
                    if cfield is None:
                        continue
                    field_dict.setdefault("field-id", cfield.field_id)
                    _annotate_type(field_dict.get("type"), cfield.field_type)
            elif kind == "array" and isinstance(canonical_type, MapType):
                inner.setdefault("logicalType", "map")
                items = inner.get("items")
                if isinstance(items, dict):
                    for kv_field in items.get("fields", []) or []:
                        name = kv_field.get("name")
                        if name == "key":
                            kv_field.setdefault("field-id", canonical_type.key_id)
                        elif name == "value":
                            kv_field.setdefault("field-id", canonical_type.value_id)
                            _annotate_type(
                                kv_field.get("type"), canonical_type.value_type
                            )
            elif kind == "array" and isinstance(canonical_type, ListType):
                inner.setdefault("element-id", canonical_type.element_id)
                _annotate_type(inner.get("items"), canonical_type.element_type)
            elif kind == "map" and isinstance(canonical_type, MapType):
                inner.setdefault("key-id", canonical_type.key_id)
                inner.setdefault("value-id", canonical_type.value_id)
                _annotate_type(inner.get("values"), canonical_type.value_type)

        def _annotate_top_level(avro_schema, canonical_schema):
            """Inject canonical ids into the top-level record of ``avro_schema``."""
            by_name = {f.name: f for f in canonical_schema.fields}
            for field_dict in avro_schema.get("fields", []) or []:
                cfield = by_name.get(field_dict.get("name"))
                if cfield is None:
                    continue
                field_dict.setdefault("field-id", cfield.field_id)
                _annotate_type(field_dict.get("type"), cfield.field_type)

        original_get_schema = header_cls.get_schema

        def patched_get_schema(self):
            schema_json = self.meta.get("avro.schema")
            if not schema_json:
                return original_get_schema(self)
            try:
                avro_schema = json.loads(schema_json)
            except (ValueError, TypeError):
                return original_get_schema(self)
            if not isinstance(avro_schema, dict):
                return original_get_schema(self)

            versions = canonical_by_record_name.get(avro_schema.get("name"))
            if versions is None:
                return original_get_schema(self)

            canonical = _pick_canonical_version(avro_schema, versions)
            _annotate_top_level(avro_schema, canonical)
            return conv_cls().avro_to_iceberg(avro_schema)

        header_cls.get_schema = patched_get_schema
        header_cls._clickhouse_export_patched = True


_install_avro_schema_workarounds()


HOST_MINIO_ENDPOINT = "http://localhost:9002"


def _latest_metadata_location(
    minio_root_user,
    minio_root_password,
    bucket,
    table_prefix,
    endpoint_url=HOST_MINIO_ENDPOINT,
):
    """Return ``s3://<bucket>/<key>`` of the newest ``*.metadata.json`` below
    ``s3://<bucket>/<table_prefix>/metadata/``.
    """
    import boto3

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=minio_root_user,
        aws_secret_access_key=minio_root_password,
    )

    paginator = s3.get_paginator("list_objects_v2")
    candidates = []
    for page in paginator.paginate(Bucket=bucket, Prefix=f"{table_prefix}/metadata/"):
        for obj in page.get("Contents", []) or []:
            if obj["Key"].endswith(".metadata.json"):
                candidates.append(obj)

    assert candidates, error(
        f"No *.metadata.json under s3://{bucket}/{table_prefix}/metadata/"
    )

    candidates.sort(key=lambda o: (o["LastModified"], o["Key"]), reverse=True)
    return f"s3://{bucket}/{candidates[0]['Key']}"


def load_pyiceberg_table(
    destination,
    minio_root_user,
    minio_root_password,
    bucket=DEFAULT_S3_WAREHOUSE_BUCKET,
    no_catalog_prefix_root="data",
    endpoint_url=HOST_MINIO_ENDPOINT,
):
    """Load the destination as a PyIceberg ``Table`` regardless of catalog mode.

    Callers should refresh the returned table before asserting on the
    current snapshot if a ``EXPORT PARTITION`` was just issued - PyIceberg
    caches metadata otherwise.
    """
    handle = as_pyiceberg_handle(destination)
    if handle is not None:
        catalog = handle["pyiceberg_catalog"]
        table = catalog.load_table(f"{handle['namespace']}.{handle['table_name']}")
        table.refresh()
        return table

    from pyiceberg.table import StaticTable

    table_name = as_destination_name(destination)
    metadata_location = _latest_metadata_location(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        bucket=bucket,
        table_prefix=f"{no_catalog_prefix_root}/{table_name}",
        endpoint_url=endpoint_url,
    )
    properties = {
        "s3.endpoint": endpoint_url,
        "s3.access-key-id": minio_root_user,
        "s3.secret-access-key": minio_root_password,
    }
    return StaticTable.from_metadata(metadata_location, properties)


@TestStep(Then)
def get_snapshots(self, destination, minio_root_user, minio_root_password):
    """Return the full snapshot history (ordered by metadata order)."""
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    return list(table.snapshots())


@TestStep(Then)
def get_current_snapshot_summary(
    self, destination, minio_root_user, minio_root_password
):
    """Return the ``summary`` of the current snapshot as a plain ``{str: str}`` dict.

    PyIceberg's ``Summary`` is a pydantic model with a map-style ``__getitem__``
    that expects string keys (it calls ``.lower()`` on them); passing it to
    ``dict(...)`` triggers pydantic's field iteration which returns tuples and
    breaks that lookup. We instead pull from ``additional_properties`` directly
    and tack on ``operation`` so callers see every summary key.
    """
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    snapshot = table.current_snapshot()
    assert snapshot is not None, error(
        f"Destination {as_destination_name(destination)} has no current snapshot"
    )
    summary = snapshot.summary
    if summary is None:
        return {}
    result = dict(summary.additional_properties or {})
    operation = getattr(summary, "operation", None)
    if operation is not None:
        result["operation"] = str(getattr(operation, "value", operation))
    return result


@TestStep(Then)
def assert_snapshot_advanced(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    minimum_snapshots=1,
):
    """Assert that at least ``minimum_snapshots`` snapshots exist and that
    ``current_snapshot`` is set.
    """
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    snapshots = list(table.snapshots())
    assert len(snapshots) >= minimum_snapshots, error(
        f"Expected at least {minimum_snapshots} snapshot(s) for "
        f"{as_destination_name(destination)}, got {len(snapshots)}"
    )
    assert table.current_snapshot() is not None, error(
        f"Destination {as_destination_name(destination)} has no current snapshot"
    )


@TestStep(Then)
def assert_snapshot_row_count(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    expected,
):
    """Assert that the current snapshot summary reports ``expected`` total rows.

    Iceberg stores this in ``total-records`` on the snapshot summary.
    """
    summary = get_current_snapshot_summary(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    total_records = int(summary.get("total-records", "0"))
    assert total_records == expected, error(
        f"Expected total-records = {expected} in current snapshot summary "
        f"of {as_destination_name(destination)}, got {total_records}. "
        f"Summary: {summary!r}"
    )


@TestStep(Then)
def get_data_files(self, destination, minio_root_user, minio_root_password):
    """Return every data file referenced by the current snapshot."""
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    snapshot = table.current_snapshot()
    assert snapshot is not None, error(
        f"Destination {as_destination_name(destination)} has no current snapshot"
    )
    data_files = []
    for manifest in snapshot.manifests(table.io):
        for entry in manifest.fetch_manifest_entry(table.io):
            data_files.append(entry.data_file)
    return data_files


@TestStep(Then)
def assert_manifest_spec_matches_partition(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    expected_source_columns,
):
    """Assert that the table's partition spec references the given source
    columns by name, in order.

    ``expected_source_columns`` is a list of source column names (pre-transform).
    """
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    spec = table.spec()
    schema = table.schema()

    source_ids = [f.source_id for f in spec.fields]
    source_names = [schema.find_column_name(sid) for sid in source_ids]

    assert source_names == list(expected_source_columns), error(
        f"Expected partition spec source columns {list(expected_source_columns)!r} "
        f"for {as_destination_name(destination)}, got {source_names!r}"
    )


@TestStep(Then)
def assert_column_stats_present(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    required_stats=(
        "column_sizes",
        "null_value_counts",
        "lower_bounds",
        "upper_bounds",
    ),
):
    """Assert that every data file has non-empty statistics for each entry in
    ``required_stats``.

    A regression here silently disables predicate push-down and
    partition-pruning at read time.

    NOTE: ``value_counts`` is intentionally not in the default
    ``required_stats``. As of the current EXPORT PARTITION implementation
    in ClickHouse (``IcebergWrites.cpp`` / ``IcebergDataFileEntry.h``),
    the ``value_counts`` map is declared in the Avro schema but is never
    populated on the write path (the struct carries only ``column_sizes``,
    ``null_value_counts``, ``lower_bounds`` and ``upper_bounds``).
    A dedicated XFail scenario in ``manifest_integrity.py`` covers
    ``value_counts`` so that the gap is visible and flips to a pass
    automatically once ClickHouse starts writing it.
    """
    data_files = get_data_files(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    assert data_files, error(
        f"No data files in current snapshot of {as_destination_name(destination)}"
    )

    missing = []
    for data_file in data_files:
        for stat in required_stats:
            value = getattr(data_file, stat, None)
            if not value:
                missing.append((data_file.file_path, stat))

    assert not missing, error(
        f"Missing column stats in {as_destination_name(destination)}: {missing!r}"
    )


@TestStep(Then)
def assert_value_counts_sum_to(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    expected_total,
):
    """For each column, assert ``sum(data_file.value_counts[field_id]) == expected_total``.

    This cross-checks the per-file statistics against the total row count
    without needing to decode ``lower_bounds`` / ``upper_bounds`` bytes.
    """
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    data_files = get_data_files(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    schema = table.schema()

    per_column_totals = {}
    for data_file in data_files:
        for field_id, count in (data_file.value_counts or {}).items():
            per_column_totals[field_id] = per_column_totals.get(field_id, 0) + count

    bad = []
    for field in schema.fields:
        total = per_column_totals.get(field.field_id, 0)
        if total != expected_total:
            bad.append((field.name, field.field_id, total))

    assert not bad, error(
        f"value_counts do not sum to {expected_total} for "
        f"{as_destination_name(destination)}: {bad!r}"
    )


@TestStep(Then)
def assert_file_paths_under_prefix(
    self,
    destination,
    minio_root_user,
    minio_root_password,
    expected_prefix,
):
    """Assert that every data file's path begins with ``expected_prefix``.

    Useful when validating ``write_full_path_in_iceberg_metadata`` and mixed
    storage paths.
    """
    data_files = get_data_files(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    bad_paths = [
        df.file_path for df in data_files if not df.file_path.startswith(expected_prefix)
    ]
    assert not bad_paths, error(
        f"Data files not under expected prefix {expected_prefix!r} in "
        f"{as_destination_name(destination)}: {bad_paths!r}"
    )
