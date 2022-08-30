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
@Name("alter with merge")
@Requirements(RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable("1.0"))
@Examples(
    "name engine",
    [
        ("mt_test_alter_with_merge", "MergeTree()"),
        # ("replicated_mt_test_alter_with_merge", "ReplicatedMergeTree('/clickhouse/replicated_test_alter_with_merge', '1')"),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that TTL expressions are re-evaluated for
    existing parts after ALTER command changes TTL expressions
    and parts are merged.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        for positive in (True, False):
            with Example(
                f"table name='{name}', engine='{engine}', positive={positive}"
            ):
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
                            TTL d1 + INTERVAL 3000 SECOND TO DISK 'jbod2',
                                d1 + INTERVAL 6000 SECOND TO VOLUME 'external'
                            SETTINGS storage_policy='jbods_with_external', merge_with_ttl_timeout=0
                        """
                        )
                        try:
                            with When("I disallow moves and merges"):
                                node.query("SYSTEM STOP MOVES")
                                node.query("SYSTEM STOP MERGES")

                            with When("I insert data"):
                                for p in range(3):
                                    data = []  # 2MB in total
                                    now = time.time()
                                    for i in range(2):
                                        s1 = get_random_string(
                                            cluster, 1024 * 1024, steps=False
                                        )  # 1MB
                                        d1 = now - 1 if positive else now + 300
                                        note(f"now is {now} and d1 is {d1}")
                                        data.append(f"('{s1}', toDateTime({d1}))")
                                    values = ",".join(data)
                                    node.query(
                                        f"INSERT INTO {name} (s1, d1) VALUES {values}"
                                    )

                            with And("I get used disks for the table"):
                                used_disks = get_used_disks_for_table(node, name)
                                with Then(f"parts have been placed using round-robin"):
                                    assert set(used_disks) == {
                                        "jbod1",
                                        "jbod2",
                                    }, error()

                            with Then("number of rows should match"):
                                r = node.query(
                                    f"SELECT count() FROM {name}"
                                ).output.strip()
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

                            with When("I restart moves and merges"):
                                node.query("SYSTEM START MOVES")
                                node.query("SYSTEM START MERGES")

                            with And("I optimize table to force merge"):
                                node.query(f"OPTIMIZE TABLE {name}")

                            with And("I wait for merge to complete"):
                                time.sleep(1)

                            with And("I get number of active parts"):
                                active = node.query(
                                    f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                                ).output.strip()
                                with Then("active parts should be 1"):
                                    assert "1" == active

                            with And("I wait until second TTL expression triggers"):
                                time.sleep(6)

                                with When("I get used disks for the table"):
                                    used_disks = get_used_disks_for_table(node, name)
                                    with Then(
                                        f"parts {'should' if positive else 'should not'} have been moved"
                                    ):
                                        assert set(used_disks) in (
                                            ({"external"},)
                                            if positive
                                            else ({"jbod1"}, {"jbod2"})
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
                                    assert r == ("0" if positive else "6"), error()

                        finally:
                            with Finally("I drop the table"):
                                node.query(f"DROP TABLE IF EXISTS {name} SYNC")
