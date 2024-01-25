#!/usr/bin/env python3
import time, datetime

from testflows.core import *
from testflows.combinatorics import permutations

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


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


@TestStep(When)
def insert_data_time(self, node, table_name, days_ago, rows):
    t = time.mktime(
        (datetime.date.today() - datetime.timedelta(days=days_ago)).timetuple()
    )
    values = ",".join(f"({x},{t})" for x in range(rows))
    node.query(f"INSERT INTO {table_name} VALUES {values}")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_TTLDelete("1.0"))
def ttl_delete(self):
    """Check that TTL delete works properly when <allow_vfs> parameter is set to 1."""
    nodes = self.context.ch_nodes
    table_name = "ttl_delete"

    with Given("I enable vfs"):
        enable_vfs(disk_names=["external", "external_tiered"])

    with And("I have a replicated table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="tiered",
            columns="d UInt64, d1 DateTime",
            ttl="d1 + interval 2 day",
        )

    with When("I add data to the table"):
        with By("first inserting 200k rows"):
            insert_data_time(
                node=nodes[0], table_name=table_name, days_ago=7, rows=200000
            )

        with And("another insert of 400k rows"):
            insert_data_time(
                node=nodes[1], table_name=table_name, days_ago=3, rows=400000
            )

        with And("a large insert of 800k rows"):
            insert_data_time(
                node=nodes[2], table_name=table_name, days_ago=0, rows=800000
            )

    with Then("I check the row count"):
        retry(assert_row_count, timeout=5, delay=1)(
            node=nodes[0], table_name=table_name, rows=800000
        )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_TTLMove("1.0"))
def ttl_move(self):
    """Check that TTL moves work properly when <allow_vfs> parameter is set to 1."""
    nodes = self.context.ch_nodes
    table_name = "ttl_move"

    with Given("I enable vfs"):
        enable_vfs(disk_names=["external", "external_tiered"])

    with And("I have a replicated table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="tiered",
            columns="d UInt64, d1 DateTime",
            ttl="d1 + interval 2 day to volume 'external'",
        )

    with When("I add data to the table"):
        with By("first inserting 200k rows"):
            insert_data_time(
                node=nodes[0], table_name=table_name, days_ago=7, rows=200000
            )

        with And("another insert of 400k rows"):
            insert_data_time(
                node=nodes[1], table_name=table_name, days_ago=3, rows=400000
            )

        with And("a large insert of 800k rows"):
            insert_data_time(
                node=nodes[2], table_name=table_name, days_ago=0, rows=800000
            )

    with Then("I check the row count"):
        retry(assert_row_count, timeout=5, delay=1)(
            node=nodes[0], table_name=table_name, rows=1400000
        )


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Table_Migration("1.0"))
@Examples("source destination", permutations(["replicated", "zero-copy", "vfs"], 2))
def migration(self, source, destination):
    node = self.context.node

    with Given("I have a replicated table"):
        _, replicated_table_name = replicated_table_cluster(
            storage_policy="external_no_vfs"
        )

    with And("I have a zero-copy table"):
        _, zero_copy_table_name = replicated_table_cluster(
            storage_policy="external_no_vfs", allow_zero_copy=True
        )

    with And("I have a vfs table"):
        _, vfs_table_name = replicated_table_cluster(storage_policy="external_vfs")

    table_names = {
        "replicated": replicated_table_name,
        "zero-copy": zero_copy_table_name,
        "vfs": vfs_table_name,
    }

    with And(f"I select {source} as the source table"):
        source_table_name = table_names[source]

    with And(f"I select {destination} as the destination table"):
        dest_table_name = table_names[destination]

    with And("I insert data to the source table"):
        insert_random(node=node, table_name=source_table_name, rows=1000000)

    with When("I copy the source table to the destination table"):
        node.query(f"INSERT INTO {dest_table_name} SELECT * from {source_table_name}")

    with And("I delete the source table"):
        node.query(f"DROP TABLE {source_table_name}")

    with Then("the data should be in the destination table"):
        assert_row_count(node=node, table_name=dest_table_name, rows=1000000)


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
