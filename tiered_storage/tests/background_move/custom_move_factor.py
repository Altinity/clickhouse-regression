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


@TestScenario
@Name("custom move factor")
@Examples(
    "name engine",
    [
        ("moving_mt", "MergeTree()"),
        (
            "moving_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/moving_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when data in the volume reaches the limit
    specified by the **move_factor** option
    then in the background the parts are moved to the external volume.
    """
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

                with And("I get table's uuid"):
                    table_uuid = node.query(
                        f"SELECT uuid FROM system.tables WHERE name = '{name}'"
                    ).output.strip()
                    table_uuid_prefix = table_uuid[:3]

                try:
                    with And("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And(
                        "I insert 5 times 5MB of data with 5 rows 1MB each",
                        description="small jbod size is 40MB",
                    ):
                        for i in range(5):
                            data = []
                            for i in range(5):
                                data.append(
                                    get_random_string(cluster, 1024 * 1024, steps=False)
                                )
                            values = ",".join(["('" + x + "')" for x in data])
                            node.query(f"INSERT INTO {name} VALUES {values}")

                    with And("poll maximum 40 times to check used disks for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        retry = 40
                        i = 0
                        while (
                            not sum(1 for x in used_disks if x == "jbod1") <= 2
                            and i < retry
                        ):
                            with And("sleep 0.5 sec"):
                                time.sleep(0.5)
                            used_disks = get_used_disks_for_table(node, name)
                            i += 1

                    with Then(
                        "check that jbod1 disk is used less than or equal to 2 times"
                    ):
                        assert sum(1 for x in used_disks if x == "jbod1") <= 2, error()

                    with And("that at least 3 parts were moved to 'external'"):
                        assert (
                            sum(1 for x in used_disks if x == "external") >= 3
                        ), error()

                    with And("I flush all system logs"):
                        node.query("SYSTEM FLUSH LOGS")

                    with When("I read path_on_disk from system.part_log"):
                        path = node.query(
                            f"SELECT path_on_disk FROM system.part_log WHERE table = '{name}'"
                            " AND event_type='MovePart' ORDER BY event_time LIMIT 1"
                        ).output

                    with Then(
                        "the first (oldest) part path_on_disk should have path to the external"
                    ):
                        if cluster.with_minio or (
                            (cluster.with_s3amazon or cluster.with_s3gcs)
                            and check_clickhouse_version(">=22.3")(self)
                        ):
                            assert path.startswith(
                                "/var/lib/clickhouse/disks/external/"
                            ), error()
                        else:
                            assert path.startswith("/external"), error()

                    with When("I check if parts were eventually deleted jbod1"):
                        for attempt in retries(timeout=60, delay=5):
                            with attempt:
                                with By("getting number of parts on jbod1"):
                                    entries = (
                                        node.command(
                                            f"find /jbod1/store/{table_uuid_prefix}/{table_uuid}/ -name 'all_*'",
                                            exitcode=0,
                                        )
                                        .output.strip()
                                        .splitlines()
                                    )

                                with Then(
                                    "number of parts left on jbod1 should be <= 2"
                                ):
                                    assert len(entries) <= 2, error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
