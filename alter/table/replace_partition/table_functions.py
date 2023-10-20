from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.tables import (
    create_table_partitioned_by_column,
    insert_into_table_random_uint64,
)


@TestScenario
def table_functions(self):
    """Checking that the usage of table functions with replace partition outputs an expected error and does not crash the ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I have two tables with the same structure"):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        insert_into_table_random_uint64(
            table_name=destination_table, number_of_values=10
        )
        insert_into_table_random_uint64(table_name=source_table, number_of_values=10)

    with Check("I check that the usage of table functions outputs an expected error"):
        node.query(
            f"ALTER TABLE {destination_table} REPLACE PARTITION 2 FROM {source_table} file('file.parquet')",
            exitcode=62,
            message="DB::Exception: Syntax error",
        )


@TestFeature
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions("1.0")
)
@Name("table functions")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse doesn't crash when using table functions with replace partition clause."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=table_functions)
