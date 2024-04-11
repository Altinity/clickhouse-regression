from helpers.common import *
from helpers.cluster import *


@TestScenario
def insert(self):
    with Given("I create table"):
        table_name = "tbl" + getuid()
        replica_path_suffix = table_name
        replica_name = "{replica}"
        create_table_query = f"""           
                CREATE TABLE default.{table_name} (ev_time DateTime DEFAULT now(), a DateTime, b String) 
                ENGINE = ReplicatedMergeTree('/clickhouse/tables/sharded_cluster/{replica_path_suffix}', '{replica_name}')
                ORDER BY (ev_time, a)
                PARTITION BY toStartOfWeek(ev_time);
                """
        for node in self.context.nodes:
            node.query(create_table_query)

    with And("I create second table"):
        second_table_name = "tbl_hourly" + getuid()
        replica_path_suffix = second_table_name
        create_second_table_query = f"""
                CREATE TABLE default.{second_table_name} (
                    event_count Int64 DEFAULT 1, 
                    ev_time_hour DateTime DEFAULT toStartOfHour(ev_time),\
                    ev_time DateTime DEFAULT toStartOfHour(now()) TTL ev_time_hour + INTERVAL 1 MINUTE,\
                    a DateTime,
                    b String)
                ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/sharded_cluster/{replica_path_suffix}', '{replica_name}', (a,b))
                PARTITION BY toStartOfWeek(ev_time_hour)
                ORDER BY (ev_time_hour, event_count, a, b);
                """
        for node in self.context.nodes:
            node.query(create_second_table_query)

    with And("I create third table"):
        third_table_name = "tbl_hourly_second" + getuid()
        replica_path_suffix = third_table_name
        create_third_table_query = f"""
                CREATE TABLE default.{third_table_name} (
                    event_count Int64 DEFAULT 1, 
                    ev_time_hour DateTime DEFAULT toStartOfHour(ev_time),\
                    ev_time DateTime DEFAULT toStartOfHour(now()) TTL ev_time_hour + INTERVAL 1 MINUTE,\
                    a DateTime,
                    b String)
                ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/sharded_cluster/{replica_path_suffix}', '{replica_name}', (a,b))
                PARTITION BY toStartOfWeek(ev_time_hour)
                ORDER BY (ev_time_hour, event_count, a, b);
                """
        for node in self.context.nodes:
            node.query(create_third_table_query)

    with And("I insert data"):
        insert_query = f"""
                INSERT INTO {table_name} 
                VALUES \
                ('2024-02-01 00:01:00', '2024-02-01 00:01:00', 'test1'),\
                ('2024-02-01 00:01:01', '2024-12-11 00:01:00', 'test1'),\
                ('2024-02-03 00:00:00', '2023-01-11 00:01:00', 'test1'),\
                ('2024-03-01 00:01:00', '2024-01-11 00:01:00', 'test1'),\
                ('2024-03-06 00:01:01', '2024-02-01 00:01:10', 'test1'),\
                ('2024-08-01 00:00:01', '2024-02-01 00:01:00', 'test1'),\
                ('2024-05-01 00:01:00', '2024-05-01 00:01:00', 'test1'),\
                ('2024-04-01 00:01:00', '2024-05-01 00:01:00', 'test1'),\
                ('2024-01-11 00:01:00', '2024-02-01 00:01:00', 'test1')\
                """
        self.context.node_1.query(insert_query)

    with And("I select data from first table"):
        select_query = f"""
                SELECT toStartOfHour(ev_time) AS ev_time_hour, a
                FROM default.{table_name} 
                WHERE (ev_time >= '2024-02-01 00:00:00' AND ev_time <= '2024-02-03 00:00:00')
                ORDER BY ev_time_hour, a
                FORMAT PrettyCompactMonoBlock
                """
        result = self.context.node_1.query(select_query).output

    with And("I insert data from one table to another"):
        insert_from_query = f"""
                INSERT INTO default.{second_table_name} (ev_time_hour, a, b)
                SELECT toStartOfHour(ev_time) AS ev_time_hour, a, b
                FROM default.{table_name} WHERE (ev_time >= '2024-02-01 00:00:00'
                AND ev_time <= '2024-02-03 00:00:00')
                """
        self.context.node_1.query(insert_from_query)
        select_query = f"""
                SELECT ev_time_hour, a 
                FROM {second_table_name} 
                ORDER BY ev_time_hour, a 
                FORMAT PrettyCompactMonoBlock
                """
        result_without_with = self.context.node_1.query(select_query).output

    with And(
        "I insert the same data to third table but using `with` and expect same results"
    ):
        insert_from_with = f"""
                INSERT INTO default.{third_table_name} (ev_time_hour, a, b)
                WITH ev_time >= '2024-02-01 00:00:00' AS time_step
                SELECT toStartOfHour(ev_time) AS ev_time_hour, a, b
                FROM default.{table_name} WHERE time_step and ev_time <= '2024-02-03 00:00:00'
                """
        self.context.node_1.query(insert_from_with)
        select_query = f"""
                SELECT ev_time_hour, a 
                FROM {third_table_name} 
                ORDER BY ev_time_hour, a 
                FORMAT PrettyCompactMonoBlock
                """
        result_with_with = self.context.node_1.query(select_query).output

        assert result_with_with == result_without_with == result


@TestFeature
@Name("insert")
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
