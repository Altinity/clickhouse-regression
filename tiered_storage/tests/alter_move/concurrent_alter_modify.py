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
from testflows.uexpect import ExpectTimeoutError


@TestOutline(Scenario)
@Name("concurrent alter modify")
@Examples(
    "engine",
    [
        ["MergeTree()"],
        ["ReplicatedMergeTree('/clickhouse/replicated_alter_modifying_mt', '1')"],
    ],
)
def scenario(self, engine):
    """Check concurrent alter move and alter modify
    does not crash the server or cause data loss.
    """
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    table_name = "table_" + engine.split("(")[0].lower()
    random.seed(201)

    with When("I create table"):
        node.query(
            f"""
            DROP TABLE IF EXISTS {table_name} SYNC;
            CREATE TABLE {table_name} (
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
                        f"INSERT INTO {table_name} VALUES(toDate('2019-{month}-{day}'), {value})",
                        steps=False,
                        timeout=60,
                    )

        def alter_move(num):
            with When(f"I perform alter move {num} times"):
                for i in range(num):
                    produce_alter_move(
                        node,
                        table_name,
                        steps=False,
                        raise_on_exception=True,
                        timeout=240,
                        random_seed=231 * i,
                    )

        def alter_modify(num):
            with When(f"I perform alter modify {num} times"):
                for i in range(num):
                    column_type = random.choice(["UInt64", "String"])
                    try:
                        node.query(
                            f"ALTER TABLE {table_name} MODIFY COLUMN number {column_type}",
                            steps=False,
                            raise_on_exception=True,
                            timeout=30,
                            retry_count=10,
                            retry_delay=60,
                        )
                    except QueryRuntimeException:
                        pass
                    except ExpectTimeoutError as e:
                        r = node.query(
                            "SELECT * FROM system.mutations WHERE is_done=0 FORMAT Vertical",
                            no_checks=True,
                        )
                        assert r.output.strip() == "", error(
                            "ALTER timed out due to stuck mutation:\n" + r.output
                        )
                        raise e

        with When("I first prepare table"):
            insert(100)
            with And("I count number of rows"):
                r = node.query(
                    f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
                ).output.strip()
            with Then("the count should be 100"):
                assert r == "100", error()

        with When("in parallel I perform alter move and alter modify"):
            with Pool(50) as p:
                tasks = []
                for i in range(5):
                    tasks.append(p.submit(alter_move, (100,)))
                    tasks.append(p.submit(alter_modify, (100,)))

                for task in tasks:
                    task.result(timeout=900)

        with When("I check the server is still up"):
            r = node.query("SELECT 1 FORMAT TabSeparated").output.strip()
            with Then("it should return the result of 1"):
                assert r == "1", error()

        with And("I ensure that number of rows in the table has not changed"):
            r = node.query(
                f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
            ).output.strip()
            with Then("it should return the count of 100"):
                assert r == "100", error()
    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", timeout=500)
