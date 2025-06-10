#!/usr/bin/env python3
import random
from itertools import chain
import time
import inspect

from testflows.core import *
from testflows.combinatorics import combinations

from helpers.alter import *
from helpers.common import check_clickhouse_version
from alter.stress.tests.actions import *
from alter.stress.tests.steps import *


def build_action_list(
    columns=True,
    part_manipulation=True,
    ttl=True,
    projections=False,
    indexes=True,
    restarts=False,
    network_restarts=False,
    add_remove_replicas=False,
    fill_disks=False,
):
    actions = [
        delete_random_rows,
    ]

    if ttl:
        actions += [
            modify_random_ttl,
            remove_random_ttl,
        ]

    if restarts:
        actions += [restart_keeper, restart_clickhouse]

    if network_restarts:
        actions.append(restart_network)

    if add_remove_replicas:
        actions += [delete_replica, add_replica]

    if columns:
        actions += [
            add_random_column,
            rename_random_column,
            clear_random_column,
            delete_random_column,
            update_random_column,
        ]

    if part_manipulation:
        actions += [
            detach_attach_random_partition,
            freeze_unfreeze_random_part,
            drop_random_part,
            replace_random_part,
            move_random_partition_to_random_disk,
            move_random_partition_to_random_table,
            attach_random_part_from_table,
            fetch_random_part_from_table,
        ]

    if projections:
        actions += [
            add_random_projection,
            clear_random_projection,
            drop_random_projection,
        ]
    else:
        actions += [delete_random_rows_lightweight]

    if indexes:
        actions += [
            add_random_index,
            clear_random_index,
            drop_random_index,
        ]

    if fill_disks:
        actions += [
            fill_clickhouse_disks,
            fill_zookeeper_disks,
        ]

    return actions


def build_action_groups(
    actions: list,
    combination_size=3,
    limit=10,
    shuffle=True,
    with_replacement=True,
):
    with Given(f"I make a list of groups of {combination_size} actions"):
        action_groups = list(
            combinations(actions, combination_size, with_replacement=with_replacement)
        )

    if shuffle:
        with And("I shuffle the list"):
            random.shuffle(action_groups)

    if limit:
        with And(f"I choose {limit} groups of actions"):
            action_groups = action_groups[:limit]

    return action_groups


@TestOutline(Scenario)
def alter_combinations(
    self,
    actions: list,
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
    n_columns=50,
    network_impairment=False,
    limit_disk_space=False,
    enforce_table_structure=None,
    kill_stuck_mutations=None,
    always_wait_for_mutations_to_finish=False,
):
    """
    Perform combinations of alter actions, checking that all replicas agree.
    """

    self.context.ignore_failed_part_moves = ignore_failed_part_moves
    self.context.sync_replica_timeout = sync_replica_timeout
    self.context.storage_policy = storage_policy
    self.context.minimum_replicas = minimum_replicas
    self.context.maximum_replicas = maximum_replicas

    assert not (
        restart_network in actions and network_impairment
    ), "network impairment is not compatible with restart_network"

    if fill_clickhouse_disks in actions or fill_zookeeper_disks in actions:
        assert (
            limit_disk_space
        ), "enable limit_disk_space when using fill_disks to avoid unexpected behavior"

    if enforce_table_structure is None:
        enforce_table_structure = self.flags & TE
    if kill_stuck_mutations is None:
        kill_stuck_mutations = self.flags & TE

    action_groups = build_action_groups(
        actions=actions,
        combination_size=combination_size,
        limit=limit,
        shuffle=shuffle,
    )

    # To test a single combination, uncomment and edit as needed.
    # action_groups = [
    #     [
    #         delete_replica,
    #         add_replica,
    #     ]
    # ]

    background_actions = [
        insert_to_random,
        select_count_random,
        select_sum_random,
        select_max_min_random,
    ]

    if limit_disk_space:
        with Given("Clickhouse is restarted with limited disk space"):
            for node in self.context.ch_nodes:
                limit_clickhouse_disks(node=node)

        with And("Zookeeper is restarted with limited disk space"):
            for node in self.context.zk_nodes:
                limit_zookeeper_disks(node=node)

    try:
        with Given(f"I create {n_tables} tables with {n_columns} columns and data"):
            self.context.table_names = []
            columns = "key DateTime," + ",".join(
                f"value{i} UInt16" for i in range(n_columns)
            )
            ttl = (
                f"key + INTERVAL {random.randint(1, 10)} YEAR"
                if modify_random_ttl in actions
                else None
            )
            table_settings = (
                "min_bytes_for_wide_part=0"
                if self.context.workarounds.get("wide_parts_only")
                else None
            )

            for i in range(n_tables):
                table_name = f"table{i}_{self.context.storage_policy}"
                replicated_table_cluster(
                    table_name=table_name,
                    storage_policy=self.context.storage_policy,
                    partition_by="toQuarter(key) - 1",
                    columns=columns,
                    ttl=ttl,
                    no_cleanup=True,
                    settings=table_settings,
                )
                self.context.table_names.append(table_name)
                insert_random(
                    node=self.context.node, table_name=table_name, columns=columns
                )

        with And("I create 10 random projections and indexes if required"):
            for _ in range(10):
                # safe=False because we don't need to waste time on extra checks during setup
                if drop_random_projection in actions:
                    add_random_projection(safe=False)

                if drop_random_index in actions:
                    add_random_index(safe=False)

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
                try:
                    if network_impairment:
                        with Given("a network impairment"):
                            impaired_network(network_mode=net_mode)

                    with When("I perform a group of actions"):
                        for action in chain(background_actions, chosen_actions):
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

                    if always_wait_for_mutations_to_finish:
                        with And("I wait for all mutations to finish"):
                            wait_for_mutations_to_finish(timeout=300)

                except:
                    with Finally("I dump system.part_logs to csv"):
                        for node in self.context.ch_nodes:
                            node.query(
                                "SELECT * FROM system.part_log INTO OUTFILE '/var/log/clickhouse-server/part_log.csv' TRUNCATE FORMAT CSV"
                            )

                finally:
                    with Finally(
                        "I make sure that the replicas are consistent", flags=TE
                    ):
                        if kill_stuck_mutations:
                            with By("killing any failing mutations"):
                                for node in self.context.ch_nodes:
                                    r = node.query(
                                        "SELECT * FROM system.mutations WHERE is_done=0 AND latest_fail_reason != '' FORMAT Vertical",
                                        no_checks=True,
                                    )
                                    if r.output != "":
                                        r = node.query(
                                            "KILL MUTATION WHERE latest_fail_reason != ''"
                                        )
                                        assert r.output == "", error(
                                            "An erroring mutation was killed"
                                        )

                        with By("making sure that replicas agree"):
                            check_consistency(
                                restore_consistent_structure=enforce_table_structure
                            )

                    with And(
                        "I make sure that there is still free disk space on the host"
                    ):
                        r = self.context.cluster.command(None, "df -h .")
                        if "100%" in r.output:
                            with When("I drop rows to free up space"):
                                for table_name in self.context.table_names:
                                    delete_random_rows(table_name=table_name)
                                    delete_random_rows(table_name=table_name)

            note(f"Average time per test combination {(time.time()-t)/(i+1):.1f}s")

    finally:
        with Finally("I log any pending mutations that might have caused a fail"):
            log_failing_mutations()

        with Finally(
            "I drop each table on each node in case the cluster is in a bad state"
        ):
            for node in self.context.ch_nodes:
                for table_name in self.context.table_names:
                    When(test=delete_one_replica, parallel=True)(
                        node=node, table_name=table_name, timeout=120
                    )
            join()


@TestScenario
def one_by_one(self):
    """
    Perform only one subset of actions at a time.
    """

    action_subsets = inspect.getfullargspec(build_action_list).args
    all_disabled = {action: False for action in action_subsets}

    for action in action_subsets:
        with Example(action.replace("_", " ")):
            action_list_args = all_disabled.copy()
            action_list_args[action] = True

            action_list = build_action_list(**action_list_args)

            # If the list is short, multiply it to get more combinations
            if len(action_list) <= 4:
                action_list *= 2

            alter_combinations(
                actions=action_list,
                limit=None if self.context.stress else 20,
                limit_disk_space=(action == "fill_disks"),
            )


@TestScenario
def pairs(self):
    """
    Perform a mix of two subsets of actions.
    """

    action_subsets = inspect.getfullargspec(build_action_list).args
    all_disabled = {action: False for action in action_subsets}

    for action1, action2 in combinations(action_subsets, 2):
        with Example(f"{action1} and {action2}".replace("_", " ")):
            if "fill_disks" in [action1, action2]:
                skip("TODO: investigate fill_disks behavior")

            action_list_args = all_disabled.copy()
            action_list_args[action1] = True
            action_list_args[action2] = True

            alter_combinations(
                actions=build_action_list(**action_list_args),
                limit=None if self.context.stress else 20,
                limit_disk_space=("fill_disks" in [action1, action2]),
            )


@TestScenario
def safe(self):
    """
    Perform only actions that are relatively unlikely to cause exceptions.
    """

    alter_combinations(
        actions=build_action_list(
            columns=False,  # column operations trigger issues in other alters
            projections=False,  # projection operations have issues when combined with other alters
        ),
        limit=None if self.context.stress else 20,
        kill_stuck_mutations=False,  # KILL may have unsafe side effects
    )


@TestScenario
def columns(self):
    """
    Perform only actions that manipulate columns.
    """

    alter_combinations(
        actions=build_action_list(
            columns=True, part_manipulation=False, ttl=False, indexes=False
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def parts(self):
    """
    Perform only actions that manipulate parts.
    """

    alter_combinations(
        actions=build_action_list(
            columns=False, part_manipulation=True, ttl=False, indexes=False
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def columns_and_indexes(self):
    """
    Perform only actions that manipulate columns and indexes.
    """

    alter_combinations(
        actions=build_action_list(
            columns=True, part_manipulation=False, ttl=False, indexes=True
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def columns_and_indexes_unsafe(self):
    """
    Perform only actions that manipulate columns and indexes, disable related workarounds.
    """
    self.context.workarounds["wide_parts_only"] = False

    alter_combinations(
        actions=build_action_list(
            columns=True, part_manipulation=False, ttl=False, indexes=True
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def columns_and_parts(self):
    """
    Perform only actions that manipulate columns and parts.
    """

    alter_combinations(
        actions=build_action_list(
            columns=True, part_manipulation=True, ttl=False, indexes=False
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def indexes_and_projections(self):
    """
    Perform only actions using indexes and projections.

    Column actions are disabled to avoid mutation timeouts.
    """

    alter_combinations(
        actions=build_action_list(
            columns=False,
            projections=True,
            indexes=True,
        ),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def network_faults(self):
    """
    Perform actions with random network interference.
    """

    alter_combinations(
        actions=build_action_list(),
        limit=None if self.context.stress else 20,
        network_impairment=True,
    )


@TestScenario
def restarts(self):
    """
    Allow restarting nodes randomly. High probability of crashes.
    """

    alter_combinations(
        actions=build_action_list(restarts=True),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def add_remove_replicas(self):
    """
    Allow adding and removing replicas randomly.
    """

    alter_combinations(
        actions=build_action_list(add_remove_replicas=True),
        limit=None if self.context.stress else 20,
    )


@TestScenario
def full_disk(self):
    """
    Allow filling clickhouse and zookeeper disks.
    """

    alter_combinations(
        actions=self.build_action_list(fill_disks=True),
        limit=None if self.context.stress else 20,
        limit_disk_space=True,
    )


@TestFeature
@Name("combinations")
def feature(self):
    """Stress test with many alters."""

    # Workarounds
    self.context.workarounds = {}

    if not self.context.unsafe:
        # https://github.com/ClickHouse/ClickHouse/issues/62459
        self.context.workarounds["disallow_move_partition_to_self"] = (
            check_clickhouse_version("<24.3")(self)
        )

        # https://github.com/ClickHouse/ClickHouse/issues/63545#issuecomment-2105013462
        self.context.workarounds["wide_parts_only"] = True

        # SELECT count() fails sporadically when column and part manipulation are combined
        # Use SELECT count(key) instead when we actually need to know the row count
        self.context.workarounds["use_key_column_for_count"] = True

    with Given("I have S3 disks configured"):
        disk_config()

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, tags=["long", "combinatoric"])
