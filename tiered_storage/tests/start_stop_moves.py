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
@Name("start stop moves")
@Examples(
    "name engine",
    [
        ("stopped_moving_mt", "MergeTree()"),
        (
            "stopped_moving_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/stopped_moving_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check stop and start of data moves."""
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='moving_jbod_with_external'
                    """
                    )
                try:
                    with And("I insert some values"):
                        node.query(f"INSERT INTO {name} VALUES ('HELLO')")
                        node.query(f"INSERT INTO {name} VALUES ('WORLD')")

                    used_disks = get_used_disks_for_table(node, name)

                    with Then("all writes should go to jbod disks"):
                        assert all(d == "jbod1" for d in used_disks), error()

                    with When("I get the first part in system.parts"):
                        first_part = node.query(
                            f"SELECT name FROM system.parts WHERE table = '{name}'"
                            " AND active = 1 ORDER BY modification_time LIMIT 1"
                        ).output.strip()

                    with When("I disallow moves"):
                        node.query("SYSTEM STOP MOVES")
                        try:
                            with When("I try to use alter MOVE PART query"):
                                exitcode = 236
                                message = "Exception: Cannot move parts because moves are manually disabled"
                                node.query(
                                    f"ALTER TABLE {name} MOVE PART '{first_part}' TO VOLUME 'external'",
                                    message,
                                    exitcode,
                                )

                            used_disks = get_used_disks_for_table(node, name)

                            with Then(
                                "blocked moves should not actually move anything"
                            ):
                                assert all(d == "jbod1" for d in used_disks), error()
                        finally:
                            with Finally("I allow move again"):
                                node.query("SYSTEM START MOVES")

                    with When("I try to move part after move are enabled"):
                        node.query(
                            f"ALTER TABLE {name} MOVE PART '{first_part}' TO VOLUME 'external'"
                        )

                        with And("I select disk_name form system.parts"):
                            disk = node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                f" AND name = '{first_part}' and active = 1"
                            ).output.strip()

                        with Then("part should be on external disk"):
                            assert disk == "external", error()

                    with When("I truncate table"):
                        node.query(f"TRUNCATE TABLE {name}")

                        with And("then stop moves and merges"):
                            node.query(f"SYSTEM STOP MOVES {name}")
                            node.query(f"SYSTEM STOP MERGES {name}")
                        try:
                            with And(
                                "I insert 5 times 5MB of data with 5 rows 1MB each",
                                description="jbod size is 40MB",
                            ):
                                for i in range(5):
                                    data = []
                                    for i in range(5):
                                        data.append(
                                            get_random_string(
                                                cluster, 1024 * 1024, steps=False
                                            )
                                        )
                                    values = ",".join(["('" + x + "')" for x in data])
                                    node.query(
                                        f"INSERT INTO {name} VALUES {values}",
                                        timeout=30,
                                    )

                            used_disks = get_used_disks_for_table(node, name)

                            with And(
                                "I wait until disks using jbod1 are <= 2 or max retry count of 5"
                            ):
                                retry = 5
                                i = 0
                                while (
                                    not sum(1 for x in used_disks if x == "jbod1") <= 2
                                    and i < retry
                                ):
                                    time.sleep(0.1)
                                    used_disks = get_used_disks_for_table(node, name)
                                    i += 1
                            with Then(
                                "the first (oldest) part should not move anywhere"
                            ):
                                assert used_disks[0] == "jbod1", error()
                        finally:
                            with Finally("restart moves and merges"):
                                node.query(f"SYSTEM START MOVES {name}")
                                node.query(f"SYSTEM START MERGES {name}")

                    with When("I wait until background back-off finishes"):
                        with By(
                            "waiting until disks using jbod1 <=2 or max retry count of 30"
                        ):
                            retry = 30
                            i = 0
                            while (
                                not sum(1 for x in used_disks if x == "jbod1") <= 2
                                and i < retry
                            ):
                                time.sleep(1)
                                used_disks = get_used_disks_for_table(node, name)
                                i += 1

                        with Then("the number of disks using jbod1 should be <= 2"):
                            assert (
                                sum(1 for x in used_disks if x == "jbod1") <= 2
                            ), error()

                        with And("that some parts were moved to 'external'"):
                            assert "external" in used_disks, error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
