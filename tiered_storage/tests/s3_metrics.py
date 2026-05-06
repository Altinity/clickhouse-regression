import json
import os
from datetime import datetime, timezone


S3_EVENT_FILTER = (
    "WHERE {column} ILIKE '%S3%' "
    "OR {column} ILIKE '%BufferFromS3%' "
    "OR {column} ILIKE 'DiskS3%'"
)


def _query_s3_events(node):
    """Return S3-related system.events rows for builds with name or event column."""
    queries = [
        (
            "name",
            "SELECT name, value FROM system.events "
            + S3_EVENT_FILTER.format(column="name")
            + " ORDER BY name FORMAT TabSeparated",
        ),
        (
            "event",
            "SELECT event, value FROM system.events "
            + S3_EVENT_FILTER.format(column="event")
            + " ORDER BY event FORMAT TabSeparated",
        ),
    ]

    for _, query in queries:
        result = node.query(query, steps=False, no_checks=True, retry_count=0)
        if result.exitcode == 0 and "Exception:" not in result.output:
            return result.output

    return ""


def snapshot_s3_events(node):
    """Capture current S3-related counters from a ClickHouse node."""
    events = {}
    for line in _query_s3_events(node).strip().splitlines():
        if not line.strip():
            continue

        try:
            name, value = line.split("\t", maxsplit=1)
            events[name] = int(value)
        except ValueError:
            continue

    return events


def snapshot_cluster_s3_events(cluster, node_names):
    """Capture S3 counters from all requested ClickHouse nodes."""
    snapshot = {}
    for node_name in node_names:
        snapshot[node_name] = snapshot_s3_events(cluster.node(node_name))
    return snapshot


def diff_s3_event_snapshots(before, after):
    """Return per-node deltas between two S3 event snapshots."""
    delta = {}
    for node_name in sorted(set(before) | set(after)):
        before_events = before.get(node_name, {})
        after_events = after.get(node_name, {})
        event_delta = {}

        for event_name in sorted(set(before_events) | set(after_events)):
            value = after_events.get(event_name, 0) - before_events.get(event_name, 0)
            if value > 0:
                event_delta[event_name] = value

        delta[node_name] = event_delta

    return delta


def sum_s3_event_deltas(delta):
    """Sum per-node S3 event deltas into cluster totals."""
    totals = {}
    for events in delta.values():
        for name, value in events.items():
            totals[name] = totals.get(name, 0) + value
    return dict(sorted(totals.items()))


def _is_bytes_event(name):
    return "Bytes" in name or name.endswith("Size")


def _is_read_bytes_event(name):
    lower_name = name.lower()
    return _is_bytes_event(name) and (
        "read" in lower_name or "get" in lower_name or "download" in lower_name
    )


def _is_write_bytes_event(name):
    lower_name = name.lower()
    return _is_bytes_event(name) and (
        "write" in lower_name
        or "put" in lower_name
        or "upload" in lower_name
        or "multipart" in lower_name
    )


def _format_bytes(value):
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(value)
    for unit in units:
        if abs(size) < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def build_s3_metrics_payload(before, after):
    """Build a JSON-serializable metrics payload from two snapshots."""
    delta = diff_s3_event_snapshots(before, after)
    totals = sum_s3_event_deltas(delta)
    read_bytes = sum(value for name, value in totals.items() if _is_read_bytes_event(name))
    write_bytes = sum(value for name, value in totals.items() if _is_write_bytes_event(name))

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "per_node": delta,
        "totals": totals,
        "estimated_read_bytes": read_bytes,
        "estimated_write_bytes": write_bytes,
        "estimated_total_bytes": read_bytes + write_bytes,
    }


def format_s3_metrics_report(payload):
    """Format collected S3 metrics for TestFlows output."""
    lines = [
        "S3 metrics collected from ClickHouse system.events",
        f"Estimated read bytes: {_format_bytes(payload['estimated_read_bytes'])}",
        f"Estimated write bytes: {_format_bytes(payload['estimated_write_bytes'])}",
        f"Estimated read + write bytes: {_format_bytes(payload['estimated_total_bytes'])}",
        "",
        "Cluster totals:",
    ]

    totals = payload["totals"]
    if totals:
        for name, value in totals.items():
            formatted = _format_bytes(value) if _is_bytes_event(name) else str(value)
            lines.append(f"  {name}: {formatted}")
    else:
        lines.append("  No S3-related system.events deltas were captured.")

    lines.extend(["", "Per-node totals:"])
    for node_name, events in payload["per_node"].items():
        lines.append(f"  {node_name}:")
        if events:
            for name, value in events.items():
                formatted = _format_bytes(value) if _is_bytes_event(name) else str(value)
                lines.append(f"    {name}: {formatted}")
        else:
            lines.append("    No S3-related deltas.")

    return "\n".join(lines)


def write_s3_metrics_payload(payload, path=None):
    """Write metrics payload to a JSON file for CI artifacts."""
    if path is None:
        path = os.getenv("TIERED_STORAGE_S3_METRICS_FILE", "tiered_storage_s3_metrics.json")

    with open(path, "w", encoding="utf-8") as fd:
        json.dump(payload, fd, indent=2, sort_keys=True)
        fd.write("\n")

    return path
