from testflows.core import *


@TestFeature
@Name("operations")
def feature(self):
    """Check operations on a table that uses encrypted disk."""
    Feature(
        run=load(
            "disk_level_encryption.tests.operations.alter_move_multi_volume_policy",
            "feature",
        )
    )
    Feature(
        run=load(
            "disk_level_encryption.tests.operations.alter_move_multi_disk_volume",
            "feature",
        )
    )
    Feature(
        run=load("disk_level_encryption.tests.operations.insert_and_select", "feature")
    )
