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
from helpers.common import check_clickhouse_version
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("alter move")
@Examples(
    "name engine",
    [
        ("altering_mt", "MergeTree()"),
        # ("altering_replicated_mt","ReplicatedMergeTree('/clickhouse/altering_replicated_mt', '1')")
        # SYSTEM STOP MERGES doesn't disable merges assignments
    ],
)
def scenario(self, cluster, node="clickhouse1"):
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
                    SETTINGS storage_policy='jbods_with_external'
                """
                )
            try:
                with And("I stop merges to avoid conflicts"):
                    node.query(f"SYSTEM STOP MERGES {name}")

                with And("I insert 4 values"):
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 66)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-04-10'), 42)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-04-11'), 43)")

                used_disks = get_used_disks_for_table(node, name)

                with Then("all writes should go to jbods"):
                    assert all(d.startswith("jbod") for d in used_disks), error()

                with When("I get the first part from system.parts"):
                    first_part = node.query(
                        f"SELECT name FROM system.parts WHERE table = '{name}'"
                        " AND active = 1 ORDER BY modification_time LIMIT 1"
                    ).output.strip()

                    with And("I try to move first part to 'external' volume"):
                        time.sleep(1)
                        node.query(
                            f"ALTER TABLE {name} MOVE PART '{first_part}' TO VOLUME 'external'"
                        )
                    with And("I get disk name from system.parts for the first part"):
                        disk = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}' "
                            f" AND name = '{first_part}' and active = 1"
                        ).output.strip()

                    with Then("the disk name should be 'external'"):
                        assert disk == "external", error()
                    with And("path should start with '/external'"):
                        expected = "/external"
                        if cluster.with_minio or (
                            (cluster.with_s3amazon or cluster.with_s3gcs)
                            and check_clickhouse_version(">=22.3")(self)
                        ):
                            expected = "/var/lib/clickhouse/disks/external"
                        assert get_path_for_part_from_part_log(
                            node, name, first_part
                        ).startswith(expected), error()

                with When("I move the first part to 'jbod1' disk"):
                    time.sleep(1)
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '{first_part}' TO DISK 'jbod1'"
                    )

                    with And("I get disk name from system.parts for the first part"):
                        disk = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                            f" AND name = '{first_part}' and active = 1"
                        ).output.strip()

                    with Then("the disk name shoul dbe 'jbod1'"):
                        assert disk == "jbod1", error()
                    with And("path should start with '/jbod1'"):
                        assert get_path_for_part_from_part_log(
                            node, name, first_part
                        ).startswith("/jbod1"), error()

                with When("I move partition 201904 to 'external' volume"):
                    time.sleep(1)
                    node.query(
                        f"ALTER TABLE {name} MOVE PARTITION 201904 TO VOLUME 'external'"
                    )

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
                        assert all(d == "external" for d in disks), error()
                    with And("all paths should start with '/external'"):
                        expected = "/external"
                        if cluster.with_minio or (
                            (cluster.with_s3amazon or cluster.with_s3gcs)
                            and check_clickhouse_version(">=22.3")(self)
                        ):
                            expected = "/var/lib/clickhouse/disks/external"
                        assert all(
                            path.startswith(expected)
                            for path in get_paths_for_partition_from_part_log(
                                node, name, "201904"
                            )[:2]
                        ), error()

                with When("I move partition 201904 to disk 'jbod2'"):
                    time.sleep(1)
                    node.query(
                        f"ALTER TABLE {name} MOVE PARTITION 201904 TO DISK 'jbod2'"
                    )

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
                    with And("all disks should be 'jbod2'"):
                        assert all(d == "jbod2" for d in disks), error()
                    with And("all paths should start with '/jbod2'"):
                        assert all(
                            path.startswith("/jbod2")
                            for path in get_paths_for_partition_from_part_log(
                                node, name, "201904"
                            )[:2]
                        ), error()

                with When("in the end I get number of rows in the table"):
                    count = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("the count should be 4"):
                        assert count == "4", error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
