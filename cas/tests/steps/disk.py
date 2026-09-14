"""CAS disk / policy helpers."""

from testflows.core import *

REPLICATED_CLUSTER = "replicated_cluster"
SHARDED_CLUSTER = "sharded_cluster"
CAS_POLICY = "cas_policy"


def cas_disk_clause(
    self,
    pool_prefix,
    server_root_id=None,
    node=None,
    endpoint_host="http://minio:9000",
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

    access_key = self.context.minio_root_user
    secret_key = self.context.minio_root_password
    name = f"name = '{disk_name}', " if disk_name else ""

    return (
        "SETTINGS disk = disk("
        f"{name}"
        "type = object_storage, "
        "object_storage_type = s3, "
        "metadata_type = cas, "
        f"server_root_id = '{server_root_id}', "
        f"endpoint = '{endpoint_host}/warehouse/{pool_prefix}/', "
        f"access_key_id = '{access_key}', "
        f"secret_access_key = '{secret_key}'"
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
