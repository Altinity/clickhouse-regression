#!/usr/bin/env python3
import time
import random
import json

from testflows.core import *
from testflows.combinatorics import product, combinations

from vfs.tests.steps import *
from vfs.requirements import *


@TestScenario
@Tags("sanity")
def no_duplication(self):
    """
    Check that data on replicated tables only exists once in S3.
    """

    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_test_replicas_duplication"
    nodes = self.context.ch_nodes[:2]

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_stable_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with And("I enable vfs"):
        enable_vfs()

    with And("I create a replicated table"):
        replicated_table_cluster(
            table_name=table_name,
            columns="d UInt64, m UInt64",
        )

    with Check("insert"):
        with When("I add data to the table on the first node"):
            insert_random(
                node=nodes[0],
                table_name=table_name,
                columns="d UInt64, m UInt64",
                rows=1000000,
            )

        with And("I get the new size of the s3 bucket"):
            size_after_insert = get_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                minio_enabled=self.context.minio_enabled,
                access_key=self.context.secret_access_key,
                key_id=self.context.access_key_id,
            )
            size_added = size_after_insert - size_empty

        with And("I add more data to the table on the second node"):
            insert_random(
                node=nodes[1],
                table_name=table_name,
                columns="d UInt64, m UInt64",
                rows=1000000,
            )

        with And("I wait for the nodes to sync"):
            nodes[0].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=30)
            nodes[1].query(f"SYSTEM SYNC REPLICA {table_name}", timeout=30)
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[0], table_name=table_name, rows=2000000
            )
            retry(assert_row_count, timeout=120, delay=1)(
                node=nodes[1], table_name=table_name, rows=2000000
            )

        with Then("the size of the s3 bucket should be doubled and no more"):
            expected_size = size_empty + size_added * 2
            check_stable_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=expected_size,
                tolerance=1500,
                minio_enabled=self.context.minio_enabled,
            )

    with Check("alter"):
        with When("I rename a column"):
            nodes[1].query(f"ALTER TABLE {table_name} RENAME COLUMN m TO u")

        with Then("the other node should reflect the change"):
            r = nodes[0].query(f"DESCRIBE TABLE {table_name}")
            assert "m\tUInt64" not in r.output, error(r)
            assert "u\tUInt64" in r.output, error(r)

        with And("there should be no change in storage usage"):
            check_stable_bucket_size(
                name=bucket_name,
                prefix=bucket_path,
                expected_size=expected_size,
                tolerance=2500,
                minio_enabled=self.context.minio_enabled,
            )


@TestScenario
@Tags("sanity")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Add("1.0"))
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
@Tags("sanity")
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
@Tags("sanity")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove("1.0"))
def add_remove_one_node(self):
    """
    Test that no data is lost when a node is removed and added as a replica
    during inserts on other replicas.
    """

    table_name = "add_remove_one_replica"
    storage_policy = "external_vfs"
    parallel = False
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

    with Given("I have a replicated table"):
        replicated_table_cluster(
            table_name=table_name, storage_policy=storage_policy, columns="d UInt64"
        )

    When(
        "I start inserts on the second node",
        test=insert_random,
        parallel=parallel,
    )(
        node=nodes[1],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )

    And(
        "I delete the replica on the third node",
        test=delete_one_replica,
        parallel=parallel,
    )(node=nodes[2], table_name=table_name)

    And(
        "I replicate the table on the third node",
        test=create_one_replica,
        parallel=parallel,
    )(node=nodes[2], table_name=table_name)

    When(
        "I start inserts on the first node",
        test=insert_random,
        parallel=parallel,
    )(
        node=nodes[0],
        table_name=table_name,
        columns="d UInt64",
        rows=rows_per_insert,
    )

    join()

    for node in nodes:
        with Then(f"I wait for {node.name} to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=node, table_name=table_name, rows=rows_per_insert * 2
            )


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
        insert_sets = 1

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
        insert_sets += 1

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

        And(
            "I continue with parallel inserts on the second node",
            test=insert_random,
            parallel=True,
        )(
            node=nodes[1],
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
        )
        insert_sets += 1

        join()

        with And("I wait for the third node to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
            )

        with Then("I also check the row count on the second node"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
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
        insert_sets += 1
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
        insert_sets += 1

        And(
            "I replicate the table on the first node again in parallel",
            test=create_one_replica,
            parallel=True,
        )(node=nodes[0], table_name=table_name)

        join()

        with Then("I wait for the first node to sync by watching the row count"):
            retry(assert_row_count, **retry_settings)(
                node=nodes[0], table_name=table_name, rows=rows_per_insert * insert_sets
            )

        with And("I check the row count on the other nodes"):
            assert_row_count(
                node=nodes[1], table_name=table_name, rows=rows_per_insert * insert_sets
            )
            assert_row_count(
                node=nodes[2], table_name=table_name, rows=rows_per_insert * insert_sets
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestOutline(Example)
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Replica_Remove("1.0"))
def command_combinations_outline(self, table_name, shuffle_seed=None, allow_vfs=True):
    """
    Perform combinations of actions on replicas, including adding and removing,
    checking that the replicas agree.
    """

    nodes = self.context.ch_nodes
    rows_per_insert = 500

    combination_size = 5
    shuffle_combinations = True
    combinations_limit = 50

    fault_probability = 0.15

    if self.context.stress:
        combinations_limit = 10000

    storage_policy = "external_vfs" if allow_vfs else "external_no_vfs"

    @TestStep(When)
    def add_replica(self, node):
        create_one_replica(
            node=node,
            table_name=table_name,
            replica_name=getuid(),
            no_checks=True,
            storage_policy=storage_policy,
        )

    @TestStep(When)
    def rm_replica(self, node):
        delete_one_replica(node=node, table_name=table_name)

    @TestStep(When)
    def insert(self, node):
        insert_random(
            node=node,
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert,
            no_checks=True,
            settings=f"insert_keeper_fault_injection_probability={fault_probability}",
        )

    @TestStep(When)
    def insert_large(self, node):
        insert_random(
            node=node,
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert * 10,
            no_checks=True,
            settings=f"insert_keeper_fault_injection_probability={fault_probability}",
        )

    @TestStep(When)
    def insert_small(self, node):
        insert_random(
            node=node,
            table_name=table_name,
            columns="d UInt64",
            rows=rows_per_insert // 10,
            no_checks=True,
            settings=f"insert_keeper_fault_injection_probability={fault_probability}",
        )

    @TestStep(When)
    def optimize(self, node):
        node.query(f"OPTIMIZE TABLE {table_name}", no_checks=True)

    @TestStep(When)
    def select(self, node):
        for _ in range(random.randint(2, 10)):
            node.query(f"SELECT count() FROM {table_name}", no_checks=True)

    @TestStep(When)
    def truncate(self, node):
        node.query(f"TRUNCATE TABLE IF EXISTS {table_name}", no_checks=True)

    @TestStep(When)
    def get_row_count(self, node):
        r = node.query(
            f"SELECT count() FROM {table_name} FORMAT JSON",
            exitcode=0,
        )
        return int(json.loads(r.output)["data"][0]["count()"])

    @TestStep(Then)
    @Retry(timeout=60, delay=0.5)
    def check_consistency(self):
        with When("I check which nodes have the table"):
            active_nodes = [
                n
                for n in nodes
                if table_name in n.query("SHOW TABLES", no_checks=True).output
            ]
            if not active_nodes:
                return

        with When("I make sure all nodes are synced"):
            for node in active_nodes:
                node.query(
                    f"SYSTEM SYNC REPLICA {table_name}", timeout=10, no_checks=True
                )

        with When("I query all nodes for their row counts"):
            row_counts = {}
            for node in active_nodes:
                row_counts[node.name] = get_row_count(node=node)

        with Then("All replicas should have the same state"):
            for n1, n2 in combinations(active_nodes, 2):
                assert row_counts[n1.name] == row_counts[n2.name], error()

    actions = [
        add_replica,
        insert,
        # insert_small,
        # insert_large,
        optimize,
        select,
        truncate,
        rm_replica,
    ]

    action_pairs = list(product(nodes, actions))

    action_combos = list(combinations(action_pairs, combination_size))
    n_combinations = len(action_combos)
    note(f"There are {n_combinations} possible combinations")

    if shuffle_combinations:
        random.Random(shuffle_seed).shuffle(action_combos)

    # To run a single n-command group, uncomment and adjust as required
    # action_combos = [
    #     [
    #         (nodes[0], insert),
    #         (nodes[0], optimize),
    #         (nodes[0], truncate),
    #         (nodes[2], insert),
    #         (nodes[2], select),
    #     ]
    # ]

    try:
        t = time.time()
        for i, combo in enumerate(action_combos):
            if i >= combinations_limit:
                break

            with Check(
                f"{i} " + ",".join([f"{n.name[-1]}:{f.name}" for n, f in combo])
            ):
                for action_node, action_func in combo:
                    When(
                        f"I {action_func.name} on {action_node.name}",
                        test=action_func,
                        parallel=True,
                        flags=TE,
                    )(node=action_node)

                join()

                with Then("I check that the replicas are consistent", flags=TE):
                    check_consistency()

                a = (time.time() - t) / (i + 1)
                with And(f"I note the average time taken: {a:.2f}s"):
                    note(f"Average time per combo {a:.2f}s")

        with Then(f"I record the average time taken: {a:.2f}s"):
            metric("Average time per combo", a, "s")
            note(
                f"It would take {(n_combinations*a)/60/60:.2f}h to test all {n_combinations} combinations"
            )

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                for attempt in retries(timeout=120, delay=2):
                    with attempt:
                        node.query(
                            f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0
                        )
                        node.restart()


@TestScenario
@Tags("combinatoric")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Combinatoric("0.0"))
def command_combinations(self, parallel=True):
    """
    Perform parallel actions on replicas and check that they all agree.
    """

    random_seed = random.random()
    note(f"Command combinations shuffle seed {random_seed}")
    Example(name="vfs", test=command_combinations_outline, parallel=parallel)(
        table_name="add_remove_vfs", shuffle_seed=random_seed, allow_vfs=True
    )
    Example(name="no vfs", test=command_combinations_outline, parallel=parallel)(
        table_name="add_remove_no_vfs", shuffle_seed=random_seed, allow_vfs=False
    )


@TestFeature
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
@Name("replica")
def feature(self):
    """Test that replicas can be added and removed without errors or duplicate data."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
