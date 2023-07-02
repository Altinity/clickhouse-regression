import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Dictionary("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Dictionary("1.0"),
)
def dictionary(self):
    """Checking importing and exporting of hte Parquet file with the Dictionary encoding."""
    with Given("I have a Parquet file with the Dictionary encoding"):
        import_file = os.path.join("arrow", "alltypes_dictionary.parquet")

    import_export(snapshot_name="dictionary_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain("1.0"),
)
def plain(self):
    """Checking importing and exporting of hte Parquet file with the Plain encoding."""
    with Given("I have a Parquet file with the Plain encoding"):
        import_file = os.path.join("arrow", "alltypes_plain.parquet")

    import_export(snapshot_name="plain_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaStrings("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaStrings("1.0"),
)
def delta_byte_array(self):
    """Checking importing and exporting of the Parquet file with the Delta Strings: (DELTA_BYTE_ARRAY) encoding."""
    with Given("I have a Parquet file with the Delta Strings encoding"):
        import_file = os.path.join("encodings", "aws2.parquet")

    import_export(snapshot_name="delta_string_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain("1.0"),
)
def plain_rle_snappy(self):
    """Checking importing and exporting of hte Parquet file with the PLAIN and RLE_DICTIONARY encodings and snappy compression."""
    with Given("I have a Parquet file with the Plain and Dictionary encoding"):
        import_file = os.path.join("encodings", "aws1.snappy.parquet")

    import_export(snapshot_name="rle_dict_plain_structure", import_file=import_file)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaStrings("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaStrings("1.0"),
)
def delta_byte_array2(self):
    """Checking importing and exporting of the Parquet file with the Delta Strings: (DELTA_BYTE_ARRAY) encoding."""
    import_file = os.path.join("encodings", "delta_byte_array.parquet")
    pass


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaLengthByteArray("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaLengthByteArray("1.0"),
)
def delta_length_byte_array(self):
    """Checking importing and exporting of the Parquet file with the Delta-length byte array (DELTA_LENGTH_BYTE_ARRAY) encoding."""
    import_file = os.path.join("encodings", "delta_length_byte_array.parquet")
    pass


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_RunLength("1.0"),
)
def rle_boolean(self):
    """Checking importing and exporting of the Parquet file with boolean values and the Run Length Encoding / Bit-Packing Hybrid (RLE)."""
    import_file = os.path.join("encodings", "rle_boolean_encoding.parquet")
    pass


@TestFeature
@Name("encoding")
def feature(self, node="clickhouse1"):
    """Check importing and exporting encoded parquet files."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "encoding"

    for scenario in loads(current_module(), Scenario):
        scenario()
