#!/usr/bin/env python3
import json
import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid, check_clickhouse_version

from s3.tests.common import s3_storage, check_bucket_size, get_bucket_size


DEFAULT_COLUMNS = "key UInt32, value1 String, value2 String, value3 String"
WIDE_PART_SETTING = "min_bytes_for_wide_part=0"
COMPACT_PART_SETTING = "min_bytes_for_wide_part=100000"


@TestStep(Given)
def s3_config(self):
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

    with s3_storage(disks, policies, restart=True, timeout=60):
        yield


@TestStep(Given)
def check_vfs_state(
    self, node=None, enabled: bool = True, config_file="enable_vfs.xml"
):
    if node is None:
        node = current().context.node

    c = f'grep "<allow_vfs>1" /etc/clickhouse-server/config.d/{config_file}'

    if enabled:
        node.command(c, exitcode=0)
    else:
        r = node.command(c, exitcode=None)
        assert r.exitcode in [1, 2], error()


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    if node is None:
        node = current().context.node
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSONColumns",
        exitcode=0,
    )
    actual_count = int(json.loads(r.output)["count()"][0])
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
):
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
    no_checks=False,
    settings=None,
):
    if columns is None:
        columns = DEFAULT_COLUMNS

    if settings:
        settings = "SETTINGS " + settings
    else:
        settings = ""

    node.query(
        f"INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') LIMIT {rows} {settings}",
        no_checks=no_checks,
        exitcode=0,
    )


@TestStep(Given)
def create_one_replica(
    self,
    node,
    table_name,
    columns="d UInt64",
    order_by='d',
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

    r = node.query(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({columns}) 
        ENGINE=ReplicatedMergeTree('/clickhouse/tables/{replica_path_suffix}', '{replica_name}')
        ORDER BY ({order_by})
        SETTINGS storage_policy='{storage_policy}'
        """,
        no_checks=no_checks,
        exitcode=0,
    )
    return r


@TestStep(Given)
def delete_one_replica(self, node, table_name):
    r = node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0)
    return r


@TestStep(Given)
def storage_config(self, disks, policies, nodes=None, restart=False, timeout=30, config_file="storage_config.xml"):
    with s3_storage(
        disks,
        policies,
        nodes=nodes,
        restart=restart,
        timeout=timeout,
        config_file=config_file,
    ):
        yield

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
        skip("vfs not supported on ClickHouse < 24.1")

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

    with s3_storage(
        disks,
        policies,
        nodes=nodes,
        restart=True,
        timeout=timeout,
        config_file=config_file,
    ):
        yield


@TestStep
def get_stable_bucket_size(
    self,
    name,
    prefix,
    minio_enabled,
    access_key,
    key_id,
    delay=10,
):
    with By("Checking the current bucket size"):
        size_previous = get_bucket_size(
            name=name,
            prefix=prefix,
            minio_enabled=minio_enabled,
            access_key=access_key,
            key_id=key_id,
        )
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
    current_size = get_stable_bucket_size(
        name=name,
        prefix=prefix,
        minio_enabled=minio_enabled,
        access_key=self.context.secret_access_key,
        key_id=self.context.access_key_id,
        delay=10,
    )
    assert abs(current_size - expected_size) <= tolerance, error()
