from testflows.core import *
from testflows.asserts import error
from testflows.connect import Parser


@TestStep(Given)
def delete_any_old_topic_and_consumer_group(
    self, bootstrap_server, topic, consumer_group, node="kafka1"
):
    """Delete any old topic and consumer group."""
    cluster = current().context.cluster
    node = cluster.node(node)

    with By("deleting topic"):
        command = (
            f"kafka-topics "
            f"--bootstrap-server {bootstrap_server} --delete --topic {topic}"
        )
        node.cmd(command)

    with By("deleting consumer group"):
        command = (
            f"kafka-consumer-groups "
            f"--bootstrap-server {bootstrap_server} --delete --group {consumer_group}"
        )
        node.cmd(command)


@TestStep(Given)
def create_topic(
    self,
    bootstrap_server,
    topic,
    consumer_group,
    replication_factor,
    partitions,
    node="kafka1",
):
    """Create Kafka topic."""
    cluster = current().context.cluster
    node = cluster.node(node)

    try:
        command = (
            f"kafka-topics --create --bootstrap-server {bootstrap_server} "
            f"--replication-factor {replication_factor} --partitions {partitions} --topic {topic}"
        )
        node.cmd(command, exitcode=0)

        yield topic
    finally:
        with Finally("I cleanup Kafka topic and consumer group"):
            command = (
                f"kafka-topics "
                f"--bootstrap-server {bootstrap_server} --delete --topic {topic}"
            )
            node.cmd(command)

            command = (
                f"kafka-consumer-groups "
                f"--bootstrap-server {bootstrap_server} --delete --group {consumer_group}"
            )
            node.cmd(command)


def check_counts(counts, timeout, node="clickhouse1", steps=True):
    """Check counts."""
    parser = Parser(
        r"(?P<count>\d+)\s+(?P<unique>\d+)", types={"count": int, "unique": int}
    )
    node = current().context.cluster.node(node)

    sql = "SELECT count(), uniqExact(id) FROM dummy"

    try:
        with When(
            f"I repeatedly execute command until counts match or timeout"
        ) if steps else NullStep():
            for retry in retries(timeout=timeout, delay=1):
                with retry:
                    cmd = node.query(sql, parser=parser)
                    assert (
                        cmd.values["count"] >= counts or cmd.values["unique"] >= counts
                    )
    except Exception:
        with Finally(
            "I see that counts did not match then I re-execute query for debugging"
        ) if steps else NullStep():
            sql = "SELECT host, count(), uniqExact(id) FROM dummy GROUP BY host"
            node.query(sql)
        raise
