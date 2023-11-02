from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    create_partitions_with_random_uint64,
    check_partition_was_replaced,
    create_two_tables_partitioned_by_column_with_data,
)
from alter.table.replace_partition.alter_steps import alter_table_add_column
from helpers.tables import create_table_partitioned_by_column


@TestOutline
def concurrent(
    self,
    action,
    destination_table,
    source_table,
    table_name=None,
    column_name=None,
    column_type=None,
    column_name_old=None,
    column_name_new=None,
    comment=None,
    index_name=None,
    expression=None,
    index_type=None,
    partition_name=None,
    constraint_name=None,
    ttl_expression=None,
    settings=None,
    path_to_backup=None,
    backup_name=None,
    condition=None,
    interval=None,
):
    params = {
        k: v
        for k, v in locals().items()
        if v is not None
        and k not in ["self", "action", "destination_table", "source_table"]
    }

    node = self.context.node

    with Given(
        "I have two tables with the same structure, partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table,
            source_table=source_table,
            number_of_partitions=3,
            number_of_values=3,
        )

    with When("I perform concurrent operations"):
        for retry in retries(count=5, delay=1):
            with retry:
                Step(
                    name="replace partition on the destination table",
                    test=replace_partition,
                    parallel=True,
                )(destination_table=destination_table, source_table=source_table)
                Step(
                    name=f"{action.__name__}",
                    test=action,
                    parallel=True,
                )(**params)

    with Then("I check that partition was replaced on the destination table"):
        check_partition_was_replaced(
            destination_table=destination_table, source_table=source_table, column="i"
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add("1.0")
)
def concurrent_alter_update(self):
    """Check that it is possible to add column to the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    concurrent(
        action=alter_table_add_column,
        destination_table=destination_table,
        source_table=source_table,
        table_name=destination_table,
        column_name=column_name,
        column_type="UInt8",
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent("1.0"))
@Name("concurrent actions")
def feature(self, node="clickhouse1"):
    """Check that it is possible to perform other actions at the same time as replace partitions is being triggered."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
