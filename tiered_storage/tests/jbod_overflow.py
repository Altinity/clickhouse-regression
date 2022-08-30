#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time

from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("jbod overflow")
@Examples(
    "name engine",
    [
        ("mt_with_overflow", "MergeTree()"),
        (
            "replicated_mt_with_overflow",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_with_overflow', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when merges are stopped then all small parts
    first go to JBOD disks and large part goes to the external disk.
    After merges are restarted and executed then all parts are moved
    to the external disk.
    """
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='small_jbod_with_external'
                    """
                    )
                try:
                    with And("I stop merges"):
                        node.query("SYSTEM STOP MERGES")

                    with And(
                        "I insert 5MB batch 7 times",
                        description="small jbod size is 40MB",
                    ):
                        for i in range(7):
                            data = []
                            for i in range(5):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name} VALUES {values}")

                    for attempt in retries(timeout=60, delay=5):
                        with attempt:
                            used_disks = get_used_disks_for_table(node, name)

                            with Then("all parts should go to 'jbod1'"):
                                assert all(
                                    disk == "jbod1" for disk in used_disks
                                ), error()

                    with When("I insert 10MB with 10 rows of 1MB each"):
                        data = []
                        for i in range(10):
                            data.append(
                                get_random_string(cluster, 1024 * 1024, steps=False)
                            )
                        values = ",".join(["('" + x + "')" for x in data])
                        node.query(f"INSERT INTO {name} VALUES {values}")

                    used_disks = get_used_disks_for_table(node, name)

                    with Then("the last 10MB part should go to 'external'"):
                        assert used_disks[-1] == "external", error()

                    with When("I start merges"):
                        node.query("SYSTEM START MERGES")
                        with And("sleep 1 sec"):
                            time.sleep(1)

                    with And("I execute optimize table final"):
                        node.query(f"OPTIMIZE TABLE {name} FINAL")
                        with And("sleep 10 sec"):
                            time.sleep(10)

                    with And("I read disk_name from system.parts"):
                        disks_for_merges = (
                            node.query(
                                f"SELECT disk_name FROM system.parts WHERE table == '{name}'"
                                " AND level >= 1 and active = 1 ORDER BY modification_time"
                            )
                            .output.strip()
                            .split("\n")
                        )

                    with Then("all parts should be on 'external' disk"):
                        assert all(
                            disk == "external" for disk in disks_for_merges
                        ), error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
