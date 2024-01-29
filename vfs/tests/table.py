#!/usr/bin/env python3
import time, datetime

from testflows.core import *
from testflows.combinatorics import permutations

from vfs.tests.steps import *
from vfs.requirements import *


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_Detach("1.0"))
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
            nodes[1].command(f"rm {part_path}/count.txt")

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


# RQ_SRS_038_DiskObjectStorageVFS_Integrity_ConnectionInterruption
# RQ_SRS_038_DiskObjectStorageVFS_Table_StoragePolicy
# RQ_SRS_038_DiskObjectStorageVFS_Table_BackgroundCollapse,


@TestFeature
@Name("table")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
