from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def verify_keycloak_auth_flow(self, auth_step):
    """Verify Keycloak authentication role/group behavior."""

    with Given("I set Keycloak authentication-related configuration or state"):
        auth_step()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        # response = access_clickhouse(token=token)
        # assert response.status_code == 200, error()
        pass

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestSketch(Scenario)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserDirectories_UserGroups("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_MultipleGroups("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoGroups("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SubgroupMemberships("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoMatchingClickHouseRoles("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SameName("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoMatchingRoles("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoPermissionToViewGroups("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoDefaultRole("1.0"),
)
def auth_scenarios(self):
    """Check Keycloak authentication requirements."""
    client = self.context.provider_client

    configurations = [
        client.OAuthProvider.auth_user_directories_user_groups,
        client.OAuthProvider.auth_user_roles,
        client.OAuthProvider.auth_user_roles_group_filtering,
        client.OAuthProvider.auth_user_roles_multiple_groups,
        client.OAuthProvider.auth_user_roles_no_groups,
        client.OAuthProvider.auth_user_roles_subgroup_memberships,
        client.OAuthProvider.auth_user_roles_no_matching_clickhouse_roles,
        client.OAuthProvider.auth_user_roles_same_name,
        client.OAuthProvider.auth_user_roles_no_matching_roles,
        client.OAuthProvider.auth_user_roles_no_permission_to_view_groups,
        client.OAuthProvider.auth_user_roles_no_default_role,
    ]

    for step in configurations:
        verify_keycloak_auth_flow(auth_step=step)


@TestFeature
@Name("authentication")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
)
def feature(self):
    """Feature to test Keycloak authentication requirements."""

    Scenario(run=auth_scenarios)
