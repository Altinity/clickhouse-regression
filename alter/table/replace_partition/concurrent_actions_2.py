import random

from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_two_tables_partitioned_by_column_with_data,
    create_table_partitioned_by_column_with_data,
    replace_partition_and_validate_data,
)
from helpers.alter import *
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.tables import Column, create_table_partitioned_by_column

destination_table = "destination_" + getuid()
source_table = "source_" + getuid()


@TestStep(When)
def add_column(self, table_name):
    """Add column to the table."""
    alter_table_add_column(
        table_name=table_name,
        column_name="column_" + getuid(),
        column_type="String",
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add("1.0")
)
def add_column_to_destination_table(self):
    """Alter add column to the destination table."""
    add_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Add("1.0")
)
def add_column_to_source_table(self):
    """Alter add column to the source table."""
    add_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
def replace_partition_on_source_table(self):
    """Replace partition on the source table while using this source table to replace partition on another
    destination table."""
    new_table = "new_" + getuid()

    with By(
        "creating a new table and replacing a partition on the source table from that new table"
    ):
        create_table_partitioned_by_column_with_data(table_name=new_table)
        replace_partition(
            destination_table=source_table, source_table=new_table, partition=2
        )


@TestStep(When)
def drop_column(self, table_name):
    """Drop column on the table."""
    alter_table_drop_column(table_name=table_name, column_name="extra")


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Drop("1.0")
)
def drop_column_on_destination_table(self):
    """Drop column on the destination table."""
    drop_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Drop("1.0")
)
def drop_column_on_source_table(self):
    """Drop table on the source table."""
    drop_column(table_name=source_table)


@TestStep(When)
def modify_column(self, table_name):
    """Modify column type of the table."""
    alter_table_modify_column(
        table_name=table_name, column_name="extra", column_type="String"
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Modify("1.0")
)
def modify_destination_table_column(self):
    """Modify column on the destination table."""
    modify_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_Modify("1.0")
)
def modify_source_table_column(self):
    """Modify column on the source table."""
    modify_column(table_name=source_table)


@TestStep(When)
def rename_column(self, table_name):
    """Rename column on the table."""
    alter_table_rename_column(
        table_name=table_name, column_name_old="extra", column_name_new="extra_new"
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_RenameColumn(
        "1.0"
    )
)
def rename_destination_table_column(self):
    """Rename the column on the destination table."""
    rename_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_RenameColumn(
        "1.0"
    )
)
def rename_source_table_column(self):
    """Rename the column on the source table."""
    rename_column(table_name=source_table)


@TestStep(When)
def comment_column(self, table_name):
    """Comment column on the table."""
    alter_table_comment_column(
        table_name=table_name, column_name="extra", comment="test_comment"
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_CommentColumn(
        "1.0"
    )
)
def comment_destination_table_column(self):
    """Comment column on the destination table."""
    comment_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_CommentColumn(
        "1.0"
    )
)
def comment_source_table_column(self):
    """Comment column on the source table."""
    comment_column(table_name=source_table)


@TestStep(When)
def add_constraint(self, table_name):
    """Add constraint to the table."""
    constraint_name = "constraint_" + getuid()

    alter_table_add_constraint(
        table_name=table_name, constraint_name=constraint_name, expression="(i > 1)"
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_AddConstraint(
        "1.0"
    )
)
def add_constraint_to_the_destination_table(self):
    """Add constraint to the destination table."""
    add_constraint(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_AddConstraint(
        "1.0"
    )
)
def add_constraint_to_the_source_table(self):
    """Add constraint to the source table."""
    add_constraint(table_name=source_table)


@TestStep(When)
def detach_partition(self, table_name):
    """Detach partition from the table."""
    partition_name = random.randrange(5, 100)
    alter_table_detach_partition(table_name=table_name, partition_name=partition_name)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach(
        "1.0"
    )
)
def detach_partition_from_destination_table(self):
    """Detach partition from the destination table."""
    detach_partition(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach(
        "1.0"
    )
)
def detach_partition_from_source_table(self):
    """Detach partition from the source table."""
    detach_partition(table_name=source_table)


@TestStep(When)
def attach_partition(self, table_name):
    """Attach partition to the table."""
    alter_table_attach_partition(table_name=table_name, partition_name=12)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach(
        "1.0"
    )
)
def attach_partition_to_destination_table(self):
    """Attach partition to the destination table."""
    attach_partition(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach(
        "1.0"
    )
)
def attach_partition_to_source_table(self):
    """Attach partition to the source table."""
    attach_partition(table_name=source_table)


@TestStep(When)
def attach_partition_from(self, table_name, source_table):
    """Attach partition from another table."""
    alter_table_attach_partition_from(
        table_name=table_name, partition_name=2, path_to_backup=source_table
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_AttachFrom(
        "1.0"
    )
)
def attach_partition_from_destination_to_source(self):
    """Attach partition on the source table from the destination table."""
    attach_partition_from(table_name=source_table, source_table=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_AttachFrom(
        "1.0"
    )
)
def attach_partition_from_source_to_destination(self):
    """Attach partition on the destination table from the source table."""
    attach_partition_from(table_name=destination_table, source_table=source_table)


@TestStep(When)
def move_partition(self, table_name, source_table):
    alter_table_move_partition_to_table(
        table_name=table_name, partition_name=2, path_to_backup=source_table
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable(
        "1.0"
    )
)
def move_partition_to_destination_table(self):
    """Move partition from the source table to the destination table."""
    move_partition(table_name=destination_table, source_table=source_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable(
        "1.0"
    )
)
def move_partition_to_source_table(self):
    """Move partition from the destination table to the source table."""
    move_partition(table_name=source_table, source_table=destination_table)


@TestStep(When)
def move_partition_to_volume(self, table_name, number_of_partitions=None):
    """Move partition to another volume."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    for retry in retries(count=5):
        with retry:
            partition_name = random.randrange(5, number_of_partitions)
            alter_table_move_partition(
                table_name=table_name,
                partition_name=partition_name,
                disk_name="external",
            )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move(
        "1.0"
    )
)
def move_destination_partition(self):
    """Move the partition from the destination table to external volume."""
    move_partition_to_volume(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move(
        "1.0"
    )
)
def move_source_partition(self):
    """Move the partition from the source table to external volume."""
    move_partition_to_volume(table_name=source_table)


@TestStep(When)
def clear_column(self, table_name, number_of_partitions=None):
    """Clear column in a specific partition of the table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)

    alter_table_clear_column_in_partition(
        table_name=table_name, partition_name=partition_name, column_name="i"
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition(
        "1.0"
    )
)
def clear_destination_table_column(self):
    """Clear column on the destination table."""
    clear_column(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition(
        "1.0"
    )
)
def clear_source_table_column(self):
    """Clear column on the source table."""
    clear_column(table_name=source_table)


@TestStep(When)
def fetch_partition(self, table_name, source_table, number_of_partitions=None):
    """Fetch partition from the replicated table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)

    partitioned_replicated_merge_tree_table(
        table_name=source_table + "_replica", partition="p"
    )

    alter_table_fetch_partition(
        table_name=table_name,
        partition_name=partition_name,
        path_to_backup=f"/clickhouse/tables/shard0/{source_table}_replica",
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Fetch(
        "1.0"
    )
)
def fetch_partition_from_destination_table(self):
    """Fetch partition from the destination table into a source table."""
    fetch_partition(table_name=source_table, source_table=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Fetch(
        "1.0"
    )
)
def fetch_partition_from_source_table(self):
    """Fetch partition from the destination table into a source table."""
    fetch_partition(table_name=destination_table, source_table=source_table)


@TestStep(When)
def freeze_partition(self, table_name, number_of_partitions=None):
    """Freeze a random partition of the table."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)

    alter_table_freeze_partition(table_name=table_name, partition_name=partition_name)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_destination_partition(self):
    """Freeze partition on the destination table."""
    freeze_partition(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_source_partition(self):
    """Freeze partition on the destination table."""
    freeze_partition(table_name=source_table)


@TestStep(When)
def freeze_partition_with_name(self, table_name):
    """Freeze partition with name on the table."""
    partition_name = random.randrange(5, 100)

    alter_table_freeze_partition_with_name(
        table_name=table_name, backup_name=partition_name
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_destination_partition_with_name(self):
    """Freeze partition on the destination table using name of the partition."""
    freeze_partition_with_name(table_name=destination_table)


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_source_partition_with_name(self):
    """Freeze partition on the source table using name of the partition."""
    freeze_partition_with_name(table_name=source_table)


@TestCheck
def concurrent_replace(
    self,
    action,
    number_of_concurrent_queries=None,
    number_of_partitions=None,
):
    node = self.context.node

    if number_of_concurrent_queries is None:
        number_of_concurrent_queries = self.context.number_of_concurrent_queries

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions
    try:
        with Given("I have two partitioned tables with the same structure"):
            create_two_tables_partitioned_by_column_with_data(
                destination_table=destination_table,
                source_table=source_table,
                number_of_partitions=number_of_partitions,
            )

        with When(
            "I save the data from the source table before replacing partitions on the destination table"
        ):
            source_data_before = node.query(
                f"SELECT i FROM {source_table} WHERE p = 1 ORDER BY tuple(*)"
            )

        with And("I execute replace partition concurrently with another action"):
            Check(
                name="replace partition on the destination table",
                test=replace_partition,
                parallel=True,
            )(
                destination_table=destination_table,
                source_table=source_table,
                partition=1,
            )
            for i in range(number_of_concurrent_queries):
                Check(
                    name=f"{action.__name__} #{i}",
                    test=action,
                    parallel=True,
                )()

        with Then("I check that the partition was replaced on the destination table"):
            check_partition_was_replaced(
                destination_table=destination_table,
                source_table=source_table,
                source_table_before_replace=source_data_before,
            )
    finally:
        with Finally("I delete both source and destination tables"):
            node.query(f"DROP TABLE {destination_table}")
            node.query(f"DROP TABLE {source_table}")


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent("1.0"))
@Name("concurrent actions2")
def feature(
    self,
    node="clickhouse1",
    number_of_concurrent_queries=100,
    number_of_partitions=500,
):
    """Check that it is possible to perform other actions at the same time as replace partitions is being triggered."""
    self.context.node = self.context.cluster.node(node)
    self.context.number_of_concurrent_queries = number_of_concurrent_queries
    self.context.number_of_partitions = number_of_partitions

    actions = [
        add_column_to_destination_table,
        add_column_to_source_table,
        replace_partition_on_source_table,
        drop_column_on_destination_table,
        drop_column_on_source_table,
        modify_destination_table_column,
        modify_source_table_column,
        rename_destination_table_column,
        rename_source_table_column,
        comment_destination_table_column,
        comment_source_table_column,
        add_constraint_to_the_destination_table,
        add_constraint_to_the_source_table,
        detach_partition_from_destination_table,
        detach_partition_from_source_table,
        attach_partition_to_destination_table,
        attach_partition_to_source_table,
        attach_partition_from_destination_to_source,
        attach_partition_from_source_to_destination,
        move_partition_to_destination_table,
        move_partition_to_source_table,
        move_destination_partition,
        move_source_partition,
        clear_destination_table_column,
        clear_source_table_column,
        fetch_partition_from_destination_table,
        fetch_partition_from_source_table,
        freeze_source_partition,
        freeze_destination_partition,
        freeze_destination_partition_with_name,
        freeze_source_partition_with_name,
    ]

    for action in actions:
        Scenario(
            name=f"{action.__name__}".replace("_", " "),
            test=concurrent_replace,
        )(
            action=action,
        )
