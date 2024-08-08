#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import random

from testflows.core import *
from testflows.asserts import error

from helpers.common import check_clickhouse_version
from tiered_storage.tests.common import produce_alter_move


@TestOutline(Scenario)
@Name("concurrent alter move")
@Examples(
    "engine",
    [
        ["MergeTree()"],
        ["ReplicatedMergeTree('/clickhouse/concurrently_altering_replicated_mt', '1')"],
    ],
)
def scenario(self, engine):
    """Check that doing insert, alter move, alter update
    and optimize table concurrently does not result
    in data loss.
    """
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    table_name = "table_" + engine.split("(")[0].lower()

    random.seed(200)

    OPTIMIZE_FINAL_TIMEOUT = 200
    if check_clickhouse_version(">=24.4")(self):
        # https://github.com/ClickHouse/ClickHouse/pull/62067
        OPTIMIZE_FINAL_TIMEOUT = 600

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
                        raise_on_exception=True,
                    )

        def alter_move(num):
            with When(f"I perform alter move {num} times"):
                for i in range(num):
                    produce_alter_move(
                        node,
                        table_name,
                        steps=False,
                        timeout=360,
                        raise_on_exception=True,
                        random_seed=321 * (i + 1),
                    )

        def alter_update(num):
            with When(f"I update {num} values"):
                for i in range(num):
                    for attempt in retries(timeout=30, delay=5):
                        with attempt:
                            node.query(
                                f"ALTER TABLE {table_name} UPDATE number = number + 1 WHERE 1",
                                steps=False,
                                timeout=60,
                                raise_on_exception=True,
                            )

        def optimize_table(num):
            with When(f"I optimize table {num} times"):
                for i in range(num):
                    node.query(
                        f"OPTIMIZE TABLE {table_name} FINAL",
                        steps=False,
                        timeout=OPTIMIZE_FINAL_TIMEOUT,
                        raise_on_exception=True,
                    )

        with When(
            "in parallel I perform insert, alter move, update and optimize table"
        ):
            with Pool(15) as p:
                n_batches = 50
                n_inserts = 200
                n_other_queries_each = 500
                n_other_per_batch = n_other_queries_each // n_batches
                tasks = []
                for i in range(n_batches):
                    tasks.append(p.submit(insert, (n_inserts // n_batches,)))
                    tasks.append(p.submit(alter_move, (n_other_per_batch,)))
                    tasks.append(p.submit(alter_update, (n_other_per_batch,)))
                    tasks.append(p.submit(optimize_table, (n_other_per_batch,)))

                for task in tasks:
                    task.result(timeout=OPTIMIZE_FINAL_TIMEOUT * 3)

        with When("I check the server is still up"):
            r = node.query("SELECT 1 FORMAT TabSeparated").output.strip()
            with Then("it should return the result of 1"):
                assert r == "1", error()

        for retry in retries(timeout=30, delay=5):
            with retry:
                with When("I ensure all rows are in the table"):
                    r = node.query(
                        f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
                    ).output.strip()
                    with Then("it should return the result of 500"):
                        assert r == str(n_inserts), error()
    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC", timeout=360)
