#!/usr/bin/env python3
from testflows.core import *

from s3.tests.common import s3_storage, enable_vfs

from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_IncompatibleSettings("1.0"))
def incompatible_settings(self):
    cluster = self.context.cluster

    try:
        with Given("I get some nodes to replicate the table"):
            nodes = cluster.nodes["clickhouse"][:2]

        with And(f"cluster nodes {nodes}"):
            nodes = [cluster.node(name) for name in nodes]

        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

        with When("I create a replicated table on each node"):
            for i, node in enumerate(nodes):
                node.restart()
                r = node.query(
                    f"""
                    CREATE TABLE zero_copy_replication (
                        d UInt64
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/vfs_zero_copy_replication', '{i + 1}')
                    ORDER BY d
                    SETTINGS storage_policy='external', allow_remote_fs_zero_copy_replication=1
                """
                )

        with Then("Exitcode should not be zero"):
            assert r.exitcode != 0

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS zero_copy_replication SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_PreservesData("1.0"))
def data_preservation(self):
    node = current().context.node

    try:
        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

        with And("I have a table with vfs"):
            node.restart()
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

        with Then("The data is accesssible"):
            node.query(
                f"SELECT count(*) FROM my_vfs_table",
                message="1000000",
            )

        with When("VFS is no longer enabled"):
            node.query(
                "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
                message='"allow_object_storage_vfs","0"',
            )

        with Then("The data becomes inaccessible"):
            r = node.query(f"SELECT count(*) FROM my_vfs_table")
            pause(r.output)

        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

        with Then("The data becomes accessible again"):
            r = node.query(f"SELECT count(*) FROM my_vfs_table")
            pause(r.output)

    finally:
        with Finally("I drop the tables on each node"):
            node.query("DROP TABLE IF EXISTS my_vfs_table SYNC")

    try:
        with Given("VFS is not enabled"):
            r = node.query(
                "SELECT name, value, changed FROM system.merge_tree_settings WHERE name = 'allow_object_storage_vfs' FORMAT CSV",
                message='"allow_object_storage_vfs","0"',
            )

        with Given("I have a table without vfs"):
            node.restart()
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
                f"SELECT count(*) FROM my_non_vfs_table",
                message="1000000",
            )

        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

        with Then("The data remains accessible"):
            r = node.query(f"SELECT count(*) FROM my_non_vfs_table")
            pause(r.output)

    finally:
        with Finally("I drop the tables on each node"):
            node.query("DROP TABLE IF EXISTS my_non_vfs_table SYNC")


# @TestScenario
# @Requirements(RQ_SRS_038_DiskObjectStorageVFS_Migration("1.0"))
# def migration(self):
#     pass


# @TestScenario
# @Requirements(RQ_SRS_038_DiskObjectStorageVFS_DeleteInParallel("1.0"))
# def parallel_delete(self):
#     pass


# @TestScenario
# @Requirements(RQ_SRS_038_DiskObjectStorageVFS_SharedSettings("1.0"))
# def shared_settings(self):
#     pass


# @TestScenario
# @Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("1.0"))
# def performance(self):
#     pass

# RQ_SRS_038_DiskObjectStorageVFS_AWS
# RQ_SRS_038_DiskObjectStorageVFS_MinIO
# RQ_SRS_038_DiskObjectStorageVFS_GCS


@TestOutline(Feature)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def outline(self, uri, key, secret, node="clickhouse1"):
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
