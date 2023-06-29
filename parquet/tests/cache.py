import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Query_Cache("1.0"))
def cache1(self):
    """Checking that reading the cache.parquet files does not result in any kind of errors."""
    with Given("I have a cache1 Parquet file"):
        import_file = os.path.join("cache", "cache1.parquet")

    import_export(snapshot_name="cache1_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Query_Cache("1.0"))
def cache2(self):
    """Checking that reading the cache.parquet files does not result in any kind of errors."""
    with Given("I have a cache1 Parquet file"):
        import_file = os.path.join("cache", "cache1.parquet")

    import_export(snapshot_name="cache1_structure", import_file=import_file)


@TestFeature
@Name("cache")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with the query cache functionality."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "cache"

    for scenario in loads(current_module(), Scenario):
        scenario()
