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
@Name("concurrent read")
@Requirements(
    RQ_SRS_004_AutomaticPartMovementInTheBackground_NoEffectOnQuerying("1.0"),
)
@Examples(
    "name engine",
    [
        ("mt_background_move_concurrent_read", "MergeTree()"),
        (
            "replicated_mt_background_move_concurrent_read",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_background_move_concurrent_read', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that moves performed in the background have no effect
    on queries when custom move factor is used.
    """
    with Given("cluster"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with When(f"for example table name='{name}', engine='{engine}'"):
            with When("I create table"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d1 UInt64,
                        s1 String
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    SETTINGS storage_policy='moving_jbod_with_external'
                """
                )
            try:
                with And("I stop moves and merges"):
                    node.query(f"SYSTEM STOP MOVES {name}")
                    node.query(f"SYSTEM STOP MERGES {name}")

                inserts = 240

                with And(
                    "I do a lot of small inserts",
                    description=f"{inserts} times 133 rows with 1k each",
                ):
                    data = []
                    for i in range(133):
                        data.append(get_random_string(cluster, 1 * 1024, steps=False))
                    values = ",".join([f"({k},'{x}')" for k, x in enumerate(data)])
                    node.query(
                        ";\n".join([f"INSERT INTO {name} VALUES {values}"] * inserts),
                        timeout=60,
                    )

                with And("I check used disks"):
                    used_disks = set(get_used_disks_for_table(node, name))
                    with Then("number of disk used should be 1"):
                        assert len(used_disks) == 1, error()
                    with And("disk used should be 'jbod1'"):
                        assert used_disks == {"jbod1"}, error()

                def select_count(i, num):
                    with When(f"I perform select {i} {num} times"):
                        with Then("result should be as expected"):
                            for i in range(num):
                                r = node.query(
                                    f"SELECT sum(d1) FROM {name}",
                                    steps=False,
                                    timeout=60,
                                ).output.strip()
                                if engine.startswith("Replicated"):
                                    # replicated tables do block deduplication
                                    assert r == f"{sum(range(133))}", error()
                                else:
                                    assert r == f"{inserts * sum(range(133))}", error()

                with When("I start performing select in parallel"):
                    with Pool(15) as p:
                        tasks = []
                        for i in range(5):
                            tasks.append(
                                p.submit(
                                    select_count,
                                    (
                                        i,
                                        25,
                                    ),
                                )
                            )
                            tasks.append(
                                p.submit(
                                    select_count,
                                    (
                                        i,
                                        25,
                                    ),
                                )
                            )

                        with When("I wait 5 sec to restart moves"):
                            time.sleep(5)

                        with And("I restart moves"):
                            node.query(f"SYSTEM START MOVES {name}")

                        with And("I wait for parallel selects to complete"):
                            for task in tasks:
                                task.result(timeout=600)

                with And("I check used disks after selects"):
                    used_disks = set(get_used_disks_for_table(node, name))
                    # FIXME: all parts are moved to external?
                    # with Then("number of disk used should be 2"):
                    #    assert len(used_disks) == 2, error()
                    # with And("disks used should be 'jbod1' and 'external'"):
                    #    assert used_disks == {'jbod1', 'external'}, error()
                    with Then("one of the disks should be 'external'"):
                        assert "external" in used_disks, error()
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
