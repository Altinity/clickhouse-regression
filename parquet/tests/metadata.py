import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def cache1(self):
    with Given("I have a cache1 Parquet file"):
        import_file = os.path.join("cache", "cache1.parquet")

    import_export(snapshot_name="cache1_structure", import_file=import_file)

@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw("1.0"))
def cache2(self):
    with Given("I have a cache1 Parquet file"):
        import_file = os.path.join("cache", "cache1.parquet")

    import_export(snapshot_name="cache1_structure", import_file=import_file)


@TestFeature
@Name("metadata")
def feature(self, node="clickhouse1"):
    """Check importing and exporting compressed parquet files."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "metadata"

    for scenario in loads(current_module(), Scenario):
        scenario()
