import json

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.common import temporary_bucket_path, s3_storage


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
def get_parts_per_partition(self, table_name, node=None):
    """Get the number of parts per partition as a dictionary {partition: count}."""

    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT partition, count() as part_count
        FROM system.parts
        WHERE table = '{table_name}' AND active = 1
        GROUP BY partition
        ORDER BY partition
        FORMAT JSONEachRow
        """,
        exitcode=0,
        steps=True,
    )
    
    parts_per_partition = {}
    for line in result.output.strip().splitlines():
        if line.strip():
            row = json.loads(line)
            parts_per_partition[row["partition"]] = int(row["part_count"])
    return parts_per_partition


@TestStep(When)
def optimize_partition(self, table_name, partition, node=None):
    """Optimize a partition of a table."""

    if node is None:
        node = self.context.node

    node.query(
        f"OPTIMIZE TABLE {table_name} PARTITION '{partition}' FINAL",
        exitcode=0,
        steps=True,
    )


@TestStep(When)
def get_s3_parts_per_partition(self, table_name, node=None):
    """Get the number of files (parts) per partition in an S3 table."""
    if node is None:
        node = self.context.node
    
    result = node.query(
        f"""
        SELECT 
            p as partition,
            uniqExact(_file) as part_count
        FROM {table_name}
        GROUP BY partition
        ORDER BY partition
        FORMAT JSONEachRow
        """,
        exitcode=0,
        steps=True,
    )
    
    parts_per_partition = {}
    for line in result.output.strip().splitlines():
        if line.strip():
            row = json.loads(line)
            partition = str(row["partition"])
            parts_per_partition[partition] = int(row["part_count"])
    return parts_per_partition


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
def get_column_info(self, node, table_name):
    """Get column information in the same structure as default_columns.

    Returns a list of dictionaries with 'name' and 'type' keys.
    Example: [{"name": "p", "type": "UInt8"}, {"name": "i", "type": "UInt64"}]
    """
    r = node.query(
        f"""
        SELECT name, type
        FROM system.columns 
        WHERE table = '{table_name}' AND database = currentDatabase()
        ORDER BY position
        FORMAT JSONEachRow
        """,
        exitcode=0,
        steps=True,
    )

    columns = []
    for line in r.output.strip().splitlines():
        col = json.loads(line)
        columns.append({"name": col["name"], "type": col["type"]})
    return columns


@TestStep(When)
def get_parts(self, table_name, node):
    """Get all parts for a table on a given node."""

    query = f"SELECT name FROM system.parts WHERE table = '{table_name}' AND active = 1"

    output = node.query(
        query,
        exitcode=0,
        steps=True,
    ).output

    return sorted([row.strip() for row in output.splitlines()])


@TestStep(When)
def export_parts(
    self,
    source_table,
    destination_table,
    node,
    parts=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
):
    """Export parts from a source table to a destination table on the same node. If parts are not provided, all parts will be exported."""

    if parts is None:
        parts = get_parts(table_name=source_table, node=node)

    if inline_settings is True:
        inline_settings = self.context.default_settings

    no_checks = exitcode != 0
    output = []

    for part in parts:
        output.append(
            node.query(
                f"ALTER TABLE {source_table} EXPORT PART '{part}' TO TABLE {destination_table}",
                exitcode=exitcode,
                no_checks=no_checks,
                steps=True,
                settings=settings,
                inline_settings=inline_settings,
            )
        )

    return output


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
        events["PartsExportFailures"] = 0
    if "PartsExports" not in events:
        events["PartsExports"] = 0
    if "PartsExportDuplicated" not in events:
        events["PartsExportDuplicated"] = 0

    return events


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


@TestStep(When)
def get_num_active_exports(self, node):
    """Get the number of active exports from the system.metrics table of a given node."""

    num_active_exports = node.query(
        "SELECT value FROM system.metrics WHERE metric = 'Export'",
        exitcode=0,
        steps=True,
    ).output.strip()

    return int(num_active_exports)


@TestStep(When)
def insert_into_table(self, table_name, node=None):
    """Insert values into a table."""

    if node is None:
        node = self.context.node

    node.query(
        f"""INSERT INTO {table_name}
            SELECT *
            FROM generateRandom((
                SELECT arrayStringConcat(
                        groupArray(concat(name, ' ', type)),
                        ', '
                    )
                FROM
                (
                    SELECT name, type
                    FROM system.columns
                    WHERE database = currentDatabase()
                    AND table = '{table_name}'
                    ORDER BY position
                )
            ))
            LIMIT 10;""",
        exitcode=0,
        steps=True,
    )


@TestStep(When)
def concurrent_export_tables(self, num_tables, number_of_values=3, number_of_parts=1):
    """Check concurrent exports from different sources to the same S3 table."""

    with By(f"I create {num_tables} populated source tables"):
        source_tables = []
        for i in range(num_tables):
            source_tables.append(
                partitioned_merge_tree_table(
                    table_name=f"source_{getuid()}",
                    partition_by="p",
                    columns=default_columns(),
                    stop_merges=True,
                    number_of_values=number_of_values,
                    number_of_parts=number_of_parts,
                )
            )

    with And(f"I create {num_tables} empty S3 tables"):
        destination_tables = []
        destination_tables.append(
            create_s3_table(table_name=f"s3_{getuid()}", create_new_bucket=True)
        )
        for i in range(num_tables - 1):
            destination_tables.append(create_s3_table(table_name=f"s3_{getuid()}"))

    with And("I export parts from all sources concurrently to the S3 table"):
        for i in range(num_tables):
            Step(test=export_parts, parallel=True)(
                source_table=source_tables[i],
                destination_table=destination_tables[i],
                node=self.context.node,
            )
        join()

    return source_tables, destination_tables


@TestStep(Then)
def source_matches_destination(
    self, source_table, destination_table, source_node=None, destination_node=None
):
    """Check that source and destination table data matches."""

    if source_node is None:
        source_node = self.context.node
    if destination_node is None:
        destination_node = self.context.node

    source_data = select_all_ordered(table_name=source_table, node=source_node)
    destination_data = select_all_ordered(
        table_name=destination_table, node=destination_node
    )
    assert source_data == destination_data, error()


@TestStep(Then)
def verify_export_concurrency(self, node, source_tables):
    """Verify exports from different tables ran concurrently by checking overlapping execution times.

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
