from testflows.core import *

S3_ENDPOINT_PORT = 9001


@TestStep(When)
def block_s3_network(self, node, port=S3_ENDPOINT_PORT, device="eth0"):
    """Drop all packets to the MinIO endpoint port on ``node`` using tc-netem.

    Only S3-bound traffic is affected (Keeper coordination and the local client
    connection stay healthy), so the export worker keeps running and surfaces a
    retryable object-storage failure. Pair with :func:`unblock_s3_network`."""
    node.command(f"tc qdisc add dev {device} root handle 1: prio", exitcode=0)
    node.command(
        f"tc qdisc add dev {device} parent 1:3 handle 30: netem loss 100%",
        exitcode=0,
    )
    node.command(
        f"tc filter add dev {device} protocol ip parent 1:0 prio 3 u32 "
        f"match ip protocol 6 0xff match ip dport {port} 0xffff flowid 1:3",
        exitcode=0,
    )


@TestStep(When)
def unblock_s3_network(self, node, device="eth0", no_checks=False):
    """Remove the tc-netem rule added by :func:`block_s3_network`."""
    node.command(
        f"tc qdisc del dev {device} root",
        exitcode=None if no_checks else 0,
        no_checks=no_checks,
    )


@TestStep(When)
def kill_minio(self, cluster=None, container_name="s3_env-minio1-1", signal="KILL"):
    """Forcefully kill MinIO container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for MinIO container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("MinIO container still running")


@TestStep(When)
def start_minio(self, cluster=None, container_name="s3_env-minio1-1"):
    """Start MinIO container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting MinIO container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for MinIO to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} curl -f http://localhost:9001/minio/health/live",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("MinIO health check failed")


@TestStep(When)
def kill_keeper(self, cluster=None, container_name="s3_env-keeper1-1", signal="KILL"):
    """Forcefully kill ClickHouse Keeper container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for Keeper container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("Keeper container still running")


@TestStep(When)
def kill_zookeeper(
    self, cluster=None, container_name="s3_env-zookeeper1-1", signal="KILL"
):
    """Forcefully kill ZooKeeper container to simulate network crash."""

    if cluster is None:
        cluster = self.context.cluster

    retry(cluster.command, 5)(
        None,
        f"docker kill --signal={signal} {container_name}",
        timeout=60,
        exitcode=0,
        steps=False,
    )

    if signal == "TERM":
        with And("Waiting for ZooKeeper container to stop"):
            for attempt in retries(timeout=30, delay=1):
                with attempt:
                    result = cluster.command(
                        None,
                        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
                        timeout=10,
                        steps=False,
                        no_checks=True,
                    )
                    if container_name not in result.output:
                        break
                    fail("ZooKeeper container still running")


@TestStep(When)
def start_keeper(self, cluster=None, container_name="s3_env-keeper1-1"):
    """Start ClickHouse Keeper container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting Keeper container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for Keeper to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} curl -f http://localhost:9182/ready",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("Keeper health check failed")


@TestStep(When)
def start_zookeeper(self, cluster=None, container_name="s3_env-zookeeper1-1"):
    """Start ZooKeeper container and wait for it to be ready."""

    if cluster is None:
        cluster = self.context.cluster

    with By("Starting ZooKeeper container"):
        retry(cluster.command, 5)(
            None,
            f"docker start {container_name}",
            timeout=60,
            exitcode=0,
            steps=True,
        )

    with And("Waiting for ZooKeeper to be ready"):
        for attempt in retries(timeout=30, delay=1):
            with attempt:
                result = cluster.command(
                    None,
                    f"docker exec {container_name} sh -c 'echo stat | nc localhost 2181'",
                    timeout=10,
                    steps=False,
                    no_checks=True,
                )
                if result.exitcode != 0:
                    fail("ZooKeeper health check failed")
