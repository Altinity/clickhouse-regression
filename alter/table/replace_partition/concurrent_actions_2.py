from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    check_partition_was_replaced,
    create_two_tables_partitioned_by_column_with_data,
    create_table_partitioned_by_column_with_data,
)
from helpers.alter import *
from helpers.tables import Column, create_table_partitioned_by_column
import random

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
def add_column_to_destination_table(self):
    """Alter add column to the destination table."""
    add_column(table_name=destination_table)


@TestStep(When)
def add_column_to_source_table(self):
    """Alter add column to the source table."""
    add_column(table_name=destination_table)


@TestStep(When)
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
def drop_column_on_destination_table(self):
    """Drop column on the destination table."""
    drop_column(table_name=destination_table)


@TestStep(When)
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
def modify_destination_table_column(self):
    """Modify column on the destination table."""
    modify_column(table_name=destination_table)


@TestStep(When)
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
def rename_destination_table_column(self):
    """Rename the column on the destination table."""
    rename_column(table_name=destination_table)


@TestStep(When)
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
def comment_destination_table_column(self):
    """Comment column on the destination table."""
    comment_column(table_name=destination_table)


@TestStep(When)
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
def add_constraint_to_the_destination_table(self):
    """Add constraint to the destination table."""
    add_constraint(table_name=destination_table)


@TestStep(When)
def add_constraint_to_the_source_table(self):
    """Add constraint to the source table."""
    add_constraint(table_name=source_table)


@TestStep(When)
def detach_partition(self, table_name):
    """Detach partition from the table."""
    partition_name = random.randrange(5, 100)
    alter_table_detach_partition(table_name=table_name, partition_name=partition_name)


@TestStep(When)
def detach_partition_from_destination_table(self):
    """Detach partition from the destination table."""
    detach_partition(table_name=destination_table)


@TestStep(When)
def detach_partition_from_source_table(self):
    """Detach partition from the source table."""
    detach_partition(table_name=source_table)


@TestStep(When)
def attach_partition(self, table_name):
    """Attach partition to the table."""
    alter_table_attach_partition(table_name=table_name, partition_name=12)


@TestStep(When)
def attach_partition_to_destination_table(self):
    """Attach partition to the destination table."""
    attach_partition(table_name=destination_table)


@TestStep(When)
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
def attach_partition_from_destination_to_source(self):
    """Attach partition on the source table from the destination table."""
    attach_partition_from(table_name=source_table, source_table=destination_table)


@TestStep(When)
def attach_partition_from_source_to_destination(self):
    """Attach partition on the destination table from the source table."""
    attach_partition_from(table_name=destination_table, source_table=source_table)


@TestStep(When)
def move_partition(self, table_name, source_table):
    alter_table_move_partition_to_table(
        table_name=table_name, partition_name=2, path_to_backup=source_table
    )


@TestStep(When)
def move_partition_to_destination_table(self):
    """Move partition from the source table to the destination table."""
    move_partition(table_name=destination_table, source_table=source_table)


@TestStep(When)
def move_partition_to_source_table(self):
    """Move partition from the destination table to the source table."""
    move_partition(table_name=source_table, source_table=destination_table)


@Retry(5)
@TestStep(When)
def move_partition_to_volume(self, table_name):
    """Move partition to another volume."""
    partition_name = random.randrange(5, 100)
    alter_table_move_partition(
        table_name=table_name, partition_name=partition_name, disk_name="external"
    )


@TestStep(When)
def move_destination_partition(self):
    """Move the partition from the destination table to external volume."""
    move_partition_to_volume(table_name=destination_table)


@TestStep(When)
def move_source_partition(self):
    """Move the partition from the source table to external volume."""
    move_partition_to_volume(table_name=source_table)


@TestStep(When)
def clear_column(self, table_name):
    """Clear column in a specific partition of the table."""


@TestCheck
def concurrent_replace(
    self,
    action,
    partition_to_replace,
    number_of_concurrent_queries,
):
    node = self.context.node

    try:
        with Given("I have two partitioned tables with the same structure"):
            create_two_tables_partitioned_by_column_with_data(
                destination_table=destination_table,
                source_table=source_table,
                number_of_partitions=100,
            )

        with When(
            "I save the data from the source table before replacing partitions on the destination table"
        ):
            source_data_before = node.query(
                f"SELECT i FROM {source_table} WHERE p = {partition_to_replace} ORDER BY tuple(*)"
            )

        with And("I execute replace partition concurrently with another action"):
            Step(
                name="replace partition on the destination table",
                test=replace_partition,
                parallel=True,
            )(
                destination_table=destination_table,
                source_table=source_table,
                partition=partition_to_replace,
            )
            for _ in range(number_of_concurrent_queries):
                Step(
                    name=f"{action.__name__}",
                    test=action,
                    parallel=True,
                )()

        with Check("I check that the partition was replaced on the destination table"):
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
def feature(self, node="clickhouse1"):
    """Check that it is possible to perform other actions at the same time as replace partitions is being triggered."""
    self.context.node = self.context.cluster.node(node)
    partition_to_replace = 1
    number_of_concurrent_queries = 5
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
    ]

    for action in actions:
        Scenario(test=concurrent_replace, name=f"{action.__name__}")(
            partition_to_replace=partition_to_replace,
            number_of_concurrent_queries=number_of_concurrent_queries,
            action=action,
        )
