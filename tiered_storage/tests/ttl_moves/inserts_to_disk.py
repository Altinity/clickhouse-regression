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
@Name("inserts to disk")
@Requirements()
@Examples(
    "name engine",
    [
        ("mt_test_inserts_to_disk", "MergeTree()"),
        (
            "replicated_mt_test_inserts_to_disk",
            "ReplicatedMergeTree('/clickhouse/replicated_test_inserts_to_disk', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when a TTL expression is set to a DateTime column
    without any interval offset then the inserted parts are immediately
    moved to the specified disk if the DateTime column value
    is less than the TLL expression and are not
    moved when the value is greater.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        for positive in (True, False):
            with When(
                f"I check that inserted parts should {'be' if positive else 'not be'} moved"
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
                        with When("I insert data"):
                            data = []  # 10MB in total
                            now = time.time()
                            for i in range(10):
                                s1 = get_random_string(
                                    cluster, 1024 * 1024, steps=False
                                )  # 1MB
                                d1 = now - 1 if i > 0 or positive else now + 300
                                data.append(f"('{s1}', toDateTime({d1}))")
                            values = ",".join(data)
                            node.query(f"INSERT INTO {name} (s1, d1) VALUES {values}")

                        with And("I get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(
                                f"I check parts {'were' if positive else 'were not'} moved"
                            ):
                                assert set(used_disks) == (
                                    {"external" if positive else "jbod1"}
                                ), error()

                        with Then(
                            "I also double check that number of rows did not change"
                        ):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "10", error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
