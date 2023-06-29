import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *
from parquet.tests.outline import import_export
import time


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


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Query_Cache_Performance("1.0"))
def performance(self):
    """Test that the execution time is less for the second run of the same query when working with the Parquet files."""
    node = self.context.node
    with Given("I have a cache1 Parquet file"):
        import_file = os.path.join("cache", "cache1.parquet")

    with When("I read the data from that file using SELECT"):
        start_time = time.time()
        node.query(f"SELECT * FROM file('{import_file}', Parquet)")
        end_time = time.time()
        first_run = end_time - start_time

    with Then("I read the data from that file the second time using SELECT"):
        start_time = time.time()
        node.query(f"SELECT * FROM file('{import_file}', Parquet)")
        end_time = time.time()

    with And(
        "I check that the time of the execution is lees for the second query run compared to the first run"
    ):
        second_run = end_time - start_time
        assert second_run > first_run, error()


@TestFeature
@Name("cache")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with the query cache functionality."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "cache"

    for scenario in loads(current_module(), Scenario):
        scenario()
