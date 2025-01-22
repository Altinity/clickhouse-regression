import json
import random
import base64
import datetime
import json

from decimal import Decimal
from inspect import stack

from testflows.core import *
from alter.table.attach_partition.conditions import order_by
from helpers.common import getuid
from parquet.tests.common import generate_values
from parquet.tests.steps.bloom_filter import (
    parquet_file_name,
    row_group_size,
    page_size,
    encodings,
    bloom_filter,
    options,
    schema,
    writer_version,
    compression,
    schema_type,
    physical_types,
    logical_types,
)


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder:
        - Supports DateTime serialization.
        - Supports Date serialization.
        - Supports bytes serialization.
        - Supports Decimal serialization.
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                return base64.b64encode(obj).decode("ascii")
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


@TestStep(Given)
def save_json_definition(self, path, file_definition):
    """Save the JSON file definition."""
    with open(path, "w") as json_file:
        json.dump(file_definition, json_file, cls=JSONEncoder, indent=2)


@TestStep(Given)
def build_parquet_schema(
    self,
    name,
    schema_type,
    physical_type=None,
    logical_type=None,
    data=None,
    random_data=False,
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

    if data is not None and schema_type not in groups:
        if random_data:
            if logical_type is None:
                entry["data"] = generate_values(physical_type, random.randint(1, 100))
            else:
                entry["data"] = generate_values(logical_type, random.randint(1, 100))
        else:
            entry["data"] = data

    if schema_type in groups and fields is not None:
        entry["fields"] = fields

    return entry


@TestStep(Given)
def parquetify(self, json_file, output_path, node=None, no_checks=False):
    """Execute a Parquetify program for generating a Parquet file based on a json file."""
    if node is None:
        node = self.context.cluster.node("parquetify")

    return node.command(
        f"parquetify --json {json_file} --output {output_path}", no_checks=no_checks
    )


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
    no_checks=False,
    limit=False,
    stack_trace=None,
    key_column=None,
):
    """Select from a parquet file."""
    if node is None:
        node = self.context.node

    if file_type is None:
        file_type = "Parquet"

    with By(f"selecting the data from the parquet file {file_name}"):
        r = rf"SELECT {statement} FROM file('{file_name}', {file_type}"

        if key_column is not None:
            r += rf", '{key_column}')"
        else:
            r += ")"

        if condition:
            r += rf" {condition}"

        if order_by:
            r += rf" ORDER BY {order_by}"

        if format is None:
            format = "TabSeparated"

        if limit:
            r += f" LIMIT {limit}"

        r += rf" FORMAT {format}"

        if settings is not None:
            r += rf" SETTINGS {settings}"

        if stack_trace is not None:
            output = node.query(r, no_checks=no_checks, stack_trace=stack_trace)
        else:
            output = node.query(r, no_checks=no_checks)

    return output


@TestStep(When)
def get_parquet_structure(self, file_name, node=None):
    """Get the structure of a parquet file."""
    if node is None:
        node = self.context.node

    output = node.query(
        f"DESCRIBE TABLE file('{file_name}', Parquet) FORMAT TabSeparated"
    )

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


def rows_read(json_data, client=True):
    """Get the number of rows read from the json data."""
    if client:
        data = json_data[-1]
    else:
        data = int(json.loads(json_data)["statistics"]["rows_read"])
    return data


@TestStep(Given)
def create_parquet_json_definition(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    parquet_file,
    data,
    row_group_size_bytes=256,
    page_size_bytes=1024,
    enable_bloom_filter=False,
    column_name=None,
):
    """Create the JSON definition for the parquet file."""
    file_definition = {}
    option_list = {}
    schema_values = {}

    file_definition.update(parquet_file_name(filename=f"{parquet_file}"))
    option_list.update(writer_version())
    option_list.update(compression_value())
    option_list.update(row_group_size(size=row_group_size_bytes))
    option_list.update(page_size(size=page_size_bytes))
    option_list.update(encodings())

    if enable_bloom_filter:
        option_list.update(bloom_filter())

    file_definition.update(options(options=option_list))

    if column_name is None:
        column_name = (
            logical_type()["logicalType"].lower()
            if logical_type()["logicalType"] != "NONE"
            else physical_type()["physicalType"].lower()
        )

    schema_values.update(
        schema_type(
            name=column_name,
            physical_type=physical_type(),
            logical_type=logical_type(),
            data=data,
        )
    )
    file_definition.update(schema(schema=schema_values))

    return file_definition


@TestStep(Given)
def create_and_save_parquet_json_definition(
    self,
    path,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    parquet_file,
    data,
    row_group_size_bytes=256,
    page_size_bytes=1024,
    enable_bloom_filter=False,
):
    """Create a JSON definition for a parquet schema and save it as a real JSON file."""

    with By(f"Creating a JSON definition for the parquet schema"):
        file_definition = create_parquet_json_definition(
            schema_type=schema_type,
            writer_version=writer_version,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=compression_value,
            parquet_file=parquet_file,
            data=data,
            row_group_size_bytes=row_group_size_bytes,
            page_size_bytes=page_size_bytes,
            enable_bloom_filter=enable_bloom_filter,
        )

    with And(f"Saving the JSON definition to {path}"):
        save_json_definition(path=path, file_definition=file_definition)

    return file_definition


@TestStep(Given)
def generate_parquet_file(self, json_file_path, output_path=None, no_checks=True):
    """Generate the parquet file from its JSON definition."""

    if output_path is None:
        output_path = self.context.parquet_output_path

    return parquetify(
        json_file=json_file_path,
        output_path=output_path,
        no_checks=no_checks,
    )
