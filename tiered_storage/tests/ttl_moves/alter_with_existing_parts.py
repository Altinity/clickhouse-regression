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
@Name("alter with existing parts")
@Requirements(RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_alter_with_existing_parts", "MergeTree()"),
        # ("replicated_mt_test_alter_with_existing_parts", "ReplicatedMergeTree('/clickhouse/replicated_test_alter_with_existing_parts', '1')"),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that TTL expressions are re-evaluated for
    existing parts after ALTER command changes TTL expressions.
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
                            p1 Int64,
                            s1 String,
                            d1 DateTime
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        PARTITION BY p1
                        TTL d1 + INTERVAL 3000 SECOND TO DISK 'jbod2',
                            d1 + INTERVAL 6000 SECOND TO VOLUME 'external'
                        SETTINGS storage_policy='jbods_with_external', merge_with_ttl_timeout=0
                    """
                    )
                    try:
                        with When("I insert data"):
                            for p in range(3):
                                data = []  # 2MB in total
                                now = time.time()
                                for i in range(2):
                                    p1 = p
                                    s1 = get_random_string(
                                        cluster, 1024 * 1024, steps=False
                                    )  # 1MB
                                    d1 = now - 1 if i > 0 or positive else now + 300
                                    data.append(f"({p1}, '{s1}', toDateTime({d1}))")
                                values = ",".join(data)
                                node.query(
                                    f"INSERT INTO {name} (p1, s1, d1) VALUES {values}"
                                )

                        with And("I get used disks for the table"):
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(f"parts have been placed using round-robin"):
                                assert set(used_disks) == {"jbod1", "jbod2"}, error()

                        with Then("number of rows should match"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "6", error()

                        with When("I change TTL expressions using ALTER TABLE"):
                            node.query(
                                f"""
                                ALTER TABLE {name} MODIFY
                                TTL d1 + INTERVAL 0 SECOND TO DISK 'jbod2',
                                    d1 + INTERVAL 5 SECOND TO VOLUME 'external',
                                    d1 + INTERVAL 10 SECOND DELETE
                            """
                            )

                        with And("I materialize ttl in the whole table"):
                            node.query(
                                f"ALTER TABLE {name} MATERIALIZE TTL SETTINGS mutations_sync=2"
                            )

                        with And("I wait until second TTL expression triggers"):
                            time.sleep(5)

                            with When("I get used disks for the table"):
                                used_disks = get_used_disks_for_table(node, name)
                                with Then(
                                    f"parts {'should' if positive else 'should not'} have been moved"
                                ):
                                    assert set(used_disks) == (
                                        {"external"} if positive else {"jbod1", "jbod2"}
                                    ), error()

                            with Then("again number of rows should match"):
                                r = node.query(
                                    f"SELECT count() FROM {name}"
                                ).output.strip()
                                assert r == "6", error()

                        with And("I wait until TTL expression to delete triggers"):
                            time.sleep(5)

                            with When(
                                "I ran optimize final to make sure delete completes"
                            ):
                                node.query(f"OPTIMIZE TABLE {name} FINAL")

                            with Then(
                                f"number of rows should {'be 0' if positive else 'match'}"
                            ):
                                r = node.query(
                                    f"SELECT count() FROM {name}"
                                ).output.strip()
                                assert r == ("0" if positive else "3"), error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
