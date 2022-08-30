#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_used_disks_for_table
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("round robin")
@Requirements(RQ_SRS_004_StoragePolicy_Rules_RoundRobinDistribution("1.0"))
@Examples(
    "name engine",
    [
        ("mt_on_jbod", "MergeTree()"),
        (
            "replicated_mt_on_jbod",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_on_jbod', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1", count=10000):
    """Check round-robin algorithm is used
    when a volume contains multiple disks.
    """
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                try:
                    with When(f"I create table"):
                        node.query(
                            f"""
                            CREATE TABLE {name} (
                                d UInt64
                            ) ENGINE = {engine}
                            ORDER BY d
                            SETTINGS storage_policy='jbods_with_external'
                        """
                        )

                    with When(f"I insert {count} numbers into table {name}"):
                        node.query(f"insert into {name} select * from numbers(10000)")
                        used_disk = get_used_disks_for_table(node, name, step=And)

                        with Then("number of used disks should be 1"):
                            assert len(used_disk) == 1, error(
                                "More than one disk used for single insert"
                            )

                    with When(
                        f"I insert another {count} numbers starting from {1 * count} into {name}"
                    ):
                        node.query(
                            f"insert into {name} select * from numbers({1 * count}, {count})"
                        )
                        used_disks = get_used_disks_for_table(node, name, step=And)

                        with Then("number of used disks should be 2"):
                            assert len(used_disks) == 2, error(
                                "Two disks should be used for two parts"
                            )

                        with And("disks should be different"):
                            assert used_disks[0] != used_disks[1], error(
                                "Should write to different disks"
                            )

                    with When(
                        f"I insert another {count} numbers from {2 * count} into {name}",
                        description="jbod1 -> jbod2 -> jbod1 -> jbod2 ... etc",
                    ):
                        node.query(
                            f"insert into {name} select * from numbers({2 * count}, {count})"
                        )
                        used_disks = get_used_disks_for_table(node, name, step=And)

                        with Then("number of used disks should be 3"):
                            assert len(used_disks) == 3, error()

                        with And("first and second disks should be different"):
                            assert used_disks[0] != used_disks[1], error()

                        with And("last disk should be the same as the first"):
                            assert used_disks[2] == used_disks[0], error()
                finally:
                    with Finally("I drop the table if exists"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
