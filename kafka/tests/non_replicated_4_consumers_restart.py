from testflows.core import *
from kafka.tests.common import *


@TestScenario
@Name("non_replicated_4_consumers_restart")
@Retry(5)
def scenario(self):
    """Check that Kafka table engine can handle reading
    messages from Kafka in non-replicated mode
    with number of consumers set to 4
    when two Kafka and one ClickHouse nodes are restarted.
    Only one materialized view is attached that
    is writing to a MergeTree table.
    """
    cluster = self.context.cluster
    topic = "dummytopic"
    consumer_group = "dummytopic_consumer_group3"
    bootstrap_server = "localhost:9092"
    replication_factor = "3"
    partitions = "12"
    num_consumers = "4"
    counts = 240000
    timeout = 60

    with Given(f"there is no old topic & consumer group left"):
        delete_any_old_topic_and_consumer_group(
            bootstrap_server=bootstrap_server,
            topic=topic,
            consumer_group=consumer_group,
        )

    with And("Kafka topic"):
        create_topic(
            bootstrap_server=bootstrap_server,
            topic=topic,
            consumer_group=consumer_group,
            partitions=partitions,
            replication_factor=replication_factor,
        )

    try:
        with When("I create data source table"):
            sql = f"""
                DROP TABLE IF EXISTS source_table SYNC;
                CREATE TABLE source_table ENGINE = Log AS SELECT toUInt32(number) as id from numbers({counts}); 
                """
            cluster.node("clickhouse1").query(sql)

        with And("I copy table data to topic"):
            command = (
                f"{cluster.docker_compose} exec -T clickhouse1 clickhouse client "
                "--query='SELECT * FROM source_table FORMAT JSONEachRow' | "
                f"{cluster.docker_compose} exec -T kafka1 kafka-console-producer "
                f"--broker-list kafka1:9092,kafka2:9092,kafka3:9092 --topic {topic} > /dev/null"
            )
            cluster.command(None, command)

        with And("I create destination tables pipeline"):
            sql = f"""
                DROP TABLE IF EXISTS dummy_queue SYNC;
                DROP TABLE IF EXISTS dummy SYNC;
                DROP TABLE IF EXISTS dummy_mv SYNC;

                CREATE TABLE dummy_queue (id UInt32)
                    ENGINE = Kafka
                    SETTINGS kafka_broker_list = 'kafka1:9092,kafka2:9092,kafka3:9092',
                              kafka_topic_list = '{topic}',
                              kafka_group_name = '{consumer_group}',
                              kafka_format = 'JSONEachRow',
                              kafka_num_consumers = {num_consumers};

                CREATE TABLE dummy (
                    host String,
                    id UInt32,
                    consume_time DateTime
                ) ENGINE = MergeTree() ORDER BY (id);

                CREATE MATERIALIZED VIEW dummy_mv TO dummy AS SELECT hostName() as host, id, now() as consume_time FROM dummy_queue;
                """
            cluster.node("clickhouse1").query(sql)

        try:
            with When("I restart two Kafka and one ClickHouse nodes"):
                with By("restarting kafka3"):
                    cluster.node("kafka3").restart()

                with By("restarting kafka2"):
                    cluster.node("kafka2").restart()

                with By("restarting clickhouse1"):
                    cluster.node("clickhouse1").restart()

            with Then(f"counts should be {counts} within {timeout} sec"):
                check_counts(node="clickhouse1", counts=counts, timeout=timeout)

        finally:
            with Finally("I bring up docker-compose to restore all services"):
                command = f"{cluster.docker_compose} up -d --no-recreate 2>&1 | tee"
                cluster.command(None, command)
    finally:
        with Finally("I cleanup tables"):
            sql = """
                DROP TABLE IF EXISTS source_table SYNC;
                DROP TABLE IF EXISTS dummy_queue SYNC;
                DROP TABLE IF EXISTS dummy SYNC;
                DROP TABLE IF EXISTS dummy_mv SYNC;
                """
            cluster.node("clickhouse1").query(sql)
