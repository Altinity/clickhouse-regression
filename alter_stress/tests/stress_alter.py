#!/usr/bin/env python3
import random
from itertools import chain
import time

from testflows.core import *
from testflows.combinatorics import combinations

from helpers.alter import *
from alter_stress.tests.steps import *
from alter_stress.tests.actions import *


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
    n_tables=5,
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
        with Given(f"I create {n_tables} tables with 50 columns and data"):
            self.context.table_names = []
            columns = "key DateTime," + ",".join(f"value{i} UInt16" for i in range(50))
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

        with And("I create 10 random projections and indexes"):
            for _ in range(10):
                add_random_projection()
                add_random_index()

        # To test a single combination, uncomment and edit as needed.
        # action_groups = [
        #     [
        #         delete_replica,
        #         add_replica,
        #     ]
        # ]
        action_groups = [
            [
                drop_random_part,
                delete_random_rows,
                move_random_partition_to_random_table,
            ]
        ] * 5

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
                f"sudo {current_dir()}/../create_fixed_volumes.sh",
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
                f"sudo {current_dir()}/../destroy_fixed_volumes.sh",
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
def normal(self):
    """Run test scenarios without vfs."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, tags=["long", "combinatoric"])


@TestFeature
@Name("alter")
def feature(self):
    """Stress test with many alters."""

    with Given("I have S3 disks configured"):
        s3_config()

    for sub_feature in loads(current_module(), Feature):
        if sub_feature is feature:
            continue
        Feature(run=sub_feature)
