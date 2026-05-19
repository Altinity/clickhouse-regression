"""Security-focused negatives for browser OAuth and OIDC discovery."""

import textwrap

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields,
)
from oauth.tests.client_oauth_login.common import oauth_connection_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    assert_no_segfault,
    kill_clickhouse_oauth_background_if_alive,
    reset_client_state,
    run_clickhouse_client_no_host,
    start_clickhouse_oauth_client_background,
    write_client_config_xml,
    write_oauth_credentials_file, DEFAULT_CREDS_PATH,
)

BROWSER_SECURITY_LOG = "/tmp/ch_oauth_browser_security.log"
BROWSER_SECURITY_PID = "/tmp/ch_oauth_browser_security.pid"
MOCK_OIDC_PID_FILE = "/tmp/mock_oidc_oversized.pid"


@TestScenario
@Name("loopback /start must not leak oauth state in Location")
def loopback_start_must_not_redirect_with_oauth_state(self):
    """Unauthenticated GET /start must not expose CSRF ``state`` (clickhouse/audit #1606)."""

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

        with And("I probe /start on the loopback server"):
            result = self.context.node.command(
                command=(
                    "sleep 3; " "(curl -sSI http://127.0.0.1:49152/start || true) 2>&1"
                ),
                no_checks=True,
            )
            probe = result.output

        with Then("HTTP responded and Location omits oauth state"):
            assert (
                "HTTP/" in probe
            ), f"Expected an HTTP response from :49152/start, got:\n{probe}"
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
            kill_clickhouse_oauth_background_if_alive(
                self, pid_path=BROWSER_SECURITY_PID
            )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"),
)
@Name("oversized OIDC discovery document fails without hanging")
def oversized_oidc_discovery_response_is_bounded(self):
    """Huge ``openid-configuration`` payloads must not grow memory without bound."""

    mock_py = textwrap.dedent(
        """
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class H(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass

            def do_GET(self):
                if ".well-known/openid-configuration" not in self.path:
                    self.send_response(404)
                    self.end_headers()
                    return
                pad = b"x" * 8000000
                body = b'{"issuer":"http://bash-tools:18080/x","pad":"' + pad + b'"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        HTTPServer(("0.0.0.0", 18080), H).serve_forever()
        """
    ).strip()

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I start a mock discovery endpoint on bash-tools"):
            bash = self.context.bash_tools
            bash.command(
                command=(
                    f"cat > /tmp/mock_oidc_oversized.py <<'PY'\n{mock_py}\nPY\n"
                    "nohup python3 -u /tmp/mock_oidc_oversized.py "
                    f">/tmp/mock_oidc_oversized.log 2>&1 & "
                    f"echo $! > {MOCK_OIDC_PID_FILE}"
                )
            )

        with And("I write a connection that discovers via the mock"):
            write_client_config_xml(
                contents=oauth_connection_config_xml(
                    login_mode="device",
                    oauth_url="http://bash-tools:18080/realms/x",
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
            self.context.bash_tools.command(
                command=(
                    f"PID=$(cat {MOCK_OIDC_PID_FILE} 2>/dev/null); "
                    'if [ -n "$PID" ]; then kill "$PID" 2>/dev/null || true; fi'
                ),
                no_checks=True,
            )


@TestFeature
@Name("browser flow security")
def feature(self):
    """Security regressions for client OAuth."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
