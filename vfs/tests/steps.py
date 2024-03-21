#!/usr/bin/env python3
import json
import time
from contextlib import contextmanager
from platform import processor
from threading import Event

from testflows.core import *
from testflows.asserts import error
from testflows.uexpect.uexpect import ExpectTimeoutError
from testflows.combinatorics import combinations

from helpers.common import getuid, check_clickhouse_version

from s3.tests.common import s3_storage, check_bucket_size, get_bucket_size


DEFAULT_COLUMNS = "key UInt32, value1 String, value2 String, value3 String"
WIDE_PART_SETTING = "min_bytes_for_wide_part=0"
COMPACT_PART_SETTING = "min_bytes_for_wide_part=100000"

DOCKER_NETWORK = "vfs_env_default" if processor() == "x86_64" else "vfs_env_arm64"


@TestStep(Given)
def s3_config(self):
    """Set up disks and policies for vfs tests."""
    with Given("I have two S3 disks configured"):
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/storage/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_vfs": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/vfs/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
                "allow_vfs": "1",
            },
            "external_vfs_2": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/vfs-2/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
                "allow_vfs": "1",
            },
            "external_no_vfs": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/no-vfs/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_tiered": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/tiered/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
        }

    with And("""I have a storage policy configured to use the S3 disk"""):
        policies = {
            "external": {"volumes": {"external": {"disk": "external"}}},
            "external_vfs": {"volumes": {"external": {"disk": "external_vfs"}}},
            "external_no_vfs": {"volumes": {"external": {"disk": "external_no_vfs"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "external"},
                    "external": {"disk": "external_tiered"},
                }
            },
        }

    return s3_storage(
        disks=disks,
        policies=policies,
        restart=True,
        timeout=30,
        config_file="vfs_storage.xml",
    )


@TestStep(Given)
def check_vfs_state(
    self, node=None, enabled: bool = True, config_file="enable_vfs.xml"
):
    """DEPRECATED assert that vfs is enabled on at least one or on no disks."""
    if node is None:
        node = current().context.node

    c = f'grep "<allow_vfs>1" /etc/clickhouse-server/config.d/{config_file}'

    if enabled:
        node.command(c, exitcode=0)
    else:
        r = node.command(c, exitcode=None)
        assert r.exitcode in [1, 2], error()


@TestStep
def get_row_count(self, node, table_name, timeout=30):
    """Get the number of rows in the given table."""
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON", exitcode=0, timeout=timeout
    )
    return int(json.loads(r.output)["data"][0]["count()"])


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    """Assert that the number of rows in a table is as expected."""
    if node is None:
        node = current().context.node

    actual_count = get_row_count(node=node, table_name=table_name)
    assert rows == actual_count, error()


@TestStep(Given)
def replicated_table_cluster(
    self,
    table_name: str = None,
    storage_policy: str = "external",
    cluster_name: str = "replicated_cluster",
    columns: str = None,
    order_by: str = None,
    partition_by: str = None,
    primary_key: str = None,
    ttl: str = None,
    settings: str = None,
    allow_zero_copy: bool = None,
    exitcode: int = 0,
    no_cleanup=False,
):
    """Create a replicated table with the ON CLUSTER clause."""
    node = current().context.node

    if table_name is None:
        table_name = "table_" + getuid()

    if columns is None:
        columns = DEFAULT_COLUMNS

    if order_by is None:
        order_by = columns.split()[0]

    if settings is None:
        settings = []
    else:
        settings = [settings]

    settings.append(f"storage_policy='{storage_policy}'")

    if allow_zero_copy is not None:
        settings.append(f"allow_remote_fs_zero_copy_replication={int(allow_zero_copy)}")

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    if primary_key is not None:
        primary_key = f"PRIMARY KEY {primary_key}"
    else:
        primary_key = ""

    if ttl is not None:
        ttl = "TTL " + ttl
    else:
        ttl = ""

    try:
        with Given("I have a table"):
            r = node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} 
                ON CLUSTER '{cluster_name}' ({columns}) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
                ORDER BY {order_by} {partition_by} {primary_key} {ttl}
                SETTINGS {', '.join(settings)}
                """,
                settings=[("distributed_ddl_task_timeout ", 360)],
                exitcode=exitcode,
            )

        yield r, table_name

    finally:
        if not no_cleanup:
            with Finally(f"I drop the table"):
                node.query(
                    f"DROP TABLE IF EXISTS {table_name} ON CLUSTER '{cluster_name}' SYNC"
                )


@TestStep(Given)
def insert_random(
    self,
    node,
    table_name,
    columns: str = None,
    rows: int = 1000000,
    settings=None,
    **kwargs,
):
    """Insert random data to a table."""
    if columns is None:
        columns = DEFAULT_COLUMNS

    if settings:
        settings = "SETTINGS " + settings
    else:
        settings = ""

    node.query(
        f"INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') LIMIT {rows} {settings}",
        exitcode=0,
        **kwargs,
    )


@TestStep(Given)
def create_one_replica(
    self,
    node,
    table_name,
    columns="d UInt64",
    order_by="d",
    partition_by=None,
    replica_path_suffix=None,
    replica_name="{replica}",
    no_checks=False,
    storage_policy="external",
):
    """
    Create a simple replicated table on the given node.
    Call multiple times with the same table name and different nodes
    to create multiple replicas.
    """
    if replica_path_suffix is None:
        replica_path_suffix = table_name

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    r = node.query(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({columns}) 
        ENGINE=ReplicatedMergeTree('/clickhouse/tables/{replica_path_suffix}', '{replica_name}')
        ORDER BY ({order_by}) {partition_by}
        SETTINGS storage_policy='{storage_policy}'
        """,
        no_checks=no_checks,
        exitcode=0,
    )
    return r


@TestStep(Given)
def delete_one_replica(self, node, table_name, timeout=30):
    """Delete the local copy of a replicated table."""
    r = node.query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0, timeout=timeout
    )
    return r


@TestStep(When)
def sync_replica(self, node, table_name, raise_on_timeout=False, **kwargs):
    """Call SYSTEM SYNC REPLICA on the given node and table"""
    try:
        node.query(f"SYSTEM SYNC REPLICA {table_name}", **kwargs)
    except (ExpectTimeoutError, TimeoutError):
        if raise_on_timeout:
            raise


@TestStep(When)
def optimize(self, node, table_name, final=False, no_checks=False):
    """Apply OPTIMIZE on the given table and node"""
    q = f"OPTIMIZE TABLE {table_name}" + " FINAL" if final else ""
    node.query(q, no_checks=no_checks, exitcode=0)


@TestStep(Given)
def enable_vfs(
    self,
    nodes=None,
    config_file="enable_vfs.xml",
    timeout=30,
    disk_names: list = None,
    vfs_gc_sleep_ms=2000,
):
    """
    Add the config file for object storage vfs for the disks in `disk_names`.
    Default disk names are ["external"].
    """

    if check_clickhouse_version("<24.1")(self):
        skip("vfs not supported on ClickHouse < 24.2 and requires --allow-vfs flag")

    if disk_names is None:
        disk_names = ["external"]

    disks = {
        n: {
            "allow_vfs": "1",
            "vfs_gc_sleep_ms": f"{vfs_gc_sleep_ms}",
        }
        for n in disk_names
    }

    policies = {}

    return s3_storage(
        disks=disks,
        policies=policies,
        nodes=nodes,
        restart=True,
        timeout=timeout,
        config_file=config_file,
    )


@TestStep
def get_stable_bucket_size(
    self,
    name,
    prefix,
    minio_enabled,
    access_key,
    key_id,
    delay=10,
    timeout=300,
):
    """Get the size of an s3 bucket, waiting until the size hasn't change for [delay] seconds."""

    with By("Checking the current bucket size"):
        size_previous = get_bucket_size(
            name=name,
            prefix=prefix,
            minio_enabled=minio_enabled,
            access_key=access_key,
            key_id=key_id,
        )

    start_time = time.time()
    while True:
        with And(f"Waiting {delay}s"):
            time.sleep(delay)
        with And("Checking the current bucket size"):
            size = get_bucket_size(
                name=name,
                prefix=prefix,
                minio_enabled=minio_enabled,
                access_key=access_key,
                key_id=key_id,
            )
        with And(f"Checking if current={size} == previous={size_previous}"):
            if size_previous == size:
                break
        size_previous = size

        with And("Checking timeout"):
            assert time.time() - start_time <= timeout, error(
                f"Bucket size did not stabilize in {timeout}s"
            )

    return size


@TestStep
def check_stable_bucket_size(
    self,
    name,
    prefix,
    expected_size,
    tolerance=0,
    minio_enabled=False,
    delay=10,
):
    """Assert the size of an s3 bucket, waiting until the size hasn't change for [delay] seconds."""

    current_size = get_stable_bucket_size(
        name=name,
        prefix=prefix,
        minio_enabled=minio_enabled,
        access_key=self.context.secret_access_key,
        key_id=self.context.access_key_id,
        delay=delay,
    )
    assert abs(current_size - expected_size) <= tolerance, error()


@TestStep
def get_column_string(self, node, table_name, timeout=30) -> str:
    """Get a string with column names and types."""
    r = node.query(
        f"DESCRIBE TABLE {table_name}",
        timeout=timeout,
    )
    return ",".join([l.strip() for l in r.output.splitlines()])


@TestStep
def get_column_names(self, node, table_name, timeout=30) -> list:
    """Get a list of a table's column names."""
    r = node.query(
        f"DESCRIBE TABLE {table_name} FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_active_parts(self, node, table_name, timeout=30):
    """Get a list of active parts in a table."""
    r = node.query(
        f"SELECT name FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_active_partition_ids(self, node, table_name, timeout=30):
    """Get a list of active partitions in a table."""
    r = node.query(
        f"SELECT partition_id FROM system.parts WHERE table='{table_name}' and active=1 FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["partition_id"]


@contextmanager
def interrupt_node(node):
    """
    Stop the given node container.
    Instance is restarted on context exit.
    """
    try:
        with When(f"{node.name} is stopped"):
            node.stop()
            yield

    finally:
        with When(f"{node.name} is started"):
            node.start()


@contextmanager
def interrupt_clickhouse(node, safe=True, signal="KILL"):
    """
    Stop the given clickhouse instance with the given signal.
    Instance is restarted on context exit.
    """
    try:
        with When(f"{node.name} is stopped"):
            node.stop_clickhouse(safe=safe, signal=signal)
            yield

    finally:
        with When(f"{node.name} is started"):
            node.start_clickhouse(check_version=False)


@contextmanager
def interrupt_network(cluster, node):
    """
    Disconnect the given node container.
    Instance is reconnected on context exit.
    """
    if processor() == "x86_64":
        container = f"vfs_env-{node.name}-1"
    else:
        container = f"vfs_env_arm64-{node.name}-1"

    try:
        with When(f"{node.name} is disconnected"):
            cluster.command(
                None, f"docker network disconnect {DOCKER_NETWORK} {container}"
            )

        yield

    finally:
        with When(f"{node.name} is reconnected"):
            cluster.command(
                None, f"docker network connect {DOCKER_NETWORK} {container}"
            )


@TestStep(Then)
def check_consistency(self, nodes, table_name):
    """SYNC the given nodes and check that they agree about the given table"""

    with When("I make sure all nodes are synced"):
        for node in nodes:
            sync_replica(node=node, table_name=table_name, timeout=10, no_checks=True)

    with When("I query all nodes for their row counts"):
        row_counts = {}
        for node in nodes:
            row_counts[node.name] = get_row_count(node=node, table_name=table_name)

    with Then("All replicas should have the same state"):
        for n1, n2 in combinations(nodes, 2):
            assert row_counts[n1.name] == row_counts[n2.name], error()


@TestStep(When)
def repeat_until_stop(self, stop_event: Event, func, delay=0.5):
    """
    Call the given function with no arguments until stop_event is set.
    Use with parallel=True.
    """
    while not stop_event.is_set():
        func()
        time.sleep(delay)
