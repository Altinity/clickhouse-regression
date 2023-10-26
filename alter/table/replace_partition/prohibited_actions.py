from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
)


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions("1.0")
)
def table_functions(self):
    """Checking that the usage of table functions after from clause outputs an expected error and does not crash the
    ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I have two tables with the same structure filled with random data"):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check("I check that the usage of table functions outputs an expected error"):
        node.query(
            f"ALTER TABLE {destination_table} REPLACE PARTITION 2 FROM {source_table} file('file.parquet')",
            exitcode=62,
            message="DB::Exception: Syntax error",
        )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited("1.0"))
@Name("prohibited actions")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse doesn't crash when using table functions with replace partition clause."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=table_functions)
