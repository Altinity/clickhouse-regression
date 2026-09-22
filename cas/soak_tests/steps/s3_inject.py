"""Direct S3 access to the soak_tests RustFS pool. No cas.soak imports."""

import io
import json
import os

# Host-mapped RustFS port from soak_tests_env. Credentials default to helpers.argparser
# minio flags (minio_user/minio123), overridable so they match the live compose env.
_S3_ENDPOINT_DEFAULT = "http://localhost:9002"
_S3_BUCKET_DEFAULT = "warehouse"
_S3_KEY_DEFAULT = "minio_user"
_S3_SECRET_DEFAULT = "minio123"
POOL_PREFIX_DEFAULT = "soak_pool"
REF_LOG_SUFFIX = ".zst"
HUGE_SEQ = 0xFFFFFFFFFFFFFFFE
POOL_PREFIX = os.environ.get("CA_SOAK_TESTS_POOL_PREFIX", POOL_PREFIX_DEFAULT)


def zstd_decompress(data: bytes) -> bytes:
    import zstandard

    with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)) as r:
        return r.read()


def zstd_compress(data: bytes) -> bytes:
    import zstandard

    return zstandard.ZstdCompressor().compress(data)


def _env(name, default):
    return os.environ.get(name) or default


def s3_client():
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=_env("CA_SOAK_TESTS_S3_ENDPOINT", _S3_ENDPOINT_DEFAULT),
        aws_access_key_id=_env("CA_SOAK_TESTS_S3_ACCESS_KEY", _S3_KEY_DEFAULT),
        aws_secret_access_key=_env("CA_SOAK_TESTS_S3_SECRET_KEY", _S3_SECRET_DEFAULT),
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 5}),
    )


def list_common_prefixes(s3, prefix: str) -> list:
    resp = s3.list_objects_v2(Bucket=bucket(), Prefix=prefix, Delimiter="/")
    return [p["Prefix"] for p in resp.get("CommonPrefixes", [])]


def list_keys(s3, prefix: str) -> list:
    keys = []
    token = None
    while True:
        kw = {"Bucket": bucket(), "Prefix": prefix}
        if token:
            kw["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kw)
        keys += [o["Key"] for o in resp.get("Contents", [])]
        if not resp.get("IsTruncated"):
            return keys
        token = resp.get("NextContinuationToken")


def discover_single_life_id(s3):
    prefix = f"{POOL_PREFIX}/cas/ns/stream/"
    children = list_common_prefixes(s3, prefix)
    if len(children) != 1:
        return None
    child = children[0]
    if not child.startswith(prefix) or not child.endswith("/"):
        return None
    life_id = child[len(prefix) : -1]
    if len(life_id) != 32 or any(c not in "0123456789abcdef" for c in life_id):
        return None
    return life_id


def render_ref_txn_id(writer_epoch: int, ref_sequence: int) -> str:
    return f"{writer_epoch:016x}-{ref_sequence:016x}"


def parse_ref_txn_id(leaf: str):
    if leaf.endswith(REF_LOG_SUFFIX):
        leaf = leaf[: -len(REF_LOG_SUFFIX)]
    parts = leaf.split("-")
    if len(parts) != 2 or not all(len(p) == 16 for p in parts):
        return None
    try:
        return int(parts[0], 16), int(parts[1], 16)
    except ValueError:
        return None


def restamp_ref_log_txn(body: bytes, ref_sequence: int, writer_epoch=None, keep_ops=False) -> bytes:
    lines = zstd_decompress(body).decode().splitlines()
    if len(lines) < 3:
        raise ValueError(f"ref-log body has {len(lines)} lines")
    meta = json.loads(lines[1])
    meta["rs"] = str(ref_sequence)
    if writer_epoch is not None:
        meta["we"] = str(writer_epoch)
    meta.pop("!pse", None)
    meta.pop("!pss", None)
    if keep_ops:
        ops = lines[2:-1]
        out = [lines[0], json.dumps(meta, separators=(",", ":"))] + ops + ['{"n":%d}' % len(ops)]
    else:
        out = [lines[0], json.dumps(meta, separators=(",", ":")), '{"n":0}']
    return zstd_compress(("\n".join(out) + "\n").encode())


def bucket():
    return _env("CA_SOAK_TESTS_S3_BUCKET", _S3_BUCKET_DEFAULT)
