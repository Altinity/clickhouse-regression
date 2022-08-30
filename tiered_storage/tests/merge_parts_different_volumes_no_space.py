#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table
from tiered_storage.tests.common import get_random_string

from tiered_storage.requirements import *

from testflows.core import TestScenario, Name, Examples, Requirements
from testflows.core import Given, When, And, Then, Finally, current
from testflows.asserts import error


@TestScenario
@Name("merge parts different volumes no space")
@Examples(
    "name engine",
    [
        ("merge_parts_different_volumes_no_space_mt", "MergeTree()"),
        # ("merge_parts_different_volumes_no_space_replicated_mt","ReplicatedMergeTree('/clickhouse/merge_parts_different_volumes_no_space_replicated_mt', '1')")
        # SYSTEM STOP MERGES doesn't disable merges assignments
    ],
)
@Requirements(RQ_SRS_004_BackgroundMergeProcess_FaultTolerance_NoSpace("1.0"))
def scenario(self, cluster, node="clickhouse1"):
    """Check that when parts are merged from different
    volumes and there is no space on the disk where
    the resulting part should be placed then move is aborted
    and a message is written to the log.
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
                        number UInt64,
                        s String
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    PARTITION BY toYYYYMM(EventDate)
                    SETTINGS storage_policy='jbod1_with_jbod2'
                """
                )
            try:
                with And("I stop merges to avoid conflicts"):
                    node.query(f"SYSTEM STOP MERGES {name}")

                with And("I insert data"):
                    string = get_random_string(cluster, 2 * 1024 * 1024, steps=False)
                    node.query(
                        f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65, '{string}')"
                    )
                    node.query(
                        f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 66, '{string}')"
                    )
                    node.query(
                        f"INSERT INTO {name} VALUES(toDate('2019-03-17'), 42, '{string}')"
                    )
                    node.query(
                        f"INSERT INTO {name} VALUES(toDate('2019-03-18'), 43, '{string}')"
                    )

                used_disks = get_used_disks_for_table(node, name)

                with Then("all writes should go to 'main' volume"):
                    assert all(d.startswith("jbod1") for d in used_disks), error()

                with When("I get the parts from system.parts"):
                    first_part = node.query(
                        f"SELECT name FROM system.parts WHERE table = '{name}'"
                        " AND active = 1 ORDER BY modification_time"
                    ).output.strip()

                with When("I move part 201903_4_4_0 to 'external' volume"):
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '201903_4_4_0' TO VOLUME 'external'"
                    )

                    with And("I get disk name from system.parts for the part"):
                        disk = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}' "
                            f" AND name = '201903_4_4_0' and active = 1"
                        ).output.strip()

                    with Then("the disk name should be 'jbod2'"):
                        assert disk == "jbod2", error()

                with When("I create table to fill up 'external' volume"):
                    node.query(
                        f"""
                        CREATE TABLE {name}_fill_up (
                            EventDate Date,
                            number UInt64,
                            s String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        PARTITION BY toYYYYMM(EventDate)
                        SETTINGS storage_policy='only_jbod2'
                    """
                    )
                try:
                    with And(
                        "I insert data into the table that fill up 'external' volume"
                    ):
                        for i in range(15):
                            string = get_random_string(
                                cluster, 1 * 1024 * 1024, steps=False
                            )
                            node.query(
                                f"INSERT INTO {name}_fill_up VALUES(toDate('2019-03-15'), 60, '{string}')"
                            )

                    with When("I restart merges"):
                        node.query(f"SYSTEM START MERGES {name}")

                    with And("I optimize table to force merge"):
                        node.query(
                            f"OPTIMIZE TABLE {name}",
                            exitcode=243,
                            message="Exception: Not enough space for merging parts",
                        )

                    with And("I get number of active parts"):
                        active = node.query(
                            f"SELECT count() FROM system.parts WHERE table = '{name}' AND active = 1"
                        ).output.strip()

                        with Then("active parts should be 4"):
                            assert "4" == active

                    with And("I get disks for this partition"):
                        disks = set(
                            node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                " AND partition = '201903' and active = 1"
                            )
                            .output.strip()
                            .split("\n")
                        )

                        with Then("number of disks should be 2"):
                            assert len(disks) == 2, error()

                        with And("disk should be 'jbod1' and 'jbod2'"):
                            assert disks == {"jbod1", "jbod2"}, error()
                finally:
                    with Finally("I drop the table used to fill up 'external' volume"):
                        node.query(f"DROP TABLE IF EXISTS {name}_fill_up SYNC")

                with When("in the end I get number of rows in the table"):
                    count = node.query(f"SELECT COUNT() FROM {name}").output.strip()

                    with Then("the count should be 4"):
                        assert count == "4", error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
