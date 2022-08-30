#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("max data part size")
@Requirements(
    RQ_SRS_004_StoragePolicy_Application_BackgroundMerge("1.0"),
    RQ_SRS_004_StoragePolicy_Rules_MoveData_MaxPartSize("1.0"),
)
@Examples(
    "name engine policy",
    [
        ("mt_with_huge_part", "MergeTree()", "jbods_with_external"),
        (
            "replicated_mt_with_huge_part",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_with_huge_part', '1')",
            "jbods_with_external",
        ),
        ("mt_with_huge_part", "MergeTree()", "jbods_with_external_ratio"),
        (
            "replicated_mt_with_huge_part",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_with_huge_part_2', '1')",
            "jbods_with_external_ratio",
        ),
    ],
    "%-28s | %-20s | %-10s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check inserting a large part into a table which has
    storage policy that has volume with max_data_part_size_bytes limit
    and makes sure that if part size exceeds this setting then
    the part is written to the external disk.
    """
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine, policy = example
            with When(
                f"for example table name='{name}', engine='{engine}', policy='{policy}'"
            ):
                with When("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        SETTINGS storage_policy='{policy}'
                    """
                    )
                try:
                    with When("I create 10MB of random string data"):
                        data = []
                        random_data = get_random_string(
                            cluster, 10 * 1024 * 1024, steps=False
                        )
                        with By("splitting it into 10 rows 1 MB each"):
                            for i in range(10):
                                MB = 1024 * 1024
                                data.append(
                                    random_data[i * MB : (i * MB) + MB]
                                )  # 1MB row

                    with And("I insert data"):
                        values = ",".join(["('" + x + "')" for x in data])
                        node.query(f"INSERT INTO {name} VALUES {values}")

                    used_disks = get_used_disks_for_table(node, name)

                    with Then("number of disks used should be 1"):
                        assert len(used_disks) == 1, error()

                    with And("the disk used should be 'external'"):
                        assert used_disks[0] == "external", error()
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
