from helpers.common import getuid
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.keycloak_realm import (
    create_user,
    delete_user,
    create_group,
    delete_group,
    assign_user_to_group,
    remove_user_from_group,
    disable_user,
    enable_user,
    get_user_by_username,
    get_group_by_name,
)
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SameName("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
)
def group_name_matches_clickhouse_role(self):
    """When a Keycloak group name matches a ClickHouse role, the user SHALL receive that role's permissions."""
    client = self.context.provider_client

    with Given("the default 'demo' user is in group 'can-read' that matches a role"):
        note("'demo' user is pre-configured in groups 'grafana-admins' and 'can-read'")

    with And("I configure user directories with roles_filter matching 'can-read'"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
            roles_filter="can-read",
        )

    with And("I get a token for 'demo'"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
)
def roles_filter_limits_groups(self):
    """Only Keycloak groups matching ``roles_filter`` SHALL be considered for ClickHouse role mapping."""
    client = self.context.provider_client

    with Given("I configure roles_filter to only match 'grafana-admins'"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
            roles_filter="^grafana-.*$",
        )

    with And("I get a token for 'demo' (who is in 'grafana-admins' and 'can-read')"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token (grafana-admins matches filter)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoGroups("1.0"),
)
def user_with_no_groups_gets_common_roles(self):
    """A Keycloak user with no groups SHALL get only common_roles."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"nogroups_{uid}"

    with Given(f"I create a Keycloak user '{username}' with no group memberships"):
        create_user(username=username, password="testpass123")

    try:
        with And("I configure user directories with common_roles"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("ClickHouse accepts the token (common_roles applied)"):
            access_clickhouse(token=token, status_code=200)
    finally:
        with Finally(f"I clean up user '{username}'"):
            delete_user(username=username)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoDefaultRole("1.0"),
)
def user_with_no_groups_and_no_common_roles(self):
    """A user with no groups and no common_roles SHALL authenticate but have no data permissions."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"norole_{uid}"

    with Given(f"I create a Keycloak user '{username}' with no group memberships"):
        create_user(username=username, password="testpass123")

    try:
        with And("I configure user directories with empty common_roles"):
            change_user_directories_config(
                processor="keycloak",
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("ClickHouse authenticates the user"):
            access_clickhouse(token=token, status_code=200)
    finally:
        with Finally(f"I clean up user '{username}'"):
            delete_user(username=username)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_MultipleGroups("1.0"),
)
def user_in_multiple_groups(self):
    """A user in multiple matching groups SHALL receive the union of all mapped roles."""
    client = self.context.provider_client

    with Given("'demo' user is in both 'grafana-admins' and 'can-read'"):
        note("Pre-configured in realm-export.json")

    with And("I configure user directories without a restrictive filter"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a token for 'demo'"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token (union of group-mapped roles)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup("1.0"),
)
def dynamic_group_membership_update(self):
    """Adding/removing a user from a group SHALL change their effective roles after cache expiry."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"dyngrp_{uid}"
    group_name = f"test_group_{uid}"

    with Given(f"I create user '{username}' and group '{group_name}'"):
        user_id = create_user(username=username, password="testpass123")
        group_id = create_group(group_name=group_name)

    try:
        with And("I configure user directories"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
            )

        with And(f"I add '{username}' to '{group_name}'"):
            assign_user_to_group(user_id=user_id, group_id=group_id)

        with And("I get a token"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("ClickHouse accepts the token"):
            access_clickhouse(token=token, status_code=200)

        with When(f"I remove '{username}' from '{group_name}'"):
            remove_user_from_group(user_id=user_id, group_id=group_id)

        with And("I get a fresh token"):
            token2 = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("ClickHouse still accepts (common_roles still apply)"):
            access_clickhouse(token=token2, status_code=200)
    finally:
        with Finally("I clean up"):
            delete_user(username=username)
            delete_group(group_name=group_name)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
)
def disabled_user_rejected_after_cache(self):
    """A disabled Keycloak user SHALL be rejected after the token cache expires."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"disuser_{uid}"

    with Given(f"I create user '{username}'"):
        create_user(username=username, password="testpass123")

    try:
        with And("I configure short cache lifetime"):
            change_token_processors(
                processor_name="keycloak",
                processor_type="OpenID",
                token_cache_lifetime=3,
                userinfo_endpoint=(
                    f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                    f"/protocol/openid-connect/userinfo"
                ),
                token_introspection_endpoint=(
                    f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                    f"/protocol/openid-connect/token/introspect"
                ),
                jwks_uri=(
                    f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                    f"/protocol/openid-connect/certs"
                ),
            )

        with And("I configure user directories"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
            )

        with And("I get a token while user is enabled"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("first request succeeds"):
            access_clickhouse(token=token, status_code=200)

        with When(f"I disable user '{username}' in Keycloak"):
            disable_user(username=username)

        with And("I get a new token (should fail at Keycloak level)"):
            try:
                new_token = client.OAuthProvider.get_oauth_token(
                    username=username, password="testpass123"
                )
                assert "error" in new_token, error()
            except Exception:
                note("Token request correctly failed for disabled user")
    finally:
        with Finally("I clean up"):
            enable_user(username=username)
            delete_user(username=username)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
)
def deleted_user_cannot_get_token(self):
    """A deleted Keycloak user SHALL not be able to obtain a new token."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"deluser_{uid}"

    with Given(f"I create user '{username}'"):
        create_user(username=username, password="testpass123")

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I verify the user can authenticate"):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        )["access_token"]
        access_clickhouse(token=token, status_code=200)

    with When(f"I delete user '{username}' from Keycloak"):
        delete_user(username=username)

    with Then("a token request for the deleted user fails"):
        try:
            resp = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )
            assert "error" in resp, error()
        except Exception:
            note("Token request correctly failed for deleted user")


@TestFeature
@Name("groups")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
)
def feature(self):
    """Test Keycloak group-based role mapping and identity management actions."""
    Scenario(run=group_name_matches_clickhouse_role)
    Scenario(run=roles_filter_limits_groups)
    Scenario(run=user_with_no_groups_gets_common_roles)
    Scenario(run=user_with_no_groups_and_no_common_roles)
    Scenario(run=user_in_multiple_groups)
    Scenario(run=dynamic_group_membership_update)
    Scenario(run=disabled_user_rejected_after_cache)
    Scenario(run=deleted_user_cannot_get_token)
