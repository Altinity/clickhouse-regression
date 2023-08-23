#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import random
from tiered_storage.tests.common import produce_alter_move
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("concurrent alter move and drop")
@Examples(
    "name engine",
    [
        ("concurrently_dropping_mt", "MergeTree()"),
        (
            "concurrently_dropping_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/concurrently_dropping_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that doing insert, alter move, alter drop or detach partition
    concurrently does not cause server to crash.
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
                        number UInt64
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    PARTITION BY toYYYYMM(EventDate)
                    SETTINGS storage_policy='jbods_with_external'
                """
                )
            try:

                def insert(num):
                    with When(f"I perform insert {num} times"):
                        for i in range(num):
                            day = random.randint(11, 30)
                            value = random.randint(1, 1000000)
                            month = "0" + str(random.choice([3, 4]))
                            node.query(
                                f"INSERT INTO {name} VALUES(toDate('2019-{month}-{day}'), {value})",
                                steps=False,
                                timeout=240,
                                raise_on_exception=False,
                            )

                def alter_move(num):
                    with When(f"I perform alter move {num} times"):
                        for i in range(num):
                            produce_alter_move(
                                node,
                                name,
                                steps=False,
                                raise_on_exception=True,
                                timeout=240,
                            )

                def alter_drop(num):
                    with When(f"I perform alter drop or detach partition {num} times"):
                        for i in range(num):
                            partition = random.choice([201903, 201904])
                            action = random.choice(["drop", "detach"])
                            node.query(
                                f"ALTER TABLE {name} {action} PARTITION {partition}",
                                steps=False,
                                timeout=60,
                            )

                with When("I first prepare table"):
                    insert(100)

                with And(
                    "in parallel I perform insert, alter move, update and optimize table"
                ):
                    with Pool(15) as p:
                        tasks = []
                        for i in range(5):
                            tasks.append(p.submit(insert, (100,)))
                            tasks.append(p.submit(alter_move, (100,)))
                            tasks.append(p.submit(alter_drop, (100,)))

                        for task in tasks:
                            task.result(timeout=600)

                with When("I check the server is still up"):
                    r = node.query("SELECT 1").output.strip()
                    with Then("it should return the result of 1"):
                        assert r == "1", error()
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
