"""TestFlows steps for Delta tables in the suite Unity Catalog.

Create steps yield the object they made and remove it in a Finally block
when the scenario ends. RustFS credentials default to
``context.rustfs_access_key`` and ``context.rustfs_secret_key``.
"""

import json

import boto3
import pandas as pd
import requests
from deltalake import write_deltalake
from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid

UC_URL = "http://localhost:8085/api/2.1/unity-catalog"
UC_CATALOG = "unity"
UC_ENDPOINT = "http://unity-catalog:8080/api/2.1/unity-catalog"
S3_ENDPOINT = "http://localhost:9002"
STORAGE_ENDPOINT = "http://rustfs:9000/warehouse"
BUCKET = "warehouse"


class DeltaTable:
    """A Delta table written to the warehouse and registered in Unity."""

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    @property
    def location(self):
        return f"s3://{BUCKET}/delta/{self.namespace}/{self.name}"

    @property
    def prefix(self):
        return f"delta/{self.namespace}/{self.name}"

    @property
    def identifier(self):
        """Schema and table, quoted for clickhouse-client running in bash."""
        return f"\\`{self.namespace}.{self.name}\\`"

    @property
    def http_url(self):
        """Table URL on the RustFS service. ClickHouse uses this, not localhost."""
        return f"{STORAGE_ENDPOINT}/{self.prefix}/"


def column(
    name,
    type_name,
    type_text,
    delta_type,
    nullable=True,
    precision=0,
    scale=0,
    type_json=None,
):
    """Describe one Unity column.

    ``type_name`` is the Unity type (``STRING``, ``LONG``). ``type_text``
    is the SQL name (``string``, ``bigint``). ``delta_type`` is the type
    stored in ``type_json`` (``string``, ``long``, or a nested type object).
    ``nullable`` is copied into ``type_json``. Pass ``type_json`` only when
    the catalog name must differ from the log type.
    """
    spec = {
        "name": name,
        "type_name": type_name,
        "type_text": type_text,
        "delta_type": delta_type,
        "nullable": nullable,
        "precision": precision,
        "scale": scale,
    }
    if type_json is not None:
        spec["type_json"] = type_json
    return spec


def _node(self, node):
    return self.context.node if node is None else node


def _credentials(self, access_key, secret_key):
    if access_key is None:
        access_key = self.context.rustfs_access_key
    if secret_key is None:
        secret_key = self.context.rustfs_secret_key
    return access_key, secret_key


def _type_json(spec):
    if spec.get("type_json"):
        return spec["type_json"]
    payload = {
        "name": spec["name"],
        "type": spec["delta_type"],
        "nullable": spec.get("nullable", True),
        "metadata": {},
    }
    return json.dumps(payload, separators=(",", ":"))


def _unity_column(spec, position):
    nullable = spec.get("nullable", True)
    return {
        "name": spec["name"],
        "type_text": spec["type_text"],
        "type_json": _type_json(spec),
        "type_name": spec["type_name"],
        "type_precision": spec.get("precision", 0),
        "type_scale": spec.get("scale", 0),
        "position": position,
        "nullable": nullable,
    }


def _create_schema(name):
    response = requests.post(
        f"{UC_URL}/schemas",
        json={"name": name, "catalog_name": UC_CATALOG},
        timeout=30,
    )
    if response.status_code != 409:
        response.raise_for_status()


def _drop_schema(name):
    response = requests.delete(
        f"{UC_URL}/schemas/{UC_CATALOG}.{name}",
        params={"force": "true"},
        timeout=30,
    )
    if response.status_code not in (200, 404):
        response.raise_for_status()


def _drop_table(namespace, name):
    response = requests.delete(
        f"{UC_URL}/tables/{UC_CATALOG}.{namespace}.{name}",
        timeout=30,
    )
    if response.status_code not in (200, 404):
        response.raise_for_status()


def _s3(access_key, secret_key):
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def _delete_prefix(prefix, access_key, secret_key):
    client = _s3(access_key, secret_key)
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if objects:
            client.delete_objects(Bucket=BUCKET, Delete={"Objects": objects})


@TestStep(When)
def list_keys(self, prefix, access_key=None, secret_key=None):
    """Object keys under a warehouse prefix, in sorted order."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    if not prefix.endswith("/"):
        prefix = f"{prefix}/"
    client = _s3(access_key, secret_key)
    keys = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        keys.extend(item["Key"] for item in page.get("Contents", []))
    return sorted(keys)


@TestStep(When)
def put_object(self, key, body, access_key=None, secret_key=None):
    """Upload one object. ``body`` is bytes."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    _s3(access_key, secret_key).put_object(Bucket=BUCKET, Key=key, Body=body)


@TestStep(When)
def get_object(self, key, access_key=None, secret_key=None):
    """Download one object. The return value is bytes."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    response = _s3(access_key, secret_key).get_object(Bucket=BUCKET, Key=key)
    return response["Body"].read()


@TestStep(When)
def delete_prefix(self, prefix, access_key=None, secret_key=None):
    """Delete every object under a warehouse prefix."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    if not prefix.endswith("/"):
        prefix = f"{prefix}/"
    _delete_prefix(prefix, access_key, secret_key)


def _frame(columns, rows):
    frame = pd.DataFrame(list(rows), columns=[spec["name"] for spec in columns])
    for spec in columns:
        if spec["type_name"] == "LONG":
            frame[spec["name"]] = frame[spec["name"]].astype("int64")
    return frame


def _storage_options(access_key, secret_key):
    return {
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "AWS_ENDPOINT_URL": S3_ENDPOINT,
        "AWS_REGION": "us-east-1",
        "AWS_ALLOW_HTTP": "true",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        "AWS_EC2_METADATA_DISABLED": "true",
    }


def _write_table(
    table,
    columns,
    rows,
    access_key,
    secret_key,
    data=None,
    mode="overwrite",
    schema_mode=None,
):
    """Write ``data`` when it is set, otherwise a frame built from ``rows``."""
    if data is None:
        data = _frame(columns, rows)
    kwargs = {
        "mode": mode,
        "storage_options": _storage_options(access_key, secret_key),
    }
    if schema_mode is not None:
        kwargs["schema_mode"] = schema_mode
    write_deltalake(table.location, data, **kwargs)


def _register_table(table, columns):
    response = requests.post(
        f"{UC_URL}/tables",
        json={
            "name": table.name,
            "catalog_name": UC_CATALOG,
            "schema_name": table.namespace,
            "table_type": "EXTERNAL",
            "data_source_format": "DELTA",
            "storage_location": table.location,
            "columns": [
                _unity_column(spec, position)
                for position, spec in enumerate(columns)
            ],
        },
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f"Unity register failed: {response.status_code} {response.text}"
        )


@TestStep(Given)
def create_schema(self, name=None):
    """Create a Unity schema. Drop it when the scenario ends."""
    if name is None:
        name = f"dl_{getuid()}"

    try:
        _create_schema(name)
        yield name
    finally:
        with Finally(f"drop schema {name}"):
            _drop_schema(name)


@TestStep(Given)
def create_delta_table(
    self,
    columns,
    rows=None,
    namespace=None,
    name=None,
    access_key=None,
    secret_key=None,
    create_schema=True,
    register=True,
    data=None,
    mode="overwrite",
    schema_mode=None,
):
    """Write a Delta table. Register it in Unity unless ``register`` is false.

    Pass ``namespace`` from ``create_schema`` and ``create_schema=False``
    when several tables share a schema. Otherwise this step creates the
    schema and drops it with the table. A direct RustFS read passes
    ``register=False`` and ``create_schema=False``.

    ``rows`` builds a pandas frame. ``data`` is a pyarrow table and keeps
    the Arrow types in the Delta log. Pass one of the two.
    """
    if data is None and rows is None:
        raise ValueError("pass rows or data")
    access_key, secret_key = _credentials(self, access_key, secret_key)
    if namespace is None:
        namespace = f"dl_{getuid()}"
    if name is None:
        name = f"tbl_{getuid()}"

    table = DeltaTable(namespace, name)
    try:
        if create_schema:
            _create_schema(namespace)
        _write_table(
            table,
            columns,
            rows,
            access_key,
            secret_key,
            data=data,
            mode=mode,
            schema_mode=schema_mode,
        )
        if register:
            _register_table(table, columns)
        yield table
    finally:
        if register:
            with Finally(f"drop table {namespace}.{name}"):
                _drop_table(namespace, name)
        with Finally(f"delete files {table.prefix}"):
            _delete_prefix(f"{table.prefix}/", access_key, secret_key)
        if create_schema:
            with Finally(f"drop schema {namespace}"):
                _drop_schema(namespace)


@TestStep(Given)
def register_delta_table(self, table, columns):
    """Register an existing Delta path in Unity. Drop the catalog entry later."""
    try:
        _register_table(table, columns)
        yield table
    finally:
        with Finally(f"drop table {table.namespace}.{table.name}"):
            _drop_table(table.namespace, table.name)


@TestStep(When)
def commit_delta_table(
    self,
    table,
    data,
    mode="append",
    schema_mode=None,
    access_key=None,
    secret_key=None,
):
    """Write another commit to a table ``create_delta_table`` already created."""
    access_key, secret_key = _credentials(self, access_key, secret_key)
    _write_table(
        table,
        columns=None,
        rows=None,
        access_key=access_key,
        secret_key=secret_key,
        data=data,
        mode=mode,
        schema_mode=schema_mode,
    )


@TestStep(Given)
def create_database(
    self,
    unity_v2=False,
    name=None,
    node=None,
    access_key=None,
    secret_key=None,
):
    """Open the Unity catalog in ClickHouse. Drop the database when the scenario ends."""
    node = _node(self, node)
    access_key, secret_key = _credentials(self, access_key, secret_key)
    if name is None:
        name = f"delta_{getuid()}"

    try:
        node.query(
            "SET allow_database_unity_catalog=1; "
            f"CREATE DATABASE {name} "
            f"ENGINE = DataLakeCatalog('{UC_ENDPOINT}') "
            "SETTINGS "
            "catalog_type = 'unity', "
            f"use_unity_catalog_v2 = '{int(unity_v2)}', "
            f"warehouse = '{UC_CATALOG}', "
            "vended_credentials = 'false', "
            f"storage_endpoint = '{STORAGE_ENDPOINT}', "
            f"aws_access_key_id = '{access_key}', "
            f"aws_secret_access_key = '{secret_key}'"
        )
        yield name
    finally:
        with Finally(f"drop database {name}"):
            node.query(f"DROP DATABASE IF EXISTS {name}")


@TestStep(When)
def select_rows(self, database, table, columns, order_by=None, node=None):
    """Read columns from a registered Delta table."""
    node = _node(self, node)
    order = f" ORDER BY {order_by}" if order_by else ""
    selected = ", ".join(columns)
    return node.query(
        f"SELECT {selected} FROM {database}.{table.identifier}{order} "
        "FORMAT TabSeparated"
    )


@TestStep(Then)
def expect_delta_table(self, database, table, node=None):
    """Check that ClickHouse lists the table as DeltaLake at its storage path."""
    node = _node(self, node)
    listed = node.query(f"SHOW TABLES FROM {database}").output
    assert f"{table.namespace}.{table.name}" in listed, error(listed)

    show_create = node.query(f"SHOW CREATE TABLE {database}.{table.identifier}").output
    assert "DeltaLake" in show_create, error(show_create)
    assert table.prefix in show_create, error(show_create)


@TestStep(Then)
def expect_rows(self, database, table, expected, columns, order_by=None, node=None):
    """Check that a select returns these lines, in order."""
    node = _node(self, node)
    order = f" ORDER BY {order_by}" if order_by else ""
    selected = ", ".join(columns)
    result = node.query(
        f"SELECT {selected} FROM {database}.{table.identifier}{order} "
        "FORMAT TabSeparated"
    )
    assert result.output.splitlines() == list(expected), error(result.output)
