import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BINARY("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BINARY("1.0"),
)
def binary(self):
    """Check importing and exporting the Parquet file with the binary."""
    with Given("I have a Parquet file with the binary datatype columns"):
        import_file = os.path.join("arrow", "binary.parquet")

    import_export(snapshot_name="binary_values_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
)
def byte_array(self):
    """Check importing and exporting the Parquet file with the byte_array."""
    with Given("I have a Parquet file with the decimal byte array datatype columns"):
        import_file = os.path.join("arrow", "byte_array_decimal.parquet")

    import_export(snapshot_name="byte_array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
)
def fixed_length_decimal(self):
    """Check importing and exporting the Parquet file with the fixed_length_decimal."""
    with Given("I have a Parquet file with the fixed length decimal datatype columns"):
        import_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    import_export(
        snapshot_name="fixed_length_decimal_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
)
def fixed_length_decimal_legacy(self):
    """Check importing and exporting the Parquet file with the legacy fixed_length_decimal."""
    with Given(
        "I have a Parquet file with the fixed length decimal legacy datatype columns"
    ):
        import_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    import_export(
        snapshot_name="fixed_length_decimal_legacy_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32("1.0"),
)
def int32_decimal(self):
    """Check importing and exporting the Parquet file with the int32 with decimal."""
    with Given("I have a Parquet file with the int32 decimal datatype columns"):
        import_file = os.path.join("arrow", "int32_decimal.parquet")

    import_export(snapshot_name="int32_decimal_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def int64_decimal(self):
    """Check importing and exporting the Parquet file with the int64 with decimal."""
    with Given("I have a Parquet file with the int64 decimal datatype columns"):
        import_file = os.path.join("arrow", "int64_decimal.parquet")

    import_export(snapshot_name="int64_decimal_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL_Filter("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL_Filter("1.0"),
)
def decimal_with_filter(self):
    """Check importing and exporting the Parquet file with the decimal with specified filter."""
    with Given(
        "I have a Parquet file with the decimal value with specified filters of precision and scale"
    ):
        import_file = os.path.join("arrow", "lineitem-arrow.parquet")

    import_export(
        snapshot_name="decimal_with_filter_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
)
def singlenull(self):
    """Check importing and exporting the Parquet file with the single null value."""
    with Given("I have a Parquet file with single null value"):
        import_file = os.path.join("arrow", "single_nan.parquet")

    import_export(snapshot_name="single_null_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"))
def unsupported_uuid(self):
    """Checking that the fixed_size_binary is not supported by CliCkhouse when trying to import from the Parquet files"""
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
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
)
def pandasdecimal(self):
    """Checking that ClickHouse can import and export Parquet files created via pandas"""
    with Given(
        "I have a Parquet file generated via pandas library with the decimal values"
    ):
        import_file = os.path.join("decimal", "pandas_decimal.parquet")

    import_export(snapshot_name="pandas_decimal_structure", import_file=import_file)


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
)
@Name("datatypes")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with various datatypes."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "datatypes"

    for scenario in loads(current_module(), Scenario):
        scenario()
