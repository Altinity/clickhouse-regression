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
        with When("I try to import the binary Parquet file into the table"):
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
            export_columns_structure = node.query(
                f"DESCRIBE TABLE file('{path_to_export}')"
            )
            assert (
                import_column_structure.output.strip()
                == export_columns_structure.output.strip()
            ), error()


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
    path_to_export = f"/var/lib/clickhouse/user_files/uuid_{table_name}.parquet"

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


@TestFeature
@Name("datatypes")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
