from testflows.asserts import *
from testflows.core import *

from alter.table.replace_partition.common import create_partitions_with_random_uint64
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid
from helpers.tables import create_table_partitioned_by_column


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromTemporaryTable("1.0"),
)
def from_temporary_to_regular(self):
    """Check that it is possible to replace partition from the temporary table into a regular MergeTree table."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "temporary_source_" + getuid()

    with Given(
        "I have a destination table partitioned by a column and filled with random data"
    ):
        create_table_partitioned_by_column(table_name=destination_table)
        create_partitions_with_random_uint64(table_name=destination_table)

    with And("I open a single clickhouse instance"):
        with node.client() as client:
            with When(
                "I create a temporary table with the same structure as the destination table"
            ):
                client.query(
                    f"CREATE TEMPORARY TABLE {source_table} (p UInt16,i UInt64,extra UInt8) ENGINE = MergeTree "
                    f"PARTITION BY p ORDER BY tuple();"
                )

            with And(
                "I populate the temporary table with the data to create multiple partitions"
            ):
                client.query(
                    f"INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,"
                    f"7,8,9,10]) AS number FROM numbers(3));"
                )
            with And(
                "I replace the partition on the destination table from the temporary source table"
            ):
                client.query(
                    f"ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};"
                )

            with Then(
                "I check that the data on the destination table's partition was replaced with the data from the "
                "temporary table"
            ):
                client.query(f"SELECT * FROM '{source_table}' WHERE p = 1 ORDER BY i")
                source_data = client.result
                client.query(
                    f"SELECT * FROM '{destination_table}' WHERE p = 1 ORDER BY i"
                )
                destination_data = client.result
                assert destination_data.strip() == source_data.strip(), error()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_ToTemporaryTable("1.0")
)
def from_temporary_to_temporary_table(self):
    """Check that it is not possible to replace partition from the temporary table into another temporary table."""
    node = self.context.node
    destination_table = "temporary_destination_" + getuid()
    source_table = "temporary_source_" + getuid()

    with Given("I open a single clickhouse instance"):
        with node.client() as client:
            with And("I create two temporary tables with the same structure"):
                client.query(
                    f"CREATE TEMPORARY TABLE {destination_table} (p UInt16,i UInt64,extra UInt8) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();"
                )
                client.query(
                    f"CREATE TEMPORARY TABLE {source_table} (p UInt16,i UInt64,extra UInt8) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();"
                )

            with When("I populate them with data that creates multiple partitions"):
                client.query(
                    f"INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3));"
                )
                client.query(
                    f"INSERT INTO {destination_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3));"
                )

            with Then(
                "I check if it is possible to replace partition on the temporary destination table from the temporary source table"
            ):
                client.query(
                    f"ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};",
                    exitcode=60,
                )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_FromRegularTable("1.0")
)
def from_regular_to_temporary(self):
    """Check that it is not possible to replace partition from the regular table into temporary table."""
    node = self.context.node
    destination_table = "temporary_destination_" + getuid()
    source_table = "source_" + getuid()

    with Given("I open a single clickhouse instance"):
        with node.client() as client:
            with And(
                "I create one temporary table and one regular table with the same structure"
            ):
                client.query(
                    f"CREATE TEMPORARY TABLE {destination_table} (p UInt16,i UInt64,extra UInt8) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();"
                )
                client.query(
                    f"CREATE TABLE {source_table} (p UInt8,i UInt64) ENGINE = MergeTree PARTITION BY p ORDER BY tuple();"
                )

            with When("I populate them with the data to create multiple partitions"):
                client.query(
                    f"INSERT INTO {source_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3));"
                )
                client.query(
                    f"INSERT INTO {destination_table} (p, i) SELECT number, rand64() FROM (SELECT arrayJoin([1,2,3,4,5,6,7,8,9,10]) AS number FROM numbers(3));"
                )

            with Then(
                "I check if it is possible to replace partition on the regular table from the temporary table"
            ):
                client.query(
                    f"ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table};",
                    exitcode=60,
                )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_TemporaryTable("1.0"))
@Name("temporary table")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use temporary tables to replace partitions on the destination table."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=from_temporary_to_regular)
    Scenario(run=from_temporary_to_temporary_table)
    Scenario(run=from_regular_to_temporary)
