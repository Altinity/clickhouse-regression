"""Tests for the ClickHouse Cloud auto-login detection."""

from testflows.core import *
from testflows.asserts import error

from oauth.tests.steps.client_login import (
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
)


@TestScenario
@Name("cloud auto-login is NOT triggered for non-cloud hostnames")
def cloud_auto_login_off_for_non_cloud_host(self):
    """Check that bare ``--login`` against a non-cloud host requires explicit OAuth args."""

    reset_client_state()

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login",
        ],
        query="SELECT 1",
        timeout=8,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert_no_segfault(output=output, exit_code=exit_code)
    assert (
        "oauth-url" in output.lower()
        or "BAD_ARGUMENTS" in output
        or "AUTHENTICATION_FAILED" in output
    ), f"Expected explicit-OAuth-args hint or BAD_ARGUMENTS, got:\n---\n{output}\n---"


@TestFeature
@Name("cloud auto-login")
def feature(self):
    """Tests for the ClickHouse Cloud auto-login detection."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
