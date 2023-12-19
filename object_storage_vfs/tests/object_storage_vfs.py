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
    skip("TODO")
    


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
