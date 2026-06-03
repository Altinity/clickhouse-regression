"""Tests for the device-authorization (``--login=device``) flow."""

from testflows.core import *

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
    assert_client_rejected,
    assert_device_user_code_present,
    assert_no_segfault,
    keycloak_enable_optional_scope,
    kill_clickhouse_oauth_background_if_alive,
    parse_background_client_exit_code,
    read_clickhouse_oauth_background_log,
    reset_client_state,
    run_clickhouse_client,
    start_clickhouse_oauth_client_background,
    wait_clickhouse_oauth_background_finished,
    wait_for_device_user_code,
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
    """Device grant SHALL succeed after Keycloak approves the user code."""

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

        with And("I wait until the log contains a device user_code"):
            user_code = wait_for_device_user_code()

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
    """Device flow SHALL print verification URI and user code before polling."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("http://", "https://"),
        )
        assert_device_user_code_present(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow fails cleanly when device_authorization_uri is unreachable")
def device_flow_unreachable_device_authorization_uri(self):
    """Unreachable ``device_authorization_uri`` SHALL fail with a network error, not a crash."""

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

    with Then(
        "the client surfaces a network error and does not crash",
        description="""
            Acceptable network-failure shapes from Poco / glibc / curl-style
            diagnostics — pinning at least one is required so the scenario
            cannot pass on an unrelated failure mode (e.g. arg-parse error).
        """,
    ):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=(
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
            ),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow fails cleanly when device_authorization_uri returns 404")
def device_flow_device_authorization_endpoint_404(self):
    """404 from the device endpoint SHALL exit cleanly without a stack trace."""

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
        assert_client_rejected(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow rejects unknown client_id at Keycloak")
def device_flow_unknown_client_id(self):
    """Unknown ``client_id`` SHALL surface an OAuth error without crashing."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=(
                "client",
                "unauthorized",
                "invalid",
                "bad_arguments",
                "authentication_failed",
            ),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow rejects wrong client_secret at Keycloak")
def device_flow_wrong_client_secret(self):
    """Wrong ``client_secret`` SHALL fail device authorization without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And(
        "I write a credentials file with a wrong secret",
        description="""
            ``grafana-client`` is a public client in the realm export, so
            Keycloak ignores ``client_secret`` for it entirely. Use the
            confidential client ``grafana-client-confidential`` so the wrong
            secret actually trips Keycloak's authentication check.
        """,
    ):
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

    with Then(
        "the client exits with an OAuth invalid-client diagnostic",
        description="""
            Keycloak responds 401 with {"error":"invalid_client"} when the
            device endpoint receives a wrong client_secret for a confidential
            client. Pin at least one of the OAuth-spec failure markers so the
            scenario can't silently pass on, say, a network error.
        """,
    ):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=(
                "invalid_client",
                "unauthorized",
                "401",
                "client_secret",
                "authentication_failed",
            ),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_ConfidentialClient("1.0"))
@Name("device flow succeeds with confidential client secret")
def device_flow_succeeds_with_confidential_client(self):
    """Confidential client with correct secret SHALL complete the device grant."""

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

        with And("I wait until the log contains a device user_code"):
            user_code = wait_for_device_user_code()

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
    """Confidential client without ``client_secret`` SHALL be refused without crashing."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=(
                "secret",
                "bad_arguments",
                "invalid_client",
                "unauthorized",
                "401",
                "authentication_failed",
            ),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device flow timeout message is actionable")
def device_flow_timeout_message_is_actionable(self):
    """Expired device sessions SHALL report timeout or expiry without C++ leaks."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("timeout", "timed out", "expired", "expire"),
        )
        ol = output.lower()
        for bad in ("std::bad_cast", "std::exception", "poco::", "stack trace:"):
            assert bad not in ol, f"Unexpected low-level marker {bad!r} in:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login with explicit --port reaches OAuth stage without crash")
def device_flow_with_explicit_tcp_port(self):
    """Explicit ``--port`` SHALL not block reaching device authorization."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("http://", "https://"),
            require_nonzero_exit=False,
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login does not crash when targeting clickhouse2")
def device_flow_against_second_cluster_node(self):
    """Device flow SHALL work when ``--host`` is ``clickhouse2``."""

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

    with Then(
        "device authorization details appear against the second node",
        description="""
            OAuth happens before the TCP connection — the device user_code
            MUST appear regardless of which cluster node is named on --host.
            Asserting on user_code (rather than just "no crash") catches a
            regression where the OAuth path is short-circuited by node-
            specific routing.
        """,
    ):
        assert_device_user_code_present(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login with --secure does not crash")
def device_flow_with_secure_transport_flag(self):
    """``--secure`` with device login SHALL reach user-code display without crashing."""

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

    with Then(
        "the device-auth step runs to user_code before TLS would matter",
        description="""
            ``--secure`` only matters AFTER OAuth produces a token; in this
            ~12s window the device endpoint must still print the user_code
            so we know --secure didn't break the OAuth-front half of
            --login=device. The eventual TLS handshake failure (server is
            plaintext) is not observable in this timeout window and is not
            what this scenario is regressing.
        """,
    ):
        assert_device_user_code_present(output=output, exit_code=exit_code)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"),
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_NonJSONResponse("1.0"),
)
@Name("device flow times out cleanly when token endpoint never returns id_token")
def device_flow_token_endpoint_eventually_times_out(self):
    """Unapproved device flow SHALL exit without ``std::bad_cast``."""

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
        assert_client_rejected(output=output, exit_code=exit_code)
        assert (
            "bad_cast" not in output and "std::bad_cast" not in output
        ), f"Device flow leaked Poco bad_cast:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_UnreachableEndpoint("1.0"))
@Name("device flow handles invalid token endpoint URL")
def device_flow_invalid_token_endpoint(self):
    """Unreachable ``token_uri`` SHALL fail cleanly without crashing."""

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
        assert_client_rejected(output=output, exit_code=exit_code)


@TestFeature
@Name("device flow")
def feature(self):
    """Tests for the device-authorization (``--login=device``) flow."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
