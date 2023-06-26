import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4_raw(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = (
        f"/var/lib/clickhouse/user_files/lz4_raw_compressed_export_{table_name}.parquet"
    )

    with Given("I have a Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed.parquet")
        node.command(f"rm -r {path_to_export}")

    with Check("import"):
        with When("I try to import the lz4_raw compressed Parquet file into the table"):
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
                    snapshot(
                        read.output.strip(),
                        name=f"dictionary_encoded_parquet_examples2",
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
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"dictionary_encoded_parquet_examples2",
                    )
                ), error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4rawlarge(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/lz4_raw_large_compressed_export_{table_name}.parquet"

    with Given("I have a large Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed_larger.parquet")

    with Check("import"):
        with When("I try to import the lz4_raw compressed Parquet file into the table"):
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
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_raw_large",
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
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_raw_large",
                    )
                ), error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_hadoop(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/lz4_hadoop_compressed_export_{table_name}.parquet"

    with Given("I have a Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    with Check("import"):
        with When(
            "I try to import the hadoop lz4 compressed Parquet file into the table"
        ):
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
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_hadoop",
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
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_hadoop",
                    )
                ), error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_hadoop_large(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/lz4_hadoop_compressed_large_export_{table_name}.parquet"

    with Given("I have a large Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    with Check("import"):
        with When(
            "I try to import the large hadoop lz4 compressed Parquet file into the table"
        ):
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
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_hadoop_large",
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
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_hadoop_large",
                    )
                ), error()


def lz4_non_hadoop(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/lz4_non_hadoop_compressed_export_{table_name}.parquet"

    with Given("I have a large Parquet file with the non hadoop lz4 compression"):
        import_file = os.path.join("arrow", "non_hadoop_lz4_compressed.parquet")

    with Check("import"):
        with When(
            "I try to import the large non hadoop lz4 compressed Parquet file into the table"
        ):
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
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_non_hadoop_large",
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
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"lz4_non_hadoop_large",
                    )
                ), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength("1.0"),
)
def snappy_rle(self):
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with the snappy compression"):
        import_file = os.path.join("arrow", "datapage_v2.snappy.parquet")

    with Check("import"):
        with When("I try to import the snappy compressed Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """,
                message="DB::ParsingException: Error while reading Parquet data: IOError: Unknown encoding type.",
                exitcode=33,
            )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength("1.0"),
)
def snappy_plain(self):
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a Parquet file with the snappy compression"):
        import_file = os.path.join("arrow", "alltypes_plain.snappy.parquet")

    with Check("import", flags=XFAIL):
        with When("I try to import the snappy compressed Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """,
                message="DB::ParsingException: Error while reading Parquet data: IOError: Unknown encoding type.",
                exitcode=33,
            )


@TestFeature
@Name("compression")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
