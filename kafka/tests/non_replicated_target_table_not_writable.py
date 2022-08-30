import time
from testflows.core import *
from testflows.core.utils import Timer
from kafka.tests.common import *


@TestScenario
@Name("non_replicated_target_table_not_writable")
def scenario(self):
    """Check that Kafka table engine can handle reading
    messages from Kafka in non-replicated mode
    with only one materialized view
    attached that is writing to a MergeTree table
    but the target table sometimes not writable.
    """
    cluster = self.context.cluster
    topic = "dummytopic"
    consumer_group = "dummytopic_consumer_group2"
    bootstrap_server = "localhost:9092"
    replication_factor = "3"
    partitions = "12"
    counts = 240000
    timeout = 15

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

        with When("I make materialized view target table sometimes read-only"):
            with By("first checking current permissions"):
                command = f"{cluster.docker_compose} exec -T clickhouse1 ls -la /var/lib/clickhouse/data/default"
                cluster.command(None, command, exitcode=0)

            change_permissions_timeout = 12
            change_permissions_interval = 3
            change_permissions_command = f"{cluster.docker_compose} exec -T clickhouse1 chmod u=,g=,o= /var/lib/clickhouse/data/default/dummy"
            restore_permissions_command = f"{cluster.docker_compose} exec -T clickhouse1 chmod u=rwx,g=rx,o= /var/lib/clickhouse/data/default/dummy"
            with By(
                f"then repeatedly changing permissions",
                description=f"""
                    for {change_permissions_timeout} sec with and interval of {change_permissions_interval} sec
                    by using command
                        {change_permissions_command}
                    and restoring permissions using command
                        {restore_permissions_command}
                    """,
            ):
                timer = Timer(change_permissions_timeout)

                while timer.time():
                    cluster.command(None, change_permissions_command, exitcode=0)
                    cluster.command(
                        None,
                        f"{cluster.docker_compose} exec -T clickhouse1 ls -la /var/lib/clickhouse/data/default",
                        exitcode=0,
                    )

                    time.sleep(change_permissions_interval)

                    cluster.command(None, restore_permissions_command, exitcode=0)
                    cluster.command(
                        None,
                        f"{cluster.docker_compose} exec -T clickhouse1 ls -la /var/lib/clickhouse/data/default",
                        exitcode=0,
                    )

        with Then(f"counts should be {counts} within {timeout} sec"):
            check_counts(node="clickhouse1", counts=counts, timeout=timeout)

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
