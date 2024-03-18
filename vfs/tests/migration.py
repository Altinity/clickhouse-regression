#!/usr/bin/env python3
from testflows.core import *
from testflows.combinatorics import permutations

from vfs.tests.steps import *
from vfs.requirements import *


@TestOutline(Scenario)
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Table_Migration("1.0"))
@Examples("source destination", permutations(["replicated", "zero-copy", "vfs"], 2))
def migration(self, source, destination):
    """Test migrating tables between disks with and without vfs."""

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
        delete_one_replica(node=node, table_name=source_table_name)

    with Then("the data should be in the destination table"):
        assert_row_count(node=node, table_name=dest_table_name, rows=1000000)


@TestFeature
@Name("migration")
def feature(self):
    """Test migrating tables between disks with and without vfs."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
