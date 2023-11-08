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
from testflows.core import Given, When, Then, And, Finally, current
from testflows.asserts import error


@TestScenario
@Name("freeze")
def scenario(self, cluster, node="clickhouse1"):
    """Check table freeze when storage policy for the table is specified."""
    count = "50"

    with Given("cluster node"):
        node = cluster.node(node)

    try:
        with When("I create table"):
            node.query(
                """
                CREATE TABLE default.freezing_table (
                    d Date,
                    s String
                ) ENGINE = MergeTree
                ORDER BY tuple()
                PARTITION BY toYYYYMM(d)
                SETTINGS storage_policy='small_jbod_with_external'
            """
            )

            with And("I stop merges to avoid conflicts"):
                node.query(f"SYSTEM STOP MERGES default.freezing_table")

            with When("I insert 50MB of data 5 times 10 rows 1MB each"):
                for _ in range(5):
                    data = []
                    dates = []
                    for i in range(10):
                        data.append(
                            get_random_string(cluster, 1024 * 1024, steps=False)
                        )  # 1MB value
                        dates.append("toDate('2019-03-05')")
                    values = ",".join(
                        ["(" + d + ", '" + s + "')" for d, s in zip(dates, data)]
                    )
                    node.query(
                        f"INSERT INTO freezing_table VALUES {values}", steps=False
                    )

            disks = get_used_disks_for_table(node, "freezing_table")

            with Then("number of used disk should be > 1"):
                assert len(disks) > 1, error()

            expected_disks = {"external", "jbod1"}
            with Then(
                f"the used disk should match {expected_disks}", format_name=False
            ):
                assert set(disks) == expected_disks, error()

            with When("I get the number of rows"):
                r = node.query(
                    "SELECT COUNT() FROM default.freezing_table"
                ).output.strip()
                with Then(f"count should be {count}"):
                    assert r == count

            with When("I freeze table partition"):
                node.query("ALTER TABLE freezing_table FREEZE PARTITION 201903")

            with Then("shadow files (backups) should exist"):
                node.command("find /jbod1/shadow -name '*mrk2' | grep '.*'", exitcode=0)
                if cluster.with_minio or cluster.with_s3amazon or cluster.with_s3gcs:
                    node.command(
                        "find /var/lib/clickhouse/disks/external/shadow -name '*mrk2' | grep '.*'",
                        exitcode=0,
                    )
                else:
                    node.command(
                        "find /external/shadow -name '*mrk2' | grep '.*'", exitcode=0
                    )
    finally:
        with Finally("I remove any shadow files if any"):
            node.command("rm -rf /jbod1/shadow")
            if cluster.with_minio:
                node.command("rm -rf /var/lib/clickhouse/disks/external/shadow")
            else:
                node.command("rm -rf /external/shadow")

        with Finally("I drop the table"):
            node.query("DROP TABLE IF EXISTS default.freezing_table SYNC")
