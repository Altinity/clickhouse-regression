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
    """Check importing and exporting a parquet file with lz4 raw compression."""
    with Given("I have a Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed.parquet")

    import_export(snapshot_name="lz4_raw_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def lz4_raw_large(self):
    """Check importing and exporting a large parquet file with lz4 raw compression."""
    with Given("I have a large Parquet file with the lz4_raw compression"):
        import_file = os.path.join("arrow", "lz4_raw_compressed_larger.parquet")

    import_export(snapshot_name="lz4_raw_large_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_hadoop(self):
    """Check importing and exporting a parquet file with hadoop lz4 compression."""
    with Given("I have a Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_hadoop_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Hadoop("1.0"))
def lz4_hadoop_large(self):
    """Check importing and exporting a large parquet file with hadoop lz4 compression."""
    with Given("I have a large Parquet file with the hadoop lz4 compression"):
        import_file = os.path.join("arrow", "hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_hadoop_large_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4_non_hadoop(self):
    """Check importing and exporting a parquet file with lz4 compression."""
    with Given("I have a large Parquet file with the non hadoop lz4 compression"):
        import_file = os.path.join("arrow", "non_hadoop_lz4_compressed.parquet")

    import_export(snapshot_name="lz4_non_hadoop_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Delta("1.0"),
)
def snappyrle(self):
    """Check importing and exporting a parquet file with Snappy compression and RLE and DELTA encodings."""
    with Given("I have a Parquet file with the Snappy compression and RLE encoding"):
        import_file = os.path.join("arrow", "datapage_v2.snappy.parquet")

    import_export(snapshot_name="snappy_rle_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain("1.0"),
)
def snappyplain(self):
    """Check importing and exporting a parquet file with snappy compression end plain encoding."""
    with Given("I have a Parquet file with the Snappy compression and Plain encoding"):
        import_file = os.path.join("arrow", "alltypes_plain.snappy.parquet")

    import_export(snapshot_name="snappyplain_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli("1.0"))
def brotli(self):
    """Check importing and exporting a parquet file with brotli compression."""
    with Given("I have a parquet file with brotli compression"):
        import_file = os.path.join("compression", f"data_page=1_BROTLI.parquet")

    import_export(snapshot_name="brotli_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def gzippages(self):
    """Check importing and exporting a parquet file with gzip compression placed in two different page files."""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with gzip compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_GZIP.parquet"
            )

        import_export(
            snapshot_name=f"gzip_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"))
def lz4pages(self):
    """Check importing and exporting a parquet file with lz4 compression placed in two different page files."""
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
    """Check importing and exporting a parquet file with no compression placed in two different page files."""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with None compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_NONE.parquet"
            )

        import_export(
            snapshot_name=f"none_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"))
def snappypages(self):
    """Check importing and exporting a parquet file with snappy compression placed in two different page files."""
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
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"))
def zstdpages(self):
    """Check importing and exporting a parquet file with zstd compression placed in two different page files."""
    for page_number in range(1, 3):
        with Given(f"I have a parquet page={page_number} file with ZSTD compression"):
            import_file = os.path.join(
                "compression", f"data_page={page_number}_ZSTD.parquet"
            )

        import_export(
            snapshot_name=f"zstd_page_{page_number}_structure", import_file=import_file
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy("1.0"),
)
def arrow_snappy(self):
    """Checking that ClickHouse can import and export Parquet files generated with arrow2 and snappy compression."""
    with Given("I have a Parquet file generated with arrow2 and snappy compression"):
        import_file = os.path.join("arrow", "7-set.snappy.arrow2.parquet")

    import_export(snapshot_name="arrow_snappy_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"))
def largegzip(self):
    """Checking that ClickHouse can import and export very large Parquet files with gzip compression."""
    with Given("I have a large Parquet large Parquet file with gzip compression"):
        import_file = os.path.join("compression", "lineitem-top10000.gzip.parquet")

    import_export(snapshot_name="complex_nested_2_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Zstd("1.0"))
def zstd(self):
    """Checking that ClickHouse can import Parquet files with zstd compression."""
    with Given("I have a large Parquet Parquet file with zstd compression"):
        import_file = os.path.join("compression", "zstd.parquet")

    import_export(snapshot_name="zstd_compression_1_structure", import_file=import_file)


@TestFeature
@Name("compression")
def feature(self, node="clickhouse1"):
    """Check importing and exporting compressed parquet files."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "compression"

    for scenario in loads(current_module(), Scenario):
        scenario()
