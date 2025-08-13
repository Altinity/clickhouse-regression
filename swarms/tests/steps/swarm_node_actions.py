#!/usr/bin/env python3
import random
import json
import time
from threading import RLock
from itertools import chain

from testflows.core import *
from testflows.combinatorics import combinations

from helpers.alter import *
from helpers.common import *
from alter.stress.tests.tc_netem import *
from alter.stress.tests.steps import *
from ssl_server.tests.zookeeper.steps import add_zookeeper_config_file

table_schema_lock = RLock()

# There's an important tradeoff between these two sets of timeouts.
# If the query runs for longer than the step timeout, the step will not
# get retried using a different node and table.

step_retry_timeout = 900
step_retry_delay = 30


@TestStep(Given)
def restart_zookeeper(self, delay=None, delay_before_interrupt=None):
    """
    Stop a random zookeeper instance, wait, and restart.
    This simulates a short outage.
    """
    zookeeper_node = random.choice(self.context.zookeeper_nodes)

    if delay is None:
        delay = random.random() * 10 + 1

    if delay_before_interrupt:
        time.sleep(delay_before_interrupt)

    with interrupt_node(zookeeper_node):
        with When(f"I wait {delay:.2}s"):
            time.sleep(delay)


@TestStep(Given)
def restart_random_swarm_node(self, delay=None):
    """
    Send a kill signal to a random clickhouse swarm instance, wait, and restart.
    This simulates a short outage.
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
    This simulates a short outage.
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
def fill_clickhouse_disks(self):
    """Force clickhouse to run on a full disk."""

    node = random.choice(self.context.swarm_nodes)
    clickhouse_disk_mounts = [
        "/var/log/clickhouse-server-limited",
        "/var/lib/clickhouse-limited",
    ]
    delay = random.random() * 10 + 5
    file_name = "file.dat"

    with Given("apply limited disk config"):
        clickhouse_limited_disk_config(node=node)

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
def limit_clickhouse_disks(self, node):
    """
    Restart clickhouse using small disks.
    """

    migrate_dirs = {
        "/var/lib/clickhouse": "/var/lib/clickhouse-limited",
        "/var/log/clickhouse-server": "/var/log/clickhouse-server-limited",
    }

    try:
        with Given("I stop clickhouse"):
            node.stop_clickhouse()

        with And("I move clickhouse files to small disks"):
            node.command("apt update && apt install rsync -y")

            for normal_dir, limited_dir in migrate_dirs.items():
                node.command(f"rsync -a -H --delete {normal_dir}/ {limited_dir}")

        with And("I write an override config for clickhouse"):
            clickhouse_limited_disk_config(node=node)

        with And("I restart clickhouse on those disks"):
            node.start_clickhouse(log_dir="/var/log/clickhouse-server-limited")

        yield

    finally:
        with Finally("I stop clickhouse"):
            node.stop_clickhouse()

        with And("I move clickhouse files from the small disks"):
            for normal_dir, limited_dir in migrate_dirs.items():
                node.command(f"rsync -a -H --delete {limited_dir}/ {normal_dir}")

        with And("I restart clickhouse on those disks"):
            node.start_clickhouse()


@TestStep(Given)
def limit_zookeeper_disks(self, node):
    """
    Restart zookeeper using small disks.
    """

    migrate_dirs = {
        "/data": "/data-limited",
        "/datalog": "/datalog-limited",
    }
    zk_config = {"dataDir": "/data-limited", "dataLogDir": "/datalog-limited"}

    try:
        with Given("I stop zookeeper"):
            node.stop_zookeeper()

        with And("I move zookeeper files to small disks"):
            node.command("apt update && apt install rsync -y")

            for normal_dir, limited_dir in migrate_dirs.items():
                node.command(f"rsync -a -H --delete {normal_dir}/ {limited_dir}")

        with And("I write an override config for zookeeper"):
            add_zookeeper_config_file(entries=zk_config, restart=True, node=node)

        yield

    finally:
        with Finally("I stop zookeeper"):
            node.stop_zookeeper()

        with And("I move zookeeper files from the small disks"):
            for normal_dir, limited_dir in migrate_dirs.items():
                node.command(f"rsync -a -H --delete {limited_dir}/ {normal_dir}")

        with Finally("I start zookeeper"):
            node.start_zookeeper()


@TestStep(Given)
def fill_zookeeper_disks(self):
    """Force zookeeper to run on a full disk."""

    node = random.choice(self.context.zk_nodes)
    zookeeper_disk_mounts = ["/data-limited", "/datalog-limited"]
    delay = random.random() * 10 + 5
    file_name = "file.dat"

    try:
        for disk_mount in zookeeper_disk_mounts:
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

    finally:
        with Finally(f"I delete the large file on {node.name}"):
            for disk_mount in zookeeper_disk_mounts:
                node.command(f"rm {disk_mount}/{file_name}")

        with And(f"I restart {node.name} in case it crashed"):
            node.restart_zookeeper()
