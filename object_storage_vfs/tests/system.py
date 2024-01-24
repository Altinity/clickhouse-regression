from testflows.core import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *


"""
RQ_SRS_038_DiskObjectStorageVFS_System_AddKeeper
RQ_SRS_038_DiskObjectStorageVFS_System_RemoveKeeper
"""





@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_System_CompactWideParts("1.0"))
def wide_parts(self):
    """Check that data can be stored in S3 using only wide data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    try:
        with Given(
            f"""I create table using S3 storage policy external_vfs,
                    min_bytes_for_wide_parts set to 0"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external_vfs',
                min_bytes_for_wide_part=0
            """
            )

        with When("I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Wide"):
            for _type in part_types:
                assert _type == "Wide", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_System_CompactWideParts("1.0"))
def compact_parts(self):
    """Check that data can be stored in S3 using only compact data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    try:
        with Given(
            f"""I create table using S3 storage policy external_vfs,
                    min_bytes_for_wide_parts set to a very large value"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external_vfs',
                min_bytes_for_wide_part=100000
            """
            )

        with When("I store simple data in the table, stored as compact parts"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Compact"):
            for _type in part_types:
                assert _type == "Compact", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestFeature
@Name("system")
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
