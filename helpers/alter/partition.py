from testflows.core import *


@TestStep(Given)
def alter_table_drop_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Drop partition from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping partition from the table"):
        query = f"ALTER TABLE {table_name} DROP PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_drop_detached_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Drop detached partition from the table using alter."""
    if node is None:
        node = self.context.node

    with By("dropping detached partition from the table"):
        query = f"ALTER TABLE {table_name} DROP DETACHED PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_detach_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Detach partition from the table using alter."""
    if node is None:
        node = self.context.node

    with By("detaching partition from the table"):
        query = f"ALTER TABLE {table_name} DETACH PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_attach_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Attach partition to the table using alter."""
    if node is None:
        node = self.context.node

    with By("attaching partition to the table"):
        query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_attach_partition_from(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Attach partition from a backup to the table using alter."""
    if node is None:
        node = self.context.node

    with By("attaching partition from a backup to the table"):
        query = f"ALTER TABLE {table_name} ATTACH PARTITION {partition_name} FROM {path_to_backup}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_attach_detached_partition(
    self, table_name, partition_name, path_to_backup=None, node=None, **query_kwargs
):
    """Attach detached partition to the table using alter."""
    if node is None:
        node = self.context.node

    with By("attaching detached partition to the table"):
        query = f"ALTER TABLE {table_name} ATTACH DETACHED PARTITION {partition_name}"
        if path_to_backup:
            query += f" FROM '{path_to_backup}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_move_partition_to_table(
    self, table_name, partition_name, destination_table, node=None, **query_kwargs
):
    """Move partition to another table using alter."""
    if node is None:
        node = self.context.node

    with By("moving partition to another table"):
        query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO TABLE {destination_table}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_move_partition(
    self,
    table_name,
    partition_name,
    disk_name,
    node=None,
    disk="VOLUME",
    **query_kwargs,
):
    """Move partition to a different disk or volume using alter."""
    if node is None:
        node = self.context.node

    with By("moving partition to a different disk or volume"):
        query = f"ALTER TABLE {table_name} MOVE PARTITION {partition_name} TO {disk} '{disk_name}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_replace_partition(
    self, table_name, partition_name, source_table, node=None, **query_kwargs
):
    """Replace partition from a source table using alter."""
    if node is None:
        node = self.context.node

    with By("replacing partition from a source table to the destination table"):
        query = f"ALTER TABLE {table_name} REPLACE PARTITION {partition_name} FROM {source_table}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_fetch_partition(
    self, table_name, partition_name, path_to_backup, node=None, **query_kwargs
):
    """Fetch partition from a source table using alter."""
    if node is None:
        node = self.context.node

    with By("fetching partition from a source table"):
        query = f"ALTER TABLE {table_name} FETCH PARTITION {partition_name} FROM '{path_to_backup}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_freeze_partition(
    self, table_name, partition_name, node=None, **query_kwargs
):
    """Freeze partition for backup using alter."""
    if node is None:
        node = self.context.node

    with By("freezing partition for backup"):
        query = f"ALTER TABLE {table_name} FREEZE PARTITION {partition_name}"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_freeze_partition_with_name(
    self, table_name, backup_name, partition_name=None, node=None, **query_kwargs
):
    """Freeze partition with a name using alter."""
    if node is None:
        node = self.context.node

    partition = ""
    if partition_name:
        partition = f"PARTITION {partition_name} "

    with By("freezing partition with a name"):
        query = f"ALTER TABLE {table_name} FREEZE {partition}WITH NAME '{backup_name}'"
        node.query(query, **query_kwargs)


@TestStep(Given)
def alter_table_unfreeze_partition_with_name(
    self, table_name, backup_name, partition_name=None, node=None, **query_kwargs
):
    """Unfreeze partition with a name using alter."""
    if node is None:
        node = self.context.node

    partition = ""
    if partition_name:
        partition = f"PARTITION {partition_name} "

    with By("unfreezing partition with a name"):
        query = (
            f"ALTER TABLE {table_name} UNFREEZE {partition}WITH NAME '{backup_name}'"
        )
        node.query(query, **query_kwargs)

