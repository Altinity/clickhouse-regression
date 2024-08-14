#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import os
import random
from tiered_storage.tests.common import produce_alter_move
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestOutline(Scenario)
@Name("concurrent alter move with insert and select")
@Requirements(RQ_SRS_004_DataMovement_Locking("1.0"))
@Examples(
    "engine",
    [
        ["MergeTree()"],
        ["ReplicatedMergeTree('/clickhouse/concurrently_altering_replicated_mt', '1')"],
    ],
)
@Retry(3)
def scenario(self, engine):
    """Check that doing alter move, insert and select
    concurrently does not result in data loss and there should
    not be any duplicate parts on the disks.
    """
    cluster = self.context.cluster
    node = cluster.node("clickhouse1")
    table_name = "table_" + engine.split("(")[0].lower()

    random.seed(204)

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

    with And("I get table's uuid"):
        table_uuid = node.query(
            f"SELECT uuid FROM system.tables WHERE name = '{table_name}'"
        ).output.strip()
        table_uuid_prefix = table_uuid[:3]

    try:
        with And("I stop merges to avoid conflicts"):
            node.query(f"SYSTEM STOP MERGES {table_name}")

        def insert(i, num):
            with When(f"I insert {i} {num} values"):
                for i in range(num):
                    day = random.randint(11, 30)
                    value = random.randint(1, 1000000)
                    month = "0" + str(random.choice([3, 4]))
                    node.query(
                        f"INSERT INTO {table_name} VALUES(toDate('2019-{month}-{day}'), {value})",
                        steps=False,
                        timeout=120,
                    )

        def select_count(i, num):
            with When(f"I perform select {i} {num} times"):
                for i in range(num):
                    node.query(
                        f"SELECT sleepEachRow(0.001), COUNT() FROM {table_name} FORMAT TabSeparated",
                        steps=False,
                        timeout=120,
                    )

        def alter_move(i, num):
            with When(f"I perform alter move {i} {num} times"):
                for i in range(num):
                    produce_alter_move(
                        node,
                        table_name,
                        steps=False,
                        timeout=600,
                        raise_on_exception=True,
                        random_seed=327 * i,
                    )

        with When("in parallel I perform alter move, and select count"):
            with Pool(15) as p:
                tasks = []
                for i in range(5):
                    tasks.append(p.submit(alter_move, (i, 5)))
                    tasks.append(p.submit(insert, (i, 50)))
                    tasks.append(p.submit(select_count, (i, 100)))
                    tasks.append(p.submit(select_count, (i, 100)))

                for task in tasks:
                    task.result(timeout=1000)

        with When("I check the server is still up"):
            r = node.query("SELECT 1 FORMAT TabSeparated").output.strip()
            with Then("it should return the result of 1"):
                assert r == "1", error()

        with And("I ensure all rows are in the table"):
            r = node.query(
                f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated"
            ).output.strip()
            with Then("it should return the result of 250"):
                assert r == "250", error()

        with When("I check if there are any duplicate parts on the disks"):
            for retry in retries(timeout=60, delay=10):
                with retry:
                    jbod1_entries = set(
                        [
                            os.path.basename(entry)
                            for entry in node.command(
                                f"find /jbod1/store/{table_uuid_prefix}/{table_uuid}/ -name '20*'",
                                exitcode=0,
                            )
                            .output.strip()
                            .splitlines()
                        ]
                    )

                    jbod2_entries = set(
                        [
                            os.path.basename(entry)
                            for entry in node.command(
                                f"find /jbod2/store/{table_uuid_prefix}/{table_uuid}/ -name '20*'",
                                exitcode=0,
                            )
                            .output.strip()
                            .splitlines()
                        ]
                    )

                    if not (
                        hasattr(cluster, "with_minio")
                        and hasattr(cluster, "with_s3amazon")
                        and hasattr(cluster, "with_s3gcs")
                    ):
                        external_entries = set(
                            [
                                os.path.basename(entry)
                                for entry in node.command(
                                    f"find /external/store/{table_uuid_prefix}/{table_uuid}/ -name '20*'",
                                    exitcode=0,
                                )
                                .output.strip()
                                .splitlines()
                            ]
                        )
                    else:
                        external_entries = set()

                    with Then("there should be no duplicate parts"):
                        len_union = len(
                            jbod1_entries.union(jbod2_entries).union(external_entries)
                        )
                        len_entries = (
                            len(jbod1_entries)
                            + len(jbod2_entries)
                            + len(external_entries)
                        )
                        assert len_union == len_entries, error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
