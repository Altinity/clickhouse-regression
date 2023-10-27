from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, replace_partition
from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable("1.0"),
)
def from_temporary_to_regular(self):
    """Check that it is possible to replace partition from the temporary table into a regular MergeTree table."""
    fail()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ToTemporaryTable("1.0")
)
def from_temporary_to_temporary_table(self):
    """Check that it is possible to replace partition from the temporary table into another temporary table."""
    fail()


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTable("1.0"))
@Name("temporary table")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use temporary tables to replace partitions."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=from_temporary_to_regular)
    Scenario(run=from_temporary_to_temporary_table)
