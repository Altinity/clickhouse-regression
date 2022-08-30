#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("alter move half of partition")
@Examples(
    "storage_type name engine",
    [
        ("DISK", "alter_move_half_of_partition", "MergeTree()"),
        ("VOLUME", "alter_move_half_of_partition", "MergeTree()"),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check moving partition data in two half chunks."""
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        storage, name, engine = example
        with When(
            f"for example storage is '{storage}' and table name='{name}', engine='{engine}'"
        ):
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

                with When("I insert 2 rows"):
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-15'), 65)")
                    node.query(f"INSERT INTO {name} VALUES(toDate('2019-03-16'), 42)")
                    used_disks = get_used_disks_for_table(node, name)
                    with Then("all writes should go to jbods"):
                        assert all(d.startswith("jbod") for d in used_disks), error()

                with When("I select name from system.parts"):
                    time.sleep(1)
                    parts = node.query(
                        f"SELECT name FROM system.parts WHERE table = '{name}'"
                        " AND active = 1"
                    ).output.splitlines()
                    with Then("number of parts should be 2"):
                        assert len(parts) == 2, error()

                with When("I move first part to 'external' volume"):
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '{parts[0]}' TO VOLUME 'external'"
                    )
                    with And("I get disk name from system.parts"):
                        disks = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                            f" AND name = '{parts[0]}' and active = 1"
                        ).output.splitlines()
                    with Then("the disk name should be 'external'"):
                        assert disks == ["external"], error()

                with When(f"I move partition 201903 to 'external' {storage}"):
                    time.sleep(1)
                    node.query(
                        f"ALTER TABLE {name} MOVE PARTITION 201903 TO {storage} 'external'"
                    )
                    with And("I get disk name from system.parts"):
                        disks = node.query(
                            f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                            " AND partition = '201903' and active = 1"
                        ).output.splitlines()
                    with Then("both disk names should be 'external'"):
                        assert disks == ["external"] * 2, error()

                with When("in the end I get the number of rows in the table"):
                    count = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("the count should be 2"):
                        assert count == "2", error()
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
