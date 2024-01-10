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
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_adding_replicas"
    nodes = self.context.ch_nodes

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with And("I enable vfs"):
        enable_vfs()

    try:
        with Given("I have a replicated table on one node"):
            nodes[0].query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    d UInt64
                ) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '1')
                ORDER BY d
                SETTINGS storage_policy='external'
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
                SETTINGS storage_policy='external'
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


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Core_DropReplica("1.0"))
def drop_replica(self):
    table_name = "vfs_dropping_replicas"
    nodes = self.context.ch_nodes

    with Given("I enable vfs"):
        enable_vfs()

    with And(f"I create a replicated table on each node"):
        replicated_table(
            table_name=table_name,
            columns="d UInt64",
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


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Core_Delete("1.0"))
def delete(self):
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_deleting_replicas"
    nodes = self.context.ch_nodes[:2]

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with And("I enable vfs"):
        enable_vfs()

    try:
        with Given("I have a replicated table"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE {table_name}  (
                        d UInt64
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{i + 1}')
                    ORDER BY d
                    SETTINGS storage_policy='external'
                    """
                )

        with And("I add data to the table on the first node"):
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

        with And("I wait for the second node to sync"):
            nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10)

        with And("I check the row count on the second node"):
            assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)

        with And("The size of the s3 bucket should be the same"):
            check_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=size_after_insert,
                tolerance=0,
                minio_enabled=self.context.minio_enabled,
            )

        with And("I drop the table on the second node"):
            nodes[1].query(f"DROP TABLE {table_name} SYNC")

        with Then("The size of the s3 bucket should be the same"):
            retry(check_bucket_size, timeout=60, delay=1)(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=size_after_insert,
                tolerance=0,
                minio_enabled=self.context.minio_enabled,
            )

        with And("I check the row count on the first node"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

        with And("I drop the table on the first node"):
            nodes[0].query(f"DROP TABLE {table_name} SYNC")

        with Then(
            "The size of the s3 bucket should be very close to the size before adding any data"
        ):
            retry(check_bucket_size, timeout=600, delay=1)(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=size_empty,
                tolerance=5,
                minio_enabled=self.context.minio_enabled,
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication("1.0"))
def no_duplication(self):
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_test_replicas_duplication"
    nodes = self.context.ch_nodes[:2]

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with And("I enable vfs"):
        enable_vfs()

    with And("I create a replicated table"):
        replicated_table(
            table_name=table_name,
            columns="d UInt64, m UInt64",
        )

    with Check("insert"):
        with When("I add data to the table on the first node"):
            insert_random(
                node=nodes[0],
                table_name=table_name,
                columns="d UInt64, m UInt64",
                rows=1000000,
            )

        with And("I get the new size of the s3 bucket"):
            size_after_insert = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )
            size_added = size_after_insert - size_empty

        with And("I add more data to the table on the second node"):
            insert_random(
                node=nodes[0],
                table_name=table_name,
                columns="d UInt64, m UInt64",
                rows=1000000,
            )

        with Then("the size of the s3 bucket should be doubled and no more"):
            expected_size = size_empty + size_added * 2
            check_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=expected_size,
                tolerance=50,
                minio_enabled=self.context.minio_enabled,
            )

    with Check("alter"):
        with When("I rename a column"):
            nodes[1].query(f"ALTER TABLE {table_name} RENAME COLUMN m TO u")

        with Then("the other node should reflect the change"):
            r = nodes[0].query(f"DESCRIBE TABLE {table_name}")
            assert "m\tUInt64" not in r.output, error(r)
            assert "u\tUInt64" in r.output, error(r)

        with And("there should be no change in storage usage"):
            check_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=expected_size,
                tolerance=1500,
                minio_enabled=self.context.minio_enabled,
            )


@TestFeature
@Name("core")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
