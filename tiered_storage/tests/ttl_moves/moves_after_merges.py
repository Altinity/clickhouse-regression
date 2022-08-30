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
@Name("moves after merges")
@Requirements()
@Examples(
    "name engine",
    [
        ("mt_test_moves_after_merges", "MergeTree()"),
        (
            "replicated_mt_test_moves_after_merges",
            "ReplicatedMergeTree('/clickhouse/replicated_test_moves_after_merges', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that after merge is completed parts are moved
    according to the TTL expression only if TTL expression is triggered.
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
                            s1 String,
                            d1 DateTime
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        TTL d1 TO DISK 'external'
                        SETTINGS storage_policy='small_jbod_with_external'
                    """
                    )
                    try:
                        now = time.time()
                        wait_expire_1 = 10
                        wait_expire_2 = 10
                        time_1 = now + wait_expire_1
                        time_2 = now + wait_expire_1 + wait_expire_2

                        wait_expire_1_thread = threading.Thread(
                            target=time.sleep, args=(wait_expire_1,)
                        )
                        wait_expire_1_thread.start()

                        with When(
                            "I insert data",
                            description="two parts with 8 rows 1MB each",
                        ):
                            for _ in range(2):
                                data = []  # 8MB in total
                                for i in range(8):
                                    s1 = get_random_string(
                                        cluster, 1024 * 1024, steps=False
                                    )  # 1MB
                                    d1 = time_1 if i > 0 or positive else time_2
                                    data.append(f"('{s1}', toDateTime({d1}))")
                                values = ",".join(data)
                                node.query(
                                    f"INSERT INTO {name} (s1, d1) VALUES {values}"
                                )

                        with And("I optimize table to force merge"):
                            node.query(f"OPTIMIZE TABLE {name}")

                        with And("I wait 1 sec for merge to complete"):
                            time.sleep(1)

                        with And("I get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(f"check that no parts were moved"):
                                assert set(used_disks) == {"jbod1"}, error()

                        with And("I get number of active parts"):
                            active = node.query(
                                f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                            ).output.strip()
                            with Then("active parts should be 1"):
                                assert "1" == active

                        with And(
                            f"I wait until TTL expression {'triggers' if positive else 'is close to triggering'}"
                        ):
                            wait_expire_1_thread.join()
                            time.sleep(wait_expire_2 / 2)

                        with And("get used disks for the table after merge"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(
                                f"parts {'should' if positive else 'should not'} have been moved"
                            ):
                                assert set(used_disks) == (
                                    {"external" if positive else "jbod1"}
                                ), error()

                        with Then("I double check that number of rows did not change"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "16", error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
