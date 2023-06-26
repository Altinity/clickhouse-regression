import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *

@TestOutline
def import_export(self, snapshot_name, import_file):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/{table_name}.parquet"

    with And("I save file structure"):
        import_column_structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

    with Check("import"):
        with When(f"I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            import_read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
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
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            assert read.output.strip() == import_read.output.strip(), error()

        with And("I check that table structure matches ..."):
            export_columns_structure = node.query(f"DESCRIBE TABLE file('{path_to_export}')")
            assert import_column_structure.output.strip() == export_columns_structure.output.strip(), error()

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def array(self):
    with Given("I have a Parquet file with the array datatype"):
        import_file = os.path.join("arrow", "list_columns.parquet")

    import_export(snapshot_name="array_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_array(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_lists.snappy.parquet")

    import_export(snapshot_name="nested_array_structure", import_file=import_file)

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_map(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_maps.snappy.parquet")

    import_export(snapshot_name="nested_map_structure", import_file=import_file)


@TestScenario
@XFailed("Difference between imported values and exported values")
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_struct(self):
    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_structs.rust.parquet")

    import_export(snapshot_name="nested_struct_structure", import_file=import_file)



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

    import_export(snapshot_name="complex_null_structure", import_file=import_file)



@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def tuple_of_nulls(self):
    with Given("I have a Parquet file with the tuple of nulls datatype"):
        import_file = os.path.join("arrow", "nulls.snappy.parquet")

    import_export(snapshot_name="tuple_of_nulls_structure", import_file=import_file)

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def big_tuple_with_nulls(self):
    with Given("I have a Parquet file with the big tuple with nulls datatype"):
        import_file = os.path.join("arrow", "repeated_no_annotation.parquet")

    import_export(snapshot_name="big_tuple_with_nulls_structure", import_file=import_file)

@TestFeature
@Name("complex")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
