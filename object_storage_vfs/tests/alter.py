#!/usr/bin/env python3
import random

from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_Alter_PartManipulation,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Index,
RQ_SRS_038_DiskObjectStorageVFS_Alter_OrderBy,
RQ_SRS_038_DiskObjectStorageVFS_Alter_SampleBy,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Projections,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Column,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Update,
"""


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Fetch("0.0"))
@Examples("fetch_item", [["PARTITION 2"], ["PART '2_0_0_0'"]])
def fetch(self, fetch_item):
    """Test fetching a new part from another replica."""

    nodes = self.context.ch_nodes
    node = nodes[0]

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=node, table_name=source_table_name)

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = node.query(f"SELECT count() FROM {source_table_name} where key % 4 = 2;")
        row_count = int(r.output)

    with When("I fetch a partition from the first table"):
        node.query(
            f"ALTER TABLE {destination_table_name} FETCH {fetch_item} FROM '/clickhouse/tables/{source_table_name}'"
        )

    with And("I attach the partition to the second table"):
        node.query(f"ALTER TABLE {destination_table_name} ATTACH {fetch_item}")

    with Then("I check the number of rows on the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=destination_table_name, rows=row_count
            )


@TestFeature
@Name("alter")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
