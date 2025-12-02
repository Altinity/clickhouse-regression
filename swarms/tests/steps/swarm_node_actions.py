#!/usr/bin/env python3
import time
import random

from testflows.core import *

from helpers.alter import *
from helpers.common import *
from alter.stress.tests.steps import (
    interrupt_clickhouse,
    interrupt_node,
    interrupt_network,
)

import iceberg.tests.steps.iceberg_engine as iceberg_engine


# There's an important tradeoff between these two sets of timeouts.
# If the query runs for longer than the step timeout, the step will not
# get retried using a different node and table.
step_retry_timeout = 900
step_retry_delay = 30


@TestStep(Given)
def restart_random_swarm_node(self, delay=None):
    """
    Stop selected swarm node container, wait, and restart.
    """
    clickhouse_node = random.choice(self.context.swarm_nodes)

    if delay is None:
        delay = random.random() * 10 + 1

    with interrupt_node(clickhouse_node):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


@TestStep(Given)
def restart_clickhouse_on_random_swarm_node(self, signal="SEGV", delay=None):
    """
    Send a kill signal to a random clickhouse swarm instance, wait, and restart.
    """
    clickhouse_node = random.choice(self.context.swarm_nodes)

    if delay is None:
        delay = random.random() * 10 + 1

    with interrupt_clickhouse(clickhouse_node, safe=False, signal=signal):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


@TestStep(Given)
@Retry(timeout=step_retry_timeout, delay=step_retry_delay)
def restart_network_on_random_swarm_node(
    self, restart_node_after=True, delay_before_disconnect=2
):
    """
    Stop the network on a random instance, wait, and restart.
    This simulates a short outage.
    """
    node = random.choice(self.context.swarm_nodes)
    delay = random.random() * 5 + 1

    if delay_before_disconnect:
        with When(f"I wait {delay_before_disconnect}s before disconnecting"):
            time.sleep(delay_before_disconnect)

    with interrupt_network(self.context.cluster, node, "swarms"):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)

    if restart_node_after:
        with When("I restart the node to ensure communication is restored"):
            node.restart()


@TestStep(Given)
def fill_clickhouse_disks(
    self, node=None, database_name=None, minio_root_user=None, minio_root_password=None
):
    """Force clickhouse to run out of disk space."""
    if node is None:
        node = self.context.node

    clickhouse_disk_mounts = [
        "/var/log/clickhouse-server-limited",
        "/var/lib/clickhouse-limited",
    ]
    delay = random.random() * 10 + 5
    file_name = "file.dat"

    with Given("apply limited disk config"):
        clickhouse_limited_disk_config(node=node)

    if database_name is not None:
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    try:
        for disk_mount in clickhouse_disk_mounts:
            with When(f"I get the size of {disk_mount} on {node.name}"):
                r = node.command(f"df -k --output=size {disk_mount}")
                disk_size_k = r.output.splitlines()[1].strip()
                assert int(disk_size_k) < 100e6, error(
                    "Disk does not appear to be restricted!"
                )

            with And(f"I create a file to fill {disk_mount} on {node.name}"):
                node.command(
                    f"dd if=/dev/zero of={disk_mount}/{file_name} bs=1K count={disk_size_k}",
                    no_checks=True,
                )

        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)

        with And("check that disk is actually full"):
            result = node.query(
                f"SELECT total_space, free_space FROM system.disks FORMAT TabSeparated"
            )
            assert result.output == "1073740800	0", error()

        yield

    finally:
        with Finally(f"I delete the large file on {node.name}"):
            for disk_mount in clickhouse_disk_mounts:
                node.command(f"rm {disk_mount}/{file_name}")

        with And(f"I restart {node.name} in case it crashed"):
            node.restart_clickhouse(safe=False)


@TestStep(Given)
def clickhouse_limited_disk_config(self, node):
    """Install a config file overriding clickhouse storage locations"""
    config_override = {
        "logger": {
            KeyWithAttributes(
                "log", {"replace": "replace"}
            ): "/var/log/clickhouse-server-limited/clickhouse-server.log",
            KeyWithAttributes(
                "errorlog", {"replace": "replace"}
            ): "/var/log/clickhouse-server-limited/clickhouse-server.err.log",
        },
        KeyWithAttributes(
            "path", {"replace": "replace"}
        ): "/var/lib/clickhouse-limited/",
        KeyWithAttributes(
            "tmp_path", {"replace": "replace"}
        ): "/var/lib/clickhouse-limited/tmp/",
        KeyWithAttributes(
            "user_files_path", {"replace": "replace"}
        ): "/var/lib/clickhouse-limited/user_files/",
        KeyWithAttributes(
            "access_control_path", {"replace": "replace"}
        ): "/var/lib/clickhouse-limited/access/",
        "user_directories": {
            "local_directory": {
                KeyWithAttributes(
                    "path", {"replace": "replace"}
                ): "/var/lib/clickhouse-limited/access/"
            },
        },
    }

    config = create_xml_config_content(
        entries=config_override,
        config_file="override_data_dir.xml",
    )
    return add_config(
        config=config,
        restart=True,
        node=node,
        check_preprocessed=True,
        after_removal=False,
    )


@TestStep(Given)
def swarm_cpu_load(self, node=None, seconds=60 * 3):
    """
    Create CPU contention by spawning many tight busy-loop processes inside a node.
    - node: target ClickHouse node (defaults to a random swarm node)
    - seconds: how long to keep the overload
    - factor: processes per core (e.g., 1.0 ~= 1 per core, 2.0 ~= 2 per core)
    """
    if node is None:
        node = random.choice(self.context.swarm_nodes)

    with By("give yes higher priority than clickhouse"):
        node.command("pgrep -x yes | xargs -r renice -n -5")
        node.command("pgrep -x clickhouse-server | xargs -r renice -n +10")

    try:
        start = "yes > /dev/null"
        node.command(start)
        with By(f"I keep CPU saturated for {seconds:.1f}s"):
            time.sleep(seconds)
        yield
    finally:
        with Finally("I stop CPU hogs"):
            stop = "pkill -9 yes"
            node.command(stop)


@TestStep(Given)
def swarm_cpu_load(self, node=None, seconds=60 * 3, factor=3.0):
    """
    Create CPU contention by starting `yes` workers.
    - seconds: duration to keep the load
    - factor: workers per core (1.0 ≈ 1 per core, 2.0 ≈ 2 per core)
    """
    import random, time, math

    if node is None:
        node = random.choice(self.context.swarm_nodes)

    # How many logical CPUs?
    cores = int(node.command("nproc").output.strip())
    procs = max(1, math.ceil(cores * float(factor)))

    with By("give yes higher priority than clickhouse"):
        node.command("pgrep -x yes | xargs -r renice -n -10")
        node.command("pgrep -x clickhouse-server | xargs -r renice -n +20")

    try:
        # Start one `yes` per worker in background
        start = f"sh -c 'for i in $(seq 1 {procs}); do yes > /dev/null & done'"
        node.command(start)

        with By(
            f"CPU load: {procs} workers (~{cores} cores × factor {factor}) for {seconds}s"
        ):
            time.sleep(seconds)
        yield
    finally:
        with Finally("stop cpu hogs"):
            node.command("sh -c 'pkill -9 yes 2>/dev/null || true'")


@TestStep(Given)
def swarm_cpu_load_by_stop_clickhouse(self, node=None, seconds=60 * 1, factor=3.0):
    """
    Create CPU contention by starting `yes` workers.
    - seconds: duration to keep the load
    - factor: workers per core (1.0 ≈ 1 per core, 2.0 ≈ 2 per core)
    """

    if node is None:
        node = random.choice(self.context.swarm_nodes)

    try:
        start = f"pgrep -x clickhouse | xargs -r kill -STOP"
        node.command(start)

        with By(f"sleep {seconds}s with clickhouse stopped"):
            time.sleep(seconds)
        yield
    finally:
        with Finally("start clickhouse"):
            node.command("pgrep -x clickhouse | xargs -r kill -CONT")
