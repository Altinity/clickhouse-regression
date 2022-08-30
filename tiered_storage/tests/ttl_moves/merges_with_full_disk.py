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


@TestScenario
@Name("merges with full disk")
@Requirements(RQ_SRS_004_TTLExpressions_FaultTolerance_NoSpace("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_merges_with_full_disk", "MergeTree()"),
        (
            "replicated_mt_test_merges_with_full_disk",
            "ReplicatedMergeTree('/clickhouse/replicated_test_merges_with_full_disk', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when no space is available then the merge operation
    still completes but move is not performed if the TTL expression
    is triggered. However, once the disk space is available
    the move eventually occurs if TTL expression triggers
    or does not occur if it didn't.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        name_temp = name + "_temp"
        for positive in (True, False):
            with When(
                f"I check that parts should {'be' if positive else 'not be'} moved"
            ):
                with Given(
                    f"temporary table name='{name}', engine='MergeTree()'",
                    description="with storage policy that includes only the second disk",
                ):
                    node.query(
                        f"""
                        CREATE TABLE {name_temp} (
                            s1 String
                        ) ENGINE = MergeTree()
                        ORDER BY tuple()
                        SETTINGS storage_policy='only_jbod2'
                    """
                    )
                    try:
                        with When("I check free space on the second disk"):
                            node.command("df -h /jbod2")

                        with When("I fill up the second disk"):
                            data = []  # 25MB in total
                            for i in range(25):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )  # 1MB row
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name_temp} VALUES {values}")

                        with And("I get used disks for the temporary table"):
                            used_disks = get_used_disks_for_table(node, name_temp)
                            with Then(f"check that all parts are on the second disk"):
                                assert set(used_disks) == {"jbod2"}, error()

                        with Given(
                            f"second table name '{name}', engine='{engine}'",
                            description=(
                                "with storage policy that includes first and second disks"
                                "and TTL expression to move parts to the second disk"
                            ),
                        ):
                            node.query(
                                f"""
                                CREATE TABLE {name} (
                                    s1 String,
                                    d1 DateTime
                                ) ENGINE = {engine}
                                ORDER BY tuple()
                                TTL d1 TO DISK 'jbod2'
                                SETTINGS storage_policy='jbod1_with_jbod2'
                            """
                            )
                            try:
                                wait_expire_1 = 10
                                time_1 = (
                                    time.time()
                                    + wait_expire_1
                                    + (0 if positive else 300)
                                )

                                wait_expire_1_thread = threading.Thread(
                                    target=time.sleep, args=(wait_expire_1,)
                                )
                                wait_expire_1_thread.start()

                                with When(
                                    "I insert data into the second table",
                                    description="two parts with 6 rows 1MB each",
                                ):
                                    for _ in range(2):
                                        data = []  # 6MB in total
                                        for i in range(6):
                                            s1 = get_random_string(
                                                cluster, 1024 * 1024, steps=False
                                            )  # 1MB
                                            d1 = time_1
                                            data.append(f"('{s1}', toDateTime({d1}))")
                                        values = ",".join(data)
                                        node.query(
                                            f"INSERT INTO {name} (s1, d1) VALUES {values}"
                                        )

                                with And("I get used disks for the second table"):
                                    used_disks = get_used_disks_for_table(node, name)
                                    with Then(
                                        f"check that all parts are on the first disk"
                                    ):
                                        assert set(used_disks) == {"jbod1"}, error()

                                with And("I get number of active parts"):
                                    active = node.query(
                                        f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                                    ).output.strip()
                                    with Then("active parts should be 2"):
                                        assert "2" == active

                                with And("I wait for TTL expression to be triggered"):
                                    wait_expire_1_thread.join()

                                with When("I optimize table to trigger merge"):
                                    node.query(f"OPTIMIZE TABLE {name}")

                                with And("wait for 1 sec for merge to complete"):
                                    time.sleep(1)

                                with And(
                                    "I get used disks for the second table after merge"
                                ):
                                    used_disks = get_used_disks_for_table(node, name)
                                    with Then(
                                        f"I check parts were not moved because second disk is full"
                                    ):
                                        assert set(used_disks) == {"jbod1"}, error()

                                with And("I get number of active parts after merge"):
                                    active = node.query(
                                        f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                                    ).output.strip()
                                    with Then("active parts should be 1"):
                                        assert "1" == active

                                with Then(
                                    "I also double check that number of rows did not change"
                                ):
                                    r = node.query(
                                        f"SELECT count() FROM {name}"
                                    ).output.strip()
                                    assert r == "12", error()

                                with And(
                                    "then I drop temporary table to free up second disk"
                                ):
                                    node.query(f"DROP TABLE {name_temp} SYNC")

                                with And("I sleep for 2 sec"):
                                    time.sleep(2)

                                with And(
                                    "I get used disks for the second table after the sleep"
                                ):
                                    used_disks = get_used_disks_for_table(node, name)
                                    with Then(
                                        f"I check parts {'were' if positive else 'were not'} moved"
                                    ):
                                        assert set(used_disks) == (
                                            {"jbod2"} if positive else {"jbod1"}
                                        ), error()

                                with Then(
                                    "I again check that number of rows did not change"
                                ):
                                    r = node.query(
                                        f"SELECT count() FROM {name}"
                                    ).output.strip()
                                    assert r == "12", error()
                            finally:
                                with Finally("I drop second table"):
                                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
                    finally:
                        with Finally("I drop the temporary table"):
                            node.query(f"DROP TABLE IF EXISTS {name_temp} SYNC")
