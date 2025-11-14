from time import sleep
from testflows.core import *
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
from helpers.alter import *
from alter.stress.tests.tc_netem import *


def get_alter_functions():
    return [
        (
            alter_table_add_column,
            {"column_name": "new_column", "column_type": "UInt64"},
        ),
        (alter_table_drop_column, {"column_name": "Path"}),
        (
            alter_table_modify_column,
            {"column_name": "i", "column_type": "String"},
        ),
        (
            alter_table_rename_column,
            {"column_name_old": "Path", "column_name_new": "renamed_column"},
        ),
        (
            alter_table_comment_column,
            {"column_name": "p", "comment": "test column comment"},
        ),
        (
            alter_table_add_constraint,
            {"constraint_name": "new_constraint", "expression": "1 = 1"},
        ),
        (alter_table_drop_constraint, {"constraint_name": "new_constraint"}),
        (alter_table_drop_partition, {"partition_name": "1"}),
        (
            alter_table_modify_ttl,
            {
                "ttl_expression": "if(Time < toDateTime('2006-02-07'), Time + INTERVAL 100 YEAR, toDateTime('2106-02-07'))"
            },
        ),
        (alter_table_detach_partition, {"partition_name": "1"}),
        (alter_table_attach_partition, {"partition_name": "1"}),
        (
            alter_table_attach_partition_from,
            {"partition_name": "1", "path_to_backup": ""},
        ),
        (
            alter_table_move_partition_to_table,
            {"partition_name": "1", "path_to_backup": ""},
        ),
        (alter_table_move_partition, {"partition_name": "1", "disk_name": ""}),
        (
            alter_table_clear_column_in_partition,
            {"partition_name": "1", "column_name": "i"},
        ),
        (
            alter_table_clear_index_in_partition,
            {"partition_name": "1", "index": "idx_i"},
        ),
        (alter_table_freeze_partition, {"partition_name": "1"}),
        (
            alter_table_freeze_partition_with_name,
            {"partition_name": "1", "backup_name": "frozen_partition"},
        ),
        (
            alter_table_unfreeze_partition_with_name,
            {"partition_name": "1", "backup_name": "frozen_partition"},
        ),
        (
            alter_table_replace_partition,
            {"partition_name": "1", "path_to_backup": ""},
        ),
        (
            alter_table_update_column,
            {"column_name": "i", "expression": "0", "condition": "1 = 1"},
        ),
        (alter_table_delete_rows, {"condition": "p = 1"}),
        (alter_table_modify_comment, {"comment": "test table comment"}),
        (
            alter_table_fetch_partition,
            {"partition_name": "1", "path_to_backup": ""},
        ),
    ]


SETUP_FUNCTIONS = {
    alter_table_drop_constraint: lambda table_name, node: node.query(
        f"ALTER TABLE {table_name} ADD CONSTRAINT new_constraint CHECK 1 = 1"
    ),
    alter_table_attach_partition: lambda table_name, node: node.query(
        f"ALTER TABLE {table_name} DETACH PARTITION 1"
    ),
    alter_table_attach_partition_from: lambda table_name, node: (
        partitioned_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )
    ),
    alter_table_move_partition_to_table: lambda table_name, node: (
        partitioned_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )
    ),
    alter_table_clear_index_in_partition: lambda table_name, node: node.query(
        f"ALTER TABLE {table_name} ADD INDEX idx_i i TYPE minmax GRANULARITY 1"
    ),
    alter_table_unfreeze_partition_with_name: lambda table_name, node: (
        alter_table_freeze_partition_with_name(
            table_name=table_name,
            backup_name="frozen_partition",
            partition_name="1",
        )
    ),
    alter_table_replace_partition: lambda table_name, node: (
        partitioned_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )
    ),
    alter_table_fetch_partition: lambda table_name, node: (
        partitioned_replicated_merge_tree_table(
            table_name=table_name + "_temp",
            partition_by="p",
            columns=get_column_info(node=node, table_name=table_name),
            query_settings="storage_policy = 'tiered_storage'",
        )
    ),
}


@TestOutline(Scenario)
@Examples(
    "alter_function, kwargs",
    get_alter_functions(),
)
def alter_before_export(self, alter_function, kwargs):
    """Test altering the source table before exporting parts."""

    with Given("I create a populated source table"):
        source_table = "source_" + getuid()

        if alter_function == alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )

    with And("I run setup if needed"):
        if alter_function in SETUP_FUNCTIONS:
            SETUP_FUNCTIONS[alter_function](
                table_name=source_table, node=self.context.node
            )
            if (
                alter_function == alter_table_attach_partition_from
                or alter_function == alter_table_replace_partition
            ):
                kwargs["path_to_backup"] = f"{source_table}_temp"
            elif alter_function == alter_table_move_partition_to_table:
                kwargs["path_to_backup"] = source_table
            elif alter_function == alter_table_fetch_partition:
                kwargs["path_to_backup"] = (
                    f"/clickhouse/tables/shard0/{source_table}_temp"
                )

    with When(f"I {alter_function.__name__} on the source table"):
        if alter_function == alter_table_move_partition:
            moved = False
            while not moved:
                for volume in ["hot", "cold"]:
                    try:
                        kwargs["disk_name"] = volume
                        alter_function(table_name=source_table, **kwargs)
                        moved = True
                        break
                    except Exception as e:
                        note(f"Failed to move to {volume}: {e}")
                        pass
        else:
            alter_function(
                table_name=(
                    source_table
                    if alter_function != alter_table_move_partition_to_table
                    else f"{source_table}_temp"
                ),
                **kwargs,
            )

    with And("I populate the source table with new parts"):
        insert_into_table(
            table_name=source_table,
        )

    with When("I create an empty S3 table"):
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=get_column_info(node=self.context.node, table_name=source_table),
        )

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestOutline(Scenario)
@Examples(
    "alter_function, kwargs",
    get_alter_functions(),
)
def alter_after_export(self, alter_function, kwargs):
    """Test altering the source table after exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        if alter_function == alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I run setup if needed"):
        if alter_function in SETUP_FUNCTIONS:
            SETUP_FUNCTIONS[alter_function](
                table_name=source_table, node=self.context.node
            )
            if (
                alter_function == alter_table_attach_partition_from
                or alter_function == alter_table_replace_partition
            ):
                kwargs["path_to_backup"] = f"{source_table}_temp"
            elif alter_function == alter_table_move_partition_to_table:
                kwargs["path_to_backup"] = source_table
            elif alter_function == alter_table_fetch_partition:
                kwargs["path_to_backup"] = (
                    f"/clickhouse/tables/shard0/{source_table}_temp"
                )

    with When("I read data on the S3 table"):
        initial_destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with And(f"I {alter_function.__name__} on the source table"):
        if alter_function == alter_table_move_partition:
            moved = False
            while not moved:
                for volume in ["hot", "cold"]:
                    try:
                        kwargs["disk_name"] = volume
                        alter_function(table_name=source_table, **kwargs)
                        moved = True
                        break
                    except Exception as e:
                        note(f"Failed to move to {volume}: {e}")
                        pass
        else:
            alter_function(
                table_name=(
                    source_table
                    if alter_function != alter_table_move_partition_to_table
                    else f"{source_table}_temp"
                ),
                **kwargs,
            )

    with Then("Check destination is not affected by the alter"):
        final_destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert initial_destination_data == final_destination_data, error()


@TestOutline(Scenario)
@Examples(
    "alter_function, kwargs",
    get_alter_functions(),
)
def alter_during_export(self, alter_function, kwargs):
    """Test altering the source table during exporting parts."""

    with Given("I create a populated source table and empty S3 table"):
        source_table = "source_" + getuid()

        if alter_function == alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                columns=default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False),
        )

    with And("I read data on the source table"):
        initial_source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I run setup if needed"):
        if alter_function in SETUP_FUNCTIONS:
            SETUP_FUNCTIONS[alter_function](
                table_name=source_table, node=self.context.node
            )
            if (
                alter_function == alter_table_attach_partition_from
                or alter_function == alter_table_replace_partition
            ):
                kwargs["path_to_backup"] = f"{source_table}_temp"
            elif alter_function == alter_table_move_partition_to_table:
                kwargs["path_to_backup"] = source_table
            elif alter_function == alter_table_fetch_partition:
                kwargs["path_to_backup"] = (
                    f"/clickhouse/tables/shard0/{source_table}_temp"
                )

    with And(f"I {alter_function.__name__} on the source table"):
        if alter_function == alter_table_move_partition:
            moved = False
            while not moved:
                for volume in ["hot", "cold"]:
                    try:
                        kwargs["disk_name"] = volume
                        alter_function(table_name=source_table, **kwargs)
                        moved = True
                        break
                    except Exception as e:
                        note(f"Failed to move to {volume}: {e}")
                        pass
        else:
            alter_function(
                table_name=(
                    source_table
                    if alter_function != alter_table_move_partition_to_table
                    else f"{source_table}_temp"
                ),
                **kwargs,
            )

    with Then("Check destination matches original source data"):
        sleep(5)
        destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )
        assert initial_source_data == destination_data, error()


@TestFeature
@Name("concurrent alter")
def feature(self):
    """Check concurrent ALTER operations on the source table during exporting parts to S3 storage."""

    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)

    Scenario(run=alter_before_export)
    Scenario(run=alter_during_export)
    Scenario(run=alter_after_export)
