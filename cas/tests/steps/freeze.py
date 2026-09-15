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
