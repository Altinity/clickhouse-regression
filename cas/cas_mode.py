"""Helpers for running the CAS suite with a cache disk in front of cas_disk."""

from pathlib import Path
from xml.sax.saxutils import escape

from testflows.core import *

CAS_DISK = "cas_disk"
CAS_CACHE_DISK = "cas_cache"
CAS_POLICY = "cas_policy"

CAS_S3_CACHE_PLACEHOLDER = """\
<clickhouse>
    <!--
    Placeholder for the CAS disk overlay.

    cas/regression.py fills this file in before the cluster starts. It sets the
    cas_disk endpoint from cas_endpoint() and, with --cas-s3-cache, adds a
    type=cache disk in front of cas_disk and retargets cas_policy. The file is
    reset to this placeholder when the run ends. The default policy stays on
    the local disk so system logs do not write into the CAS pool.
    -->
</clickhouse>
"""


def cas_minio_disk_overlay(endpoint, with_cache=False):
    """Overlay that sets the named cas_disk endpoint, and optionally the cache.

    Only the endpoint is written here, from the same ``cas_endpoint`` helper
    that builds inline disks. MinIO credentials stay in ``storage.xml``.
    """
    cache_disk = ""
    cache_policy = ""
    if with_cache:
        cache_disk = f"""
            <{CAS_CACHE_DISK}>
                <type>cache</type>
                <disk>{CAS_DISK}</disk>
                <path>/var/lib/clickhouse/cas_cache/</path>
                <max_size>10Gi</max_size>
            </{CAS_CACHE_DISK}>
"""
        cache_policy = f"""
        <policies>
            <{CAS_POLICY}>
                <volumes>
                    <main>
                        <disk>{CAS_CACHE_DISK}</disk>
                    </main>
                </volumes>
            </{CAS_POLICY}>
        </policies>
"""
    return f"""\
<clickhouse>
    <storage_configuration>
        <disks>
            <{CAS_DISK}>
                <endpoint>{escape(endpoint)}</endpoint>
            </{CAS_DISK}>
            {cache_disk}
        </disks>
        {cache_policy}
    </storage_configuration>
</clickhouse>
"""


def cas_s3_cache_config_path():
    """Path of the overlay that sets the cas_disk endpoint and optional cache.

    Always mounted. The `zz_` prefix keeps it last in the config.d merge order
    so its cas_disk endpoint and, when present, cas_policy win over storage.xml.
    The default policy is left on the local disk.
    """
    return (
        Path(__file__).resolve().parent
        / "configs"
        / "clickhouse"
        / "config.d"
        / "zz_cas_s3_cache.xml"
    )


def reset_cas_s3_cache_config():
    """Reset the S3-cache overlay back to its no-op placeholder."""
    cas_s3_cache_config_path().write_text(CAS_S3_CACHE_PLACEHOLDER)


def cas_aws_storage_overlay(
    s3_endpoint,
    cas_endpoint,
    region,
    with_cache=False,
):
    """Override s3_disk / cas_disk endpoints and optionally retarget cas_policy.

    AWS keys are not written here. The overlay points both disks at
    ``CAS_ACCESS_KEY_ID`` and ``CAS_SECRET_ACCESS_KEY`` in the server
    environment, which replaces the MinIO credentials from ``storage.xml``.
    """
    cache_disk = ""
    cache_policy = ""
    if with_cache:
        cache_disk = f"""
            <{CAS_CACHE_DISK}>
                <type>cache</type>
                <disk>{CAS_DISK}</disk>
                <path>/var/lib/clickhouse/cas_cache/</path>
                <max_size>10Gi</max_size>
            </{CAS_CACHE_DISK}>
"""
        cache_policy = f"""
        <policies>
            <{CAS_POLICY}>
                <volumes>
                    <main>
                        <disk>{CAS_CACHE_DISK}</disk>
                    </main>
                </volumes>
            </{CAS_POLICY}>
        </policies>
"""
    return f"""\
<clickhouse>
    <storage_configuration>
        <disks>
            <s3_disk>
                <endpoint>{escape(s3_endpoint)}</endpoint>
                <region>{escape(region)}</region>
                <access_key_id from_env="CAS_ACCESS_KEY_ID"/>
                <secret_access_key from_env="CAS_SECRET_ACCESS_KEY"/>
            </s3_disk>
            <cas_disk>
                <endpoint>{escape(cas_endpoint)}</endpoint>
                <region>{escape(region)}</region>
                <access_key_id from_env="CAS_ACCESS_KEY_ID"/>
                <secret_access_key from_env="CAS_SECRET_ACCESS_KEY"/>
            </cas_disk>
            {cache_disk}
        </disks>
        {cache_policy}
    </storage_configuration>
</clickhouse>
"""


@TestStep(Given)
def enable_cas_minio_disk(self, endpoint, with_cache=False):
    """Point the named cas_disk at ``endpoint`` before the cluster starts.

    ``endpoint`` comes from ``cas_endpoint``. With ``with_cache``, a type=cache
    disk is placed in front of cas_disk and cas_policy is retargeted to it.
    Tests keep using ``storage_policy = 'cas_policy'``. The default policy is
    not remapped, so system log tables stay off the CAS pool.
    """
    cas_s3_cache_config_path().write_text(
        cas_minio_disk_overlay(endpoint, with_cache=with_cache)
    )
    if with_cache:
        self.context.use_cas_s3_cache = True
        self.context.cas_disk_name = CAS_CACHE_DISK
    try:
        yield
    finally:
        with Finally("reset CAS disk overlay to its placeholder"):
            reset_cas_s3_cache_config()


@TestStep(Given)
def enable_cas_aws_storage(
    self,
    s3_endpoint,
    cas_endpoint,
    region,
    with_cache=False,
):
    """Point the named S3 / CAS disks at AWS before the cluster starts.

    Reuses the already-mounted ``zz_cas_s3_cache.xml`` overlay so compose
    files do not change. Reset to the placeholder when the run ends.
    """
    cas_s3_cache_config_path().write_text(
        cas_aws_storage_overlay(
            s3_endpoint=s3_endpoint,
            cas_endpoint=cas_endpoint,
            region=region,
            with_cache=with_cache,
        )
    )
    if with_cache:
        self.context.use_cas_s3_cache = True
        self.context.cas_disk_name = CAS_CACHE_DISK
    try:
        yield
    finally:
        with Finally("reset CAS storage overlay to its placeholder"):
            reset_cas_s3_cache_config()


def check_cas_s3_cache_mode(test):
    """True when the CAS suite was started with ``--cas-s3-cache``."""
    return bool(getattr(test.context, "use_cas_s3_cache", False))
