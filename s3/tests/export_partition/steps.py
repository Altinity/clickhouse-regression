import json

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.common import temporary_bucket_path, s3_storage
from s3.tests.export_part.steps import wait_for_all_exports_to_complete


@TestStep(Given)
def minio_storage_configuration(self, restart=True):
    """Create storage configuration with jbod disks, MinIO S3 disk, and tiered storage policy."""
    with Given(
        "I configure storage with jbod disks, MinIO S3 disk, and tiered storage"
    ):
        disks = {
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/"},
            "jbod3": {"path": "/jbod3/"},
            "jbod4": {"path": "/jbod4/"},
            "external": {"path": "/external/"},
            "external2": {"path": "/external2/"},
            "minio": {
                "type": "s3",
                "endpoint": "http://minio1:9001/root/data/",
                "access_key_id": "minio_user",
                "secret_access_key": "minio123",
            },
            "s3_cache": {
                "type": "cache",
                "disk": "minio",
                "path": "minio_cache/",
                "max_size": "22548578304",
                "cache_on_write_operations": "1",
            },
        }

        policies = {
            "jbod1": {"volumes": {"main": {"disk": "jbod1"}}},
            "jbod2": {"volumes": {"main": {"disk": "jbod2"}}},
            "jbod3": {"volumes": {"main": {"disk": "jbod3"}}},
            "jbod4": {"volumes": {"main": {"disk": "jbod4"}}},
            "external": {"volumes": {"main": {"disk": "external"}}},
            "external2": {"volumes": {"main": {"disk": "external2"}}},
            "tiered_storage": {
                "volumes": {
                    "hot": [
                        {"disk": "jbod1"},
                        {"disk": "jbod2"},
                        {"max_data_part_size_bytes": "2048"},
                    ],
                    "cold": [
                        {"disk": "external"},
                        {"disk": "external2"},
                    ],
                },
                "move_factor": "0.7",
            },
            "s3_cache": {"volumes": {"external": {"disk": "s3_cache"}}},
            "minio_external_nocache": {"volumes": {"external": {"disk": "minio"}}},
        }

        s3_storage(disks=disks, policies=policies, restart=restart)


def default_columns(simple=True, partition_key_type="UInt8"):
    columns = [
        {"name": "p", "type": partition_key_type},
        {"name": "i", "type": "UInt64"},
        {"name": "Path", "type": "String"},
        {"name": "Time", "type": "DateTime"},
        {"name": "Value", "type": "Float64"},
        {"name": "Timestamp", "type": "Int64"},
    ]

    if simple:
        return columns[:2]
    else:
        return columns


def valid_partition_key_types_columns():
    return [
        {"name": "int8", "type": "Int8"},
        {"name": "int16", "type": "Int16"},
        {"name": "int32", "type": "Int32"},
        {"name": "int64", "type": "Int64"},
        {"name": "uint8", "type": "UInt8"},
        {"name": "uint16", "type": "UInt16"},
        {"name": "uint32", "type": "UInt32"},
        {"name": "uint64", "type": "UInt64"},
        {"name": "date", "type": "Date"},
        {"name": "date32", "type": "Date32"},
        {"name": "datetime", "type": "DateTime"},
        {"name": "datetime64", "type": "DateTime64"},
        {"name": "string", "type": "String"},
        {"name": "fixedstring", "type": "FixedString(10)"},
    ]


@TestStep(Given)
def create_temp_bucket(self):
    """Create temporary S3 bucket."""

    temp_s3_path = temporary_bucket_path(
        bucket_prefix=f"{self.context.bucket_prefix}/export_part"
    )

    self.context.uri = f"{self.context.uri_base}export_part/{temp_s3_path}/"


@TestStep(Given)
def create_s3_table(
    self,
    table_name,
    cluster=None,
    create_new_bucket=False,
    columns=None,
    partition_by="p",
):
    """Create a destination S3 table."""

    if create_new_bucket:
        create_temp_bucket()

    if columns is None:
        columns = default_columns(simple=True)

    table_name = f"{table_name}_{getuid()}"
    engine = f"""
        S3(
            '{self.context.uri}',
            '{self.context.access_key_id}',
            '{self.context.secret_access_key}',
            filename='{table_name}',
            format='Parquet',
            compression='auto',
            partition_strategy='hive'
        )
    """

    create_table(
        table_name=table_name,
        columns=columns,
        partition_by=partition_by,
        engine=engine,
        cluster=cluster,
    )

    return table_name


@TestStep(When)
def kill_minio(self, cluster=None, container_name="s3_env-minio1-1", signal="KILL"):
    """Forcefully kill MinIO container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for MinIO container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("MinIO container still running")


@TestStep(When)
def start_minio(self, cluster=None, container_name="s3_env-minio1-1"):
    """Start MinIO container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting MinIO container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for MinIO to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} curl -f http://localhost:9001/minio/health/live",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("MinIO health check failed")


@TestStep(When)
def kill_keeper(self, cluster=None, container_name="s3_env-keeper1-1", signal="KILL"):
    """Forcefully kill ClickHouse Keeper container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for Keeper container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("Keeper container still running")


@TestStep(When)
def kill_zookeeper(
    self, cluster=None, container_name="s3_env-zookeeper1-1", signal="KILL"
):
    """Forcefully kill ZooKeeper container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for ZooKeeper container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("ZooKeeper container still running")


@TestStep(When)
def start_keeper(self, cluster=None, container_name="s3_env-keeper1-1"):
    """Start ClickHouse Keeper container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting Keeper container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for Keeper to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} curl -f http://localhost:9182/ready",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("Keeper health check failed")


@TestStep(When)
def start_zookeeper(self, cluster=None, container_name="s3_env-zookeeper1-1"):
    """Start ZooKeeper container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting ZooKeeper container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for ZooKeeper to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} sh -c 'echo stat | nc localhost 2181'",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("ZooKeeper health check failed")


@TestStep(When)
def get_partitions(self, table_name, node):
    """Get all partitions for a table on a given node."""

    output = node.query(
        f"SELECT DISTINCT partition_id FROM system.parts WHERE table = '{table_name}'",
        exitcode=0,
        steps=True,
    ).output
    return sorted([row.strip() for row in output.splitlines()])


@TestStep(When)
def export_partitions(
    self,
    source_table,
    destination_table,
    node,
    partitions=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
    retry_times=0,
    force_export=False,
):
    """Export partitions from a source table to a destination table on the same node. If partitions are not provided, all partitions will be exported."""

    if partitions is None:
        partitions = get_partitions(table_name=source_table, node=node)

    if inline_settings:
        inline_settings = self.context.default_settings

    if force_export:
        inline_settings.append(("export_merge_tree_partition_force_export", 1))

    no_checks = exitcode != 0

    output = []
    with By(f"running EXPORT PARTITION for {source_table} partitions"):
        for partition in partitions:
            for attempt in retries(count=retry_times, delay=5):
                with attempt:
                    output.append(
                        node.query(
                            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' TO TABLE {destination_table}",
                            exitcode=exitcode,
                            no_checks=no_checks,
                            steps=True,
                            settings=settings,
                            inline_settings=inline_settings,
                        )
                    )
                    wait_for_export_to_complete(
                        partition_id=partition, source_table=source_table, node=node
                    )
                    get_export_partition_zookeeper_events(node=node)
    return output


@TestStep(When)
def kill_export_partition(
    self,
    partition_id,
    source_table,
    destination_table,
    node=None,
    exitcode=0,
):
    """Kill an export partition operation.

    Args:
        partition_id: The partition ID to kill the export for
        source_table: The source table name
        destination_table: The destination table name
        node: The node to execute the query on (defaults to context.node)
        exitcode: Expected exit code (default: 0)
    """
    if node is None:
        node = self.context.node

    no_checks = exitcode != 0

    with By(
        f"killing EXPORT PARTITION for partition_id='{partition_id}', "
        f"source_table='{source_table}', destination_table='{destination_table}'"
    ):
        result = node.query(
            f"KILL EXPORT PARTITION WHERE partition_id = '{partition_id}' "
            f"AND source_table = '{source_table}' "
            f"AND destination_table = '{destination_table}'",
            exitcode=exitcode,
            no_checks=no_checks,
            steps=True,
        )

    return result


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
def get_export_partition_zookeeper_events(self, node=None):
    """Get the export partition ZooKeeper/Keeper profile events from the system.events table of a given node.

    Returns a dictionary with all ExportPartitionZooKeeper* profile events.
    Events are initialized to 0 if they don't exist in the system.events table.
    """

    if node is None:
        node = self.context.node

    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%ExportPartitionZooKeeper%%' FORMAT JSONEachRow",
        exitcode=0,
        steps=True,
    ).output

    # events = {}
    # for line in output.strip().splitlines():
    #     event = json.loads(line)
    #     events[event["name"]] = int(event["value"])
    #
    # expected_events = [
    #     "ExportPartitionZooKeeperRequests",
    #     "ExportPartitionZooKeeperGet",
    #     "ExportPartitionZooKeeperGetChildren",
    #     "ExportPartitionZooKeeperGetChildrenWatch",
    #     "ExportPartitionZooKeeperGetWatch",
    #     "ExportPartitionZooKeeperCreate",
    #     "ExportPartitionZooKeeperSet",
    #     "ExportPartitionZooKeeperRemove",
    #     "ExportPartitionZooKeeperRemoveRecursive",
    #     "ExportPartitionZooKeeperMulti",
    #     "ExportPartitionZooKeeperExists",
    # ]
    #
    # for event_name in expected_events:
    #     if event_name not in events:
    #         events[event_name] = 0

    return output


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


@TestStep
def get_export_field(
    self,
    field_name,
    source_table,
    timeout=30,
    delay=3,
    node=None,
    where_clause=None,
    select_clause=None,
):
    """Get a field value from system.replicated_partition_exports table."""

    if node is None:
        node = self.context.node

    if select_clause is None:
        select_clause = field_name

    base_where = f"source_table = '{source_table}'"
    if where_clause:
        where_clause = f"{base_where} AND {where_clause}"
    else:
        where_clause = base_where

    query = f"SELECT {select_clause} FROM system.replicated_partition_exports WHERE {where_clause}"

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            result = node.query(
                query,
                exitcode=0,
                no_checks=True,
            )

    return result


@TestStep
def get_source_database(self, source_table, timeout=30, delay=3, node=None):
    """Get source_database from system.replicated_partition_exports."""
    return get_export_field(
        field_name="source_database",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_destination_database(self, source_table, timeout=30, delay=3, node=None):
    """Get destination_database from system.replicated_partition_exports."""
    return get_export_field(
        field_name="destination_database",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_destination_table(self, source_table, timeout=30, delay=3, node=None):
    """Get destination_table from system.replicated_partition_exports."""
    return get_export_field(
        field_name="destination_table",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_create_time(self, source_table, timeout=30, delay=3, node=None):
    """Get create_time from system.replicated_partition_exports."""
    return get_export_field(
        field_name="create_time",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_partition_id(self, source_table, timeout=30, delay=3, node=None):
    """Get partition_id from system.replicated_partition_exports."""
    return get_export_field(
        field_name="partition_id",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_transaction_id(self, source_table, timeout=30, delay=3, node=None):
    """Get transaction_id from system.replicated_partition_exports."""
    return get_export_field(
        field_name="transaction_id",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_source_replica(self, source_table, timeout=30, delay=3, node=None):
    """Get source_replica from system.replicated_partition_exports."""
    return get_export_field(
        field_name="source_replica",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts(self, source_table, timeout=30, delay=3, node=None):
    """Get parts array from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts_count(self, source_table, timeout=30, delay=3, node=None):
    """Get parts_count from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts_count",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts_to_do(self, source_table, timeout=30, delay=3, node=None):
    """Get parts_to_do from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts_to_do",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_replica(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_replica from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_replica",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_last_exception(self, source_table, timeout=30, delay=3, node=None):
    """Get last_exception from system.replicated_partition_exports."""
    return get_export_field(
        field_name="last_exception",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_part(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_part from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_part",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_count(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_count from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_count",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep(Then)
def source_matches_destination(
    self,
    source_table,
    destination_table,
    source_node=None,
    destination_node=None,
    partition=None,
    source_data=None,
    destination_data=None,
):
    """Check that source and destination table data matches."""

    if source_node is None:
        source_node = self.context.node
    if destination_node is None:
        destination_node = self.context.node

    for attempt in retries(timeout=35, delay=3):
        with attempt:
            if source_data is None:
                source_data = select_all_ordered(
                    table_name=source_table, node=source_node, identifier=partition
                )
            if destination_data is None:
                destination_data = select_all_ordered(
                    table_name=destination_table,
                    node=destination_node,
                    identifier=partition,
                )
            assert source_data == destination_data, error()


@TestStep(Then)
def verify_export_concurrency(self, node, source_tables):
    """Verify exget_export_eventsports from different tables ran concurrently by checking overlapping execution times.

    Checks that for each table, there's at least one pair of consecutive exports from that table
    with an export from another table in between, confirming concurrent execution.
    """

    table_filter = " OR ".join([f"table = '{table}'" for table in source_tables])

    query = f"""
    SELECT 
        table
    FROM system.part_log 
    WHERE event_type = 'ExportPart' 
        AND ({table_filter})
    ORDER BY event_time_microseconds
    """

    result = node.query(query, exitcode=0, steps=True)

    exports = [line for line in result.output.strip().splitlines()]

    tables_done = set()

    for i in range(len(exports) - 1):
        current_table = exports[i]
        next_table = exports[i + 1]

        if current_table != next_table and current_table not in tables_done:
            for j in range(i + 2, len(exports)):
                if exports[j] == current_table:
                    tables_done.add(current_table)
                    break

    assert len(tables_done) == len(source_tables), error()
