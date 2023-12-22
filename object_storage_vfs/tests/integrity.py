#!/usr/bin/env python3
from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Integrity_VFSToggled("1.0"))
def disable_vfs_with_vfs_table(self):
    """
    Check that removing global allow_object_storage_vfs=1 when a vfs table exists does not cause data to become inaccessible.
    """
    node = current().context.node

    try:
        with Check("I create a table with VFS globally enabled"):
            with Given("I enable allow_object_storage_vfs"):
                enable_vfs()

            with And("I have a table with vfs"):
                node.query(
                    f"""
                    CREATE TABLE my_vfs_table (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='external'
                    """,
                )

            with And("I insert some data"):
                node.query(
                    f"INSERT INTO my_vfs_table SELECT * FROM generateRandom('d UInt64') LIMIT 1000000"
                )

            with Then("the data is accesssible"):
                assert_row_count(node=node, table_name="my_vfs_table", rows=1000000)

        with Check("Access the table without VFS"):
            with When("VFS is no longer enabled"):
                check_global_vfs_state(node=node, enabled=False)

            with Then("the data remains accessible"):
                assert_row_count(node=node, table_name="my_vfs_table", rows=1000000)

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

    with Given("VFS is not enabled"):
        check_global_vfs_state(enabled=False)

    with And("I have a table without vfs"):
        replicated_table(
            table_name="my_non_vfs_table",
            columns="d UInt64",
            allow_vfs=False,
        )

    with And("I insert some data"):
        node.query(
            f"INSERT INTO my_non_vfs_table SELECT * FROM generateRandom('d UInt64') LIMIT 1000000"
        )
        assert_row_count(node=node, table_name="my_non_vfs_table", rows=1000000)

    with And("I globally enable allow_object_storage_vfs"):
        enable_vfs()

    with Then("the data remains accessible"):
        assert_row_count(node=node, table_name="my_non_vfs_table", rows=1000000)


# RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration
# RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLMove
# RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLDelete


@TestFeature
@Name("integrity")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
