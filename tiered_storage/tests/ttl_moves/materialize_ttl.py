#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_used_disks_for_table, get_random_string
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("materialize ttl")
@Requirements(RQ_SRS_004_TTLExpressions_MaterializeTTL("1.0"))
@Examples(
    "name engine partitions_to_materialize",
    [
        ("mt_test_materialize_ttl", "MergeTree()", []),
        ("mt_test_materialize_ttl_0", "MergeTree()", [0]),
        ("mt_test_materialize_ttl_12", "MergeTree()", [1, 2]),
        ("mt_test_materialize_ttl_012", "MergeTree()", [0, 1, 2]),
        (
            "replicated_mt_materialize_ttl",
            "ReplicatedMergeTree('/clickhouse/replicated_test_materialize_ttl', '1')",
            [],
        ),
        (
            "replicated_mt_materialize_ttl_0",
            "ReplicatedMergeTree('/clickhouse/replicated_test_materialize_ttl_0', '1')",
            [0],
        ),
        (
            "replicated_mt_materialize_ttl_12",
            "ReplicatedMergeTree('/clickhouse/replicated_test_materialize_ttl_12', '1')",
            [1, 2],
        ),
        (
            "replicated_mt_materialize_ttl_012",
            "ReplicatedMergeTree('/clickhouse/replicated_test_materialize_ttl_012', '1')",
            [0, 1, 2],
        ),
    ],
    "%-30s | %-65s | %-7s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that MATERIALIZE TTL statement causes TTL expressions
    to be re-evaluated for existing parts either for the whole
    table or for some specific partitions.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine, partitions_to_materialize = example
        for positive in (True, False):
            with When(
                f"table name='{name}', engine='{engine}' and parts should {'be' if positive else 'not be'} moved"
            ):
                with Given(f"table name='{name}', engine='{engine}'"):
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            p1 Int64,
                            s1 String,
                            d1 DateTime
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        PARTITION BY p1
                        TTL d1 + INTERVAL 3000 SECOND TO DISK 'jbod2', 
                            d1 + INTERVAL 6000 SECOND TO VOLUME 'external'
                        SETTINGS storage_policy='jbods_with_external', merge_with_ttl_timeout=0
                    """
                    )
                    try:
                        with When("I insert data"):
                            for p in range(3):
                                data = []  # 2MB in total
                                now = time.time()
                                for i in range(2):
                                    p1 = p
                                    s1 = get_random_string(
                                        cluster, 1024 * 1024, steps=False
                                    )  # 1MB
                                    d1 = now - 1 if i > 0 or positive else now + 300
                                    data.append(f"({p1}, '{s1}', toDateTime({d1}))")
                                values = ",".join(data)
                                node.query(
                                    f"INSERT INTO {name} (p1, s1, d1) VALUES {values}"
                                )

                        with And("I get used disks for the table"):
                            time.sleep(30)
                            used_disks = get_used_disks_for_table(node, name)
                            with Then(f"parts have been placed using round-robin"):
                                assert set(used_disks) == {"jbod1", "jbod2"}, error()

                        with Then("number of rows should match"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            assert r == "6", error()

                        with When("I change TTL expressions using ALTER TABLE"):
                            node.query(
                                f"""
                                ALTER TABLE {name} MODIFY
                                TTL d1 + INTERVAL 0 SECOND TO DISK 'jbod2', 
                                    d1 + INTERVAL 35 SECOND TO VOLUME 'external',
                                    d1 + INTERVAL 120 SECOND DELETE
                            """
                            )

                        if not partitions_to_materialize:
                            with And("I materialize ttl in the whole table"):
                                node.query(
                                    f"ALTER TABLE {name} MATERIALIZE TTL SETTINGS mutations_sync=2"
                                )
                        else:
                            for partition in partitions_to_materialize:
                                with And(f"I materialize ttl in partition {partition}"):
                                    node.query(
                                        f"ALTER TABLE {name} MATERIALIZE TTL IN PARTITION {partition}"
                                    )

                        with When(
                            "I wait until second TTL expression triggers",
                            description="5 sec",
                        ):
                            time.sleep(5)

                            with Then("I check delete has not been triggered"):
                                r = node.query(
                                    f"SELECT count() FROM {name}"
                                ).output.strip()
                                assert r == "6", error()

                            with When(
                                "I get used disks for the table", description="20 sec"
                            ):
                                time.sleep(20)

                                for attempt in retries(timeout=60, delay=0.25):
                                    with attempt:
                                        used_disks = get_used_disks_for_table(
                                            node, name
                                        )
                                        if not positive:
                                            with Then(
                                                f"parts should not have been moved"
                                            ):
                                                assert set(used_disks) == {
                                                    "jbod1",
                                                    "jbod2",
                                                }, error()
                                        else:
                                            if not partitions_to_materialize or set(
                                                partitions_to_materialize
                                            ) == {0, 1, 2}:
                                                with Then(
                                                    f"all parts should have been moved"
                                                ):
                                                    assert set(used_disks) == {
                                                        "external"
                                                    }, error()
                                            else:
                                                with Then(
                                                    "some parts should have been moved"
                                                ):
                                                    assert "external" in set(
                                                        used_disks
                                                    ), error()

                            with Then("number of rows should still not have changed"):
                                r = node.query(
                                    f"SELECT count() FROM {name}"
                                ).output.strip()
                                assert r == "6", error()

                        with When(
                            "I wait until TTL expression to delete triggers",
                            description="5 sec",
                        ):
                            time.sleep(5)

                            with By(
                                "running optimize final to make sure delete completes"
                            ):
                                node.query(f"OPTIMIZE TABLE {name} FINAL")

                            for attempt in retries(timeout=300, delay=5):
                                with attempt:
                                    if not positive:
                                        with Then(f"number of rows should change"):
                                            r = node.query(
                                                f"SELECT count() FROM {name}"
                                            ).output.strip()
                                            assert r == "3", error()
                                    else:
                                        if not partitions_to_materialize or set(
                                            partitions_to_materialize
                                        ) == {0, 1, 2}:
                                            with Then(
                                                f"all rows should have been deleted"
                                            ):
                                                r = node.query(
                                                    f"SELECT count() FROM {name}"
                                                ).output.strip()
                                                assert r == "0", error()
                                        else:
                                            with Then(
                                                f"some rows should have been deleted"
                                            ):
                                                r = node.query(
                                                    f"SELECT count() FROM {name}"
                                                ).output.strip()
                                                assert (
                                                    r
                                                    < f"{ 6 - 2 * len(set(partitions_to_materialize)) }"
                                                ), error()

                    finally:
                        with Finally("I drop the table"):
                            node.query(f"DROP TABLE IF EXISTS {name} SYNC")
