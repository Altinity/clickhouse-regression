"""Helpers for running the aggregate functions suite with CAS storage."""

from pathlib import Path

from testflows.core import *

from helpers.cas_storage import apply_cas_context, cas_storage_config

# Always mounted, but empty unless --cas / --cas-s3-cache is set. A real cas
# disk in a permanently-mounted config breaks non-Antalya builds at startup
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
def enable_cas_storage(self, s3_cache=False):
    """Write the CAS disk/policy config and route create_table onto it.

    Must run before the cluster starts; disk config is read at server startup.
    When ``s3_cache`` is set, ``cas_policy`` points at a ``type=cache`` disk in
    front of ``cas_disk``.
    """
    cas_config_path().write_text(
        cas_storage_config(
            "aggregate-functions-cas-{replica}",
            with_s3_cache=s3_cache,
            override_default_policy=False,
        )
    )
    apply_cas_context(self, s3_cache=s3_cache)
    try:
        yield
    finally:
        with Finally("reset CAS config to its placeholder"):
            reset_cas_config()
