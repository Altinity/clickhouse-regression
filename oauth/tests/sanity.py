from oauth.tests.steps.clikhouse import *
from testflows.asserts import *


@TestScenario
def check_authentication_flow(self):
    """Check the authentication flow with Azure AD."""
    client = self.context.provider_client

    with Given(f"I get an OAuth token from {self.context.provider_name}"):
        token = client.OAuthProvider.get_oauth_token()
    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code == 200, error()


@TestFeature
def feature(self):
    """Feature to test OAuth authentication flow."""

    Scenario(run=check_authentication_flow)
