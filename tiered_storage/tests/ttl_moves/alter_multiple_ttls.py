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


@TestOutline(Scenario)
@Name("alter multiple ttls")
@Requirements(
    RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable("1.0"),
    RQ_SRS_004_TTLExpressions_AddingToTable_AlterTable_ReplaceExisting("1.0"),
)
@Examples(
    "name engine",
    [
        ("mt_test_alter_multiple_ttls", "MergeTree()"),
        (
            "replicated_mt_test_alter_multiple_ttls",
            "ReplicatedMergeTree('/clickhouse/replicated_test_alter_multiple_ttls', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, name, engine):
    """Check that when multiple TTL expressions are set
    and before any parts are inserted the TTL expressions
    are changed with ALTER command then all old
    TTL expressions are removed and the
    the parts are moved to the specified disk or volume or
    deleted if the new TTL expression is triggered
    and are not moved or deleted when it is not.
    """
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")

    for positive in (True, False):
        with Check(f"inserted parts should {'be' if positive else 'not be'} moved"):
            try:
                with Given("table"):
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

                with When("I straightaway change TTL expressions using ALTER TABLE"):
                    node.query(
                        f"""
                        ALTER TABLE {name} MODIFY
                        TTL d1 + INTERVAL 0 SECOND TO DISK 'jbod2',
                            d1 + INTERVAL 60 SECOND TO VOLUME 'external',
                            d1 + INTERVAL 90 SECOND DELETE
                    """
                    )

                with When("I check table schema"):
                    for attempt in retries(timeout=120, delay=5):
                        with attempt:
                            r = node.query(
                                f"""
                                SHOW CREATE TABLE {name} FORMAT Vertical
                            """
                            ).output.strip()
                            expected = (
                                "TTL d1 + toIntervalSecond(0) TO DISK 'jbod2', "
                                "d1 + toIntervalSecond(60) TO VOLUME 'external', "
                                "d1 + toIntervalSecond(90)"
                            )
                            with Then(
                                "it should contain new TTL expressions",
                                description=expected,
                            ):
                                assert expected in r, error()

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
                        node.query(f"INSERT INTO {name} (p1, s1, d1) VALUES {values}")

                with And("I get used disks for the table"):
                    used_disks = get_used_disks_for_table(node, name)
                    with Then(
                        f"parts {'should' if positive else 'should not'} have been moved"
                    ):
                        assert set(used_disks) == (
                            {"jbod2"} if positive else {"jbod1", "jbod2"}
                        ), error()

                with Then("number of rows should match"):
                    r = node.query(
                        f"SELECT count() FROM {name} FORMAT TabSeparated"
                    ).output.strip()
                    assert r == "6", error()

                with And("I wait until second TTL expression eventually triggers"):
                    time.sleep(60)

                    for attempt in retries(timeout=300, delay=10):
                        with attempt:
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
                                    f"SELECT count() FROM {name} FORMAT TabSeparated"
                                ).output.strip()
                                assert r == "6", error()

                with And("I wait until TTL expression to delete eventually triggers"):
                    time.sleep(30)

                    with By("running optimize final to make sure delete completes"):
                        node.query(f"OPTIMIZE TABLE {name} FINAL")

                    with And("retrying until number of rows reaches the expected"):
                        for attempt in retries(timeout=300, delay=10):
                            with attempt:
                                with Then(
                                    f"number of rows should {'be 0' if positive else 'match'}"
                                ):
                                    r = node.query(
                                        f"SELECT count() FROM {name} FORMAT TabSeparated"
                                    ).output.strip()
                                    assert r == ("0" if positive else "3"), error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
