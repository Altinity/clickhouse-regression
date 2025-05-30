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
from tiered_storage.requirements import *


@TestOutline(Scenario)
@Name("delete")
@Requirements(RQ_SRS_004_TTLExpressions_Compatibility("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_moves_to_disk", "MergeTree()"),
        (
            "replicated_mt_test_moves_to_disk",
            "ReplicatedMergeTree('/clickhouse/replicated_test_moves_to_disk', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, name, engine):
    """Check that delete operation using TTL expression still works."""
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")

    for positive in (True, False):
        with Check(f"parts should {'be' if positive else 'not be'} deleted"):
            try:
                with Given("table"):
                    node.query(
                        f"""
                            CREATE TABLE {name} (
                                s1 String,
                                d1 DateTime
                            ) ENGINE = {engine}
                            ORDER BY tuple()
                            TTL d1 DELETE
                            SETTINGS storage_policy='small_jbod_with_external'
                        """
                    )

                now = time.time()
                wait_expire_1 = 0
                wait_expire_2 = 30
                time_1 = now + wait_expire_1
                time_2 = now + wait_expire_1 + wait_expire_2

                wait_expire_1_thread = threading.Thread(
                    target=time.sleep, args=(wait_expire_1,)
                )
                wait_expire_1_thread.start()

                with When("I insert data"):
                    data = []  # 10MB in total
                    for i in range(10):
                        s1 = get_random_string(cluster, 1024 * 1024, steps=False)  # 1MB
                        d1 = time_1 if i > 0 or positive else time_2
                        data.append(f"('{s1}', toDateTime({d1}))")
                    values = ",".join(data)
                    node.query(f"INSERT INTO {name} (s1, d1) VALUES {values}")

                for retry in retries(count=5):
                    with retry:
                        with When("I get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            assert set(used_disks) == {"jbod1"}, error()

                with When(
                    f"I wait until TTL expression {'triggers' if positive else 'is close to triggering'}"
                ):
                    wait_expire_1_thread.join()
                    time.sleep(wait_expire_2 / 2)

                with And("I then again get used disks for the table"):
                    used_disks = get_used_disks_for_table(node, name)
                    expected_disks = (
                        {""}
                        if positive and not engine.startswith("Replicated")
                        else {"jbod1"}
                    )
                    assert set(used_disks) == expected_disks, error()

                with Then(f"number of rows should be {'0' if positive else '1'}"):
                    for attempt in retries(timeout=30, delay=5):
                        with attempt:
                            r = node.query(
                                f"SELECT count() FROM {name} FORMAT TabSeparated"
                            ).output.strip()
                            assert r == ("0" if positive else "1"), error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
