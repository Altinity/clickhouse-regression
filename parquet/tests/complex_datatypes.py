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
# @XFailed("Difference between imported values and exported values")
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT("1.0"),
)
def nestedstruct(self):
    """Check importing and exporting the Parquet file with the nested map value."""
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
def tuple_of_nulls(self):
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
