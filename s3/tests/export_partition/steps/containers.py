from testflows.core import *


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
