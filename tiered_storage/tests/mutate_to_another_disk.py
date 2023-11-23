#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from tiered_storage.tests.common import get_random_string

from testflows.core import TestScenario, Name, Examples
from testflows.core import Given, When, By, And, Then, Finally, current
from testflows.asserts import error


@TestScenario
@Name("mutate to another disk")
@Examples(
    "name engine",
    [
        ("mutating_mt", "MergeTree()"),
        (
            "replicated_mutating_mt",
            "ReplicatedMergeTree('/clickhouse/replicated_mutating_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that mutation if not completed
    can succeed after parts are merged
    and moved to another disk.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with When(f"for example table name='{name}', engine='{engine}'"):
            with When("I create table"):
                node.query(
                    f"""
                    DROP TABLE IF EXISTS {name} SYNC;
                    CREATE TABLE {name} (
                        s1 String
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    SETTINGS storage_policy='moving_jbod_with_external'
                """
                )
            try:
                with When("I insert some data"):
                    for i in range(5):
                        data = []
                        for i in range(5):
                            data.append(
                                get_random_string(cluster, 1024 * 1024, steps=False)
                            )
                        values = ",".join(["('" + x + "')" for x in data])
                        node.query(f"INSERT INTO {name} VALUES {values}", steps=False)

                with When("I count number of rows"):
                    r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("the count should be 25"):
                        assert r == "25"

                with When("I do an update"):
                    node.query(
                        f"ALTER TABLE {name} UPDATE s1 = concat(s1, 'x') WHERE 1",
                        exitcode=0,
                    )

                def wait_mutation_completes(retry, sleep):
                    sql = "SELECT * FROM system.mutations WHERE is_done = 0"
                    with By(
                        f"polling until there are no mutations or max {retry} count is reached",
                        description=sql,
                    ):
                        while (
                            node.query(sql, steps=False).output.strip() != ""
                            and retry > 0
                        ):
                            retry -= 1
                            time.sleep(sleep)

                with When("I wait until mutation completes"):
                    wait_mutation_completes(retry=20, sleep=3)

                with When("I check if mutation status"):
                    r = node.query(
                        f"SELECT latest_fail_reason FROM system.mutations WHERE table = '{name}'"
                    ).output.strip()
                    if r == "":
                        with When("I see that mutation did not fail"):
                            with Then("mutation should have been applied"):
                                r = node.query(
                                    f"SELECT sum(endsWith(s1, 'x')) FROM {name}"
                                ).output.strip()
                                assert r == "25", error()
                    else:
                        with When("I see that mutation has failed"):
                            with And("I try it on another disk"):
                                node.query(f"OPTIMIZE TABLE {name} FINAL")
                                node.query(
                                    f"ALTER TABLE {name} UPDATE s1 = concat(s1, 'x') WHERE 1",
                                    exitcode=0,
                                )
                            with And("I wait until mutation completes"):
                                wait_mutation_completes(retry=20, sleep=1)
                            with Then("mutation should have been applied"):
                                r = node.query(
                                    f"SELECT sum(endsWith(s1, 'x')) FROM {name}"
                                ).output.strip()
                                assert r == "25", error()
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
