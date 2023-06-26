import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4_raw(self):
    with Given("I have a Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed.parquet")

    import_export(snapshot_name="lz4_raw_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4_raw_large(self):
    with Given("I have a large Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed_larger.parquet")

    import_export(snapshot_name="lz4_raw_large_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_hadoop(self):
    with Given("I have a Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_hadoop_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_hadoop_large(self):
    with Given("I have a large Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_hadoop_large_structure", import_file=import_file)


def lz4_non_hadoop(self):
    with Given("I have a large Parquet file with the non hadoop lz4 compression"):
        import_file = os.path.join("arrow", "non_hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_non_hadoop_structure", import_file=import_file)


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
    """Check importing and exporting compressed parquet files."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "compression"

    for scenario in loads(current_module(), Scenario):
        scenario()
