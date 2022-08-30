#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time

from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *

from tiered_storage.tests.common import get_random_string


@TestScenario
@Name("alter table policy")
@Requirements(RQ_SRS_004_Volume_StoragePolicy_AddingToTable_AlterTable("1.0"))
@Examples(
    "name engine",
    [
        ("alter_table_policy_mt", "MergeTree()"),
        (
            "alter_table_policy_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/alter_table_policy_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check changing storage policy on existing table."""
    self = current()

    def fill_up_disk(table, size):
        with By(f"inserting {size}MB of data"):
            data = []
            for i in range(size):
                data.append(get_random_string(cluster, 1024 * 1024))
            values = ",".join(["('" + x + "')" for x in data])
            node.query(f"INSERT INTO {table} VALUES {values}")

    def check_disk_utilization(name, size, above=True):
        with By("reading system.disks table"):
            node.query("SELECT * FROM system.disks")
            r = node.query(
                f"""
                SELECT
                    greatest((1 - (free_space/(total_space - keep_free_space))) * 100, 0) AS used
                FROM system.disks WHERE name = '{name}' ORDER BY name
            """
            ).output.strip("> \n")

        if above:
            with Then(f"checking utilization is above {size}%%"):
                assert float(r) >= size, error()
        else:
            with Then(f"checking utilization is below {size}%%"):
                assert float(r) < size, error()

    with Given("cluster node"):
        node = cluster.node(node)

    for name, engine in self.examples:
        with When(f"for example table name='{name}', engine='{engine}'"):
            try:
                with When("I create table with one volume that only has one disk"):
                    node.query(
                        f"""
                            CREATE TABLE {name} (
                                s1 String
                            ) ENGINE = {engine}
                            ORDER BY tuple()
                            SETTINGS storage_policy='one_small_disk'
                        """
                    )

                with And("I fill up the disk above 90%%"):
                    fill_up_disk(name, 37)

                with And("I check disk utilization is above 90%%"):
                    check_disk_utilization("jbod1", 90)

                with And("I change storage policy to add another disk to the volume"):
                    node.query(
                        f"ALTER TABLE {name} MODIFY SETTING storage_policy='jbods'"
                    )

                with And("I fill up the disk above 150%% of the original"):
                    fill_up_disk(name, 24)

                with And("I check disks utilizations"):
                    with By("checking jbod1 utilization is the same"):
                        check_disk_utilization("jbod1", 90)
                    with And("new disk utilization if above 70%%"):
                        check_disk_utilization("jbod2", 70)

                with And(
                    "I then try to change storage policy that contains new volume but missing one of the old disks"
                ):
                    exitcode = 36
                    message = "Exception: New storage policy"
                    sql = f"ALTER TABLE {name} MODIFY SETTING storage_policy='moving_jbod_with_external'"
                    node.query(sql, message, exitcode)

                with And(
                    "I now change to a new policy that contains all old disks and a new external volume"
                ):
                    node.query(
                        f"ALTER TABLE {name} MODIFY SETTING storage_policy='jbods_with_external'"
                    )

                with And(
                    "I fill up the disk above 200%% of the original but in chunks"
                ):
                    fill_up_disk(name, 1)
                    fill_up_disk(name, 5)
                    fill_up_disk(name, 5)
                    fill_up_disk(name, 9)

                if cluster.with_s3amazon or cluster.with_s3gcs:
                    with And("I check external is being used"):
                        output = node.query(
                            f"SELECT disk_name, active FROM system.parts WHERE table = '{name}' "
                        ).output
                        assert "external\t1" in output, error()
                else:
                    with And("I recheck disks utilizations"):
                        with By("checking jbod1 utilization remains above 10%%"):
                            check_disk_utilization("jbod1", 10)
                        with And("new disk utilization reached above 0%%"):
                            check_disk_utilization("jbod2", 0)
                        with And("external disk utilization is above 30%%"):
                            check_disk_utilization("external", 30)

                with And("I now try to go back to the old policy"):
                    exitcode = 36
                    message = "Exception: New storage policy"
                    node.query(
                        f"ALTER TABLE {name} MODIFY SETTING storage_policy='jbod1_with_jbod2'",
                        message,
                        exitcode,
                    )

                with And("I keep adding data to the table above 300%% of the original"):
                    fill_up_disk(name, 20)

                if cluster.with_s3amazon or cluster.with_s3gcs:
                    output = node.query(
                        f"SELECT disk_name, active FROM system.parts WHERE table = '{name}' "
                    ).output
                    assert "external\t1" in output, error()
                else:
                    with And("I recheck disks utilizations"):
                        with By("checking jbod1 utilization remains above 10%%"):
                            check_disk_utilization("jbod1", 10)
                        with And("new disk utilization reached above 0%%"):
                            check_disk_utilization("jbod2", 0)
                        with And("external disk utilization is above 30%%"):
                            check_disk_utilization("external", 39)

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
