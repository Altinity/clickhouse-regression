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


@TestScenario
@Name("concurrent alter move and select")
@Examples(
    "name engine",
    [
        ("concurrently_altering_mt", "MergeTree()"),
        (
            "concurrently_altering_replicated_mt",
            "ReplicatedMergeTree('/clickhouse/concurrently_altering_replicated_mt', '1')",
        ),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that doing alter move, and select
    concurrently does not result in data loss and there should
    not be any duplicate parts on the disks.
    """
    random.seed(203)
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

            with And("I get table's uuid"):
                table_uuid = node.query(
                    f"SELECT uuid FROM system.tables WHERE name = '{name}'"
                ).output.strip()
                table_uuid_prefix = table_uuid[:3]

            try:
                with And("I stop merges to avoid conflicts"):
                    node.query(f"SYSTEM STOP MERGES {name}")

                def insert(i, num):
                    with When(f"I insert {i} {num} values"):
                        for i in range(num):
                            day = random.randint(11, 30)
                            value = random.randint(1, 1000000)
                            month = "0" + str(random.choice([3, 4]))
                            node.query(
                                f"INSERT INTO {name} VALUES(toDate('2019-{month}-{day}'), {value})",
                                steps=False,
                                timeout=60,
                            )

                def select_count(i, num):
                    with When(f"I perform select {i} {num} times"):
                        with Then("result should always be 500"):
                            for i in range(num):
                                for attempt in retries(timeout=60, delay=1):
                                    with attempt:
                                        r = node.query(
                                            f"SELECT sleepEachRow(0.1), COUNT() FROM {name}",
                                            steps=False,
                                            timeout=60,
                                        ).output.strip()
                                        assert r == "0\t500", error()

                def alter_move(i, num):
                    with When(f"I perform alter move {i} {num} times"):
                        for i in range(num):
                            produce_alter_move(
                                node,
                                name,
                                steps=False,
                                timeout=2400,
                                raise_on_exception=True,
                                random_seed=371 * i,
                            )

                with When("I first prepare table"):
                    for i in range(5):
                        insert(i, 100)

                with When("in parallel I perform alter move, and select count"):
                    with Pool(15) as p:
                        tasks = []
                        for i in range(5):
                            tasks.append(
                                p.submit(
                                    alter_move,
                                    (
                                        i,
                                        5,
                                    ),
                                )
                            )
                            tasks.append(
                                p.submit(
                                    select_count,
                                    (
                                        i,
                                        100,
                                    ),
                                )
                            )
                            tasks.append(
                                p.submit(
                                    select_count,
                                    (
                                        i,
                                        100,
                                    ),
                                )
                            )

                        for task in tasks:
                            task.result(timeout=2400)

                with When("I check the server is still up"):
                    r = node.query("SELECT 1").output.strip()
                    with Then("it should return the result of 1"):
                        assert r == "1", error()

                for attempt in retries(timeout=30, delay=5):
                    with attempt:
                        with When("I ensure all rows are in the table"):
                            r = node.query(f"SELECT COUNT() FROM {name}").output.strip()
                        with Then("it should return the result of 500"):
                            assert r == "500", error()

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
                                    jbod1_entries.union(jbod2_entries).union(
                                        external_entries
                                    )
                                )
                                len_entries = (
                                    len(jbod1_entries)
                                    + len(jbod2_entries)
                                    + len(external_entries)
                                )
                                assert len_union == len_entries, error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
