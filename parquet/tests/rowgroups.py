import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize("1.0"))
def many_row_groups(self):
    """Checking that ClickHouse can import and export parquet files that are  written such that every row has its own row group."""
    import_file = os.path.join("manyrowgroups.parquet")
    xfail(reason="Test not added yet")


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize("1.0"))
def many_row_groups2(self):
    """Checking that ClickHouse can import and export parquet files that are  written such that every row has its own row group."""
    import_file = os.path.join("manyrowgroups2.parquet")
    xfail(reason="Test not added yet")


@TestFeature
@Name("rowgroups")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with the query cache functionality."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "rowgroups"

    for scenario in loads(current_module(), Scenario):
        scenario()
