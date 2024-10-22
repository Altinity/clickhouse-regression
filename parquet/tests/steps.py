import json

from testflows.core import *
from alter.table.attach_partition.conditions import order_by
from helpers.common import getuid


@TestStep(Given)
def build_parquet_schema(
    name,
    schema_type,
    physical_type=None,
    logical_type=None,
    data=None,
    fields=None,
):
    """Build a Parquet schema."""

    groups = ["optionalGroup", "requiredGroup", "repeatedGroup"]

    if schema_type not in [
        "optional",
        "required",
        "repeated",
        "optionalGroup",
        "requiredGroup",
        "repeatedGroup",
    ]:
        raise ValueError(f"Invalid schema type: {schema_type}")

    entry = {
        "name": name,
        "schemaType": schema_type,
    }

    if schema_type not in groups and physical_type is not None:
        entry["physicalType"] = physical_type

    if logical_type:
        entry["logicalType"] = logical_type

    if data in groups:
        entry["data"] = data

    if schema_type in groups and fields is not None:
        entry["fields"] = fields

    return entry


@TestStep(Given)
def generate_parquet_json_definition(
    self,
    file_name,
    parquet_file_name,
    schema=None,
    writer_version=None,
    compression=None,
    row_group_size=None,
    page_size=None,
    encodings=None,
    bloom_filter=None,
):
    """Generate a Parquet JSON definition file."""

    if encodings is None:
        encodings = ["PLAIN"]
    if writer_version is None:
        writer_version = "1.0"
    if compression is None:
        compression = "SNAPPY"
    if row_group_size is None:
        row_group_size = 134217728
    if page_size is None:
        page_size = 1048576
    if bloom_filter is None:
        bloom_filter = "none"

    file_definition = {
        "fileName": parquet_file_name + getuid() + ".parquet",
        "options": {
            "writerVersion": writer_version,
            "compression": compression,
            "rowGroupSize": row_group_size,
            "pageSize": page_size,
            "encodings": encodings,
            "bloomFilter": bloom_filter,
        },
        "schema": schema,
    }

    with open(file_name, "w") as json_file:
        json.dump(file_definition, json_file, indent=2)

    return file_name


@TestStep(Given)
def parquetify(
    self,
    json_file,
    output_path,
    node=None,
):
    """Execute a Parquetify program for generating a Parquet file based on a json file."""
    if node is None:
        node = self.context.cluster.node("parquetify")

    node.command(f"parquetify --json {json_file} --output {output_path}")


@TestStep(Given)
def create_parquet_files(
    self,
    output_path,
    file_name,
    parquet_file_name,
    schema,
    writer_version=None,
    compression=None,
    row_group_size=None,
    page_size=None,
    encodings=None,
    bloom_filter=None,
):
    """Create Parquet files with different types and bloom filters."""
    with By("creating JSON file for the parquetify"):
        json_file = generate_parquet_json_definition(
            file_name=file_name,
            parquet_file_name=parquet_file_name,
            schema=schema,
            writer_version=writer_version,
            compression=compression,
            row_group_size=row_group_size,
            page_size=page_size,
            encodings=encodings,
            bloom_filter=bloom_filter,
        )

    with And("generating parquet file"):
        parquetify(json_file=json_file, output_path=output_path)


@TestStep(Given)
def select_from_parquet(
    self,
    file_name,
    node=None,
    file_type=None,
    statement="*",
    condition=False,
    settings=None,
    format=None,
    order_by=False,
):
    """Select from a parquet file."""
    if node is None:
        node = self.context.node

    if file_type is None:
        file_type = ", Parquet"

    with By(f"selecting the data from the parquet file {file_name}"):
        r = rf"SELECT {statement} FROM file('{file_name}'{file_type})"

        if condition:
            r += rf" {condition}"

        if order_by:
            r += rf" ORDER BY {order_by}"

        if format is None:
            format = "TabSeparated"

        r += rf" FORMAT {format}"

        if settings is not None:
            r += rf" SETTINGS {settings}"

        output = node.query(r)

    return output


@TestStep(Given)
def count_rows_in_parquet(self, file_name, node=None):
    """Count rows in a parquet file."""
    if node is None:
        node = self.context.node

    with Given(f"I count the rows in the parquet file {file_name}"):
        output = select_from_parquet(
            file_name=file_name, node=node, statement="count(*)"
        )

    return int(output.output.strip())
