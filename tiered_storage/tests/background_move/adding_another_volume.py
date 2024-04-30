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


@TestOutline(Scenario)
@Name("adding another volume")
@Requirements()
@Examples(
    "engine",
    [
        ["MergeTree()"],
        [
            "ReplicatedMergeTree('/clickhouse/adding_another_volume_replicated_mt', '1')",
        ],
    ],
)
def scenario(self, engine):
    """Check that when at the beginning a table has storage policy that only contains
    one volume with one disk is filled up and then the policy is changed
    that has two volumes the data from the first volume is moved to the
    second and all moved parts are removed from the first.
    """

    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    rows_count = 5 * 7 + 2

    table_name = "table_" + engine.split("(")[0].lower()

    with When("I create table"):
        node.query(
            f"""
            DROP TABLE IF EXISTS {table_name} SYNC;
            CREATE TABLE {table_name} (
                s1 String
            ) ENGINE = {engine}
            ORDER BY tuple()
            SETTINGS storage_policy='one_small_disk'
        """
        )

    with And("I get table's uuid"):
        table_uuid = node.query(
            f"SELECT uuid FROM system.tables WHERE name = '{table_name}' FORMAT TabSeparated"
        ).output.strip()
        table_uuid_prefix = table_uuid[:3]

    try:
        with And("I stop merges to avoid conflicts"):
            node.query(f"SYSTEM STOP MERGES {table_name}")

        with And(
            "I fill up first disk above 90%%",
            description="small jbod size is 40MB",
        ):
            with By("first inserting 2MB of data with 2 rows 1MB each"):
                data = []
                for i in range(2):
                    data.append(get_random_string(cluster, 1024 * 1024, steps=False))
                values = ",".join(["('" + x + "')" for x in data])
                node.query(f"INSERT INTO {table_name} VALUES {values}")

            with And("then inserting 7 times 5MB of data with 5 rows 1MB each"):
                for i in range(7):
                    data = []
                    for i in range(5):
                        data.append(
                            get_random_string(cluster, 1024 * 1024, steps=False)
                        )
                    values = ",".join(["('" + x + "')" for x in data])
                    node.query(f"INSERT INTO {table_name} VALUES {values}")

            with And("I ensure all rows are in the table"):
                r = node.query(
                    f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
                ).output.strip()
                with Then(f"it should return the result of {rows_count}"):
                    assert r == f"{rows_count}", error()

        with When("check used disks for the table"):
            for attempt in retries(timeout=15, delay=2):
                with attempt:
                    used_disks = get_used_disks_for_table(node, table_name)

                    with Then("check that jbod1 disk is used equals to 8 times"):
                        assert used_disks.count("jbod1") == 8, error()

        with When("I change storage policy to contain another volume and restart"):
            node.command(
                "cp /etc/clickhouse-server/config_variants/updated_storage_configuration.xml /etc/clickhouse-server/config.d"
            )
            node.command("ls /etc/clickhouse-server/config.d")
            node.restart()

            with And("I ensure all rows are in the table"):
                r = node.query(
                    f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
                ).output.strip()
                with Then(f"it should return the result of {rows_count}"):
                    assert r == f"{rows_count}", error()

        with When("check used disks for the table"):
            for attempt in retries(timeout=60, delay=2):
                with attempt:
                    used_disks = get_used_disks_for_table(node, table_name)

                    with Then(
                        "check that jbod1 disk is used is less than or equals to 7 times"
                    ):
                        assert used_disks.count("jbod1") <= 7, error()

                    with And(
                        "that the first two (oldest) parts were moved to 'external'"
                    ):
                        assert used_disks[0] == "external", error()

        with When("I restart again"):
            node.restart()

        with And("I ensure there are no duplicates and all rows are in the table"):
            r = node.query(
                f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
            ).output.strip()
            with Then(f"it should return the result of {rows_count}"):
                assert r == f"{rows_count}", error()
    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

            with And("I change storage policy back and restart"):
                node.command(
                    "rm /etc/clickhouse-server/config.d/updated_storage_configuration.xml"
                )
                node.command("ls /etc/clickhouse-server/config.d")
                node.restart()
