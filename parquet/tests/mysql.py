from testflows.core import *
from parquet.requirements import *
from helpers.common import *
from parquet.tests.common import *
from s3.tests.common import *


@TestSuite
@Requirements()
def mysql(self, node=None):
    """Check that ClickHouse writes Parquet format correctly into mysql."""

    if node is None:
        node = self.context.node

    Scenario(run=write_mysql_table_engine)
    Scenario(run=write_mysql_table_function)


@TestScenario
@Requirements()
def write_mysql_table_engine(self):
    """Check that ClickHouse writes Parquet format correctly into mysql table function."""

    mysql_node = self.context.cluster.node("mysql1")
    table_name = "table_" + getuid()

    with Given("I have a table."):
        table(
            name=table_name, engine=f"MySQL('mysql1', 'default', 'default', '')"
        )  # TODO

    with When("I insert some data."):
        insert_test_data(name=table_name)

    with Then("I check the mysql table."):
        check_mysql(mysql_node=mysql_node, name=table_name)


@TestScenario
@Requirements()
def write_mysql_table_function(self):
    """Check that ClickHouse writes Parquet format correctly into mysql table function."""
    node = self.context.node
    mysql_node = self.context.cluster.node("mysql1")
    table_name = "table_" + getuid()

    with When("I insert some data into the s3 function."):
        node.query(
            f"""
            INSERT INTO FUNCTION mysql('mysql1:9004', 'default', {table_name}, 'default', '', Parquet)
            SELECT (1,2,3,4,5,6,7,8,9,10,11,'2022-01-01','2022-01-01 00:00:00','A','B',[1,2,3],(1,2,3), {{'a':1, 'b',2}})
            """
        )

    with Then("I check the mysql table."):
        check_mysql(mysql_node=mysql_node, name=table_name)


@TestFeature
@Name("mysql")
def feature(self, node="clickhouse1"):
    """Run checks for clickhouse using Parquet format using mysql engines."""

    self.context.node = self.context.cluster.node(node)
    xfail("Not implemented")

    Suite(run=mysql)
