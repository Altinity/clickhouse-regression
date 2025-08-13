#!/usr/bin/env python3
import random
import json
import time
import re
from contextlib import contextmanager
from platform import processor

from testflows.core import *
from testflows.asserts import error

from helpers.queries import *
from helpers.common import getuid
from s3.tests.common import (
    s3_storage,
    insert_random,
    replicated_table as create_one_replica,
    delete_replica as delete_one_replica,
    replicated_table_cluster,
)


@TestStep(Given)
def disk_config(self):
    """Set up disks and policies for stress tests."""

    if getattr(self.context, "uri", None):
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

        with And("I have storage policies configured to use the S3 disks"):
            policies = {
                "external": {"volumes": {"external": {"disk": "external"}}},
                "tiered": {
                    "volumes": {
                        "default": {"disk": "external"},
                        "external": {"disk": "external_tiered"},
                    }
                },
            }

    else:
        with Given("I have two jbod disks configured"):
            disks = {
                "jbod1": {"path": "/jbod1/"},
                "jbod2": {"path": "/jbod2/"},
            }

        with And("I have storage policies configured to use the jbod disks"):
            policies = {
                "external": {"volumes": {"external": {"disk": "jbod1"}}},
                "tiered": {
                    "volumes": {
                        "default": {"disk": "jbod1"},
                        "external": {"disk": "jbod2"},
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


@TestStep(Given)
def insert_random(
    self,
    node,
    table_name,
    columns,
    rows: int = 1000000,
    settings: str = None,
    **kwargs,
):
    """Insert random data to a table."""

    if settings:
        settings = "SETTINGS " + settings
    else:
        settings = ""

    return node.query(
        f"INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') LIMIT {rows} {settings}",
        exitcode=0,
        **kwargs,
    )


@TestStep(Given)
def replicated_table_cluster(
    self,
    columns: str,
    table_name: str = None,
    storage_policy: str = "external",
    cluster_name: str = "replicated_cluster",
    order_by: str = None,
    partition_by: str = None,
    primary_key: str = None,
    ttl: str = None,
    settings: str = None,
    allow_zero_copy: bool = None,
    exitcode: int = 0,
    no_cleanup=False,
):
    """Create a replicated table with the ON CLUSTER clause."""
    node = current().context.node

    if table_name is None:
        table_name = "table_" + getuid()

    if order_by is None:
        order_by = columns.split()[0]

    if settings is None:
        settings = []
    else:
        settings = [settings]

    settings.append(f"storage_policy='{storage_policy}'")

    if allow_zero_copy is not None:
        settings.append(f"allow_remote_fs_zero_copy_replication={int(allow_zero_copy)}")

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    if primary_key is not None:
        primary_key = f"PRIMARY KEY {primary_key}"
    else:
        primary_key = ""

    if ttl is not None:
        ttl = "TTL " + ttl
    else:
        ttl = ""

    try:
        with Given("I have a table"):
            r = node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} 
                ON CLUSTER '{cluster_name}' ({columns}) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
                ORDER BY {order_by} {partition_by} {primary_key} {ttl}
                SETTINGS {', '.join(settings)}
                """,
                settings=[("distributed_ddl_task_timeout", 360)],
                exitcode=exitcode,
            )

        yield r, table_name

    finally:
        if not no_cleanup:
            with Finally(f"I drop the table"):
                for attempt in retries(timeout=120, delay=5):
                    with attempt:
                        node.query(
                            f"DROP TABLE IF EXISTS {table_name} ON CLUSTER '{cluster_name}' SYNC",
                            timeout=60,
                        )


@TestStep(Given)
def create_one_replica(
    self,
    node,
    table_name,
    columns="d UInt64",
    order_by="d",
    partition_by=None,
    replica_path_suffix=None,
    replica_name="{replica}",
    no_checks=False,
    storage_policy="external",
):
    """
    Create a simple replicated table on the given node.
    Call multiple times with the same table name and different nodes
    to create multiple replicas.
    """
    if replica_path_suffix is None:
        replica_path_suffix = table_name

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    r = node.query(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} ({columns}) 
        ENGINE=ReplicatedMergeTree('/clickhouse/tables/{replica_path_suffix}', '{replica_name}')
        ORDER BY ({order_by}) {partition_by}
        SETTINGS storage_policy='{storage_policy}'
        """,
        no_checks=no_checks,
        exitcode=0,
    )
    return r


@TestStep(Given)
def delete_one_replica(self, node, table_name, timeout=30):
    """Delete the local copy of a replicated table."""
    r = node.query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0, timeout=timeout
    )
    return r


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    """Assert that the number of rows in a table is as expected."""
    if node is None:
        node = current().context.node

    actual_count = get_row_count(node=node, table_name=table_name)
    assert rows == actual_count, error()


@TestStep
def get_nodes_for_table(self, nodes, table_name):
    """Return all nodes that know about a given table."""
    active_nodes = []
    with By(f"querying all nodes for table {table_name}"):
        for node in nodes:
            r = node.query(
                f"SELECT table from system.replicas where table='{table_name}' FORMAT TSV"
            )
            if table_name == r.output.strip():
                active_nodes.append(node)

    return active_nodes


@TestStep
def get_random_table_name(self):
    return random.choice(self.context.table_names)


@TestStep
def get_random_table_names(self, choices: int, replacement=False):
    if replacement:
        return random.choices(self.context.table_names, k=choices)
    else:
        tables = self.context.table_names.copy()
        random.shuffle(tables)
        return tables[:choices]


@TestStep(Given)
def get_random_node_for_table(self, table_name):
    return random.choice(
        get_nodes_for_table(nodes=self.context.ch_nodes, table_name=table_name)
    )


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
        else f"{cluster_prefix}_env_arm64_default"
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


@TestStep(When)
def wait_for_mutations_to_finish(self, node, timeout=60, delay=5, command_like=None):
    """Wait for all pending mutations to complete."""
    query = "SELECT * FROM system.mutations WHERE is_done=0"
    if command_like:
        query += f" AND command LIKE '%{command_like}%'"

    query += " FORMAT Vertical"

    start_time = time.time()

    with By("querying system.mutations until all are done"):
        while time.time() - start_time < timeout:
            r = node.query(query, no_checks=True)
            if r.output == "":
                return

            time.sleep(delay)

        assert r.output == "", error("mutations did not finish in time")


@TestStep(Finally)
def log_failing_mutations(self, nodes=None):
    """Log failing mutations."""
    if not nodes:
        nodes = self.context.ch_nodes

    for node in nodes:
        with By("querying system.mutations"):
            r = node.query(
                "SELECT * FROM system.mutations WHERE is_done=0 FORMAT Vertical",
                no_checks=True,
            )
            if r.output.strip() == "":
                continue

            note(f"Pending mutations on {node.name}:\n{r.output.strip()}")

        with And("double checking the failed mutations"):
            r = node.query(
                "SELECT latest_failed_part, table, latest_fail_reason FROM system.mutations WHERE is_done=0 FORMAT JSONCompactColumns",
                no_checks=True,
            )
            for part, table, fail_reason in zip(*json.loads(r.output)):
                if fail_reason == "":
                    continue

                node.query(
                    f"SHOW CREATE TABLE {table} INTO OUTFILE '/var/log/clickhouse-server/show_create_{table}.txt'"
                )
                r = node.query(
                    f"SELECT * FROM system.parts WHERE name='{part}' and table='{table}' FORMAT Vertical",
                    no_checks=True,
                )
                if r.output.strip():
                    note(f"State of {part}:\n{r.output.strip()}")

                if "Not found column" in fail_reason:
                    column = re.search(r"column (.+):", fail_reason).group(1)
                    r = node.query(
                        f"SELECT * FROM system.parts_columns WHERE name='{part}' and table='{table}' and column='{column}' FORMAT Vertical",
                        no_checks=True,
                    )
                    if r.output.strip():
                        note(f"State of {column}:\n{r.output.strip()}")
