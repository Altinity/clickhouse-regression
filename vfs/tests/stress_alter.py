#!/usr/bin/env python3
import random
import json
from itertools import chain
from threading import RLock
import time

from testflows.core import *
from testflows.combinatorics import combinations

from helpers.alter import *
from vfs.tests.steps import *
from vfs.requirements import *
from vfs.tests.tc_netem import *

table_schema_lock = RLock()

step_retry_timeout = 300

@TestStep
def get_nodes_for_table(self, nodes, table_name):
    """Return all nodes that know about a given table."""
    active_nodes = []
    for node in nodes:
        r = nodes[0].query("SELECT table from system.replicas FORMAT JSONColumns")
        tables = json.loads(r.output)["table"]
        if table_name in tables:
            active_nodes.append(node)

    return active_nodes


@TestStep
def get_random_node_for_table(self, table_name):
    with table_schema_lock:
        return random.choice(
            get_nodes_for_table(nodes=self.context.ch_nodes, table_name=table_name)
        )


@TestStep
def get_random_table_name(self):
    return random.choice(self.context.table_names)


@TestStep
def optimize(self, node, table_name):
    """Apply OPTIMIZE on the given table and node"""
    with By(f"optimizing {table_name} on {node.name}"):
        node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)


@TestStep
def get_projections(self, node, table_name):
    r = node.query(
        f"SELECT distinct(name) FROM system.projection_parts WHERE table='{table_name}' FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_indexes(self, node, table_name):
    r = node.query(
        f"SELECT name FROM system.data_skipping_indices WHERE table='{table_name}' FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


@TestStep
@Name("optimize")
@Retry(timeout=10, delay=1)
def optimize_random(self, node=None, table_name=None, repeat_limit=3):
    """Apply OPTIMIZE on the given table and node, choosing at random if not specified."""
    if table_name is None:
        table_name = get_random_table_name()
    if node is None:
        node = get_random_node_for_table(table_name=table_name)

    for _ in range(random.randint(1, repeat_limit)):
        optimize(node=node, table_name=table_name)


@TestStep
@Retry(timeout=10, delay=1)
@Name("insert")
def insert_to_random(self):
    """Insert random data to a random table."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)

    columns = get_column_string(node=node, table_name=table_name)
    with By(f"inserting rows to {table_name} on {node.name}"):
        insert_random(
            node=node,
            table_name=table_name,
            columns=columns,
            no_checks=True,
            settings=f"insert_keeper_fault_injection_probability={self.context.fault_probability}",
        )


@TestStep
@Retry(timeout=10, delay=1)
def select_count_random(self, repeat_limit=10):
    """Perform select count() queries on a random node and table."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    for _ in range(random.randint(1, repeat_limit)):
        with By(f"count rows in {table_name} on {node.name}"):
            node.query(f"SELECT count() FROM {table_name}", no_checks=True)


@TestStep
def get_random_column_name(self, node, table_name):
    """Choose a column name at random."""
    columns_no_primary_key = get_column_names(node=node, table_name=table_name)[1:]
    return random.choice(columns_no_primary_key)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("add column")
def add_random_column(self):
    """Add a column with a random name."""
    with table_schema_lock:
        for table_name in self.context.table_names:
            node = get_random_node_for_table(table_name=table_name)
            By(
                name=f"add column to {table_name} with {node.name}",
                test=alter_table_add_column,
            )(
                table_name=table_name,
                column_name=f"c{random.randint(0, 99999)}",
                column_type="UInt16",
                node=node,
                exitcode=0,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("delete column")
def delete_random_column(self):
    """Delete a random column."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)

    with table_schema_lock:
        column_name = get_random_column_name(node=node, table_name=table_name)
        for table_name in self.context.table_names:
            node = get_random_node_for_table(table_name=table_name)
            By(
                name=f"delete column from {table_name} with {node.name}",
                test=alter_table_drop_column,
            )(node=node, table_name=table_name, column_name=column_name, exitcode=0)


@TestStep
@Retry(timeout=step_retry_timeout, delay=2)
@Name("rename column")
def rename_random_column(self):
    """Rename a random column to a random value."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    new_name = f"c{random.randint(0, 99999)}"

    with table_schema_lock:
        column_name = get_random_column_name(node=node, table_name=table_name)
        for table_name in self.context.table_names:
            node = get_random_node_for_table(table_name=table_name)
            By(
                name=f"rename column from {table_name} with {node.name}",
                test=alter_table_rename_column,
            )(
                node=node,
                table_name=table_name,
                column_name_old=column_name,
                column_name_new=new_name,
                exitcode=0,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("update column")
def update_random_column(self):
    """Replace some values on a random column."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    column_name = get_random_column_name(node=node, table_name=table_name)
    By(
        name=f"update column from {table_name} with {node.name}",
        test=alter_table_update_column,
    )(
        table_name=table_name,
        column_name=column_name,
        expression=f"({column_name} * 5)",
        condition=f"({column_name} < 10000)",
        node=node,
        exitcode=0,
    )


@TestStep
@Retry(timeout=step_retry_timeout, delay=2)
def get_random_part_id(self, node, table_name):
    """Choose a random active part in a table."""
    return random.choice(get_active_parts(node=node, table_name=table_name))


@TestStep
@Retry(timeout=step_retry_timeout, delay=2)
def get_random_partition_id(self, node, table_name):
    """Choose a random active partition in a table."""
    return random.choice(get_active_partition_ids(node=node, table_name=table_name))


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("detach part")
def detach_attach_random_partition(self):
    """Detach a random part, wait a random time, attach partition."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 5 + 1

    with When("I detach a part"):
        alter_table_detach_partition(
            node=node, table_name=table_name, partition_name=partition, exitcode=0
        )

    with Then(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I reattach the part"):
        alter_table_attach_partition(
            node=node, table_name=table_name, partition_name=partition, exitcode=0
        )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("freeze part")
def freeze_unfreeze_random_part(self):
    """Freeze a random part, wait a random time, unfreeze part."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    backup_name = f"backup_{getuid()}"
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 5 + 1

    with When("I freeze the part"):
        query = f"ALTER TABLE {table_name} FREEZE PARTITION {partition} WITH NAME '{backup_name}'"
        node.query(query, exitcode=0)

    with And(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I unfreeze the part"):
        query = f"ALTER TABLE {table_name} UNFREEZE PARTITION {partition} WITH NAME '{backup_name}'"
        node.query(query, exitcode=0)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("drop part")
def drop_random_part(self):
    """Detach and drop a random part."""

    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    part_id = get_random_part_id(node=node, table_name=table_name)
    detach_first = random.randint(0, 1)

    if detach_first:
        with When("I detach a partition from the first table"):
            node.query(f"ALTER TABLE {table_name} DETACH PART '{part_id}'", exitcode=0)

        with And("I drop the detached partition"):
            node.query(
                f"ALTER TABLE {table_name} DROP DETACHED PART '{part_id}' SETTINGS allow_drop_detached=1",
                exitcode=0,
            )
    else:
        with When("I drop the part"):
            node.query(f"ALTER TABLE {table_name} DROP PART '{part_id}'", exitcode=0)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("replace part")
def replace_random_part(self):
    """Test attaching a random part from one table to another."""

    destination_table_name = get_random_table_name()
    source_table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=destination_table_name)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with table_schema_lock:
        with When("I replace a partition on the second table"):
            alter_table_replace_partition(
                node=node,
                table_name=destination_table_name,
                partition_name=partition,
                path_to_backup=source_table_name,
                exitcode=0,
                no_checks=self.context.ignore_failed_part_moves,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("move partition to table")
def move_random_partition_to_random_table(self):
    """Move a random partition from one table to another."""

    destination_table_name = get_random_table_name()
    source_table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=destination_table_name)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with table_schema_lock:
        with When("I attach the partition to the second table"):
            alter_table_move_partition_to_table(
                node=node,
                table_name=source_table_name,
                partition_name=partition,
                path_to_backup=destination_table_name,
                exitcode=0,
                no_checks=self.context.ignore_failed_part_moves,
                timeout=30,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("move partition to disk")
def move_random_partition_to_random_disk(self):
    """Move a random partition from one table to another."""

    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    partition = get_random_partition_id(node=node, table_name=table_name)

    with Given("I check which disk the partition is on"):
        r = node.query(
            f"SELECT disk_name FROM system.parts WHERE table='{table_name}' and partition_id='{partition}' LIMIT 1",
            exitcode=0,
        )
        src_disk = r.output

    with Given("I check which disks are available and choose one"):
        r = node.query(
            f"select arrayJoin(disks) from system.storage_policies where policy_name='{self.context.storage_policy}' FORMAT JSONColumns",
            exitcode=0,
        )
        disks = json.loads(r.output)["arrayJoin(disks)"]
        disks.remove(src_disk)
        dest_disk = random.choice(disks)

    with When(f"I move the partition from {src_disk} to {dest_disk}"):
        alter_table_move_partition(
            node=node,
            table_name=table_name,
            partition_name=partition,
            disk_name=dest_disk,
            disk="DISK",
            exitcode=0,
            no_checks=self.context.ignore_failed_part_moves,
            timeout=30,
        )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("attach part")
def attach_random_part_from_table(self):
    """Attach a random partition from one table to another."""

    destination_table_name = get_random_table_name()
    source_table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=destination_table_name)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with table_schema_lock:
        with When("I attach the partition to the second table"):
            alter_table_attach_partition_from(
                node=node,
                table_name=destination_table_name,
                partition_name=partition,
                path_to_backup=source_table_name,
                exitcode=0,
                no_checks=self.context.ignore_failed_part_moves,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("fetch part")
def fetch_random_part_from_table(self):
    """Fetching a random part from another table replica."""

    destination_table_name = get_random_table_name()
    source_table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=destination_table_name)
    part_id = get_random_part_id(node=node, table_name=source_table_name)

    with table_schema_lock:
        with When("I fetch a part from the first table"):
            node.query(
                f"ALTER TABLE {destination_table_name} FETCH PART '{part_id}' FROM '/clickhouse/tables/{source_table_name}'",
                exitcode=0,
            )

        with And("I attach the part to the second table"):
            node.query(
                f"ALTER TABLE {destination_table_name} ATTACH PART '{part_id}'",
                exitcode=0,
            )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("clear column")
def clear_random_column(self):
    """Clear a random column on a random partition."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    column_name = get_random_column_name(node=node, table_name=table_name)
    By(
        name=f"clear column from {table_name} with {node.name}",
        test=alter_table_clear_column_in_partition,
    )(
        node=node,
        table_name=table_name,
        column_name=column_name,
        partition_name=str(random.randint(0, 3)),
        no_checks=True,
    )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("delete row")
def delete_random_rows(self):
    """Delete a few rows at random."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    column_name = get_random_column_name(node=node, table_name=table_name)
    divisor = random.choice([5, 11, 17, 23])
    remainder = random.randint(0, divisor - 1)

    By(
        name=f"delete rows from {table_name} with {node.name}",
        test=alter_table_delete_rows,
    )(
        table_name=table_name,
        condition=f"({column_name} % {divisor} = {remainder})",
        node=node,
        no_checks=True,
    )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("light delete row")
def delete_random_rows_lightweight(self):
    """Lightweight delete a few rows at random."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    column_name = get_random_column_name(node=node, table_name=table_name)
    divisor = random.choice([5, 11, 17, 23])
    remainder = random.randint(0, divisor - 1)

    with By(f"delete rows from {table_name} with {node.name}"):
        node.query(
            f"DELETE FROM {table_name} WHERE ({column_name} % {divisor} = {remainder})",
            no_checks=True,
        )

    if random.randint(0, 1):
        node.query(
            f"ALTER TABLE {table_name} APPLY DELETED MASK",
            no_checks=True,
        )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("add projection")
def add_random_projection(self):
    projection_name = "projection_" + getuid()

    with table_schema_lock:
        table_name = get_random_table_name()
        node = get_random_node_for_table(table_name=table_name)
        column_name = get_random_column_name(node=node, table_name=table_name)

        node.query(
            f"ALTER TABLE {table_name} ADD PROJECTION {projection_name} (SELECT {column_name}, key ORDER BY {column_name})",
            exitcode=0,
        )

    node.query(
        f"ALTER TABLE {table_name} MATERIALIZE PROJECTION {projection_name}", exitcode=0
    )


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("clear projection")
def clear_random_projection(self):
    tables = self.context.table_names.copy()
    random.shuffle(tables)
    with table_schema_lock:
        for table_name in tables:
            node = get_random_node_for_table(table_name=table_name)
            projections = get_projections(node=node, table_name=table_name)
            if len(projections) == 0:
                continue

            projection_name = random.choice(projections)
            partition_name = get_random_partition_id(node=node, table_name=table_name)

            node.query(
                f"ALTER TABLE {table_name} CLEAR PROJECTION {projection_name} IN PARTITION {partition_name}",
                exitcode=0,
            )
            return


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("drop projection")
def drop_random_projection(self):
    tables = self.context.table_names.copy()
    random.shuffle(tables)
    with table_schema_lock:
        for table_name in tables:
            node = get_random_node_for_table(table_name=table_name)
            projections = get_projections(node=node, table_name=table_name)
            if len(projections) == 0:
                continue

            projection_name = random.choice(projections)

            node.query(
                f"ALTER TABLE {table_name} DROP PROJECTION {projection_name}",
                exitcode=0,
            )
            return


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("add index")
def add_random_index(self):
    index_name = "index_" + getuid()

    with table_schema_lock:
        table_name = get_random_table_name()
        node = get_random_node_for_table(table_name=table_name)
        column_name = get_random_column_name(node=node, table_name=table_name)

        node.query(
            f"ALTER TABLE {table_name} ADD index {index_name} {column_name} TYPE bloom_filter",
            exitcode=0,
        )

    node.query(f"ALTER TABLE {table_name} MATERIALIZE index {index_name}", exitcode=0)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("clear index")
def clear_random_index(self):
    tables = self.context.table_names.copy()
    random.shuffle(tables)

    for table_name in tables:
        node = get_random_node_for_table(table_name=table_name)
        indexes = get_indexes(node=node, table_name=table_name)
        if len(indexes) == 0:
            continue

        index_name = random.choice(indexes)
        partition_name = get_random_partition_id(node=node, table_name=table_name)

        node.query(
            f"ALTER TABLE {table_name} CLEAR index {index_name} IN PARTITION {partition_name}",
            exitcode=0,
        )
        return


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("drop index")
def drop_random_index(self):
    tables = self.context.table_names.copy()
    random.shuffle(tables)

    for table_name in tables:
        node = get_random_node_for_table(table_name=table_name)
        indexs = get_indexes(node=node, table_name=table_name)
        if len(indexs) == 0:
            continue

        index_name = random.choice(indexs)

        node.query(
            f"ALTER TABLE {table_name} DROP index {index_name}",
            exitcode=0,
        )
        return


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("modify ttl")
def modify_random_ttl(self):
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)

    ttl_expression = f"key + INTERVAL {random.randint(1, 10)} YEAR"
    if random.randint(0, 1):
        ttl_expression += " to volume 'external'"

    node.query(f"ALTER TABLE {table_name} MODIFY TTL {ttl_expression}", exitcode=0)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
@Name("remove ttl")
def remove_random_ttl(self):
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)

    node.query(f"ALTER TABLE {table_name} REMOVE TTL", no_checks=True)


@TestStep(Then)
@Retry(timeout=step_retry_timeout, delay=5)
def check_consistency(self, tables=None, sync_timeout=None):
    """
    Check that the given tables hold the same amount of data on all nodes where they exist.
    Also check that column names match, subsequent part move tests require matching columns.
    """
    if sync_timeout is None:
        sync_timeout = getattr(self.context, "sync_replica_timeout", 60)

    nodes = self.context.ch_nodes
    if tables is None:
        tables = self.context.table_names
    for table_name in tables:
        with When("I check which nodes have the table"):
            active_nodes = [
                n
                for n in nodes
                if table_name in n.query("SHOW TABLES", no_checks=True).output
            ]
            assert len(active_nodes) > 0, "At least one node should have this table"

        row_counts = {}
        column_names = {}
        with When(f"I sync and count rows on nodes for table {table_name}"):
            for node in active_nodes:
                By(f"running SYNC REPLICA", test=sync_replica, parallel=True)(
                    node=node,
                    table_name=table_name,
                    raise_on_timeout=False,
                    timeout=sync_timeout,
                    no_checks=True,
                )
                join()

            for node in active_nodes:
                with By(f"querying the row count"):
                    row_counts[node.name] = get_row_count(
                        node=node, table_name=table_name
                    )
                    column_names[node.name] = get_column_names(
                        node=node, table_name=table_name
                    )

        with Then("All replicas should have the same state"):
            for n1, n2 in combinations(active_nodes, 2):
                with By(f"Checking {n1.name} and {n2.name}"):
                    assert row_counts[n1.name] == row_counts[n2.name], error()
                    assert column_names[n1.name] == column_names[n2.name], error()


@TestStep
def add_replica(self):
    """
    Add a replica that has been deleted, chosen at random.
    Does not handle the case where all replicas of a table have been deleted.
    """

    nodes = self.context.ch_nodes.copy()
    random.shuffle(nodes)
    tables = self.context.table_names.copy()
    random.shuffle(tables)

    tables_by_node = {}

    with table_schema_lock:
        for node in nodes:
            with When(f"I check which tables are known by {node.name}"):
                r = node.query("SELECT table from system.replicas FORMAT JSONColumns")
                tables_by_node[node.name] = json.loads(r.output)["table"]

        with And("I check that there exists a node that does not replicate all tables"):
            table_counts = [len(tables) for tables in tables_by_node.values()]
            if min(table_counts) == self.context.maximum_replicas:
                return

        with Given(
            "I choose one node to add the new replicated table to, and save the other nodes to query structure from"
        ):
            adding_node = None
            reference_nodes = []
            for node, count in zip(nodes, table_counts):
                if count < self.context.maximum_replicas and adding_node is None:
                    adding_node = node
                else:
                    reference_nodes.append(node)

        assert (
            adding_node is not None
        ), "Early return logic should prevent failing to find a node that can have a replica added"

        for table in tables:
            if table not in tables_by_node[adding_node.name]:
                columns = None
                for ref_node in reference_nodes:
                    with When(f"I check if {ref_node.name} knows about {table}"):
                        if table in tables_by_node[ref_node.name]:
                            with When(
                                f"I query {ref_node.name} for the columns in {table}"
                            ):
                                columns = get_column_string(
                                    node=ref_node, table_name=table
                                )
                                break

                    assert (
                        columns is not None
                    ), "There should always be at least one node that knows about a table"

                with And(f"I create a new replica on {adding_node.name}"):
                    create_one_replica(
                        node=adding_node,
                        table_name=table,
                        columns=columns,
                        order_by="key",
                        partition_by="key % 4",
                        storage_policy=self.context.storage_policy,
                    )
                    return


@TestStep
def delete_replica(self):
    """
    Delete a random table replica, being careful to not delete the last replica.
    """
    node = random.choice(self.context.ch_nodes)
    tables = self.context.table_names.copy()
    random.shuffle(tables)

    with table_schema_lock:

        with Given("I check the replica counts for all tables"):
            r = node.query(
                "SELECT table, active_replicas from system.replicas FORMAT JSONColumns"
            )
            out = json.loads(r.output)
            current_tables = out["table"]
            active_replicas = {
                t: r for t, r in zip(current_tables, out["active_replicas"])
            }

        with When("I look for a table that has more than the minimum replicas"):
            for table in tables:
                if (
                    table in current_tables
                    and active_replicas[table] > self.context.minimum_replicas
                ):
                    with And(
                        f"I delete the replica for table {table} on node {node.name}"
                    ):
                        delete_one_replica(node=node, table_name=table)
                        return


@TestStep
def restart_keeper(self):
    """
    Stop a random zookeeper instance, wait, and restart.
    This simulates a short outage.
    """
    keeper_node = random.choice(self.context.zk_nodes)
    delay = random.random() * 10 + 1

    with interrupt_node(keeper_node):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


@TestStep
def restart_clickhouse(self, signal="SEGV"):
    """
    Send a kill signal to a random clickhouse instance, wait, and restart.
    This simulates a short outage.
    """
    clickhouse_node = random.choice(self.context.ch_nodes)
    delay = random.random() * 10 + 1

    with interrupt_clickhouse(clickhouse_node, safe=False, signal=signal):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


@TestStep
@Retry(timeout=step_retry_timeout, delay=5)
def restart_network(self):
    """
    Stop the network on a random instance, wait, and restart.
    This simulates a short outage.
    """
    node = random.choice(self.context.zk_nodes + self.context.ch_nodes)
    delay = random.random() * 5 + 1

    with interrupt_network(self.context.cluster, node):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


network_impairments = [
    network_packet_delay,
    network_packet_loss,
    network_packet_loss_gemodel,
    network_packet_corruption,
    network_packet_duplication,
    network_packet_reordering,
    network_packet_rate_limit,
]


@TestStep(Given)
def impaired_network(self, network_mode):
    """Apply a network impairment mode to all nodes"""
    nodes = chain(self.context.zk_nodes, self.context.ch_nodes)

    for node in nodes:
        network_mode(node=node)


@TestStep
def fill_clickhouse_disks(self):
    node = random.choice(self.context.ch_nodes)
    clickhouse_disk_mounts = ["/var/log/clickhouse-server", "/var/lib/clickhouse"]
    delay = random.random() * 5 + 1
    file_name = "file.dat"

    try:
        for disk_mount in clickhouse_disk_mounts:
            with When(f"I get the size of {disk_mount} on {node.name}"):
                r = node.command(f"df -k --output=size {disk_mount}")
                disk_size_k = r.output.splitlines()[1].strip()

            with And(f"I create a file to fill {disk_mount} on {node.name}"):
                node.command(
                    f"dd if=/dev/zero of={disk_mount}/{file_name} bs=1K count={disk_size_k}",
                    no_checks=True,
                )

        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)

    finally:
        with Finally(f"I delete the large file on {node.name}"):
            for disk_mount in clickhouse_disk_mounts:
                node.command(f"rm {disk_mount}/{file_name}")

        with And(f"I restart {node.name} in case it crashed"):
            node.restart_clickhouse(safe=False)


@TestStep
def fill_zookeeper_disks(self):
    node = random.choice(self.context.zk_nodes)
    zookeeper_disk_mounts = ["/data", "/datalog"]
    delay = random.random() * 5 + 1
    file_name = "file.dat"

    try:
        for disk_mount in zookeeper_disk_mounts:
            with When(f"I get the size of {disk_mount} on {node.name}"):
                r = node.command(f"df -k --output=size {disk_mount}")
                disk_size_k = r.output.splitlines()[1].strip()

            with And(f"I create a file to fill {disk_mount} on {node.name}"):

                node.command(
                    f"dd if=/dev/zero of={disk_mount}/{file_name} bs=1K count={disk_size_k}",
                    no_checks=True,
                )

        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)

    finally:
        with Finally(f"I delete the large file on {node.name}"):
            for disk_mount in zookeeper_disk_mounts:
                node.command(f"rm {disk_mount}/{file_name}")

        with And(f"I restart {node.name} in case it crashed"):
            node.restart_clickhouse(safe=False)


@TestOutline
def alter_combinations(
    self,
    limit=10,
    shuffle=True,
    combination_size=3,
    run_groups_in_parallel=True,
    run_optimize_in_parallel=True,
    ignore_failed_part_moves=False,
    sync_replica_timeout=600,
    storage_policy="tiered",
    minimum_replicas=1,
    maximum_replicas=3,
    n_tables=3,
    restarts=False,
    add_remove_replicas=False,
    fill_disks=False,
    insert_keeper_fault_injection_probability=0,
    network_impairment=False,
):
    """
    Perform combinations of alter actions, checking that all replicas agree.
    """

    self.context.ignore_failed_part_moves = ignore_failed_part_moves
    self.context.sync_replica_timeout = sync_replica_timeout
    self.context.storage_policy = storage_policy
    self.context.minimum_replicas = minimum_replicas
    self.context.maximum_replicas = maximum_replicas
    self.context.fault_probability = insert_keeper_fault_injection_probability

    with Given("I have a list of actions I can perform"):
        actions = [
            add_random_column,
            rename_random_column,
            clear_random_column,
            delete_random_column,
            update_random_column,
            delete_random_rows,
            delete_random_rows_lightweight,
            detach_attach_random_partition,
            freeze_unfreeze_random_part,
            drop_random_part,
            replace_random_part,
            add_random_projection,
            clear_random_projection,
            drop_random_projection,
            add_random_index,
            clear_random_index,
            drop_random_index,
            modify_random_ttl,
            remove_random_ttl,
            move_random_partition_to_random_disk,
            move_random_partition_to_random_table,
            attach_random_part_from_table,
            fetch_random_part_from_table,
        ]
        if restarts:
            actions += [restart_keeper, restart_clickhouse]

        if not network_impairment:
            actions.append(restart_network)

        if add_remove_replicas:
            actions += [delete_replica, add_replica]

        if fill_disks:
            actions += [fill_clickhouse_disks, fill_zookeeper_disks]

    with And(f"I make a list of groups of {combination_size} actions"):
        action_groups = list(
            combinations(actions, combination_size, with_replacement=True)
        )
        note(f"Created {len(action_groups)} groups of actions to run")

    if shuffle:
        with And("I shuffle the list"):
            random.shuffle(action_groups)

    if limit:
        with And(f"I choose {limit} groups of actions"):
            action_groups = action_groups[:limit]

    try:
        with Given(f"I create {n_tables} tables with 10 columns and data"):
            self.context.table_names = []
            columns = "key DateTime," + ",".join(f"value{i} UInt16" for i in range(10))
            for i in range(n_tables):
                table_name = f"table{i}_{self.context.storage_policy}"
                replicated_table_cluster(
                    table_name=table_name,
                    storage_policy=self.context.storage_policy,
                    partition_by="toQuarter(key) - 1",
                    columns=columns,
                    ttl=f"key + INTERVAL {random.randint(1, 10)} YEAR",
                    no_cleanup=True,
                )
                self.context.table_names.append(table_name)
                insert_random(
                    node=self.context.node, table_name=table_name, columns=columns
                )

        with And("I create 5 random projections and indexes"):
            for _ in range(5):
                add_random_projection()
                add_random_index()

        # To test a single combination, uncomment and edit as needed.
        # action_groups = [
        #     [
        #         delete_replica,
        #         add_replica,
        #     ]
        # ]

        t = time.time()
        total_combinations = len(action_groups)
        for i, chosen_actions in enumerate(action_groups):
            title = f"{i+1}/{total_combinations} " + ",".join(
                [f"{f.name}" for f in chosen_actions]
            )

            if network_impairment:
                net_mode = random.choice(network_impairments)
                title += "," + net_mode.name

            with Check(title):
                if network_impairment:
                    with Given("a network impairment"):
                        impaired_network(network_mode=net_mode)

                with When("I perform a group of actions"):
                    for action in chain(
                        [insert_to_random, select_count_random], chosen_actions
                    ):
                        By(
                            f"I {action.name}",
                            run=action,
                            parallel=run_groups_in_parallel,
                            flags=TE | ERROR_NOT_COUNTED,
                        )

                    for table in self.context.table_names:
                        By(
                            f"I OPTIMIZE {table}",
                            test=optimize_random,
                            parallel=run_optimize_in_parallel,
                            flags=TE,
                        )(table_name=table_name)

                    join()

                with Then("I check that the replicas are consistent", flags=TE):
                    check_consistency()

            note(f"Average time per test combination {(time.time()-t)/(i+1):.1f}s")

    finally:
        with Finally(
            "I drop each table on each node in case the cluster is in a bad state"
        ):
            for node in self.context.ch_nodes:
                for table_name in self.context.table_names:
                    When(test=delete_one_replica, parallel=True)(
                        node=node, table_name=table_name
                    )
            join()


@TestScenario
def safe(self):
    """
    Perform only actions that are relatively unlikely to cause crashes.
    """

    alter_combinations(
        limit=None if self.context.stress else 20,
        shuffle=True,
        restarts=False,
    )


@TestScenario
def insert_faults(self):
    """
    Perform actions with keeper fault injection on inserts.
    """

    alter_combinations(
        limit=None if self.context.stress else 20,
        shuffle=True,
        insert_keeper_fault_injection_probability=0.1,
    )


@TestScenario
def network_faults(self):
    """
    Perform actions with random network interference.
    """

    alter_combinations(
        limit=None if self.context.stress else 20,
        shuffle=True,
        network_impairment=True,
        restarts=False,
    )


@TestScenario
def restarts(self):
    """
    Allow restarting nodes randomly. High probability of crashes.
    """

    alter_combinations(
        limit=None if self.context.stress else 20,
        shuffle=True,
        restarts=True,
    )


@TestScenario
def add_remove_replicas(self):
    """
    Allow adding and removing replicas randomly.
    """

    alter_combinations(
        limit=None if self.context.stress else 20,
        shuffle=True,
        add_remove_replicas=True,
    )


@TestScenario
def full_disk(self):
    """
    Allow filling clickhouse and zookeeper disks.
    """
    cluster = self.context.cluster

    try:
        with Given("disk space is restricted"):
            cluster.command(
                None,
                f"sudo {current_dir()}/../vfs_env/create_fixed_volumes.sh",
                no_checks=True,
                timeout=5,
            )
            r = cluster.command(
                None, "df | grep -c clickhouse-regression", no_checks=True
            )
            restrictions_enabled = int(r.output) == 3 * 2 * 2

        if not restrictions_enabled:
            skip("run sudo vfs_env/create_fixed_volumes.sh before this scenario")

        alter_combinations(
            limit=None if self.context.stress else 2,
            shuffle=True,
            fill_disks=True,
        )
    finally:
        with Finally("disk space is de-restricted"):
            cluster.command(
                None,
                f"sudo {current_dir()}/../vfs_env/destroy_fixed_volumes.sh",
                no_checks=True,
                timeout=5,
            )


@TestFeature
def vfs(self):
    """Run test scenarios with vfs."""

    with Given("VFS is enabled"):
        enable_vfs(disk_names=["external", "external_tiered"])

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, tags=["long", "combinatoric"])


@TestFeature
def no_vfs(self):
    """Run test scenarios without vfs."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, tags=["long", "combinatoric"])


@TestFeature
@Name("stress alter")
def feature(self):
    """Stress test with many alters."""

    with Given("I have S3 disks configured"):
        s3_config()

    for sub_feature in loads(current_module(), Feature):
        if sub_feature is feature:
            continue
        Feature(run=sub_feature)
