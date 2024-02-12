#!/usr/bin/env python3
import random
import json
from itertools import chain
from threading import Lock

from testflows.core import *
from testflows.combinatorics import combinations
from testflows.uexpect.uexpect import ExpectTimeoutError

from helpers.alter import *
from vfs.tests.steps import *
from vfs.requirements import *

delete_replica_lock = Lock()
table_schema_lock = Lock()


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
        insert_random(node=node, table_name=table_name, columns=columns, no_checks=True)


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
@Retry(timeout=10, delay=1)
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
@Retry(timeout=10, delay=1)
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
@Retry(timeout=10, delay=1)
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
@Retry(timeout=10, delay=1)
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
def get_random_part_id(self, node, table_name):
    """Choose a random active part in a table."""
    return random.choice(get_active_parts(node=node, table_name=table_name))


@TestStep
def get_random_partition_id(self, node, table_name):
    """Choose a random active partition in a table."""
    return random.choice(get_active_partition_ids(node=node, table_name=table_name))


@TestStep
@Name("detach part")
def detach_attach_random_partition(self):
    """Detach a random part, wait a random time, attach partition."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 3

    with When("I detach a part"):
        alter_table_detach_partition(node=node, partition_name=partition, exitcode=0)

    with Then(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I reattach the part"):
        alter_table_attach_partition(node=node, partition_name=partition, exitcode=0)


@TestStep
@Name("freeze part")
def freeze_unfreeze_random_part(self):
    """Freeze a random part, wait a random time, unfreeze part."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    backup_name = f"backup_{getuid()}"
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 3

    with When("I freeze the part"):
        alter_table_freeze_partition_with_name(
            node=node, partition_name=partition, backup_name=backup_name, exitcode=0
        )

    with Then(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I unfreeze the part"):
        alter_table_unfreeze_partition_with_name(
            node=node, partition_name=partition, backup_name=backup_name, exitcode=0
        )


@TestStep
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
            )


@TestStep
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
            )


@TestStep
@Retry(timeout=10, delay=1)
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
            )


@TestStep
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
@Retry(timeout=10, delay=1)
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
@Retry(timeout=10, delay=1)
@Name("delete row")
def delete_random_rows(self):
    """Delete a few rows at random."""
    table_name = get_random_table_name()
    node = get_random_node_for_table(table_name=table_name)
    column_name = get_random_column_name(node=node, table_name=table_name)
    divisor = random.choice([47, 53, 59, 61, 67])
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


@TestStep(Then)
def check_consistency(self, tables=None):
    """
    Check that the given tables hold the same amount of data on all nodes where they exist.
    Also check that column names match, subsequent part move tests require matching columns.
    """
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

        for attempt in retries(timeout=90, delay=2):
            with attempt:
                row_counts = {}
                column_names = {}
                for node in active_nodes:
                    with When(
                        f"I sync and count rows on node {node.name} for table {table_name}"
                    ):
                        with By(f"running SYNC REPLICA"):
                            try:
                                node.query(
                                    f"SYSTEM SYNC REPLICA {table_name}",
                                    timeout=10,
                                    no_checks=True,
                                )
                            except ExpectTimeoutError:
                                pass

                        with And(f"querying the row count"):
                            row_counts[node.name] = get_row_count(
                                node=node, table_name=table_name
                            )
                            column_names[node.name] = get_column_names(
                                node=node, table_name=table_name
                            )

                with Then("All replicas should have the same state"):
                    for n1, n2 in combinations(nodes, 2):
                        with By(f"Checking {n1.name} and {n2.name}"):
                            assert row_counts[n1.name] == row_counts[n2.name], error()
                            assert (
                                column_names[n1.name] == column_names[n2.name]
                            ), error()


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

    with delete_replica_lock:
        for node in nodes:
            r = nodes[0].query("SELECT table from system.replicas FORMAT JSONColumns")
            tables_by_node[node.name] = json.loads(r.output)["table"]

        table_counts = [len(tables) for tables in tables_by_node.values()]

        if min(table_counts) == 3:
            return

        adding_node = None
        reference_nodes = []
        for node, count in zip(nodes, table_counts):
            if count < 3 and adding_node is None:
                adding_node = node
            else:
                reference_nodes.append(node)

        assert adding_node is not None, "Early return logic should prevent this"

        with table_schema_lock:
            for table in tables:
                if table not in tables_by_node[adding_node.name]:

                    if table in tables_by_node[reference_nodes[0].name]:
                        columns = get_column_string(
                            node=reference_nodes[0], table_name=table
                        )
                    elif table in tables_by_node[reference_nodes[1].name]:
                        columns = get_column_string(
                            node=reference_nodes[1], table_name=table
                        )
                    else:
                        assert False, "This line should never be reached"

                    create_one_replica(
                        node=adding_node, table_name=table, columns=columns
                    )


@TestStep
def delete_replica(self):
    """
    Delete a random table replica, being careful to not delete the last replica
    """
    node = random.choice(self.context.ch_nodes)
    tables = self.context.table_names.copy()
    random.shuffle(tables)

    with delete_replica_lock:
        r = node.query(
            "SELECT table, active_replicas from system.replicas FORMAT JSONColumns"
        )
        out = json.loads(r.output)
        current_tables = out["table"]
        active_replicas = {t: r for t, r in zip(current_tables, out["active_replicas"])}

        for table in tables:
            if table in current_tables and active_replicas["table"] > 1:
                delete_one_replica(node=node, table_name=table)


@TestScenario
def parallel_alters(self):
    """
    Perform combinations of alter actions, checking that all replicas agree.
    """

    unstressed_limit = 100
    combination_size = 3
    run_groups_in_parallel = True
    storage_policy = "external_vfs"

    with Given("I have a list of actions I can perform"):
        actions = [
            add_random_column,
            rename_random_column,
            clear_random_column,
            delete_random_column,
            update_random_column,
            delete_random_rows,
            # delete_replica,
            # add_replica,
            detach_attach_random_partition,
            freeze_unfreeze_random_part,
            drop_random_part,
            replace_random_part,
            # move_random_partition_to_random_table,
            attach_random_part_from_table,
            fetch_random_part_from_table,
        ]

    with And(f"I make a list of groups of {combination_size} actions"):
        action_groups = list(
            combinations(actions, combination_size, with_replacement=True)
        )

    if not self.context.stress:
        with And(f"I shuffle the list and choose {unstressed_limit} groups of actions"):
            random.shuffle(action_groups)
            action_groups = action_groups[:unstressed_limit]

    with Given("I create 3 tables with 10 columns and data"):
        self.context.table_names = []
        columns = "key UInt64," + ",".join(f"value{i} UInt16" for i in range(10))
        for i in range(3):
            table_name = f"table{i}_{storage_policy}"
            replicated_table_cluster(
                table_name=table_name,
                storage_policy=storage_policy,
                partition_by="key % 4",
                columns=columns,
            )
            self.context.table_names.append(table_name)
            insert_random(
                node=self.context.node, table_name=table_name, columns=columns
            )

    total_combinations = len(action_groups)
    for i, chosen_actions in enumerate(action_groups):
        with Check(
            f"{i}/{total_combinations} "
            + ",".join([f"{f.name}" for f in chosen_actions])
        ):
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
                        parallel=True,
                        flags=TE,
                    )(table_name=table_name)

                join()

            with Then("I check that the replicas are consistent", flags=TE):
                check_consistency()


@TestFeature
@Name("stress alter")
def feature(self):
    """Stress test with many alters."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
