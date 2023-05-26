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
@Name("multi column ttl")
@Requirements(RQ_SRS_004_TTLExpressions_MultipleColumns("1.0"))
@Examples(
    "name engine",
    [
        ("mt_multi_column_ttl", "MergeTree()"),
        (
            "replicated_mt_multi_column_ttl",
            "ReplicatedMergeTree('/clickhouse/replicated_multi_column_ttl', '1')",
        ),
    ],
    "%-31s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that TTL expression can use multiple columns
    and arithmetic operations.
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

            def date(offset):
                date = (
                    datetime.datetime.now() + datetime.timedelta(days=offset)
                ).strftime("%Y-%m-%d")
                return f"toDate('{date}')"

            with When("I check free space on disks"):
                node.query("SELECT * FROM system.disks FORMAT JSON")

            with And("I check storage policies"):
                node.query(
                    "SELECT * FROM system.storage_policies WHERE policy_name = 'fast_med_and_slow' FORMAT JSON"
                )

            with When("I insert data that would fall into different TTL expressions"):
                node.query(f"INSERT INTO {name} VALUES ({date(0)},2,'fast')")
                node.query(f"INSERT INTO {name} VALUES ({date(-1.1)},1,'medium')")
                node.query(f"INSERT INTO {name} VALUES ({date(-2.1*4)},2,'slow')")
                node.query(f"INSERT INTO {name} VALUES ({date(-4*24)},3,'delete')")

            with And("I run optimize tablt to trigger delete"):
                node.query(f"OPTIMIZE TABLE {name} FINAL")

            for retry in retries(timeout=60, delay=1):
                with retry:
                    with When("I read data from the table"):
                        with By("reading number of rows"):
                            r = node.query(f"SELECT count() FROM {name}").output.strip()
                            with Then(
                                "checking that the rows that fall into TTL delete expression not to be present"
                            ):
                                assert r == "3", error()

                        with By("reading actual data"):
                            r = (
                                node.query(f"SELECT value FROM {name} ORDER BY value")
                                .output.strip()
                                .splitlines()
                            )
                            with Then("checking the expected data is there"):
                                assert r == ["fast", "medium", "slow"], error()

            with When(
                "I check that disks that should be used according to TTL expressions"
            ):
                with By("getting disks name from system.parts"):
                    node.query(
                        f"SELECT partition, disk_name FROM system.parts WHERE table = '{name}' AND active = 1 FORMAT Vertical"
                    )
                    disks = node.query(
                        f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                        " AND active = 1"
                    ).output.splitlines()
                with Then("checking disk names"):
                    assert set(disks) == {"jbod1", "jbod2", "external"}, error()

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")
