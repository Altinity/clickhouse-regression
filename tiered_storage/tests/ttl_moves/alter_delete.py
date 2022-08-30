#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("alter delete")
@Requirements(RQ_SRS_004_TTLExpressions_Compatibility("1.0"))
@Examples(
    "name engine",
    [
        ("mt_alter_delete", "MergeTree()"),
        (
            "replicated_mt_alter_delete",
            "ReplicatedMergeTree('/clickhouse/replicated_test_mt_alter_delete', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check compatibility with old TTL delete expressions to make sure
    that:
    * alter modify of column's TTL delete expression works
    * alter to add new columns works
    * alter modify to add TTL delete expression to a a new column works
    for a table that has TTL delete expression defined but
    no explicit storage policy assigned.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with Given(f"table name='{name}', engine='{engine}'"):
            node.query(
                f"""
                CREATE TABLE {name} (
                    s1 String,
                    d1 DateTime
                ) ENGINE = {engine}
                ORDER BY tuple()
                TTL d1 + INTERVAL 1 DAY DELETE
            """
            )
            try:
                with When("I modify TTL delete expression on a column"):
                    node.query(
                        f"""ALTER TABLE {name} MODIFY COLUMN s1 String TTL d1 + INTERVAL 1 SECOND"""
                    )

                with When("I add new column"):
                    node.query(f"""ALTER TABLE {name} ADD COLUMN b1 Int32""")

                with When("I now insert data into table"):
                    node.query(
                        f"""INSERT INTO {name} (s1, b1, d1) VALUES ('hello1', 1, toDateTime({time.time()}))"""
                    )
                    node.query(
                        f"""INSERT INTO {name} (s1, b1, d1) VALUES ('hello2', 2, toDateTime({time.time() + 360}))"""
                    )

                with And("I wait for TTL on a column to expire"):
                    time.sleep(1)

                with And("I optimize table to make sure TTL has executed"):
                    node.query(f"OPTIMIZE TABLE {name}")

                with And("I read data from the table"):
                    r = (
                        node.query(f"SELECT s1, b1, d1 FROM {name} ORDER BY b1")
                        .output.strip()
                        .splitlines()
                    )

                with Then("check that row where TTL has expired is not there"):
                    assert len(r) == 2, error()
                    assert r[0].startswith("1\t"), error()
                    assert r[1].startswith("hello2\t2"), error()

                with When("I add TTL delete expression on a new column"):
                    node.query(f"""ALTER TABLE {name} MODIFY COLUMN b1 Int32 TTL d1""")

                with When("I again insert data into table"):
                    node.query(
                        f"""INSERT INTO {name} (s1, b1, d1) VALUES ('hello3', 3, toDateTime({time.time()}))"""
                    )
                with And("I again wait for TTL on a column to expire"):
                    time.sleep(1)

                with And("I again optimize table to make sure TTL has executed"):
                    node.query(f"OPTIMIZE TABLE {name}")

                with And("I again read data from the table"):
                    r = (
                        node.query(f"SELECT s1, b1, d1 FROM {name} ORDER BY b1")
                        .output.strip()
                        .splitlines()
                    )

                with Then("again check that row where TTL has expired is not there"):
                    assert len(r) == 3, error()
                    assert r[0].startswith("0\t"), error()
                    assert r[1].startswith("\t0\t"), error()
                    assert r[2].startswith("hello2\t2"), error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
