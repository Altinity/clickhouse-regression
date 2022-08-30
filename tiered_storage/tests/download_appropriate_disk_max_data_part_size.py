#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time

from tiered_storage.tests.common import get_used_disks_for_table, get_random_string

from testflows.core import TestScenario, Name, Examples, Requirements
from testflows.core import Given, When, And, By, Then, Finally, current
from testflows.asserts import error

from tiered_storage.requirements import *


@TestScenario
@Name("download appropriate disk max data part size")
@Requirements(
    RQ_SRS_004_StoragePolicy_ReplicatedTable_DownloadedPartPlacement("1.0"),
    RQ_SRS_004_StoragePolicy_Rules_MoveData_MaxPartSize("1.0"),
)
@Examples(
    "name policy",
    [
        (
            "replicated_table_download_appropriate_disk_max_data_part_size",
            "jbods_with_external",
        ),
        (
            "replicated_table_download_appropriate_disk_max_data_part_size_ratio",
            "jbods_with_external_ratio",
        ),
    ],
    "%-38s | %-20s",
)
def scenario(self, cluster, nodes=None):
    """Check that when parts are downloaded from a replica
    they are placed according to the storage policy specified for the table.
    In this test we check that `max_data_part_size` and `max_data_part_size_ratio`
    are properly calculated and parts are placed on the replica according to
    their constraints.
    """
    if nodes is None:
        nodes = cluster.nodes["clickhouse"]

    with Given(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    for example in self.examples:
        name, policy = example

        try:
            with When("I create replicated table on each node"):
                for i, node in enumerate(nodes):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            d1 UInt64,
                            s1 String
                        ) ENGINE = ReplicatedMergeTree('/clickhouse/{name}', '{i + 1}')
                        ORDER BY tuple()
                        SETTINGS storage_policy='{policy}', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
                    """
                    )

            with And("I create 10MB of random string data"):
                data = []
                random_data = get_random_string(cluster, 10 * 1024 * 1024, steps=False)
                with By("splitting it into 10 rows 1 MB each"):
                    for i in range(10):
                        MB = 1024 * 1024
                        data.append(random_data[i * MB : (i * MB) + MB])  # 1MB row

            with And("I insert data into last node"):
                node = nodes[-1]
                values = ",".join([f"({i},'{x}')" for i, x in enumerate(data)])
                node.query(f"INSERT INTO {name} VALUES {values}")

            with And("I do system sync replica on each node"):
                for node in nodes:
                    node.query(f"SYSTEM SYNC REPLICA {name}")

            with And("wait for replication and moves to complete"):
                time.sleep(3)

            with When("I check used disks on each node"):
                for node in nodes:
                    with When(f"on node {node.name}"):
                        used_disks = get_used_disks_for_table(node, name)
                        with Then("number of disk used should be 1"):
                            assert len(used_disks) == 1, error()
                        with Then("disk used should be 'external'"):
                            assert used_disks[0] == "external", error()

            with When("I query replicated table on each node"):
                for node in nodes:
                    with When(f"on node {node.name}"):
                        r = node.query(f"SELECT sum(d1) FROM {name}").output.strip()
                        with Then("the result should match"):
                            assert r == "45", error()

        finally:
            with Finally("I drop the table on each node"):
                for node in nodes:
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
