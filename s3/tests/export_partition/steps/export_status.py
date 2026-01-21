import json

from testflows.core import *
from testflows.asserts import error
from helpers.queries import *


@TestStep(When)
def get_export_events(self, node):
    """Get the export data from the system.events table of a given node."""

    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%Export%%' FORMAT JSONEachRow",
        exitcode=0,
        steps=True,
    ).output

    events = {}
    for line in output.strip().splitlines():
        event = json.loads(line)
        events[event["name"]] = int(event["value"])

    if "PartsExportFailures" not in events:
        events["PartsExportFailurget_export_eventses"] = 0
    if "PartsExports" not in events:
        events["PartsExports"] = 0
    if "PartsExportDuplicated" not in events:
        events["PartsExportDuplicated"] = 0

    return events


@TestStep(When)
def get_export_partition_zookeeper_events(self, node=None, cluster=None):
    """Get the export partition ZooKeeper/Keeper profile events from the system.events table, aggregated across all nodes in the cluster."""

    if cluster is not None:
        node_names = get_cluster_nodes(cluster=cluster)
    elif node is not None:
        node_names = None
    else:
        node_names = ["clickhouse1"]

    aggregated_events = {}

    if node_names is None:
        if node is None:
            node = self.context.node
        output = node.query(
            "SELECT name, value FROM system.events WHERE name LIKE '%%ExportPartitionZooKeeper%%' FORMAT JSONEachRow",
            exitcode=0,
            steps=True,
        ).output

        for line in output.strip().splitlines():
            if line.strip():
                event = json.loads(line)
                event_name = event["name"]
                event_value = int(event["value"])
                aggregated_events[event_name] = event_value
    else:
        for node_name in node_names:
            cluster_node = self.context.cluster.node(node_name)
            output = cluster_node.query(
                "SELECT name, value FROM system.events WHERE name LIKE '%%ExportPartitionZooKeeper%%' FORMAT JSONEachRow",
                exitcode=0,
                steps=True,
            ).output

            for line in output.strip().splitlines():
                if line.strip():
                    event = json.loads(line)
                    event_name = event["name"]
                    event_value = int(event["value"])
                    aggregated_events[event_name] = (
                        aggregated_events.get(event_name, 0) + event_value
                    )

    output_lines = []
    for event_name, event_value in sorted(aggregated_events.items()):
        output_lines.append(json.dumps({"name": event_name, "value": str(event_value)}))

    return "\n".join(output_lines)


@TestStep(Then)
def verify_zookeeper_events_increased(
    self, initial_events, final_events, min_total_requests=1
):
    """Verify that ZooKeeper/Keeper events increased after an export partition operation.

    Args:
        initial_events: Dictionary of events before the operation
        final_events: Dictionary of events after the operation
        min_total_requests: Minimum number of total ZooKeeper requests expected (default: 1)
    """
    with By("checking that total ZooKeeper requests increased"):
        total_requests_before = initial_events.get(
            "ExportPartitionZooKeeperRequests", 0
        )
        total_requests_after = final_events.get("ExportPartitionZooKeeperRequests", 0)
        total_requests_diff = total_requests_after - total_requests_before

        assert total_requests_diff >= min_total_requests, error(
            f"Expected at least {min_total_requests} ZooKeeper requests, but got {total_requests_diff}"
        )

    with And("checking individual ZooKeeper operation types"):
        operation_types = [
            "ExportPartitionZooKeeperGet",
            "ExportPartitionZooKeeperGetChildren",
            "ExportPartitionZooKeeperGetChildrenWatch",
            "ExportPartitionZooKeeperGetWatch",
            "ExportPartitionZooKeeperCreate",
            "ExportPartitionZooKeeperSet",
            "ExportPartitionZooKeeperRemove",
            "ExportPartitionZooKeeperRemoveRecursive",
            "ExportPartitionZooKeeperMulti",
            "ExportPartitionZooKeeperExists",
        ]

        operations_occurred = []
        for op_type in operation_types:
            before = initial_events.get(op_type, 0)
            after = final_events.get(op_type, 0)
            diff = after - before
            if diff > 0:
                operations_occurred.append((op_type, diff))

        assert len(operations_occurred) > 0, error(
            f"No ZooKeeper operations detected. Total requests: {total_requests_diff}"
        )


@TestStep(When)
def get_part_log(self, node):
    """Get the part log from the system.part_log table of a given node."""

    output = node.query(
        "SELECT part_name FROM system.part_log WHERE event_type = 'ExportPart'",
        exitcode=0,
        steps=True,
    ).output.splitlines()

    return output


@TestStep(When)
def get_system_exports(self, node):
    """Get the system.exports source and destination table columns for all ongoing exports."""

    exports = node.query(
        "SELECT source_table, destination_table FROM system.exports",
        exitcode=0,
        steps=True,
    ).output.splitlines()

    return [line.strip().split("\t") for line in exports]


@TestStep
def check_export_status(self, status, source_table, partition_id, node=None):
    """Check the export status in system.replicated_partition_exports."""

    if node is None:
        node = self.context.node

    exports = node.query(
        f"SELECT COUNT(*) FROM system.replicated_partition_exports WHERE status = '{status}' AND source_table = '{source_table}' AND partition_id='{partition_id}'",
        retry_count=120,
        retry_delay=3,
        exitcode=0,
    )

    return exports


@TestStep(When)
def wait_for_export_to_start(
    self, source_table, partition_id, node=None, assertion=None
):
    """Wait for export partition operation to start."""
    with By("checking export status until it starts"):

        for attempt in retries(timeout=35, delay=3):
            with attempt:
                exports = check_export_status(
                    status="PENDING",
                    source_table=source_table,
                    node=node,
                    partition_id=partition_id,
                )

                if assertion is None:
                    assert int(exports.output.strip()) > 0, error()
                else:
                    assert assertion, error()


@TestStep(When)
def wait_for_export_to_complete(
    self, source_table, partition_id, node=None, assertion=None
):
    """Wait for export partition operation to complete."""
    with By("checking export status until it starts"):
        for attempt in retries(timeout=120, delay=3):
            with attempt:
                exports = check_export_status(
                    status="COMPLETED",
                    source_table=source_table,
                    node=node,
                    partition_id=partition_id,
                )

                if assertion is None:
                    assert int(exports.output.strip()) > 0, error()
                else:
                    assert assertion, error()


@TestStep(When)
def check_error_export_status(
    self, source_table, partition_id, node=None, assertion=None
):
    """Check error export status."""
    with By("checking export status until it starts"):
        exports = check_export_status(
            status="ERROR",
            source_table=source_table,
            node=node,
            partition_id=partition_id,
        )

        if assertion is None:
            assert int(exports.output.strip()) > 0, error()
        else:
            assert assertion, error()


@TestStep(When)
def check_killed_export_status(
    self, source_table, partition_id, node=None, populated=True
):
    """Check error export status is killed."""
    with By("checking export status until it starts"):
        exports = check_export_status(
            status="KILLED",
            source_table=source_table,
            node=node,
            partition_id=partition_id,
        )

        if populated:
            assert int(exports.output.strip()) > 0, error()
        else:
            assert int(exports.output.strip()) == 0, error()
