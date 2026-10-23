"""Heavyweight ALTER mutation scenarios for CAS-backed MergeTree tables."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
def mutation_table(self, suffix):
    """Create and fill an isolated table for one mutation scenario."""
    table_name = f"cas_alter_mutation_{suffix}_{getuid()}"
    create_cas_merge_tree_table(
        table_name=table_name,
        columns=ALTER_COLUMNS,
        partition_by="partition_column",
        order_by="(partition_column, id)",
    )
    insert_alter_rows(table_name=table_name)
    return table_name


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter("1.0"),
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_Update("1.0"),
)
def update(self):
    """ALTER UPDATE rewrites matching values across the table."""
    with Given("create a table"):
        table = mutation_table(suffix="update")

    with When("update matching rows"):
        alter_update(
            table_name=table, assignments="value = value + 100", condition="id < 2"
        )

    with Then("the mutation is complete and values are correct"):
        result = self.context.node.query(
            f"SELECT count(), sum(value) FROM {table}"
        ).output.strip()
        assert result == "10\t420", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_Update("1.0"),
    RQ_SRS_048_CAS_Partition_Update("1.0"),
)
def update_in_partition(self):
    """ALTER UPDATE IN PARTITION rewrites only the selected partition."""
    with Given("create a table"):
        table = mutation_table(suffix="update_partition")

    with And("assert values before update"):
        result = self.context.node.query(
            f"SELECT partition_column, sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t10\n2\t10", error(result)

    with When("update every value in partition 1"):
        alter_update(
            table_name=table,
            assignments="value = value + 10",
            condition="1",
            partition=1,
        )

    with Then("the other partition is unchanged"):
        result = self.context.node.query(
            f"SELECT partition_column, sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t60\n2\t10", error(result)

    with When("I update partition 2 by partition id"):
        alter_update(
            table_name=table,
            assignments="value = value + 1",
            condition="1",
            partition_id="2",
        )

    with Then("only partition 2 changes"):
        result = self.context.node.query(
            f"SELECT partition_column, sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t60\n2\t15", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_Delete("1.0"),
)
def delete(self):
    """ALTER DELETE removes matching rows across the table."""
    with Given("create a table"):
        table = mutation_table(suffix="delete")

    with When("delete rows matching an id"):
        alter_delete(table_name=table, condition="id = 0")

    with Then("the mutation is complete and only matching rows are gone"):
        result = self.context.node.query(
            f"SELECT count(), sum(value) FROM {table}"
        ).output.strip()
        assert result == "8\t20", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_Delete("1.0"),
    RQ_SRS_048_CAS_Partition_Delete("1.0"),
)
def delete_in_partition(self):
    """ALTER DELETE IN PARTITION removes rows only from that partition."""
    with Given("create a table"):
        table = mutation_table(suffix="delete_partition")

    with When("delete two rows from partition 1"):
        alter_delete(table_name=table, condition="id < 2", partition=1)

    with Then("the other partition remains intact"):
        result = self.context.node.query(
            f"SELECT partition_column, count(), sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t3\t9\n2\t5\t10", error(result)

    with When("I delete one row from partition 2 by partition id"):
        alter_delete(table_name=table, condition="id = 0", partition_id="2")

    with Then("partition 1 is unchanged and partition 2 lost that row"):
        result = self.context.node.query(
            f"SELECT partition_column, count(), sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == "1\t3\t9\n2\t4\t10", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Mutations("1.0"),
    RQ_SRS_048_CAS_Partition_RewriteParts("1.0"),
)
def rewrite_parts(self):
    """REWRITE PARTS and REWRITE PARTS IN PARTITION keep the rows."""
    node = self.context.node

    with Given("create a table"):
        table = mutation_table(suffix="rewrite")

    with And("capture the rows"):
        before = node.query(
            f"SELECT partition_column, count(), sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert before == "1\t5\t10\n2\t5\t10", error(before)

    with When("I rewrite every part"):
        node.query(
            f"ALTER TABLE {table} REWRITE PARTS",
            settings=[("mutations_sync", 2)],
        )

    with Then("the rows are unchanged"):
        result = node.query(
            f"SELECT partition_column, count(), sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == before, error(result)

    with When("I rewrite partition 1"):
        node.query(
            f"ALTER TABLE {table} REWRITE PARTS IN PARTITION 1",
            settings=[("mutations_sync", 2)],
        )

    with Then("both partitions still match"):
        result = node.query(
            f"SELECT partition_column, count(), sum(value) FROM {table} "
            f"GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == before, error(result)


@TestFeature
@Name("mutations")
def feature(self):
    """Heavyweight ALTER mutations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
