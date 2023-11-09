#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
import random

from tiered_storage.tests.common import get_random_string
from tiered_storage.tests.common import get_used_disks_for_table
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_004_BackgroundMergeProcess_MergingParts("1.0"),
    RQ_SRS_004_BackgroundMergeProcess_CheckStoragePolicy("1.0"),
    RQ_SRS_004_BackgroundMergeProcess_ManualTrigger("1.0"),
)
@Name("simple replication and moves")
def scenario(self, cluster, nodes=None):
    """Check simple replication and moves."""
    if nodes is None:
        nodes = cluster.nodes["clickhouse"][:2]

    with Given(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    try:
        with When("I create replicated table on each node"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE replicated_table_for_moves (
                        s1 String
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/replicated_table_for_moves', '{i + 1}')
                    ORDER BY tuple()
                    SETTINGS storage_policy='moving_jbod_with_external', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
                """
                )

        def insert(num):
            with When(f"I insert {num} values to randomly selected node"):
                for i in range(num):
                    node = random.choice(nodes)
                    data = []  # 1MB in total
                    for i in range(2):
                        data.append(
                            get_random_string(
                                cluster, 512 * 1024, steps=False, timeout=120
                            )
                        )  # 500KB value
                    values = ",".join(["('" + x + "')" for x in data])
                    node.query(
                        f"INSERT INTO replicated_table_for_moves VALUES {values}",
                        steps=False,
                        timeout=120,
                    )

        def optimize(num):
            with When(
                f"I perform optimize table {num} times on randomly selected node"
            ):
                for i in range(num):
                    node = random.choice(nodes)
                    node.query(
                        "OPTIMIZE TABLE replicated_table_for_moves FINAL",
                        steps=False,
                        timeout=120,
                    )

        with When("in parallel I perform alter insert and optimize"):
            with Pool(60) as p:
                tasks = []
                tasks.append(p.submit(insert, (20,)))
                tasks.append(p.submit(optimize, (20,)))

                for task in tasks:
                    task.result(timeout=300)

        with When("I do system sync replica on each node"):
            for node in nodes:
                node.query(
                    "SYSTEM SYNC REPLICA replicated_table_for_moves", timeout=120
                )

        with When("I check number of rows on each node"):
            for node in nodes:
                with By(f"checking on {node.name}"):
                    r = node.query(
                        "SELECT COUNT() FROM replicated_table_for_moves"
                    ).output.strip()
                with Then("count should be 40"):
                    assert r == "40", error()

        with When("I prepare 1MB of data 2 rows 512kB each"):
            data = []
            for i in range(2):
                data.append(get_random_string(cluster, 512 * 1024, steps=False))

        with And("I wait until old parts will be deleted"):
            time.sleep(3)

        try:
            with And("I stop merges on each node"):
                for node in nodes:
                    node.query("SYSTEM STOP MERGES")

            with When("I insert data on each node"):
                values = ",".join(["('" + x + "')" for x in data])
                for node in nodes:
                    node.query(
                        f"INSERT INTO replicated_table_for_moves VALUES {values}"
                    )

            with And("wait for moves to completed"):
                time.sleep(30)

            with And(
                "I check used disks on each node to eventually match the expected"
            ):
                for attempt in retries(timeout=360, delay=5):
                    with attempt:
                        with By("getting used disks on each node"):
                            disks = {}
                            for node in nodes:
                                disks[node.name] = get_used_disks_for_table(
                                    node, "replicated_table_for_moves"
                                )

                        with Then(
                            "Nodes should be using 'external' disk",
                            format_name=False,
                        ):
                            for node in nodes:
                                assert "external" in set(disks[node.name]), error()
        finally:
            with Finally("I re-start merges on each node"):
                for node in nodes:
                    node.query("SYSTEM START MERGES")

    finally:
        with Finally("I drop the table on each node if exists"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS replicated_table_for_moves SYNC")
