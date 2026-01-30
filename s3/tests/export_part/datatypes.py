from testflows.core import *
from testflows.asserts import error
from s3.tests.export_part.steps import *
from s3.tests.export_partition.steps import (
    create_table_with_json_column,
    create_table_with_json_column_with_hints,
    create_table_with_nested_column,
    create_table_with_complex_nested_column,
    escape_json_for_sql,
)
from helpers.create import *
from helpers.queries import *
from helpers.common import getuid
from s3.requirements.export_part import *


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
def create_merge_tree_all_valid_partition_key_types(
    self, column_name, cluster=None, node=None, rows_per_part=1
):
    """Create a MergeTree table with all valid partition key types and both wide and compact parts."""

    if node is None:
        node = self.context.node

    with By("creating a MergeTree table with all data types"):
        table_name = f"table_{getuid()}"
        create_merge_tree_table(
            table_name=table_name,
            columns=valid_partition_key_types_columns(),
            partition_by=column_name,
            cluster=cluster,
            stop_merges=True,
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
        table_name = create_merge_tree_all_valid_partition_key_types(
            column_name=partition_key_type,
            rows_per_part=rows_per_part,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=valid_partition_key_types_columns(),
            partition_by=partition_key_type,
        )

    with When("I export parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
        )

    with And("I read data from both tables"):
        source_data = select_all_ordered(
            table_name=table_name, order_by=partition_key_type
        )
        destination_data = select_all_ordered(
            table_name=s3_table_name,
            order_by=partition_key_type,
        )

    with Then("They should be the same"):
        assert source_data == destination_data, error()


@TestSketch(Scenario)
@Flags(TE)
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


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartTypes("1.0"))
def json_columns(self):
    """Check that JSON columns are properly exported when exporting parts."""

    with Given("I create a source table with JSON column and S3 destination table"):
        table_name = f"mt_json_{getuid()}"

        create_table_with_json_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_json",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "json_data", "type": "JSON"},
            ],
            partition_by="id",
        )

    json1_escaped = escape_json_for_sql({"a": {"b": 42}, "c": [1, 2, 3]})
    json2_escaped = escape_json_for_sql({"d": "Hello", "e": 100})
    insert_query = f"INSERT INTO {table_name} (id, json_data) VALUES (1, '{json1_escaped}'), (1, '{json2_escaped}')"

    with By("inserting data into the source table"):
        self.context.node.query(insert_query, use_file=True)

    with And("exporting parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
        )

    with And("verifying JSON column data exported to S3 matches source"):
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    order_by="id",
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    order_by="id",
                )
                assert source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartTypes("1.0"))
def json_columns_with_hints(self):
    """Check that JSON columns with type hints are properly exported when exporting parts."""

    with Given(
        "I create a source table with JSON column (with hints) and S3 destination table"
    ):
        table_name = f"mt_json_hints_{getuid()}"

        create_table_with_json_column_with_hints(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_json_hints",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "json_data", "type": "JSON(a.b UInt32, a.c String)"},
            ],
            partition_by="id",
        )

    json1_escaped = escape_json_for_sql({"a": {"b": 42, "c": "test"}})
    json2_escaped = escape_json_for_sql({"a": {"b": 100, "c": "world"}})
    insert_query = f"INSERT INTO {table_name} (id, json_data) VALUES (1, '{json1_escaped}'), (1, '{json2_escaped}')"

    with By("inserting data into the source table"):
        self.context.node.query(insert_query, use_file=True)

    with And("exporting parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
        )

    with And("verifying JSON column data with hints exported to S3 matches source"):
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    order_by="id",
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    order_by="id",
                )
                assert source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartTypes("1.0"))
def nested_columns(self):
    """Check that Nested columns are properly exported when exporting parts."""

    with Given("I create a source table with Nested column and S3 destination table"):
        table_name = f"mt_nested_{getuid()}"

        create_table_with_nested_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_nested",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {"name": "nested_data", "type": "Nested(key String, value UInt64)"},
            ],
            partition_by="id",
        )

    insert_query = f"INSERT INTO {table_name} (id, nested_data.key, nested_data.value) VALUES (1, ['key1', 'key2'], [10, 20]), (1, ['key3'], [30])"

    with By("inserting data into the source table"):
        self.context.node.query(insert_query, use_file=True)

    with And("exporting parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
        )

    with And("verifying Nested column data exported to S3 matches source"):
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    identifier="id, nested_data.key, nested_data.value",
                    order_by="id, nested_data.key",
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    identifier="id, nested_data.key, nested_data.value",
                    order_by="id, nested_data.key",
                )
                assert source_data == destination_data, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_PartTypes("1.0"))
def complex_nested_columns(self):
    """Check that complex Nested columns (with arrays) are properly exported when exporting parts."""

    with Given(
        "I create a source table with complex Nested column and S3 destination table"
    ):
        table_name = f"mt_nested_complex_{getuid()}"

        create_table_with_complex_nested_column(table_name=table_name)
        s3_table_name = create_s3_table(
            table_name="s3_nested_complex",
            create_new_bucket=True,
            columns=[
                {"name": "id", "type": "UInt32"},
                {
                    "name": "nested_data",
                    "type": "Nested(name String, age UInt8, scores Array(UInt32))",
                },
            ],
            partition_by="id",
        )

    insert_query = f"INSERT INTO {table_name} (id, nested_data.name, nested_data.age, nested_data.scores) VALUES (1, ['Alice', 'Bob'], [25, 30], [[100, 90], [85, 95]]), (1, ['Charlie'], [35], [[80, 90, 100]])"

    with By("inserting data into the source table"):
        self.context.node.query(insert_query, use_file=True)

    with And("exporting parts to the S3 table"):
        export_parts(
            source_table=table_name,
            destination_table=s3_table_name,
        )

    with And("verifying complex Nested column data exported to S3 matches source"):
        for retry in retries(timeout=35, delay=5):
            with retry:
                source_data = select_all_ordered(
                    table_name=table_name,
                    identifier="id, nested_data.name, nested_data.age, nested_data.scores",
                    order_by="id, nested_data.name",
                )
                destination_data = select_all_ordered(
                    table_name=s3_table_name,
                    identifier="id, nested_data.name, nested_data.age, nested_data.scores",
                    order_by="id, nested_data.name",
                )
                assert source_data == destination_data, error()


@TestFeature
@Name("datatypes")
@Requirements(
    RQ_ClickHouse_ExportPart_PartitionKeyTypes("1.0"),
    RQ_ClickHouse_ExportPart_PartTypes("1.0"),
)
def feature(self, num_parts=10):
    """Check that all data types are supported when exporting parts."""

    self.context.num_parts = num_parts

    Scenario(run=valid_partition_key_types_compact)
    Scenario(run=valid_partition_key_types_wide)
    Scenario(run=json_columns)
    Scenario(run=json_columns_with_hints)
    Scenario(run=nested_columns)
    Scenario(run=complex_nested_columns)
