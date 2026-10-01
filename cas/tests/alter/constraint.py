"""Constraint ALTER TABLE scenarios for CAS MergeTree."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import check_clickhouse_version, getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
def constraint_table(self, suffix):
    """Create and fill an isolated table for one constraint ALTER scenario."""
    table_name = f"cas_alter_constraint_{suffix}_{getuid()}"
    create_filled_alter_table(table_name=table_name)
    return table_name


def insert_row(node, table, value):
    """Insert one extra row with the given value."""
    return node.query(
        f"INSERT INTO {table} (partition_column, id, value, string_column) "
        f"VALUES (3, 0, {value}, 'x')",
        no_checks=True,
    )


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Constraint("1.0"))
def add_and_drop(self):
    """Check that ADD / DROP CONSTRAINT change metadata and INSERT checks."""
    node = self.context.node

    with Given("create a table"):
        table = constraint_table(suffix="add_drop")

    with And("add a CHECK constraint"):
        add_constraint(table_name=table, definition="value_nonneg CHECK value >= 0")

    with And("a violating INSERT is rejected"):
        result = insert_row(node, table, -1)
        assert result.exitcode != 0, error(result.output)
        assert "Exception" in result.output, error(result.output)

    with And("a satisfying INSERT is accepted"):
        result = insert_row(node, table, 1)
        assert result.exitcode == 0, error(result.output)

    with And("the table definition shows the constraint"):
        create_query = show_create_table(node, table)
        assert "CONSTRAINT value_nonneg CHECK value >= 0" in create_query, error(
            create_query
        )

    with And("drop the constraint"):
        drop_constraint(table_name=table, constraint_name="value_nonneg")

    with Then("a previously invalid value can be inserted"):
        result = insert_row(node, table, -1)
        assert result.exitcode == 0, error(result.output)

    with And("the table definition no longer shows the constraint"):
        create_query = show_create_table(node, table)
        assert "CONSTRAINT value_nonneg" not in create_query, error(create_query)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Constraint("1.0"))
def modify(self):
    """Check that MODIFY CONSTRAINT replaces an existing constraint declaration."""
    if check_clickhouse_version("<26.7")(self):
        skip(reason="MODIFY CONSTRAINT was added to the parser in ClickHouse 26.7")

    node = self.context.node

    with Given("create a table"):
        table = constraint_table(suffix="modify")

    with And("create table with a CHECK constraint"):
        add_constraint(table_name=table, definition="value_nonneg CHECK value >= 0")

    with When("modify the constraint to a stricter expression"):
        modify_constraint(table_name=table, definition="value_nonneg CHECK value >= 1")

    with Then("the new expression is enforced"):
        result = insert_row(node, table, 0)
        assert result.exitcode != 0, error(result.output)
        assert "Exception" in result.output, error(result.output)

    with And("a value that satisfies the new expression is accepted"):
        result = insert_row(node, table, 1)
        assert result.exitcode == 0, error(result.output)

    with And("the table definition shows the new expression"):
        create_query = show_create_table(node, table)
        assert "CONSTRAINT value_nonneg CHECK value >= 1" in create_query, error(
            create_query
        )


@TestFeature
@Name("constraint")
def feature(self):
    """Constraint ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
