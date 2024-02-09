#!/usr/bin/env python3
import random
import json
from itertools import chain

from testflows.core import *
from testflows.combinatorics import combinations
from testflows.uexpect.uexpect import ExpectTimeoutError

from helpers.alter import *
from vfs.tests.steps import *
from vfs.requirements import *


@TestStep
@Retry(timeout=10, delay=1)
def optimize(self, node=None, table_name=None):
    """Apply OPTIMIZE on the given table and node, choosing at random if not specified."""
    if node is None:
        node = random.choice(self.context.ch_nodes)
    if table_name is None:
        table_name = random.choice(self.context.table_names)
    for _ in range(random.randint(1, 5)):
        with By(f"optimizing {table_name} on {node.name}"):
            node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)


@TestStep
@Retry(timeout=10, delay=1)
def insert(self):
    """Insert random data to a random table."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    columns = get_column_string(node=node, table_name=table_name)
    with By(f"inserting rows to {table_name} on {node.name}"):
        insert_random(node=node, table_name=table_name, columns=columns, no_checks=True)


@TestStep
@Retry(timeout=10, delay=1)
def select(self):
    """Perform select queries on a random node."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    for _ in range(random.randint(1, 10)):
        with By(f"count rows in {table_name} on {node.name}"):
            node.query(f"SELECT count() FROM {table_name}", no_checks=True)


@TestStep
def get_column_string(self, node, table_name) -> str:
    """Get a string with column names and types."""
    r = node.query(f"DESCRIBE TABLE {table_name}")
    return ",".join([l.strip() for l in r.output.splitlines()])


@TestStep
def get_column_names(self, node, table_name) -> list:
    """Get a list of a table's column names."""
    r = node.query(f"DESCRIBE TABLE {table_name} FORMAT JSONColumns")
    return json.loads(r.output)["name"]


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
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    By(
        name=f"add column to {table_name} with {node.name}",
        test=alter_table_add_column,
    )(
        table_name=table_name,
        column_name=f"c{random.randint(0, 99999)}",
        column_type="UInt16",
        node=node,
        no_checks=True,
    )


@TestStep
@Retry(timeout=10, delay=1)
@Name("delete column")
def delete_random_column(self):
    """Delete a random column."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    By(
        name=f"delete column from {table_name} with {node.name}",
        test=alter_table_drop_column,
    )(node=node, table_name=table_name, column_name=column_name, no_checks=True)


@TestStep
@Retry(timeout=10, delay=1)
@Name("rename column")
def rename_random_column(self):
    """Rename a random column to a random value."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    new_name = f"c{random.randint(0, 99999)}"
    By(
        name=f"rename column from {table_name} with {node.name}",
        test=alter_table_rename_column,
    )(
        node=node,
        table_name=table_name,
        column_name_old=column_name,
        column_name_new=new_name,
        no_checks=True,
    )


@TestStep
@Retry(timeout=10, delay=1)
@Name("update column")
def update_random_column(self):
    """Replace some values on a random column."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
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
        no_checks=True,
    )


@TestStep
def get_parts(self, node, table_name):
    """Get a list of active parts in a table."""
    r = node.query(
        f"select name from system.parts where table='{table_name}' and active=1 FORMAT JSONColumns"
    )
    return json.loads(r.output)["name"]


@TestStep
def get_random_part_id(self, node, table_name):
    """Choose a random active part in a table."""
    return random.choice(get_parts(node, table_name))


@TestStep
def get_partition_ids(self, node, table_name):
    """Get a list of active partitions in a table."""
    r = node.query(
        f"select partition_id from system.parts where table='{table_name}' and active=1 FORMAT JSONColumns"
    )
    return json.loads(r.output)["partition_id"]


@TestStep
def get_random_partition_id(self, node, table_name):
    """Choose a random active partition in a table."""
    return random.choice(get_partition_ids(node, table_name))


@TestStep
@Name("detach part")
def detach_attach_random_part(self):
    """Detach a random part, wait a random time, attach part."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    backup_name = f"backup_{getuid()}"
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 5

    with When("I detach a part"):
        node.query(
            f"ALTER TABLE {table_name} DETACH PARTITION {partition}",
            exitcode=0,
        )

    with Then(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I reattach the part"):
        node.query(
            f"ALTER TABLE {table_name} ATTACH PARTITION {partition}",
            exitcode=0,
        )


@TestStep
@Name("freeze part")
def freeze_unfreeze_random_part(self):
    """Freeze a random part, wait a random time, unfreeze part."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    backup_name = f"backup_{getuid()}"
    partition = get_random_partition_id(node=node, table_name=table_name)
    delay = random.random() * 5

    with When("I freeze the part"):
        node.query(
            f"ALTER TABLE {table_name} FREEZE PARTITION {partition} WITH NAME '{backup_name}'",
            exitcode=0,
        )

    with Then(f"I wait {delay:.2}s"):
        time.sleep(delay)

    with Finally("I unfreeze the part"):
        node.query(
            f"ALTER TABLE {table_name} UNFREEZE PARTITION {partition} WITH NAME '{backup_name}'",
            exitcode=0,
        )


@TestStep
@Name("drop part")
def drop_random_part(self):
    """Detach and drop a random part."""

    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    part_id = get_random_part_id(node=node, table_name=table_name)
    detach_first = random.randint(0, 1)

    if detach_first:
        with When("I detach a partition from the first table"):
            node.query(f"ALTER TABLE {table_name} DETACH PART {part_id}", exitcode=0)

        with And("I drop the detached partition"):
            node.query(
                f"ALTER TABLE {table_name} DROP DETACHED PART {part_id} SETTINGS allow_drop_detached=1",
                exitcode=0,
            )
    else:
        with When("I drop the part"):
            node.query(f"ALTER TABLE {table_name} DROP PART {part_id}", exitcode=0)


@TestStep
@Name("replace part")
def replace_random_part(self):
    """Test attaching a random part from one table to another."""

    node = random.choice(self.context.ch_nodes)
    destination_table_name = random.choice(self.context.table_names)
    source_table_name = random.choice(self.context.table_names)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with When("I replace a partition on the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} REPLACE PARTITION {partition} FROM {source_table_name}",
            exitcode=0,
        )


@TestStep
@Name("move partition to table")
def move_random_partition_to_random_table(self):
    """Move a random partition from one table to another."""

    node = random.choice(self.context.ch_nodes)
    destination_table_name = random.choice(self.context.table_names)
    source_table_name = random.choice(self.context.table_names)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {source_table_name} MOVE PARTITION {partition} TO TABLE {destination_table_name}",
            exitcode=0,
        )


@TestStep
@Name("attach part")
def attach_random_part_from_table(self):
    """Attach a random partition from one table to another."""

    node = random.choice(self.context.ch_nodes)
    destination_table_name = random.choice(self.context.table_names)
    source_table_name = random.choice(self.context.table_names)
    partition = get_random_partition_id(node=node, table_name=source_table_name)

    with When("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} ATTACH PARTITION {partition} FROM {source_table_name}",
            exitcode=0,
        )


@TestStep
@Name("fetch part")
def fetch_random_part_from_table(self):
    """Fetching a random part from another table replica."""

    node = random.choice(self.context.ch_nodes)
    destination_table_name = random.choice(self.context.table_names)
    source_table_name = random.choice(self.context.table_names)
    part_id = get_random_part_id(node=node, table_name=source_table_name)

    with When("I fetch a partition from the first table"):
        node.query(
            f"ALTER TABLE {destination_table_name} FETCH PART '{part_id}' FROM '/clickhouse/tables/{source_table_name}'",
            exitcode=0,
        )

    with And("I attach the partition to the second table"):
        node.query(
            f"ALTER TABLE {destination_table_name} ATTACH PART '{part_id}'", exitcode=0
        )


@TestStep
@Retry(timeout=10, delay=1)
@Name("clear column")
def clear_random_column(self):
    """Clear a random column on a random partition."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
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
    """Delete rows a few rows at random."""
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    By(
        name=f"delete rows from {table_name} with {node.name}",
        test=alter_table_delete_rows,
    )(
        table_name=table_name,
        condition=f"({column_name} % 17)",
        node=node,
        no_checks=True,
    )


@TestStep(When)
@Retry(timeout=30, delay=1)
def get_row_count(self, node, table_name):
    """Get the number of rows in the given table."""
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON",
        exitcode=0,
    )
    return int(json.loads(r.output)["data"][0]["count()"])


@TestStep(Then)
def check_consistency(self, tables=None):
    """Check that the given tables hold the same amount of data on all nodes where they exist."""
    nodes = self.context.ch_nodes
    if tables is None:
        tables = self.context.table_names
    for table_name in tables:
        for attempt in retries(timeout=180, delay=2):
            with attempt:
                row_counts = {}
                for node in nodes:
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

                with Then("All replicas should have the same state"):
                    for n1, n2 in combinations(nodes, 2):
                        with By(f"Checking {n1.name} and {n2.name}"):
                            assert row_counts[n1.name] == row_counts[n2.name], error()


@TestScenario
def parallel_alters(self, storage_policy="external_vfs"):
    """
    Perform combinations of alter actions, checking that all replicas agree.
    """

    self.context.table_names = []
    columns = "key UInt64," + ",".join(f"value{i} UInt16" for i in range(10))
    unstressed_limit = 100

    with Given("I create 3 tables with data"):
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

    combination_size = 3
    actions = [
        add_random_column,
        rename_random_column,
        clear_random_column,
        delete_random_column,
        update_random_column,
        delete_random_rows,
        detach_attach_random_part,
        freeze_unfreeze_random_part,
        drop_random_part,
        replace_random_part,
        move_random_partition_to_random_table,
        attach_random_part_from_table,
        fetch_random_part_from_table,
    ]

    action_groups = list(combinations(actions, combination_size, with_replacement=True))

    if not self.context.stress:
        random.shuffle(action_groups)
        action_groups = action_groups[:unstressed_limit]

    total_combinations = len(action_groups)
    for i, chosen_actions in enumerate(action_groups):
        with Check(
            f"{i}/{total_combinations} "
            + ",".join([f"{f.name}" for f in chosen_actions])
        ):
            for action in chain([insert, select], chosen_actions):
                When(
                    f"I {action.name}",
                    run=action,
                    parallel=True,
                    flags=TE | ERROR_NOT_COUNTED,  # |FAIL_NOT_COUNTED,
                )

            for table in self.context.table_names:
                When(
                    f"I OPTIMIZE {table}",
                    test=optimize,
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
