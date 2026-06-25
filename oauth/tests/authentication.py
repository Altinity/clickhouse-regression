from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *
from helpers.workload import background_workload


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"),
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
)
def valid_token_accepted(self):
    """ClickHouse SHALL accept a valid Keycloak access token over HTTP."""
    client = self.context.provider_client

    with Given("I get a valid OAuth token from the provider"):
        token = client.OAuthProvider.get_oauth_token().access_token

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
        token = client.OAuthProvider.get_oauth_token().access_token
        token = token[:-4] + "7b39"

    with Then("ClickHouse rejects the tampered token"):
        access_clickhouse_when_forbidden(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
)
def wrong_auth_header_ignored(self):
    """ClickHouse SHALL NOT grant the OAuth identity when a valid token is
    supplied under a non-standard header (``Authentication`` instead of
    ``Authorization``): the bearer credential is only read from the
    ``Authorization`` header, so the request falls back to the
    unauthenticated ``default`` user rather than the token's subject.
    """
    client = self.context.provider_client

    with Given("I get a valid OAuth token from the provider"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with And("I confirm the token authenticates under the 'Authorization' header"):
        authorized_user = access_clickhouse(token=token, status_code=200).strip()
        assert authorized_user and authorized_user != "default", error()

    with Then(
        "ClickHouse ignores the token under the 'Authentication' header and "
        "runs the request as the unauthenticated 'default' user"
    ):
        body = access_clickhouse(
            token=token,
            status_code=200,
            header=f"Authentication: Bearer {token}",
        ).strip()
        assert body == "default", error(
            f"expected unauthenticated fallback to 'default', got '{body}'"
        )

    with And("the OAuth identity was not granted via the wrong header"):
        assert body != authorized_user, error()

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
)
def malformed_token_rejected(self):
    """ClickHouse SHALL reject a completely malformed token."""
    with Then("ClickHouse rejects the garbage token"):
        access_clickhouse(token="not.a.valid-jwt", status_code=403)

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
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("every node accepts the token"):
        access_clickhouse_on_all_nodes(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserRoles_NoAccessTokenProcessors("1.0"),
)
def no_token_processor_configured(self):
    """ClickHouse SHALL reject auth when no valid token processor is defined."""
    client = self.context.provider_client

    with Given("I replace the keycloak processor with an empty one"):
        change_token_processors(
            processor_name="keycloak",
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
def bearer_token_not_exposed_via_client_http_header(self):
    """The bearer ``Authorization`` header SHALL NOT be retained in
    ``client_info.http_headers``: reading it back via
    ``getClientHTTPHeader('Authorization')`` SHALL NOT return the raw
    token, so the credential cannot be exfiltrated through SQL.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "the raw token is not retrievable via " "getClientHTTPHeader('Authorization')"
    ):
        body = access_clickhouse(
            token=token,
            status_code=200,
            query=(
                "SELECT getClientHTTPHeader('Authorization') "
                "SETTINGS allow_get_client_http_header=1"
            ),
        )
        assert token not in body, error(
            "bearer token leaked via getClientHTTPHeader('Authorization')"
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"),
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
)
def valid_token_accepted_under_load(self):
    """ClickHouse SHALL accept a valid OAuth token while the server is under realistic workload."""
    client = self.context.provider_client
    node = self.context.node

    with background_workload(node, intensity="medium"):
        with Given("I get a valid OAuth token from the provider"):
            token = client.OAuthProvider.get_oauth_token().access_token

        with Then("ClickHouse accepts the token under load"):
            body = access_clickhouse(token=token, status_code=200)

        with And("the response contains a user identity"):
            assert len(body) > 0, error()

        with And("a second authentication also succeeds under load"):
            token2 = client.OAuthProvider.get_oauth_token().access_token
            access_clickhouse(token=token2, status_code=200)


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
    Scenario(run=wrong_auth_header_ignored)
    Scenario(run=malformed_token_rejected)
    Scenario(run=valid_token_on_all_nodes)
    Scenario(run=no_token_processor_configured)
    Scenario(run=bearer_token_not_exposed_via_client_http_header)
    Scenario(run=valid_token_accepted_under_load)
