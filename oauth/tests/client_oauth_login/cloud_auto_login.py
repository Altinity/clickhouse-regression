"""Tests for the ClickHouse Cloud auto-login detection."""

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Cloud_AutoLogin,
    RQ_SRS_042_OAuth_Client_Login_Cloud_NonCloudHost,
)
from oauth.tests.client_oauth_login.common import connection_only_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    run_clickhouse_client_no_host,
    write_client_config_xml,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cloud_NonCloudHost("1.0"))
@Name("cloud auto-login is NOT triggered for non-cloud hostnames")
def cloud_auto_login_off_for_non_cloud_host(self):
    """Bare ``--login`` on non-cloud hosts SHALL require explicit OAuth args."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with bare --login against a non-cloud host"):
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

    with Then("the client requires explicit OAuth args and did not crash"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            "oauth-url" in output.lower()
            or "BAD_ARGUMENTS" in output
            or "AUTHENTICATION_FAILED" in output
        ), f"Expected explicit-OAuth-args hint or BAD_ARGUMENTS, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cloud_AutoLogin("1.0"))
@Name("clickhouse.cloud host avoids bare-login BAD_ARGUMENTS")
def cloud_hostname_triggers_auto_login_branch(self):
    """``*.clickhouse.cloud`` SHALL not immediately require ``--oauth-url``."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run bare --login against a cloud-shaped hostname"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "test.clickhouse.cloud",
                "--login",
            ],
            query="SELECT 1",
            timeout=18,
            expect_error=True,
        )

    with Then("failure is connectivity—not missing oauth-url arguments"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert not (
            "bad_arguments" in ol and "oauth-url" in ol
        ), f"Cloud host should not complain about oauth-url:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cloud_AutoLogin("1.0"))
@Name("cloud hostname via connection block uses auto-login branch")
def cloud_hostname_via_connection_block(self):
    """Cloud hostname via connection block SHALL use auto-login detection."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I install a cloud-shaped hostname in connections_credentials"):
        write_client_config_xml(
            contents=connection_only_config_xml(
                host="test.clickhouse.cloud",
                port=9440,
                name="cloud_conn",
            )
        )

    with When("I run bare --login with --connection"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "cloud_conn",
                "--login",
            ],
            query="SELECT 1",
            timeout=18,
        )

    with Then("failure is not missing-oauth-url BAD_ARGUMENTS"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert not (
            "bad_arguments" in ol and "oauth-url" in ol
        ), f"Cloud host should not complain about oauth-url:\n{output}"


@TestFeature
@Name("cloud auto-login")
def feature(self):
    """Tests for the ClickHouse Cloud auto-login detection."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
