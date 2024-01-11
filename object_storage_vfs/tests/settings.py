#!/usr/bin/env python3
from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_ZeroCopyIncompatible("1.0"))
def incompatible_with_zero_copy(self):
    """
    Check that using zero copy replication when vfs is enabled is not allowed.
    """
    with Given("VFS is globally enabled"):
        enable_vfs()

    with When("I create a replicated table with both vfs and 0-copy enabled"):
        r, _ = replicated_table(
            table_name="vfs_zero_copy_replication",
            allow_zero_copy=True,
            exitcode=None,
        )

    with Then("I expect it to fail"):
        assert r.exitcode != 0, error()


@TestStep(When)
def create_insert_measure_replicated_table(self):
    nodes = self.context.ch_nodes
    n_rows = 100_000
    columns = "d UInt64, m UInt64"

    with Given("an s3 bucket with a known amount of data"):
        size_before = get_bucket_size(
            name=self.context.bucket_name,
            prefix=self.context.bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with When("a replicated table is created successfully"):
        _, table_name = replicated_table(columns=columns, exitcode=0)

    with And("I add data to the table"):
        insert_random(
            node=nodes[0],
            table_name=table_name,
            columns=columns,
            rows=n_rows,
        )

    with And("I wait for the replicas to sync", flags=TE):
        # nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=300)
        # nodes[2].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=300)
        retry(assert_row_count, timeout=120, delay=1)(
            node=nodes[0], table_name=table_name, rows=n_rows
        )
        retry(assert_row_count, timeout=120, delay=1)(
            node=nodes[1], table_name=table_name, rows=n_rows
        )
        retry(assert_row_count, timeout=120, delay=1)(
            node=nodes[2], table_name=table_name, rows=n_rows
        )

    with And("I get the size of the data added to s3"):
        size_after = get_bucket_size(
            name=self.context.bucket_name,
            prefix=self.context.bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )
        size = size_after - size_before

    return size


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_Global("1.0"))
def disk_setting(self):
    """
    Check that allow_vfs can be globally enabled
    """
    with Given("VFS is not globally enabled"):
        check_global_vfs_state(enabled=False)

    with When("I measure the disk usage after create and insert without vfs"):
        size_no_vfs = create_insert_measure_replicated_table()

    with Given("VFS is globally enabled"):
        enable_vfs()

    with When("I measure the disk usage after create and insert with global vfs"):
        size_global = create_insert_measure_replicated_table()

    with Then("Data usage should be less than half compared to no vfs"):
        assert size_global <= size_no_vfs // 2, error()


# RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared


@TestFeature
@Name("settings")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration("1.0"))
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
