#!/usr/bin/env python3
from testflows.core import *

from helpers.create import create_replicated_merge_tree_table
from s3.tests.common import s3_storage, enable_vfs

from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("0.0"))
def stress_inserts(self):
    """
    Check that performing tens of millions of individual inserts does not lose data
    """
    cluster = self.context.cluster

    max_inserts = 50_000_000
    n_cols = 200

    columns = ", ".join([f"d{i} UInt8" for i in range(n_cols)])

    def insert_sequence():
        n = 1000
        while n < max_inserts:
            n = min(n * 10, max_inserts)
            yield n//4
            yield n//2
            yield n

    try:
        with Given("I get some nodes to replicate the table"):
            nodes = cluster.nodes["clickhouse"][:2]

        with And(f"cluster nodes {nodes}"):
            nodes = [cluster.node(name) for name in nodes]

        with Given("I enable allow_object_storage_vfs"):
            enable_vfs()

        with Given(f"I create a replicated table with {n_cols} cols on each node"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE vfs_stress_test ({columns}) 
                    ENGINE = ReplicatedMergeTree('/clickhouse/vfs_stress_test', '{i + 1}')
                    ORDER BY d0
                    SETTINGS storage_policy='external', allow_object_storage_vfs=1
                    """
                )

        for n_inserts in insert_sequence():
            with When(f"I perform {n_inserts:,} individual inserts"):
                node.query(
                    f"""
                    INSERT INTO vfs_stress_test SELECT * FROM generateRandom('{columns}') 
                    LIMIT {n_inserts} SETTINGS max_insert_block_size=1,  max_insert_threads=32
                    """,
                    timeout=600,
                )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfs_stress_test SYNC")


# RQ_SRS_038_DiskObjectStorageVFS_AWS
# RQ_SRS_038_DiskObjectStorageVFS_MinIO
# RQ_SRS_038_DiskObjectStorageVFS_GCS


@TestOutline(Feature)
@Name("stress")
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
