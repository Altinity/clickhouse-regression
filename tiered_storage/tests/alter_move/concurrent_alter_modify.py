#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import random
from tiered_storage.tests.common import produce_alter_move, QueryRuntimeException
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("concurrent alter modify")
@Examples(
    "name engine",
    [
        ("alter_modifying_mt", "MergeTree()"),
        (
            "replicated_alter_modifying_mt",
            "ReplicatedMergeTree('/clickhouse/replicated_alter_modifying_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check concurrent alter move and alter modify
    does not crash the server or cause data loss.
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
                    with When(f"I insert {num} values"):
                        for i in range(num):
                            day = random.randint(11, 30)
                            value = random.randint(1, 1000000)
                            month = "0" + str(random.choice([3, 4]))
                            node.query(
                                f"INSERT INTO {name} VALUES(toDate('2019-{month}-{day}'), {value})",
                                steps=False,
                                timeout=60,
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

                def alter_modify(num):
                    with When(f"I perform alter modify {num} times"):
                        for i in range(num):
                            column_type = random.choice(["UInt64", "String"])
                            try:
                                node.query(
                                    f"ALTER TABLE {name} MODIFY COLUMN number {column_type}",
                                    steps=False,
                                    raise_on_exception=True,
                                    timeout=60,
                                )
                            except QueryRuntimeException:
                                pass

                with When("I first prepare table"):
                    insert(100)
                    with And("I count number of rows"):
                        r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("the count should be 100"):
                        assert r == "100", error()

                with When("in parallel I perform alter move and alter modify"):
                    with Pool(50) as p:
                        tasks = []
                        for i in range(5):
                            tasks.append(p.submit(alter_move, (100,)))
                            tasks.append(p.submit(alter_modify, (100,)))

                        for task in tasks:
                            task.result(timeout=600)

                with When("I check the server is still up"):
                    r = node.query("SELECT 1").output.strip()
                    with Then("it should return the result of 1"):
                        assert r == "1", error()

                with And("I ensure that number of rows in the table has not changed"):
                    r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                    with Then("it should return the count of 100"):
                        assert r == "100", error()
            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
