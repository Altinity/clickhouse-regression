"""Helpers for running the aggregate functions suite with CAS storage."""

from pathlib import Path

from testflows.core import *

CAS_CONFIG = """\
<clickhouse>
    <storage_configuration>
        <disks>
            <cas_disk>
                <type>object_storage</type>
                <object_storage_type>s3</object_storage_type>
                <metadata_type>cas</metadata_type>
                <server_root_id>aggregate-functions-cas-{replica}</server_root_id>
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
        </policies>
    </storage_configuration>
</clickhouse>
"""

# Always mounted, but empty unless --cas is set. A real cas disk in a
# permanently-mounted config breaks non-Antalya builds at startup
# (unknown metadata storage type: cas).
CAS_CONFIG_PLACEHOLDER = """\
<clickhouse>
</clickhouse>
"""


def cas_config_path():
    return (
        Path(__file__).resolve().parent
        / "configs"
        / "clickhouse"
        / "config.d"
        / "cas.xml"
    )


def reset_cas_config():
    cas_config_path().write_text(CAS_CONFIG_PLACEHOLDER)


@TestStep(Given)
def enable_cas_storage(self):
    """Write the CAS disk/policy config and route create_table onto it.

    Must run before the cluster starts; disk config is read at server startup.
    """
    cas_config_path().write_text(CAS_CONFIG)
    self.context.default_storage_policy = "cas_policy"
    try:
        yield
    finally:
        with Finally("reset CAS config to its placeholder"):
            reset_cas_config()
