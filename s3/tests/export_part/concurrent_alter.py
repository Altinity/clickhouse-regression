from testflows.core import *
import s3.tests.export_part.steps as steps
from helpers.create import *
from helpers.queries import *
from s3.requirements.export_part import *
import helpers.alter.partition
import helpers.alter.column
import helpers.alter.constraint
import helpers.alter.ttl
import helpers.alter.update
import helpers.alter.delete
import helpers.alter.table
from alter.stress.tests.tc_netem import *
from helpers.common import getuid


def get_alter_functions():
    return [
        (
            helpers.alter.column.alter_table_add_column,
            {"column_name": "new_column", "column_type": "UInt64"},
        ),
        (helpers.alter.column.alter_table_drop_column, {"column_name": "Path"}),
        (
            helpers.alter.column.alter_table_modify_column,
            {"column_name": "i", "column_type": "String"},
        ),
        (
            helpers.alter.column.alter_table_rename_column,
            {"column_name_old": "Path", "column_name_new": "renamed_column"},
        ),
        (
            helpers.alter.column.alter_table_comment_column,
            {"column_name": "p", "comment": "test column comment"},
        ),
        (
            helpers.alter.constraint.alter_table_add_constraint,
            {"constraint_name": "new_constraint", "expression": "1 = 1"},
        ),
        (steps.alter_table_drop_constraint, {"constraint_name": "new_constraint"}),
        (helpers.alter.partition.alter_table_drop_partition, {"partition_name": "1"}),
        (
            helpers.alter.ttl.alter_table_modify_ttl,
            {
                "ttl_expression": "if(Time < toDateTime('2006-02-07'), Time + INTERVAL 100 YEAR, toDateTime('2106-02-07'))"
            },
        ),
        (helpers.alter.partition.alter_table_detach_partition, {"partition_name": "1"}),
        (steps.alter_table_attach_partition, {"partition_name": "1"}),
        (
            steps.alter_table_attach_partition_from,
            {"partition_name": "1"},
        ),
        (
            steps.alter_table_move_partition_to_table,
            {"partition_name": "1"},
        ),
        (steps.alter_table_move_partition, {"partition_name": "1"}),
        (
            helpers.alter.column.alter_table_clear_column_in_partition,
            {"partition_name": "1", "column_name": "i"},
        ),
        (
            steps.alter_table_clear_index_in_partition,
            {"partition_name": "1", "index": "idx_i"},
        ),
        (helpers.alter.partition.alter_table_freeze_partition, {"partition_name": "1"}),
        (
            helpers.alter.partition.alter_table_freeze_partition_with_name,
            {"partition_name": "1", "backup_name": "frozen_partition"},
        ),
        (
            steps.alter_table_unfreeze_partition_with_name,
            {"partition_name": "1", "backup_name": "frozen_partition"},
        ),
        (
            steps.alter_table_replace_partition,
            {"partition_name": "1"},
        ),
        (
            helpers.alter.update.alter_table_update_column,
            {"column_name": "i", "expression": "0", "condition": "1 = 1"},
        ),
        (helpers.alter.delete.alter_table_delete_rows, {"condition": "p = 1"}),
        (
            helpers.alter.table.alter_table_modify_comment,
            {"comment": "test table comment"},
        ),
        (
            steps.alter_table_fetch_partition,
            {"partition_name": "1"},
        ),
        (
            create_partitions_with_random_uint64,
            {"number_of_partitions": 5, "number_of_parts": 1},
        ),
        (steps.optimize_partition, {"partition": "1"}),
    ]


@TestOutline(Scenario)
@Examples(
    "alter_function, kwargs",
    get_alter_functions(),
)
def alter_before_export(self, alter_function, kwargs):
    """Test altering the source table before exporting parts."""

    with Given("I create a populated source table"):
        source_table = f"source_{getuid()}"

        if alter_function == steps.alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )

    with When(f"I {alter_function.__name__} on the source table"):
        alter_function(table_name=source_table, **kwargs)

    with And("I populate the source table with new parts"):
        steps.insert_into_table(
            table_name=source_table,
        )

    with When("I create an empty S3 table"):
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.get_column_info(
                node=self.context.node, table_name=source_table
            ),
        )

    with And("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Check source matches destination"):
        steps.source_matches_destination(
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
        source_table = f"source_{getuid()}"

        if alter_function == steps.alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with And("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with When("I read data on the S3 table"):
        initial_destination_data = select_all_ordered(
            table_name=s3_table_name, node=self.context.node
        )

    with And(f"I {alter_function.__name__} on the source table"):
        alter_function(table_name=source_table, **kwargs)

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
        source_table = f"source_{getuid()}"

        if alter_function == steps.alter_table_fetch_partition:
            partitioned_replicated_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        else:
            partitioned_merge_tree_table(
                table_name=source_table,
                partition_by="p",
                number_of_parts=2,
                columns=steps.default_columns(simple=False),
                query_settings="storage_policy = 'tiered_storage'",
            )
        s3_table_name = steps.create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=steps.default_columns(simple=False),
        )

    with And("I read data on the source table"):
        initial_source_data = select_all_ordered(
            table_name=source_table, node=self.context.node
        )

    with And("I slow the network"):
        network_packet_rate_limit(node=self.context.node, rate_mbit=0.05)

    with And("I export parts to the S3 table"):
        steps.export_parts(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And(f"I {alter_function.__name__} on the source table"):
        alter_function(table_name=source_table, **kwargs)

    with Then("Check destination matches original source data"):
        steps.source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
            source_data=initial_source_data,
        )


@TestFeature
@Name("concurrent alter")
def feature(self):
    """Check concurrent actions on the source table during exporting parts to S3 storage."""

    with Given("I set up MinIO storage configuration"):
        steps.minio_storage_configuration(restart=True)

    Scenario(run=alter_before_export)
    # Scenario(run=alter_during_export)
    Scenario(run=alter_after_export)
