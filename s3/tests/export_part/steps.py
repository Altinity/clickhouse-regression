import json
import random
from time import sleep
from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.common import temporary_bucket_path, s3_storage
from helpers.alter import *
from platform import processor

MINIO_CONTAINER = (
    "s3_env-minio1-1" if processor() == "x86_64" else "s3_env_arm64-minio1-1"
)


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
            "minio_cache": {
                "type": "cache",
                "disk": "minio",
                "path": "minio_cache/",
                "max_size": "22548578304",
                "cache_on_write_operations": "1",
            },
            "local_encrypted": {
                "type": "encrypted",
                "disk": "jbod1",
                "path": "encrypted/",
                "key": "1234567812345678",
            },
            "minio_encrypted": {
                "type": "encrypted",
                "disk": "minio",
                "path": "encrypted/",
                "key": "1234567812345678",
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
            "minio_cache": {"volumes": {"external": {"disk": "minio_cache"}}},
            "minio_nocache": {"volumes": {"external": {"disk": "minio"}}},
            "local_encrypted": {"volumes": {"main": {"disk": "local_encrypted"}}},
            "minio_encrypted": {"volumes": {"external": {"disk": "minio_encrypted"}}},
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


@TestStep(Given)
def create_distributed_table(
    self,
    cluster,
    local_table_name,
    distributed_table_name=None,
    sharding_key="rand()",
    node=None,
):
    """Create a Distributed table that points to local tables on a cluster."""
    if node is None:
        node = self.context.node

    if distributed_table_name is None:
        distributed_table_name = f"distributed_{getuid()}"

    node.query(
        f"""
        CREATE TABLE {distributed_table_name} AS {local_table_name}
        ENGINE = Distributed({cluster}, default, {local_table_name}, {sharding_key})
        """,
        exitcode=0,
        steps=True,
    )

    return distributed_table_name


@TestStep(When)
def get_storage_policy(self, table_name, node=None):
    """Get the storage policy of a table."""
    if node is None:
        node = self.context.node

    return node.query(
        f"SELECT storage_policy FROM system.tables WHERE name = '{table_name}'",
        exitcode=0,
        steps=True,
    ).output.strip()


@TestStep(When)
def create_new_partition(
    self, table_name, node=None, number_of_values=3, number_of_parts=1
):
    """Create a unique partition by inserting data with a unique partition key value.
    Returns the partition ID (as string) that was created.
    """
    if node is None:
        node = self.context.node

    partition_id = str(random.randint(0, 255))

    with By(f"Creating unique partition {partition_id}"):
        for _ in range(number_of_parts):
            node.query(
                f"INSERT INTO {table_name} (p, i) SELECT {partition_id}, rand64() FROM numbers({number_of_values})",
                exitcode=0,
                steps=True,
            )

    return partition_id


@TestStep(When)
def get_column_type(self, table_name, column_name, node=None):
    """Get the type of a specific column from a table."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT type
        FROM system.columns
        WHERE database = currentDatabase()
          AND table = '{table_name}'
          AND name = '{column_name}'
        LIMIT 1
        """,
        exitcode=0,
        steps=True,
    )

    return result.output.strip()


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
def get_random_partition(self, table_name, node=None):
    """Get a random partition ID from a table."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT partition
        FROM system.parts
        WHERE table = '{table_name}' AND active = 1
        GROUP BY partition
        ORDER BY rand()
        LIMIT 1
        """,
        exitcode=0,
        steps=True,
    )
    return result.output.strip()


@TestStep(When)
def get_random_part(self, table_name, node=None, partition=None):
    """Get a random part name from a table."""
    if node is None:
        node = self.context.node

    if partition is not None:
        query = f"""
        SELECT name
        FROM system.parts
        WHERE table = '{table_name}' AND active = 1 AND partition = '{partition}'
        ORDER BY rand()
        LIMIT 1
        """
    else:
        query = f"""
        SELECT name
        FROM system.parts
        WHERE table = '{table_name}' AND active = 1
        ORDER BY rand()
        LIMIT 1
        """
    result = node.query(
        query,
        exitcode=0,
        steps=True,
    )
    return result.output.strip()


@TestStep(When)
def wait_for_all_mutations_to_complete(self, node=None, table_name=None):
    """Wait for all mutations to complete on a given node."""
    if node is None:
        node = self.context.node

    if table_name is None:
        query = "SELECT count() FROM system.mutations WHERE is_done = 0"
    else:
        query = f"SELECT count() FROM system.mutations WHERE table = '{table_name}' AND is_done = 0"

    for attempt in retries(timeout=30, delay=1):
        with attempt:
            pending_mutations = node.query(
                query,
                exitcode=0,
                steps=True,
            ).output.strip()
            assert int(pending_mutations) == 0, error()


@TestStep(When)
def wait_for_all_merges_to_complete(self, node=None, table_name=None):
    """Wait for all merges to complete on a given node."""
    if node is None:
        node = self.context.node

    if table_name is None:
        query = "SELECT count() FROM system.merges"
    else:
        query = f"SELECT count() FROM system.merges WHERE table = '{table_name}'"

    for attempt in retries(timeout=30, delay=1):
        with attempt:
            pending_merges = node.query(
                query,
                exitcode=0,
                steps=True,
            ).output.strip()
            assert int(pending_merges) == 0, error()


@TestStep(When)
def start_merges(self, table_name, node=None):
    """Start merges on a given table."""
    if node is None:
        node = self.context.node

    node.query(f"SYSTEM START MERGES {table_name}", exitcode=0)


@TestStep(When)
def flush_log(self, node=None, table_name=None):
    """Flush the logs for the whole cluster or for a given table."""
    if node is None:
        node = self.context.node

    if table_name is None:
        node.query("SYSTEM FLUSH LOGS", exitcode=0)
    else:
        node.query(f"SYSTEM FLUSH LOGS {table_name}", exitcode=0)


@TestStep(When)
def count_s3_files(self, table_name, node=None):
    """Count the number of distinct files in an S3 table."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT count(DISTINCT _file) as file_count
        FROM {table_name}
        """,
        exitcode=0,
        steps=True,
    ).output.strip()

    return int(result)


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
def get_s3_parts(self, table_name, node=None):
    """Get all part names (filenames) from an S3 table."""
    if node is None:
        node = self.context.node

    output = node.query(
        f"""
        SELECT DISTINCT 
            replaceRegexpOne(_file, '_[A-F0-9]+\\.parquet$', '') as part_name
        FROM {table_name}
        ORDER BY part_name
        """,
        exitcode=0,
        steps=True,
    ).output

    return [row.strip() for row in output.splitlines()]


@TestStep(When)
def kill_minio(self, cluster=None, container_name=MINIO_CONTAINER, signal="KILL"):
    """Forcefully kill MinIO container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Killing MinIO container"):
        retry(cluster.command, 5)(
            None,
            f"docker kill --signal={signal} {container_name}",
            timeout=60,
            exitcode=0,
            steps=False,
        )

    with And("Waiting for MinIO container to stop"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                    timeout=10,
                )
                assert result.exitcode == 0, error()
                assert container_name not in result.output, error()


@TestStep(When)
def start_minio(self, cluster=None, container_name=MINIO_CONTAINER):
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
def get_column_info(self, table_name, node=None):
    """Get column information in the same structure as default_columns.

    Returns a list of dictionaries with 'name' and 'type' keys.
    Example: [{"name": "p", "type": "UInt8"}, {"name": "i", "type": "UInt64"}]
    """
    if node is None:
        node = self.context.node

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
def get_columns_with_kind(self, table_name, node=None):
    """Get column information including default_kind from system.columns."""
    if node is None:
        node = self.context.node

    r = node.query(
        f"""
        SELECT name, type, default_kind
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
        columns.append({
            "name": col["name"],
            "type": col["type"],
            "default_kind": col.get("default_kind", "")
        })
    return columns


@TestStep(When)
def verify_column_not_in_destination(self, table_name, column_name, node=None):
    """Verify that a column (e.g., EPHEMERAL) is not present in the destination table schema."""
    if node is None:
        node = self.context.node

    dest_columns = get_columns_with_kind(table_name=table_name, node=node)
    matching_columns = [col["name"] for col in dest_columns if column_name in col["name"]]
    assert len(matching_columns) == 0, error(
        f"Column '{column_name}' should not be in destination table, but found: {matching_columns}"
    )


@TestStep(When)
def verify_column_in_destination(self, table_name, column_name, node=None):
    """Verify that a column is present in the destination table schema."""
    if node is None:
        node = self.context.node

    dest_columns = get_columns_with_kind(table_name=table_name, node=node)
    matching_columns = [col["name"] for col in dest_columns if col["name"] == column_name]
    assert len(matching_columns) > 0, error(
        f"Column '{column_name}' should be in destination table, but not found. Available columns: {[col['name'] for col in dest_columns]}"
    )


@TestStep(Then)
def verify_exported_data_matches_with_columns(self, source_table, destination_table, columns, order_by="p", node=None):
    """Verify that exported data matches source table using explicit column list."""
    if node is None:
        node = self.context.node

    source_data = select_all_ordered(
        table_name=source_table,
        order_by=order_by,
        identifier=columns,
        node=node,
    )
    destination_data = select_all_ordered(
        table_name=destination_table,
        order_by=order_by,
        identifier=columns,
        node=node,
    )
    assert source_data == destination_data, error()


@TestStep(When)
def get_parts(self, table_name, node=None):
    """Get all parts for a table on a given node."""
    if node is None:
        node = self.context.node

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
    node=None,
    parts=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
):
    """Export parts from a source table to a destination table on the same node. If parts are not provided, all parts will be exported."""
    if node is None:
        node = self.context.node

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
def export_parts_to_table_function(
    self,
    source_table,
    filename,
    node=None,
    parts=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
    structure=None,
    partition_by=None,
    uri=None,
):
    """Export parts from a source table to a table function destination."""
    if node is None:
        node = self.context.node

    if parts is None:
        parts = get_parts(table_name=source_table, node=node)

    if inline_settings is True:
        inline_settings = self.context.default_settings

    if uri is None:
        uri = self.context.uri

    no_checks = exitcode != 0
    output = []

    if partition_by is None:
        partition_key_result = node.query(
            f"""
            SELECT partition_key
            FROM system.tables
            WHERE database = currentDatabase() AND name = '{source_table}'
            """,
            exitcode=0,
            steps=True,
        )
        partition_by = partition_key_result.output.strip()

    for part in parts:
        if structure:
            table_function_params = f"s3_credentials, url='{uri}{filename}', format='Parquet', structure='{structure}', partition_strategy='hive'"
        else:
            table_function_params = f"s3_credentials, url='{uri}{filename}', format='Parquet', partition_strategy='hive'"
        
        query = f"ALTER TABLE {source_table} EXPORT PART '{part}' TO TABLE FUNCTION s3({table_function_params}) PARTITION BY {partition_by}"
        
        output.append(
            node.query(
                query,
                exitcode=exitcode,
                no_checks=no_checks,
                steps=True,
                settings=settings,
                inline_settings=inline_settings,
            )
        )

    return output


@TestStep(When)
def get_export_events(self, node=None):
    """Get the export data from the system.events table of a given node."""
    if node is None:
        node = self.context.node

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
    if "PartsExportTotalMilliseconds" not in events:
        events["PartsExportTotalMilliseconds"] = 0

    return events


@TestStep(When)
def get_part_log(self, table_name=None, event_type="ExportPart", node=None):
    """Get the part log from the system.part_log table of a given node."""
    if node is None:
        node = self.context.node

    if table_name is None:
        query = f"SELECT part_name FROM system.part_log WHERE event_type = '{event_type}' and read_rows > 0 ORDER BY part_name"
    else:
        query = f"SELECT part_name FROM system.part_log WHERE event_type = '{event_type}' AND table = '{table_name}' AND read_rows > 0 ORDER BY part_name"

    output = node.query(
        query,
        exitcode=0,
        steps=True,
    ).output

    return [row.strip() for row in output.splitlines()]


@TestStep(When)
def get_failed_part_log(self, table_name=None, node=None):
    """Get failed export operations from the system.part_log table of a given node."""
    if node is None:
        node = self.context.node

    if table_name is None:
        query = "SELECT part_name FROM system.part_log WHERE event_type = 'ExportPart' AND error != 0 ORDER BY part_name"
    else:
        query = f"SELECT part_name FROM system.part_log WHERE event_type = 'ExportPart' AND table = '{table_name}' AND error != 0 ORDER BY part_name"

    output = node.query(
        query,
        exitcode=0,
        steps=True,
    ).output

    return [row.strip() for row in output.splitlines() if row.strip()]


@TestStep(When)
def get_system_exports(self, node=None):
    """Get the system.exports source and destination table columns for all ongoing exports."""

    if node is None:
        node = self.context.node

    exports = node.query(
        "SELECT source_table, destination_table FROM system.exports",
        exitcode=0,
        steps=True,
    ).output.splitlines()

    return [line.strip().split("\t") for line in exports]


@TestStep(When)
def get_num_active_exports(self, node=None, table_name=None):
    """Get the number of active exports from the system.exports table of a given node."""

    if node is None:
        node = self.context.node

    if table_name is None:
        query = "SELECT count() FROM system.exports"
    else:
        query = (
            f"SELECT count() FROM system.exports WHERE source_table = '{table_name}'"
        )

    num_active_exports = node.query(
        query,
        exitcode=0,
        steps=True,
    ).output.strip()

    return int(num_active_exports)


@TestStep(When)
def get_average_export_duration(self, node=None, table_name=None):
    """Get the average duration of the exports from the system.part_log table of a given node."""
    if node is None:
        node = self.context.node

    if table_name is None:
        query = "SELECT avg(duration_ms) FROM system.part_log WHERE event_type = 'ExportPart'"
    else:
        query = f"SELECT avg(duration_ms) FROM system.part_log WHERE event_type = 'ExportPart' AND table = '{table_name}'"

    average_duration = node.query(
        query,
        exitcode=0,
        steps=True,
    ).output.strip()

    return float(average_duration)


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
            )
        join()

    return source_tables, destination_tables


@TestStep(When)
def wait_for_all_exports_to_complete(self, node=None, table_name=None):
    """Wait for all exports to complete on a given node."""

    if node is None:
        node = self.context.node

    for attempt in retries(timeout=60, delay=1):
        with attempt:
            assert (
                get_num_active_exports(node=node, table_name=table_name) == 0
            ), error()


@TestStep(When)
def wait_for_distributed_table_data(self, table_name, expected_count, node=None):
    """Wait for data to be distributed to all shards in a Distributed table."""
    if node is None:
        node = self.context.node

    for attempt in retries(timeout=60, delay=1):
        with attempt:
            result = node.query(
                f"SELECT count() FROM {table_name}",
                exitcode=0,
                steps=True,
            )
            assert int(result.output.strip()) == expected_count, error()


@TestStep(Then)
def source_matches_destination(
    self,
    source_table,
    destination_table,
    node=None,
):
    """Check that source and destination table data matches."""

    wait_for_all_exports_to_complete(node=node)
    source_matches_destination_hash(
        source_table=source_table,
        destination_table=destination_table,
        node=node,
    )
    source_matches_destination_rows(
        source_table=source_table,
        destination_table=destination_table,
        node=node,
    )


@TestStep(Then)
def source_matches_destination_hash(self, source_table, destination_table, node=None):
    """Check that source and destination table hashes match."""
    if node is None:
        node = self.context.node

    match, msg = table_hashes_match(
        table_name1=source_table, table_name2=destination_table, node=node
    )
    assert match, error(msg)


@TestStep(Then)
def source_does_not_match_destination_hash(
    self, source_table, destination_table, node=None
):
    """Check that source and destination table hashes do not match."""
    if node is None:
        node = self.context.node

    match, _ = table_hashes_match(
        table_name1=source_table, table_name2=destination_table, node=node
    )
    assert not match, error()


@TestStep(Then)
def source_matches_destination_rows(
    self,
    source_table,
    destination_table,
    node=None,
):
    """Check that source and destination table rows matches."""

    if node is None:
        node = self.context.node

    source_data = select_all_ordered(table_name=source_table, node=node)
    destination_data = select_all_ordered(table_name=destination_table, node=node)

    err_msg = "SOURCE != DESTINATION"

    if source_data != destination_data:
        source_set = set(source_data)
        destination_set = set(destination_data)
        missing = source_set - destination_set
        extra = destination_set - source_set
        if missing:
            err_msg += f"\nMissing in destination ({len(missing)} rows): {sorted(list(missing))}"
        if extra:
            err_msg += (
                f"\nExtra in destination ({len(extra)} rows): {sorted(list(extra))}"
            )

    assert source_data == destination_data, error(err_msg)


@TestStep(Then)
def part_log_matches_destination(self, source_table, destination_table, node=None):
    """Check that the part log matches the destination table."""
    if node is None:
        node = self.context.node

    for attempt in retries(timeout=60, delay=1):
        with attempt:
            wait_for_all_exports_to_complete(node=node, table_name=source_table)
            flush_log(node=node, table_name="system.part_log")
            part_log = get_part_log(table_name=source_table, node=node)
            destination_parts = get_s3_parts(table_name=destination_table)

            missing_parts = []
            for part_name in part_log:
                if not any(
                    dest_part.startswith(part_name) for dest_part in destination_parts
                ):
                    missing_parts.append(part_name)

            err_msg = ""
            if missing_parts:
                err_msg = (
                    f"Parts from part_log not found in destination: {missing_parts}\n"
                    f"Part log: {part_log}\n"
                    f"Destination parts: {destination_parts}"
                )

            assert len(missing_parts) == 0, error(err_msg)


@TestStep(Then)
def verify_export_concurrency(self, source_tables, node=None):
    """Verify exports from different tables ran concurrently by checking overlapping execution times.

    Checks that for each table, there's at least one pair of consecutive exports from that table
    with an export from another table in between, confirming concurrent execution.
    """
    if node is None:
        node = self.context.node

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


@TestStep(Given)
def create_partitions_with_sequential_uint64(
    self,
    table_name,
    number_of_values=3,
    number_of_partitions=5,
    number_of_parts=1,
    node=None,
    start_value=1,
):
    """Insert sequential UInt64 values into a column to create multiple partitions with predictable values.

    This is useful for testing deletion scenarios where you need to target specific rows.
    Values start from start_value and increment sequentially.
    """
    if node is None:
        node = self.context.node

    with By("Inserting sequential values into a column with uint64 datatype"):
        current_value = start_value
        for i in range(1, number_of_partitions + 1):
            for parts in range(1, number_of_parts + 1):
                node.query(
                    f"INSERT INTO {table_name} (p, i) SELECT {i}, {current_value} + number FROM numbers({number_of_values})",
                    exitcode=0,
                    steps=True,
                )
                current_value += number_of_values
