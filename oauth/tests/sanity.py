from testflows.core import *

from helpers.common import getuid
from oauth.tests.steps.azure_application import (
    create_azure_application_with_secret,
    init_azure,
)
from oauth.tests.steps import azure_application as azure
from oauth.tests.steps import keycloak_realm as keycloak


@TestScenario
def check_authentication_flow(self):
    """Check the authentication flow with Azure AD."""
    client = self.context.provider_client
    user_name = "user_" + getuid()
    email = f"{user_name}@gmail.com"
    principal_name = f"{user_name}"
    password = getuid()

    with Given(f"I create a user in {self.context.provider}"):
        client.create_user(
            display_name=user_name,
            main_nickname=email,
            user_principal_name=principal_name,
            password=password,
        )
    with And("I create a group"):
        client.create_group()
    with And("I assign the user to the group"):
        client.assign_user_to_group()


@TestFeature
def feature(self):
    """Feature to test OAuth authentication flow."""

    Scenario(run=check_authentication_flow)
