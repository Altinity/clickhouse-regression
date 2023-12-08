from testflows.core import *

from alter.table.attach_partition.requirements.requirements import (
    SRS034_ClickHouse_Alter_Table_Attach_Partition,
)


@TestFeature
@Specifications(SRS034_ClickHouse_Alter_Table_Attach_Partition)
@Name("attach partition")
def feature(self):
    """Run features from the attach partition suite."""
    with Pool(2) as pool:
        Feature(
            run=load("alter.table.attch_partition.partition_types", "feature"),
            parallel=True,
            executor=pool,
        )
        join()
