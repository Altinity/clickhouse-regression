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
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
)
def fixed_length_decimal(self):
    """Check importing and exporting the Parquet file with Decimal(precision=25, scale=2)."""
    with Given("I have a Parquet file with the fixed length decimal datatype columns"):
        import_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    import_export(
        snapshot_name="fixed_length_decimal_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
)
def fixed_length_decimal_legacy(self):
    """Check importing and exporting the Parquet file with the Decimal(precision=13, scale=2)."""
    with Given(
        "I have a Parquet file with the fixed length decimal legacy datatype columns"
    ):
        import_file = os.path.join("arrow", "fixed_length_decimal_legacy.parquet")

    import_export(
        snapshot_name="fixed_length_legacy_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray_FLOAT16(
        "1.0"
    )
)
def float16(self):
    """Check importing a Parquet file with the FLOAT16 logical type."""

    node = self.context.node
    table_name = "table_" + getuid()
    expected = "[-2,-1,0,1,2,3,4,5,6,7,8,9]"

    # TODO: Once ClickHouse works correctly with FLOAT16, use snapshot

    with Given("I have a Parquet file with float16 logical type columns"):
        import_file = os.path.join("datatypes", "float16.parquet")

    try:
        with And("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name} (floatfield Float32)
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT floatfield FROM file('{import_file}', Parquet)
                """
            )

        with Then("I read the contents of the created table"):
            output = node.query(
                f"SELECT groupArray(round(*)) FROM {table_name} FORMAT TSV"
            ).output
            assert output == expected, error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


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
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def int64(self):
    """Check importing and exporting the Parquet file with int64."""
    with Given("I have a Parquet file with the int64 datatype columns"):
        import_file = os.path.join("datatypes", "file_row_number.parquet")

    import_export(snapshot_name="int64_structure1", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL_Filter("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL_Filter("1.0"),
)
def decimal_with_filter(self):
    """Check importing and exporting the Parquet file with the decimal with specified filter Decimal(precision=15, scale=2)."""
    with Given(
        "I have a Parquet file with the decimal value with specified filters of precision and scale"
    ):
        import_file = os.path.join("arrow", "lineitem-arrow.parquet")

    import_export(
        snapshot_name="decimal_with_filter_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL_Filter("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL_Filter("1.0"),
)
def decimalwithfilter2(self):
    """Check importing and exporting the Parquet file with the decimal with specified filter Decimal(precision=15, scale=2)."""
    with Given("I have a Parquet file with the Decimal(precision=15, scale=2)"):
        import_file = os.path.join("datatypes", "p2strings.parquet")

    import_export(snapshot_name="decimal_15_2_structure", import_file=import_file)


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
def supporteduuid(self):
    """Checking that the fixed_size_binary is supported by CliCkhouse when trying to import from the Parquet file."""
    with Given("I have a Parquet file with uuid"):
        import_file = os.path.join("arrow", "uuid-arrow.parquet")

    import_export(snapshot_name="uuid_2_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas("1.0"))
def pandasdecimal(self):
    """Checking that ClickHouse can import and export Parquet files created via pandas."""
    with Given(
        "I have a Parquet file generated via pandas library with the decimal values"
    ):
        import_file = os.path.join("decimal", "pandas_decimal.parquet")

    import_export(snapshot_name="pandas_decimal_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE("1.0"),
)
def pandasdecimaldate(self):
    """Checking that ClickHouse can import and export Parquet files with a DATE column from an arrow-parquet generated file via pandas."""
    with Given(
        "I have a Parquet file with a DATE generated via arrow-parquet and pandas libraries"
    ):
        import_file = os.path.join("datatypes", "pandas-date.parquet")

    import_export(
        snapshot_name="pandas_arrow_timestamp_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_ParquetGO("1.0"),
)
def parquetgo(self):
    """Checking that ClickHouse can import and export Parquet files generated via parquet-go library."""
    with Given("I have a Parquet file generated via parquet-go library"):
        import_file = os.path.join("datatypes", "parquet_go.parquet")

    snapshot_name = (
        "parquet_go_structure_above_26"
        if check_clickhouse_version(">=26.1")(self)
        else "parquet_go_structure"
    )
    import_export(snapshot_name=snapshot_name, import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_H2OAI("1.0"))
def h2oai(self):
    """Checking that ClickHouse can import and export Parquet files created via h2oAI."""
    with Given("I have a Parquet file generated via h2oAI"):
        import_file = os.path.join("h2oai", "h2oai_group_small.parquet")

    import_export(snapshot_name="h2oai_structure3123", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def string(self):
    """Checking that ClickHouse can import and export Parquet files with String datatype."""
    with Given("I have a Parquet file with String datatype"):
        import_file = os.path.join("hive-partitioning", "test.parquet")

    import_export(snapshot_name="string_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Hive("1.0"))
def hive(self):
    """Checking if the ClickHouse can import and export parquet files created for hive partitioning."""
    for page_number in range(1, 3):
        with Given("I have a Parquet file created for hive partitioning datatype"):
            import_file = os.path.join("hive-partitioning", f"f{page_number}.parquet")

        import_export(
            snapshot_name=f"f{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray("1.0")
)
def enum(self):
    """Checking that ClickHouse can import and export Parquet file with enum datatype."""
    with Given("I have a Parquet file with enum datatype"):
        import_file = os.path.join("datatypes", "adam_genotypes.parquet")

    snapshot_name = (
        "enum_structure_above_26"
        if check_clickhouse_version(">=26.1")(self)
        else "enum_structure"
    )
    import_export(snapshot_name=snapshot_name, import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"),
)
def enum2(self):
    """Checking that ClickHouse can import and export Parquet file with enum datatype."""
    with Given("I have a Parquet file with enum datatype"):
        import_file = os.path.join("datatypes", "enum.parquet")

    import_export(snapshot_name="enum_structure_2", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
)
def binary_string(self):
    """Checking that ClickHouse can import a parquet file with a binary values as a string and export it back."""
    with Given("I have a Parquet file with binary datatype"):
        import_file = os.path.join("datatypes", "binary_string.parquet")

    import_export(snapshot_name="binary_string_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BLOB("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BLOB("1.0"),
)
def blob(self):
    """Checking that ClickHouse can import and export Parquet files with blob values."""
    with Given("I have a Parquet file with blob values"):
        import_file = os.path.join("datatypes", "blob.parquet")

    import_export(snapshot_name="blob_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BOOL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BOOL("1.0"),
)
def boolean(self):
    """Checking that ClickHouse can import and export Parquet files with boolean datatype."""
    with Given(
        "I have a Parquet file with boolean datatype containing true and false values"
    ):
        import_file = os.path.join("datatypes", "boolean_stats.parquet")

    import_export(snapshot_name="boolean_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FLOAT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FLOAT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BOOL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BOOL("1.0"),
)
def manydatatypes(self):
    """Checking that ClickHouse can import and export a single Parquet file with int, float, decimal, string, bool and date datatypes."""
    with Given(
        "I have a Parquet file with int, float, decimal, string, bool and date datatypes"
    ):
        import_file = os.path.join("datatypes", "data-types.parquet")

    import_export(snapshot_name="many_datatypes_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE("1.0"),
)
def date(self):
    """Checking that ClickHouse can import and export a Parquet file with date datatype."""
    with Given("I have a Parquet file with date datatype"):
        import_file = os.path.join("datatypes", "date.parquet")

    import_export(snapshot_name="date_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ns("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ns("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"),
)
def timestamp1(self):
    """Checking that ClickHouse can import and export a Parquet file with timestamp (ms, ns) datatypes."""
    with Given("I have a Parquet file with timestamp (ms, ns) datatype"):
        import_file = os.path.join("datatypes", "date_stats.parquet")

    import_export(snapshot_name="timestamp_ms_ns_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
)
def statdecimal(self):
    """Checking that ClickHouse can import and export a Parquet file with decimal datatype having
    CAST(-999999999999999999999999999999999.99999 AS DECIMAL(38,5)) as a column name."""
    with Given("I have a Parquet file with decimal datatype"):
        import_file = os.path.join("datatypes", "decimal_stats.parquet")

    import_export(snapshot_name="decimal_table_name_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
)
def decimalvariousfilters(self):
    """Checking that ClickHouse can import and export a Parquet file with decimal datatype having various precision filters."""
    with Given("I have a Parquet file with decimal datatype"):
        import_file = os.path.join("datatypes", "decimals.parquet")

    import_export(
        snapshot_name="decimal_various_precision_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray(
        "1.0"
    ),
)
def fixedstring(self):
    """Checking that ClickHouse can import and export Parquet file with FixedString(16) datatype."""
    with Given("I have a Parquet file with FixedString(16) datatype"):
        import_file = os.path.join("datatypes", "fixed.parquet")

    snapshot_name = (
        "fixed_structure_above_26"
        if check_clickhouse_version(">=26.1")(self)
        else "fixed_structure"
    )
    import_export(snapshot_name=snapshot_name, import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"),
)
def json(self):
    """Checking that ClickHouse can't import json from parquet files datatype."""
    with Given("I have a Parquet file with json datatype"):
        import_file = os.path.join("datatypes", "json_convertedtype.parquet")

    import_export(snapshot_name="json_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE("1.0"),
)
def largedouble(self):
    """Checking that ClickHouse can import and export a very large Parquet file with double datatype."""
    with Given("I have a large Parquet file with double datatype"):
        import_file = os.path.join("datatypes", "leftdate3_192_loop_1.parquet")

    import_export(
        snapshot_name="double_structure",
        import_file=import_file,
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE("1.0"),
)
def nandouble(self):
    """Checking that ClickHouse can import and export a Parquet file with double datatype having an infinity value."""
    with Given("I have a large Parquet file with infinity value"):
        import_file = os.path.join("datatypes", "nan-float.parquet")

    import_export(snapshot_name="nan_double_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def nullbyte(self):
    """Checking that ClickHouse can import and export a Parquet file with null bytes in strings."""
    with Given("I have a large Parquet file with null bytes in strings"):
        import_file = os.path.join("datatypes", "nullbyte.parquet")

    import_export(snapshot_name="nullbytes_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def nullbytemultiple(self):
    """Checking that ClickHouse can import and export a Parquet file with multiple null bytes in strings."""
    with Given("I have a large Parquet file with multiple null bytes in strings"):
        import_file = os.path.join("datatypes", "nullbyte_multiple.parquet")

    import_export(snapshot_name="multiple_nullbytes_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def nullsinid(self):
    """Checking that ClickHouse can import and export a Parquet file with int64 datatype having nulls in id column."""
    with Given("I have a large Parquet file with int64 datatype having nulls"):
        import_file = os.path.join("datatypes", "p2.parquet")

    snapshot_name = (
        "int64_nulls_structure_above_26"
        if check_clickhouse_version(">=26.1")(self)
        else "int64_nulls_structure"
    )
    import_export(snapshot_name=snapshot_name, import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def nameswithemoji(self):
    """Checking that ClickHouse can import and export a Parquet file with emojis for column names."""
    with Given("I have a large Parquet file emojis for column names"):
        import_file = os.path.join("datatypes", "silly-names.parquet")

    import_export(snapshot_name="silly_names_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark("1.0"),
)
def sparkv21(self):
    """Checking that ClickHouse can import and export a Parquet file generated via Spark's Parquet v2 writer."""
    with Given("I have a large Parquet file generated via Spark's Parquet v2 writer"):
        import_file = os.path.join("datatypes", "spark-ontime.parquet")

    import_export(snapshot_name="pyspark_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark("1.0"),
)
def sparkv22(self):
    """Checking that ClickHouse can import and export a Parquet file generated via Spark's Parquet v2 writer."""
    with Given("I have a large Parquet file generated via Spark's Parquet v2 writer"):
        import_file = os.path.join("datatypes", "spark-store.parquet")

    import_export(snapshot_name="pyspark_structure_2", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def struct(self):
    """Checking that ClickHouse can import and export a Parquet file with struct."""
    with Given("I have a large Parquet file with struct datatype"):
        import_file = os.path.join("datatypes", "struct.parquet")

    import_export(snapshot_name="struct_structure_1", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP("1.0"),
)
def maps(self):
    """Checking that ClickHouse can import a Parquet file with sizable dataset that contains a map."""
    with Given("I have a large Parquet file with sizable dataset that contains a map"):
        import_file = os.path.join("datatypes", "struct_skip_test.parquet")

    import_export(snapshot_name="map_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms("1.0"),
)
def arrowtimestamp(self):
    """Checking that ClickHouse can import a Parquet file with timestamp column from a pyarrow generated file."""
    with Given(
        "I have a large Parquet file with timestamp column from a pyarrow generated file"
    ):
        import_file = os.path.join("datatypes", "timestamp.parquet")

    import_export(snapshot_name="arrow_timestamp_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"),
)
def arrowtimestampms(self):
    """Checking that ClickHouse can import a Parquet file with timestamp (ms) column from a pyarrow generated file."""
    with Given(
        "I have a large Parquet file with timestamp (ms) column from a pyarrow generated file"
    ):
        import_file = os.path.join("datatypes", "timestamp-ms.parquet")

    import_export(snapshot_name="arrow_timestamp_ms_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_DateUTCAdjusted("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def timezone(self):
    """Checking that ClickHouse can import a Parquet file with timezone information."""
    with Given("I have a large Parquet file with timezone information"):
        import_file = os.path.join("datatypes", "tz.parquet")

    import_export(snapshot_name="timestamp_timezone_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT8("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT16("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT8("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT16("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT64("1.0"),
)
def unsigned(self):
    """Checking that ClickHouse can import and export Parquet files with unsigned integers."""
    unsigned_parquet = ["unsigned", "unsigned_stats"]

    for file_name in unsigned_parquet:
        with Given("I have a large Parquet Parquet files with unsigned integers"):
            import_file = os.path.join("datatypes", f"{file_name}.parquet")

        import_export(snapshot_name=f"{file_name}_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def stringtypes(self):
    """Checking that ClickHouse can import and export Parquet files containing different string values like emojis, symbols, etc."""
    with Given("I have a large Parquet file with different string values like emojis"):
        import_file = os.path.join("datatypes", "userdata1.parquet")

    import_export(snapshot_name="user_data_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def columnname(self):
    """Checking that ClickHouse can import and export Parquet files having hello\x00world as column name."""
    with Given(
        r"I have a large Parquet file with having hello\x00world as column name"
    ):
        import_file = os.path.join("datatypes", "varchar_stats.parquet")

    import_export(snapshot_name="column_name_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
)
def columnwithnull(self):
    """Checking that ClickHouse can import and export Parquet files with null values inside columns."""
    with Given("I have a Parquet file with null values inside columns"):
        import_file = os.path.join("datatypes", "bug687_nulls.parquet")

    import_export(snapshot_name="column_with_nulls_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
)
def columnwithnull2(self):
    """Checking that ClickHouse can import and export Parquet files with null values inside columns."""
    with Given("I have a Parquet file with null values inside columns"):
        import_file = os.path.join("datatypes", "bug1554.parquet")

    import_export(
        snapshot_name="column_with_nulls_2_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BOOL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BOOL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def manydatatypes2(self):
    """Checking that ClickHouse can import and export Parquet files with int32, int64, BOOLEAN and String."""
    with Given("I have a Parquet file with int32, int64, BOOLEAN and String datatypes"):
        import_file = os.path.join("datatypes", "bug1588.parquet")

    import_export(snapshot_name="many_datatypes_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32("1.0"),
)
def int32(self):
    """Checking that ClickHouse can import and export Parquet files with int32."""
    with Given("I have a Parquet file with int32 datatype"):
        import_file = os.path.join("datatypes", "bug1589.parquet")

    import_export(snapshot_name="int32_1_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32("1.0"),
)
def int32(self):
    """Checking that ClickHouse can import and export Parquet Int(bitWidth=32, isSigned=true)."""
    with Given("I have a Parquet file with Int(bitWidth=32, isSigned=true)"):
        import_file = os.path.join("datatypes", "bug3734.parquet")

    import_export(snapshot_name="int32_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ns("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ns("1.0"),
)
def timestamp2(self):
    """Checking that ClickHouse can import and export Parquet file with Timestamp(isAdjustedToUTC=true, timeUnit=nanoseconds, is_from_converted_type=false, force_set_converted_type=false)."""
    with Given(
        "I have a Parquet file with Timestamp(isAdjustedToUTC=true, timeUnit=nanoseconds, is_from_converted_type=false, force_set_converted_type=false)"
    ):
        import_file = os.path.join("datatypes", "bug4442.parquet")

    import_export(snapshot_name="int32_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def negativeint64(self):
    """Checking that ClickHouse can import and export Parquet file with negative int64 values."""
    with Given("I have a Parquet file with negative int64"):
        import_file = os.path.join("datatypes", "bug4903.parquet")

    import_export(snapshot_name="int64_negative_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def large_string_map(self):
    """Checking that ClickHouse can import and export Parquet file with negative int64 values."""
    with Given("I have a Parquet file with negative int64"):
        import_file = os.path.join("arrow", "large_string_map.brotli.parquet")

    snapshot_name = (
        "large_string_map_structure_above_26"
        if check_clickhouse_version(">=26.1")(self)
        else "large_string_map_structure"
    )
    import_export(snapshot_name=snapshot_name, import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def selectdatewithfilter(self):
    """Checking that ClickHouse can import and export Parquet files with dates using filters."""
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/{table_name}.parquet"

    with Given("I have a Parquet file with negative int64"):
        import_file = os.path.join("datatypes", "filter_bug1391.parquet")

    with And("I save file structure"):
        import_column_structure = node.query(
            f"DESCRIBE TABLE file('{import_file}') FORMAT TabSeparated"
        )

    with Check("import"):
        with When("I try to import the binary Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet) WHERE NAMEVALIDFROM <= '2017-03-01' ORDER BY ORGUNITID
                """
            )

        with And("I read the contents of the created table"):
            import_read = node.query(
                f"SELECT * FROM {table_name} ORDER BY ORGUNITID FORMAT TabSeparated"
            )

        with Then("I check the output is correct"):
            with values() as that:

                snapshot_name = "import_using_filter_structure_above_26" if check_clickhouse_version(">=26.1")(self) else "import_using_filter_structure"

                assert that(
                    snapshot(
                        import_column_structure.output.strip(),
                        name=snapshot_name,
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet) ORDER BY ORGUNITID FORMAT TabSeparated"
            )

        with Then("output must match the snapshot"):
            assert read.output.strip() == import_read.output.strip(), error()

        with And("I check that table structure matches ..."):
            export_columns_structure = node.query(
                f"DESCRIBE TABLE file('{path_to_export}') FORMAT TabSeparated"
            )
            assert (
                import_column_structure.output.strip()
                == export_columns_structure.output.strip()
            ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"),
)
def unsupportednull(self):
    """Checking that ClickHouse outputs an error when trying to import a Parquet file with 'null' datatype."""

    node = self.context.node

    for number in range(1, 3):
        table_name = "table_" + getuid()

        if check_clickhouse_version(">=26.1")(self):
            message, exitcode = (None, 0)
        elif check_clickhouse_version("<24.2")(self):
            message, exitcode = ("DB::Exception: Unsupported Parquet type", 50)
        else:
            message, exitcode = ("DB::Exception: Unsupported Parquet type", 124)

        with Given("I have a Parquet file with null datatype"):
            import_file = os.path.join("datatypes", f"issue6630_{number}.parquet")

        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """,
                message=message,
                exitcode=exitcode,
                settings=[("max_memory_usage", 20000000000)]
            )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Offsets_MonotonicallyIncreasing("1.0"))
def string_int_list_inconsistent_offset_multiple_batches(self):
    """Checking that ClickHouse does not crash when importing and exporting the parquet file with monotonically increassing offsets."""
    with Given("I have a Parquet file with monotonically increasing offsets"):
        import_file = os.path.join(
            "datatypes", "string_int_list_inconsistent_offset_multiple_batches.parquet"
        )

    import_export(
        snapshot_name="inconsistent_offsets", import_file=import_file, limit=1
    )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
)
@Name("datatypes")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with various datatypes."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "datatypes"

    for scenario in loads(current_module(), Scenario):
        scenario()
