"""Helpers for running the CAS suite with a cache disk in front of cas_disk."""

from pathlib import Path

from testflows.core import *

CAS_DISK = "cas_disk"
CAS_CACHE_DISK = "cas_cache"
CAS_POLICY = "cas_policy"

CAS_S3_CACHE_CONFIG = f"""\
<clickhouse>
    <storage_configuration>
        <disks>
            <{CAS_CACHE_DISK}>
                <type>cache</type>
                <disk>{CAS_DISK}</disk>
                <path>/var/lib/clickhouse/cas_cache/</path>
                <max_size>10Gi</max_size>
            </{CAS_CACHE_DISK}>
        </disks>
        <policies>
            <{CAS_POLICY}>
                <volumes>
                    <main>
                        <disk>{CAS_CACHE_DISK}</disk>
                    </main>
                </volumes>
            </{CAS_POLICY}>
            <default>
                <volumes>
                    <default>
                        <disk>{CAS_CACHE_DISK}</disk>
                    </default>
                </volumes>
            </default>
        </policies>
    </storage_configuration>
</clickhouse>
"""

CAS_S3_CACHE_PLACEHOLDER = """\
<clickhouse>
    <!--
    Placeholder for the CAS S3-cache overlay.

    The dedicated CAS suite always defines cas_disk in storage.xml. This file is
    filled in by cas/cas_mode.py when the suite is started with the cas-s3-cache
    option (adds a type=cache disk in front of cas_disk and retargets cas_policy /
    default) and reset back to this placeholder afterwards.
    -->
</clickhouse>
"""


def cas_s3_cache_config_path():
    """Path of the overlay that adds cas_cache and retargets cas_policy.

    Always mounted; only holds the cache disk when the suite is started with
    `--cas-s3-cache`. The `zz_` prefix keeps it last in the config.d merge order
    so `cas_policy` and `default` win over the uncached definitions in
    storage.xml.
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


@TestStep(Given)
def enable_cas_s3_cache(self):
    """Put a type=cache disk in front of cas_disk for this run.

    Must be called before the cluster is created; the config is read at server
    startup. Tests keep using ``storage_policy = 'cas_policy'``.
    """
    cas_s3_cache_config_path().write_text(CAS_S3_CACHE_CONFIG)
    self.context.use_cas_s3_cache = True
    self.context.cas_disk_name = CAS_CACHE_DISK
    try:
        yield
    finally:
        with Finally("reset CAS S3-cache overlay to its placeholder"):
            reset_cas_s3_cache_config()


def check_cas_s3_cache_mode(test):
    """True when the CAS suite was started with ``--cas-s3-cache``."""
    return bool(getattr(test.context, "use_cas_s3_cache", False))
