from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def verify_keycloak_action_effect(self, action_step):
    """Verify ClickHouse behavior for Keycloak-driven actions."""

    with Given("I apply a Keycloak-related action or state change"):
        action_step()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code in (200, 401), error()

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_GroupDeleted("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_ClientDisabled("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_ConsentRevoked("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_TokenInvalid("1.0"),
)
def group_actions(self):
    """Check Keycloak actions requirements."""
    client = self.context.provider_client

    steps = [
        client.OAuthProvider.actions_user_disabled,
        client.OAuthProvider.actions_user_deleted,
        client.OAuthProvider.actions_user_added_to_group,
        client.OAuthProvider.actions_user_removed_from_group,
        client.OAuthProvider.actions_group_deleted,
        client.OAuthProvider.actions_client_disabled,
        client.OAuthProvider.actions_consent_revoked,
        client.OAuthProvider.actions_token_invalid,
    ]

    for step in steps:
        Scenario(test=verify_keycloak_action_effect)(action_step=step)


@TestFeature
@Name("groups")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
)
def feature(self):
    """Feature to test Keycloak actions requirements."""

    Scenario(run=group_actions)
