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
    with When("I create a replicated table with both vfs and 0-copy enabled"):
        r, _ = replicated_table(
            table_name="vfs_zero_copy_replication",
            allow_vfs=True,
            allow_zero_copy=True,
            exitcode=None,
        )

    with Then("I expect it to fail"):
        assert r.exitcode != 0, error()


@TestScenario
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS_Settings_Global("1.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Settings_Local("1.0"),
)
def vfs_setting(self):
    """
    Check that allow_object_storage_vfs global and local behave the same
    """
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    nodes = self.context.ch_nodes

    with Check("global"):
        with Given("VFS is globally enabled"):
            enable_vfs()

        with Then("creating a table is successful"):
            r, _ = replicated_table(
                table_name="my_local_vfs_table", columns="d UInt64", exitcode=0
            )

        with And("I add data to the table"):
            insert_random(
                node=nodes[0],
                table_name="my_local_vfs_table",
                columns="d UInt64",
                rows=1000000,
            )

        with And("I get the size of the s3 bucket"):
            size_global = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )

    with Check("local"):
        with Given("VFS is not globally enabled"):
            check_global_vfs_state(enabled=False)

        with Then("creating a table with allow_object_storage_vfs=1 is successful"):
            replicated_table(
                table_name="my_global_vfs_table",
                columns="d UInt64",
                allow_vfs=True,
                exitcode=0
            )


        with And("I add data to the table"):
            insert_random(
                node=nodes[0],
                table_name="my_global_vfs_table",
                columns="d UInt64",
                rows=1000000,
            )

        with And("I get the size of the s3 bucket"):
            size_local = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )

    with Check("bucket sizes match"):
        with Then("bucket sizes should match"):
            assert size_global == size_local, error()


# RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared,


@TestFeature
@Name("settings")
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS("1.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration("1.0"),
)
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
