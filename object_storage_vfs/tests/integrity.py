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
        with Check("create a table with VFS globally enabled"):
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

        with Check("access the table without VFS"):
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
        replicated_table_cluster(
            table_name="my_non_vfs_table",
            columns="d UInt64",
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


@TestScenario
def bad_detached_part(self):
    """
    Test that a bad detached part on one replica does not affect the other replica.
    """

    table_name = "detach_table"

    with Given("I have a pair of clickhouse nodes"):
        nodes = self.context.ch_nodes[:2]

    with And("I enable allow_object_storage_vfs"):
        enable_vfs()

    try:
        with When("I create a replicated table on each node"):
            for i, node in enumerate(nodes):
                node.restart()
                node.query(
                    f"""
                    CREATE TABLE {table_name} (
                        d UInt64,
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{i + 1}')
                    ORDER BY d
                    SETTINGS storage_policy='external', min_bytes_for_wide_part=0
                """
                )

        with And("I insert data on the second node"):
            nodes[1].query(f"INSERT INTO {table_name} VALUES (123)")

        with And("I sync the first node"):
            nodes[0].query(f"SYSTEM SYNC REPLICA {table_name}")

        with And("I get the path for the part"):
            r = nodes[1].query(
                f"SELECT path FROM system.parts where table='{table_name}' and name='all_0_0_0'"
            )
            part_path = r.output
            assert part_path.startswith("/"), error("Expected absolute path!")

        with And("I delete the part's count.txt"):
            nodes[1].command(f'rm {part_path}/count.txt')

        with And("I detach the table on the second node"):
            nodes[1].query(f"DETACH TABLE {table_name} SYNC")

        with And("I reattach the table on the second node"):
            nodes[1].query(f"ATTACH TABLE {table_name}")

        with And("I check detached parts on the second node"):
            r = nodes[1].query(
                f"SELECT reason, name FROM system.detached_parts where table='{table_name}'"
            )
            assert r.output == "broken-on-start	broken-on-start_all_0_0_0", error()

        with And("I drop the table on the second node"):
            nodes[1].query(f"DROP TABLE {table_name} SYNC")

        with Then("The first node should still have the data"):
            r = nodes[0].query(f"SELECT * FROM {table_name}")
            assert r.output == "123", error()

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


# RQ_SRS_038_DiskObjectStorageVFS_Integrity_Migration
# RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLMove
# RQ_SRS_038_DiskObjectStorageVFS_Integrity_TTLDelete


@TestFeature
@Name("integrity")
def feature(self):

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
