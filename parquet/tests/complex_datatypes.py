import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def array(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/array_{table_name}.parquet"

    with Given("I have a Parquet file with the array datatype"):
        import_file = os.path.join("arrow", "list_columns.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="array_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="array")), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="array")), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="array_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_array(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/nested_array_{table_name}.parquet"

    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_lists.snappy.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="nested_array_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="nested_array")), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="nested_array")), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="nested_array_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_map(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/nested_map_{table_name}.parquet"

    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_maps.snappy.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="nested_map_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="nested_map")), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="nested_map")), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="nested_map_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
)
def nested_struct(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = (
        f"/var/lib/clickhouse/user_files/nested_struct_{table_name}.parquet"
    )

    with Given("I have a Parquet file with the nested array datatype"):
        import_file = os.path.join("arrow", "nested_structs.rust.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="nested_struct_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="nested_struct")
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="nested_struct")
                ), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="nested_struct_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def complex_null(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = (
        f"/var/lib/clickhouse/user_files/nested_struct_{table_name}.parquet"
    )

    with Given(
        "I have a Parquet file with the array, map and tuple with null values datatype"
    ):
        import_file = os.path.join("arrow", "nullable.impala.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="complex_null_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="complex_null")), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="complex_null")), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="complex_null_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def tupleofnulls(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = (
        f"/var/lib/clickhouse/user_files/nested_struct_{table_name}.parquet"
    )

    with Given("I have a Parquet file with the tuple of nulls datatype"):
        import_file = os.path.join("arrow", "nulls.snappy.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="tuple_of_nulls_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="tuple_of_nulls")
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="tuple_of_nulls")
                ), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="tuple_of_nulls_describe")
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues("1.0"),
)
def bigtuplewithnulls(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = (
        f"/var/lib/clickhouse/user_files/nested_struct_{table_name}.parquet"
    )

    with Given("I have a Parquet file with the big tuple with nulls datatype"):
        import_file = os.path.join("arrow", "repeated_no_annotation.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="big_tuple_with_nulls_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="big_tuple_with_nulls")
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(read.output.strip(), name="big_tuple_with_nulls")
                ), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(), name="big_tuple_with_nulls_describe"
                    )
                ), error()


@TestFeature
@Name("complex")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
