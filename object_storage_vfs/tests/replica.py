#!/usr/bin/env python3
import time
import random
import json

from testflows.core import *
from testflows.combinatorics import product, combinations

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_038_DiskObjectStorageVFS_Replica_Add("1.0"),
    RQ_SRS_038_DiskObjectStorageVFS_Core_NoDataDuplication("1.0"),
)
def add_replica(self):
    """
    Test that replicas can be added to an existing table:
     - with the full data being accessible.
     - without significantly increasing disk usage.
    """

    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_adding_replicas"
    nodes = self.context.ch_nodes

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with And("I enable vfs"):
        enable_vfs()

    try:
        with Given("I have a replicated table on one node"):
            create_one_replica(node=nodes[0], table_name=table_name)

        with And("I add data to the table"):
            insert_random(
                node=nodes[0], table_name=table_name, columns="d UInt64", rows=1000000
            )

        with And("I get the new size of the s3 bucket"):
            size_after_insert = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )

        with And("I create a replicated table on the second node"):
            create_one_replica(node=nodes[1], table_name=table_name)

        with And("I wait for the replica to sync"):
            nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=30)
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[1], table_name=table_name, rows=1000000
            )

        with Then(
            """The size of the s3 bucket should be 1 byte more
                    than previously because of the additional replica"""
        ):
            check_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=size_after_insert + 1,
                tolerance=500,
                minio_enabled=self.context.minio_enabled,
            )

        with And("I check the row count on the first node"):
            assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

        with And("I wait for the second node to sync"):
            nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10)

        with And("I check the row count on the second node"):
            assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Offline("1.0"))
def offline_replica(self):
    """
    Test that an offline replica can recover data that was inserted on another replica.
    """

    table_name = "vfs_dropping_replicas"
    nodes = self.context.ch_nodes

    with Given("I enable vfs"):
        enable_vfs()

    with And(f"I create a replicated table on each node"):
        replicated_table_cluster(
            table_name=table_name,
            columns="d UInt64",
        )

    with When("I add data to the table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns="d UInt64", rows=500000
        )

    with And("I stop the other node"):
        nodes[1].stop()

    with And("I add more data to the table"):
        insert_random(
            node=nodes[0], table_name=table_name, columns="d UInt64", rows=500000
        )

    with Then("I restart the other node"):
        nodes[1].start()

    with And("I check the row count on the first node"):
        assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

    with And("I wait for the second node to sync"):
        nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=10)

    with And("I check the row count on the second node"):
        assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove("1.0"))
def parallel_add_remove(self):
    """
    Test that no data is lost when replicas are added and removed
    during inserts on other replicas.
    """

    table_name = "vfs_add_remove_replicas"
    nodes = self.context.ch_nodes
    rows_per_insert = 100_000_000
    retry_settings = {
        "timeout": 120,
        "initial_delay": 5,
        "delay": 2,
    }

    if self.context.stress:
        rows_per_insert = 500_000_000
        retry_settings["timeout"] = 300
        retry_settings["delay"] = 5

    with Given("I enable vfs"):
        enable_vfs()

    try:
        with Given("I have a replicated table on one node"):
            create_one_replica(node=nodes[0], table_name=table_name)

        When(
            "I start parallel inserts on the first node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[0],
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
        )

        And(
            "I replicate the table on the second node in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[1], table_name=table_name)

        join()

        with Then("I wait for the second node to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=nodes[1], table_name=table_name, rows=rows_per_insert
            )

        And(
            "I start parallel inserts on the second node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
        )

        And(
            "I delete the replica on the first node",
            test=delete_one_replica,
            parallel=True,
        )(node=nodes[0], table_name=table_name)

        And(
            "I replicate the table on the third node in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[2], table_name=table_name)

        join()

        with And("I wait for the third node to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * 2
            )

        with Then("I also check the row count on the second node"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * 2
            )

        Given(
            "I start parallel inserts on the second node in parallel",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
        )
        And(
            "I start parallel inserts on the third node in parallel",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[2],
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
        )

        And(
            "I replicate the table on the first node again in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[0], table_name=table_name)

        join()

        with Then("I wait for the first node to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=nodes[0], table_name=table_name, rows=rows_per_insert * 4
            )

        with And("I check the row count on the other nodes"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * 4
            )
            assert_row_count(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * 4
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestOutline(Scenario)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove("1.0"))
def add_remove_replicas(self, allow_vfs=True):
    table_name = "vfs_random_add_remove_replicas"
    nodes = self.context.ch_nodes
    rows_per_insert = 1_000_000

    loop_sleep = 10
    n_loops = 10
    n_parallel = 5

    @TestStep(When)
    def add_table_replica(self, node):
        create_one_replica(
            node=node, table_name=table_name, replica_name=getuid(), no_checks=True
        )

    @TestStep(When)
    def remove_replica(self, node):
        delete_one_replica(node=node, table_name=table_name)

    @TestStep(When)
    def insert_data(self, node):
        insert_random(
            node=node,
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
            no_checks=True,
        )

    @TestStep(When)
    def optimize_table(self, node):
        node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)

    @TestStep(When)
    def select_count(self, node):
        r = node.query(f"SELECT count() FROM {table_name}", no_checks=True)

    @TestStep(When)
    def get_row_count(self, node):
        r = node.query(
            f"SELECT count() FROM {table_name} FORMAT JSON",
            exitcode=0,
        )
        return int(json.loads(r.output)["data"][0]["count()"])

    @TestStep(Then)
    def check_consistency(self):
        with When("I check which nodes have the table"):
            active_nodes = [
                n for n in nodes if table_name in n.query("SHOW TABLES").output
            ]
            if not active_nodes: return

        with When("I make sure all nodes are synced"):
            for node in active_nodes:
                node.query(
                    f"SYSTEM SYNC REPLICA {table_name}", timeout=60, no_checks=True
                )

        with And("I query all nodes for their row counts"):
            row_counts = {}
            for node in active_nodes:
                row_counts[node.name] = get_row_count(node=node)

        with Then("All replicas should have the same state"):
            for n1, n2 in combinations(active_nodes, 2):
                assert row_counts[n1.name] == row_counts[n2.name], error()

    actions = [
        add_table_replica,
        insert_data,
        optimize_table,
        select_count,
        remove_replica,
    ]

    action_pairs = list(product(nodes, actions))

    try:
        if allow_vfs:
            with Given("I enable vfs"):
                enable_vfs()

        for _ in range(n_loops):
            action_node, action_func = random.choice(action_pairs)

            for _ in range(n_parallel):
                When(
                    f"I {action_func.name} on {action_node.name}",
                    test=action_func,
                    parallel=True,
                )(node=action_node)

            join()

            with Then("I check that the replicas are consistent"):
                check_consistency()

        with When("I wait for all tasks to finish"):
            join()

        with And("I make sure all nodes are replicating"):
            for node in nodes:
                add_table_replica(node=node)

        with When("I make sure all nodes are synced"):
            for node in nodes:
                node.query(
                    f"SYSTEM SYNC REPLICA {table_name}", timeout=60, no_checks=True
                )

        with And("I query all nodes for their row counts"):
            row_counts = []
            for node in nodes:
                row_counts.append(get_row_count(node=node))

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestScenario
def random_add_remove(self):
    """
    Randomly perform actions on replicas and check that they all agree.
    """
    add_remove_replicas(allow_vfs=True)


@TestScenario
def random_add_remove_no_vfs(self):
    """
    To isolate issues, run the same test without vfs
    """
    add_remove_replicas(allow_vfs=False)


@TestFeature
@Name("replica")
def feature(self):
    # Use the same seed for all tests, but a different seed each run
    random_seed = random.random()
    note(f"Using seed {random_seed}")

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        random.seed(random_seed)
        scenario()
