from testflows.core import *


@TestStep
def get_export_field(
    self,
    field_name,
    source_table,
    timeout=30,
    delay=3,
    node=None,
    where_clause=None,
    select_clause=None,
):
    """Get a field value from system.replicated_partition_exports table."""

    if node is None:
        node = self.context.node

    if select_clause is None:
        select_clause = field_name

    base_where = f"source_table = '{source_table}'"
    if where_clause:
        where_clause = f"{base_where} AND {where_clause}"
    else:
        where_clause = base_where

    query = f"SELECT {select_clause} FROM system.replicated_partition_exports WHERE {where_clause}"

    for attempt in retries(timeout=timeout, delay=delay):
        with attempt:
            result = node.query(
                query,
                exitcode=0,
                no_checks=True,
            )

    return result


@TestStep
def get_source_database(self, source_table, timeout=30, delay=3, node=None):
    """Get source_database from system.replicated_partition_exports."""
    return get_export_field(
        field_name="source_database",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_destination_database(self, source_table, timeout=30, delay=3, node=None):
    """Get destination_database from system.replicated_partition_exports."""
    return get_export_field(
        field_name="destination_database",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_destination_table(self, source_table, timeout=30, delay=3, node=None):
    """Get destination_table from system.replicated_partition_exports."""
    return get_export_field(
        field_name="destination_table",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_create_time(self, source_table, timeout=30, delay=3, node=None):
    """Get create_time from system.replicated_partition_exports."""
    return get_export_field(
        field_name="create_time",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_partition_id(self, source_table, timeout=30, delay=3, node=None):
    """Get partition_id from system.replicated_partition_exports."""
    return get_export_field(
        field_name="partition_id",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_transaction_id(self, source_table, timeout=30, delay=3, node=None):
    """Get transaction_id from system.replicated_partition_exports."""
    return get_export_field(
        field_name="transaction_id",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_source_replica(self, source_table, timeout=30, delay=3, node=None):
    """Get source_replica from system.replicated_partition_exports."""
    return get_export_field(
        field_name="source_replica",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts(self, source_table, timeout=30, delay=3, node=None):
    """Get parts array from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts_count(self, source_table, timeout=30, delay=3, node=None):
    """Get parts_count from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts_count",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_parts_to_do(self, source_table, timeout=30, delay=3, node=None):
    """Get parts_to_do from system.replicated_partition_exports."""
    return get_export_field(
        field_name="parts_to_do",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_replica(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_replica from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_replica",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_last_exception(self, source_table, timeout=30, delay=3, node=None):
    """Get last_exception from system.replicated_partition_exports."""
    return get_export_field(
        field_name="last_exception",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_part(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_part from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_part",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )


@TestStep
def get_exception_count(self, source_table, timeout=30, delay=3, node=None):
    """Get exception_count from system.replicated_partition_exports."""
    return get_export_field(
        field_name="exception_count",
        source_table=source_table,
        timeout=timeout,
        delay=delay,
        node=node,
    )
