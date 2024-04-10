from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *


@TestFeature
@Requirements(RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom("1.0"))
@Name("part level")
def feature(self):
    """Check that too high part levels are fixed upon attach from disk."""

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]
    self.context.node = self.context.node_1

    with Pool(3) as executor:
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.part_levels_user_example",
                "part_levels_user_example",
            ),
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.part_level_reset",
                "part_level_reset",
            ),
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.merge_increment",
                "merge_increment",
            ),
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.replicated_tables",
                "replicated_tables",
            ),
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.too_high_level",
                "too_high_level",
            ),
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=load(
                "alter.table.attach_partition.part_names.too_high_level",
                "reset_when_equal_to_legacy_max_level",
            ),
            parallel=True,
            executor=executor,
        )
        join()
