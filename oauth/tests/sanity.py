from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Credentials("1.0"), RQ_SRS_042_OAuth_Azure_ApplicationSetup("1.0")
)
def check_authentication_flow(self):
    """Check the authentication flow with Azure AD."""
    client = self.context.provider_client

    with Given(f"I get an OAuth token from {self.context.provider_name}"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("I try to access ClickHouse with the token"):
        access_clickhouse(token=token)


@TestScenario
def check_authentication_with_invalid_token(self):
    """Check ClickHouse behavior with an invalid token."""
    client = self.context.provider_client

    with Given(f"I get an OAuth token from {self.context.provider_name}"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]
        token = token[:-4] + "7b39"

    with When("I try to access ClickHouse with the invalid token"):
        access_clickhouse_when_forbidden(token=token)


@TestFeature
@Requirements(
    RQ_SRS_042_OAuth_Azure_Token_Supported("1.0"),
    RQ_SRS_042_OAuth_Azure_GetAccessToken("1.0"),
    RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"),
)
@Name("sanity")
def feature(self):
    """Feature to test OAuth authentication flow."""
    Scenario(run=check_authentication_flow)
    Scenario(run=check_authentication_with_invalid_token)
