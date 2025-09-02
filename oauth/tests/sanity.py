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
        token = client.OAuthProvider.get_oauth_token()
    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code == 200, error()


@TestFeature
@Requirements(
    RQ_SRS_042_OAuth_Azure_Token_Supported("1.0"),
    RQ_SRS_042_OAuth_Azure_GetAccessToken("1.0"),
    RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"),
)
def feature(self):
    """Feature to test OAuth authentication flow."""

    Scenario(run=check_authentication_flow)
