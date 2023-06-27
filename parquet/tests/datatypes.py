import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"))
def binary(self):
    with Given("I have a Parquet file with the binary datatype columns"):
        import_file = os.path.join("arrow", "binary.parquet")

    import_export(snapshot_name="binary_values_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def byte_array(self):
    with Given("I have a Parquet file with the decimal byte array datatype columns"):
        import_file = os.path.join("arrow", "byte_array_decimal.parquet")

    import_export(snapshot_name="byte_array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def fixed_length_decimal(self):
    with Given("I have a Parquet file with the fixed length decimal datatype columns"):
        import_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    import_export(
        snapshot_name="fixed_length_decimal_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def fixed_length_decimal_legacy(self):
    with Given(
        "I have a Parquet file with the fixed length decimal legacy datatype columns"
    ):
        import_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    import_export(
        snapshot_name="fixed_length_decimal_legacy_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def int32_decimal(self):
    with Given("I have a Parquet file with the int32 decimal datatype columns"):
        import_file = os.path.join("arrow", "int32_decimal.parquet")

    import_export(snapshot_name="int32_decimal_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def int64_decimal(self):
    with Given("I have a Parquet file with the int64 decimal datatype columns"):
        import_file = os.path.join("arrow", "int64_decimal.parquet")

    import_export(snapshot_name="int64_decimal_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def decimal_with_filter(self):
    with Given(
        "I have a Parquet file with the decimal value with specified filters of precision and scale"
    ):
        import_file = os.path.join("arrow", "lineitem-arrow.parquet")

    import_export(
        snapshot_name="decimal_with_filter_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def singlenull(self):
    with Given("I have a Parquet file with single null value"):
        import_file = os.path.join("arrow", "single_nan.parquet")

    import_export(snapshot_name="single_null_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_DataTypes_Unsupported("1.0"))
def unsupported_uuid(self):
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with single null value"):
        import_file = os.path.join("arrow", "uuid-arrow.parquet")

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """,
                message="DB::Exception: Unsupported Parquet type 'fixed_size_binary'",
                exitcode=50,
            )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0"),
)
def pandasdecimal(self):
    with Given(
        "I have a Parquet file generated via pandas library with the decimal values"
    ):
        import_file = os.path.join("decimal", "pandas_decimal.parquet")

    import_export(snapshot_name="pandas_decimal_structure", import_file=import_file)


@TestFeature
@Name("datatypes")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with various datatypes."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "datatypes"

    for scenario in loads(current_module(), Scenario):
        scenario()
