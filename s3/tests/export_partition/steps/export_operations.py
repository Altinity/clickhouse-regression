from testflows.core import *
from .export_status import wait_for_export_to_complete


@TestStep(When)
def get_partitions(self, table_name, node):
    """Get all partitions for a table on a given node."""

    output = node.query(
        f"SELECT DISTINCT partition_id FROM system.parts WHERE table = '{table_name}'",
        exitcode=0,
        steps=True,
    ).output
    return sorted([row.strip() for row in output.splitlines()])


@TestStep(When)
def export_partitions(
    self,
    source_table,
    destination_table,
    node,
    partitions=None,
    exitcode=0,
    settings=None,
    inline_settings=True,
    retry_times=60,
    force_export=False,
    check_export=True,
):
    """Export partitions from a source table to a destination table on the same node. If partitions are not provided, all partitions will be exported."""

    if partitions is None:
        partitions = get_partitions(table_name=source_table, node=node)

    if inline_settings:
        inline_settings = self.context.default_settings

    if force_export:
        inline_settings.append(("export_merge_tree_partition_force_export", 1))

    no_checks = exitcode != 0

    output = []
    with By(f"running EXPORT PARTITION for {source_table} partitions"):
        for partition in partitions:
            for attempt in retries(count=retry_times, delay=5):
                with attempt:
                    output.append(
                        node.query(
                            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition}' TO TABLE {destination_table}",
                            exitcode=exitcode,
                            no_checks=no_checks,
                            steps=True,
                            settings=settings,
                            inline_settings=inline_settings,
                        )
                    )
                    if check_export:
                        wait_for_export_to_complete(
                            partition_id=partition, source_table=source_table, node=node
                        )

    return output


@TestStep(When)
def kill_export_partition(
    self,
    partition_id,
    source_table,
    destination_table,
    node=None,
    exitcode=0,
):
    """Kill an export partition operation.

    Args:
        partition_id: The partition ID to kill the export for
        source_table: The source table name
        destination_table: The destination table name
        node: The node to execute the query on (defaults to context.node)
        exitcode: Expected exit code (default: 0)
    """
    if node is None:
        node = self.context.node

    no_checks = exitcode != 0

    with By(
        f"killing EXPORT PARTITION for partition_id='{partition_id}', "
        f"source_table='{source_table}', destination_table='{destination_table}'"
    ):
        result = node.query(
            f"KILL EXPORT PARTITION WHERE partition_id = '{partition_id}' "
            f"AND source_table = '{source_table}' "
            f"AND destination_table = '{destination_table}'",
            exitcode=exitcode,
            no_checks=no_checks,
            steps=True,
        )

    return result
