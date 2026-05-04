from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
def token_auth_over_https(self):
    """ClickHouse SHALL accept a valid bearer token over an HTTPS connection."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token over HTTPS"):
        body = access_clickhouse(token=token, https=True, status_code=200)
        assert len(body.strip()) > 0, error()


@TestScenario
def token_auth_over_https_multinode(self):
    """Token authentication over HTTPS SHALL work on every node in the cluster."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    for i, ip in enumerate(["clickhouse1", "clickhouse2", "clickhouse3"], 1):
        with Then(f"node {i} ({ip}) accepts the token over HTTPS"):
            access_clickhouse(token=token, ip=ip, https=True, status_code=200)


@TestScenario
def token_auth_http_disabled(self):
    """When the HTTP port is disabled, ClickHouse SHALL reject plain HTTP
    connections and only accept token-authenticated requests over HTTPS."""
    client = self.context.provider_client

    with Given("I disable the HTTP port, leaving only HTTPS"):
        change_ports_config(remove_http=True, https_port=8443)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("plain HTTP connection is refused"):
        access_clickhouse_connection_refused(token=token, https=False)

    with And("HTTPS connection with a valid token succeeds"):
        access_clickhouse(token=token, https=True, status_code=200)


@TestScenario
def invalid_token_over_https(self):
    """TLS SHALL NOT bypass token validation — a tampered token sent over
    HTTPS SHALL be rejected."""
    client = self.context.provider_client

    with Given("I get a valid token and tamper with it"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"sub": "invalid-subject-id"}
        )

    with Then("ClickHouse rejects the tampered token over HTTPS"):
        access_clickhouse(token=modified, https=True, status_code=500)


@TestScenario
def empty_token_over_https(self):
    """An empty bearer token sent over HTTPS SHALL be rejected with HTTP 403."""

    with Then("ClickHouse rejects the empty token over HTTPS"):
        access_clickhouse(token="", https=True, status_code=403)


@TestFeature
@Name("tls")
def feature(self):
    """Test TLS enforcement for OAuth token-bearing connections."""
    Scenario(run=token_auth_over_https)
    Scenario(run=token_auth_over_https_multinode)
    Scenario(run=token_auth_http_disabled)
    Scenario(run=invalid_token_over_https)
    Scenario(run=empty_token_over_https)
