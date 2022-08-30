from testflows.core import *
from kafka.tests.common import *


@TestScenario
@Name("replicated_stop_and_restart")
@Retry(5)
def scenario(self):
    """Check that Kafka table engine can handle stopping and
    and restarting of one of the Kafka and ClickHouse
    nodes without losing or duplicating messages when
    materialized view is writing to a ReplicatedMergeTree table.
    """
    cluster = self.context.cluster
    topic = "dummytopic"
    consumer_group = "dummytopic_consumer_group1"
    bootstrap_server = "localhost:9092"
    replication_factor = "2"
    partitions = "12"
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
            cluster.command(None, command, exitcode=0)

        with And("I create destination tables pipeline"):
            sql = (
                f"""
                DROP TABLE IF EXISTS dummy_queue ON CLUSTER replicated_cluster SYNC;
                DROP TABLE IF EXISTS dummy ON CLUSTER replicated_cluster SYNC;
                DROP TABLE IF EXISTS dummy_mv ON CLUSTER replicated_cluster SYNC;

                CREATE TABLE dummy_queue ON CLUSTER replicated_cluster (
                     id UInt32
                ) ENGINE = Kafka('kafka1:9092,kafka2:9092,kafka3:9092',
                      '{topic}', '{consumer_group}', 'JSONEachRow'
                );"""
                """
                CREATE TABLE dummy ON CLUSTER replicated_cluster (
                     host String,
                     id UInt32
                ) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{database}-{shard}/{table}', '{replica}') ORDER BY (id);

                CREATE MATERIALIZED VIEW dummy_mv ON CLUSTER replicated_cluster TO dummy AS SELECT hostName() as host, id FROM dummy_queue;
                """
            )
            cluster.node("clickhouse1").query(sql)

        with Then(f"counts should be {counts} within {timeout} sec"):
            check_counts(node="clickhouse1", counts=counts, timeout=timeout)

        with When("I stop one kafka node (broker rebalance)"):
            command = f"{cluster.docker_compose} stop kafka2 >/dev/null"
            cluster.command(None, command, exitcode=0)

            with And("put more data into kafka"):
                cluster.command(
                    None,
                    f"{cluster.docker_compose} exec -T clickhouse1 clickhouse client "
                    "--query='SELECT id+1000000 as id FROM source_table FORMAT JSONEachRow' | "
                    f"{cluster.docker_compose} exec -T kafka1 kafka-console-producer "
                    f"--broker-list kafka1:9092,kafka2:9092,kafka3:9092 --topic {topic} > /dev/null",
                    exitcode=0,
                )

            with Then(f"counts should be {counts*2} within {timeout}"):
                check_counts(node="clickhouse1", counts=counts * 2, timeout=timeout)

        with When("I start kafka node back (broker rebalance #2)"):
            cluster.command(None, f"{cluster.docker_compose} start kafka2", exitcode=0)

            with Then(f"counts should be {counts*2}"):
                check_counts(node="clickhouse1", counts=counts * 2, timeout=30)

            with And("ask Kafka for consumer group description"):
                command = (
                    f"{cluster.docker_compose} exec kafka1 kafka-consumer-groups "
                    f"--bootstrap-server {bootstrap_server} --describe --group {consumer_group}"
                )
                cluster.command(None, command, exitcode=0)

            with When("I stop one clickhouse node (consumer group rebalance)"):
                cluster.node("clickhouse2").stop(safe=False)

            with And("put more data into kafka"):
                command = (
                    f"{cluster.docker_compose} exec -T clickhouse1 clickhouse client "
                    "--query='SELECT id+2000000 as id FROM source_table FORMAT JSONEachRow' | "
                    f"{cluster.docker_compose} exec -T kafka1 kafka-console-producer "
                    f"--broker-list kafka1:9092,kafka2:9092,kafka3:9092 --topic {topic} > /dev/null"
                )
                cluster.command(None, command, exitcode=0)

            with Then(f"counts should be {counts*3} within {timeout}"):
                check_counts(node="clickhouse1", counts=counts * 3, timeout=timeout)

        with When("I start clickhouse node back (consumer group rebalance #2)"):
            cluster.node("clickhouse2").start()

            with Then(f"counts should be still be {counts*3}"):
                check_counts(node="clickhouse1", counts=counts * 3, timeout=30)

    finally:
        with Finally("I bring up docker-compose to restore all services"):
            command = f"{cluster.docker_compose} up -d --no-recreate 2>&1 | tee"
            cluster.command(None, command)

        with And("cleanup tables"):
            sql = """
                DROP TABLE IF EXISTS source_table SYNC;
                DROP TABLE IF EXISTS dummy_queue ON CLUSTER replicated_cluster SYNC;
                DROP TABLE IF EXISTS dummy ON CLUSTER replicated_cluster SYNC;
                DROP TABLE IF EXISTS dummy_mv ON CLUSTER replicated_cluster SYNC;
                """
            cluster.node("clickhouse1").query(sql)
