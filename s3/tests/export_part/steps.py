import json

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.common import temporary_bucket_path


def default_columns(simple=True, partition_key_type="Int8"):
    columns = [
        {"name": "p", "type": partition_key_type},
        {"name": "i", "type": "UInt64"},
        {"name": "Path", "type": "String"},
        {"name": "Time", "type": "DateTime"},
        {"name": "Value", "type": "Float64"},
        {"name": "Timestamp", "type": "Int64"},
    ]

    if simple:
        return columns[:2]
    else:
        return columns


@TestStep(Given)
def create_temp_bucket(self):
    """Create temporary S3 bucket."""

    temp_s3_path = temporary_bucket_path(
        bucket_prefix=f"{self.context.bucket_prefix}/export_part"
    )

    self.context.uri = f"{self.context.uri_base}export_part/{temp_s3_path}/"


@TestStep(Given)
def create_s3_table(
    self,
    table_name,
    cluster=None,
    create_new_bucket=False,
    columns=None,
):
    """Create a destination S3 table."""

    if create_new_bucket:
        create_temp_bucket()

    if columns is None:
        columns = default_columns(simple=True)

    table_name = f"{table_name}_{getuid()}"
    engine = f"""
        S3(
            '{self.context.uri}',
            '{self.context.access_key_id}',
            '{self.context.secret_access_key}',
            filename='{table_name}',
            format='Parquet',
            compression='auto',
            partition_strategy='hive'
        )
    """

    create_table(
        table_name=table_name,
        columns=columns,
        partition_by="p",
        engine=engine,
        cluster=cluster,
    )

    return table_name


@TestStep(When)
def get_parts(self, table_name, node):
    """Get all parts for a table on a given node."""

    output = node.query(
        f"SELECT name FROM system.parts WHERE table = '{table_name}'", exitcode=0
    ).output
    return [row.strip() for row in output.splitlines()]


@TestStep(When)
def export_parts(self, source_table, destination_table, node, parts=None, exitcode=0, explicit_set=True):
    """Export parts from a source table to a destination table on the same node. If parts are not provided, all parts will be exported."""

    if parts is None:
        parts = get_parts(table_name=source_table, node=node)

    no_checks = exitcode != 0

    output = []

    for part in parts:
        if explicit_set:
            output.append(node.query(
                f"SET allow_experimental_export_merge_tree_part = 1; ALTER TABLE {source_table} EXPORT PART '{part}' TO TABLE {destination_table}",
                exitcode=exitcode,
                no_checks=no_checks,
            ))
        else:
            output.append(node.query(
                f"ALTER TABLE {source_table} EXPORT PART '{part}' TO TABLE {destination_table}",
                settings=[("allow_experimental_export_merge_tree_part", 1)],
                exitcode=exitcode,
                no_checks=no_checks,
            ))

    return output


# TODO find the simplest way to parse the output
@TestStep(When)
def get_export_events(self, node):
    """Get the export data from the system.events table of a given node."""

    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%Export%%' FORMAT JSONEachRow",
        exitcode=0,
    ).output
    # return {row.name: int(row.value) for row in json.loads(output)}
    # return [json.loads(row) for row in output.splitlines()]
    return output


@TestStep(Then)
def source_matches_destination(
    self, source_table, destination_table, source_node, destination_node
):
    """Check that source and destination table data matches."""

    source_data = select_all_ordered(source_table, source_node)
    destination_data = select_all_ordered(destination_table, destination_node)
    assert source_data == destination_data, error()
