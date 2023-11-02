from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_two_tables_partitioned_by_column_with_data,
)
from helpers.alter import *
from helpers.datatypes import UInt64, UInt8, DateTime
from helpers.tables import Column
from helpers.create import (
    partitioned_replicated_merge_tree_table,
)


@TestStep(When)
def perform_concurrent_actions(self, action, destination_table, source_table, params):
    with By(
        f"executing replace_partition and {action.__name__} actions on the destination table"
    ):
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
    columns=None,
    disk_name=None,
    constraint=False,
):
    """
    Test outline to perform the following actions:
        1. Create two tables that have the same structure. If constraint is not None, then the specified constraints are
        applied to these tables.
        2. Concurrently execute replace partition action and another actions specified in `action` value.
        3. Check that the partition was replaced on the destination table after the concurrent actions are finished.
    """
    params = {
        k: v
        for k, v in locals().items()
        if v is not None
        and k
        not in [
            "self",
            "action",
            "destination_table",
            "source_table",
            "columns",
            "constraint",
            "settings",
        ]
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
            columns=columns,
            query_settings=settings,
        )

        if constraint:
            with And(f"I add constraint to the {table_name} table"):
                alter_table_add_constraint(
                    table_name=table_name,
                    constraint_name=constraint_name,
                    expression="(i > 1)",
                )

    with When("I perform concurrent operations"):
        perform_concurrent_actions(
            action=action,
            destination_table=destination_table,
            source_table=source_table,
            params=params,
        )

    with Then("I check that partition was replaced on the destination table"):
        check_partition_was_replaced(
            destination_table=destination_table, source_table=source_table, column="i"
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add("1.0")
)
def alter_add(self):
    """Check that it is possible to add column to the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    with Given(
        "I try to concurrently replace partition and add column on the destination table"
    ):
        concurrent(
            action=alter_table_add_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name=column_name,
            column_type="UInt8",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Drop("1.0")
)
def alter_drop(self):
    """Check that it is possible to drop column on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=UInt8()),
    ]

    with Given(
        "I try to concurrently replace partition and drop table on the destination table"
    ):
        concurrent(
            action=alter_table_drop_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name=column_name,
            columns=columns,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Modify("1.0")
)
@Retry(5)
def alter_modify(self):
    """Check that it is possible to modify column on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=UInt8()),
    ]

    with Given(
        "I try to concurrently replace partition and modify column on the destination table"
    ):
        concurrent(
            action=alter_table_modify_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name=column_name,
            column_type="UInt64",
            columns=columns,
        )


@TestScenario
@Requirements()  # TODO ADD RENAME REQUIREMENTS
def alter_rename_column(self):
    """Check that it is possible to rename column on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()
    column_new_name = "new_column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=UInt8()),
    ]

    with Given(
        "I try to concurrently replace partition and rename column on the destination table"
    ):
        concurrent(
            action=alter_table_rename_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name_old=column_name,
            column_name_new=column_new_name,
            columns=columns,
        )


@TestScenario
@Requirements()  # TODO ADD COMMENT REQUIREMENTS
def alter_comment_column(self):
    """Check that it is possible to comment column on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=UInt8()),
    ]

    with Given(
        "I try to concurrently replace partition and comment column on the destination table"
    ):
        concurrent(
            action=alter_table_comment_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name=column_name,
            comment="test comment",
            columns=columns,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_AddConstraint(
        "1.0"
    )
)
def alter_add_constraint(self):
    """Check that it is possible to add constraint on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and add constraint on the destination table"
    ):
        concurrent(
            action=alter_table_add_constraint,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            constraint_name="test_constraint",
            expression="(i > 1)",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_DropConstraint(
        "1.0"
    )
)
def alter_drop_constraint(self):
    """Check that it is possible to drop constraint on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    constraint_name = getuid()

    with Given(
        "I try to concurrently replace partition and drop on the destination table"
    ):
        concurrent(
            action=alter_table_drop_constraint,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            constraint_name=constraint_name,
            constraint=True,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_ModifyTTL("1.0")
)
def alter_modify_ttl(self):
    """Check that it is possible to modify ttl on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=DateTime()),
    ]

    with Given(
        "I try to concurrently replace partition and modify ttl on the destination table"
    ):
        concurrent(
            action=alter_table_modify_ttl,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            columns=columns,
            ttl_expression=f"{column_name} + INTERVAL 1 YEAR",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach(
        "1.0"
    )
)
def alter_detach_partition(self):
    """Check that it is possible to detach partition on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and detach partition on the destination table"
    ):
        concurrent(
            action=alter_table_detach_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            partition_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach(
        "1.0"
    )
)
def alter_attach_partition(self):
    """Check that it is possible to attach partition on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and attach partition on the destination table"
    ):
        concurrent(
            action=alter_table_attach_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            partition_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Fetch(
        "1.0"
    )
)
def alter_fetch_partition(self):
    """Check that it is possible to fetch partition on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    columns = [
        {"name": "p", "type": "Int8"},
        {"name": "i", "type": "UInt64"},
    ]
    params = {
        "table_name": destination_table,
        "partition_name": 2,
        "path_to_backup": f"/clickhouse/tables/shard0/{destination_table}",
    }

    with Given(
        "I create partitioned ReplicatedMergeTree destination and source tables with the same structure"
    ):
        partitioned_replicated_merge_tree_table(
            table_name=destination_table, partition="p", columns=columns
        )
        partitioned_replicated_merge_tree_table(
            table_name=source_table, partition="p", columns=columns
        )

    with When(
        "I run concurrent replace partition and fetch partition actions on the destination table"
    ):
        perform_concurrent_actions(
            action=alter_table_fetch_partition,
            destination_table=destination_table,
            source_table=source_table,
            params=params,
        )

    with Then("I check that partition was replaced on the destination table"):
        check_partition_was_replaced(
            destination_table=destination_table, source_table=source_table, column="i"
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def alter_freeze_partition(self):
    """Check that it is possible to freeze partition on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and freeze partition on the destination table"
    ):
        concurrent(
            action=alter_table_freeze_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            partition_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def alter_freeze_partition_with_name(self):
    """Check that it is possible to freeze partition with name on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and freeze partition with name on the destination table"
    ):
        concurrent(
            action=alter_table_freeze_partition_with_name,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            backup_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Unfreeze(
        "1.0"
    )
)
def alter_unfreeze_partition_with_name(self):
    """Check that it is possible to unfreeze partition with name on the table while replacing partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and unfreeze partition with name on the destination table"
    ):
        concurrent(
            action=alter_table_unfreeze_partition_with_name,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            backup_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
def alter_replace_partition(self):
    """Check that it is possible to replace partition on the table while replacing another partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and another replace partition on the destination table"
    ):
        concurrent(
            action=alter_table_replace_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            partition_name=3,
            path_to_backup=source_table,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_UpdateInPartition(
        "1.0"
    )
)
def alter_update_partition(self):
    """Check that it is possible to replace partition on the table while updating columns on the partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    column_name = "column" + getuid()

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name=column_name, datatype=UInt8()),
    ]

    with Given(
        "I try to concurrently replace partition and update partition on the destination table"
    ):
        concurrent(
            action=alter_table_update_column,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            columns=columns,
            column_name=column_name,
            expression=1,
            condition="p > 1",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_DeleteInPartition(
        "1.0"
    )
)
def alter_delete_rows(self):
    """Check that it is possible to replace partition on the table while deleting rows."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and delete rows on the destination table"
    ):
        concurrent(
            action=alter_table_delete_rows,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            condition="p < 1",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_UpdateInPartition(
        "1.0"
    )
)
def alter_modify_comment(self):
    """Check that it is possible to replace partition on the table while modifying the table comment."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and modify comment on the destination table"
    ):
        concurrent(
            action=alter_table_modify_comment,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            comment="test",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_AttachFrom(
        "1.0"
    )
)
def alter_attach_partition_from(self):
    """Check that it is possible to replace partition on the table while attaching the partition from another table."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition and attach partition from another table on the destination table"
    ):
        concurrent(
            action=alter_table_attach_partition_from,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            path_to_backup=source_table,
            partition_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable(
        "1.0"
    )
)
def alter_move_partition_to_another_table(self):
    """Check that it is possible to replace partition on the table while moving a partition to another table."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition on the destination table and move partition to another table"
    ):
        concurrent(
            action=alter_table_move_partition_to_table,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            path_to_backup=source_table,
            partition_name=3,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move(
        "1.0"
    )
)
def alter_move_partition_to_another_volume(self):
    """Check that it is possible to replace partition on the table while moving a partition to another volume."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition on the destination table and move partition to another volume"
    ):
        concurrent(
            action=alter_table_move_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            disk_name="external",
            partition_name=2,
            settings="storage_policy = 'my_policy'",
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition(
        "1.0"
    )
)
def alter_clear_column_in_partition(self):
    """Check that it is possible to replace partition on the table while clearing column in partition."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I try to concurrently replace partition on the destination table and clear column in partition"
    ):
        concurrent(
            action=alter_table_clear_column_in_partition,
            destination_table=destination_table,
            source_table=source_table,
            table_name=destination_table,
            column_name="i",
            partition_name=3,
        )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent("1.0"))
@Name("concurrent actions")
def feature(self, node="clickhouse1"):
    """Check that it is possible to perform other actions at the same time as replace partitions is being triggered."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
