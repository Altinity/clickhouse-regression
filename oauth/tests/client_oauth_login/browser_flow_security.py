"""Security-focused negatives for browser OAuth and OIDC discovery."""

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields,
)
from oauth.tests.client_oauth_login.common import oauth_connection_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    kill_clickhouse_oauth_background_if_alive,
    reset_client_state,
    run_clickhouse_client_no_host,
    start_clickhouse_oauth_client_background,
    start_oversized_oidc_discovery_mock,
    stop_mock_oidc_server,
    wait_for_http_response,
    write_client_config_xml,
    write_oauth_credentials_file,
)

BROWSER_SECURITY_LOG = "/tmp/ch_oauth_browser_security.log"
BROWSER_SECURITY_PID = "/tmp/ch_oauth_browser_security.pid"
OVERSIZED_OIDC_MOCK_PORT = 18080


@TestScenario
@Name("loopback /start must not leak oauth state in Location")
def loopback_start_must_not_redirect_with_oauth_state(self):
    """GET /start SHALL not expose OAuth ``state`` in the Location header."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write credentials for browser OAuth"):
            write_oauth_credentials_file(
                client_id="grafana-client",
                client_secret="grafana-secret",
                auth_uri=(
                    "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth"
                ),
                token_uri=(
                    "http://keycloak:8080/realms/grafana/protocol/openid-connect/token"
                ),
                redirect_uris=["http://127.0.0.1"],
                device_authorization_uri=None,
            )

        with When("I start browser login pinned to callback port 49152"):
            start_clickhouse_oauth_client_background(
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
                log_path=BROWSER_SECURITY_LOG,
                pid_path=BROWSER_SECURITY_PID,
                wall_timeout=25,
            )

        with And("I probe /start on the loopback server once it binds"):
            # Poll the loopback callback server rather than waiting a
            # fixed sleep — the previous sleep(3) raced against
            # clickhouse-client's port-bind under load and produced
            # phantom passes when /start was queried before the
            # server was up.
            probe = wait_for_http_response(
                url="http://127.0.0.1:49152/start",
                max_wait=15,
            )

        with Then("HTTP responded and Location omits oauth state"):
            assert "HTTP/" in probe, (
                "Loopback /start never responded within the poll window — "
                f"the callback server may not have bound. Probe:\n{probe}"
            )
            loc_line = ""
            for line in probe.splitlines():
                if line.lower().startswith("location:"):
                    loc_line = line
                    break
            ol = loc_line.lower()
            assert "state=" not in ol, (
                "Expected /start not to expose state= in Location header "
                f"(got {loc_line!r}). Full probe:\n{probe}"
            )

    finally:
        with Finally("I stop the browser-login background client"):
            kill_clickhouse_oauth_background_if_alive(pid_path=BROWSER_SECURITY_PID)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"),
)
@Name("oversized OIDC discovery document fails without hanging")
def oversized_oidc_discovery_response_is_bounded(self):
    """Oversized OIDC discovery response SHALL fail without hanging or crashing."""

    mock_pid_file = None
    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I start the oversized OIDC discovery mock on bash-tools"):
            mock_pid_file = start_oversized_oidc_discovery_mock(
                port=OVERSIZED_OIDC_MOCK_PORT,
            )

        with And("I write a connection that discovers via the mock"):
            write_client_config_xml(
                contents=oauth_connection_config_xml(
                    login_mode="device",
                    oauth_url=f"http://bash-tools:{OVERSIZED_OIDC_MOCK_PORT}/realms/x",
                    oauth_client_id="grafana-client",
                    oauth_client_secret="grafana-secret",
                )
            )

        with When("I run clickhouse-client against the mock issuer"):
            exit_code, output = run_clickhouse_client_no_host(
                args=[
                    "--config",
                    DEFAULT_CONFIG_PATH,
                    "--connection",
                    "ch_oauth",
                ],
                query="SELECT 1",
                timeout=45,
                expect_error=True,
            )

        with Then("the client stops with an error and no crash"):
            assert_no_segfault(output=output, exit_code=exit_code)

    finally:
        with Finally("I stop the mock HTTP server"):
            if mock_pid_file is not None:
                stop_mock_oidc_server(pid_file=mock_pid_file)


@TestFeature
@Name("browser flow security")
def feature(self):
    """Security regressions for client OAuth."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
