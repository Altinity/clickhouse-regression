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
        r = replicated_table(
            table_name="vfs_zero_copy_replication",
            allow_vfs=True,
            allow_zero_copy=True,
        )

    with Then("I expect it to fail"):
        assert r.exitcode != 0, error()


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_Local("1.0"))
def local_setting(self):
    """
    Check that allow_object_storage_vfs can be enabled per-table
    """
    with Given("VFS is not globally enabled"):
        check_global_vfs_state(enabled=False)

    with Then("creating a table with allow_object_storage_vfs=1 is successful"):
        r = replicated_table(
            table_name="my_vfs_table",
            allow_vfs=True,
        )
        assert r.exitcode == 0, error()


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Settings_Global("1.0"))
def global_setting(self):
    """
    Check that allow_object_storage_vfs can be enabled globally
    """
    with Given("VFS is globally enabled"):
        enable_vfs()

    with Then("creating a table is successful"):
        r = replicated_table(
            table_name="my_vfs_table",
        )
        assert r.exitcode == 0, error()


# RQ_SRS_038_DiskObjectStorageVFS_Settings_Shared,


@TestFeature
@Name("settings")
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS("1.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Providers_Configuration("1.0"),
)
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
