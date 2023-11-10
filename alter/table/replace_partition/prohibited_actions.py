from testflows.core import *
from testflows.asserts import *
from helpers.common import getuid, replace_partition
from helpers.datatypes import UInt64, UInt8
from helpers.tables import create_table_partitioned_by_column, Column
from alter.table.replace_partition.requirements.requirements import *
from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
    create_merge_tree_and_memory_tables,
    create_table_partitioned_by_column_with_data,
)


def io_error_message(exitcode=62, message="Syntax error"):
    return (
        exitcode,
        f"DB::Exception: {message}",
    )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_TableFunctions("1.0")
)
def table_functions(self):
    """Checking that the usage of table functions after FROM clause on replace partition outputs an expected error and does not crash the
    ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    exitcode, message = io_error_message()

    with Given("I have two tables with the same structure filled with random data"):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check(
        "I check that the usage of table function after from clause outputs an expected error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table="file('file.parquet')",
            partition=2,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Join("1.0"))
def join(self):
    """Checking that the usage of JOIN after FROM clause on replace partition does output an expected error and does not crash the ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    exitcode, message = io_error_message()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check(
        "I check that the usage of join after from clause outputs an expected error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table="JOIN table_2 ON table_1.p",
            partition=2,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Subquery("1.0")
)
def subquery(self):
    """Checking that the usage of subquery after FROM clause on replace partition does output an expected error and does not crash the ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    exitcode, message = io_error_message()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check(
        "I check that the usage of subquery after from clause outputs an expected error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table="(SELECT 1)",
            partition=2,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_OrderAndPartition(
        "1.0"
    )
)
def order_by_partition_by(self):
    """Checking that the usage of order by and partition by does output an expected error and does not crash the ClickHouse."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    exitcode, message = io_error_message()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check(
        "I check that the usage of subquery after from clause outputs an expected error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table="ORDER BY p PARTITION BY p",
            partition=2,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_IncorrectTableEngines(
        "1.0"
    )
)
def non_mergetree_table(self):
    """Checking that it is not possible to replace partition on a destination table from a table that is not a MergeTree table."""
    node = self.context.node
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()
    exitcode, message = io_error_message(
        exitcode=48, message="Cannot replace partition from table"
    )

    with Given(
        "I create a destination table with a MergeTree engine partitioned by a column and a memory table that has no partitions"
    ):
        create_merge_tree_and_memory_tables(
            merge_tree_table=destination_table, memory_table=source_table
        )

    with Check(
        "that it is not possible to replace a partition on a MergeTree table from a Memory table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=2,
            message=message,
            exitcode=exitcode,
        )

    with But("check that partition was not replaced on the destination table"):
        destination_data = node.query(
            f"SELECT * FROM {destination_table} WHERE p = 2 ORDER BY p"
        )
        source_data = node.query(f"SELECT * FROM {source_table} WHERE p = 2 ORDER BY p")

        assert destination_data.output.strip() != source_data.output.strip()


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_View_Normal("1.0")
)
def view(self):
    node = self.context.node
    destination_table = "destination_" + getuid()
    view_name = "view_" + getuid()
    exitcode, message = io_error_message(
        exitcode=48, message="Cannot replace partition from table"
    )

    with Given("I have a MergeTree table partitioned by a column"):
        create_table_partitioned_by_column(table_name=destination_table)

    with When("I create a normal view"):
        node.query(f"CREATE VIEW {view_name} AS SELECT 1;")

    with Check(
        "I check that replacing partition on the destination table from the normal view outputs an error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=view_name,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_View_Materialized(
        "1.0"
    )
)
def materialized_view(self):
    node = self.context.node
    destination_table = "destination_" + getuid()
    view_name = "view_" + getuid()
    exitcode, message = io_error_message(
        exitcode=48, message="Cannot replace partition from table"
    )

    with Given("I have a MergeTree table partitioned by a column"):
        create_table_partitioned_by_column(table_name=destination_table)

    with When("I create a materialized view of the destination table"):
        node.query(
            f"CREATE MATERIALIZED VIEW {view_name} TO {destination_table} AS SELECT * FROM {destination_table};"
        )

    with Check(
        "I check that replacing partition on the destination table from the normal view outputs an error"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=view_name,
            message=message,
            exitcode=exitcode,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_StoragePolicy(
        "1.0"
    )
)
def storage_policy(self):
    """Check that it is not possible to replace partition on the destination table when the destination table and
    source table have different storage policies."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    exitcode, message = io_error_message(
        exitcode=36, message="Could not clone and load part"
    )

    with Given("I have a partitioned destination table with a policy1"):
        create_table_partitioned_by_column_with_data(
            table_name=destination_table, query_settings="storage_policy = 'policy1'"
        )

    with And("I have a partitioned source table with a different policy"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, query_settings="storage_policy = 'policy2'"
        )

    with Then(
        "I try to replace partition on the destination table with a different policy from the source table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestStep
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key("1.0")
)
def partition_by(self):
    """Check that it is not possible to replace partition on the destination table when destination table and source
    table have different partition by key."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    exitcode, message = io_error_message(
        exitcode=36, message="Tables have different partition key"
    )

    with Given("I have a partitioned destination table"):
        create_table_partitioned_by_column_with_data(table_name=destination_table)

    with And("I have a partitioned source table with a different partition key"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, partition_by="i"
        )

    with Then(
        "I try to replace partition on the destination table with a different partition key from the source table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestStep
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Key("1.0")
)
def order_by(self):
    """Check that it is not possible to replace partition on the destination table when destination table and source
    table have different order by key."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    exitcode, message = io_error_message(
        exitcode=36, message="Tables have different ordering"
    )

    with Given("I have a partitioned destination table"):
        create_table_partitioned_by_column_with_data(table_name=destination_table)

    with And("I have a partitioned source table with a different order key"):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, order_by="i"
        )

    with Then(
        "I try to replace partition on the destination table with a different order key from the source table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions_Different_Structure(
        "1.0"
    )
)
def structure(self):
    """Check that it is not possible to replace partition on the destination table when the destination and source
    table have different structure."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    exitcode, message = io_error_message(
        exitcode=122, message="Tables have different structure"
    )

    columns = [
        Column(name="p", datatype=UInt8()),
        Column(name="i", datatype=UInt64()),
        Column(name="extra_column", datatype=UInt64()),
    ]

    with Given("I have a partitioned destination table"):
        create_table_partitioned_by_column_with_data(table_name=destination_table)

    with And(
        "I have a partitioned source table with a different structure",
        description="this table has an extra column compared to the destination table",
    ):
        create_table_partitioned_by_column_with_data(
            table_name=source_table, columns=columns
        )

    with Then(
        "I try to replace partition on the destination table with a different structure from the source table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_IntoOutfile("1.0"))
def into_outfile(self):
    """Checking that the usage of INTO OUTFILE does output any errors and does not crash the ClickHouse."""
    destination_table = "destination_" + getuid()
    source_table = "source_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check("I check tha the INTO OUTFILE clause does not output any errors"):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            additional_parameters="INTO OUTFILE 'test.file'",
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Format("1.0"))
def format(self):
    """Checking that the usage of FORMAT does output any errors and does not crash the ClickHouse."""
    destination_table = "table_" + getuid()
    source_table = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check("I check tha the FORMAT clause does not output any errors"):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            additional_parameters="FORMAT CSV",
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Settings("1.0"))
def settings(self):
    """Checking that the usage of SETTINGS does not output any errors and does not crash the ClickHouse."""
    destination_table = "table_" + getuid()
    source_table = "table_" + getuid()

    with Given(
        "I have two tables with a MergeTree engine, with the same structure partitioned by the same column"
    ):
        create_two_tables_partitioned_by_column_with_data(
            destination_table=destination_table, source_table=source_table
        )

    with Check("I check tha the SETTINGS clause does not output any errors"):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            additional_parameters="SETTINGS async_insert = 1",
        )


@TestSuite
def from_clause(self):
    """Check that the ClickHouse outputs an error and does not replace partition when prohibited actions are being
    used with from clause."""
    Scenario(run=table_functions)
    Scenario(run=join)
    Scenario(run=subquery)
    Scenario(run=non_mergetree_table)
    Scenario(run=view)
    Scenario(run=materialized_view)


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Conditions("1.0"))
def conditions(self):
    """Check that it is not possible to replace the partition from the source table to the destination table when these two tables have
    different:
    * Storage Policy
    * Structure
    * Partition key
    * Order By key
    """

    Scenario(run=storage_policy)
    Scenario(run=partition_by)
    Scenario(run=order_by)
    Scenario(run=structure)


@TestSuite
def miscellaneous(self):
    """Check replace partition with some miscellaneous actions."""
    Scenario(run=order_by_partition_by)
    Scenario(run=into_outfile)
    Scenario(run=format)
    Scenario(run=settings)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited("1.0"))
@Name("prohibited actions")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse doesn't crash and outputs an error when doing prohibited actions with replace
    partition."""
    self.context.node = self.context.cluster.node(node)

    Feature(run=from_clause)
    Feature(run=conditions)
    Feature(run=miscellaneous)
