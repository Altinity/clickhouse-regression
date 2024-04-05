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
            run=load("alter.table.attach_partition.partition_types", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.partition_key", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.partition_key_datetime", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.storage", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.corrupted_partitions",
                "feature",
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.rbac", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.conditions", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.table_names",
                "feature",
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.partition_expression",
                "feature",
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.temporary_table",
                "feature",
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.replica.replica_sanity", "feature"),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.replica.add_delete_replica", "feature"
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load(
                "alter.table.attach_partition.operations_on_attached_partition",
                "feature",
            ),
            parallel=True,
            executor=pool,
        )
        Feature(
            run=load("alter.table.attach_partition.part_level", "feature"),
            parallel=True,
            executor=pool,
        )
        join()

    Feature(
        run=load("alter.table.attach_partition.restart_clickhouse_server", "feature")
    )
