from alter.table.attach_partition.common import create_partitions_with_random_uint64
from helpers.alter import alter_table_add_column
from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import *
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
)
from s3.requirements.export_partition import *


@TestCheck
def schema_evolution(
    self,
    number_of_partitions_before,
    number_of_parts_before,
    number_of_partitions_after,
    number_of_parts_after,
):
    """Test exporting partitions when source table has parts with both old and new schema."""

    source_table = f"source_{getuid()}"
    new_column_name = f"new_col_{getuid()}"

    with Given("I create an empty source table and stop merges"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            populate=False,
            columns=default_columns(simple=True, partition_key_type="Int8"),
        )

    with And("I insert data that creates multiple parts/partitions with old schema"):
        create_partitions_with_random_uint64(
            table_name=source_table,
            node=self.context.node,
            number_of_partitions=number_of_partitions_before,
            number_of_parts=number_of_parts_before,
            number_of_values=500,
        )

    with When("I add a new column to the source table"):
        alter_table_add_column(
            table_name=source_table,
            column_name=new_column_name,
            column_type="String",
            node=self.context.node,
        )

    with And(
        "I insert data with the new schema that creates parts with updated schema"
    ):
        for i in range(1, number_of_partitions_after + 1):
            for _ in range(1, number_of_parts_after + 1):
                self.context.node.query(
                    f"INSERT INTO {source_table} (p, i, {new_column_name}) SELECT {i}, rand64(), 'new_value_{i}' FROM numbers(500)"
                )

    with And("I create destination S3 table matching the new schema with added column"):
        new_columns = default_columns(simple=True, partition_key_type="Int8")
        new_columns.append({"name": new_column_name, "type": "String"})
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=new_columns,
        )

    with Then("I export partitions to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And("I verify source and destination tables match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestSketch(Scenario)
@Flags(TE)
def schema_evolution_combos(self):
    """Test exporting partitions with schema evolution - parts with old and new schema."""

    number_of_partitions_before = [3] if not self.context.stress else [1, 3, 5]
    number_of_parts_before = [2] if not self.context.stress else [1, 2, 3]
    number_of_partitions_after = [2] if not self.context.stress else [1, 2, 3]
    number_of_parts_after = [2] if not self.context.stress else [1, 2, 3]

    number_of_partitions_before = either(*number_of_partitions_before)
    number_of_parts_before = either(*number_of_parts_before)
    number_of_partitions_after = either(*number_of_partitions_after)
    number_of_parts_after = either(*number_of_parts_after)

    Combination(
        name=f"before: partitions={number_of_partitions_before} parts={number_of_parts_before}, after: partitions={number_of_partitions_after} parts={number_of_parts_after}",
        test=schema_evolution,
    )(
        number_of_partitions_before=number_of_partitions_before,
        number_of_parts_before=number_of_parts_before,
        number_of_partitions_after=number_of_partitions_after,
        number_of_parts_after=number_of_parts_after,
    )


@TestFeature
@Name("schema evolution")
@Requirements(RQ_ClickHouse_ExportPartition_SchemaChangeIsolation("1.0"))
def feature(self):
    """Check exporting parts to S3 storage when source table has parts with both old and new schema."""

    Scenario(run=schema_evolution_combos)
