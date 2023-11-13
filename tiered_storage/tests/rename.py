#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_random_string
from tiered_storage.tests.common import get_used_disks_for_table
from testflows.core import TestScenario, Name
from testflows.core import Given, When, And, By, Then, Finally, current
from testflows.asserts import error

from helpers.common import check_clickhouse_version


@TestScenario
@Name("rename")
def scenario(self, cluster, node="clickhouse1"):
    """Check renaming table when storage policy for the table is specified."""
    count = "50"

    with Given("cluster node"):
        node = cluster.node(node)

    try:
        with When("I create table"):
            node.query(
                """
                CREATE TABLE default.renaming_table (
                    s String
                ) ENGINE = MergeTree
                ORDER BY tuple()
                SETTINGS storage_policy='small_jbod_with_external'
            """
            )

        with And("I stop merges to avoid conflicts"):
            node.query(f"SYSTEM STOP MERGES default.renaming_table")

        with When("I insert 50MB of data 5 times 10 rows 1MB each"):
            for _ in range(5):
                data = []
                for i in range(10):
                    data.append(get_random_string(cluster, 1024 * 1024, steps=False))
                values = ",".join(["('" + x + "')" for x in data])
                node.query(f"INSERT INTO renaming_table VALUES {values}", steps=False)

        disks = get_used_disks_for_table(node, "renaming_table")

        with Then("number of disks should be > 1"):
            assert len(disks) > 1, error()

        expected_disks = {"external", "jbod1"}
        with Then(f"the used disk should match {expected_disks}", format_name=False):
            assert set(disks) == expected_disks, error()

        with When("I get the number of rows"):
            r = node.query("SELECT COUNT() FROM default.renaming_table").output.strip()
            with Then(f"count should be {count}"):
                assert r == count

        with When("I rename table"):
            node.query("RENAME TABLE default.renaming_table TO default.renaming_table1")
            with When("I get the number of rows in the new table"):
                r = node.query(
                    "SELECT COUNT() FROM default.renaming_table1"
                ).output.strip()
                with Then(f"count should be {count}"):
                    assert r == count

            with When("I get the number of rows for the old table"):
                exitcode = 60
                if check_clickhouse_version("<23.8")(self):
                    message = "Exception: Table default.renaming_table doesn't exist"
                else:
                    message = "Exception: Table default.renaming_table does not exist"
                node.query(
                    "SELECT COUNT() FROM default.renaming_table", message, exitcode
                )

        with When("I create new database"):
            node.query("CREATE DATABASE IF NOT EXISTS test")
            with By("renaming the table and using the new database"):
                node.query(
                    "RENAME TABLE default.renaming_table1 TO test.renaming_table2"
                )
            with And("I get the number of rows in the new table"):
                r = node.query(
                    "SELECT COUNT() FROM test.renaming_table2"
                ).output.strip()
                with Then(f"count should be {count}"):
                    assert r == count

            with When("I get the number of rows for the old table"):
                exitcode = 60
                if check_clickhouse_version("<23.8")(self):
                    message = "Exception: Table default.renaming_table1 doesn't exist"
                else:
                    message = "Exception: Table default.renaming_table1 does not exist"
                node.query(
                    "SELECT COUNT() FROM default.renaming_table1", message, exitcode
                )

    finally:
        with Finally("I drop all the tables"):
            node.query("DROP TABLE IF EXISTS default.renaming_table SYNC")
            node.query("DROP TABLE IF EXISTS default.renaming_table1 SYNC")
            node.query("DROP TABLE IF EXISTS test.renaming_table2 SYNC")
