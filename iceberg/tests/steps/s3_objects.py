"""Host-side object storage helpers shared by the iceberg suites.

Tables written through the catalogs in ``iceberg/iceberg_env`` live in the
``warehouse`` bucket on MinIO. From the test host MinIO is reachable at
``http://localhost:9002``; ClickHouse nodes reach it in-network at
``http://minio:9000``. These helpers use boto3 against the host endpoint to
inspect raw table objects without going through ClickHouse, so a test can
prove what a statement did (or did not do) to storage independently of what
the server reported.

Credentials come from ``self.context.minio_root_user`` /
``self.context.minio_root_password`` (set by each feature's entry point) or
can be passed explicitly.
"""

import gzip
import json

import boto3

from testflows.core import *

S3_HOST_ENDPOINT = "http://localhost:9002"
S3_NETWORK_ENDPOINT = "http://minio:9000"
WAREHOUSE_BUCKET = "warehouse"

GZIP_MAGIC = b"\x1f\x8b"


def s3_client(test=None, access_key=None, secret_key=None, endpoint=S3_HOST_ENDPOINT):
    """Cached boto3 client against the host-side MinIO endpoint."""
    test = test or current()
    client = getattr(test.context, "iceberg_s3_client", None)
    if client is None:
        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key or test.context.minio_root_user,
            aws_secret_access_key=secret_key or test.context.minio_root_password,
            region_name="us-east-1",
        )
        test.context.iceberg_s3_client = client
    return client


def key_from_uri(uri, bucket=WAREHOUSE_BUCKET):
    """``s3://warehouse/ns/t/...``, ``s3a://...`` or ``ns/t/...`` → bucket-relative key.

    Raises if the URI names a different bucket, so an assertion never silently
    inspects the wrong place.
    """
    if uri.startswith("s3://") or uri.startswith("s3a://"):
        rest = uri.split("://", 1)[1]
        uri_bucket, _, key = rest.partition("/")
        assert (
            uri_bucket == bucket
        ), f"expected bucket {bucket}, got {uri_bucket} in {uri}"
        return key
    return uri.lstrip("/")


def prefix_from_uri(uri, bucket=WAREHOUSE_BUCKET):
    """Bucket-relative prefix (with trailing slash) for a table location URI."""
    return key_from_uri(uri, bucket=bucket).rstrip("/") + "/"


def list_keys(prefix, bucket=WAREHOUSE_BUCKET):
    """List every object key under *prefix*."""
    keys = []
    paginator = s3_client().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        keys.extend(item["Key"] for item in page.get("Contents", []))
    return keys


def object_inventory(prefix, bucket=WAREHOUSE_BUCKET):
    """``{key: (etag, size)}`` of every object under *prefix*.

    Two inventories compare equal exactly when the set of objects and their
    contents are unchanged, which is how the invariants prove that a
    statement modified nothing (or removed everything).
    """
    inventory = {}
    paginator = s3_client().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            inventory[item["Key"]] = (item["ETag"], item["Size"])
    return inventory


def object_exists(key, bucket=WAREHOUSE_BUCKET):
    """``True`` if the object exists (HEAD succeeds)."""
    try:
        s3_client().head_object(Bucket=bucket, Key=key_from_uri(key, bucket=bucket))
        return True
    except s3_client().exceptions.ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def get_object_bytes(key, bucket=WAREHOUSE_BUCKET):
    """Download an object and return its bytes."""
    response = s3_client().get_object(
        Bucket=bucket, Key=key_from_uri(key, bucket=bucket)
    )
    return response["Body"].read()


def put_object_bytes(key, data, bucket=WAREHOUSE_BUCKET):
    """Upload bytes to an object key (replacing existing content)."""
    s3_client().put_object(
        Bucket=bucket, Key=key_from_uri(key, bucket=bucket), Body=data
    )


def read_json_object(key, bucket=WAREHOUSE_BUCKET):
    """Download a JSON object, transparently decompressing gzip, and parse it.

    Iceberg metadata files may be written as ``v1.gz.metadata.json`` when
    ``iceberg_metadata_compression_method = 'gzip'``; the content, not the
    name, decides whether to decompress.
    """
    data = get_object_bytes(key, bucket=bucket)
    if data[:2] == GZIP_MAGIC:
        data = gzip.decompress(data)
    return json.loads(data)


def delete_prefix(prefix, bucket=WAREHOUSE_BUCKET):
    """Delete every object under *prefix*. Returns the number deleted."""
    keys = list_keys(prefix, bucket=bucket)
    client = s3_client()
    for start in range(0, len(keys), 1000):
        client.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [{"Key": key} for key in keys[start : start + 1000]],
                "Quiet": True,
            },
        )
    return len(keys)


def metadata_keys(inventory):
    """Keys of ``*.metadata.json`` objects in an inventory."""
    return sorted(k for k in inventory if k.endswith(".metadata.json"))
