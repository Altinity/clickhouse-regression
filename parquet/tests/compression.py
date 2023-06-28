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
    """Check importing and exporting a parquet file with lz4 raw compression"""
    with Given("I have a Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed.parquet")

    import_export(snapshot_name="lz4_raw_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4_raw_large(self):
    """Check importing and exporting a large parquet file with lz4 raw compression"""
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
    """Check importing and exporting a parquet file with lz4 compression"""
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
    """Check importing and exporting a parquet file with snappy compression and rle encoding"""
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
    """Check importing and exporting a parquet file with snappy compression end plain encoding"""
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


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli("1.0"))
def brotli(self):
    """Check importing and exporting a parquet file with brotli compression"""
    with Given("I have a parquet file with brotli compression"):
        import_file = os.path.join("compression", f"data_page=1_BROTLI.parquet")

    import_export(snapshot_name="lz4_non_hadoop_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def gzip_pages(self):
    """Check importing and exporting a parquet file with gzip compression"""
    for page_number in range(1, 3):
        with Given(
            f"I have a parquet page={page_number} file with gzip page1 compression"
        ):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_GZIP.parquet"
            )

        import_export(
            snapshot_name=f"gzip_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4pages(self):
    """Check importing and exporting a parquet file with lz4 compression"""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with lz4 compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_LZ4.parquet"
            )

        import_export(
            snapshot_name=f"lz4_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"))
def nonepages(self):
    """Check importing and exporting a parquet file with no compression"""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with None compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_NONE.parquet"
            )

        import_export(
            snapshot_name=f"none_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy("1.0"))
def snappypages(self):
    """Check importing and exporting a parquet file with snappy compression"""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with Snappy compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_SNAPPY.parquet"
            )

        import_export(
            snapshot_name=f"snappy_page_{page_number}_structure",
            import_file=import_file,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy("1.0"))
def zstdpages(self):
    """Check importing and exporting a parquet file with snappy compression"""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with ZSTD compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_ZSTD.parquet"
            )

        import_export(
            snapshot_name=f"zstd_page_{page_number}_structure", import_file=import_file
        )


@TestFeature
@Name("compression")
def feature(self, node="clickhouse1"):
    """Check importing and exporting compressed parquet files."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "compression"

    for scenario in loads(current_module(), Scenario):
        scenario()
