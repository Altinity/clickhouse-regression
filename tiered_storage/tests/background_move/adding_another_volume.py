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
@Name("adding another volume")
@Requirements()
@Examples(
    "name engine",
    [
        ("adding_another_volume_mt", "MergeTree()"),
        (
            "adding_another_volume_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/adding_another_volume_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when at the beginning a table has storage policy that only contains
    one volume with one disk is filled up and then the policy is changed
    that has two volumes the data from the first volume is moved to the
    second and all moved parts are removed from the first.
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
                    with And("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And(
                        "I fill up first disk above 90%%",
                        description="small jbod size is 40MB",
                    ):
                        with By("first inserting 2MB of data with 2 rows 1MB each"):
                            data = []
                            for i in range(2):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name} VALUES {values}")

                        with And(
                            "then inserting 7 times 5MB of data with 5 rows 1MB each"
                        ):
                            for i in range(7):
                                data = []
                                for i in range(5):
                                    data.append(
                                        get_random_string(
                                            cluster, 1024 * 1024, steps=False
                                        )
                                    )
                                values = ",".join(["('" + x + "')" for x in data])
                                node.query(f"INSERT INTO {name} VALUES {values}")

                        with And("I ensure all rows are in the table"):
                            r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                            with Then(f"it should return the result of {rows_count}"):
                                assert r == f"{rows_count}", error()

                    with And("poll maximum 30 times to check used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        retry = 30
                        i = 0
                        while (
                            not sum(1 for x in used_disks if x == "jbod1") == 8
                            and i < retry
                        ):
                            with And("sleep 0.5 sec"):
                                time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then("check that jbod1 disk is used equals to 8 times"):
                        assert sum(1 for x in used_disks if x == "jbod1") == 8, error()

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
                            not sum(1 for x in used_disks if x == "external") >= 1
                            and i < retry
                        ):
                            with And("sleep 0.5 sec"):
                                time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then(
                        "check that jbod1 disk is used is less than or equals to 7 times"
                    ):
                        assert sum(1 for x in used_disks if x == "jbod1") <= 7, error()

                    with And(
                        "that the first two (oldest) parts were moved to 'external'"
                    ):
                        for attempt in retries(timeout=180, delay=1):
                            with attempt:
                                assert used_disks[0] == "external", error()

                    with When("I restart again"):
                        node.restart()

                    with And(
                        "I ensure there are no duplicates and all rows are in the table"
                    ):
                        r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                        with Then(f"it should return the result of {rows_count}"):
                            assert r == f"{rows_count}", error()
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

                        with And("I change storage policy back and restart"):
                            node.command(
                                "rm /etc/clickhouse-server/config.d/updated_storage_configuration.xml"
                            )
                            node.command("ls /etc/clickhouse-server/config.d")
                            node.restart()
