from testflows.core import *

from alter.table.attach_partition.requirements.requirements import (
    SRS034_ClickHouse_Alter_Table_Attach_Partition,
)


@TestFeature
@Specifications(SRS034_ClickHouse_Alter_Table_Attach_Partition)
@Name("attach partition")
def feature(self):
    """Run features from the attach partition suite."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    with Feature("part 1"):
        with Pool() as pool:
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
                run=load(
                    "alter.table.attach_partition.partition_key_datetime", "feature"
                ),
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
                run=load(
                    "alter.table.attach_partition.replica.replica_sanity", "feature"
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
                run=load(
                    "alter.table.attach_partition.part_names.part_names", "feature"
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "alter.table.attach_partition.simple_attach_partition_from",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            join()

    with Feature("part 2"):
        Feature(
            run=load(
                "alter.table.attach_partition.replica.add_remove_replica", "feature"
            ),
        )
        Feature(
            run=load(
                "alter.table.attach_partition.restart_clickhouse_server", "feature"
            )
        )
