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
@Name("adding another volume one large part")
@Requirements()
@Examples(
    "name engine",
    [
        ("adding_another_volume_one_large_part_mt", "MergeTree()"),
        (
            "adding_another_volume_one_large_part_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/adding_another_volume_one_large_part_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when at the beginning a table has storage policy that only contains
    one volume with one disk is filled up to over 90% with one large part
    and when the policy is changed that has two volumes then
    the data from the first volume is moved to the
    second and the moved part is removed from the first.
    """
    with Given("cluster"):
        node = cluster.node(node)
        rows_count = 5 * 7 + 2
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        f"""
                        DROP TABLE IF EXISTS {name} SYNC;
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='one_small_disk'
                    """
                    )

                with And("I get table's uuid"):
                    table_uuid = node.query(
                        f"SELECT uuid FROM system.tables WHERE name = '{name}'"
                    ).output.strip()
                    table_uuid_prefix = table_uuid[:3]

                try:
                    with When("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And(
                        "I fill up first disk above 90%% with one large part",
                        description="small jbod size is 40MB",
                    ):
                        with By(
                            "then inserting one time 37MB of data with 37 rows 1MB each"
                        ):
                            data = []
                            for i in range(37):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name} VALUES {values}")

                        with And("I ensure all rows are in the table"):
                            r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                            with Then(f"it should return the result of {rows_count}"):
                                assert r == f"{rows_count}", error()

                    with And("poll maximum 20 times to check used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        retry = 20
                        i = 0
                        while (
                            not sum(1 for x in used_disks if x == "jbod1") == 1
                            and i < retry
                        ):
                            time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then("check that jbod1 disk is used equals to 1 times"):
                        assert sum(1 for x in used_disks if x == "jbod1") == 1, error()

                    with When(
                        "I change storage policy to contain another volume and restart"
                    ):
                        node.command(
                            "cp /etc/clickhouse-server/config_variants/updated_storage_configuration.xml /etc/clickhouse-server/config.d"
                        )
                        node.command("ls /etc/clickhouse-server/config.d")
                        node.restart()

                        with And("I ensure all rows are in the table"):
                            r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                            with Then(f"it should return the result of {rows_count}"):
                                assert r == f"{rows_count}", error()

                    with And("poll maximum 20 times to check used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        retry = 20
                        i = 0
                        while (
                            not sum(1 for x in used_disks if x == "external") == 1
                            and i < retry
                        ):
                            time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then("check that jbod1 disk is not used"):
                        assert sum(1 for x in used_disks if x == "jbod1") == 0, error()

                    with And("that the part was moved to 'external'"):
                        assert used_disks[0] == "external", error()

                    with When("I check if the part was deleted from jbod1"):
                        entries = (
                            node.command(
                                f"find /jbod1/store/{table_uuid_prefix}/{table_uuid}/ -name 'all_*'",
                                exitcode=0,
                            )
                            .output.strip()
                            .splitlines()
                        )

                    with Then("number of parts left on jbod1 should be 0"):
                        assert len(entries) == 0, error()

                    with When("I restart again"):
                        node.restart()

                    with And(
                        "I ensure there are no duplicates and all rows are in the table"
                    ):
                        r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                        with Then(f"it should return the result of {rows_count}"):
                            assert r == f"{rows_count}", error()
                finally:
                    with Finally("I drop the table", flags=TE):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

                    with And("I change storage policy back and restart", flags=TE):
                        node.command(
                            "rm /etc/clickhouse-server/config.d/updated_storage_configuration.xml"
                        )
                        node.command("ls /etc/clickhouse-server/config.d")
                        node.restart()
