#!/usr/bin/env python3
import random
from itertools import combinations, chain

from testflows.core import *
from testflows.combinatorics import CoveringArray

from helpers.common import getuid
from s3.tests.common import s3_table, s3_storage

from vfs.tests.steps import insert_random, replicated_table_cluster
from alter.stress.tests.actions import optimize_random, check_consistency


@TestStep
@Retry(timeout=10, delay=1)
def insert(self, table_name, settings):
    """Insert random data to a table."""
    node = random.choice(self.context.ch_nodes)
    with By(f"inserting rows to {table_name} on {node.name} with settings {settings}"):
        insert_random(node=node, table_name=table_name, settings=settings, rows=5000000)


@TestStep
@Retry(timeout=10, delay=1)
def select(self, table_name, settings=None):
    """Perform select queries on a random node."""
    node = random.choice(self.context.ch_nodes)
    if settings:
        settings = "SETTINGS " + settings
    for _ in range(random.randint(3, 10)):
        with By(f"count rows in {table_name} on {node.name}"):
            node.query(
                f"SELECT count() FROM {table_name} {settings} FORMAT TabSeparated"
            )


def combinations_all_lengths(items, min_size=1, max_size=None):
    """Get combinations for all possible combination sizes, up to a given limit."""
    if max_size is None:
        max_size = len(items)
    return chain(*[combinations(items, i) for i in range(min_size, max_size + 1)])


@TestOutline(Combination)
def check_setting_combination(
    self, table_setting, select_setting, insert_setting, storage_setting
):
    """Perform concurrent inserts and selects with a combination of settings."""

    if storage_setting is not None:
        with Given(f"storage with settings {storage_setting}"):
            storage_setting = storage_setting.split("=")
            disks = {
                "external": {
                    storage_setting[0]: storage_setting[1],
                }
            }
            s3_storage(disks=disks, restart=False, config_file="test_settings.xml")

    with Given("a table"):
        _, table_name = replicated_table_cluster(
            storage_policy="external",
            exitcode=0,
            settings=table_setting,
        )

    with And("some inserted data"):
        insert(table_name=table_name, settings=insert_setting)

    When(
        f"I INSERT in parallel",
        test=insert,
        parallel=True,
        flags=TE,
    )(table_name=table_name, settings=insert_setting)
    When(
        f"I SELECT in parallel",
        test=select,
        parallel=True,
        flags=TE,
    )(table_name=table_name, settings=select_setting)
    When(
        f"I OPTIMIZE {table_name}",
        test=optimize_random,
        parallel=True,
        flags=TE,
    )(table_name=table_name)

    join()

    with Then("I check that the replicas are consistent", flags=TE):
        check_consistency(tables=[table_name])


@TestScenario
@Tags("long", "combinatoric")
def setting_combinations(self):
    """Perform concurrent inserts and selects with various settings."""
    settings = {
        "table_setting": (
            None,
            "remote_fs_execute_merges_on_single_replica_time_threshold=0",
            "zero_copy_concurrent_part_removal_max_split_times=2",
            "zero_copy_concurrent_part_removal_max_postpone_ratio=0.1",
            "zero_copy_merge_mutation_min_parts_size_sleep_before_lock=0",
        ),
        "select_setting": (
            None,
            "merge_tree_min_rows_for_concurrent_read_for_remote_filesystem=0",
            "merge_tree_min_bytes_for_concurrent_read_for_remote_filesystem=0",
        ),
        "insert_setting": (
            None,
            *[
                ",".join(c)
                for c in combinations_all_lengths(
                    [
                        "s3_truncate_on_insert=1",
                        "s3_create_new_file_on_insert=1",
                        "s3_skip_empty_files=1",
                        f"s3_max_single_part_upload_size={int(64*1024)}",
                    ],
                    min_size=2,
                    max_size=3,
                )
            ],
        ),
        "storage_setting": (
            None,
            "remote_fs_read_backoff_threshold=0",
            "remote_fs_read_backoff_max_tries=0",
        ),
    }

    covering_array_strength = len(settings) if self.context.stress else 2
    for config in CoveringArray(settings, strength=covering_array_strength):
        title = ",".join([f"{k}={v}" for k, v in config.items()])
        Combination(title, test=check_setting_combination)(**config)


@TestFeature
@Name("settings")
def feature(self, uri):
    """Test interactions between settings."""

    self.context.uri = uri
    cluster = self.context.cluster
    self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]

    with Given("I have two S3 disks configured"):
        disks = {
            "external": {
                "type": "s3",
                "endpoint": self.context.uri,
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
        }

    with And(
        """I have a storage policy configured to use the S3 disk and a tiered
             storage policy using both S3 disks"""
    ):
        policies = {"external": {"volumes": {"external": {"disk": "external"}}}}

    with Given("I have S3 disks configured"):
        s3_storage(disks=disks, policies=policies, restart=True)

    for scenario in loads(current_module(), Scenario):
        scenario()
