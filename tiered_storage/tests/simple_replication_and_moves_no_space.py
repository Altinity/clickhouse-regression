#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time

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
@Name("simple replication and moves no space")
def scenario(self, cluster, nodes=None):
    """Check that simple replication and moves do not
    misbehave when one of the nodes does not have space on the
    destination disk.
    """
    name = "replicated_table_for_moves_no_space"

    if nodes is None:
        nodes = cluster.nodes["clickhouse"][:2]

    with Given(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    try:
        with When("I create replicated table on each node"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        s1 String
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/{name}', '{i + 1}')
                    ORDER BY tuple()
                    SETTINGS storage_policy='moving_jbod_with_external', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
                """
                )

        with And("I check who is leader"):
            for i, node in enumerate(nodes):
                is_leader = node.query(
                    f"SELECT is_leader FROM system.replicas WHERE table = '{name}'"
                ).output.strip()
                if is_leader == "1":
                    leader = i
                    note(f"leader is node {i}")

        with And("I make the leader to be the first node"):
            leader = nodes.pop(leader)
            nodes.insert(0, leader)

        def insert(num):
            with When(f"I insert {num} values into leader node"):
                for i in range(num):
                    node = nodes[0]
                    data = []  # 1MB in total
                    for i in range(2):
                        data.append(
                            get_random_string(
                                cluster, 512 * 1024, steps=False, timeout=120
                            )
                        )  # 500KB value
                    values = ",".join(["('" + x + "')" for x in data])
                    node.query(
                        f"INSERT INTO {name} VALUES {values}", steps=False, timeout=120
                    )

        def optimize(num):
            with When(f"I perform optimize table {num} times on the leader node"):
                for i in range(num):
                    node = nodes[0]
                    node.query(f"OPTIMIZE TABLE {name} FINAL", steps=False, timeout=300)
                    time.sleep(0.1)

        def fillup_disk(num):
            with When(
                "I fill up non leader node external volume",
                description="only 5MB of free space left",
            ):
                for i in range(num):
                    nodes[1].command(
                        "cat /dev/urandom | head -c 204472320 > /external/dummy",
                        steps=False,
                        timeout=120,
                    )
                    nodes[1].command("df -h /external", steps=False, timeout=120)
                    time.sleep(0.4)
                    nodes[1].command("rm -rf /exernal/dummy", steps=False, timeout=120)

        with When(
            "in parallel I perform insert and optimize on the leader and fill up and free disk on the replica"
        ):
            with Pool(60) as p:
                tasks = []
                tasks.append(p.submit(insert, (20,)))
                tasks.append(p.submit(optimize, (20,)))
                tasks.append(p.submit(fillup_disk, (10,)))

                for task in tasks:
                    task.result(timeout=600)

        with When("I do system sync replica on each node"):
            for node in nodes:
                node.query(f"SYSTEM SYNC REPLICA {name}", timeout=120)

        with When("I check number of rows on each node"):
            for node in nodes:
                with And(f"I check on {node.name}"):
                    r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
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
                    node.query(f"INSERT INTO {name} VALUES {values}")

            with And("wait for moves to completed"):
                time.sleep(3)

            with And(
                "I check used disks on each node to eventually match the expected"
            ):
                for attempt in retries(timeout=300, delay=5):
                    with attempt:
                        with By("getting used disks on each node"):
                            disks = {}
                            for node in nodes:
                                disks[node.name] = get_used_disks_for_table(node, name)

                        expected_disks = {"jbod1", "external"}
                        with Then(f"on each node disks should be {expected_disks}"):
                            for node in nodes:
                                assert set(disks[node.name]) == expected_disks, error()
        finally:
            with Finally("I restart merges on each node"):
                for node in nodes:
                    node.query("SYSTEM START MERGES")
    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query(f"DROP TABLE IF EXISTS {name} SYNC", timeout=30)
