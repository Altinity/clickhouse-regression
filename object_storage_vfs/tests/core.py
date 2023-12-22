#!/usr/bin/env python3
from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS_Core_AddReplica("1.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication("1.0"),
)
def add_replica(self):
    cluster = self.context.cluster
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_adding_replicas"

    with Given("I get some cluster nodes"):
        nodes = cluster.nodes["clickhouse"]

    with And(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    with And("I get the size of the s3 bucket before adding data"):
        size_empty = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    try:
        with Given("I have a table"):
            nodes[0].query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    d UInt64
                ) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '1')
                ORDER BY d
                SETTINGS storage_policy='external', allow_object_storage_vfs=1
                """,
            )

        with And("I add data to the table"):
            insert_random(
                node=nodes[0], table_name=table_name, columns="d UInt64", rows=1000000
            )

        with And("I get the new size of the s3 bucket"):
            size_after_insert = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )

        with And("I create a replicated table on the second node"):
            nodes[1].query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    d UInt64
                ) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '2')
                ORDER BY d
                SETTINGS storage_policy='external', allow_object_storage_vfs=1
                """,
            )

        with Then(
            """The size of the s3 bucket should be 1 byte more
                    than previously because of the additional replica"""
        ):
            check_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=size_after_insert + 1,
                tolerance=0,
                minio_enabled=self.context.minio_enabled,
            )

        with And("I check the row count on the first node"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

        with And("I wait for the second node to sync"):
            nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10)

        with And("I check the row count on the second node"):
            assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

    with Then(
        """The size of the s3 bucket should be very close to the size
                before adding any data"""
    ):
        check_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            expected_size=size_empty,
            tolerance=5,
            minio_enabled=self.context.minio_enabled,
        )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Core_DropReplica("1.0"))
def drop_replica(self):
    cluster = self.context.cluster
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_dropping_replicas"

    with Given("I get some cluster nodes"):
        nodes = cluster.nodes["clickhouse"]

    with And(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    with And(f"I create a replicated table on each node"):
        replicated_table(
            table_name=table_name,
            columns="d UInt64",
            allow_vfs=True,
        )

    with When("I add data to the table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns="d UInt64", rows=500000
        )

    with And("I stop the other node"):
        nodes[1].stop()

    with And("I add more data to the table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns="d UInt64", rows=500000
        )

    with Then("I restart the other node"):
        nodes[1].start()

    with And("I check the row count on the first node"):
        assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

    with And("I wait for the second node to sync"):
        nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10)

    with And("I check the row count on the second node"):
        assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)

    
# RQ_SRS_038_DiskObjectStorageVFS_Core_Delete
# RQ_SRS_038_DiskObjectStorageVFS_Core_DeleteInParallel
# RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication

@TestFeature
@Name("core")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret
    self.context.bucket_name = "root"
    self.context.bucket_path = "data/object-storage-vfs"

    self.context.minio_enabled = True

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
