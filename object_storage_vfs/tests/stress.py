#!/usr/bin/env python3
from testflows.core import *
from testflows.asserts import error

from helpers.create import create_replicated_merge_tree_table
from s3.tests.common import s3_storage, enable_vfs

from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Performance("1.0"))
def stress_inserts(self):
    """
    Check that performing tens of millions of individual inserts does not cause data to be lost
    """
    cluster = self.context.cluster

    max_inserts = 50_000_000
    n_cols = 40

    columns = ", ".join([f"d{i} UInt8" for i in range(n_cols)])

    def insert_sequence():
        """
        Produce a sequence of increasing numbers.
        It is desireable to know how close ClickHouse gets to max_inserts before failing.
        """
        n = 1000
        while n < max_inserts:
            n = min(n * 10, max_inserts)
            yield n // 4
            yield n // 2
            yield n

    try:
        with Given("I get some nodes to replicate the table"):
            nodes = cluster.nodes["clickhouse"][:2]

        with And(f"cluster nodes {nodes}"):
            nodes = [cluster.node(name) for name in nodes]

        with And("I enable allow_object_storage_vfs"):
            enable_vfs()

        with And(f"I create a replicated table with {n_cols} cols on each node"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE vfs_stress_test ({columns}) 
                    ENGINE = ReplicatedMergeTree('/clickhouse/vfs_stress_test', '{i + 1}')
                    ORDER BY d0
                    SETTINGS storage_policy='external', allow_object_storage_vfs=1
                    """
                )

        total_rows = 0
        for n_inserts in insert_sequence():
            with When(f"I perform {n_inserts:,} individual inserts"):
                nodes[0].query(
                    f"""
                    INSERT INTO vfs_stress_test SELECT * FROM generateRandom('{columns}') 
                    LIMIT {n_inserts} SETTINGS max_insert_block_size=1, max_insert_threads=32
                    """,
                    exitcode=0,
                    timeout=600,
                )
                total_rows += n_inserts

            with Then(f"there should be {total_rows} rows"):
                r = nodes[0].query("SELECT count() FROM vfs_stress_test")
                assert r.output == str(total_rows), error()

        with When("I perform optimize on each node"):
            for node in nodes:
                node.query("OPTIMIZE TABLE vfs_stress_test")

        with Then(f"there should still be {total_rows} rows"):
            r0 = nodes[0].query("SELECT count() FROM vfs_stress_test")
            r1 = nodes[1].query("SELECT count() FROM vfs_stress_test")

            assert r0.output == r1.output == str(total_rows), error()


    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfs_stress_test SYNC")


# RQ_SRS_038_DiskObjectStorageVFS_AWS
# RQ_SRS_038_DiskObjectStorageVFS_MinIO
# RQ_SRS_038_DiskObjectStorageVFS_GCS


@TestFeature
@Name("stress")
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
