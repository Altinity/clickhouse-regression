#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_random_string

from testflows.core import TestScenario, Name, Examples, Requirements
from testflows.core import Given, When, And, Then, Finally, current
from testflows.asserts import error

from tiered_storage.requirements import *


@TestScenario
@Name("system.detached_parts")
@Requirements(RQ_SRS_004_Configuration_Disks_DetachedParts_Reading("1.0"))
@Examples(
    "name engine",
    [
        ("detach_attach_mt", "MergeTree()"),
        (
            "replicated_detach_attach_mt",
            "ReplicatedMergeTree('/clickhouse/replicated_detach_attach_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check system.detached_parts table has new disk column."""
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                with When("I create table"):
                    node.query(
                        """
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='moving_jbod_with_external'
                    """.format(
                            name=name, engine=engine
                        )
                    )
                try:
                    with And("I insert some values"):
                        data = []  # 5MB in total
                        for i in range(5):
                            data.append(
                                get_random_string(cluster, 1024 * 1024, steps=False)
                            )
                        values = ",".join(["('" + x + "')" for x in data])
                        node.query(f"INSERT INTO {name} VALUES {values}")

                    with When("I detach partition"):
                        node.query(f"ALTER TABLE {name} DETACH PARTITION tuple()")

                    with Then("number of rows should be 0"):
                        count = node.query(f"SELECT count() FROM {name}").output.strip()
                        assert count == "0", error()

                    with And(
                        "disk column for the table in system.detached_parts should have value of 'jbod1'"
                    ):
                        disk = node.query(
                            f"SELECT disk FROM system.detached_parts WHERE table = '{name}'"
                        ).output.strip()
                        assert disk == "jbod1", error()

                    with When("I reattach the partition"):
                        node.query(f"ALTER TABLE {name} ATTACH PARTITION tuple()")

                    with Then("number of rows should be 5"):
                        count = node.query(f"SELECT count() FROM {name}").output.strip()
                        assert count == "5", error()

                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
