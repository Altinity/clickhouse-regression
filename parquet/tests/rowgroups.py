import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize("1.0"))
def manyrowgroups(self):
    """Checking that ClickHouse can import and export parquet files that are  written such that every row has its own row group."""
    with Given("I have a large Parquet file in which every row has its own row group"):
        import_file = os.path.join("datatypes", "manyrowgroups.parquet")

    import_export(snapshot_name="many_row_groups_structure", import_file=import_file)


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize("1.0"))
def manyrowgroups2(self):
    """Checking that ClickHouse can import and export parquet files that are  written such that every row has its own row group."""
    with Given("I have a large Parquet file in which every row has its own row group"):
        import_file = os.path.join("datatypes", "manyrowgroups2.parquet")

    import_export(snapshot_name="many_row_groups_2_structure", import_file=import_file)


@TestFeature
@Name("rowgroups")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with the query cache functionality."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "rowgroups"

    for scenario in loads(current_module(), Scenario):
        scenario()
