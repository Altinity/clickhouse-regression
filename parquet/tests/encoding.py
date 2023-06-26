import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export

snapshot_id = "encoding"

@TestScenario
@XFailed("Issue with datetime. Different number of on import and export")
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Dictionary("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Dictionary("1.0"),
)
def dictionary(self):
    with Given("I have a Parquet file with the Dictionary encoding"):
        import_file = os.path.join("arrow", "alltypes_dictionary.parquet")

    import_export(snapshot_name="dictionary_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestScenario
@XFailed("Issue with datetime. Different number of on import and export")
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain("1.0"),
)
def plain(self):
    with Given("I have a Parquet file with the Plain encoding"):
        import_file = os.path.join("arrow", "alltypes_plain.parquet")

    import_export(snapshot_name="plain_structure", import_file=import_file, snapshot_id=snapshot_id)


@TestFeature
@Name("encoding")
def feature(self, node="clickhouse1"):
    """Check importing and exporting encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
