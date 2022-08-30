#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_random_string
from testflows.core import TestScenario, Name, Examples
from testflows.core import Given, When, And, Then, By, Finally, current


@TestScenario
@Name("keep free space")
@Examples(
    "name engine policy size max_size",
    [
        ("mt_keep_free_space_bytes0", "MergeTree()", "only_jbod2", 28, 30),
        ("mt_keep_free_space_bytes1", "MergeTree()", "only_jbod2", 31, 30),
        ("mt_keep_free_space_ratio0", "MergeTree()", "only_jbod3", 18, 20),
        ("mt_keep_free_space_ratio1", "MergeTree()", "only_jbod3", 21, 20),
        (
            "replicated_mt_keep_free_space_bytes0",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_keep_free_space_bytes0', '1')",
            "only_jbod2",
            28,
            30,
        ),
        (
            "replicated_mt_keep_free_space_bytes1",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_keep_free_space_bytes1', '1')",
            "only_jbod2",
            31,
            30,
        ),
        (
            "replicated_mt_keep_free_space_ratio0",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_keep_free_space_ratio0', '1')",
            "only_jbod3",
            18,
            20,
        ),
        (
            "replicated_mt_keep_free_space_ratio1",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_keep_free_space_ratio1', '1')",
            "only_jbod3",
            21,
            20,
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that keep_free_space_bytes and keep_free_space_ratio
    options correctly limit the space available on the disk.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine, policy, size, max_size = example
        with When(f"for example table name='{name}', engine='{engine}'"):
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
                with When(
                    f"I insert data",
                    description=f"{size}MB when {max_size}MB is available",
                ):
                    data = []
                    for i in range(size):
                        data.append(get_random_string(cluster, 1024 * 1024))
                    values = ",".join(["('" + x + "')" for x in data])
                    query = f"INSERT INTO {name} VALUES {values}"
                    message = None
                    if size > max_size:
                        message = (
                            f"Exception: Cannot reserve {size}.00 MiB, not enough space"
                        )
                    node.query(
                        query,
                        message=message,
                        timeout=120,
                        max_query_output_in_bytes=1024,
                    )
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
