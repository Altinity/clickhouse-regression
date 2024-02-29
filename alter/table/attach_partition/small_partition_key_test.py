from testflows.core import *


@TestScenario
@Flags(TE)
def small_test(self, with_id=False):
    node_1 = self.context.node_1
    node_2 = self.context.node_2
    node_3 = self.context.node_3
    nodes = [node_1, node_2, node_3]

    for node in nodes:
        node.query("drop table IF EXISTS source")
        node.query("drop table IF EXISTS destination")

    for node in nodes:
        node.query(f"""
                CREATE TABLE IF NOT EXISTS source 
                ON CLUSTER replicated_cluster_secure 
                (a UInt16,b UInt16,c UInt16,extra UInt64,Path String,Time DateTime,Value Float64,Timestamp Int64,sign Int8)
                ENGINE = ReplicatedMergeTree
                PARTITION BY (a,b)
                ORDER BY tuple()
                """
        ) 

    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT 1, 5, 9, number+1000, 1 FROM numbers(4)")
    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT number+10, number+1+14, number+1+18, number+1001, 1 FROM numbers(10)")
    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT 2, 6, 10, number+1000, 1 FROM numbers(4)")
    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT number+10, number+2+14, number+2+18, number+1001, 1 FROM numbers(10)")
    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT 3, 7, 11, number+1000, 1 FROM numbers(4)")
    node_2.query(f"INSERT INTO source (a, b, c, extra, sign) SELECT number+10, number+3+14, number+3+18, number+1001, 1 FROM numbers(10)")

    for node in nodes:
        node.query(f"""
                CREATE TABLE IF NOT EXISTS destination
                ON CLUSTER replicated_cluster_secure (a UInt16,b UInt16,c UInt16,extra UInt64,Path String,Time DateTime,Value Float64,Timestamp Int64,sign Int8)
                ENGINE = ReplicatedMergeTree
                PARTITION BY b
                ORDER BY tuple()
                """
        )
        node.query(f"ALTER TABLE destination MODIFY SETTING allow_experimental_alter_partition_with_different_key=1")
   
    node_1.query(f"ALTER TABLE destination ATTACH PARTITION (1,5) FROM source")
    node_2.query(f"ALTER TABLE destination ATTACH PARTITION (10,16) FROM source")

    node_1.query(f"SELECT * FROM source format PrettyCompactMonoBlock")
    node_2.query(f"SELECT * FROM source format PrettyCompactMonoBlock")
    node_3.query(f"SELECT * FROM source format PrettyCompactMonoBlock")

    node_1.query(f"SELECT * FROM destination format PrettyCompactMonoBlock")
    node_2.query(f"SELECT * FROM destination format PrettyCompactMonoBlock")
    node_3.query(f"SELECT * FROM destination format PrettyCompactMonoBlock")

    for node in nodes:
        node.query("drop table IF EXISTS source")
        node.query("drop table IF EXISTS destination")


@TestFeature
@Name("small test")
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