#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import datetime
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("mutation update column in ttl")
@Requirements(RQ_SRS_004_TTLExpressions_Mutations_Update("1.0"))
@Examples(
    "name engine",
    [
        ("mt_mutation_update_column_in_ttl", "MergeTree()"),
        (
            "replicated_mutation_update_column_in_ttl",
            "ReplicatedMergeTree('/clickhouse/replicated_mutation_update_column_in_ttl', '1')",
        ),
    ],
    "%-31s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that update mutation in a column that is
    used in the TTL expression causes TTL re-evaluation.
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
                    PARTITION BY (date)
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
                    node.query(f"INSERT INTO {name} VALUES ({date(-1)},2,'fast{i}')")

            with When("I perform update mutation"):
                with By("updating ttl_days to 0"):
                    node.query(f"ALTER TABLE {name} UPDATE ttl_days = 0 WHERE 1")
                    node.query(f"OPTIMIZE TABLE {name}")

            with Then("TTL expressions should be re-evaluated"):
                with By("checking that all data has been deleted"):
                    r = node.query(f"SELECT * FROM {name}").output.strip()
                    assert r == "", error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")
