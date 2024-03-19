#!/usr/bin/env python3
from threading import Thread
from queue import Queue, Empty
import random
import time

from testflows.core import *
from testflows.combinatorics import product, combinations

from vfs.tests.steps import *
from vfs.requirements import *


@TestOutline(Check)
def parallel_operations(self, table_name, operations):
    """
    Perform a group of operations on a given table in parallel.

    operations is a list of (Node, callable) pairs where callable is a TestStep that takes the arguments (node, table_name)
    """
    executor = Pool()
    for action_node, action_func in operations:
        When(
            f"I {action_func.name} on {action_node.name}",
            test=action_func,
            parallel=True,
            executor=executor,
            flags=TE,
        )(node=action_node, table_name=table_name)


@TestStep(When)
def get_row_count(self, node, table_name):
    """Get the number of rows in a given table."""
    r = node.query(
        f"SELECT count() FROM {table_name} FORMAT JSON",
        exitcode=0,
    )
    return int(json.loads(r.output)["data"][0]["count()"])


@TestStep(Then)
def check_consistency(self, nodes, table_name):
    """Check that tables that exist on multiple nodes are consistent."""

    with When("I check which nodes have the table"):
        active_nodes = [n for n in nodes if table_name in n.query("SHOW TABLES").output]
        if not active_nodes:
            return

    with When("I make sure all nodes are synced"):
        for node in active_nodes:
            node.query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10, no_checks=True)

    with And("I query all nodes for their row counts"):
        row_counts = {}
        for node in active_nodes:
            row_counts[node.name] = get_row_count(node=node, table_name=table_name)

    with Then("All replicas should have the same state"):
        for n1, n2 in combinations(active_nodes, 2):
            assert row_counts[n1.name] == row_counts[n2.name], error()


@TestStep(When)
def operate_and_check(self, nodes, table_name, operations):
    """
    Perform a group of operations on a given table in parallel.
    Then check that on nodes where `table_name` exists, the number of rows match.

    operations is a list of (Node, callable) pairs where callable is a TestStep that takes the arguments (node, table_name)
    """
    with Check(",".join([f"{n.name[-1]}:{f.name}" for n, f in operations]), flags=TE):
        parallel_operations(table_name=table_name, operations=operations)

        with Then("I check that the replicas are consistent", flags=TE):
            check_consistency(nodes=nodes, table_name=table_name)


@TestOutline(Example)
def operate_and_check_worker(self, nodes, work_queue, refresh_table=False):
    """
    Call operate_and_check() on items in work_queue
    """

    table_name = "table_" + getuid()

    try:
        while True:
            if refresh_table:
                for node in nodes:
                    node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", timeout=10)
                table_name = "table_" + getuid()

            try:
                operations = work_queue.get_nowait()
            except Empty:
                return

            try:
                operate_and_check(
                    nodes=nodes, table_name=table_name, operations=operations
                )
            finally:
                work_queue.task_done()
    finally:
        # Even though `return` is above, the below should still execute
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", timeout=10)


@TestStep(When)
def operate_multiple_parallel(
    self, nodes, operations_groups, n_tables=10, refresh_tables=False
):
    """
    Perform groups of operations divided between many tables.

    operations_groups is a list of lists of (Node, callable) pairs where callable is a TestStep that takes the arguments (node, table_name)

    If `refresh_tables` is True, each group of operations will be provided with an unused table.
    """

    operations_queue = Queue()
    for g in operations_groups:
        operations_queue.put(g)

    executor = Pool()
    for i in range(n_tables):
        Example(
            f"thread_{i}",
            test=operate_and_check_worker,
            parallel=True,
            executor=executor,
        )(nodes=nodes, work_queue=operations_queue, refresh_table=refresh_tables)

    with Then("I wait for workers to finish"):
        join()

    with Then("I make sure the queued tasks were completed"):
        operations_queue.join()


@TestStep(When)
def rm_replica(self, node, table_name):
    """Remove the replica of a table on the given node."""
    delete_one_replica(node=node, table_name=table_name)


@TestStep(When)
def optimize(self, node, table_name):
    """OPTIMIZE TABLE with no checks."""
    node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)


@TestStep(When)
def select(self, node, table_name):
    """SELECT count() with no checks."""
    r = node.query(f"SELECT count() FROM {table_name}", no_checks=True)


@TestOutline(Example)
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Replica_Remove("1.0"))
def add_remove_outline(self, random_seed=None, allow_vfs=True):
    """
    Perform combinations of add/remove actions on replicas,
    checking that the replicas agree.
    """

    nodes = self.context.ch_nodes
    rows_per_insert = 500

    combination_size = 5
    shuffle_combinations = True
    combinations_limit = 200
    n_tables = combinations_limit // 5

    if self.context.stress:
        combinations_limit = None

    storage_policy = "external_vfs" if allow_vfs else "external_no_vfs"

    @TestStep(When)
    def add_replica(self, node, table_name):
        create_one_replica(
            node=node,
            table_name=table_name,
            replica_name=getuid(),
            no_checks=True,
            storage_policy=storage_policy,
        )

    @TestStep(When)
    def insert(self, node, table_name):
        insert_random(
            node=node,
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
            no_checks=True,
        )

    actions = [
        add_replica,
        insert,
        optimize,
        select,
        rm_replica,
    ]

    action_pairs = list(product(nodes, actions))

    action_combos = list(combinations(action_pairs, combination_size))
    if shuffle_combinations:
        random.seed(random_seed)
        random.shuffle(action_combos)

    if combinations_limit:
        action_combos = action_combos[:combinations_limit]

    operate_multiple_parallel(
        nodes=nodes, operations_groups=action_combos, n_tables=n_tables
    )


@TestScenario
@Tags("long", "combinatoric")
def add_remove_commands(self, parallel=True):
    """
    Perform parallel actions on replicas and check that they all agree.
    """
    random_seed = random.random()
    Example(name="vfs", test=add_remove_outline, parallel=parallel)(
        allow_vfs=True, random_seed=random_seed
    )
    Example(name="no vfs", test=add_remove_outline, parallel=parallel)(
        allow_vfs=False, random_seed=random_seed
    )


@TestFeature
@Name("parallel replica")
def feature(self):
    """Test operating on multiple replicated tables in parallel."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
