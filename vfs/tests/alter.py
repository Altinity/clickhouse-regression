#!/usr/bin/env python3
import random

from testflows.core import *
from testflows.combinatorics import product

from helpers.alter import *
from vfs.tests.steps import *
from vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_Alter_Freeze,
RQ_SRS_038_DiskObjectStorageVFS_Alter_MovePart,
"""


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Update("0.0"))
def update_delete(self):
    """Test that ALTER UPDATE and DELETE execute without errors."""
    table_name = "update_table"
    nodes = self.context.ch_nodes
    columns = "key UInt64, d Int64, e Int64"

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy="external_vfs", columns=columns
        )

    with And("I insert some data"):
        insert_random(node=nodes[0], table_name=table_name, columns=columns)

    with Then("I lightweight DELETE with success"):
        nodes[0].query(f"DELETE FROM {table_name} WHERE (e % 4 = 0)", exitcode=0)

    with And("I UPDATE with success"):
        alter_table_update_column(
            table_name=table_name,
            column_name="d",
            expression="(e * 2)",
            condition="(d > e)",
            node=nodes[0],
            exitcode=0,
        )

    with And("I OPTIMIZE FINAL with success"):
        nodes[0].query(f"OPTIMIZE TABLE {table_name} FINAL", exitcode=0)

    with And("I DELETE with success"):
        alter_table_delete_rows(
            table_name=table_name, condition="(d < e)", node=nodes[0], exitcode=0
        )


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


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Index("0.0"))
def index(self):
    """Test that MODIFY ORDER BY executes without errors."""
    table_name = "index_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(table_name=table_name, storage_policy="external_vfs")

    with And("I insert some data"):
        insert_random(node=nodes[0], table_name=table_name)

    with Check("add"):
        with When("I add an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} ADD INDEX idxtest value1 TYPE set(100) GRANULARITY 2",
                exitcode=0,
            )

    with Check("materialize"):
        with When("I materialize an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} MATERIALIZE INDEX idxtest",
                exitcode=0,
            )

    with Check("clear"):
        with When("I clear an index"):
            retry(nodes[0].query, timeout=15, delay=1)(
                f"ALTER TABLE {table_name} CLEAR INDEX idxtest",
                exitcode=0,
            )

    with Check("drop"):
        with When("I drop an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} DROP INDEX idxtest",
                exitcode=0,
            )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Projections("0.0"))
def projection(self):
    """Test that adding projections does not error."""
    table_name = "proj_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(table_name=table_name, storage_policy="external_vfs")

    with When("I add a projection with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} ADD PROJECTION value1_projection (SELECT * ORDER BY value1)",
            exitcode=0,
        )

    with And("I materialize the projection with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} MATERIALIZE PROJECTION value1_projection",
            exitcode=0,
        )

    with Then("I insert data with success"):
        insert_random(node=nodes[0], table_name=table_name)

    with And("I clear the projection with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} CLEAR PROJECTION value1_projection",
            exitcode=0,
        )

    with And("I drop the projection with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} DROP PROJECTION value1_projection",
            exitcode=0,
        )


@TestOutline(Scenario)
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS_Alter_Fetch("0.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Alter_Attach("0.0"),
)
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
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_AttachFrom("0.0"))
def attach_from(self):
    """Test attaching a part from one table to another"""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = 1000000

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=node, table_name=source_table_name, rows=insert_rows)

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = node.query(f"SELECT count() FROM {source_table_name} where key % 4 = 2;")
        row_count = int(r.output)

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} ATTACH {fetch_item} FROM {source_table_name}"
        )

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=source_table_name, rows=insert_rows
            )

    with And("I check the number of rows on the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=destination_table_name, rows=row_count
            )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_MoveToTable("0.0"))
def move_to_table(self):
    """Test moving a part from one table to another"""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = 1000000
    storage_policy = "external"
    source_table_name = "table_move_src"
    destination_table_name = "table_move_dest"

    with Given("I have two replicated tables"):
        replicated_table_cluster(
            table_name=source_table_name,
            storage_policy=storage_policy,
            partition_by="key % 4",
        )
        replicated_table_cluster(
            table_name=destination_table_name,
            storage_policy=storage_policy,
            partition_by="key % 4",
        )

    with And("I insert data into the first table"):
        insert_random(node=node, table_name=source_table_name, rows=insert_rows)

    with And("I insert less data into the second table"):
        insert_random(
            node=node, table_name=destination_table_name, rows=insert_rows // 2
        )

    with And("I count the rows in a partition on the first table"):
        r = node.query(f"SELECT count() FROM {source_table_name} where key % 4 = 2;")
        row_count = int(r.output)
        note(f"1 {row_count}")

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {source_table_name} MOVE {fetch_item} TO TABLE {destination_table_name}"
        )

    with Then("I check the number of rows in the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=source_table_name, rows=(insert_rows - row_count)
            )

    with And("I check the number of rows in the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node,
                table_name=destination_table_name,
                rows=(insert_rows // 2 + row_count),
            )


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Replace("0.0"))
def replace(self):
    """Test attaching a part from one table to another"""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = 1000000

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=node, table_name=source_table_name, rows=insert_rows)

    with And("I insert a smaller amount of data into the second table"):
        insert_random(
            node=node, table_name=destination_table_name, rows=insert_rows // 2
        )

    with And("I count the rows in a partition on the first table"):
        r = node.query(f"SELECT count() FROM {source_table_name} where key % 4 = 2;")
        row_count_source = int(r.output)

    with When("I replace a partition on the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} REPLACE {fetch_item} FROM {source_table_name}"
        )

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node, table_name=source_table_name, rows=insert_rows
            )

    with And("I check the size of the replaced part"):
        for node in nodes:
            r = node.query(
                f"SELECT count() FROM {destination_table_name} where key % 4 = 2;"
            )
            assert row_count_source == int(r.output)


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Drop("0.0"))
@Examples(
    "drop_item detach_first", product(["PARTITION 2", "PART '2_0_0_0'"], [False, True])
)
def drop(self, drop_item, detach_first):
    """Test detaching a part on one replica and reattaching it on another"""

    nodes = self.context.ch_nodes
    insert_rows = 1000000

    with Given("I have a replicated tables"):
        _, table_name = replicated_table_cluster(
            storage_policy="external_vfs", partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=nodes[1], table_name=table_name, rows=insert_rows)

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = nodes[1].query(f"SELECT count() FROM {table_name} where key % 4 = 2;")
        part_row_count = int(r.output)

    if detach_first:
        with When("I detach a partition from the first table"):
            nodes[1].query(f"ALTER TABLE {table_name} DETACH {drop_item}", exitcode=0)

        with And("I drop the detached partition"):
            nodes[1].query(
                f"ALTER TABLE {table_name} DROP DETACHED {drop_item} SETTINGS allow_drop_detached=1",
                exitcode=0,
            )

    else:
        with When("I drop the partition"):
            nodes[1].query(f"ALTER TABLE {table_name} DROP {drop_item}", exitcode=0)

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node,
                table_name=table_name,
                rows=(insert_rows - part_row_count),
            )


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Alter_Detach("0.0"))
@Examples("detach_item", [["PARTITION 2"], ["PART '2_0_0_0'"]])
def detach(self, detach_item):
    """Test detaching a part"""

    nodes = self.context.ch_nodes
    insert_rows = 1000000
    storage_policy = "external_vfs"

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy=storage_policy, partition_by="key % 4"
        )

    with And("I insert data into the first table"):
        insert_random(node=nodes[1], table_name=source_table_name, rows=insert_rows)

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = nodes[1].query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2;"
        )
        part_row_count = int(r.output)

    with When("I detach a partition from the first table"):
        nodes[1].query(
            f"ALTER TABLE {source_table_name} DETACH {detach_item}", exitcode=0
        )

    with Then("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=1)(
                node=node,
                table_name=source_table_name,
                rows=(insert_rows - part_row_count),
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
        with When("I add a constraint on the second node"):
            alter_table_add_constraint(
                node=nodes[1],
                table_name=table_name,
                constraint_name="non_negative_key",
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
