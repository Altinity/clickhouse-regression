"""OAuth/JWT feature-support detection.

The server cannot start on a build without JWT support (the static ``jwt_user``
is rejected at boot), so support is probed from the binary with
``clickhouse local`` before any cluster is brought up.
"""

from testflows.core import *

from helpers.feature_support import get_clickhouse_binary, run_clickhouse_local


def jwt_authentication_supported(test):
    """Return True if the build supports ``IDENTIFIED WITH jwt``.

    The ``no_password`` control avoids a false negative when ``clickhouse local``
    cannot run ``CREATE USER`` for an unrelated reason.
    """
    with Given("I get the ClickHouse binary for the build under test"):
        binary = get_clickhouse_binary(test.context.clickhouse_path)

    with When("I create a user with a valid authentication type as a control"):
        control = run_clickhouse_local(
            binary, "CREATE USER OR REPLACE jwt_probe IDENTIFIED WITH no_password"
        )

    with And("I try to create a user identified with jwt"):
        probe = run_clickhouse_local(
            binary, "CREATE USER OR REPLACE jwt_probe IDENTIFIED WITH jwt"
        )

    with Then("I determine whether jwt authentication is supported"):
        if probe.returncode == 0:
            supported = True
        elif control.returncode == 0:
            supported = False
        else:
            probe_output = (probe.stdout + probe.stderr).lower()
            supported = not (
                "authentication type" in probe_output or "jwt" in probe_output
            )

    return supported
