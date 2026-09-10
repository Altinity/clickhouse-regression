"""EXPORT PARTITION from a CAS ReplicatedMergeTree source to Iceberg.

EXPORT PARTITION is implemented only for ReplicatedMergeTree. The source
must be replicated even though this scenario only needs one replica to
issue the ALTER.
"""

from testflows.core import *

from helpers.common import getuid
from helpers.config import config_d, users_d
from cas.requirements.requirements import RQ_SRS_048_CAS_MergeTree_Transparency
from cas.tests.steps import create_replicated_cas_table
from iceberg.tests.export_partition.steps.export_operations import export_partition
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    assert_source_and_destination_match,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"
EXPORT_SOURCE_SETTINGS = [
    "enable_block_number_column = 1",
    "enable_block_offset_column = 1",
]


@TestScenario
@Name("export single partition from a CAS disk")
@Requirements(RQ_SRS_048_CAS_MergeTree_Transparency("1.0"))
def export_partition_from_cas_disk(self):
    """Export one partition from a ``cas_policy`` source and check the
    Iceberg destination has those rows and no others.
    """
    source_table = f"rmt_cas_export_{getuid()}"
    user = self.context.minio_root_user
    password = self.context.minio_root_password

    with Given("a ReplicatedMergeTree source on the CAS storage policy"):
        create_replicated_cas_table(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            order_by="id",
            extra_settings=EXPORT_SOURCE_SETTINGS,
        )

    with And("insert data into two partitions"):
        self.context.node.query(
            f"INSERT INTO {source_table} VALUES "
            "(1, 2020), (2, 2020), (3, 2020), (4, 2021)"
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=user,
            minio_root_password=password,
        )

    with When("I export the 2020 partition to Iceberg"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with Then("only the 2020 partition rows land in the destination"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=user,
            minio_root_password=password,
        )

    with And("data in the destination matches the source for that partition"):
        assert_source_and_destination_match(
            source_table=source_table,
            destination=destination,
            minio_root_user=user,
            minio_root_password=password,
            partition_where="year = 2020",
            order_by="id",
        )


@TestFeature
@Name("export")
def feature(self):
    """EXPORT PARTITION behaviour for tables stored on a CAS disk."""
    self.context.catalog = "no"
    self.context.source_engine = "replicated"

    config_d.enable_export_partition()

    with Given(
        "enable export-partition Iceberg writes in the default profile"
    ):
        for node in self.context.nodes:
            users_d.create_and_add(
                entries={
                    "profiles": {
                        "default": {
                            "allow_experimental_insert_into_iceberg": "1",
                        }
                    }
                },
                config_file="allow_experimental_insert_into_iceberg.xml",
                node=node,
                modify=True,
            )

    Scenario(run=export_partition_from_cas_disk)
