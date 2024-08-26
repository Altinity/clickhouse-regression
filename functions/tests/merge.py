from helpers.common import *
from helpers.cluster import *

# https://github.com/ClickHouse/ClickHouse/issues/59401


@TestScenario
@Repeat(200, until="fail")
def merge(self):
    "Automated test for issue 59401."
    node_1 = self.context.node_1
    with Given("create table on three nodes"):
        table_name = "test_local" + getuid()
        create_table_query = f"""           
            CREATE TABLE default.{table_name} (name String, date Date, sign Int8) 
            ENGINE = CollapsingMergeTree(sign) 
            PARTITION BY date 
            ORDER BY name 
            SETTINGS index_granularity = 8192
        """
        for node in self.context.nodes:
            node.query(create_table_query)

    with And("I create distributed table on first node"):
        distributed_table_name = "test_distributed" + getuid()
        create_distributed = f"""
            CREATE TABLE {distributed_table_name} 
            ENGINE = Distributed(sharded_cluster, currentDatabase(), {table_name}, rand64());
        """
        node_1.query(create_distributed)

    with And("insert data into the distributed table"):
        insert_query = f"""
            INSERT INTO {distributed_table_name} 
            VALUES ('11', '2024-01-01', 1),\
            ('3', '2024-01-01', 1),\
            ('2', '2024-05-01', 1),\
            ('8', '2024-01-05', 1),\
            ('5', '2024-01-06', 1),\
            ('4', '2024-02-01', 1),\
            ('6', '2024-04-01', 1),\
            ('16', '2024-01-11', 1),\
            ('12', '2024-01-12', 1),\
            ('1', '2024-08-01', 1),\
            ('9', '2024-11-01', 1)\
        """
        node_1.query(insert_query)

    with And("check that data was inserted into the distributed table"):
        select_query = f"""
            SELECT count()
            FROM default.{distributed_table_name}
            FORMAT TabSeparated
        """
        for retry in retries(timeout=60, delay=2):
            with retry:
                count = node_1.query(select_query)
                assert count.output == "11", error()

    with Then("select count() without using `merge`"):
        correct_query = f"""
            SELECT count()
            FROM default.{distributed_table_name}
            WHERE name GLOBAL IN (
            SELECT name
            FROM default.{distributed_table_name}
            )
        """
        without_merge = node_1.query(correct_query)

    with And("select count() with using `merge` and expect the same result"):
        incorrect_query = f"""
            SELECT count()
            FROM merge('default', '{distributed_table_name}')
            WHERE name GLOBAL IN (
                SELECT name
                FROM default.{distributed_table_name}
            )
        """
        with_merge = node_1.query(incorrect_query)

    with And("check that the results without and with `merge` are the same"):
        assert with_merge.output == without_merge.output, error()


@TestFeature
@Name("merge")
def feature(self):

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node("clickhouse1"),
        self.context.cluster.node("clickhouse2"),
        self.context.cluster.node("clickhouse3"),
    ]

    for scenario in loads(current_module(), Scenario):
        scenario()
