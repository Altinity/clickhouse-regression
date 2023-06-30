import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax("1.0"))
def bigtuplewithnulls(self):
    """Checking importing and exporting a parquet file with Min/Max values where offset between Min and Max is zero."""
    with Given("I have a Parquet file with the zero offset between min and max"):
        import_file = os.path.join("arrow", "dict-page-offset-zero.parquet")

    import_export(
        snapshot_name="min_max_zero_offset_structure", import_file=import_file
    )


@TestFeature
@Name("indexing")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with indexing."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "indexing"

    for scenario in loads(current_module(), Scenario):
        scenario()
