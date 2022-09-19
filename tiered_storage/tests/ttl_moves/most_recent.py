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
from tiered_storage.requirements import *


@TestScenario
@Name("most recent")
@Requirements(RQ_SRS_004_TTLExpressions_Selection("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_inserts_multiple_ttls", "MergeTree()"),
        (
            "replicated_mt_test_inserts_multiple_ttls",
            "ReplicatedMergeTree('/clickhouse/replicated_test_inserts_multiple_ttls', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when multiple TTL expressions are triggered then
    the most recent is used to move the data.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with When(f"I create table name='{name}' with engine='{engine}'"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    p1 Int64,
                    s1 String,
                    d1 DateTime
                ) ENGINE = {engine}
                ORDER BY tuple()
                PARTITION BY p1
                TTL d1 + INTERVAL 30 SECOND TO DISK 'jbod2', 
                    d1 + INTERVAL 60 SECOND TO VOLUME 'external'
                SETTINGS storage_policy='jbods_with_external', merge_with_ttl_timeout=0
            """
            )
            try:
                with When("I disallow moves"):
                    node.query("SYSTEM STOP MOVES")

                with And("I insert data"):
                    for p in range(3):
                        data = []  # 2MB in total
                        now = time.time()
                        for i in range(2):
                            s1 = get_random_string(
                                cluster, 1024 * 1024, steps=False
                            )  # 1MB
                            data.append(f"({p}, '{s1}', toDateTime({now - 1}))")
                        values = ",".join(data)
                        node.query(f"INSERT INTO {name} (p1, s1, d1) VALUES {values}")

                with And("I get used disks for the table"):
                    used_disks = get_used_disks_for_table(node, name)
                    with Then(
                        f"parts should have been placed according to the round-robin"
                    ):
                        assert set(used_disks) == {"jbod1", "jbod2"}, error()

                with And("I wait until both TTL expressions would trigger"):
                    time.sleep(30)

                with And("I get used disks for the table before I resume moves"):
                    used_disks = get_used_disks_for_table(node, name)
                    with Then(f"parts should remain according to the round-robin"):
                        assert set(used_disks) == {"jbod1", "jbod2"}, error()

                with And("I resume moves"):
                    node.query(f"SYSTEM START MOVES {name}")

                with And("I sleep for 40 sec to allow moves to complete"):
                    time.sleep(40)

                for retry in retries(count=5, delay=1):
                    with retry:
                        with And("I again get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(
                                f"parts should have been moved according to the most recent TTL expression"
                            ):
                                assert set(used_disks) == {"external"}, error()

                        with Then("number of rows should match"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "6", error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
