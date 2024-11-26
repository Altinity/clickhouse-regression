from testflows.core import *
from parquet.requirements import *
from parquet.tests.outline import import_export
from parquet.tests.steps.general import *
from helpers.common import *


@TestStep(Given)
def create_table_with_500_columns(self, table_name, node=None):
    """Create a table with 500 columns."""

    if node is None:
        node = self.context.node

    q = f"CREATE TABLE {table_name} ("

    for i in range(500 + 1):
        q += f"c{i} Int64"
        q += ","

    for i in range(500 + 1):
        q += f"b{i} Int64"

        if i == 500:
            q += ")"
        else:
            q += ","

    q += " ENGINE = MergeTree ORDER BY tuple();"

    node.query(q)


@TestStep(When)
def insert_values_to_all_columns(self, table_name, node=None):
    """Insert values into all the columns."""
    if node is None:
        node = self.context.node

    with By("inserting an integer value into all of the columns"):
        node.query(f"INSERT INTO {table_name}(c1) values(1);")


@TestScenario
def check_error_with_500_columns(self, node=None):
    """Check the error message when creating a table with 500 columns."""
    table_name = "table_" + getuid()

    if node is None:
        node = self.context.node

    with Given("I crete a table with 500 columns"):
        create_table_with_500_columns(table_name=table_name)

    with When("I insert values into all of the columns"):
        insert_values_to_all_columns(table_name=table_name)

    with Then("I check the error message"):
        node.query(f"SELECT c1 FROM {table_name} ORDER BY tuple(*)")


@TestFeature
@Name("column related errors")
def feature(self, node="clickhouse1"):
    """Check the error message when creating a table with 500 columns."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_error_with_500_columns)
