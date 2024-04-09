from testflows.core import *

from alter.table.move_partition.requirements.requirements import (
    SRS038_ClickHouse_Alter_Table_Move_Partition,
)


@TestFeature
@Specifications(SRS038_ClickHouse_Alter_Table_Move_Partition)
@Name("move partition")
def feature(self):
    """Run features from the move partition suite."""
    with Pool(2) as pool:
        Feature(
            run=load("alter.table.move_partition.partition_key", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.move_partition.partition_key_datetime", "feature"),
            parallel=True,
            executor=pool,
        )
        join()

    Feature(
        run=load("alter.table.move_partition.move_to_self", "feature"),
    )
