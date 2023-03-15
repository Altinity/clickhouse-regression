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
@Name("moves to volume concurrent read")
@Requirements(
    RQ_SRS_004_AutomaticPartMovementInTheBackground_NoEffectOnQuerying("1.0"),
    RQ_SRS_004_TTLExpressions_Application_NoEffectOnQuerying("1.0"),
)
@Examples(
    "name engine",
    [
        ("mt_test_moves_to_volume_concurrent_read", "MergeTree()"),
        (
            "replicated_mt_test_moves_to_volume_concurrent_read",
            "ReplicatedMergeTree('/clickhouse/replicated_test_moves_to_volume_concurrent_read', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that during active TTL moves to volume
    concurrent reads are not affected.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with When(f"I check that parts should be moved"):
            with Given(f"table name='{name}', engine='{engine}'"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        p1 Int64,
                        s1 String,
                        d1 DateTime
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    PARTITION BY p1
                    TTL d1 TO VOLUME 'external'
                    SETTINGS storage_policy='jbods_with_external'
                """
                )
                try:
                    wait_expire = 20

                    with When("I insert data", description="10MB in total"):
                        for p in range(10):
                            data = []
                            for i in range(1):
                                s1 = get_random_string(
                                    cluster, 1024 * 1024, steps=False
                                )  # 1MB
                                d1 = time.time() + wait_expire
                                p1 = p
                                data.append(f"({p1}, '{s1}', toDateTime({d1}))")
                                values = ",".join(data)
                            node.query(
                                f"INSERT INTO {name} (p1, s1, d1) VALUES {values}"
                            )

                    with And("I get used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        with Then(f"check that no parts were moved"):
                            assert set(used_disks) == {"jbod1", "jbod2"}, error()

                    def select_count():
                        with When(f"I perform select count for 20 sec"):
                            with Then("result should always be 10"):
                                start_time = time.time()
                                while time.time() - start_time < 20:
                                    r = node.query(
                                        f"SELECT count() FROM {name}",
                                        steps=False,
                                        timeout=60,
                                    ).output.strip()
                                    assert r == "10", error()

                    def select_slow_count():
                        with When("I perform slow query for 20 sec"):
                            with Then("result should always be 10"):
                                start_time = time.time()
                                while time.time() - start_time < 20:
                                    r = node.query(
                                        f"SELECT sleep(3), sleep(2), sleep(1), count() FROM {name}",
                                        steps=False,
                                        timeout=60,
                                    ).output.strip()
                                    assert r == "0\t0\t0\t10", error()

                    with And("in parallel I perform select count"):
                        with Pool(15) as p:
                            tasks = []
                            for i in range(5):
                                tasks.append(p.submit(select_count))
                                tasks.append(p.submit(select_count))
                                tasks.append(p.submit(select_slow_count))

                            for task in tasks:
                                task.result(timeout=60)
                    
                    for retry in retries(timeout=60):
                        with retry:
                            with When("I then again get used disks for the table"):
                                used_disks = get_used_disks_for_table(node, name)
                                with Then(f"parts should have been moved"):
                                    assert set(used_disks) == ({"external"}), error()

                    with Then("number of rows should match"):
                        r = node.query(f"SELECT count() FROM {name}").output.strip()
                        assert r == "10", error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
