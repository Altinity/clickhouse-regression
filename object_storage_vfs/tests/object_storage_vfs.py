#!/usr/bin/env python3
from testflows.core import *

from s3.tests.common import s3_storage, enable_vfs

from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible("1.0"))
def incompatible_with_zero_copy(self):
    """
    Check that using zero copy replication when vfs is enabled is not allowed.
    """
    cluster = self.context.cluster

    try:
        with Given("I get some nodes to replicate the table"):
            nodes = cluster.nodes["clickhouse"][:2]

        with And(f"cluster nodes {nodes}"):
            nodes = [cluster.node(name) for name in nodes]

        with And("I enable allow_object_storage_vfs"):
            enable_vfs()

        with When(
            "I create a replicated table on each node with both vfs and 0-copy enabled"
        ):
            for i, node in enumerate(nodes):
                r = node.query(
                    f"""
                    CREATE TABLE zero_copy_replication (
                        d UInt64
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/vfs_zero_copy_replication', '{i + 1}')
                    ORDER BY d
                    SETTINGS storage_policy='external', allow_object_storage_vfs=1, allow_remote_fs_zero_copy_replication=1
                """
                )

        with Then("I expect it to fail"):
            assert r.exitcode != 0

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS zero_copy_replication SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_Local("1.0"))
def local_setting(self):
    """
    Check that allow_object_storage_vfs can be enabled per-table
    """
    node = current().context.node

    try:
        with Given("VFS is not enabled"):
            node.query(
                "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
                message='"allow_object_storage_vfs","0"',
            )

        with When("I create a table with allow_object_storage_vfs=1"):
            r = node.query(
                f"""
                CREATE TABLE my_vfs_table (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external', allow_object_storage_vfs=1
                """,
                exitcode=0,
            )

    finally:
        with Finally("I drop the table"):
            node.query("DROP TABLE IF EXISTS my_vfs_table SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled("1.0"))
def disable_vfs_with_vfs_table(self):
    """
    Check that removing global allow_object_storage_vfs=1 when a vfs table exists does not cause data to become inaccessible.
    """
    node = current().context.node

    try:
        with Check("I create a table with VFS enabled"):
            with Given("I enable allow_object_storage_vfs"):
                enable_vfs()

            with And("I have a table with vfs"):
                node.query(
                    f"""
                    CREATE TABLE my_vfs_table (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='external', allow_object_storage_vfs=1
                    """,
                )

            with And("I insert some data"):
                node.query(
                    f"INSERT INTO my_vfs_table SELECT * FROM generateRandom('d UInt64') LIMIT 1000000"
                )

            with Then("the data is accesssible"):
                node.query(
                    f"SELECT count() FROM my_vfs_table",
                    message="1000000",
                )

        with Check("Access the table without VFS"):
            with When("VFS is no longer enabled"):
                node.query(
                    "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
                    message='"allow_object_storage_vfs","0"',
                )

            with Then("the data remains accessible"):
                r = node.query(
                    f"SELECT count() FROM my_vfs_table",
                    message="1000000",
                )

    finally:
        with Finally("I drop the tables on each node"):
            node.query("DROP TABLE IF EXISTS my_vfs_table SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled("1.0"))
def enable_vfs_with_non_vfs_table(self):
    """
    Check that globally enabling allow_object_storage_vfs when a non-vfs table exists does not cause data to become inaccessible.
    """

    node = current().context.node
    try:
        with Given("VFS is not enabled"):
            r = node.query(
                "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
                message='"allow_object_storage_vfs","0"',
            )

        with And("I have a table without vfs"):
            node.query(
                f"""
                CREATE TABLE my_non_vfs_table (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external', allow_object_storage_vfs=0
                """,
            )

        with And("I insert some data"):
            node.query(
                f"INSERT INTO my_non_vfs_table SELECT * FROM generateRandom('d UInt64') LIMIT 1000000"
            )
            node.query(
                f"SELECT count() FROM my_non_vfs_table",
                message="1000000",
            )

        with And("I globally enable allow_object_storage_vfs"):
            enable_vfs()

        with Then("the data remains accessible"):
            r = node.query(
                f"SELECT count() FROM my_non_vfs_table",
                message="1000000",
            )

    finally:
        with Finally("I drop the tables on each node"):
            node.query("DROP TABLE IF EXISTS my_non_vfs_table SYNC")


# RQ_SRS_038_DiskObjectStorageVFS_Core_Delete,
# RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel,
# RQ_SRS_038_DiskObjectStorageVFS_Settings_Global,
# RQ_SRS_038_DiskObjectStorageVFS_Settings_Local,
# RQ_SRS_038_DiskObjectStorageVFS_Settings_SharedSettings,
# RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration,


@TestFeature
@Name("core")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    with Given("I have two S3 disks configured"):
        uri_tiered = self.context.uri + "tiered/"
        # /zero-copy-replication/
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage-vfs/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_tiered": {
                "type": "s3",
                "endpoint": f"{uri_tiered}",
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
        for scenario in loads(current_module(), Scenario):
            scenario()
