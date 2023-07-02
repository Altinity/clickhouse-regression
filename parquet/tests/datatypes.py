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
    import_file = os.path.join("arrow", "file_row_number.parquet")
    pass

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
def decimal_with_filter2(self):
    """Check importing and exporting the Parquet file with the decimal with specified filter Decimal(precision=15, scale=2)."""
    import_file = os.path.join("arrow", "p2strings.parquet")
    pass

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
    """Checking that the fixed_size_binary is not supported by CliCkhouse when trying to import from the Parquet files."""
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
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas("1.0"))
def pandasdecimal(self):
    """Checking that ClickHouse can import and export Parquet files created via pandas."""
    with Given(
        "I have a Parquet file generated via pandas library with the decimal values"
    ):
        import_file = os.path.join("decimal", "pandas_decimal.parquet")

    import_export(snapshot_name="pandas_decimal_structure", import_file=import_file)

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas("1.0"),
              RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"))
def pandasdecimal_date(self):
    """Checking that ClickHouse can import and export Parquet files with a timestamp column from an arrow-parquet generated file via pandas."""
    import_file = os.path.join("datatypes", "pandas-date.parquet")
    pass

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_ParquetGO("1.0"),)
def parquet_go(self):
    """Checking that ClickHouse can import and export Parquet files generated via parquet-go library."""
    import_file = os.path.join("datatypes", "parquet_go.parquet")
    pass

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Libraries_H2OAI("1.0"))
def h2oai(self):
    """Checking that ClickHouse can import and export Parquet files created via h2oAI."""
    with Given("I have a Parquet file generated via h2oAI"):
        import_file = os.path.join("h2oai", "h2oai_group_small.parquet")

    import_export(snapshot_name="h2oai_structure", import_file=import_file)


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
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0")
)
def enum(self):
    """Checking that ClickHouse can import and export Parquet file with enum datatype."""
    import_file = os.path.join("datatypes", "adam_genotypes.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"),
)
def enum2(self):
    """Checking that ClickHouse can import and export Parquet file with enum datatype."""
    import_file = os.path.join("datatypes", "enum.parquet")
    pass

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
def manydatatypes(self):
    """Checking that ClickHouse can import and export a single Parquet file with int, float, decimal, string, bool and date datatypes."""
    import_file = os.path.join("datatypes", "data-types.parquet")
    pass


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE("1.0"),
)
def date(self):
    """Checking that ClickHouse can import and export a Parquet file with date datatype."""
    import_file = os.path.join("datatypes", "date.parquet")
    pass


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ns("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ns("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"),
)
def timestamp(self):
    """Checking that ClickHouse can import and export a Parquet file with timestamp (ms, ns) datatypes."""
    import_file = os.path.join("datatypes", "date_stats.parquet")
    pass


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
)
def stat_decimal(self):
    """Checking that ClickHouse can import and export a Parquet file with decimal datatype having
    CAST(-999999999999999999999999999999999.99999 AS DECIMAL(38,5)) as a column name."""
    import_file = os.path.join("datatypes", "decimal_stats.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL("1.0"),
)
def decimal_various_filters(self):
    """Checking that ClickHouse can import and export a Parquet file with decimal datatype having various precision filters."""
    import_file = os.path.join("datatypes", "decimals.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray("1.0"),
)
def fixedstring(self):
    """Checking that ClickHouse can import and export Parquet file with FixedString(16) datatype."""
    import_file = os.path.join("datatypes", "fixed.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported("1.0"),
)
def json(self):
    """Checking that ClickHouse can't import json from parquet files datatype."""
    import_file = os.path.join("datatypes", "json_convertedtype.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE("1.0"),
)
def large_double(self):
    """Checking that ClickHouse can import and export a very large Parquet file with double datatype."""
    import_file = os.path.join("datatypes", "leftdate3_192_loop_1.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE("1.0"),
)
def nan_double(self):
    """Checking that ClickHouse can import and export a Parquet file with double datatype having an infinity value."""
    import_file = os.path.join("datatypes", "nan-float.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE("1.0"),
)
def nan_double(self):
    """Checking that ClickHouse can import and export a Parquet file with double datatype having an infinity value."""
    import_file = os.path.join("datatypes", "nan-float.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def nullbyte(self):
    """Checking that ClickHouse can import and export a Parquet file with null bytes in strings."""
    import_file = os.path.join("datatypes", "nullbyte.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def nullbyte_multiple(self):
    """Checking that ClickHouse can import and export a Parquet file with multiple null bytes in strings."""
    import_file = os.path.join("datatypes", "nullbyte_multiple.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def nulls_in_id(self):
    """Checking that ClickHouse can import and export a Parquet file with int64 datatype having nulls."""
    import_file = os.path.join("datatypes", "p2.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def names_with_emoji(self):
    """Checking that ClickHouse can import and export a Parquet file with emojis for column names."""
    import_file = os.path.join("datatypes", "silly-names.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark("1.0"),
)
def spark_v2_1(self):
    """Checking that ClickHouse can import and export a Parquet file generated via Spark's Parquet v2 writer."""
    import_file = os.path.join("datatypes", "spark-ontime.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark("1.0"),
)
def spark_v2_2(self):
    """Checking that ClickHouse can import and export a Parquet file generated via Spark's Parquet v2 writer."""
    import_file = os.path.join("datatypes", "spark-store.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def struct(self):
    """Checking that ClickHouse can import and export a Parquet file with struct."""
    import_file = os.path.join("datatypes", "struct.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP("1.0"),
)
def struct_skip(self):
    """Checking that ClickHouse can import a Parquet file with sizable dataset that contains a map."""
    import_file = os.path.join("datatypes", "struct.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0")
)
def arrow_timestamp(self):
    """Checking that ClickHouse can import a Parquet file with timestamp column from a pyarrow generated file."""
    import_file = os.path.join("datatypes", "timestamp.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms("1.0"),
)
def arrow_timestamp_ms(self):
    """Checking that ClickHouse can import a Parquet file with timestamp (ms) column from a pyarrow generated file."""
    import_file = os.path.join("datatypes", "timestamp.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_DateUTCAdjusted("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64("1.0"),
)
def timezone(self):
    """Checking that ClickHouse can import a Parquet file with timezone information."""
    import_file = os.path.join("datatypes", "tz.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT8("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT16("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT64("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT8("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT16("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT32("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT64("1.0"),
)
def unsigned(self):
    """Checking that ClickHouse can import a Parquet file with timezone information."""
    import_file = os.path.join("datatypes", "unsigned.parquet")
    import_file2 = os.path.join("datatypes", "unsigned_stats.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def string_types(self):
    """Checking that ClickHouse can import and export Parquet files containing different string values like emojis, symbols, etc."""
    import_file = os.path.join("datatypes", "userdata1.parquet")
    pass

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING("1.0"),
)
def column_name(self):
    """Checking that ClickHouse can import and export Parquet files having hello\x00world as column name."""
    import_file = os.path.join("datatypes", "varchar_stats.parquet")
    pass

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
