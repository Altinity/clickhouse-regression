import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_LIST("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_LIST("1.0"),
)
def list(self):
    """Check importing and exporting the Parquet file with the array value."""
    with Given("I have a Parquet file with the array datatype"):
        import_file = os.path.join("arrow", "list_columns.parquet")

    import_export(snapshot_name="array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_LIST("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_LIST("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
)
def nested_array(self):
    """Check importing and exporting the Parquet file with the nested array value and snappy compression."""
    with Given(
        "I have a Parquet file with the nested array datatype and snappy compression"
    ):
        import_file = os.path.join("arrow", "nested_lists.snappy.parquet")

    import_export(snapshot_name="nested_array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
)
def nested_map(self):
    """Check importing and exporting the Parquet file with the nested map value."""
    with Given("I have a Parquet file with the nested map datatype"):
        import_file = os.path.join("arrow", "nested_maps.snappy.parquet")

    import_export(snapshot_name="nested_map_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def nestedstruct(self):
    """Check importing and exporting the Parquet file with the nested struct value."""
    with Given("I have a Parquet file with the nested struct datatype"):
        import_file = os.path.join("arrow", "nested_structs.rust.parquet")

    import_export(snapshot_name="nested_struct_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
)
def complex_null(self):
    """Check importing and exporting the Parquet file with the nested complex datatypes that have null values."""
    with Given("I have a Parquet file with the array, map and tuple with null values"):
        import_file = os.path.join("arrow", "nullable.impala.parquet")

    import_export(snapshot_name="complex_null_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def tupleofnulls(self):
    """Check importing and exporting the Parquet file with the nested tuple with null values."""
    with Given("I have a Parquet file with the tuple of nulls"):
        import_file = os.path.join("arrow", "nulls.snappy.parquet")

    import_export(snapshot_name="tuple_of_nulls_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def big_tuple_with_nulls(self):
    """Check importing and exporting a big Parquet file with the nested tuple with null values."""
    with Given("I have a Parquet file with the big tuple with nulls"):
        import_file = os.path.join("arrow", "repeated_no_annotation.parquet")

    import_export(
        snapshot_name="big_tuple_with_nulls_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested("1.0"),
)
def arraystring(self):
    """Check importing and exporting a Parquet file with nested array containing strings."""
    with Given("I have a Parquet file with nested array containing strings"):
        import_file = os.path.join("datatypes", "apkwan.parquet")

    import_export(snapshot_name="array_string_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_ARRAY("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_ARRAY("1.0"),
)
def largenestedarray(self):
    """Check importing and exporting a large Parquet file with arrays."""
    with Given("I have a large Parquet file with array datatype"):
        import_file = os.path.join("datatypes", "candidate.parquet")

    import_export(snapshot_name="large_array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def largestruct(self):
    """Check importing and exporting a large Parquet file with struct."""
    with Given("I have a large Parquet file with struct datatype"):
        import_file = os.path.join("datatypes", "complex.parquet")

    import_export(snapshot_name="large_struct_structure1", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def largestruct2(self):
    """Check importing and exporting a large Parquet file with struct."""
    with Given("I have a large Parquet file with struct datatype"):
        import_file = os.path.join("malloy-smaller", "tbl_.parquet")

    import_export(
        snapshot_name="large_nested_struct_2_structure", import_file=import_file
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def largestruct3(self):
    """Check importing and exporting a large Parquet file with struct."""
    with Given("I have a large Parquet file with struct datatype"):
        import_file = os.path.join("datatypes", "bug4859.parquet")

    import_export(snapshot_name="large_struct_3_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP("1.0"),
)
def lagemap(self):
    """Check importing and exporting a large Parquet file with map."""
    with Given("I have a large Parquet file with map datatype"):
        import_file = os.path.join("datatypes", "map.parquet")

    import_export(snapshot_name="large_map_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def tuplewithdatetime(self):
    """Check importing and exporting a large Parquet file with tuple containing DateTime64(6, 'UTC'))."""
    with Given(
        "I have a large Parquet file with tuple containing DateTime64(6, 'UTC'))"
    ):
        import_file = os.path.join("datatypes", "simple.parquet")

    import_export(
        snapshot_name="struct_datetime64_UTC_2_structure", import_file=import_file
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
def bytearraydictionary(self):
    """Check importing and exporting a Parquet file with dictionary of fixed length byte arrays."""
    with Given(
        "I have a large Parquet file with dictionary of fixed length byte arrays"
    ):
        import_file = os.path.join("datatypes", "sorted.zstd_18_131072_small.parquet")

    import_export(
        snapshot_name="fixed_length_byte_dictionary_structure",
        import_file=import_file,
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Nested("1.0"),
)
def nestedallcomplex(self):
    """Check importing and exporting a Parquet file with nested complex datatypes."""
    with Given("I have a large Parquet file with nested complex datatypes"):
        import_file = os.path.join("datatypes", "test_unnest_rewriter.parquet")

    import_export(snapshot_name="complex_nested_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def nestedstruct2(self):
    """Checking that ClickHouse can import and export Parquet files with nested struct."""
    with Given("I have a Parquet file with with nested struct"):
        import_file = os.path.join("datatypes", "bug1589.parquet")

    import_export(snapshot_name="nestedstruct_2_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def nestedstruct3(self):
    """Checking that ClickHouse can import and export Parquet files with nested struct."""
    with Given("I have a Parquet file with with nested struct"):
        import_file = os.path.join("datatypes", "bug2267.parquet")

    import_export(snapshot_name="nestedstruct_3_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def nestedstruct4(self):
    """Checking that ClickHouse can import and export Parquet files with nested struct."""
    with Given("I have a Parquet file with with nested struct"):
        import_file = os.path.join("datatypes", "issue_6013.parquet")

    import_export(snapshot_name="nestedstruct_4_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_ARRAY("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_ARRAY("1.0"),
)
def nestedarray2(self):
    """Checking that ClickHouse can import and export Parquet files with nested array."""
    with Given("I have a Parquet file with with nested array"):
        import_file = os.path.join("datatypes", "bug2557.parquet")

    import_export(snapshot_name="nestedarray_2_structure", import_file=import_file)


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Nested_Complex("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Nested_Complex("1.0"),
)
@Name("complex")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with complex datatypes."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "complex_datatypes"
    for scenario in loads(current_module(), Scenario):
        scenario()
