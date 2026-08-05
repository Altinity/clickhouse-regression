"""Helpers for running the alter suite with content-addressed default storage."""

from pathlib import Path

from testflows.core import *

CAS_CONFIG = """\
<clickhouse>
    <storage_configuration>
        <disks>
            <cas_disk>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>content_addressed</metadata_type>
                <server_root_id>alter-cas-{replica}</server_root_id>
                <endpoint>http://minio:9001/cas/data/</endpoint>
                <access_key_id>minio</access_key_id>
                <secret_access_key>minio123</secret_access_key>
            </cas_disk>
        </disks>
        <policies>
            <cas_policy>
                <volumes>
                    <main>
                        <disk>cas_disk</disk>
                    </main>
                </volumes>
            </cas_policy>
            <default>
                <volumes>
                    <default>
                        <disk>cas_disk</disk>
                    </default>
                </volumes>
            </default>
        </policies>
    </storage_configuration>
</clickhouse>
"""

CAS_CONFIG_PLACEHOLDER = """\
<clickhouse>
    <!--
    Placeholder for the content-addressed storage configuration.

    Content-addressed metadata storage only exists in Antalya builds, and disk
    definitions are parsed at server startup, so a `content_addressed` disk in a
    config that is always mounted makes every older server fail to start with
    `MetadataStorageFactory: unknown metadata storage type: content_addressed`.

    This file is filled in by alter/cas_mode.py when the suite is started with
    the `cas` option and reset back to this placeholder afterwards.
    -->
</clickhouse>
"""


def cas_config_path():
    """Path of the config that defines the CAS disk and policies.

    The file is always mounted into the ClickHouse containers, but it only holds
    the CAS definitions when the suite is started with `--cas`.
    """
    return (
        Path(__file__).resolve().parent
        / "configs"
        / "clickhouse"
        / "config.d"
        / "cas.xml"
    )


def reset_cas_config():
    """Reset the CAS config back to its no-op placeholder."""
    cas_config_path().write_text(CAS_CONFIG_PLACEHOLDER)


@TestStep(Given)
def enable_cas_default_storage(self):
    """Define the CAS disk and make it the default storage policy for this run.

    Must be called before the cluster is created, the config is read at server
    startup.
    """
    cas_config_path().write_text(CAS_CONFIG)
    self.context.use_cas_storage = True
    self.context.default_storage_policy = "cas_policy"
    try:
        yield
    finally:
        with Finally("reset CAS config to its placeholder"):
            reset_cas_config()


def check_cas_mode(test):
    """True when alter was started with --cas."""
    return bool(getattr(test.context, "use_cas_storage", False))
