from testflows.core import *
from s3.tests.export_partition.steps import export_partitions
from s3.tests.export_part.steps import *
from helpers.create import *
from helpers.queries import *
from helpers.common import getuid
from s3.requirements.export_partition import *


@TestStep(When)
def insert_all_datatypes(self, table_name, rows_per_part=1, num_parts=1, node=None):
    """Insert all datatypes into a MergeTree table."""

    if node is None:
        node = self.context.node

    for part in range(num_parts):
        node.query(
            f"INSERT INTO {table_name} (int8, int16, int32, int64, uint8, uint16, uint32, uint64, date, date32, datetime, datetime64, string, fixedstring) SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, '13', '14' FROM numbers({rows_per_part})"
        )


@TestStep(Given)
def create_replicated_merge_tree_all_valid_partition_key_types(
    self, column_name, cluster=None, node=None, rows_per_part=1
):
    """Create a MergeTree table with all valid partition key types and both wide and compact parts."""

    if node is None:
        node = self.context.node

    with By("creating a MergeTree table with all data types"):
        table_name = f"table_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=table_name,
            columns=valid_partition_key_types_columns(),
            partition_by=column_name,
            cluster=cluster,
            stop_merges=False,
            query_settings=f"min_rows_for_wide_part=10",
        )

    with And("I insert compact and wide parts into the table"):
        insert_all_datatypes(
            table_name=table_name,
            rows_per_part=rows_per_part,
            num_parts=self.context.num_parts,
            node=node,
        )

    return table_name


@TestCheck
def valid_partition_key_table(self, partition_key_type, rows_per_part=1):
    """Check exporting to a source table with specified valid partition key type and rows."""

    with Given(
        f"I create a source table with valid partition key type {partition_key_type} and empty S3 table"
    ):
        table_name = create_replicated_merge_tree_all_valid_partition_key_types(
            column_name=partition_key_type,
            rows_per_part=rows_per_part,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=valid_partition_key_types_columns(),
            partition_by=partition_key_type,
        )

    with When("I export partitions to the S3 table"):
        export_partitions(
            source_table=table_name,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with Then("I compare the source and destination data"):
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    node=self.context.node,
                    order_by=partition_key_type,
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    node=self.context.node,
                    order_by=partition_key_type,
                )

                assert source_data == destination_data, error()


@TestSketch(Scenario)
@Flags(TE)
@Requirements(RQ_ClickHouse_ExportPartition_PartitionKeyTypes("1.0"))
def valid_partition_key_types_compact(self):
    """Check that all partition key data types are supported when exporting compact parts."""

    key_types = [datatype["name"] for datatype in valid_partition_key_types_columns()]
    valid_partition_key_table(partition_key_type=either(*key_types), rows_per_part=1)


@TestSketch(Scenario)
@Flags(TE)
def valid_partition_key_types_wide(self):
    """Check that all partition key data types are supported when exporting wide parts."""

    key_types = [datatype["name"] for datatype in valid_partition_key_types_columns()]
    valid_partition_key_table(partition_key_type=either(*key_types), rows_per_part=100)


@TestStep(Given)
def create_table_with_alias_column(self, table_name):
    """Create a MergeTree table with ALIAS column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "alias": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_materialized_column(self, table_name):
    """Create a MergeTree table with MATERIALIZED column."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "a", "type": "UInt32"},
            {"name": "arr", "type": "Array(UInt64)"},
            {"name": "arr_1", "type": "UInt64", "materialized": "arr[1]"},
        ],
        partition_by="a",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_ephemeral_and_default_column(self, table_name):
    """Create a MergeTree table with EPHEMERAL and DEFAULT columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name_input", "type": "String", "ephemeral": ""},
            {"name": "name_upper", "type": "String", "default": "upper(name_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_mixed_columns(self, table_name):
    """Create a MergeTree table with mixed ALIAS, MATERIALIZED, and EPHEMERAL columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "value", "type": "UInt32"},
            {"name": "tag_input", "type": "String", "ephemeral": ""},
            {"name": "doubled", "type": "UInt64", "alias": "value * 2"},
            {"name": "tripled", "type": "UInt64", "materialized": "value * 3"},
            {"name": "tag", "type": "String", "default": "upper(tag_input)"},
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(Given)
def create_table_with_complex_expressions(self, table_name):
    """Create a MergeTree table with complex expressions in computed columns."""
    create_replicated_merge_tree_table(
        table_name=table_name,
        columns=[
            {"name": "id", "type": "UInt32"},
            {"name": "name", "type": "String"},
            {"name": "upper_name", "type": "String", "alias": "upper(name)"},
            {
                "name": "concat_result",
                "type": "String",
                "materialized": "concat(name, '-', toString(id))",
            },
        ],
        partition_by="id",
        query_settings="index_granularity = 1",
    )


@TestStep(When)
def export_and_verify_columns(
    self,
    table_name,
    s3_table_name,
    insert_query,
    description="columns",
):
    """Helper function to export partitions and verify data matches."""

    with By(f"I inserting data into the source table"):
        self.context.node.query(insert_query)

    with And("exporting partitions to the S3 table"):
        export_partitions(
            source_table=table_name,
            destination_table=s3_table_name,
            node=self.context.node,
        )

    with And(f"verifying{description} exported to S3 matches source"):
        source_matches_destination(
            source_table=table_name, destination_table=s3_table_name
        )


@TestCheck
def alias_column_export(self):
    """Check exporting ALIAS columns to S3 table."""

    with Given("I create a source table with ALIAS column and S3 destination table"):
        table_name = f"mt_alias_{getuid()}"

        create_table_with_alias_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_alias",
            create_new_bucket=True,
            columns=[
                {"name": "a", "type": "UInt32"},
                {"name": "arr", "type": "Array(UInt64)"},
                {"name": "arr_1", "type": "UInt64"},
            ],
            partition_by="a",
        )

    export_and_verify_columns(
        table_name=table_name,
        s3_table_name=s3_table_name,
        insert_query=f"INSERT INTO {table_name} VALUES (1, [1, 2, 3]), (1, [10, 20, 30])",
        description="ALIAS column data",
    )


@TestCheck
def materialized_column_export(self):
    """Check exporting MATERIALIZED columns to S3 table."""

    with Given(
        "I create a source table with MATERIALIZED column and S3 destination table"
    ):
        table_name = f"mt_materialized_{getuid()}"
        create_table_with_materialized_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_materialized",
            create_new_bucket=True,
            columns=[
                {"name": "a", "type": "UInt32"},
                {"name": "arr", "type": "Array(UInt64)"},
                {"name": "arr_1", "type": "UInt64"},
            ],
            partition_by="a",
        )

    export_and_verify_columns(
        table_name=table_name,
        s3_table_name=s3_table_name,
        insert_query=f"INSERT INTO {table_name} VALUES (1, [1, 2, 3]), (1, [10, 20, 30])",
        description="MATERIALIZED column data",
    )


@TestCheck
def ephemeral_and_default_column_export(self):
    """Check exporting EPHEMERAL and DEFAULT columns to S3 table."""

    with Given(
        "I create a source table with EPHEMERAL and DEFAULT columns and S3 destination table"
    ):
        table_name = f"mt_ephemeral_{getuid()}"

        create_table_with_ephemeral_and_default_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_ephemeral",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "name_upper", "type": "String"},
            ],
            partition_by="id",
        )

    export_and_verify_columns(
        table_name=table_name,
        s3_table_name=s3_table_name,
        insert_query=f"INSERT INTO {table_name} (id, name_input) VALUES (1, 'alice'), (1, 'bob')",
        description="EPHEMERAL and DEFAULT column data",
    )


@TestCheck
def mixed_columns_export(self):
    """Check exporting mixed ALIAS, MATERIALIZED, and EPHEMERAL columns to S3 table."""

    with Given("I create a source table with mixed columns and S3 destination table"):
        table_name = f"mt_mixed_{getuid()}"

        create_table_with_mixed_columns(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_mixed",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "value", "type": "UInt32"},
                {"name": "doubled", "type": "UInt64"},
                {"name": "tripled", "type": "UInt64"},
                {"name": "tag", "type": "String"},
            ],
            partition_by="id",
        )

    export_and_verify_columns(
        table_name=table_name,
        s3_table_name=s3_table_name,
        insert_query=f"INSERT INTO {table_name} (id, value, tag_input) VALUES (1, 5, 'test'), (1, 10, 'prod')",
        description="mixed columns",
    )


@TestCheck
def complex_expressions_export(self):
    """Check exporting complex expressions in computed columns to S3 table."""

    with Given(
        "I create a source table with complex expressions and S3 destination table"
    ):
        table_name = f"mt_complex_expr_{getuid()}"

        create_table_with_complex_expressions(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_complex_expr",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "name", "type": "String"},
                {"name": "upper_name", "type": "String"},
                {"name": "concat_result", "type": "String"},
            ],
            partition_by="id",
        )

    export_and_verify_columns(
        table_name=table_name,
        s3_table_name=s3_table_name,
        insert_query=f"INSERT INTO {table_name} (id, name) VALUES (1, 'alice'), (1, 'bob')",
        description="complex expressions",
    )


@TestScenario
@Flags(TE)
def alias_columns(self):
    """Check that ALIAS columns are properly exported when exporting partitions."""

    alias_column_export()


@TestScenario
@Flags(TE)
def materialized_columns(self):
    """Check that MATERIALIZED columns are properly exported when exporting partitions."""

    materialized_column_export()


@TestScenario
@Flags(TE)
def ephemeral_and_default_columns(self):
    """Check that EPHEMERAL and DEFAULT columns are properly exported when exporting partitions."""

    ephemeral_and_default_column_export()


@TestScenario
@Flags(TE)
def mixed_columns(self):
    """Check that mixed ALIAS, MATERIALIZED, and EPHEMERAL columns are properly exported when exporting partitions."""

    mixed_columns_export()


@TestScenario
@Flags(TE)
def complex_expressions(self):
    """Check that complex expressions in computed columns are properly exported when exporting partitions."""

    complex_expressions_export()


@TestFeature
@Name("datatypes")
@Requirements(
    RQ_ClickHouse_ExportPartition_PartitionKeyTypes("1.0"),
    RQ_ClickHouse_ExportPartition_PartitionContent("1.0"),
)
def feature(self, num_parts=10):
    """Check that all data types are supported when exporting partitions."""

    self.context.num_parts = num_parts

    # Scenario(run=valid_partition_key_types_compact)
    # Scenario(run=valid_partition_key_types_wide)
    Scenario(run=alias_columns)
    Scenario(run=materialized_columns)
    Scenario(run=ephemeral_and_default_columns)
    Scenario(run=mixed_columns)
    Scenario(run=complex_expressions)
