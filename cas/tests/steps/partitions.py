"""Partition ALTER helpers for CAS scenarios."""

from testflows.core import *


@TestStep(When)
@Name("attach partition from another table")
def attach_partition_from(self, destination, source, partition, node=None, **kwargs):
    """ATTACH PARTITION FROM ``source`` into ``destination``."""
    if node is None:
        node = self.context.node
    return node.query(
        f"ALTER TABLE {destination} ATTACH PARTITION {partition} FROM {source}",
        **kwargs,
    )


@TestStep(When)
@Name("replace partition from another table")
def replace_partition_from(self, destination, source, partition, node=None, **kwargs):
    """REPLACE PARTITION on ``destination`` from ``source``."""
    if node is None:
        node = self.context.node
    return node.query(
        f"ALTER TABLE {destination} REPLACE PARTITION {partition} FROM {source}",
        **kwargs,
    )


@TestStep(When)
@Name("move partition to another table")
def move_partition_to_table(self, source, destination, partition, node=None):
    """MOVE PARTITION from ``source`` to ``destination``."""
    if node is None:
        node = self.context.node
    node.query(
        f"ALTER TABLE {source} MOVE PARTITION {partition} TO TABLE {destination}"
    )


@TestStep(When)
@Name("detach partition")
def detach_partition(self, table_name, partition, node=None):
    """DETACH PARTITION on ``table_name``."""
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {table_name} DETACH PARTITION {partition}")


@TestStep(When)
@Name("attach partition")
def attach_partition(self, table_name, partition, node=None, **kwargs):
    """ATTACH a previously detached partition.

    ``partition`` may be ``ALL``.
    """
    if node is None:
        node = self.context.node
    return node.query(
        f"ALTER TABLE {table_name} ATTACH PARTITION {partition}", **kwargs
    )


@TestStep(When)
@Name("detach part")
def detach_part(self, table_name, part_name, node=None):
    """DETACH PART on ``table_name``."""
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {table_name} DETACH PART '{part_name}'")


@TestStep(When)
@Name("attach part")
def attach_part(self, table_name, part_name, node=None):
    """ATTACH a previously detached part."""
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {table_name} ATTACH PART '{part_name}'")


@TestStep(When)
@Name("drop detached partition")
def drop_detached_partition(self, table_name, partition, node=None):
    """DROP DETACHED PARTITION on ``table_name``.

    ``allow_drop_detached`` defaults to 0, so it has to be enabled per query.
    """
    if node is None:
        node = self.context.node
    node.query(
        f"ALTER TABLE {table_name} DROP DETACHED PARTITION {partition}",
        settings=[("allow_drop_detached", 1)],
    )


@TestStep(When)
@Name("drop partition")
def drop_partition(self, table_name, partition, node=None):
    """DROP PARTITION on ``table_name``.

    ``partition`` may be ``ALL``.
    """
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {table_name} DROP PARTITION {partition}")


@TestStep(When)
@Name("drop part")
def drop_part(self, table_name, part_name, node=None):
    """DROP PART on ``table_name``."""
    if node is None:
        node = self.context.node
    node.query(f"ALTER TABLE {table_name} DROP PART '{part_name}'")


@TestStep(When)
@Name("drop detached part")
def drop_detached_part(self, table_name, part_name, node=None):
    """DROP DETACHED PART on ``table_name``.

    ``allow_drop_detached`` defaults to 0, so it has to be enabled per query.
    """
    if node is None:
        node = self.context.node
    node.query(
        f"ALTER TABLE {table_name} DROP DETACHED PART '{part_name}'",
        settings=[("allow_drop_detached", 1)],
    )


@TestStep(When)
@Name("forget partition")
def forget_partition(self, table_name, partition, node=None, timeout=60):
    """FORGET PARTITION on a ReplicatedMergeTree table.

    The partition must be empty on every replica, and that emptiness propagates
    asynchronously after DROP PARTITION, so the command is retried.
    """
    if node is None:
        node = self.context.node
    for attempt in retries(timeout=timeout, delay=2):
        with attempt:
            node.query(f"ALTER TABLE {table_name} FORGET PARTITION {partition}")


@TestStep(When)
@Name("fetch part into detached")
def fetch_part(self, table_name, part_name, from_path, node=None):
    """FETCH PART from another replica's ZooKeeper path into detached."""
    if node is None:
        node = self.context.node
    node.query(
        f"ALTER TABLE {table_name} FETCH PART '{part_name}' FROM '{from_path}'"
    )


@TestStep(When)
@Name("fetch partition into detached")
def fetch_partition(self, table_name, partition, from_path, node=None):
    """FETCH PARTITION from another replica's ZooKeeper path into detached."""
    if node is None:
        node = self.context.node
    node.query(
        f"ALTER TABLE {table_name} FETCH PARTITION {partition} FROM '{from_path}'"
    )


@TestStep(When)
@Name("optimize table final")
def optimize_final(self, table_name, node=None):
    """OPTIMIZE TABLE ... FINAL."""
    if node is None:
        node = self.context.node
    node.query(f"OPTIMIZE TABLE {table_name} FINAL")


def _names(result):
    return [line.strip() for line in result.output.splitlines() if line.strip()]


def active_part_names(node, table_name, partition=None):
    """Return active part names for a table, optionally filtered by partition id."""
    where = f"database = currentDatabase() AND table = '{table_name}' AND active"
    if partition is not None:
        where += f" AND partition = '{partition}'"
    result = node.query(f"SELECT name FROM system.parts WHERE {where} ORDER BY name")
    return _names(result)


def detached_part_names(node, table_name, partition_id=None):
    """Return detached part names, optionally filtered by ``partition_id``."""
    where = f"database = currentDatabase() AND table = '{table_name}'"
    if partition_id is not None:
        where += f" AND partition_id = '{partition_id}'"
    result = node.query(
        f"SELECT name FROM system.detached_parts WHERE {where} ORDER BY name"
    )
    return _names(result)
