"""Host-side object storage helpers for the deletion-vectors suite.

All Spark-written tables live under ``s3://warehouse/<namespace>/<table>/``
on the MinIO service. From the test host MinIO is reachable at
``http://localhost:9002`` while ClickHouse nodes reach it in-network at
``http://minio:9000``. These helpers use boto3 against the host endpoint to
inspect and mutate the raw table objects (Puffin files, Avro manifests,
metadata JSON) that the corruption harness rewrites.
"""

import json

import boto3

from testflows.core import *

S3_HOST_ENDPOINT = "http://localhost:9002"
S3_NETWORK_ENDPOINT = "http://minio:9000"
WAREHOUSE_BUCKET = "warehouse"


def s3_client(test=None):
    """Cached boto3 client against the host-side MinIO endpoint using the
    suite's MinIO root credentials (set in feature.py context)."""
    test = test or current()
    client = getattr(test.context, "dv_s3_client", None)
    if client is None:
        client = boto3.client(
            "s3",
            endpoint_url=S3_HOST_ENDPOINT,
            aws_access_key_id=test.context.minio_root_user,
            aws_secret_access_key=test.context.minio_root_password,
            region_name="us-east-1",
        )
        test.context.dv_s3_client = client
    return client


def table_prefix(namespace, table_name):
    """Bucket-relative prefix of a Spark-written table."""
    return f"{namespace}/{table_name}"


def key_from_uri(uri):
    """``s3://warehouse/ns/t/...`` or ``ns/t/...`` → bucket-relative key."""
    if uri.startswith("s3://") or uri.startswith("s3a://"):
        return uri.split("://", 1)[1].split("/", 1)[1]
    return uri.lstrip("/")


def list_keys(prefix):
    """List every object key under *prefix* in the warehouse bucket."""
    keys = []
    paginator = s3_client().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=WAREHOUSE_BUCKET, Prefix=prefix):
        keys.extend(item["Key"] for item in page.get("Contents", []))
    return keys


def get_object_bytes(key):
    """Download an object and return its bytes."""
    response = s3_client().get_object(Bucket=WAREHOUSE_BUCKET, Key=key_from_uri(key))
    return response["Body"].read()


def put_object_bytes(key, data):
    """Upload bytes to an object key (replacing existing content)."""
    s3_client().put_object(Bucket=WAREHOUSE_BUCKET, Key=key_from_uri(key), Body=data)


def object_size(key):
    """Size of an object in bytes."""
    response = s3_client().head_object(Bucket=WAREHOUSE_BUCKET, Key=key_from_uri(key))
    return response["ContentLength"]


def delete_prefix(prefix):
    """Delete every object under *prefix* (suite teardown of generated
    tables)."""
    keys = list_keys(prefix)
    client = s3_client()
    for start in range(0, len(keys), 1000):
        client.delete_objects(
            Bucket=WAREHOUSE_BUCKET,
            Delete={
                "Objects": [{"Key": key} for key in keys[start : start + 1000]],
                "Quiet": True,
            },
        )
    return len(keys)


def object_inventory(prefix):
    """{key: etag} of every object under *prefix* — used to prove a set of
    ClickHouse operations modified nothing (read-only requirement)."""
    inventory = {}
    paginator = s3_client().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=WAREHOUSE_BUCKET, Prefix=prefix):
        for item in page.get("Contents", []):
            inventory[item["Key"]] = item["ETag"]
    return inventory


def find_puffin_keys(namespace, table_name):
    """All ``*.puffin`` object keys of a table."""
    return [
        key
        for key in list_keys(table_prefix(namespace, table_name))
        if key.endswith(".puffin")
    ]


@TestStep(Then)
def assert_puffin_exists(self, namespace, table_name, min_count=1):
    """Verify that the writer really produced deletion vectors: without
    ``format-version=3`` + merge-on-read modes a writer silently falls back
    to copy-on-write and the test would exercise nothing."""
    keys = find_puffin_keys(namespace, table_name)
    assert len(keys) >= min_count, (
        f"expected at least {min_count} Puffin file(s) under "
        f"{table_prefix(namespace, table_name)}, found {keys}"
    )
    return keys


def latest_metadata_key(namespace, table_name):
    """Key of the newest ``*.metadata.json`` of a table (highest version)."""
    keys = [
        key
        for key in list_keys(f"{table_prefix(namespace, table_name)}/metadata/")
        if key.endswith(".metadata.json")
    ]
    assert keys, f"no metadata.json found for {namespace}.{table_name}"

    def version(key):
        # metadata files are named like 00003-<uuid>.metadata.json
        name = key.rsplit("/", 1)[-1]
        try:
            return int(name.split("-", 1)[0])
        except ValueError:
            return -1

    return max(keys, key=version)


def read_table_metadata(namespace, table_name):
    """Parse the newest table metadata JSON into a dict."""
    return json.loads(get_object_bytes(latest_metadata_key(namespace, table_name)))


def get_snapshots(namespace, table_name):
    """Snapshots of the table ordered by commit time.

    Returns a list of dicts with ``snapshot-id``, ``timestamp-ms``,
    ``sequence-number`` and ``summary`` keys (as in the metadata JSON).
    """
    metadata = read_table_metadata(namespace, table_name)
    return sorted(
        metadata.get("snapshots", []), key=lambda snapshot: snapshot["timestamp-ms"]
    )


def current_snapshot(namespace, table_name):
    """The current snapshot dict of the table."""
    metadata = read_table_metadata(namespace, table_name)
    current_id = metadata["current-snapshot-id"]
    for snapshot in metadata["snapshots"]:
        if snapshot["snapshot-id"] == current_id:
            return snapshot
    raise AssertionError(f"current snapshot {current_id} not found in metadata")


def manifest_list_key(namespace, table_name, snapshot=None):
    """Bucket-relative key of the manifest list of a snapshot
    (current snapshot when not given)."""
    if snapshot is None:
        snapshot = current_snapshot(namespace, table_name)
    return key_from_uri(snapshot["manifest-list"])
