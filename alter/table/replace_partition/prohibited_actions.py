from testflows.core import *
from testflows.asserts import *
from helpers.common import getuid, replace_partition
from helpers.tables import create_table_partitioned_by_column, create_table
from alter.table.replace_partition.requirements.requirements import *
from alter.table.replace_partition.common import (
    create_two_tables_partitioned_by_column_with_data,
    create_merge_tree_and_memory_tables,
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
    """Checking that the usage of table functions after from clause outputs an expected error and does not crash the
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
    """Checking that the usage of JOIN does output an expected error and does not crash the ClickHouse."""
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
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited_Join("1.0"))
def subquery(self):
    """Checking that the usage of subquery does output an expected error and does not crash the ClickHouse."""
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
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited("1.0"))
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
        "That it is not possible to replace a partition on a mergetree table from a memory table"
    ):
        replace_partition(
            destination_table=destination_table,
            source_table=source_table,
            partition=2,
            message=message,
            exitcode=exitcode,
        )

    with But("Check that partition was not replaced on the destination table"):
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


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_Prohibited("1.0"))
@Name("prohibited actions")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse doesn't crash amd outputs an error when doing prohibited actions with replace
    partition."""
    self.context.node = self.context.cluster.node(node)

    Feature(run=from_clause)
    Scenario(run=order_by_partition_by)
