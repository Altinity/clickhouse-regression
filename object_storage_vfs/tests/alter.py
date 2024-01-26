#!/usr/bin/env python3
import random

from testflows.core import *

from helpers.alter import *
from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_Alter_PartManipulation,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Index,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Projections,
RQ_SRS_038_DiskObjectStorageVFS_Alter_Update,
"""


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_OrderBy("0.0"))
def order_by(self):
    """Test that MODIFY ORDER BY executes without errors."""
    table_name = "order_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(table_name=table_name, storage_policy="external_vfs")

    with And("I insert some data"):
        insert_random(node=nodes[0], table_name=table_name)

    with Then("I modify ORDER BY with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} ON CLUSTER 'replicated_cluster' ADD COLUMN valueZ Int16, MODIFY ORDER BY (key, valueZ)",
            exitcode=0,
        )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_SampleBy("0.0"))
def sample_by(self):
    """Test that MODIFY SAMPLE BY executes without errors."""
    table_name = "sample_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="external_vfs",
            primary_key="(key, cityHash64(value1))",
            order_by="(key, cityHash64(value1))",
        )

    with And("I insert some data"):
        insert_random(node=nodes[0], table_name=table_name)

    with Then("I modify SAMPLE BY with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} MODIFY SAMPLE BY cityHash64(value1)",
            exitcode=0,
        )


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


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Column("0.0"))
def columns(self):
    """Test that alter column commands execute without errors."""
    table_name = "columns_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(table_name=table_name, storage_policy="external_vfs")

    with And("I insert some data"):
        insert_random(node=nodes[0], table_name=table_name)

    with Check("drop"):
        with When("I delete a column on the second node"):
            alter_table_drop_column(
                node=nodes[1], table_name=table_name, column_name="value3", exitcode=0
            )

    with Check("add"):
        with When("I add a column on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} ADD COLUMN valueX String materialized value1",
                exitcode=0,
            )

    with Check("materialize"):
        with When(f"I materialize the new column on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} MATERIALIZE COLUMN valueX", exitcode=0
            )

    with Check("rename"):
        with When("I rename a column on the second node"):
            alter_table_rename_column(
                node=nodes[1],
                table_name=table_name,
                column_name_old="valueX",
                column_name_new="valueY",
                exitcode=0,
            )

    with Check("modify"):
        with When(f"I modify a column type on the first node"):
            alter_table_modify_column(
                node=nodes[0],
                table_name=table_name,
                column_name="valueY",
                column_type="FixedString(16)",
                exitcode=0,
            )

    with Check("comment"):
        with When("I add a comment to a column on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} COMMENT COLUMN value2 'column comment'",
                exitcode=0,
            )

        with Then("I check that the comment was added"):
            r = nodes[0].query(f"DESCRIBE TABLE {table_name}", exitcode=0)
            assert "column comment" in r.output, error(r)

    with Check("modify remove"):
        with When(f"I remove a column property on the first node"):
            nodes[0].query(
                f"ALTER TABLE {table_name} MODIFY COLUMN value2 REMOVE COMMENT",
                exitcode=0,
            )

    with Check("clear"):
        with When("I clear a column on the first node"):
            alter_table_clear_column_in_partition(
                node=nodes[0],
                table_name=table_name,
                column_name="value1",
                partition_name="tuple()",
                exitcode=0,
            )

    with Check("constraint"):
        with When("I add a contraint on the second node"):
            alter_table_add_constraint(
                node=nodes[1],
                table_name=table_name,
                constraint_name="nonnegativekey",
                expression="(key >= 0)",
                exitcode=0,
            )

    with When("I run DESCRIBE TABLE"):
        r = nodes[2].query(f"DESCRIBE TABLE {table_name}", exitcode=0)

    with Then("The output should contain all columns and comments"):
        assert "value1" in r.output, error(r)
        assert "value2" in r.output, error(r)
        assert "valueY" in r.output, error(r)
        assert "column comment" not in r.output, error(r)

    with And("The table should contain all rows"):
        assert_row_count(node=nodes[2], table_name=table_name)


@TestFeature
@Name("alter")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
