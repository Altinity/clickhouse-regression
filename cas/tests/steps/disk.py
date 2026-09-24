"""CAS disk / policy helpers."""

from testflows.core import *

REPLICATED_CLUSTER = "replicated_cluster"
SHARDED_CLUSTER = "sharded_cluster"
CAS_POLICY = "cas_policy"
CAS_POLICY_POOL = "data/shared"
# AWS s3_disk only. A sibling of the CAS pools under the per-run prefix.
# `data` would be the parent of `data/shared` and `data/<table>`.
AWS_S3_DISK_PREFIX = "s3/data"


def cas_key_prefix(self, pool_prefix=""):
    """Return ``bucket[/run_prefix]/pool_prefix`` for the active object store."""
    parts = [
        getattr(self.context, "cas_bucket", "warehouse"),
        getattr(self.context, "cas_root_prefix", ""),
        pool_prefix,
    ]
    return "/".join(part.strip("/") for part in parts if part and str(part).strip("/"))


def cas_endpoint(self, pool_prefix, endpoint_host=None):
    """Return the S3 endpoint URL for ``pool_prefix`` on the active object store."""
    host = endpoint_host or getattr(
        self.context, "cas_endpoint_host", "http://minio:9000"
    )
    return f"{host.rstrip('/')}/{cas_key_prefix(self, pool_prefix)}/"


def cas_disk_auth_clause(self):
    """Return auth (and region / http_client) fragments for an inline CAS disk."""
    access_key = getattr(self.context, "cas_access_key", self.context.minio_root_user)
    secret_key = getattr(
        self.context, "cas_secret_key", self.context.minio_root_password
    )
    clause = (
        f"access_key_id = '{access_key}', "
        f"secret_access_key = '{secret_key}'"
    )
    region = getattr(self.context, "cas_region", None)
    if region:
        clause += f", region = '{region}'"
    http_client = getattr(self.context, "cas_http_client", None)
    if http_client:
        clause += f", http_client = '{http_client}'"
    return clause


def cas_disk_clause(
    self,
    pool_prefix,
    server_root_id=None,
    node=None,
    endpoint_host=None,
    disk_name=None,
):
    """Return a SETTINGS disk = disk(...) clause for content-addressed S3.

    server_root_id defaults to 'cas-<node_name>' so all tables on the same
    ClickHouse node share one ownership root — matching production semantics.

    ``disk_name`` names the disk instead of letting ClickHouse derive a name
    from the settings hash, which is what makes the disk addressable by
    statements that take a disk, such as SYSTEM CAS GC RUN.
    """
    if node is None:
        node = self.context.node

    if server_root_id is None:
        server_root_id = f"cas-{node.name}"

    name = f"name = '{disk_name}', " if disk_name else ""
    endpoint = cas_endpoint(self, pool_prefix, endpoint_host=endpoint_host)

    return (
        "SETTINGS disk = disk("
        f"{name}"
        "type = object_storage, "
        "object_storage_type = s3, "
        "metadata_type = cas, "
        f"server_root_id = '{server_root_id}', "
        f"endpoint = '{endpoint}', "
        f"{cas_disk_auth_clause(self)}"
        ")"
    )


def cas_policy_clause(policy=CAS_POLICY):
    """Return a SETTINGS storage_policy = '...' clause for the named CAS policy."""
    return f"SETTINGS storage_policy = '{policy}'"


def storage_settings(
    self,
    *,
    pool_prefix=None,
    server_root_id=None,
    node=None,
    policy=CAS_POLICY,
    disk_name=None,
):
    """Inline CAS disk when pool_prefix is set; otherwise the named storage policy."""
    if pool_prefix is not None:
        return cas_disk_clause(
            self,
            pool_prefix=pool_prefix,
            server_root_id=server_root_id,
            node=node,
            disk_name=disk_name,
        )
    return cas_policy_clause(policy=policy)
