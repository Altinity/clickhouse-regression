from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def verify_keycloak_action_effect(self, action_step):
    """Verify ClickHouse behavior for Keycloak-driven actions."""

    with Given("I apply a Keycloak-related action or state change"):
        action_step[0]()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code == action_step[1], error()

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
        (client.OAuthProvider.disable_user, 403),
        (client.OAuthProvider.delete_user, 403),
        (client.OAuthProvider.add_user_to_group, 200),
        (client.OAuthProvider.remove_user_from_group, 403),
        (client.OAuthProvider.delete_group, 403),
        (client.OAuthProvider.disable_client, 403),
        (client.OAuthProvider.revoke_consent, 403),
        (client.OAuthProvider.invalidate_token, 403),
    ]

    for step in steps:
        Check(test=verify_keycloak_action_effect)(action_step=step)


@TestFeature
@Name("groups")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
)
def feature(self):
    """Test ClickHouse role related actions."""

    Scenario(run=group_actions)
