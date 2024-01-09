#!/usr/bin/env python3
import json

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from s3.tests.common import s3_storage, enable_vfs, check_bucket_size, get_bucket_size

DEFAULT_COLUMNS = "key UInt32, value1 String, value2 String, value3 String"


@TestStep(Given)
def s3_config(self):
    with Given("I have two S3 disks configured"):
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage-vfs/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_tiered": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage-vfs-tiered",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
        }

    with And(
        """I have a storage policy configured to use the S3 disk and a tiered
             storage policy using both S3 disks"""
    ):
        policies = {
            "external": {"volumes": {"external": {"disk": "external"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "external"},
                    "external": {"disk": "external_tiered"},
                }
            },
        }

    with s3_storage(disks, policies, restart=True):
        yield


@TestStep(Given)
def check_global_vfs_state(self, node=None, enabled: bool = True):
    if node is None:
        node = current().context.node

    node.query(
        "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
        message=f'"allow_object_storage_vfs","{int(enabled)}"',
        exitcode=0,
    )


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    if node is None:
        node = current().context.node
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON",
        # message=f'"count()": "{rows}"',
        exitcode=0,
    )
    actual_count = json.loads(r.output)["data"][0]["count()"]
    assert f"{rows}" == actual_count, error()


@TestStep(Given)
def replicated_table(
    self,
    table_name: str = None,
    storage_policy: str = "external",
    cluster_name: str = "replicated_cluster",
    columns: str = None,
    order_by: str = None,
    allow_vfs: bool = None,
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

    settings = [f"storage_policy='{storage_policy}'"]

    if allow_vfs is not None:
        settings.append(f"allow_object_storage_vfs={int(allow_vfs)}")

    if allow_zero_copy is not None:
        settings.append(f"allow_remote_fs_zero_copy_replication={int(allow_zero_copy)}")

    try:
        with Given("I have a table"):
            r = node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} 
                ON CLUSTER '{cluster_name}' ({columns}) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
                ORDER BY {order_by}
                SETTINGS {', '.join(settings)}
                """,
                settings=[("distributed_ddl_task_timeout ", 360)],
                exitcode=exitcode,
            )

        yield r, table_name

    finally:
        with Finally(f"I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} ON CLUSTER '{cluster_name}'")


@TestStep(Given)
def insert_random(self, node, table_name, columns: str = None, rows: int = 1000000):
    if columns is None:
        columns = DEFAULT_COLUMNS

    node.query(
        f"INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') LIMIT {rows}",
        exitcode=0,
    )
