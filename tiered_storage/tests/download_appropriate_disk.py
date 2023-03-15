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
from testflows.core import TestScenario, Name, Requirements, retries
from testflows.core import Given, When, And, Then, Finally
from testflows.asserts import error

from tiered_storage.requirements import *


@TestScenario
@Name("download appropriate disk")
@Requirements(RQ_SRS_004_StoragePolicy_ReplicatedTable_DownloadedPartPlacement("1.0"))
def scenario(self, cluster, nodes=None):
    """Check that insert into one node of the two-node replicated cluster
    results in data storage to the correct disk once the
    other node syncs up.
    """
    if nodes is None:
        nodes = cluster.nodes["clickhouse"][:2]

    with Given(f"cluster nodes {nodes}"):
        nodes = [cluster.node(name) for name in nodes]

    try:
        with When("I create replicated table on each node"):
            for i, node in enumerate(nodes):
                node.query(
                    f"""
                    CREATE TABLE replicated_table_for_download (
                        s1 String
                    ) ENGINE = ReplicatedMergeTree('/clickhouse/replicated_table_for_download', '{i + 1}')
                    ORDER BY tuple()
                    SETTINGS storage_policy='moving_jbod_with_external', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
                """
                )

        with When("I insert 50MB of data using 50 rows 1MB each on the first node"):
            data = []
            for i in range(50):
                data.append(get_random_string(cluster, 1024 * 1024))
            values = ",".join(["('" + x + "')" for x in data])
            nodes[0].query(f"INSERT INTO replicated_table_for_download VALUES {values}")

        with And("I sync the other replica"):
            for _ in range(10):
                try:
                    nodes[-1].query("SYSTEM SYNC REPLICA replicated_table_for_download")
                    break
                except:
                    time.sleep(0.5)

        for retry in retries(timeout=60):
            with retry:
                with When("I check the used disk on other replica"):
                    disks = get_used_disks_for_table(
                        nodes[-1], "replicated_table_for_download"
                    )

                expected_disks = {
                    "external",
                }
                with Then(
                    f"the used disk should match {expected_disks}", format_name=False
                ):
                    assert set(disks) == expected_disks, error()

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS replicated_table_for_download SYNC")
