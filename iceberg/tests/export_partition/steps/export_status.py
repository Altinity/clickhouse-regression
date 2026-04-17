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


@TestStep(When)
def get_export_row(
    self,
    source_table,
    partition_id,
    destination_table=None,
    columns="status",
    node=None,
    prefer_remote=True,
):
    """Return the requested columns for a single export row.

    Returns ``None`` if the row does not exist yet.
    """
    if node is None:
        node = self.context.node

    where = [
        f"source_table = '{source_table}'",
        f"partition_id = '{partition_id}'",
    ]
    if destination_table is not None:
        where.append(f"destination_table = '{destination_table}'")
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
    destination_table=None,
    timeout=120,
    delay=3,
    node=None,
):
    """Poll ``system.replicated_partition_exports`` until ``status`` matches.

    Fails the scenario on timeout, reporting the last observed status.
    """
    if node is None:
        node = self.context.node

    last_status = None
    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            last_status = get_export_row(
                source_table=source_table,
                partition_id=partition_id,
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
    destination_table=None,
    timeout=30,
    delay=1,
    node=None,
):
    """Wait until an export row appears in ``system.replicated_partition_exports``.

    The scheduler may not insert the row immediately, so this helper polls
    until ``count() > 0``.
    """
    if node is None:
        node = self.context.node

    where = [
        f"source_table = '{source_table}'",
        f"partition_id = '{partition_id}'",
    ]
    if destination_table is not None:
        where.append(f"destination_table = '{destination_table}'")
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
def get_exception_count(
    self,
    source_table,
    partition_id,
    destination_table=None,
    node=None,
):
    """Return ``exception_count`` for an export row as an int (0 if missing)."""
    value = get_export_row(
        source_table=source_table,
        partition_id=partition_id,
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
