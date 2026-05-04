"""Tests for the device-authorization (``--login=device``) flow."""

from testflows.core import *
from testflows.asserts import error

from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)


@TestScenario
@Name("device flow times out cleanly when token endpoint never returns id_token")
def device_flow_token_endpoint_eventually_times_out(self):
    """Check that device flow exits without ``std::bad_cast`` when no approval comes."""

    reset_client_state()
    write_oauth_credentials_file(
        client_id="grafana-client",
        client_secret="grafana-secret",
        token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
        device_authorization_uri=(
            "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
        ),
    )

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

    assert exit_code != 0, error()
    assert_no_segfault(output=output, exit_code=exit_code)
    assert "bad_cast" not in output and "std::bad_cast" not in output, (
        f"Device flow leaked Poco bad_cast:\n---\n{output}\n---"
    )


@TestScenario
@Name("device flow handles invalid token endpoint URL")
def device_flow_invalid_token_endpoint(self):
    """Check that an unreachable ``token_uri`` fails cleanly without a crash."""

    reset_client_state()
    write_oauth_credentials_file(
        client_id="grafana-client",
        client_secret="grafana-secret",
        token_uri="http://keycloak:8080/realms/does-not-exist/protocol/openid-connect/token",
        device_authorization_uri=(
            "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
        ),
    )

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

    assert exit_code != 0, error()
    assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("device flow")
def feature(self):
    """Tests for the device-authorization (``--login=device``) flow."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
