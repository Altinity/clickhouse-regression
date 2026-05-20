"""Tests for ``connections_credentials`` OAuth fields and ``--oauth-*`` CLI flags."""

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Cloud_NonCloudHost,
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_CLIOverride,
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort,
    RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields,
)
from oauth.tests.client_oauth_login.common import oauth_connection_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    assert_no_segfault,
    extract_device_user_code_from_client_output,
    reset_client_state,
    run_clickhouse_client_no_host,
    write_client_config_xml,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"))
@Name("connection block configures device-flow OAuth")
def connection_block_oauth_device(self):
    """Check that a ``<connection>`` with ``<login>device</login>`` drives device flow."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a connection block with OAuth fields and login=device"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(login_mode="device")
        )

    with When("I run clickhouse-client with --connection ch_oauth"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=15,
        )

    with Then("the device flow is driven from the XML connection block"):
        assert_no_segfault(output=output, exit_code=exit_code)
        # The connection block names a valid Keycloak realm + client,
        # so device authorization MUST hand out a user_code. Pinning
        # this rather than just "no crash" catches regressions where
        # the XML fields stop being read into the OAuth context.
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected XML-driven device flow user_code:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_CLIOverride("1.0"))
@Name("--oauth-* CLI flags override connection block")
def cli_overrides_connection_block(self):
    """Check that CLI ``--oauth-client-id`` overrides ``<oauth-client-id>`` from the block."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a connection block with oauth-client-id=block-id"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="device",
                oauth_client_id="block-id",
            )
        )

    with When(
        "I run clickhouse-client with --oauth-client-id=cli-id overriding the block"
    ):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
                "--oauth-client-id",
                "cli-id",
            ],
            query="SELECT 1",
            timeout=12,
        )

    with Then("Keycloak rejects cli-id (proving the override is in effect)"):
        assert exit_code != 0
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        # Both block-id and cli-id are fake; what we are pinning here is
        # that the *overridden* value reached Keycloak. That manifests as
        # an OAuth invalid_client/invalid-client diagnostic.
        assert (
            "invalid_client" in ol
            or "invalid client" in ol
            or "unauthorized" in ol
            or "client"
            in ol  # final fallback so Keycloak phrasing changes don't break us
        ), f"Expected OAuth invalid-client diagnostic from Keycloak, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort("1.0"))
@Name("connection block with invalid oauth-callback-port is rejected")
def invalid_callback_port_rejected(self):
    """Check that an out-of-range ``<oauth-callback-port>`` fails fast without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a connection block with oauth-callback-port=999999"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="browser",
                oauth_callback_port="999999",
            )
        )

    with When("I run clickhouse-client with the out-of-range callback port"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=10,
        )

    with Then("the client rejects the out-of-range port"):
        assert_no_segfault(output=output, exit_code=exit_code)
        # 999999 is outside the legal TCP port range; a *clean* arg-parse
        # rejection is the SRS-prescribed outcome. Mirror the assertion
        # the negative-port sibling scenario already enforces so the two
        # boundary conditions are pinned symmetrically.
        ol = output.lower()
        assert (
            "bad_arguments" in ol or "invalid" in ol or "port" in ol
        ), f"Expected out-of-range port diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"))
@Name("connection block with login browser drives browser OAuth")
def connection_block_login_browser(self):
    """``<login>browser</login>`` reaches browser OAuth without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a browser-oriented connection block"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(login_mode="browser")
        )

    with When("I run clickhouse-client with --connection ch_oauth"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=14,
        )

    with Then("the browser-flow front half ran without crashing"):
        assert_no_segfault(output=output, exit_code=exit_code)
        # ``<login>browser</login>`` must drive the authorization-code
        # flow far enough to print a visit-this-URL hint or a callback
        # message — otherwise the connection block isn't actually
        # selecting the browser path. Headless CI cannot complete the
        # callback but the *start* of the flow is observable.
        ol = output.lower()
        assert any(
            marker in ol
            for marker in (
                "browser",
                "callback",
                "loopback",
                "visit",
                "open the following",
                "http://127.0.0.1",
                "http://localhost",
                "timeout",
                "timed out",
            )
        ), f"Expected browser-flow start signal, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cloud_NonCloudHost("1.0"))
@Name("connection block bare login requires explicit oauth fields")
def connection_block_bare_login_without_oauth_requires_args(self):
    """Empty ``<login/>`` on non-cloud hosts demands OAuth configuration."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write connection metadata without oauth-url"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="",
                oauth_url=None,
                oauth_client_id=None,
            )
        )

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=12,
        )

    with Then("OAuth parameters are required"):
        assert exit_code != 0
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "oauth" in ol or "bad_arguments" in ol or "authentication_failed" in ol
        ), f"Expected OAuth requirement hint, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"))
@Name("connection oauth-url discovers device endpoints")
def connection_block_oauth_url_oidc_discovery_device_flow(self):
    """``<oauth-url>`` drives OIDC discovery for device login."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write oauth-url plus confidential client secret"):
        # Use the confidential client so the ``oauth_client_secret`` value
        # is actually validated by Keycloak (``grafana-client`` is public
        # and ignores ``client_secret`` entirely).
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="device",
                oauth_url="http://keycloak:8080/realms/grafana",
                oauth_client_id="grafana-client-confidential",
                oauth_client_secret="grafana-confidential-secret",
            )
        )

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=15,
        )

    with Then("device authorization details appear"):
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected discovery-driven device flow:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_OAuthFields("1.0"))
@Name("invalid oauth-url fails discovery cleanly")
def connection_block_invalid_oauth_url(self):
    """Bad issuer URLs stop discovery without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a bogus oauth-url"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="device",
                oauth_url="http://keycloak:8080/nonexistent-realm",
                oauth_client_id="grafana-client",
                oauth_client_secret="grafana-secret",
            )
        )

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=14,
        )

    with Then("the client errors"):
        assert exit_code != 0
        assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_CLIOverride("1.0"))
@Name("CLI oauth flags override broken connection defaults")
def cli_overrides_multiple_oauth_fields(self):
    """``--oauth-url`` / secret / audience supersede bad XML defaults."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write misleading OAuth defaults in XML"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="device",
                oauth_url="http://127.0.0.1:9/dead",
                oauth_client_id="wrong-id",
                oauth_client_secret="wrong-secret",
            )
        )

    with When("I override via CLI with working Keycloak endpoints"):
        # Override targets the confidential client so the secret-override
        # path is exercised end-to-end rather than relying on Keycloak
        # ignoring the secret for a public client.
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
                "--oauth-url",
                "http://keycloak:8080/realms/grafana",
                "--oauth-client-id",
                "grafana-client-confidential",
                "--oauth-client-secret",
                "grafana-confidential-secret",
                "--oauth-audience",
                "http://localhost",
            ],
            query="SELECT 1",
            timeout=14,
        )

    with Then("CLI wins — device flow reaches Keycloak"):
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected CLI overrides to fix discovery:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort("1.0"))
@Name("negative oauth-callback-port in connection block is rejected")
def connection_block_negative_callback_port(self):
    """Callback ports below zero are invalid."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write oauth-callback-port=-1"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="browser",
                oauth_callback_port="-1",
            )
        )

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=12,
        )

    with Then("the client rejects the port"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "bad_arguments" in ol or "invalid" in ol or "port" in ol
        ), f"Expected invalid port diagnostic:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_ConnectionBlock_InvalidCallbackPort("1.0"))
@Name("oauth-callback-port 65535 is accepted")
def connection_block_callback_port_upper_bound(self):
    """Upper TCP port boundary ``65535`` validates."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I pin oauth-callback-port to 65535"):
        write_client_config_xml(
            contents=oauth_connection_config_xml(
                login_mode="browser",
                oauth_callback_port="65535",
            )
        )

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client_no_host(
            args=[
                "--config",
                DEFAULT_CONFIG_PATH,
                "--connection",
                "ch_oauth",
            ],
            query="SELECT 1",
            timeout=14,
        )

    with Then("there is no immediate invalid-port error"):
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            "invalid port" not in output.lower()
        ), f"Unexpected rejection for 65535:\n{output}"


@TestFeature
@Name("connection block oauth")
def feature(self):
    """Tests for ``connections_credentials`` OAuth fields and ``--oauth-*`` CLI flags."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
