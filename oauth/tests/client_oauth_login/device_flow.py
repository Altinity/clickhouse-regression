"""Tests for the device-authorization (``--login=device``) flow."""

import time

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Cache_Reuse,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_ConfidentialClient,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_NonJSONResponse,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    approve_keycloak_device_user_code_via_bash_tools,
    assert_no_segfault,
    extract_device_user_code_from_client_output,
    keycloak_enable_optional_scope,
    kill_clickhouse_oauth_background_if_alive,
    parse_background_client_exit_code,
    read_clickhouse_oauth_background_log,
    reset_client_state,
    run_clickhouse_client,
    start_clickhouse_oauth_client_background,
    wait_clickhouse_oauth_background_finished,
    write_keycloak_device_credentials,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Cache_Reuse("1.0"),
)
@Name("device flow succeeds after Keycloak approves the user code")
def device_flow_succeeds_when_keycloak_approves(self):
    """Client obtains tokens via device grant and runs the query."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("offline_access scope is enabled for grafana-client"):
            keycloak_enable_optional_scope(scope_name="offline_access")

        with And("I write a credentials file pointing at the Keycloak realm"):
            write_keycloak_device_credentials()

        with When("I start clickhouse-client with device login in the background"):
            start_clickhouse_oauth_client_background(
                args=[
                    "--host",
                    "clickhouse1",
                    "--login=device",
                    "--oauth-credentials",
                    DEFAULT_CREDS_PATH,
                ],
                query="SELECT currentUser()",
                wall_timeout=120,
            )

        user_code = None
        with And("I wait until the log contains a device user_code"):
            for _ in range(50):
                log_snippet = read_clickhouse_oauth_background_log()
                user_code = extract_device_user_code_from_client_output(log_snippet)
                if user_code:
                    break
                time.sleep(1)
            assert user_code is not None, (
                "Timed out waiting for device user_code in clickhouse-client output:\n"
                f"{read_clickhouse_oauth_background_log()}"
            )

        with And("I approve the device code through Keycloak"):
            approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)

        with Then("the background client finishes successfully"):
            wait_clickhouse_oauth_background_finished(timeout_sec=90)
            full_log = read_clickhouse_oauth_background_log()
            ec = parse_background_client_exit_code(full_log)
            assert ec == 0, (
                f"Expected exit code 0 after device approval, got {ec!r}:\n---\n"
                f"{full_log}\n---"
            )
            assert_no_segfault(output=full_log, exit_code=ec)

    finally:
        with Finally("I stop any stray background client"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow prints verification URI and user code")
def device_flow_prints_user_code_and_verification_uri(self):
    """Client surfaces device authorization details before polling."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client with device login and never approve"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then("the output contains an http URL and a user code"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "http://" in ol or "https://" in ol
        ), f"Expected a verification URL in output:\n---\n{output}\n---"
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected a device user_code in output:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow fails cleanly when device_authorization_uri is unreachable")
def device_flow_unreachable_device_authorization_uri(self):
    """Unreachable ``device_authorization_uri`` yields a network error, not a crash."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file with a bogus device host"):
        write_oauth_credentials_file(
            client_id="grafana-client",
            client_secret="grafana-secret",
            token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
            device_authorization_uri="http://does-not-exist.invalid:9999/auth/device",
        )

    with When("I run clickhouse-client with device login"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=18,
            expect_error=True,
        )

    with Then("the client surfaces a network error and does not crash"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        # Acceptable network-failure shapes from Poco / glibc / curl-style
        # diagnostics — pinning at least one is required so the scenario
        # cannot pass on an unrelated failure mode (e.g. arg-parse error).
        assert any(
            marker in ol
            for marker in (
                "could not resolve",
                "name or service",
                "name resolution",
                "no such host",
                "host not found",
                "connection refused",
                "network",
                "unreachable",
                "timed out",
                "timeout",
            )
        ), f"Expected a network-failure diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow fails cleanly when device_authorization_uri returns 404")
def device_flow_device_authorization_endpoint_404(self):
    """404 from the device authorization endpoint is handled without stack traces."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I point device_authorization_uri at a missing realm path"):
        write_oauth_credentials_file(
            client_id="grafana-client",
            client_secret="grafana-secret",
            token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
            device_authorization_uri=(
                "http://keycloak:8080/realms/does-not-exist/protocol/"
                "openid-connect/auth/device"
            ),
        )

    with When("I run clickhouse-client with device login"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then("the client exits with an error and no crash"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        assert "Stack trace:" not in output, error()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow rejects unknown client_id at Keycloak")
def device_flow_unknown_client_id(self):
    """Wrong ``client_id`` surfaces an OAuth error from the device endpoint."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file with a fictitious client_id"):
        write_oauth_credentials_file(
            client_id="nonexistent-client-id-xyz",
            client_secret="grafana-secret",
            token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
            device_authorization_uri=(
                "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
            ),
        )

    with When("I run clickhouse-client with device login"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then("the client reports failure without crashing"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "client" in ol
            or "unauthorized" in ol
            or "invalid" in ol
            or "bad_arguments" in ol
            or "authentication_failed" in ol
        ), f"Expected OAuth client diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow rejects wrong client_secret at Keycloak")
def device_flow_wrong_client_secret(self):
    """Wrong ``client_secret`` fails device authorization cleanly."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file with a wrong secret"):
        # ``grafana-client`` is a public client in the realm export, so
        # Keycloak ignores ``client_secret`` for it entirely. Use the
        # confidential client ``grafana-client-confidential`` so the wrong
        # secret actually trips Keycloak's authentication check.
        write_oauth_credentials_file(
            client_id="grafana-client-confidential",
            client_secret="wrong-secret-value",
            token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
            device_authorization_uri=(
                "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
            ),
        )

    with When("I run clickhouse-client with device login"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then("the client exits with an OAuth invalid-client diagnostic"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        # Keycloak responds 401 with {"error":"invalid_client"} when the
        # device endpoint receives a wrong client_secret for a confidential
        # client. Pin at least one of the OAuth-spec failure markers so the
        # scenario can't silently pass on, say, a network error.
        assert (
            "invalid_client" in ol
            or "unauthorized" in ol
            or "401" in ol
            or "client_secret" in ol
            or "authentication_failed" in ol
        ), f"Expected OAuth invalid-client diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_ConfidentialClient("1.0"))
@Name("device flow succeeds with confidential client secret")
def device_flow_succeeds_with_confidential_client(self):
    """Confidential client + correct secret completes the device grant.

    Mirrors :func:`device_flow_succeeds_when_keycloak_approves` but points
    at ``grafana-client-confidential``, the realm's confidential client.
    With ``grafana-client`` (public) Keycloak ignores ``client_secret``
    entirely, so the secret-validation code path on both clickhouse-client
    and Keycloak is structurally untested. This scenario closes that gap.
    """

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("offline_access scope is enabled for the confidential client"):
            keycloak_enable_optional_scope(
                scope_name="offline_access",
                client_id="grafana-client-confidential",
            )

        with And("I write a credentials file with the confidential client's secret"):
            write_oauth_credentials_file(
                client_id="grafana-client-confidential",
                client_secret="grafana-confidential-secret",
                token_uri=(
                    "http://keycloak:8080/realms/grafana/protocol/openid-connect/token"
                ),
                device_authorization_uri=(
                    "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
                ),
            )

        with When("I start clickhouse-client with device login in the background"):
            start_clickhouse_oauth_client_background(
                args=[
                    "--host",
                    "clickhouse1",
                    "--login=device",
                    "--oauth-credentials",
                    DEFAULT_CREDS_PATH,
                ],
                query="SELECT currentUser()",
                wall_timeout=120,
            )

        user_code = None
        with And("I wait until the log contains a device user_code"):
            for _ in range(50):
                log_snippet = read_clickhouse_oauth_background_log()
                user_code = extract_device_user_code_from_client_output(log_snippet)
                if user_code:
                    break
                time.sleep(1)
            assert user_code is not None, (
                "Timed out waiting for device user_code in clickhouse-client output:\n"
                f"{read_clickhouse_oauth_background_log()}"
            )

        with And("I approve the device code through Keycloak"):
            approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)

        with Then("the background client finishes successfully"):
            wait_clickhouse_oauth_background_finished(timeout_sec=90)
            full_log = read_clickhouse_oauth_background_log()
            ec = parse_background_client_exit_code(full_log)
            assert ec == 0, (
                f"Expected exit code 0 after device approval with confidential "
                f"client, got {ec!r}:\n---\n{full_log}\n---"
            )
            assert_no_segfault(output=full_log, exit_code=ec)

    finally:
        with Finally("I stop any stray background client"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_ConfidentialClient("1.0"))
@Name("device flow rejects missing client_secret at confidential client")
def device_flow_missing_client_secret_at_confidential_client(self):
    """Confidential client + no ``client_secret`` is refused cleanly.

    Documents the current end-to-end behaviour when ``client_secret`` is
    omitted from the credentials JSON while pointing at a confidential
    client. Today clickhouse-client rejects the credentials at load time
    (PR-audit issue 2.2 — ``client_secret`` is hard-required); when that
    fix lands the rejection will move server-side and Keycloak will
    return ``invalid_client``. The assertion accepts either shape so the
    scenario stays meaningful across that transition.
    """

    with Given("I reset the client state"):
        reset_client_state()

    with And("I omit client_secret and point at the confidential client"):
        write_oauth_credentials_file(
            client_id="grafana-client-confidential",
            client_secret=None,
            token_uri=(
                "http://keycloak:8080/realms/grafana/protocol/openid-connect/token"
            ),
            device_authorization_uri=(
                "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
            ),
        )

    with When("I run clickhouse-client with device login"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then("the client refuses cleanly without crashing"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "secret" in ol
            or "bad_arguments" in ol
            or "invalid_client" in ol
            or "unauthorized" in ol
            or "401" in ol
            or "authentication_failed" in ol
        ), (
            "Expected client_secret-related load failure or OAuth "
            f"invalid-client diagnostic, got:\n---\n{output}\n---"
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow timeout message is actionable")
def device_flow_timeout_message_is_actionable(self):
    """Expired device sessions mention timeout or expiry without low-level exceptions."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client until device polling exhausts"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=22,
            expect_error=True,
        )

    with Then("stderr mentions timeout or expiry without C++ leaks"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "timeout" in ol or "timed out" in ol or "expired" in ol or "expire" in ol
        ), f"Expected timeout/expiry wording, got:\n---\n{output}\n---"
        for bad in ("std::bad_cast", "std::exception", "poco::", "stack trace:"):
            assert bad not in ol, f"Unexpected low-level marker {bad!r} in:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login with explicit --port reaches OAuth stage without crash")
def device_flow_with_explicit_tcp_port(self):
    """Explicit native ``--port`` must not break reaching the device-authorization step."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client with explicit tcp_port matching compose"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--port",
                "9000",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=12,
            expect_error=True,
        )

    with Then("the client shows device-flow hints without crashing"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "http://" in ol or "https://" in ol
        ), f"Expected verification URI in output, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login does not crash when targeting clickhouse2")
def device_flow_against_second_cluster_node(self):
    """OAuth device negotiation works when the TCP host is ``clickhouse2``."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client against clickhouse2"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse2",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=12,
            expect_error=True,
        )

    with Then("device authorization details appear against the second node"):
        assert_no_segfault(output=output, exit_code=exit_code)
        # OAuth happens before the TCP connection — the device user_code
        # MUST appear regardless of which cluster node is named on --host.
        # Asserting on user_code (rather than just "no crash") catches a
        # regression where the OAuth path is short-circuited by node-
        # specific routing.
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected device user_code targeting clickhouse2:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login with --secure does not crash")
def device_flow_with_secure_transport_flag(self):
    """Passing ``--secure`` while using device OAuth must not segfault."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client with --secure"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--secure",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=12,
            expect_error=True,
        )

    with Then("the device-auth step runs to user_code before TLS would matter"):
        assert_no_segfault(output=output, exit_code=exit_code)
        # ``--secure`` only matters AFTER OAuth produces a token; in this
        # ~12s window the device endpoint must still print the user_code
        # so we know --secure didn't break the OAuth-front half of
        # --login=device. The eventual TLS handshake failure (server is
        # plaintext) is not observable in this timeout window and is not
        # what this scenario is regressing.
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected device user_code with --secure:\n---\n{output}\n---"


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"),
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_NonJSONResponse("1.0"),
)
@Name("device flow times out cleanly when token endpoint never returns id_token")
def device_flow_token_endpoint_eventually_times_out(self):
    """Device flow exits without ``std::bad_cast`` when no approval comes."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file pointing at the Keycloak realm"):
        write_keycloak_device_credentials()

    with When("I run clickhouse-client with --login=device and never approve"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=20,
            expect_error=True,
        )

    with Then("the client exits cleanly without a Poco bad_cast"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            "bad_cast" not in output and "std::bad_cast" not in output
        ), f"Device flow leaked Poco bad_cast:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow handles invalid token endpoint URL")
def device_flow_invalid_token_endpoint(self):
    """Unreachable ``token_uri`` fails cleanly without a crash."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file with an unreachable token_uri"):
        write_oauth_credentials_file(
            client_id="grafana-client",
            client_secret="grafana-secret",
            token_uri="http://keycloak:8080/realms/does-not-exist/protocol/openid-connect/token",
            device_authorization_uri=(
                "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
            ),
        )

    with When(
        "I run clickhouse-client with --login=device against the unreachable token endpoint"
    ):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=20,
            expect_error=True,
        )

    with Then("the client exits with a recognisable error and no crash"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("device flow")
def feature(self):
    """Tests for the device-authorization (``--login=device``) flow."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
