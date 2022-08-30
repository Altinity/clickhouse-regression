#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
import threading
from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("moves to volume")
@Requirements()
@Examples(
    "name engine",
    [
        ("mt_test_moves_to_volume", "MergeTree()"),
        (
            "replicated_mt_test_moves_to_volume",
            "ReplicatedMergeTree('/clickhouse/replicated_test_moves_to_volume', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when a TTL expression is set to a DateTime column
    without any interval offset then the parts are
    moved to the specified volume after the TTL expression is triggered and are not
    moved when the TTL expression hasn't reached the triggering point.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        for positive in (True, False):
            with When(
                f"I check that parts should {'be' if positive else 'not be'} moved"
            ):
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
                        now = time.time()
                        wait_expire_1 = 20
                        wait_expire_2 = 10
                        time_1 = now + wait_expire_1
                        time_2 = now + wait_expire_1 + wait_expire_2

                        wait_expire_1_thread = threading.Thread(
                            target=time.sleep, args=(wait_expire_1,)
                        )
                        wait_expire_1_thread.start()

                        with When("I insert data"):
                            for p in range(2):
                                data = []  # 10MB in total
                                for i in range(5):
                                    s1 = get_random_string(
                                        cluster, 1024 * 1024, steps=False
                                    )  # 1MB
                                    d1 = time_1 if i > 0 or positive else time_2
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

                        with And(
                            f"I wait until TTL expression {'triggers' if positive else 'is close to triggering'}"
                        ):
                            wait_expire_1_thread.join()
                            time.sleep(wait_expire_2 / 2)

                        with And("I then again get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(
                                f"parts {'should' if positive else 'should not'} have been moved"
                            ):
                                assert set(used_disks) == (
                                    {"external"} if positive else {"jbod1", "jbod2"}
                                ), error()

                        with Then("number of rows should match"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "10", error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
