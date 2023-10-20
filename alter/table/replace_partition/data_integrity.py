from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.tables import (
    create_table_partitioned_by_column,
    insert_into_table_random_uint64,
)


@TestScenario
def keep_data_on_a_source_table(self):
    """Creating two tables and checking that the `REPLACE PARTITION` does not delete the data from the source table."""
    node = self.context.node
    source_table = "source" + getuid()
    destination_table = "destination" + getuid()

    with Given("I have two tables with the same structure"):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        insert_into_table_random_uint64(
            table_name=destination_table, number_of_values=10
        )
        insert_into_table_random_uint64(table_name=source_table, number_of_values=10)

    with Then("I select and store the data from the source table"):
        source_table_data = node.query(f"SELECT * FROM {source_table} ORDER BY i")

    with And("I replace partition for destination table from the source table"):
        node.query(
            f"ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table}"
        )

    with Check("I check that the values on the source table are not deleted"):
        source_table_data_after_replace = node.query(
            f"SELECT * FROM {source_table} ORDER BY i"
        )
        assert (
            source_table_data.output.strip()
            == source_table_data_after_replace.output.strip()
        ), error()


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_KeepData("1.0"))
@Name("data integrity")
def feature(self, node="clickhouse1"):
    """Check the integrity of the data on the source table after replacing partition from it."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=keep_data_on_a_source_table)
