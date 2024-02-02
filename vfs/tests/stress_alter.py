#!/usr/bin/env python3
import random
import json
from itertools import chain

from testflows.core import *
from testflows.combinatorics import combinations

from helpers.alter import *
from vfs.tests.steps import *
from vfs.requirements import *


@TestStep
def optimize(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    for _ in range(random.randint(1, 5)):
        node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)


@TestStep
def insert(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    columns = get_column_string(node=node, table_name=table_name)
    insert_random(node=node, table_name=table_name, columns=columns, no_checks=True)


@TestStep
def select(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    for _ in range(random.randint(1, 10)):
        node.query(f"SELECT count() FROM {table_name}", no_checks=True)


@TestStep
def get_column_string(self, node, table_name) -> str:
    r = node.query(f"DESCRIBE TABLE {table_name}")
    return ",".join(r.output.splitlines())


@TestStep
def get_column_names(self, node, table_name) -> list:
    r = node.query(f"DESCRIBE TABLE {table_name} FORMAT JSONColumns")
    return json.loads(r.output)["name"]


@TestStep
def get_random_column_name(self, node, table_name):
    columns_no_primary_key = get_column_names(node=node, table_name=table_name)[1:]
    return random.choice(columns_no_primary_key)


@TestStep
@Name("add column")
def add_random_column(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    alter_table_add_column(
        table_name=table_name,
        column_name=f"c{random.randint(0, 99999)}",
        column_type="UInt16",
        node=node,
        no_checks=True,
    )


@TestStep
@Name("delete column")
def delete_random_column(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    alter_table_drop_column(
        node=node, table_name=table_name, column_name=column_name, no_checks=True
    )


@TestStep
@Name("rename column")
def rename_random_column(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    new_name = f"c{random.randint(0, 99999)}"
    alter_table_rename_column(
        node=node,
        table_name=table_name,
        column_name_old=column_name,
        column_name_new=new_name,
        no_checks=True,
    )


@TestStep
@Name("update column")
def update_random_column(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    alter_table_update_column(
        table_name=table_name,
        column_name=column_name,
        expression=f"({column_name} * 5)",
        condition=f"({column_name} < 10000)",
        node=node,
        no_checks=True,
    )


@TestStep
@Name("clear column")
def clear_random_column(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    alter_table_clear_column_in_partition(
        node=node,
        table_name=table_name,
        column_name=column_name,
        partition_name=str(random.randint(0, 3)),
        no_checks=True,
    )


@TestStep
@Name("delete row")
def delete_random_rows(self):
    node = random.choice(self.context.ch_nodes)
    table_name = random.choice(self.context.table_names)
    column_name = get_random_column_name(node=node, table_name=table_name)
    alter_table_delete_rows(
        table_name=table_name,
        condition=f"({column_name} % 17)",
        node=node,
        no_checks=True,
    )


@TestStep(When)
def get_row_count(self, node, table_name):
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON",
        exitcode=0,
    )
    return int(json.loads(r.output)["data"][0]["count()"])


@TestStep(Then)
def check_consistency(self):
    nodes = self.context.ch_nodes
    for table_name in self.context.table_names:
        for attempt in retries(timeout=60, delay=0.5):
            with attempt:
                with When("I make sure all nodes are synced"):
                    for node in nodes:
                        node.query(
                            f"SYSTEM SYNC REPLICA {table_name}",
                            timeout=10,
                            no_checks=True,
                        )

                with When("I query all nodes for their row counts"):
                    row_counts = {}
                    for node in nodes:
                        row_counts[node.name] = get_row_count(
                            node=node, table_name=table_name
                        )

                with Then("All replicas should have the same state"):
                    for n1, n2 in combinations(nodes, 2):
                        assert row_counts[n1.name] == row_counts[n2.name], error()


@TestScenario
def parallel_alters(self):
    """
    Perform combinations of alter actions, checking that all replicas agree.
    """

    self.context.table_names = []
    columns = "key UInt64," + ",".join(f"value{i} UInt16" for i in range(10))

    with Given("I create 3 tables with data"):
        for _ in range(3):
            _, table_name = replicated_table_cluster(
                storage_policy="external_vfs",
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
    ]

    action_groups = list(combinations(actions, combination_size, with_replacement=True))
    for chosen_actions in action_groups:
        with Check(",".join([f"{f.name}" for f in chosen_actions])):
            for action in chain([insert, select], chosen_actions, [optimize]):
                When(
                    f"I {action.name}",
                    run=action,
                    parallel=True,
                    flags=TE,
                )

            join()

            with Then("I check that the replicas are consistent", flags=TE):
                check_consistency()


@TestFeature
@Name("stress alter")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
