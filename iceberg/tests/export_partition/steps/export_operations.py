"""EXPORT PARTITION and KILL EXPORT PARTITION helpers for the iceberg suite.

Adapted from the s3 export_partition steps. The main adjustments are:

* Waiting for completion is optional (some scenarios need to observe a
  ``PENDING`` state first).
* Supports a list of destination tables per call (useful for fan-out tests).

EXPORT PARTITION needs two ClickHouse experimental flags enabled, and
they live in different layers:

* ``allow_experimental_export_merge_tree_partition`` is a *server*
  setting (declared in ``ServerSettings.cpp``) and is enabled via
  ``configs/clickhouse/config.d/export_partition.xml``.
* ``allow_experimental_insert_into_iceberg`` is a regular per-query
  ``Setting``. The commit/write phase runs on a background context
  that ClickHouse builds from the server context plus a small manifest
  whitelist (see ``ExportPartitionUtils::getContextCopyWithTaskSettings``
  in ``ClickHouse``), and the whitelist does NOT carry this flag —
  so it must be set in the default user profile to take effect on the
  background scheduler. That happens via
  ``configs/clickhouse/users.d/allow_experimental_insert_into_iceberg.xml``.
  We additionally inject it per-query in :func:`export_partition` so
  scenarios that pass an explicit ``settings=`` list keep the
  synchronous gate (``StorageReplicatedMergeTree::exportPartitionToTable``)
  satisfied, matching what :func:`insert_into_iceberg_destination` and
  :func:`truncate_iceberg_destination` already do.
"""

from testflows.core import *

from iceberg.tests.export_partition.steps.common import (
    get_partition_ids,
)
from iceberg.tests.export_partition.steps.export_status import (
    wait_for_export_status,
)
from iceberg.tests.export_partition.steps.export_status import (
    _destination_where_pieces,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
)


# ClickHouse bug workaround (Glue only).
#
# ``IcebergWrites.cpp`` builds the ``metadata_location`` it commits to the
# external catalog with:
#
#     if (!catalog_filename.starts_with(blob_storage_type_name))
#         catalog_filename = blob_storage_type_name + "://"
#                          + blob_storage_namespace_name + "/" + metadata_name;
#
# With ``write_full_path_in_iceberg_metadata = 0`` (the server default),
# ``metadata_name`` already begins with ``/`` (e.g.
# ``/data/iceberg_xxx/metadata/v1.metadata.json``), so the concat produces
# ``s3://warehouse//data/...`` — the double slash between bucket and key.
#
# REST catalogs survive this: ``RestCatalog::updateMetadata`` ignores the
# ``new_metadata_path`` argument and commits via the REST snapshot request
# instead. ``GlueCatalog::updateMetadata`` stores the URI verbatim as
# ``Parameters['metadata_location']``, so every downstream reader
# (DataLakeCatalog SELECTs, PyIceberg ``load_table``, external engines) gets
# the malformed URI and blows up on pyarrow S3 path parsing.
#
# Setting ``write_full_path_in_iceberg_metadata = 1`` makes
# ``metadata_name`` start with ``s3://...`` which takes the
# ``starts_with(blob_storage_type_name)`` branch and keeps the URI clean.
# Force-inject it on every EXPORT under Glue so scenarios that do not
# otherwise care about this setting still commit well-formed URIs.
# Remove this helper once ``IcebergWrites.cpp`` stops prepending ``/`` when
# ``metadata_name`` already begins with one.
_GLUE_FULL_PATHS_SETTING_KEY = "write_full_path_in_iceberg_metadata"


def apply_glue_metadata_path_workaround(context_catalog, settings):
    """Return ``settings`` with the Glue double-slash workaround applied.

    Public because a handful of scenarios build the ``ALTER TABLE ...
    EXPORT PARTITION ..., EXPORT PARTITION ...`` multi-entry form by hand
    (for example :mod:`iceberg.tests.export_partition.sanity` and
    :mod:`iceberg.tests.export_partition.concurrent_writes`) and therefore
    bypass :func:`export_partition`. Those call sites pass their own
    ``settings=`` through here so the same workaround is honoured.

    Only touches settings when ``context_catalog == "glue"``. Honours an
    explicit value already present in ``settings`` so scenarios that
    deliberately toggle the knob (e.g. ``storage_paths``) keep control.
    """
    if context_catalog != "glue":
        return settings
    if settings is None:
        return [(_GLUE_FULL_PATHS_SETTING_KEY, 1)]
    for key, _ in settings:
        if key == _GLUE_FULL_PATHS_SETTING_KEY:
            return settings
    return list(settings) + [(_GLUE_FULL_PATHS_SETTING_KEY, 1)]


# Alias kept for internal call sites that want the module-private spelling.
_apply_glue_metadata_path_workaround = apply_glue_metadata_path_workaround


_INSERT_INTO_ICEBERG_SETTING_KEY = "allow_experimental_insert_into_iceberg"


def prepare_export_partition_settings(context_catalog, settings):
    """Return ``settings`` with every per-query gate EXPORT PARTITION needs.

    ClickHouse gates the Iceberg commit side of ``ALTER TABLE ... EXPORT
    PARTITION ... TO TABLE <iceberg_dest>`` on
    ``allow_experimental_insert_into_iceberg`` at query time (see
    ``StorageReplicatedMergeTree::exportPartitionToTable`` / the
    ``IcebergMetadata::write`` path). The feature itself is enabled
    server-side via ``allow_experimental_export_merge_tree_partition``
    from ``configs/clickhouse/config.d/export_partition.xml``, but that
    setting alone is no longer enough because the commit path is shared
    with INSERT/TRUNCATE.

    Layered on top, ``apply_glue_metadata_path_workaround`` may add
    ``write_full_path_in_iceberg_metadata = 1`` under Glue to sidestep
    the double-slash URI bug.

    Both injections honour an explicit caller-supplied value so
    scenarios that deliberately toggle either knob (e.g.
    :mod:`iceberg.tests.export_partition.settings` or
    :mod:`iceberg.tests.export_partition.storage_paths`) keep full
    control.
    """
    if settings is None:
        settings = []
    else:
        settings = list(settings)

    if not any(key == _INSERT_INTO_ICEBERG_SETTING_KEY for key, _ in settings):
        settings.append((_INSERT_INTO_ICEBERG_SETTING_KEY, 1))

    return apply_glue_metadata_path_workaround(context_catalog, settings)


def _resolve_destination(destination, destination_table):
    """Collapse ``destination`` / ``destination_table`` into the pair of
    values the export helpers need:

    * ``name`` — the fully-qualified SQL identifier suitable for
      ``ALTER TABLE ... TO TABLE <name>`` and ``KILL EXPORT PARTITION
      WHERE destination_table = '<name>'`` (which CH then parses through
      its own StorageID splitter).
    * ``filter_obj`` — the object to hand to
      :func:`iceberg.tests.export_partition.steps.export_status.get_export_row`
      (and friends). Prefer the dict form when available so the filter
      splits ``destination_database`` / ``destination_table`` correctly
      under catalog mode; fall back to the SQL identifier string for the
      no_catalog case.
    """
    if destination is not None:
        name = as_destination_name(destination)
        return name, destination
    return destination_table, destination_table


@TestStep(When)
def export_partition(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    node=None,
    settings=None,
    extra_settings=None,
    exitcode=0,
    message=None,
    wait_for_completion=True,
    wait_timeout=120,
):
    """Run a single ``ALTER TABLE ... EXPORT PARTITION ID ... TO TABLE ...``.

    Args:
        source_table: ReplicatedMergeTree source.
        destination: Preferred way to identify the Iceberg destination —
            either the dict returned by
            :func:`iceberg.tests.export_partition.steps.iceberg_destination.create_iceberg_destination`
            or a plain unqualified string. Callers that already hold the
            destination object should pass it here so the completion poll
            under catalog mode can split ``destination_database`` /
            ``destination_table`` correctly (see
            :func:`iceberg.tests.export_partition.steps.export_status._destination_where_pieces`).
        destination_table: Legacy path that accepts the SQL identifier
            string directly (e.g. the result of ``as_destination_name``).
            Still supported for callers that have already serialised the
            destination to a string; exactly one of
            ``destination`` / ``destination_table`` must be provided.
        partition_id: Partition ID string (as stored in ``system.parts``).
        settings: Full settings list passed directly to ``node.query``; the
            default ``None`` sends the statement without any per-query
            overrides.
        extra_settings: Appended to ``settings`` when ``settings`` is not
            provided; a convenient way to tweak one knob without rebuilding
            the whole list.
        exitcode: Expected exit code for the ``ALTER`` statement. Use ``0``
            (default) for success, or a specific code (e.g. ``36`` for
            ``BAD_ARGUMENTS``) to assert synchronous rejection.
        message: Expected substring in the error output. Typically set
            together with ``exitcode`` when asserting rejection.
        wait_for_completion: If ``True`` and no rejection is expected, block
            until the row in ``system.replicated_partition_exports`` reaches
            ``COMPLETED``.
    """
    if node is None:
        node = self.context.node

    if destination is None and destination_table is None:
        raise ValueError(
            "export_partition requires either destination= or destination_table="
        )
    name, filter_obj = _resolve_destination(destination, destination_table)

    if settings is None and extra_settings:
        settings = list(extra_settings)

    settings = prepare_export_partition_settings(self.context.catalog, settings)

    expect_failure = exitcode != 0 or message is not None

    with By(
        f"running EXPORT PARTITION id '{partition_id}' from "
        f"{source_table} to {name}"
    ):
        result = node.query(
            f"ALTER TABLE {source_table} "
            f"EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {name}",
            settings=settings,
            exitcode=exitcode,
            message=message,
            ignore_exception=expect_failure,
        )

    if wait_for_completion and not expect_failure:
        with And(f"waiting for export of partition '{partition_id}' to complete"):
            wait_for_export_status(
                source_table=source_table,
                destination=filter_obj,
                partition_id=partition_id,
                expected_status="COMPLETED",
                timeout=wait_timeout,
                node=node,
            )

    return result


@TestStep(When)
def export_all_partitions(
    self,
    source_table,
    destination=None,
    destination_table=None,
    node=None,
    settings=None,
    extra_settings=None,
    wait_for_completion=True,
    wait_timeout=120,
):
    """Export every active partition of ``source_table`` sequentially.

    Returns the list of partition IDs that were exported (useful for follow-up
    assertions against the destination).

    Accepts the same ``destination`` / ``destination_table`` split as
    :func:`export_partition`.
    """
    if node is None:
        node = self.context.node

    partition_ids = get_partition_ids(table_name=source_table, node=node)

    for pid in partition_ids:
        export_partition(
            source_table=source_table,
            destination=destination,
            destination_table=destination_table,
            partition_id=pid,
            node=node,
            settings=settings,
            extra_settings=extra_settings,
            wait_for_completion=wait_for_completion,
            wait_timeout=wait_timeout,
        )

    return partition_ids


@TestStep(When)
def insert_into_iceberg_destination(
    self,
    destination,
    values,
    node=None,
    settings=None,
    extra_settings=None,
    exitcode=0,
    message=None,
):
    """Run ``INSERT INTO <iceberg_dest> VALUES ...`` against the
    destination created by :func:`iceberg.tests.export_partition.steps.iceberg_destination.create_iceberg_destination`.

    Writing directly to an Iceberg table is gated server-side by the
    ``allow_experimental_insert_into_iceberg`` setting (see
    ``IcebergMetadata::write`` in ClickHouse), and goes through the same
    ``IcebergWrites.cpp`` commit path as EXPORT PARTITION, so the Glue
    double-slash workaround in
    :func:`apply_glue_metadata_path_workaround` applies here too — we
    bake both in by default and let callers override either through
    ``settings`` / ``extra_settings``.

    Args:
        destination: The dict or string returned by
            :func:`create_iceberg_destination`. Same semantics as
            :func:`export_partition`.
        values: The literal ``VALUES`` payload (e.g. ``"(1, 2020), (2, 2021)"``).
        settings: Full settings list passed to ``node.query``; when
            provided, it is honoured as-is *modulo* the glue workaround
            (``write_full_path_in_iceberg_metadata`` is left alone if
            the caller already set it). The
            ``allow_experimental_insert_into_iceberg`` gate is injected
            unless already present.
        extra_settings: Appended to ``settings`` when ``settings`` is
            not provided.
        exitcode / message: Pass-through assertion knobs for negative
            tests. Default ``0`` expects success.
    """
    if node is None:
        node = self.context.node

    name = as_destination_name(destination)

    if settings is None:
        settings = list(extra_settings) if extra_settings else []
    else:
        settings = list(settings)

    if not any(key == "allow_experimental_insert_into_iceberg" for key, _ in settings):
        settings.append(("allow_experimental_insert_into_iceberg", 1))

    settings = _apply_glue_metadata_path_workaround(
        self.context.catalog, settings
    )

    expect_failure = exitcode != 0 or message is not None

    with By(f"inserting into iceberg destination {name}"):
        return node.query(
            f"INSERT INTO {name} VALUES {values}",
            settings=settings,
            exitcode=exitcode,
            message=message,
            ignore_exception=expect_failure,
        )


@TestStep(When)
def truncate_iceberg_destination(
    self,
    destination,
    node=None,
    settings=None,
    extra_settings=None,
    exitcode=0,
    message=None,
):
    """Run ``TRUNCATE TABLE <iceberg_dest>`` against the destination.

    ``IcebergMetadata::truncate`` in ClickHouse is gated by the same
    ``allow_experimental_insert_into_iceberg`` setting as INSERT (it
    reuses the write path), and commits a fresh metadata.json through
    the catalog the same way, so we reuse the same two defaults:

    * ``allow_experimental_insert_into_iceberg = 1``
    * Glue double-slash workaround via
      :func:`apply_glue_metadata_path_workaround`.

    Note that ``IcebergMetadata.cpp`` builds the ``catalog_filename``
    for TRUNCATE separately from ``IcebergWrites.cpp``. If TRUNCATE
    fails under Glue with the same double-slash symptom we saw on
    EXPORT, that's a *second* instance of the same class of bug and
    should be reported rather than papered over here.
    """
    if node is None:
        node = self.context.node

    name = as_destination_name(destination)

    if settings is None:
        settings = list(extra_settings) if extra_settings else []
    else:
        settings = list(settings)

    if not any(key == "allow_experimental_insert_into_iceberg" for key, _ in settings):
        settings.append(("allow_experimental_insert_into_iceberg", 1))

    settings = _apply_glue_metadata_path_workaround(
        self.context.catalog, settings
    )

    expect_failure = exitcode != 0 or message is not None

    with By(f"truncating iceberg destination {name}"):
        return node.query(
            f"TRUNCATE TABLE {name}",
            settings=settings,
            exitcode=exitcode,
            message=message,
            ignore_exception=expect_failure,
        )


@TestStep(When)
def kill_export_partition(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    node=None,
    exitcode=0,
):
    """Run ``KILL EXPORT PARTITION WHERE ...``.

    Accepts the same ``destination`` / ``destination_table`` split as
    :func:`export_partition`. The ``WHERE`` clause is built via
    :func:`iceberg.tests.export_partition.steps.export_status._destination_where_pieces`
    so the ``destination_database`` / ``destination_table`` filter is
    aligned with what ``system.replicated_partition_exports`` actually
    stores — an unqualified ``ns.tbl`` split out from the catalog-mode
    identifier ``datalake_xxx.\\`ns.tbl\\``` (see the helper's docstring
    for the rationale). Using the fully-qualified SQL identifier here
    would match no row under Ice / Glue and silently leave the target
    PENDING, which is the Phase 3 regression this fixed.
    """
    if node is None:
        node = self.context.node
    if destination is None and destination_table is None:
        raise ValueError(
            "kill_export_partition requires either destination= or destination_table="
        )
    no_checks = exitcode != 0

    where = [
        f"partition_id = '{partition_id}'",
        f"source_table = '{source_table}'",
    ]
    where.extend(
        _destination_where_pieces(
            destination=destination, destination_table=destination_table
        )
    )
    where_clause = " AND ".join(where)

    return node.query(
        f"KILL EXPORT PARTITION WHERE {where_clause}",
        exitcode=exitcode,
        no_checks=no_checks,
    )
