"""Helpers for running the alter suite with content-addressed default storage."""

from pathlib import Path

from testflows.core import *

CAS_DEFAULT_POLICY_OVERRIDE = """\
<clickhouse>
    <storage_configuration>
        <policies>
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


def cas_default_policy_override_path():
    """Path of the optional config that remaps the default policy to cas_disk."""
    return (
        Path(__file__).resolve().parent
        / "configs"
        / "clickhouse"
        / "config.d"
        / "zz_cas_default_policy.xml"
    )


@TestStep(Given)
def enable_cas_default_storage(self):
    """Remap the default storage policy to CAS for this alter run."""
    override = cas_default_policy_override_path()
    override.write_text(CAS_DEFAULT_POLICY_OVERRIDE)
    self.context.use_cas_storage = True
    self.context.default_storage_policy = "cas_policy"
    try:
        yield
    finally:
        with Finally("remove CAS default-policy override"):
            if override.exists():
                override.unlink()


def check_cas_mode(test):
    """True when alter was started with --cas."""
    return bool(getattr(test.context, "use_cas_storage", False))
