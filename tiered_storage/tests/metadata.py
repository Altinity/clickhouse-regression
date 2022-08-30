#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import re

from tiered_storage.tests.common import get_used_disks_for_table
from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("metadata")
@Requirements(RQ_SRS_004_MultipleStorageDevices_TableMetadata("1.0"))
@Examples(
    "name engine",
    [
        ("mt_metadata", "MergeTree()"),
        (
            "replicated_mt_metadata",
            "ReplicatedMergeTree('/clickhouse/replicated_mt_metadata', '1')",
        ),
    ],
    "%-21s | %-20s",
)
def scenario(self, cluster, node="clickhouse1", count=10000):
    """Check that table metadata is stored only
    on the default disk when table has storage policy
    that has multiple disks.
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
                        used_disks = set(get_used_disks_for_table(node, name))
                        with Then("parts should be spread out between all the disks"):
                            assert len(used_disks) == 3, error()
                        expected = {"jbod1", "jbod2", "external"}
                        with And(
                            "should match the expected",
                            description=str(expected),
                            format_description=False,
                        ):
                            assert used_disks == expected, error()

                    with Then("check the metadata should exist on the default disk"):
                        node.command("ls /var/lib/clickhouse/metadata", exitcode=0)

                    with And(
                        "metadata folder should not exist on other disks that store table parts"
                    ):
                        node.command(f"find /jbod1 | grep {name}.sql", exitcode=1)
                        node.command(f"find /jbod2 | grep {name}.sql", exitcode=1)
                        node.command(f"find /external | grep {name}.sql", exitcode=1)

                    expected = f"/var/lib/clickhouse/store/.*?/{name}.sql"
                    with And(
                        "metadata_path column in system.tables points to the default disk",
                        description=expected,
                    ):
                        path = node.query(
                            f"SELECT metadata_path FROM system.tables WHERE name='{name}'"
                        ).output.strip()
                        assert re.match(expected, path) is not None, error()
                finally:
                    with Finally("I drop the table"):
                        node.query(f"DROP TABLE IF EXISTS {name} SYNC")
