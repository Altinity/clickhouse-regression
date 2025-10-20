import json

from testflows.core import *
from helpers.common import getuid
from helpers.tables import *
from s3.tests.common import temporary_bucket_path

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
def export_events(self):
    """Get the number of successful parts exports from the system.events table."""
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
def export_part(self, parts, source, destination, exitcode=0):
    """Alter export of parts."""
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
def create_source_table(
    self, columns=None, partition_by=None, order_by=None, engine=None
):
    """Create a source table."""

    if columns is None:
        columns = [
            Column(name="p", datatype=UInt16()),
            Column(name="i", datatype=UInt64()),
        ]
    if partition_by is None:
        partition_by = columns[0].name
    if order_by is None:
        order_by = "tuple()"
    if engine is None:
        engine = "MergeTree"

    source = create_table(
        name="source_table_" + getuid(),
        columns=columns,
        partition_by=partition_by,
        order_by=order_by,
        engine=engine,
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
