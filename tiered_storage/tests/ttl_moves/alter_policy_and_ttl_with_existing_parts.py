#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import datetime
from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("alter policy and ttl with existing parts")
@Requirements(RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_alter_policy_and_ttl_with_existing_parts", "MergeTree()"),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that TTL expressions are evaluated for
    existing parts after ALTER command changes TTL expressions
    that contains reference to new volume after changing
    storage policy.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        for positive in (True, False):
            with When(
                f"I check that existing parts should {'be' if positive else 'not be'} moved"
            ):
                with Given(f"table name='{name}', engine='{engine}'"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            d1 Date,
                            t1 DateTime,
                            s1 String
                        ) ENGINE = {engine}
                        PARTITION BY d1
                        ORDER BY t1
                        SETTINGS storage_policy='jbods', merge_with_ttl_timeout=0
                    """
                    )
                    try:
                        with When("I create 60 partitions with one for each day"):
                            now = datetime.datetime.now()
                            s1 = get_random_string(cluster, 1024, steps=False)  # 1MB
                            for p in range(60):
                                data = []  # 2MB in total
                                d1 = (
                                    now - datetime.timedelta(days=p)
                                    if positive
                                    else now + datetime.timedelta(days=p)
                                ).timestamp()
                                t1 = d1
                                data.append(f"(toDate({d1}), toDateTime({t1}), '{s1}')")
                                values = ",".join(data)
                                node.query(
                                    f"INSERT INTO {name} (d1, t1, s1) VALUES {values}"
                                )

                        with And("I get used disks for the table"):
                            used_disks = set(get_used_disks_for_table(node, name))
                            with Then(f"parts have been placed using round-robin"):
                                assert used_disks == {"jbod1", "jbod2"}, error()

                        with Then("number of rows should match"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "60", error()

                        with When(
                            "I change storage policy to include new external volume"
                        ):
                            node.query(
                                f"ALTER TABLE {name} MODIFY SETTING storage_policy='jbods_with_external'"
                            )

                        with And(
                            "I update table settings to include TTL to move old data"
                        ):
                            node.query(
                                f"ALTER TABLE {name} MODIFY TTL d1 + INTERVAL 1 MONTH TO DISK 'external'"
                            )

                        with And("I materialize ttl in the whole table"):
                            node.query(
                                f"ALTER TABLE {name} MATERIALIZE TTL SETTINGS mutations_sync=2"
                            )

                        with When("run optimize table final to force the move"):
                            node.query(f"OPTIMIZE TABLE {name} FINAL")

                        with And(
                            "I get used disks for the table after table is optimized"
                        ):
                            used_disks = set(get_used_disks_for_table(node, name))
                            with Then(
                                f"parts {'should' if positive else 'should not'} have been moved"
                            ):
                                assert set(used_disks) == (
                                    {"external", "jbod1", "jbod2"}
                                    if positive
                                    else {"jbod1", "jbod2"}
                                ), error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
