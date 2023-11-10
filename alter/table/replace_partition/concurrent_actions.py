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


def get_n_random_items(lst, n):
    """get n random elements from the list."""
    if n >= len(lst):
        return lst
    else:
        return random.sample(lst, n)


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
def add_column_to_destination_and_source(self):
    """Add column with the same name to both destination and source tables."""

    column_name = "column_" + getuid()

    alter_table_add_column(
        table_name=destination_table,
        column_name=column_name,
        column_type="String",
    )

    alter_table_add_column(
        table_name=source_table,
        column_name=column_name,
        column_type="String",
    )


@TestStep(When)
def replace_partition_from_another_table(self, destination_table, source_table):
    """Replace partition on the table from another newly created table."""
    number_of_partitions = self.context.number_of_partitions

    with By(
        f"replacing a partition on the {destination_table} table from the {source_table} table"
    ):
        partition_to_replace = random.randrange(1, number_of_partitions)
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=partition_to_replace,
        )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
def replace_partition_on_source_table(self):
    """Replace partition on the source table from another table."""
    replace_partition_from_another_table(
        destination_table=source_table, source_table=destination_table
    )


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Replace(
        "1.0"
    )
)
def replace_partition_on_destination_table(self):
    """Replace partition on the destination table from another table."""
    replace_partition_from_another_table(
        destination_table=destination_table, source_table=source_table
    )


@TestStep(When)
def drop_column(self, table_name):
    """Drop column on the table."""
    alter_table_drop_column(table_name=table_name, column_name="extra1")


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
def drop_column_on_destination_and_source(self):
    """Drop the same column on destination and source tables."""
    drop_column_on_destination_table()
    drop_column_on_source_table()


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
def modify_column_destination_and_source(self):
    """Modify column on destination and source tables."""
    modify_destination_table_column()
    modify_source_table_column()


@TestStep(When)
def rename_column(self, table_name):
    """Rename column on the table."""
    alter_table_rename_column(
        table_name=table_name, column_name_old="extra2", column_name_new="extra_new"
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


@TestStep
def rename_column_destination_and_source(self):
    """Rename column on destination and source tables."""
    rename_source_table_column()
    rename_destination_table_column()


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_CommentColumn(
        "1.0"
    )
)
def comment_destination_and_source_column(self):
    """Comment columns on destination and source tables."""
    comment_destination_table_column()
    comment_source_table_column()


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Alter_AddConstraint(
        "1.0"
    )
)
def add_constraint_to_destination_and_source(self):
    """Add constraint to destination and source tables."""
    add_constraint_to_the_destination_table()
    add_constraint_to_the_source_table()


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Detach(
        "1.0"
    )
)
def detach_partition_from_destination_and_source(self):
    """Detach partition from destination and source tables."""
    detach_partition_from_source_table()
    detach_partition_from_destination_table()


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Attach(
        "1.0"
    )
)
def attach_partition_to_destination_and_source(self):
    """Attach partition to destination and source tables."""
    attach_partition_to_source_table()
    attach_partition_to_destination_table()


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_MoveToTable(
        "1.0"
    )
)
def move_partition_between_source_and_destination(self):
    """Move partition between source and destination tables."""
    move_partition_to_source_table()
    move_partition_to_destination_table()


@TestStep(When)
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Disks("1.0"))
def move_partition_to_volume(
    self, table_name, number_of_partitions=None, partition_name=None
):
    """Move partition to another volume."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if partition_name is None:
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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Move(
        "1.0"
    )
)
def move_destination_and_source_partition(self):
    """Move partition to external volume from destination and source tables."""
    number_of_partitions = self.context.number_of_partitions

    partition_name = random.randrange(5, number_of_partitions)
    move_partition_to_volume(
        table_name=destination_table, partition_name=partition_name
    )
    move_partition_to_volume(table_name=source_table, partition_name=partition_name)


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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_ClearColumnInPartition(
        "1.0"
    )
)
def clear_column_on_destination_and_source(self):
    """Clear column on source and destination columns."""
    clear_source_table_column()
    clear_destination_table_column()


@TestStep(When)
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Replicas("1.0"))
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
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_partition_on_destination_and_source(self):
    """Freeze partition on source and destination tables."""
    freeze_destination_partition()
    freeze_source_partition()


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


@TestStep(When)
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent_Manipulating_Partitions_Freeze(
        "1.0"
    )
)
def freeze_destination_and_source_partition_with_name(self):
    """Freeze partitions on destination and source tables with name."""
    freeze_destination_partition_with_name()
    freeze_source_partition_with_name()


@TestStep(When)
def concurrent_replace_with_multiple_actions(
    self,
    actions,
    number_of_iterations=None,
    number_of_partitions=None,
    number_of_concurrent_queries=None,
):
    """Concurrently run replace partition with a number of other actions."""
    if number_of_concurrent_queries is None:
        number_of_concurrent_queries = self.context.number_of_concurrent_queries

    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_iterations is None:
        number_of_iterations = self.context.number_of_iterations

    with By(
        "running the replace partition number of times and each time run number of other actions in parallel"
    ):
        for i in range(number_of_iterations):
            partition_to_replace = random.randrange(1, number_of_partitions)
            for retry in retries(timeout=60):
                with retry:
                    Check(
                        name=f"replace partition on the destination table #{i}",
                        test=replace_partition_and_validate_data,
                        parallel=True,
                    )(
                        destination_table=destination_table,
                        source_table=source_table,
                        partition_to_replace=partition_to_replace,
                    )

            for action in get_n_random_items(actions, number_of_concurrent_queries):
                for retry in retries(timeout=60):
                    with retry:
                        Check(
                            name=f"{action.__name__} #{i}",
                            test=action,
                            parallel=True,
                        )()


@TestStep(When)
def replace_partition_with_single_concurrent_action(
    self,
    actions,
    number_of_iterations=None,
    number_of_partitions=None,
):
    """Concurrently run a single replace partition and another actions that is run a number of times."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    if number_of_iterations is None:
        number_of_iterations = self.context.number_of_iterations

    partition_to_replace = random.randrange(1, number_of_partitions)

    for retry in retries(timeout=30):
        with retry:
            Check(
                name=f"replace partition on the destination table",
                test=replace_partition_and_validate_data,
                parallel=True,
            )(
                destination_table=destination_table,
                source_table=source_table,
                partition_to_replace=partition_to_replace,
            )

        for i in range(number_of_iterations):
            for retry in retries(timeout=60):
                with retry:
                    Check(
                        name=f"{actions.__name__} #{i}",
                        test=actions,
                        parallel=True,
                    )()


@TestCheck
def concurrent_replace(
    self,
    actions,
    concurrent_scenario,
    number_of_partitions=None,
):
    """Concurrently run multiple actions along with replace partition."""
    if number_of_partitions is None:
        number_of_partitions = self.context.number_of_partitions

    with Given("I have two partitioned tables with the same structure"):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table,
            source_table=source_table,
            number_of_partitions=number_of_partitions,
        )

    with When("I execute multiple replace partitions along with other actions"):
        concurrent_scenario(actions=actions)


@TestScenario
def one_replace_partition(self):
    """Check that it is possible to execute a single replace partition while the number of other actions is being executed."""
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
            actions=action,
            concurrent_scenario=replace_partition_with_single_concurrent_action,
        )


@TestScenario
def replace_partition_along_other_actions(self):
    """Check that when we run multiple replace partitions in a loop along with other actions, replace partitions
    executes successfully."""
    actions = [
        add_column_to_destination_and_source,
        drop_column_on_destination_and_source,
        modify_column_destination_and_source,
        rename_column_destination_and_source,
        comment_destination_and_source_column,
        add_constraint_to_destination_and_source,
        detach_partition_from_destination_and_source,
        attach_partition_to_destination_and_source,
        move_partition_between_source_and_destination,
        move_destination_and_source_partition,
        clear_column_on_destination_and_source,
        freeze_partition_on_destination_and_source,
        freeze_destination_and_source_partition_with_name,
        replace_partition_on_source_table,
        replace_partition_on_destination_table,
    ]

    Scenario(test=concurrent_replace)(
        concurrent_scenario=concurrent_replace_with_multiple_actions, actions=actions
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Concurrent("1.0"))
@Name("concurrent actions")
def feature(
    self,
    node="clickhouse1",
    number_of_concurrent_queries=3,
    number_of_partitions=500,
    number_of_iterations=100,
    delay_before=None,
    delay_after=None,
    validate=True,
):
    """
    Concurrently execute replace partition on a destination table with
    different number of concurrent alter actions being executed in parallel.
    """
    self.context.node = self.context.cluster.node(node)
    self.context.number_of_concurrent_queries = number_of_concurrent_queries
    self.context.number_of_partitions = number_of_partitions
    self.context.number_of_iterations = number_of_iterations
    self.context.delay_before = delay_before
    self.context.delay_after = delay_after
    self.context.validate = validate

    Scenario(run=one_replace_partition)
    Scenario(run=replace_partition_along_other_actions)
