#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table
from tiered_storage.tests.common import get_path_for_part_from_part_log
from tiered_storage.tests.common import get_paths_for_partition_from_part_log

from testflows.core import TestScenario, Name, Requirements, Examples
from testflows.core import Given, When, And, Then, Finally, current
from testflows.asserts import error

from tiered_storage.requirements import *


@TestScenario
@Name("manual move with downtime")
@Requirements(RQ_SRS_004_MovingDataBetweenStorageDevices_Manual_WithDowntime("1.0"))
@Examples(
    "name engine",
    [
        ("manual_move_mt", "MergeTree()"),
        (
            "manual_move_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/manual_move_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can still manually move parts
    using ALTER TABLE DETACH|ATTACH PART|PARTITION commands
    and physical part relocation.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    external_dir = "/external"
    if cluster.with_minio:
        external_dir = "/var/lib/clickhouse/disks/external"

    for example in self.examples:
        name, engine = example
        with When(f"for example table name='{name}', engine='{engine}'"):
            with When("I create table"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        EventDate Date,
                        number UInt64
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    PARTITION BY toYYYYMM(EventDate)
                    SETTINGS storage_policy='small_jbod_with_external'
                """
                )
            try:
                with And("I stop merges to avoid conflicts"):
                    node.query(f"SYSTEM STOP MERGES {name}")

                with And("I truncate system.parts_log"):
                    node.query("TRUNCATE TABLE IF EXISTS system.part_log")

                with And("I insert 4 values"):
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 66)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-04-10'), 42)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-04-11'), 43)")

                used_disks = get_used_disks_for_table(node, name)

                with Then("all writes should go to jbod1"):
                    assert all(d.startswith("jbod1") for d in used_disks), error()

                with When("I manually move partition 201904 to 'external' volume"):
                    node.query(f"ALTER TABLE {name} DETACH PARTITION 201904")
                    node.command(
                        f"mv /jbod1/store/*/*/detached/201904_* {external_dir}/store/*/*/detached/."
                    )
                    node.query(f"ALTER TABLE {name} ATTACH PARTITION 201904")

                    with And("I get disks for this partition"):
                        disks = (
                            node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                " AND partition = '201904' and active = 1"
                            )
                            .output.strip()
                            .split("\n")
                        )

                    with Then("number of disks should be 2"):
                        assert len(disks) == 2, error()

                    with And("all disks should be 'external'"):
                        for d in disks:
                            assert d == "external", error()

                    with And(f"all paths should start with '{external_dir}'"):
                        all_paths_start_with_external = all(
                            path.startswith(external_dir)
                            for path in get_paths_for_partition_from_part_log(
                                node, name, "201904"
                            )[:2]
                        )
                        assert all_paths_start_with_external, error()

                with When("I manually move partition 201904 to back disk 'jbod1'"):
                    node.query(f"ALTER TABLE {name} DETACH PARTITION 201904")
                    node.command(
                        f"mv {external_dir}/store/*/*/detached/201904_* /jbod1/store/*/*/detached/."
                    )
                    node.query(f"ALTER TABLE {name} ATTACH PARTITION 201904")

                    with And("I get disks for this partition"):
                        disks = (
                            node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                " AND partition = '201904' and active = 1"
                            )
                            .output.strip()
                            .split("\n")
                        )

                    with Then("number of disks should be 2"):
                        assert len(disks) == 2, error()

                    with And("all disks should be 'jbod1'"):
                        assert all(d == "jbod1" for d in disks), error()

                    with And("all paths should start with '/jbod2'"):
                        all_paths_start_with_jbod1 = all(
                            path.startswith("/jbod1")
                            for path in get_paths_for_partition_from_part_log(
                                node, name, "201904"
                            )[:2]
                        )
                        assert all_paths_start_with_jbod1, error()

                with When("in the end I get number of rows in the table"):
                    count = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("the count should be 4"):
                        assert count == "4", error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
