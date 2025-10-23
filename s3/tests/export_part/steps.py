import json

from testflows.core import *
from helpers.common import getuid
from helpers.tables import *
from s3.tests.common import temporary_bucket_path


@TestStep(Given)
def create_source_and_destination_tables(self, engine=None, columns=None, partition_by=None, order_by=None, node=None, cluster=None, stop_merges=True):
    """Create source and destination tables."""

    create_temp_bucket()
    source = create_source_table(engine=engine, columns=columns, partition_by=partition_by, order_by=order_by, node=node, cluster=cluster)
    destination = create_destination_table(source=source)
    if stop_merges:
        source.stop_merges()
    
    return source, destination


@TestStep(Given)
def create_temp_bucket(self, uri=None, bucket_prefix=None):
    """Create temporary s3 bucket."""

    if uri is None:
        uri = self.context.uri_base
        
    if bucket_prefix is None:
        bucket_prefix = self.context.bucket_prefix

    temp_s3_path = temporary_bucket_path(
        bucket_prefix=f"{bucket_prefix}/export_part"
    )

    self.context.uri = f"{uri}export_part/{temp_s3_path}/"
    self.context.bucket_path = f"{bucket_prefix}/export_part/{temp_s3_path}"


@TestStep(When)
def export_events(self, node=None):
    """Get the number of successful parts exports from the system.events table."""

    if node is None:
        node = self.context.node

    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%Export%%' FORMAT JSONEachRow",
        exitcode=0,
    ).output
    return {
        row["name"]: int(row["value"])
        for row in [json.loads(row) for row in output.splitlines()]
    }


@TestStep(When)
def export_part(self, parts, source, destination, exitcode=0, node=None):
    """Alter export of parts."""

    if node is None:
        node = self.context.node

    no_checks = exitcode != 0
    results = []

    # we should be able to set the settings here instead of using the SET query, but this is a quick workaround for the bug
    for part in parts:
        results.append(node.query(
            f"SET allow_experimental_export_merge_tree_part = 1; ALTER TABLE {source.name} EXPORT PART '{part}' TO TABLE {destination.name}",
            # settings=[("allow_experimental_export_merge_tree_part", 1)],
            exitcode=exitcode,
            no_checks=no_checks
        ))

    return results


@TestStep(When)
def create_source_table(self, engine=None, columns=None, partition_by=None, order_by=None, node=None, cluster=None):
    """Create a source table."""

    if engine is None:
        engine = "MergeTree"
    if columns is None:
        columns = [
            Column(name="p", datatype=UInt16()),
            Column(name="i", datatype=UInt64()),
        ]
    if partition_by is None:
        partition_by = columns[0].name
    if order_by is None:
        order_by = "tuple()"
    if cluster is None:
        cluster = "one_shard_cluster"

    source = create_table(
        name="source_table_" + getuid(),
        engine=engine,
        columns=columns,
        partition_by=partition_by,
        order_by=order_by,
        cluster=cluster,
        node=node,
    )

    return source


@TestStep(When)
def create_destination_table(self, source, engine=None):
    """Create a destination table."""
    
    name = "destination_table_" + getuid()
    
    if engine is None:
        engine = f"""
        S3(
            '{self.context.uri}',
            '{self.context.access_key_id}',
            '{self.context.secret_access_key}',
            filename='{name}',
            format='Parquet',
            compression='auto',
            partition_strategy='hive'
        )
    """

    destination = create_table(
        name=name,
        columns=source.columns,
        partition_by=source.partition_by,
        engine=engine,
    )

    return destination
