from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
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
from s3.requirements.export_part import *


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Alias("1.0"))
def alias_columns(self):
    """Test that ALIAS columns are materialized during export and exported correctly."""

    with Given("I create a source table with ALIAS columns and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "arr", "type": "Array(UInt64)"},
                {"name": "arr_1", "type": "UInt64", "alias": "arr[1]"},
            ],
            partition_by="p",
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "arr", "type": "Array(UInt64)"},
                {"name": "arr_1", "type": "UInt64"},
            ],
            partition_by="p",
        )

    with And("I insert data and export parts"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i, arr) VALUES (1, 100, [10, 20, 30]), (2, 200, [40, 50, 60])",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify ALIAS column values are computed correctly in source"):
        source_data = self.context.node.query(
            f"SELECT p, i, arr, arr_1 FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t100\t[10,20,30]\t10" in source_data, error()
        assert "2\t200\t[40,50,60]\t40" in source_data, error()

    with And("I verify ALIAS column is exported as regular column"):
        verify_column_in_destination(table_name=s3_table_name, column_name="arr_1")
        verify_exported_data_matches_with_columns(
            source_table=source_table,
            destination_table=s3_table_name,
            columns="p, i, arr, arr_1",
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Materialized("1.0"))
def materialized_columns(self):
    """Test that MATERIALIZED columns are exported correctly with stored computed values."""

    with Given("I create a source table with MATERIALIZED columns and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "tripled", "type": "UInt64", "materialized": "i * 3"},
            ],
            partition_by="p",
            stop_merges=True,
        )
        source_columns = get_columns_with_kind(table_name=source_table)
        s3_columns = [
            {"name": col["name"], "type": col["type"]}
            for col in source_columns
            if col.get("default_kind", "") != "Ephemeral"
        ]
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=s3_columns,
            partition_by="p",
        )

    with And("I insert data and export parts"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i) VALUES (1, 10), (2, 20), (3, 30)",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify MATERIALIZED column values are stored correctly"):
        source_data = self.context.node.query(
            f"SELECT p, i, tripled FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t10\t30" in source_data, error()
        assert "2\t20\t60" in source_data, error()
        assert "3\t30\t90" in source_data, error()

    with And("I verify exported data matches source including MATERIALIZED columns"):
        verify_exported_data_matches_with_columns(
            source_table=source_table,
            destination_table=s3_table_name,
            columns="p, i, tripled",
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Ephemeral("1.0"))
def ephemeral_columns(self):
    """Test that EPHEMERAL columns are ignored during export and not present in destination table schema."""

    with Given("I create a source table with EPHEMERAL columns and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "unhexed", "type": "String", "ephemeral": ""},
                {
                    "name": "hexed",
                    "type": "FixedString(4)",
                    "default": "unhex(unhexed)",
                },
            ],
            partition_by="p",
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "hexed", "type": "FixedString(4)"},
            ],
            partition_by="p",
        )

    with And("I insert data and export parts"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i, unhexed) VALUES (1, 100, '5a90b714'), (2, 200, 'deadbeef')",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify EPHEMERAL column is not in destination schema"):
        verify_column_not_in_destination(
            table_name=s3_table_name, column_name="unhexed"
        )

    with And("I verify exported data matches source (excluding EPHEMERAL columns)"):
        verify_exported_data_matches_with_columns(
            source_table=source_table,
            destination_table=s3_table_name,
            columns="p, i, hexed",
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Default("1.0"))
def default_columns_with_default_values(self):
    """Test that DEFAULT columns are materialized during export when using default values."""

    with Given("I create a source table with DEFAULT columns and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "status", "type": "String", "default": "'active'"},
                {"name": "created_at", "type": "DateTime", "default": "now()"},
            ],
            partition_by="p",
            stop_merges=True,
        )
        source_columns = get_columns_with_kind(table_name=source_table)
        s3_columns = [
            {"name": col["name"], "type": col["type"]}
            for col in source_columns
            if col.get("default_kind", "") != "Ephemeral"
        ]
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=s3_columns,
            partition_by="p",
        )

    with And("I insert data without specifying DEFAULT columns and export"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i) VALUES (1, 100), (2, 200)",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify DEFAULT values are used in source table"):
        source_data = self.context.node.query(
            f"SELECT p, i, status FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t100\tactive" in source_data, error()
        assert "2\t200\tactive" in source_data, error()

    with And(
        "I verify exported data matches source including materialized DEFAULT values"
    ):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Default("1.0"))
def default_columns_with_explicit_values(self):
    """Test that DEFAULT columns are materialized during export when explicit values are provided."""

    with Given("I create a source table with DEFAULT columns and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "status", "type": "String", "default": "'active'"},
            ],
            partition_by="p",
            stop_merges=True,
        )
        source_columns = get_columns_with_kind(table_name=source_table)
        s3_columns = [
            {"name": col["name"], "type": col["type"]}
            for col in source_columns
            if col.get("default_kind", "") != "Ephemeral"
        ]
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=s3_columns,
            partition_by="p",
        )

    with And("I insert data with explicit values and export"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i, status) VALUES (1, 100, 'inactive'), (2, 200, 'pending')",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify explicit values are stored correctly"):
        source_data = self.context.node.query(
            f"SELECT p, i, status FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t100\tinactive" in source_data, error()
        assert "2\t200\tpending" in source_data, error()

    with And("I verify exported data matches source with materialized explicit values"):
        source_matches_destination(
            source_table=source_table,
            destination_table=s3_table_name,
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_ColumnTypes_Alias("1.0"),
    RQ_ClickHouse_ExportPart_ColumnTypes_Materialized("1.0"),
    RQ_ClickHouse_ExportPart_ColumnTypes_Default("1.0"),
    RQ_ClickHouse_ExportPart_ColumnTypes_Ephemeral("1.0"),
)
def mixed_columns(self):
    """Test that tables with ALIAS, MATERIALIZED, DEFAULT, and EPHEMERAL columns together export correctly."""

    with Given("I create a source table with mixed column types and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "tag_input", "type": "String", "ephemeral": ""},
                {"name": "doubled", "type": "UInt64", "alias": "i * 2"},
                {"name": "tripled", "type": "UInt64", "materialized": "i * 3"},
                {"name": "tag", "type": "String", "default": "upper(tag_input)"},
            ],
            partition_by="p",
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "i", "type": "UInt64"},
                {"name": "doubled", "type": "UInt64"},
                {"name": "tripled", "type": "UInt64"},
                {"name": "tag", "type": "String"},
            ],
            partition_by="p",
        )

    with And("I insert data and export parts"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, i, tag_input) VALUES (1, 10, 'test1'), (2, 20, 'test2')",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify computed columns are correct in source"):
        source_data = self.context.node.query(
            f"SELECT p, i, doubled, tripled FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t10\t20\t30" in source_data, error()
        assert "2\t20\t40\t60" in source_data, error()

    with And("I verify EPHEMERAL column is not in destination schema"):
        verify_column_not_in_destination(
            table_name=s3_table_name, column_name="tag_input"
        )

    with And(
        "I verify ALIAS, MATERIALIZED, and DEFAULT columns are exported as regular columns"
    ):
        verify_exported_data_matches_with_columns(
            source_table=source_table,
            destination_table=s3_table_name,
            columns="p, i, doubled, tripled, tag",
        )


@TestScenario
@Requirements(
    RQ_ClickHouse_ExportPart_ColumnTypes_Alias("1.0"),
    RQ_ClickHouse_ExportPart_ColumnTypes_Materialized("1.0"),
)
def complex_expressions(self):
    """Test that complex expressions in ALIAS and MATERIALIZED columns are materialized and exported correctly."""

    with Given("I create a source table with complex expressions and empty S3 table"):
        source_table = f"source_{getuid()}"
        create_merge_tree_table(
            table_name=source_table,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "id", "type": "UInt64"},
                {"name": "name", "type": "String"},
                {"name": "upper_name", "type": "String", "alias": "upper(name)"},
                {
                    "name": "concat_result",
                    "type": "String",
                    "materialized": "concat(name, '-', toString(id))",
                },
            ],
            partition_by="p",
            stop_merges=True,
        )
        s3_table_name = create_s3_table(
            table_name="s3",
            create_new_bucket=True,
            columns=[
                {"name": "p", "type": "UInt8"},
                {"name": "id", "type": "UInt64"},
                {"name": "name", "type": "String"},
                {"name": "upper_name", "type": "String"},
                {"name": "concat_result", "type": "String"},
            ],
            partition_by="p",
        )

    with And("I insert data and export parts"):
        self.context.node.query(
            f"INSERT INTO {source_table} (p, id, name) VALUES (1, 100, 'Alice'), (2, 200, 'Bob')",
            exitcode=0,
            steps=True,
        )
        export_parts(source_table=source_table, destination_table=s3_table_name)
        wait_for_all_exports_to_complete()

    with Then("I verify computed columns are correct in source"):
        source_data = self.context.node.query(
            f"SELECT p, id, name, upper_name, concat_result FROM {source_table} ORDER BY p",
            exitcode=0,
            steps=True,
        ).output.strip()
        assert "1\t100\tAlice\tALICE\tAlice-100" in source_data, error()
        assert "2\t200\tBob\tBOB\tBob-200" in source_data, error()

    with And(
        "I verify exported data matches source including materialized ALIAS and MATERIALIZED columns"
    ):
        verify_exported_data_matches_with_columns(
            source_table=source_table,
            destination_table=s3_table_name,
            columns="p, id, name, upper_name, concat_result",
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_JSON("1.0"))
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
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_JSON("1.0"))
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
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Nested("1.0"))
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
@Requirements(RQ_ClickHouse_ExportPart_ColumnTypes_Nested("1.0"))
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
@Name("columns")
def feature(self):
    """Check export part functionality with different column types: ALIAS, MATERIALIZED, EPHEMERAL, DEFAULT, JSON, and Nested."""

    Scenario(run=alias_columns)
    Scenario(run=materialized_columns)
    Scenario(run=ephemeral_columns)
    Scenario(run=default_columns_with_default_values)
    Scenario(run=default_columns_with_explicit_values)
    Scenario(run=mixed_columns)
    Scenario(run=complex_expressions)
    Scenario(run=json_columns)
    Scenario(run=json_columns_with_hints)
    Scenario(run=nested_columns)
    Scenario(run=complex_nested_columns)
