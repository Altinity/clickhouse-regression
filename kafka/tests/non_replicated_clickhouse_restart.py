import time
from testflows.core import *
from kafka.tests.common import *


@TestScenario
@Name("non_replicated_clickhouse_restart")
def scenario(self):
    """Check that Kafka table engine can handle reading
    messages from Kafka in non-replicated mode
    with only one materialized view
    attached that is writing to a MergeTree table.
    When data is read from Kafka we restart
    ClickHouse node multiple times and check the data.
    """
    cluster = self.context.cluster
    topic = "dummytopic"
    consumer_group = "dummytopic_consumer_group2"
    bootstrap_server = "localhost:9092"
    replication_factor = "3"
    partitions = "12"
    counts = 240000
    timeout = 120

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

                CREATE TABLE dummy_queue (
                    id UInt32
                ) ENGINE = Kafka('kafka1:9092,kafka2:9092,kafka3:9092', '{topic}', '{consumer_group}', 'JSONEachRow');

                CREATE TABLE dummy (
                    host String,
                    id UInt32
                ) ENGINE = MergeTree ORDER BY (id);

                CREATE MATERIALIZED VIEW dummy_mv TO dummy AS SELECT hostName() as host, id FROM dummy_queue;
                """
            cluster.node("clickhouse1").query(sql)

            with Then(
                f"I repeatedly restart ClickHouse and check that counts are {counts} within {timeout} sec"
            ):
                for attempt in retries(timeout=timeout, delay=0.1):
                    with attempt:
                        cluster.node("clickhouse1").restart(safe=False)
                        with Then("sleeping 15 sec to allow some progress"):
                            time.sleep(15)
                        check_counts(
                            node="clickhouse1", counts=counts, timeout=0, steps=False
                        )

    finally:
        with Finally("I bring up docker-compose to restore all services"):
            command = f"{cluster.docker_compose} up -d --no-recreate 2>&1 | tee"
            cluster.command(None, command)

        with And("I cleanup tables"):
            sql = """
                DROP TABLE IF EXISTS source_table SYNC;
                DROP TABLE IF EXISTS dummy_queue SYNC;
                DROP TABLE IF EXISTS dummy SYNC;
                DROP TABLE IF EXISTS dummy_mv SYNC;
                """
            cluster.node("clickhouse1").query(sql)
