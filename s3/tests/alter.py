#!/usr/bin/env python3
import random

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.alter import *
from helpers.queries import optimize
from helpers.common import getuid, check_clickhouse_version
from s3.tests.common import (
    default_s3_disk_and_volume,
    assert_row_count,
    insert_random,
    temporary_bucket_path,
    s3_storage,
    replicated_table_cluster,
)
from s3.requirements import RQ_SRS_015_S3_Alter

COLUMNS = "key UInt32, value1 String, value2 UInt8"

retry_args = {
    "timeout": 90,
    "delay": 5,
}

INSERT_SIZE = 100_000

@TestStep(When)
def detach_from_table(self, table_name: str, item: str, node=None, exitcode=0):
    """Detach an item from a table."""
    if node is None:
        node = current().context.node

    node.query(f"ALTER TABLE {table_name} DETACH {item}", exitcode=exitcode)


@TestScenario
def update_delete(self):
    """Test that ALTER UPDATE and DELETE execute without errors."""
    table_name = "update_table"
    nodes = self.context.ch_nodes
    columns = "key UInt64, d Int64, e Int64"

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=self.context.policy, columns=columns
        )

    with And("I insert some data"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=columns, rows=INSERT_SIZE
        )

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
        optimize(node=nodes[0], table_name=table_name, final=True, no_checks=False)

    with And("I DELETE with success"):
        alter_table_delete_rows(
            table_name=table_name, condition="(d < e)", node=nodes[0], exitcode=0
        )


@TestScenario
def order_by(self):
    """Test that MODIFY ORDER BY executes without errors."""
    table_name = "order_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=self.context.policy, columns=COLUMNS
        )

    with And("I insert some data"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

    with Then("I modify ORDER BY with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} ON CLUSTER 'replicated_cluster' ADD COLUMN valueZ Int16, MODIFY ORDER BY (key, valueZ)",
            exitcode=0,
        )

    with And("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestScenario
def sample_by(self):
    """Test that MODIFY SAMPLE BY executes without errors."""
    table_name = "sample_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy=self.context.policy,
            primary_key="(key, cityHash64(value1))",
            order_by="(key, cityHash64(value1))",
            columns=COLUMNS,
        )

    with And("I insert some data"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

    with Then("I modify SAMPLE BY with success"):
        nodes[0].query(
            f"ALTER TABLE {table_name} MODIFY SAMPLE BY cityHash64(value1)",
            exitcode=0,
        )

    with And("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestScenario
def index(self):
    """Test that MODIFY ORDER BY executes without errors."""
    table_name = "index_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=self.context.policy, columns=COLUMNS
        )

    with And("I insert some data"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

    with Check("add"):
        with When("I add an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} ADD INDEX idx_test value1 TYPE set(100) GRANULARITY 2",
                exitcode=0,
            )

    with Check("materialize"):
        with When("I materialize an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} MATERIALIZE INDEX idx_test",
                exitcode=0,
            )

    with Check("clear"):
        with When("I clear an index"):
            retry(nodes[0].query, **retry_args)(
                f"ALTER TABLE {table_name} CLEAR INDEX idx_test",
                exitcode=0,
            )

    with Check("drop"):
        with When("I drop an index"):
            nodes[0].query(
                f"ALTER TABLE {table_name} DROP INDEX idx_test",
                exitcode=0,
            )

    with Then("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestScenario
def projection(self):
    """Test that adding projections does not error."""
    table_name = "proj_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=self.context.policy, columns=COLUMNS
        )

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
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

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

    with And("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestOutline(Scenario)
@Examples("partition", [[""], ["PARTITION 1"]])
def freeze(self, partition):
    """Check tables work with ALTER TABLE FREEZE."""

    nodes = self.context.ch_nodes
    table_name = f"table_{getuid()}"
    backup_name = f"backup_{getuid()}"

    with Given(f"I have a table {table_name}"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy=self.context.policy,
            partition_by="key % 4",
            settings=(
                "disable_freeze_partition_for_zero_copy_replication=0"
                if self.context.allow_zero_copy
                else None
            ),
            columns=COLUMNS,
        )

    with When("I insert some data into the table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

    with Then("I freeze the table"):
        nodes[0].query(
            f"ALTER TABLE {table_name} FREEZE {partition} WITH NAME '{backup_name}'",
            exitcode=0,
        )

    with And("I unfreeze the table"):
        nodes[0].query(
            f"ALTER TABLE {table_name} UNFREEZE {partition} WITH NAME '{backup_name}'",
            exitcode=0,
        )

    with And("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestOutline(Scenario)
@Examples("fetch_item", [["PARTITION 2"], ["PART '2_0_0_0'"]])
def fetch(self, fetch_item):
    """Test fetching a new part from another replica."""

    nodes = self.context.ch_nodes
    node = nodes[0]

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )

    with And("I insert data into the first table"):
        insert_random(
            node=node, table_name=source_table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = node.query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        row_count = int(r.output)

    with When("I fetch a partition from the first table"):
        node.query(
            f"ALTER TABLE {destination_table_name} FETCH {fetch_item} FROM '/clickhouse/tables/{source_table_name}'"
        )

    with And("I attach the partition to the second table"):
        node.query(f"ALTER TABLE {destination_table_name} ATTACH {fetch_item}")

    with Then("I check the number of rows on the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=destination_table_name, rows=row_count
            )


@TestScenario
def attach_from(self):
    """Test attaching a part from one table to another."""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = INSERT_SIZE

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )

    with And("I insert data into the first table"):
        insert_random(
            node=node, table_name=source_table_name, columns=COLUMNS, rows=insert_rows
        )

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = node.query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        row_count = int(r.output)

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} ATTACH {fetch_item} FROM {source_table_name}"
        )

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=source_table_name, rows=insert_rows
            )

    with And("I check the number of rows on the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=destination_table_name, rows=row_count
            )


@TestScenario
def move_to_table(self):
    """Test moving a part from one table to another."""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = 1000000
    source_table_name = "table_move_src"
    destination_table_name = "table_move_dest"

    with Given("I have two replicated tables"):
        replicated_table_cluster(
            table_name=source_table_name,
            storage_policy=self.context.policy,
            partition_by="key % 4",
            columns=COLUMNS,
        )
        replicated_table_cluster(
            table_name=destination_table_name,
            storage_policy=self.context.policy,
            partition_by="key % 4",
            columns=COLUMNS,
        )

    with And("I insert data into the first table"):
        insert_random(
            node=node, table_name=source_table_name, columns=COLUMNS, rows=insert_rows
        )

    with And("I insert less data into the second table"):
        insert_random(
            node=node,
            table_name=destination_table_name,
            columns=COLUMNS,
            rows=insert_rows // 2,
        )

    with And("I count the rows in a partition on the first table"):
        r = node.query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        row_count = int(r.output)

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {source_table_name} MOVE {fetch_item} TO TABLE {destination_table_name}"
        )

    with Then("I check the number of rows in the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=source_table_name, rows=(insert_rows - row_count)
            )

    with And("I check the number of rows in the second table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node,
                table_name=destination_table_name,
                rows=(insert_rows // 2 + row_count),
            )


@TestScenario
def replace(self):
    """Test attaching a part from one table to another."""

    nodes = self.context.ch_nodes
    node = nodes[0]
    fetch_item = "PARTITION 2"
    insert_rows = INSERT_SIZE

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )
        _, destination_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )

    with And("I insert data into the first table"):
        insert_random(
            node=node, table_name=source_table_name, columns=COLUMNS, rows=insert_rows
        )

    with And("I insert a smaller amount of data into the second table"):
        insert_random(
            node=node,
            table_name=destination_table_name,
            columns=COLUMNS,
            rows=insert_rows // 2,
        )

    with And("I count the rows in a partition on the first table"):
        r = node.query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        row_count_source = int(r.output)

    with When("I replace a partition on the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} REPLACE {fetch_item} FROM {source_table_name}"
        )

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=source_table_name, rows=insert_rows
            )

    with And("I check the size of the replaced part"):
        for attempt in retries(timeout=120, delay=5):
            with attempt:
                for node in nodes:
                    r = node.query(
                        f"SELECT count() FROM {destination_table_name} where key % 4 = 2 FORMAT TabSeparated;"
                    )
                    table_row_count = int(r.output)
                    assert row_count_source == table_row_count, error()


@TestOutline(Scenario)
@Examples(
    "drop_item detach_first", product(["PARTITION 2", "PART '2_0_0_0'"], [False, True])
)
def drop(self, drop_item, detach_first):
    """Test detaching a part and dropping it."""

    nodes = self.context.ch_nodes
    insert_rows = 1000000

    with Given("I have a replicated tables"):
        _, table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )

    with And("I insert data into the first table"):
        insert_random(
            node=nodes[1], table_name=table_name, columns=COLUMNS, rows=insert_rows
        )

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = nodes[1].query(
            f"SELECT count() FROM {table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        part_row_count = int(r.output)

    if detach_first:
        with When("I detach a partition from the first table"):
            retry(detach_from_table, timeout=30, delay=3)(
                table_name=table_name, item=drop_item, node=nodes[1]
            )

        with And("I drop the detached partition"):
            nodes[1].query(
                f"ALTER TABLE {table_name} DROP DETACHED {drop_item} SETTINGS allow_drop_detached=1",
                exitcode=0,
            )

    else:
        with When("I drop the partition"):
            for attempt in retries(timeout=30, delay=3):
                with attempt:
                    nodes[1].query(
                        f"ALTER TABLE {table_name} DROP {drop_item}", exitcode=0
                    )

    with Then("I check the number of rows on the first table on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node,
                table_name=table_name,
                rows=(insert_rows - part_row_count),
            )


@TestOutline(Example)
def check_move(self, move_item, policy, disk_order, to_type):
    source_disk, destination_disk = disk_order

    nodes = self.context.ch_nodes
    insert_rows = 1000000

    with Given("I have a replicated table"):
        _, table_name = replicated_table_cluster(
            storage_policy=policy, partition_by="key % 4", columns=COLUMNS
        )

    with When("I insert data into the first table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=insert_rows
        )

    with Then("I check system.parts"):
        what, part_name = move_item.split()
        if what == "PART":
            what = "part_name"
        part_name = part_name.strip("'")
        query = f"SELECT disk_name FROM system.parts WHERE {what.lower()}='{part_name}' FORMAT TabSeparated"
        r = nodes[0].query(query, exitcode=0)
        assert r.output == source_disk, error()

    with When(f"I move {move_item} from {source_disk} to {destination_disk}"):
        query = f"ALTER TABLE {table_name} MOVE {move_item} TO "
        if to_type == "DISK":
            query += f"DISK '{destination_disk}'"
        elif to_type == "VOLUME":
            query += "VOLUME 'destination'"
        nodes[0].query(query, exitcode=0)

    with Then("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, timeout=15, delay=2)(
                node=node,
                table_name=table_name,
                rows=insert_rows,
            )

    with And("I check system.parts again"):
        query = f"SELECT disk_name FROM system.parts WHERE {what.lower()}='{part_name}' FORMAT TabSeparated"
        r = nodes[0].query(query, exitcode=0)
        assert r.output == destination_disk, error()


@TestOutline(Scenario)
@Examples("detach_item", [["PARTITION 2"], ["PART '2_0_0_0'"]])
def detach(self, detach_item):
    """Test detaching a part."""

    nodes = self.context.ch_nodes
    insert_rows = 1000000

    with Given("I have two replicated tables"):
        _, source_table_name = replicated_table_cluster(
            storage_policy=self.context.policy, partition_by="key % 4", columns=COLUMNS
        )

    with And("I insert data into the first table"):
        insert_random(
            node=nodes[1],
            table_name=source_table_name,
            columns=COLUMNS,
            rows=insert_rows,
        )

    with And("I count the rows in a partition"):
        # Can also get this information from system.parts
        r = nodes[1].query(
            f"SELECT count() FROM {source_table_name} where key % 4 = 2 FORMAT TabSeparated;"
        )
        part_row_count = int(r.output)

    with When("I detach a partition from the first table"):
        retry(detach_from_table, timeout=30, delay=3)(
            table_name=source_table_name, item=detach_item, node=nodes[1]
        )

    with Then("I check the number of rows on all nodes"):
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node,
                table_name=source_table_name,
                rows=(insert_rows - part_row_count),
            )


@TestScenario
def columns(self):
    """Test that alter column commands execute without errors."""
    table_name = "columns_table"
    nodes = self.context.ch_nodes

    with Given("I have a table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=self.context.policy, columns=COLUMNS
        )

    with And("I insert some data"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=COLUMNS, rows=INSERT_SIZE
        )

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
        for node in nodes:
            retry(assert_row_count, **retry_args)(
                node=node, table_name=table_name, rows=INSERT_SIZE
            )


@TestFeature
@Requirements(RQ_SRS_015_S3_Alter("1.0"))
@Name("alter")
def feature(self, uri, bucket_prefix):
    """Test ALTER commands with s3 disks"""

    cluster = self.context.cluster
    self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]

    if self.context.storage != "azure":
        with Given("a temporary s3 path"):
            temp_s3_path = temporary_bucket_path(
                bucket_prefix=f"{bucket_prefix}/backup_bucket"
            )
            self.context.uri = f"{uri}{temp_s3_path}/backup_bucket/"
    else:
        self.context.uri = uri

    with Given("I have base S3 disks configured"):
        default_s3_disk_and_volume(restart=True)

    if check_clickhouse_version(">=22.8")(self):
        with And("I define extra disks and policies"):
            extra_disks = {
                "encrypted": {
                    "type": "encrypted",
                    "disk": "s3_cache",
                    "key": "uCApvDl3Ro0D0CcS",
                }
            }
            extra_policies = {
                "encrypted": {"volumes": {"external": {"disk": "encrypted"}}}
            }
            s3_storage(
                disks=extra_disks,
                policies=extra_policies,
                restart=True,
                # Make sure config is loaded after the main disk config
                config_file="z_encrypted_disk.xml",
            )

    examples = {
        # Policy, allow zero copy
        "normal": ["external", None],
        "encrypted": ["encrypted", None],
        "zero copy": ["external", True],
        "zero copy encrypted": ["encrypted", True],
    }

    for example_name, (policy, allow_zero_copy) in examples.items():
        if policy == "encrypted" and check_clickhouse_version("<22.8")(self):
            continue

        with Example(example_name):
            self.context.policy = policy
            self.context.allow_zero_copy = allow_zero_copy

            for scenario in loads(current_module(), Scenario):
                scenario()
