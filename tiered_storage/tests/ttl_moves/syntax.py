#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *
from helpers.common import *


@TestScenario
@Name("syntax")
@Requirements(
    RQ_SRS_004_TTLExpressions_Syntax("1.0"), RQ_SRS_004_TTLExpressions_Evaluation("1.0")
)
@Examples(
    "name engine",
    [
        ("mt_test_inserts_to_disk", "MergeTree()"),
        (
            "replicated_mt_test_inserts_to_disk",
            "ReplicatedMergeTree('/clickhouse/replicated_test_inserts_to_disk', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check support for TTL expression syntax to move data to a disk or a volume."""
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with When(f"table name='{name}', engine='{engine}'"):
            with When("I create table with TTL expression that evaluates to DateTime"):
                try:
                    node.query(
                        f"""
                           CREATE TABLE {name} (
                               s1 String,
                               d1 DateTime
                           ) ENGINE = {engine}
                           ORDER BY tuple()
                           TTL d1 TO DISK 'jbod1'
                           SETTINGS storage_policy='jbods_with_external'
                       """
                    )
                    with Then("a simple select works"):
                        node.query(f"SELECT * FROM {name}")
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

            with When("I create table with TTL expression that evaluates to Date"):
                try:
                    node.query(
                        f"""
                           CREATE TABLE {name} (
                               s1 String,
                               d1 Date
                           ) ENGINE = {engine}
                           ORDER BY tuple()
                           TTL d1 TO DISK 'jbod1'
                           SETTINGS storage_policy='jbods_with_external'
                       """
                    )
                    with Then("a simple select works"):
                        node.query(f"SELECT * FROM {name}")
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

            with When(
                "I create table with TTL expressions that includes explicit delete"
            ):
                try:
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String,
                            d1 DateTime
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        TTL d1 + INTERVAL 2 DAY TO DISK 'jbod1', 
                            d1 + INTERVAL 4 DAY TO DISK 'jbod2',
                            d1 + INTERVAL 6 DAY TO VOLUME 'external',
                            d1 + INTERVAL 8 DAY DELETE
                        SETTINGS storage_policy='jbods_with_external'
                    """
                    )
                    with Then("a simple select works"):
                        node.query(f"SELECT * FROM {name}")
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

            with When(
                "I create table with TTL expressions that includes implicit delete"
            ):
                try:
                    node.query(
                        f"""
                        CREATE TABLE {name} (
                            s1 String,
                            d1 DateTime
                        ) ENGINE = {engine}
                        ORDER BY tuple()
                        TTL d1 + INTERVAL 2 DAY TO DISK 'jbod1', 
                            d1 + INTERVAL 4 DAY TO DISK 'jbod2',
                            d1 + INTERVAL 6 DAY TO VOLUME 'external',
                            d1 + INTERVAL 8 DAY
                        SETTINGS storage_policy='jbods_with_external'
                    """
                    )
                    with Then("a simple select works"):
                        node.query(f"SELECT * FROM {name}")
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")

            with When(
                "I create table with TTL expressions that specifies invalid disk"
            ):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        s1 String,
                        d1 DateTime
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    TTL d1 + INTERVAL 2 DAY TO DISK 'jbod1', 
                        d1 + INTERVAL 4 DAY TO DISK 'jbod3',
                        d1 + INTERVAL 6 DAY TO VOLUME 'external',
                        d1 + INTERVAL 8 DAY
                    SETTINGS storage_policy='jbods_with_external'
                """,
                    exitcode=194,
                    message="Exception: No such disk `jbod3`",
                )

            with When(
                "I create table with TTL expressions that specifies invalid volume"
            ):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        s1 String,
                        d1 DateTime
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    TTL d1 + INTERVAL 2 DAY TO DISK 'jbod1', 
                        d1 + INTERVAL 4 DAY TO DISK 'jbod2',
                        d1 + INTERVAL 6 DAY TO VOLUME 'external2',
                        d1 + INTERVAL 8 DAY
                    SETTINGS storage_policy='jbods_with_external'
                """,
                    exitcode=36 if check_clickhouse_version("<22.3")(self) else 194,
                    message="Exception: No such volume `external2`",
                )

            with When(
                "I create table with TTL expressions that specifies invalid policy"
            ):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        s1 String,
                        d1 DateTime
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    TTL d1 + INTERVAL 2 DAY TO DISK 'jbod1', 
                        d1 + INTERVAL 4 DAY TO DISK 'jbod2',
                        d1 + INTERVAL 6 DAY TO VOLUME 'external',
                        d1 + INTERVAL 8 DAY
                    SETTINGS storage_policy='jbods_with_external2'
                """,
                    exitcode=222,
                    message="Exception: Unknown storage policy `jbods_with_external2`",
                )

            with When(
                "I create table with TTL expressions that do not evaulate to Date or DateTime"
            ):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        s1 String,
                        d1 DateTime
                    ) ENGINE = {engine}
                    ORDER BY tuple()
                    TTL s1 TO DISK 'jbod1', 
                        s1 TO DISK 'jbod2',
                        s1 TO VOLUME 'external',
                        s1 DELETE
                    SETTINGS storage_policy='jbods_with_external'
                """,
                    exitcode=194,
                    message="Exception: TTL expression result column should have DateTime or Date type, but has String",
                )
