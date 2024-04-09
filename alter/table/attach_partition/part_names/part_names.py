from alter.table.attach_partition.part_names.common_steps import *
from alter.table.attach_partition.requirements.requirements import *


# @TestScenario
# def test(self):
#     source_table = "source_" + getuid()
#     destination_table = "destination_" + getuid()

#     with Given("I have a table"):
#         create_MergeTree_table(table_name=source_table, order_by="id")

#     with And("I insert data into the table"):
#         self.context.node.query(f"INSERT INTO {source_table} (id) SELECT number FROM numbers(10)")

#     with And("I optimize the table"):
#         optimize_table(table_name=source_table)

#     with And("I get part name"):
#         part_name = self.context.node.query(
#             f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
#         ).output

#     with And("I detach the part"):
#         detach_partition(table_name=source_table, partition="tuple()")
#         # detach_part(table_name=source_table, part_name=part_name)

#     with And("I rename the detached part"):
#         new_part_name = "_".join(part_name.split("_")[:-1]) + "_4294967295"
#         rename_detached_part(
#             table_name=source_table,
#             part_name=part_name,
#             new_part_name=new_part_name,
#         )

#     with And("I attach the part"):
#         attach_partition(table_name=source_table, partition="tuple()")
#         # attach_part(table_name=source_table, part_name=new_part_name)
#         self.context.node.query(f"SELECT * FROM {source_table}")
#         optimize_table(table_name=source_table)
#         optimize_table(table_name=source_table)

#     with And("I get part name"):
#         part_name = self.context.node.query(
#             f"SELECT name FROM system.parts WHERE table = '{source_table}' AND active"
#         ).output

#     with And("I create a destination table"):
#         create_MergeTree_table(table_name=destination_table, order_by="id")

#     with And("I attach a partition from the source table to the destination table"):
#         attach_partition_from(
#             source_table=source_table,
#             destination_table=destination_table,
#             partition="tuple()",
#         )

#     with And("I get part name"):
#         part_name = self.context.node.query(
#             f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active"
#         ).output

#     with And("I optimize the destination table"):
#         optimize_table(table_name=destination_table)

#     with And("I get part name"):
#         part_name = self.context.node.query(
#             f"SELECT name FROM system.parts WHERE table = '{destination_table}' AND active"
#         ).output


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
        # Scenario(
        #     run=load(
        #         "alter.table.attach_partition.part_names.replicated_tables",
        #         "replicated_tables",
        #     ),
        #     parallel=True,
        #     executor=executor,
        # )
        join()
