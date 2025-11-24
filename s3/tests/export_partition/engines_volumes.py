from alter.table.attach_partition.common import create_partitions_with_random_uint64
from helpers.common import getuid
from helpers.create import (
    partitioned_replicated_merge_tree_table,
    partitioned_summing_merge_tree_table,
    partitioned_collapsing_merge_tree_table,
    partitioned_versioned_collapsing_merge_tree_table,
    partitioned_aggregating_merge_tree_table,
    partitioned_graphite_merge_tree_table,
    partitioned_replacing_merge_tree_table,
)
from helpers.queries import *
from s3.tests.export_partition.steps import (
    export_partitions,
    create_s3_table,
    default_columns,
    source_matches_destination,
    minio_storage_configuration,
)
from s3.requirements.export_partition import *


@TestCheck
def configured_table(self, table_engine, number_of_partitions, number_of_parts):
    """Test a specific combination of table engine, number of partitions, and number of parts."""

    source_table = f"source_{getuid()}"

    with Given("I create a populated source table and empty S3 table"):
        table_engine(
            table_name=source_table,
            partition_by="p",
            stop_merges=False,
            number_of_partitions=number_of_partitions,
            number_of_parts=number_of_parts,
            columns=default_columns(simple=False, partition_key_type="Int8"),
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=default_columns(simple=False, partition_key_type="Int8"),
        )

    with When("I export parts to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestSketch(Scenario)
@Flags(TE)
def table_combos(self):
    """Test various combinations of table engines, number of partitions, and number of parts."""

    tables = [
        partitioned_replicated_merge_tree_table,
        partitioned_replacing_merge_tree_table,
        partitioned_summing_merge_tree_table,
        partitioned_collapsing_merge_tree_table,
        partitioned_versioned_collapsing_merge_tree_table,
        partitioned_aggregating_merge_tree_table,
        partitioned_graphite_merge_tree_table,
    ]
    number_of_partitions = [5] if not self.context.stress else [1, 5, 10]
    number_of_parts = [1] if not self.context.stress else [1, 5, 10]

    table_engine = either(*tables)
    number_of_partitions = either(*number_of_partitions)
    number_of_parts = either(*number_of_parts)

    Combination(
        name=f"{table_engine.__name__} partitions={number_of_partitions} parts={number_of_parts}",
        test=configured_table,
    )(
        table_engine=table_engine,
        number_of_partitions=number_of_partitions,
        number_of_parts=number_of_parts,
    )


@TestCheck
def configured_volume(self, volume):
    """Test a specific combination of volume."""

    source_table = f"source_{getuid()}"

    with Given(f"I create an empty source table on volume {volume} and empty S3 table"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=default_columns(),
            stop_merges=False,
            query_settings=f"storage_policy = '{volume}'",
            populate=False,
        )
        s3_table_name = create_s3_table(table_name="s3", create_new_bucket=True)

    with And("I populate the source table with parts exceeding 2KB each"):
        create_partitions_with_random_uint64(
            table_name=source_table,
            node=self.context.node,
            number_of_values=500,
        )

    with When("I export parts to the S3 table"):
        export_partitions(
            source_table=source_table,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("Source and destination tables should match"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestSketch(Scenario)
@Flags(TE)
def volume_combos(self):
    """Test exporting to various storage policies."""

    volumes = [
        "jbod1",
        "jbod2",
        "jbod3",
        "jbod4",
        "external",
        "external2",
        "tiered_storage",
    ]
    volume = either(*volumes)

    Combination(
        name=f"volume={volume}",
        test=configured_volume,
    )(
        volume=volume,
    )


@TestFeature
@Name("engines and volumes")
@Requirements(
    RQ_ClickHouse_ExportPartition_SourceEngines("1.0"),
    RQ_ClickHouse_ExportPartition_StoragePolicies("1.0"),
    RQ_ClickHouse_ExportPartition_SourcePartStorage("1.0"),
)
def feature(self):
    """Check exporting parts to S3 storage with different table engines and volumes."""
    with Given("I set up MinIO storage configuration"):
        minio_storage_configuration(restart=True)
    # Scenario(run=table_combos)
    Scenario(run=volume_combos)
