from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"),
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
)
def valid_token_accepted(self):
    """ClickHouse SHALL accept a valid Keycloak access token over HTTP."""
    client = self.context.provider_client

    with Given("I get a valid OAuth token from Keycloak"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token and returns the current user"):
        body = access_clickhouse(token=token, status_code=200)

    with And("the response contains a user identity"):
        assert len(body) > 0, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"),
)
def empty_token_rejected(self):
    """ClickHouse SHALL reject an empty bearer token with HTTP 401."""
    access_clickhouse_unauthenticated()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def tampered_signature_rejected(self):
    """ClickHouse SHALL reject a token with a tampered signature."""
    client = self.context.provider_client

    with Given("I get a valid token and tamper with the signature"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]
        token = token[:-4] + "7b39"

    with Then("ClickHouse rejects the tampered token"):
        access_clickhouse_when_forbidden(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
)
def malformed_token_rejected(self):
    """ClickHouse SHALL reject a completely malformed token."""
    with Then("ClickHouse rejects the garbage token"):
        access_clickhouse(token="not.a.valid-jwt", status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Actions_Authentication("1.0"),
)
def valid_token_on_all_nodes(self):
    """ClickHouse SHALL accept a valid token on every node in the cluster."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    for i, ip in enumerate(["clickhouse1", "clickhouse2", "clickhouse3"], 1):
        with Then(f"node {i} ({ip}) accepts the token"):
            access_clickhouse(token=token, ip=ip, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserRoles_NoAccessTokenProcessors("1.0"),
)
def no_token_processor_configured(self):
    """ClickHouse SHALL reject auth when no valid token processor is defined."""
    client = self.context.provider_client

    with Given("I configure a token processor with no type"):
        change_token_processors(
            processor_name="empty_proc",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=token, status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestFeature
@Name("authentication")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_AccessTokenProcessors("1.0"),
)
def feature(self):
    """Test basic OAuth authentication flows with Keycloak tokens."""
    Scenario(run=valid_token_accepted)
    Scenario(run=empty_token_rejected)
    Scenario(run=tampered_signature_rejected)
    Scenario(run=malformed_token_rejected)
    Scenario(run=valid_token_on_all_nodes)
    Scenario(run=no_token_processor_configured)
