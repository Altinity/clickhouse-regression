from helpers.common import *
from helpers.cluster import *
from helpers.tables import create_table


# https://github.com/ClickHouse/ClickHouse/pull/58638


@TestScenario
def projection_optimization(self):
    "Automated test for pull 58638."
    node = self.context.node

    with Given("I create two tables with projections"):
        table1_name = "table1" + getuid()
        node.query(
            f"""
            CREATE TABLE {table1_name} (col1 String, col2 String, _time DateTime, projection p (select * order by col2)) 
            ENGINE = MergeTree 
            PARTITION BY col1 
            ORDER BY tuple()
            """
        )
        table2_name = "table2" + getuid()
        node.query(
            f"""
            CREATE TABLE {table2_name} (col1 String, col2 String, _time DateTime, projection p (select * order by col2)) 
            ENGINE = MergeTree 
            PARTITION BY col1 
            ORDER BY tuple()
            """
        )

    with And("I insert data into the tables"):
        node.query(
            f"INSERT INTO {table1_name} (col1, col2, _time) VALUES ('xxx', 'zzzz', now()+1)"
        )
        node.query(
            f"INSERT INTO {table2_name} (col1, col2, _time) VALUES ('xxx', 'zzzz', now())"
        )

    with When("I run select query"):
        r = node.query(
            f"""
            SELECT count()
            FROM {table1_name}
            WHERE (col1 = 'xxx') AND (_time = (
                SELECT max(_time)
                FROM {table2_name}
                WHERE (col1 = 'xxx') AND (col2 = 'zzzz') AND (_time > (now() - toIntervalDay(3)))
            ))
            SETTINGS force_index_by_date = 1
            """
        )

    with Then("I check the output"):
        assert r.exitcode == 0, error()
        assert int(r.output) == 0 or int(r.output) == 1, error()


@TestFeature
@Name("projection optimization")
def feature(self):
    self.context.node = self.context.cluster.node("clickhouse1")
    for scenario in loads(current_module(), Scenario):
        scenario()
