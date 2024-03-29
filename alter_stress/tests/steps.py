#!/usr/bin/env python3
import random
import json
from contextlib import contextmanager
from platform import processor

from testflows.core import *

from helpers.alter import *
from s3.tests.common import s3_storage


@TestStep(Given)
def s3_config(self):
    """Set up disks and policies for vfs tests."""
    with Given("I have two S3 disks configured"):
        disks = {
            "external": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/storage/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
            "external_tiered": {
                "type": "s3",
                "endpoint": f"{self.context.uri}object-storage/tiered/",
                "access_key_id": f"{self.context.access_key_id}",
                "secret_access_key": f"{self.context.secret_access_key}",
            },
        }

    with And("""I have a storage policy configured to use the S3 disk"""):
        policies = {
            "external": {"volumes": {"external": {"disk": "external"}}},
            "tiered": {
                "volumes": {
                    "default": {"disk": "external"},
                    "external": {"disk": "external_tiered"},
                }
            },
        }

    return s3_storage(
        disks=disks,
        policies=policies,
        restart=True,
        timeout=30,
        config_file="s3_storage.xml",
    )


@TestStep
def get_nodes_for_table(self, nodes, table_name):
    """Return all nodes that know about a given table."""
    active_nodes = []
    for node in nodes:
        r = nodes[0].query("SELECT table from system.replicas FORMAT JSONColumns")
        tables = json.loads(r.output)["table"]
        if table_name in tables:
            active_nodes.append(node)

    return active_nodes


@TestStep
def get_random_table_name(self):
    return random.choice(self.context.table_names)


@TestStep
def get_random_node_for_table(self, table_name):
    return random.choice(
        get_nodes_for_table(nodes=self.context.ch_nodes, table_name=table_name)
    )


@TestStep
def get_projections(self, node, table_name):
    r = node.query(
        f"SELECT distinct(name) FROM system.projection_parts WHERE table='{table_name}' FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_indexes(self, node, table_name):
    r = node.query(
        f"SELECT name FROM system.data_skipping_indices WHERE table='{table_name}' FORMAT JSONColumns",
        exitcode=0,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_column_names(self, node, table_name, timeout=30) -> list:
    """Get a list of a table's column names."""
    r = node.query(
        f"DESCRIBE TABLE {table_name} FORMAT JSONColumns",
        timeout=timeout,
    )
    return json.loads(r.output)["name"]


@TestStep
def get_random_column_name(self, node, table_name):
    """Choose a column name at random."""
    columns_no_primary_key = get_column_names(node=node, table_name=table_name)[1:]
    return random.choice(columns_no_primary_key)


@contextmanager
def interrupt_node(node):
    """
    Stop the given node container.
    Instance is restarted on context exit.
    """
    try:
        with When(f"{node.name} is stopped"):
            node.stop()
            yield

    finally:
        with When(f"{node.name} is started"):
            node.start()


@contextmanager
def interrupt_clickhouse(node, safe=True, signal="KILL"):
    """
    Stop the given clickhouse instance with the given signal.
    Instance is restarted on context exit.
    """
    try:
        with When(f"{node.name} is stopped"):
            node.stop_clickhouse(safe=safe, signal=signal)
            yield

    finally:
        with When(f"{node.name} is started"):
            node.start_clickhouse(check_version=False)


@contextmanager
def interrupt_network(cluster, node, cluster_prefix):
    """
    Disconnect the given node container.
    Instance is reconnected on context exit.
    """
    if processor() == "x86_64":
        container = f"{cluster_prefix}_env-{node.name}-1"
    else:
        container = f"{cluster_prefix}_env_arm64-{node.name}-1"

    DOCKER_NETWORK = (
        f"{cluster_prefix}_env_default"
        if processor() == "x86_64"
        else f"{cluster_prefix}_env_arm64"
    )

    try:
        with When(f"{node.name} is disconnected"):
            cluster.command(
                None, f"docker network disconnect {DOCKER_NETWORK} {container}"
            )

        yield

    finally:
        with When(f"{node.name} is reconnected"):
            cluster.command(
                None, f"docker network connect {DOCKER_NETWORK} {container}"
            )
