"""Status / event helpers for EXPORT PARTITION.

These wrap ``system.replicated_partition_exports``, ``system.events`` and
``system.part_log`` so tests do not need to repeat the same polling logic.

Adapted from ``s3/tests/export_partition/steps/export_status.py`` with two
differences:

* ``prefer_remote_information`` is used when available (the Iceberg PR adds a
  dedicated setting so replicas can report a consistent status regardless of
  which node actually committed the manifest).
* The default timeouts are slightly higher because Iceberg commits involve an
  extra HTTP / catalog round-trip.
"""

import json

from testflows.core import *
from testflows.asserts import error


def _prefer_remote_settings():
    """Setting applied to queries against ``system.replicated_partition_exports``
    so that replicas which did not drive the export still return a meaningful
    status.

    Returns a list of ``(key, value)`` pairs suitable for ``node.query``.
    """
    return [("export_merge_tree_partition_system_table_prefer_remote_information", 1)]


def _destination_where_pieces(destination=None, destination_table=None):
    """Return the ``destination_database`` / ``destination_table`` WHERE
    fragments that filter ``system.replicated_partition_exports`` for a
    given export destination.

    ``system.replicated_partition_exports`` stores the destination identity
    split across two columns (``destination_database`` and
    ``destination_table``), where ``destination_table`` is the *unqualified*
    table name as it appears in CH's ``StorageID`` for the destination (see
    :cpp:type:`ExportReplicatedMergeTreePartitionManifest`). For a
    catalog-backed Iceberg table created via ``datalake_xxx.\\`ns.tbl\\```
    the split is::

        destination_database = "datalake_xxx"
        destination_table    = "ns.tbl"   # backticks group the dotted name

    so filtering purely on ``destination_table = 'datalake_xxx.\\`ns.tbl\\`'``
    never matches anything — that's the bug Phase 2 closes.

    This helper accepts whichever of the following the caller has on hand:

    * ``destination``: a dict produced by
      :func:`iceberg.tests.export_partition.steps.iceberg_destination.create_pyiceberg_catalog_destination`
      (carries ``database_name``, ``namespace`` and ``table_name``
      explicitly) *or* a plain unqualified string in no_catalog mode.
      Preferred.
    * ``destination_table``: legacy path accepting a plain unqualified
      string (still supported so old call sites keep working).

    Returns a list of SQL fragments that can be AND-ed into a WHERE clause.
    Empty list means "no destination filter".
    """
    if destination is not None:
        if isinstance(destination, dict):
            database = destination.get("database_name")
            namespace = destination.get("namespace")
            table_name = destination.get("table_name")
            if database is None or namespace is None or table_name is None:
                raise ValueError(
                    f"destination dict missing required keys: {destination!r}"
                )
            return [
                f"destination_database = '{database}'",
                f"destination_table = '{namespace}.{table_name}'",
            ]
        if isinstance(destination, str):
            destination_table = destination
        else:
            raise TypeError(
                f"destination must be a dict or str, got {type(destination).__name__}"
            )
    if destination_table is None:
        return []
    return [f"destination_table = '{destination_table}'"]


@TestStep(When)
def get_export_row(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    columns="status",
    node=None,
    prefer_remote=True,
):
    """Return the requested columns for a single export row.

    Returns ``None`` if the row does not exist yet.

    Pass ``destination`` (preferred) to filter against the catalog-aware
    ``(destination_database, destination_table)`` split; ``destination``
    accepts either the dict returned by
    :func:`iceberg.tests.export_partition.steps.iceberg_destination.create_iceberg_destination`
    or a plain unqualified table-name string. ``destination_table`` remains
    supported for legacy callers that only ever pass an unqualified string.
    """
    if node is None:
        node = self.context.node

    where = [
        f"source_table = '{source_table}'",
        f"partition_id = '{partition_id}'",
    ]
    where.extend(_destination_where_pieces(destination, destination_table))
    where_clause = " AND ".join(where)

    settings = _prefer_remote_settings() if prefer_remote else []
    output = node.query(
        f"SELECT {columns} FROM system.replicated_partition_exports "
        f"WHERE {where_clause}",
        settings=settings,
    ).output.strip()

    return output if output else None


@TestStep(When)
def wait_for_export_status(
    self,
    source_table,
    partition_id,
    expected_status="COMPLETED",
    destination=None,
    destination_table=None,
    timeout=120,
    delay=3,
    node=None,
):
    """Poll ``system.replicated_partition_exports`` until ``status`` matches.

    Fails the scenario on timeout, reporting the last observed status.

    See :func:`get_export_row` for the meaning of ``destination`` /
    ``destination_table``.
    """
    if node is None:
        node = self.context.node

    last_status = None
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            last_status = get_export_row(
                source_table=source_table,
                partition_id=partition_id,
                destination=destination,
                destination_table=destination_table,
                columns="status",
                node=node,
            )
            assert last_status == expected_status, error(
                f"Expected status '{expected_status}' for "
                f"source_table='{source_table}' partition_id='{partition_id}'"
                f" but got '{last_status}'"
            )


@TestStep(When)
def wait_for_export_to_start(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    timeout=30,
    delay=1,
    node=None,
):
    """Wait until an export row appears in ``system.replicated_partition_exports``.

    The scheduler may not insert the row immediately, so this helper polls
    until ``count() > 0``.

    See :func:`get_export_row` for the meaning of ``destination`` /
    ``destination_table``.
    """
    if node is None:
        node = self.context.node

    where = [
        f"source_table = '{source_table}'",
        f"partition_id = '{partition_id}'",
    ]
    where.extend(_destination_where_pieces(destination, destination_table))
    where_clause = " AND ".join(where)

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            count = int(
                node.query(
                    f"SELECT count() FROM system.replicated_partition_exports "
                    f"WHERE {where_clause}"
                ).output.strip()
            )
            assert count > 0, error(
                f"Export row for partition '{partition_id}' of '{source_table}'"
                f" did not appear within {timeout}s"
            )


@TestStep(When)
def wait_for_exports_to_settle(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    timeout=120,
    delay=3,
    node=None,
):
    """Wait until every row matching the filter reaches a terminal status.

    A terminal status is one of ``COMPLETED``, ``FAILED`` or ``CANCELLED``:
    once all matching rows are there the underlying background task has
    either committed its snapshot or given up. Useful for scenarios that
    issue an ALTER expected to fail at parse/schedule time but still leave
    one of the EXPORT entries running in the background (e.g. the
    duplicate-EXPORT-inside-one-ALTER scenario in ``concurrent_writes.py``
    - the client sees ``BAD_ARGUMENTS`` for the second entry while the
    first entry's commit is still in flight, which races PyIceberg against
    the snapshot being written and produces a "snapshots=0, rows=3"
    inconsistency on the next assertion).

    If no row ever appears within ``timeout`` the step also succeeds - the
    absence of any scheduled task is itself a terminal state as far as the
    destination is concerned.

    See :func:`get_export_row` for the meaning of ``destination`` /
    ``destination_table``.
    """
    if node is None:
        node = self.context.node

    where = [
        f"source_table = '{source_table}'",
        f"partition_id = '{partition_id}'",
    ]
    where.extend(_destination_where_pieces(destination, destination_table))
    where_clause = " AND ".join(where)

    settings = _prefer_remote_settings()
    last_pending = None
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            last_pending = node.query(
                f"SELECT count() FROM system.replicated_partition_exports "
                f"WHERE {where_clause} "
                f"  AND status NOT IN ('COMPLETED', 'FAILED', 'CANCELLED')",
                settings=settings,
            ).output.strip()
            assert last_pending == "0", error(
                f"Export rows for source_table='{source_table}' "
                f"partition_id='{partition_id}' still pending: "
                f"{last_pending} row(s) not in a terminal state"
            )


@TestStep(When)
def get_exception_count(
    self,
    source_table,
    partition_id,
    destination=None,
    destination_table=None,
    node=None,
):
    """Return ``exception_count`` for an export row as an int (0 if missing).

    See :func:`get_export_row` for the meaning of ``destination`` /
    ``destination_table``.
    """
    value = get_export_row(
        source_table=source_table,
        partition_id=partition_id,
        destination=destination,
        destination_table=destination_table,
        columns="any(exception_count)",
        node=node,
    )
    try:
        return int(value) if value else 0
    except ValueError:
        return 0


@TestStep(When)
def get_export_events(self, node=None):
    """Return all ``%Export%`` profile events from ``system.events`` as a dict."""
    if node is None:
        node = self.context.node

    output = node.query(
        "SELECT name, value FROM system.events "
        "WHERE name LIKE '%%Export%%' FORMAT JSONEachRow"
    ).output

    events = {}
    for line in output.strip().splitlines():
        if line.strip():
            event = json.loads(line)
            events[event["name"]] = int(event["value"])

    events.setdefault("PartsExportFailures", 0)
    events.setdefault("PartsExports", 0)
    events.setdefault("PartsExportDuplicated", 0)
    return events


@TestStep(When)
def get_exported_part_log(self, node=None):
    """Return the list of part names that triggered a ``ExportPart`` entry in
    ``system.part_log`` on the given node.
    """
    if node is None:
        node = self.context.node
    output = node.query(
        "SELECT part_name FROM system.part_log WHERE event_type = 'ExportPart'"
    ).output
    return [line.strip() for line in output.splitlines() if line.strip()]
