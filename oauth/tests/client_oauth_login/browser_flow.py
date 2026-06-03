"""Tests for ``--login=browser`` (authorization code + PKCE)."""

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_BrowserFlow_Authentication,
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    assert_client_rejected,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_browser_oauth_credentials,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_BrowserFlow_Authentication("1.0"))
@Name("browser login times out without crashing in headless env")
def browser_login_times_out_without_crash(self):
    """Browser login without callback SHALL time out cleanly in headless CI."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write OAuth credentials for the authorization-code flow"):
        write_browser_oauth_credentials()

    with When("I run clickhouse-client with --login=browser"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=browser",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=18,
            expect_error=True,
        )

    with Then("the client surfaces browser or callback or timeout and does not crash"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("browser", "callback", "timeout", "timed"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_BrowserFlow_Authentication("1.0"))
@Name("browser login handles unreachable auth_uri")
def browser_login_unreachable_auth_uri(self):
    """Unreachable ``auth_uri`` SHALL fail without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write credentials with a bogus authorization endpoint"):
        write_browser_oauth_credentials(
            auth_uri="http://does-not-exist.invalid:9999/oauth/auth"
        )

    with When("I run clickhouse-client with --login=browser"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=browser",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=18,
            expect_error=True,
        )

    with Then("the client exits with an error and no crash"):
        assert_client_rejected(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort("1.0"))
@Name("browser login accepts oauth-callback-port 0")
def browser_login_accepts_callback_port_zero(self):
    """``--oauth-callback-port=0`` SHALL select an ephemeral loopback port."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write OAuth credentials for the authorization-code flow"):
        write_browser_oauth_credentials()

    with When("I run clickhouse-client with --oauth-callback-port=0"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=browser",
                "--oauth-callback-port",
                "0",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=14,
            expect_error=True,
        )

    with Then("the client did not reject the port before opening the flow"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "invalid port" not in ol and "bad_arguments" not in ol
        ), f"Unexpected port rejection:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_BrowserFlow_Authentication("1.0"))
@Name("browser login accepts fixed oauth-callback-port")
def browser_login_accepts_fixed_callback_port(self):
    """Fixed loopback ``--oauth-callback-port`` in range SHALL be accepted."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write OAuth credentials for the authorization-code flow"):
        write_browser_oauth_credentials()

    with When("I run clickhouse-client with --oauth-callback-port=49152"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=browser",
                "--oauth-callback-port",
                "49152",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=14,
            expect_error=True,
        )

    with Then("there is no immediate invalid-port error"):
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            "invalid port" not in output.lower()
        ), f"Unexpected port error:\n---\n{output}\n---"


@TestFeature
@Name("browser flow")
def feature(self):
    """Tests for ``--login=browser``."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
