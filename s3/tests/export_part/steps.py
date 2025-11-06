import json

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
from helpers.create import *
from helpers.queries import *
from s3.tests.common import temporary_bucket_path


def default_columns(simple=True, partition_key_type="UInt8"):
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


def valid_partition_key_types_columns():
    return [
        {"name": "int8", "type": "Int8"},
        {"name": "int16", "type": "Int16"},
        {"name": "int32", "type": "Int32"},
        {"name": "int64", "type": "Int64"},
        {"name": "uint8", "type": "UInt8"},
        {"name": "uint16", "type": "UInt16"},
        {"name": "uint32", "type": "UInt32"},
        {"name": "uint64", "type": "UInt64"},
        {"name": "date", "type": "Date"},
        {"name": "date32", "type": "Date32"},
        {"name": "datetime", "type": "DateTime"},
        {"name": "datetime64", "type": "DateTime64"},
        {"name": "string", "type": "String"},
        {"name": "fixedstring", "type": "FixedString(10)"},
    ]


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
    partition_by="p",
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
        partition_by=partition_by,
        engine=engine,
        cluster=cluster,
    )

    return table_name


@TestStep(When)
def get_parts(self, table_name, node):
    """Get all parts for a table on a given node."""

    output = node.query(
        f"SELECT name FROM system.parts WHERE table = '{table_name}'",
        exitcode=0,
        steps=True,
    ).output
    return [row.strip() for row in output.splitlines()]


@TestStep(When)
def export_parts(
    self,
    source_table,
    destination_table,
    node,
    parts=None,
    exitcode=0,
    settings=None,
    inline_settings=True
):
    """Export parts from a source table to a destination table on the same node. If parts are not provided, all parts will be exported."""

    if parts is None:
        parts = get_parts(table_name=source_table, node=node)

    if inline_settings is True:
        inline_settings = self.context.default_settings
    
    no_checks = exitcode != 0
    output = []
 
    for part in parts:
        output.append(
            node.query(
                f"ALTER TABLE {source_table} EXPORT PART '{part}' TO TABLE {destination_table}",
                exitcode=exitcode,
                no_checks=no_checks,
                steps=True,
                settings=settings,
                inline_settings=inline_settings,
            )
        )

    return output


@TestStep(When)
def get_export_events(self, node):
    """Get the export data from the system.events table of a given node."""

    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%Export%%' FORMAT JSONEachRow",
        exitcode=0,
        steps=True,
    ).output

    events = {}
    for line in output.strip().splitlines():
        event = json.loads(line)
        events[event["name"]] = int(event["value"])

    if "PartsExportFailures" not in events:
        events["PartsExportFailures"] = 0
    if "PartsExports" not in events:
        events["PartsExports"] = 0
    if "PartsExportDuplicated" not in events:
        events["PartsExportDuplicated"] = 0

    return events


@TestStep(When)
def drop_column(self, node, table_name, column_name):
    """Drop a column from a table."""

    node.query(
        f"ALTER TABLE {table_name} DROP COLUMN {column_name}", exitcode=0, steps=True
    )


@TestStep(Then)
def source_matches_destination(
    self, source_table, destination_table, source_node=None, destination_node=None
):
    """Check that source and destination table data matches."""

    if source_node is None:
        source_node = self.context.node
    if destination_node is None:
        destination_node = self.context.node

    source_data = select_all_ordered(table_name=source_table, node=source_node)
    destination_data = select_all_ordered(
        table_name=destination_table, node=destination_node
    )
    assert source_data == destination_data, error()
