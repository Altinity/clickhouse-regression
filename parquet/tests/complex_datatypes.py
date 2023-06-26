import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export

snapshot_id = "complex_datatypes"


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def array(self):
    with Given("I have a Parquet file with the array datatype"):
        import_file = os.path.join("arrow", "list_columns.parquet")

    import_export(snapshot_name="array_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_array(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_lists.snappy.parquet")

    import_export(snapshot_name="nested_array_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_map(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_maps.snappy.parquet")

    import_export(snapshot_name="nested_map_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@XFailed("Difference between imported values and exported values")
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_struct(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_structs.rust.parquet")

    import_export(snapshot_name="nested_struct_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def complex_null(self):
    with Given(
        "I have a Parquet file with the array, map and tuple with null values datatype"
    ):
        import_file = os.path.join("arrow", "nullable.impala.parquet")

    import_export(snapshot_name="complex_null_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def tuple_of_nulls(self):
    with Given("I have a Parquet file with the tuple of nulls datatype"):
        import_file = os.path.join("arrow", "nulls.snappy.parquet")

    import_export(snapshot_name="tuple_of_nulls_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def big_tuple_with_nulls(self):
    with Given("I have a Parquet file with the big tuple with nulls datatype"):
        import_file = os.path.join("arrow", "repeated_no_annotation.parquet")

    import_export(
        snapshot_name="big_tuple_with_nulls_structure", import_file=import_file, snapshot_id=snapshot_id
    )


@TestFeature
@Name("complex")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with complex datatypes."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
