"""Generic feature-support validation shared across regression suites.

Fails once with a clear message when the build under test lacks the feature a
suite validates, instead of producing many unrelated failures.
"""

import os
import subprocess

from testflows.core import *

from helpers.cluster import PackageDownloader
from helpers.common import get_settings_value


@TestScenario
@Name("feature support validation")
def feature_support_validation(self, feature):
    """Fail when ``self.context.feature_supported`` is False."""
    if not self.context.feature_supported:
        fail(
            reason=f"{feature} is not supported by this build; "
            f"the feature is not present in this version."
        )


def validate_feature_support(self, feature, check):
    """Detect support (on the module context) and run the validation subtest.

    Plain function (not a scenario) so the flag lands on the module context and
    is visible to the module and sibling tests. Returns the support bool.
    """
    with Given(f"checking that the build supports {feature}"):
        self.context.feature_supported = bool(check(self))

    Scenario(test=feature_support_validation)(feature=feature)

    return self.context.feature_supported


def get_clickhouse_binary(clickhouse_path):
    """Download/locate the ClickHouse binary on the host (for pre-cluster probes)."""
    binary = os.path.abspath(
        PackageDownloader(
            clickhouse_path, program_name="clickhouse", binary_only=True
        ).binary_path
    )
    if os.path.isdir(binary):
        # docker:// sources return the extraction directory on a cached run
        binary = os.path.join(binary, "clickhouse")
    return binary


def run_clickhouse_local(binary, query):
    """Run a single ``query`` with ``clickhouse local`` on the host."""
    return subprocess.run(
        [binary, "local", "--query", query],
        capture_output=True,
        text=True,
    )


def setting_supported(setting_name):
    """Return a post-cluster check that is True when ``setting_name`` exists.

    Checks the setting's presence (``name`` column), not its ``value``: some
    settings default to an empty string, so a value-based check would wrongly
    report them as unsupported on builds that do have them.
    """

    def check(test):
        with Then(f"I check whether the {setting_name} setting exists"):
            name = get_settings_value(
                setting_name, node=test.context.node, column="name"
            )
        return name.strip() != ""

    return check
