#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import time
import datetime
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("mutation delete column in ttl")
@Requirements(RQ_SRS_004_TTLExpressions_Mutations_Delete("1.0"))
@Examples(
    "name engine",
    [
        ("mt_mutation_delete_column_in_ttl", "MergeTree()"),
        (
            "replicated_mutation_delete_column_in_ttl",
            "ReplicatedMergeTree('/clickhouse/replicated_mutation_delete_column_in_ttl', '1')",
        ),
    ],
    "%-31s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that delete mutation in a column that is
    used in the TTL expression works.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        try:
            with Given(f"table name='{name}', engine='{engine}'"):
                node.query(
                    f"""
                    CREATE TABLE {name}
                    (
                        date Date,
                        ttl_days UInt16,
                        value String
                    )
                    ENGINE = {engine}
                    PARTITION BY (date, ttl_days)
                    ORDER BY (date, value)
                    TTL date + INTERVAL ttl_days DAY TO VOLUME 'medium',
                        date + INTERVAL (ttl_days * 4) DAY TO VOLUME 'slow',
                        date + INTERVAL (ttl_days * 24) DAY DELETE
                    SETTINGS storage_policy='fast_med_and_slow'
                """
                )

            def date(offset, convert=True):
                date = (
                    datetime.datetime.now() + datetime.timedelta(days=offset)
                ).strftime("%Y-%m-%d")
                if convert:
                    return f"toDate('{date}')"
                else:
                    return date

            with And("some yesterday's data in the table"):
                for i in range(4):
                    node.query(f"INSERT INTO {name} VALUES ({date(-1)},{i},'fast{i}')")

            delete_value = 3

            with And("check that the data to be deleted is there"):
                r = node.query(
                    f"SELECT ttl_days FROM {name} WHERE ttl_days = {delete_value}"
                ).output.strip()
                assert r == f"{delete_value}", error()

            with And("I perform delete mutation"):
                with By("deleting the row"):
                    node.query(
                        f"ALTER TABLE {name} DELETE WHERE ttl_days = {delete_value}"
                    )

            with And("I run optimize table final to make sure mutation takes place"):
                node.query(f"OPTIMIZE TABLE {name} FINAL")
                time.sleep(5)

            with Then("checking that row has been deleted"):
                r = (
                    node.query(f"SELECT ttl_days FROM {name} ORDER BY ttl_days")
                    .output.strip()
                    .splitlines()
                )
                assert r == ["1", "2"], error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")
