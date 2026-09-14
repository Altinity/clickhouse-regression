"""FREEZE / UNFREEZE helpers for CAS tables."""

from testflows.core import *


@TestStep(When)
@Name("freeze a table under a backup name")
def freeze_table(self, table_name, backup_name, node=None):
    """Freeze every partition of ``table_name`` as backup ``backup_name``."""
    if node is None:
        node = self.context.node

    node.query(f"ALTER TABLE {table_name} FREEZE WITH NAME '{backup_name}'")


@TestStep(When)
@Name("release a table backup name")
def unfreeze_table(self, table_name, backup_name, node=None, no_checks=False):
    """Release backup ``backup_name`` of ``table_name``.

    ``no_checks`` is for the local-disk control: UNFREEZE on a replica that
    never froze may error because that node's ``shadow/`` has nothing of that
    name, and the error itself is evidence that the backup is not shared.
    """
    if node is None:
        node = self.context.node

    return node.query(
        f"ALTER TABLE {table_name} UNFREEZE WITH NAME '{backup_name}'",
        no_checks=no_checks,
    )


SHADOW_ROOT = "/var/lib/clickhouse/shadow"


@TestStep(Then)
@Name("list the files of a local-disk freeze")
def local_backup_files(self, backup_name, node=None):
    """Return the files under ``/var/lib/clickhouse/shadow/<backup_name>``.

    On a local disk a freeze lives only on the node that ran it, so this list
    is empty on every other server.
    """
    if node is None:
        node = self.context.node

    listing = node.command(
        f"find {SHADOW_ROOT}/{backup_name} -type f 2>/dev/null || true",
        no_checks=True,
    )
    prefix = f"{SHADOW_ROOT}/{backup_name}/"

    return sorted(
        line.strip()
        for line in listing.output.splitlines()
        if line.strip().startswith(prefix)
    )


@TestStep(When)
@Name("run garbage collection on a CAS pool")
def collect_garbage(self, disk, nodes=None, rounds=4):
    """Run garbage collection on ``disk`` from every server mounting the pool.

    Reclamation is staged — a round condemns what it found unreachable and a
    later round deletes it — and only one server holds the collection lease at
    a time, so a single round on a single server proves nothing either way.
    """
    if nodes is None:
        nodes = self.context.nodes

    for _ in range(rounds):
        for node in nodes:
            node.query(f"SYSTEM CAS GC RUN '{disk}'")
