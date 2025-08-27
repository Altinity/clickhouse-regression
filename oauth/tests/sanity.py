from testflows.core import *

from helpers.common import getuid
from oauth.tests.steps.clikhouse import *


@TestScenario
def check_authentication_flow(self):
    """Check the authentication flow with Azure AD."""
    client = self.context.provider_client

    with Given(f"I create a user in {self.context.provider_name}"):
        token = client.OAuthProvider.get_oauth_token()
        note(token)
        pause()
    with And("I create a group"):
        client.create_group()
    with And("I assign the user to the group"):
        client.assign_user_to_group()


@TestFeature
def feature(self):
    """Feature to test OAuth authentication flow."""

    Scenario(run=check_authentication_flow)
