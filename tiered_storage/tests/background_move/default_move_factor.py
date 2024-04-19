#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from helpers.common import check_clickhouse_version
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestOutline(Scenario)
@Name("default move factor")
@Requirements(
    RQ_SRS_004_Configuration_StorageConfiguration_MoveFactor_DefaultValue("1.0")
)
@Examples(
    "engine",
    [
        ["MergeTree()"],
        ["ReplicatedMergeTree('/clickhouse/moving_replicated_mt', '1')"],
    ],
)
def scenario(self, engine):
    """Check that once the default value of **move_factor** which is 0.1
    is reached then in the background the parts are moved to the external volume.
    """

    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    table_name = "table_" + engine.split("(")[0].lower()

    with When("I create table"):
        node.query(
            f"""
            CREATE TABLE {table_name} (
                s1 String
            ) ENGINE = {engine}
            ORDER BY tuple()
            SETTINGS storage_policy='small_jbod_with_external'
        """
        )

    with And("I get table's uuid"):
        table_uuid = node.query(
            f"SELECT uuid FROM system.tables WHERE name = '{table_name}'"
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

        with And("poll maximum 20 times to check used disks for the table"):
            used_disks = get_used_disks_for_table(node, table_name)
            retry = 20
            i = 0
            while not used_disks.count("jbod1") <= 7 and i < retry:
                with And("sleep 0.5 sec"):
                    time.sleep(0.5)
                used_disks = get_used_disks_for_table(node, table_name)
                i += 1

        with Then("check that jbod1 disk is used less than or equal to 7 times"):
            assert used_disks.count("jbod1") <= 7, error()

        with And("that some parts were moved to 'external'"):
            assert "external" in used_disks, error()

        with When("We wait 5 sec for system.part_log to be present"):
            time.sleep(5)

        with When("I read path_on_disk from system.part_log"):
            path = node.query(
                f"SELECT path_on_disk FROM system.part_log WHERE table = '{table_name}'"
                " AND event_type='MovePart' ORDER BY event_time LIMIT 1"
            ).output

        with Then(
            "the first (oldest) part path_on_disk should have path to the external"
        ):
            if cluster.with_minio or (
                (cluster.with_s3amazon or cluster.with_s3gcs)
                and check_clickhouse_version(">=22.3")(self)
            ):
                assert path.startswith("/var/lib/clickhouse/disks/external/"), error()
            else:
                assert path.startswith("/external"), error()

        with When("I check if parts were deleted from jbod1"):
            entries = (
                node.command(
                    f"find /jbod1/store/{table_uuid_prefix}/{table_uuid}/ -name 'all_*'",
                    exitcode=0,
                )
                .output.strip()
                .splitlines()
            )

        with Then("number of parts left on jbod1 should be <= 7"):
            assert len(entries) <= 7, error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
