#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from testflows.asserts import error

from tiered_storage.tests.common import get_used_disks_for_table
from tiered_storage.requirements import *


@TestScenario
@Name("startup and queries")
@Requirements(
    RQ_SRS_004_Configuration_Startup("1.0"),
    RQ_SRS_004_MultipleStorageDevices_Queries("1.0"),
)
@Examples(
    "name engine",
    [
        ("mt_startup_and_queries", "MergeTree()"),
        (
            "replicated_mt_startup_and_queries",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_startup_and_queries', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1", count=10000):
    """Check that table storage configuration that includes multiple disks
    is read during startup and information about location of parts is preserved.
    After startup, queries can be executed against the table.
    """
    with Given("cluster"):
        node = cluster.node(node)
        for example in self.examples:
            name, engine = example
            with When(f"for example table name='{name}', engine='{engine}'"):
                try:
                    with When(f"I create table"):
                        node.query(
                            f"""
                            CREATE TABLE {name} (
                                d UInt64
                            ) ENGINE = {engine}
                            ORDER BY d
                            SETTINGS storage_policy='jbods_with_external'
                        """
                        )

                    def insert_data(number_of_mb, start=0):
                        values = ",".join(
                            f"({x})"
                            for x in range(
                                start, int((1024 * 1024 * number_of_mb) / 8) + start + 1
                            )
                        )
                        node.query(
                            f"INSERT INTO {name} VALUES {values}",
                            settings=[
                                ("max_insert_block_size", number_of_mb * 1024 * 1024)
                            ],
                        )

                    with And("I stop merges to avoid conflicts"):
                        node.query(f"SYSTEM STOP MERGES {name}")

                    with And(
                        "I add data to the table such that it will be broken between disks and volumes"
                    ):
                        with By(
                            "first inserting 1MB of data",
                            description="should go to main volume jbod1",
                        ):
                            insert_data(1, 0)

                        with And(
                            "another insert of 1MB of data",
                            description="should go to main volume jbod2",
                        ):
                            insert_data(1, 1024 * 1024)

                        with And(
                            "large insert of 10Mb of data",
                            description="should go to the external volume",
                        ):
                            insert_data(10, 1024 * 1024 * 2)

                    with When("I get used disk for the table"):
                        used_disks = get_used_disks_for_table(node, name)
                        with Then("parts should be spread out between all the disks"):
                            assert len(used_disks) == 3, error()
                        expected = ["jbod1", "jbod2", "external"]
                        with And(
                            "should match the expected", description=str(expected)
                        ):
                            assert used_disks == expected, error()

                    def check_query(num, query, expected):
                        with By(f"executing query {num}", description=query):
                            r = node.query(query).output.strip()
                            with Then(
                                f"result should match the expected",
                                description=expected,
                            ):
                                assert r == expected, error()

                    with And("I check a simple query before restart"):
                        check_query(
                            0, f"SELECT COUNT() FROM {name} FORMAT TabSeparated", expected="1572867"
                        )

                    with And("I restart the clickhouse node"):
                        node.restart()

                    with When("I check simple queries"):
                        check_query(
                            0, f"SELECT COUNT() FROM {name} FORMAT TabSeparated", expected="1572867"
                        )
                        check_query(
                            1,
                            f"SELECT uniqExact(d) FROM {name} WHERE d < 10 FORMAT TabSeparated",
                            expected="10",
                        )
                        check_query(
                            2,
                            f"SELECT d FROM {name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
                            expected="3407872",
                        )
                        check_query(
                            3,
                            f"SELECT d FROM {name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
                            expected="0",
                        )
                        check_query(
                            4,
                            f"SELECT * FROM {name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d FORMAT TabSeparated",
                            expected="0\n1048578\n2097154",
                        )
                        check_query(
                            5,
                            f"SELECT * FROM (SELECT d FROM {name} WHERE d == 1) FORMAT TabSeparated",
                            expected="1",
                        )

                finally:
                    with Finally("I drop the table if exists"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
