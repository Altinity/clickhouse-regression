import os

from testflows import *
from testflows.core import *
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *
from helpers.create import (
    partitioned_merge_tree_table,
    partitioned_replacing_merge_tree_table,
    partitioned_summing_merge_tree_table,
    partitioned_collapsing_merge_tree_table,
    partitioned_versioned_collapsing_merge_tree_table,
    partitioned_graphite_merge_tree_table,
    partitioned_aggregating_merge_tree_table,
    create_replicated_merge_tree_table,
)
from alter.table.replace_partition.engines import columns


@TestStep(Given)
def create_parquet_file(
    self, table_name, compression=None, format=False, settings=None
):
    """Create a parquet file."""
    node = self.context.node
    export = self.context.path_to_export + f"{table_name}.Parquet"

    with By(
        f"selecting the data from the {table_name} and inserting into the parquet file"
    ):
        q = f"SELECT * FROM {table_name} INTO OUTFILE '{export}'"

        if compression is not None:
            q += f" COMPRESSION '{compression}'"

        if format:
            q += f" FORMAT Parquet"

        if settings is not None:
            q += f" SETTINGS {settings}"

        node.query(q)


@TestCheck
def check_parquet_file(self, table, compression, format, settings):
    """Check if we can write and read from the parquet file with different combinations of table engines, compression, format and settings"""
    node = self.context.node
    table_name = "table_" + getuid()
    reference_table_name = "reference_" + getuid()

    with Given(
        "I create a table to use as a source for the parquet file",
        description=f"""
    table_engine: {table.__name__}
    compression: {compression}, format: {format}, settings: {settings}
    """,
    ):
        table(table_name=table_name, columns=columns(), partition_by="p")

    with When(f"I create a parquet file from the {table_name}"):
        create_parquet_file(
            table_name=table_name,
            compression=compression,
            format=format,
            settings=settings,
        )

    with Then(
        "I check that it is possible to select from the parquet file and the values are preserved"
    ):
        node.query(
            f"SELECT * FROM file('{self.context.path_to_export}{table_name}.Parquet') ORDER BY p",
            exitcode=0,
        )

    with And(
        "I check if it is possible to insert from the parquet file into a new table and that the values are preserved"
    ):
        table_values = node.query(f"SELECT * FROM {table_name} ORDER BY p")
        node.query(f"CREATE TABLE {reference_table_name} AS {table_name}")

        node.query(
            f"INSERT INTO {reference_table_name} FROM INFILE '{self.context.path_to_export}{table_name}.Parquet'"
        )

        reference_table_values = node.query(
            f"SELECT * FROM {reference_table_name} ORDER BY p"
        )

        assert (
            reference_table_values.output.strip() == table_values.output.strip()
        ), error()


@TestSketch(Scenario)
@Flags(TE)
def read_and_write_parquet_file(self):
    table_engines = {
        partitioned_merge_tree_table,
        partitioned_replacing_merge_tree_table,
        partitioned_summing_merge_tree_table,
        partitioned_collapsing_merge_tree_table,
        partitioned_versioned_collapsing_merge_tree_table,
        partitioned_graphite_merge_tree_table,
        partitioned_aggregating_merge_tree_table,
        create_replicated_merge_tree_table,
    }

    compression_types = ["lz4", "snappy", "gzip", "brotli", "zstd", "none", None]
    format = ["Parquet", False]
    settings = [
        None,
        "output_format_parquet_compression_method='lz4'",
        "output_format_parquet_compression_method='snappy'",
        "output_format_parquet_compression_method='gzip'",
        "output_format_parquet_compression_method='brotli'",
        "output_format_parquet_compression_method='zstd'",
        "output_format_parquet_compression_method='none'",
    ]

    check_parquet_file(
        table=either(*table_engines),
        compression=either(*compression_types),
        format=either(*format),
        settings=either(*settings),
    )


@TestFeature
@Name("read and write")
def feature(self, node="clickhouse1"):
    """
    Check different scenarios involving selecting/inserting data from/into parquet files.

    The combinations involve different table engines:
        MergeTree,
        ReplacingMergeTree,
        SummingMergeTree,
        CollapsingMergeTree,
        VersionedCollapsingMergeTree,
        GraphiteMergeTree,
        AggregatingMergeTree,
    compression types:
        ["lz4", "snappy", "gzip", "brotli", "zstd", "none", None]
    settings:
        None,
        "output_format_parquet_compression_method='{compression_types}'",
    output formats:
        None,
        Parquet
    """
    self.context.node = self.context.cluster.node(node)
    self.context.path_to_export = f"/var/lib/clickhouse/user_files/"

    for scenario in loads(current_module(), Scenario):
        scenario()
