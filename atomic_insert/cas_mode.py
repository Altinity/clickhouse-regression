"""Helpers for running the atomic insert suite with content-addressed default storage."""

from pathlib import Path

from testflows.core import *

from helpers.cas_storage import apply_cas_context, cas_storage_config

CAS_CONFIG_PLACEHOLDER = """\
<clickhouse>
    <!--
    Placeholder for the CAS storage configuration.

    CAS metadata storage only exists in Antalya builds, and disk definitions are
    parsed at server startup, so a `cas` disk in a config that is always mounted
    makes every older server fail to start with
    `MetadataStorageFactory: unknown metadata storage type: cas`.

    This file is filled in by atomic_insert/cas_mode.py when the suite is started
    with the cas or cas-s3-cache option and reset back to this placeholder afterwards.
    -->
</clickhouse>
"""


def cas_config_path():
    """Path of the config that defines the CAS disk and policies.

    Always mounted; only holds CAS definitions when the suite is started with
    `--cas` or `--cas-s3-cache`. The `zz_` prefix keeps it last in the config.d
    merge order so the `default` policy wins. Tables created without an explicit
    `storage_policy` (or via helpers.tables) then land on CAS.
    """
    return (
        Path(__file__).resolve().parent
        / "configs"
        / "clickhouse"
        / "config.d"
        / "zz_cas.xml"
    )


def reset_cas_config():
    """Reset the CAS config back to its no-op placeholder."""
    cas_config_path().write_text(CAS_CONFIG_PLACEHOLDER)


@TestStep(Given)
def enable_cas_default_storage(self, s3_cache=False):
    """Define the CAS disk and make it the default storage policy for this run.

    Must be called before the cluster is created; the config is read at server
    startup. When ``s3_cache`` is set, ``cas_policy`` / ``default`` point at a
    ``type=cache`` disk in front of ``cas_disk``.
    """
    cas_config_path().write_text(
        cas_storage_config("atomic-insert-cas-{replica}", with_s3_cache=s3_cache)
    )
    apply_cas_context(self, s3_cache=s3_cache)
    try:
        yield
    finally:
        with Finally("reset CAS config to its placeholder"):
            reset_cas_config()


def check_cas_mode(test):
    """True when atomic insert was started with ``--cas`` or ``--cas-s3-cache``."""
    return bool(getattr(test.context, "use_cas_storage", False))
