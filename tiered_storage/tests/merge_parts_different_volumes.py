#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table

from tiered_storage.requirements import *

from testflows.core import TestScenario, Name, Examples, Requirements
from testflows.core import Given, When, And, Then, Finally, current
from testflows.asserts import error


@TestScenario
@Name("merge parts different volumes")
@Examples(
    "name engine",
    [
        ("merge_parts_different_volumes_mt", "MergeTree()"),
        # ("merge_parts_different_volumes_replicated_mt","ReplicatedMergeTree('/clickhouse/merge_parts_different_volumes_replicated_mt', '1')")
        # SYSTEM STOP MERGES doesn't disable merges assignments
    ],
)
@Requirements(
    RQ_SRS_004_BackgroundMergeProcess_MergingParts_MovesAgainstStoragePolicy("1.0"),
    RQ_SRS_004_BackgroundMergeProcess_MergingParts_FromMultipleVolumes("1.0"),
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that when parts are merged from different
    volumes the resulting part is palaced on the
    volume of the part that has the lowest priority.
    """
    with Given("cluster node"):
        node = cluster.node(node)

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
                    SETTINGS storage_policy='fast_med_and_slow'
                """
                )
            try:
                with And("I stop merges to avoid conflicts"):
                    node.query(f"SYSTEM STOP MERGES {name}")

                with And("I insert 6 values"):
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 66)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-17'), 42)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-18'), 43)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-19'), 32)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-20'), 33)")

                used_disks = get_used_disks_for_table(node, name)

                with Then("all writes should go to 'fast' volume"):
                    assert all(d.startswith("jbod1") for d in used_disks), error()

                with When("I get the parts from system.parts"):
                    first_part = node.query(
                        f"SELECT name FROM system.parts WHERE table = '{name}'"
                        " AND active = 1 ORDER BY modification_time"
                    ).output.strip()

                with When("I move part 201903_4_4_0 to 'medium' volume"):
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '201903_4_4_0' TO VOLUME 'medium'"
                    )

                    with And("I get disk name from system.parts for the part"):
                        disk = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}' "
                            f" AND name = '201903_4_4_0' and active = 1"
                        ).output.strip()

                    with Then("the disk name should be 'jbod2'"):
                        assert disk == "jbod2", error()

                with When("I move part 201903_6_6_0 to 'slow' volume"):
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '201903_6_6_0' TO VOLUME 'slow'"
                    )

                    with And("I get disk name from system.parts for the part"):
                        disk = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}' "
                            f" AND name = '201903_6_6_0' and active = 1"
                        ).output.strip()

                    with Then("the disk name should be 'external'"):
                        assert disk == "external", error()

                with When("I restart merges"):
                    node.query(f"SYSTEM START MERGES {name}")

                with And("I optimize table to force merge"):
                    node.query(f"OPTIMIZE TABLE {name}")

                with And("I wait for merge to complete"):
                    time.sleep(10)

                with And("I get number of active parts"):
                    active = node.query(
                        f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                    ).output.strip()

                    with Then("active parts should be 1"):
                        assert "1" == active

                with And("I get disks for this partition"):
                    disks = (
                        node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                            " AND partition = '201903' and active = 1"
                        )
                        .output.strip()
                        .split("\n")
                    )

                    with Then("number of disks should be 1"):
                        assert len(disks) == 1, error()

                    with And("all disks should be 'external'"):
                        assert all(d == "external" for d in disks), error()

                with When("in the end I get number of rows in the table"):
                    count = node.query(f"SELECT COUNT() FROM {name}").output.strip()

                    with Then("the count should be 6"):
                        assert count == "6", error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
