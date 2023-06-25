import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0")
)
def binary(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/binary_{table_name}.Parquet"

    with Given("I have a Parquet file with the binary datatype columns"):
        dict_encoded_file = os.path.join("arrow", "binary.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"describe_binary",
                )
            ), error()

    with Check("import"):
        with When("I try to import the binary Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"binary",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"binary",
                    )
                ), error()

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def byte_array(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/binary_{table_name}.Parquet"

    with Given("I have a Parquet file with the decimal byte array datatype columns"):
        dict_encoded_file = os.path.join("arrow", "byte_array_decimal.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"byte_array_describe",
                )
            ), error()


    with Check("import"):
        with When("I try to import the decimal byte array Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"byte_array_decimal",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"byte_array_decimal",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"byte_array_describe",
                    )
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def fixed_length_decimal(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/fixed_decimal_{table_name}.Parquet"

    with Given("I have a Parquet file with the fixed length decimal datatype columns"):
        dict_encoded_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"fixed_length_decimal_describe",
                )
            ), error()


    with Check("import"):
        with When("I try to import the fixed length decimal Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"fixed_length_decimal",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"fixed_length_decimal",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"fixed_length_decimal_describe",
                    )
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def fixed_length_decimal_legacy(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/fixed_decimal_legacy_{table_name}.Parquet"

    with Given("I have a Parquet file with the fixed length decimal legacy datatype columns"):
        dict_encoded_file = os.path.join("arrow", "fixed_length_decimal.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"fixed_length_legacy_decimal_describe",
                )
            ), error()


    with Check("import"):
        with When("I try to import the fixed length decimal legacy Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"fixed_length_decimal_legacy",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"fixed_length_decimal_legacy",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"fixed_length_legacy_decimal_describe",
                    )
                ), error()

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def int32_decimal(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/int32_decimal_{table_name}.Parquet"

    with Given("I have a Parquet file with the int32 decimal datatype columns"):
        dict_encoded_file = os.path.join("arrow", "int32_decimal.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"int32_decimal_describe",
                )
            ), error()

    with Check("import"):
        with When("I try to import the int32 decimal Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"int32_decimal",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"int32_decimal",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"int32_decimal_describe",
                    )
                ), error()

@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def int64_decimal(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/int64_decimal_{table_name}.Parquet"

    with Given("I have a Parquet file with the int64 decimal datatype columns"):
        dict_encoded_file = os.path.join("arrow", "int64_decimal.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"int64_decimal_describe",
                )
            ), error()

    with Check("import"):
        with When("I try to import the in32 decimal Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"int64_decimal",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"int64_decimal",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"int64_decimal_describe",
                    )
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Conversion("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import("1.0")
)
def decimal(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/decimal_filter_{table_name}.Parquet"

    with Given("I have a Parquet file with the decimal value with specified filters of precision and scale"):
        dict_encoded_file = os.path.join("arrow", "lineitem-arrow.parquet")

    with And("I save file structure"):
        structure = node.query(
            f"DESCRIBE TABLE file('{dict_encoded_file}')"
        )

        with values() as that:
            assert that(
                snapshot(
                    structure.output.strip(),
                    name=f"decimal_filter_describe",
                )
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"decimal_filter",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"decimal_filter",
                    )
                ), error()

        with And("I save file structure after export"):
            structure = node.query(
                f"DESCRIBE TABLE file('{dict_encoded_file}')"
            )

            with values() as that:
                assert that(
                    snapshot(
                        structure.output.strip(),
                        name=f"decimal_filter_describe",
                    )
                ), error()
@TestFeature
@Name("datatypes")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()