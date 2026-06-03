"""Group-based role-mapping and identity-management tests.

All identity-provider operations (``create_user`` etc.) are routed
through ``self.context.provider_client.OAuthProvider`` so the same
scenarios apply to any provider that implements the contract. Providers
that cannot automate a given operation raise ``UnsupportedByProvider``;
the affected scenarios ``Skip`` automatically rather than fail.
"""

import time

from helpers.common import getuid
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from oauth.tests.steps.provider_protocol import UnsupportedByProvider
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SameName("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
)
def group_name_matches_clickhouse_role(self):
    """When an IdP group name matches a ClickHouse role, the user SHALL
    receive that role's privileges.
    """
    client = self.context.provider_client

    with Given("the default 'demo' user is in groups 'grafana-admins' and 'can-read'"):
        note("Pre-configured in realm-export.json")

    with And(
        "I configure user directories with roles_filter='can-read' and "
        "no common_roles"
    ):
        change_user_directories_config(
            processor="keycloak",
            roles_filter="can-read",
        )

    with And("I get a token for 'demo'"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("the privilege granted by 'can-read' is exercisable"):
        access_clickhouse(
            token=token,
            status_code=200,
            query="SELECT count() FROM system.roles",
        )

    with And("a privilege NOT granted by 'can-read' is denied"):
        assert_query_denied(token=token, query="SELECT count() FROM system.users")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
)
def roles_filter_limits_groups(self):
    """Only IdP groups matching ``roles_filter`` SHALL be considered for
    role mapping; non-matching groups SHALL NOT contribute privileges.
    """
    client = self.context.provider_client

    with Given(
        "I configure roles_filter to only match 'grafana-admins' and "
        "leave common_roles empty"
    ):
        change_user_directories_config(
            processor="keycloak",
            roles_filter="^grafana-.*$",
        )

    with And("I get a token for 'demo' (in 'grafana-admins' and 'can-read')"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("the privilege granted by the matching group is exercisable"):
        access_clickhouse(
            token=token,
            status_code=200,
            query="SELECT count() FROM system.users",
        )

    with And("the privilege granted only by the filtered-out group is denied"):
        assert_query_denied(token=token, query="SELECT count() FROM system.roles")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
)
def roles_filter_excludes_user_groups(self):
    """A user whose groups don't match the roles_filter and who has no
    common_roles SHALL authenticate but not gain any role-bound privileges.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"excluded_{uid}"

    with Given(f"I create a user '{username}' with no groups"):
        provider_user(username=username)

    with And(
        "I configure roles_filter so that *no* IdP group matches it "
        "and no common_roles are granted"
    ):
        change_user_directories_config(
            processor="keycloak",
            roles_filter="^matches-nothing-$",
        )

    with And(f"I get a token for '{username}'"):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then("ClickHouse authenticates the user"):
        access_clickhouse(token=token, status_code=200)

    with And("the user has no privileges (cannot read system tables a guest can't)"):
        assert_query_denied(token=token, query="SELECT * FROM system.users LIMIT 1")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoGroups("1.0"),
)
def user_with_no_groups_gets_common_roles(self):
    """A user with no groups SHALL receive only ``common_roles``."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"nogroups_{uid}"

    with Given(f"I create a user '{username}' with no group memberships"):
        provider_user(username=username)

    with And("I configure user directories with common_roles=['general-role']"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And(f"I get a token for '{username}'"):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then("the privilege granted by 'general-role' is exercisable"):
        access_clickhouse(
            token=token,
            status_code=200,
            query="SELECT count() FROM default.test_table_1",
        )

    with And("a privilege NOT granted by 'general-role' is denied"):
        assert_query_denied(token=token, query="SELECT count() FROM system.users")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoDefaultRole("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    ),
)
def user_with_no_groups_and_no_common_roles(self):
    """A user with no groups and no ``common_roles`` SHALL authenticate
    but have no privileges.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"norole_{uid}"

    with Given(f"I create a user '{username}' with no group memberships"):
        provider_user(username=username)

    with And("I configure user directories with empty common_roles"):
        change_user_directories_config(
            processor="keycloak",
        )

    with And(f"I get a token for '{username}'"):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then("ClickHouse authenticates the user"):
        access_clickhouse(token=token, status_code=200)

    with And("but the user has no privileges"):
        assert_query_denied(token=token, query="SELECT * FROM system.users LIMIT 1")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_MultipleGroups("1.0"),
)
def user_in_multiple_groups(self):
    """A user in multiple matching groups SHALL receive the union of all
    mapped role privileges.
    """
    client = self.context.provider_client

    with Given("'demo' user is in both 'grafana-admins' and 'can-read'"):
        note("Pre-configured in realm-export.json")

    with And(
        "I configure user directories without a restrictive filter and no common_roles"
    ):
        change_user_directories_config(
            processor="keycloak",
        )

    with And("I get a token for 'demo'"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("the privilege granted by 'grafana-admins' is exercisable"):
        access_clickhouse(
            token=token,
            status_code=200,
            query="SELECT count() FROM system.users",
        )

    with And("the privilege granted by 'can-read' is also exercisable"):
        access_clickhouse(
            token=token,
            status_code=200,
            query="SELECT count() FROM system.roles",
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup("1.0"),
)
def dynamic_group_membership_update(self):
    """Adding or removing a user from a group SHALL change their effective
    role set on the next token issued after the change.

    For JWT-issuing IdPs, the ``groups`` claim is frozen at token signing
    time, so the contract is "the next token reflects the new groups"
    rather than "the same token updates via cache expiry".
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"dyngrp_{uid}"

    cache_lifetime = 3
    privileged_query = "SELECT count() FROM system.users"

    with Given(f"I create user '{username}'"):
        provider_user(username=username)

    with And("I look up the created user's id"):
        try:
            user = client.OAuthProvider.get_user_by_username(username=username)
        except UnsupportedByProvider as e:
            skip(str(e))
        assert user is not None, error()
        user_id = user["id"]

    with And("I configure a short token-cache lifetime"):
        configure_openid_token_processor(
            token_cache_lifetime=cache_lifetime,
            common_roles=["general-role"],
        )

    with And("I look up the existing 'grafana-admins' group"):
        try:
            group = client.OAuthProvider.get_group_by_name(group_name="grafana-admins")
        except UnsupportedByProvider as e:
            skip(str(e))
        assert group is not None, error()
        group_id = group["id"]

    with When("I get a token before adding the user to any group"):
        token_before = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then(
        "the privileged query is denied " "(user has only common_roles → general-role)"
    ):
        assert_query_denied(token=token_before, query=privileged_query)

    with When(f"I add '{username}' to 'grafana-admins'"):
        client.OAuthProvider.assign_user_to_group(user_id=user_id, group_id=group_id)

    with And(
        "I get a fresh token after the group assignment "
        "(JWT groups claim reflects current membership at issue time)"
    ):
        token_admin = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then(
        "the privileged query succeeds with the new token "
        "(user is now in grafana-admins)"
    ):
        access_clickhouse(token=token_admin, status_code=200, query=privileged_query)

    with When(f"I remove '{username}' from 'grafana-admins'"):
        client.OAuthProvider.remove_user_from_group(user_id=user_id, group_id=group_id)

    with And(
        "I wait past the token cache lifetime "
        f"({cache_lifetime + 1}s) so the cached entry for "
        "token_admin would be re-validated on use"
    ):
        time.sleep(cache_lifetime + 1)

    with And("I get a fresh token after the group removal"):
        token_after = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123"
        ).access_token

    with Then(
        "the fresh token sees the membership change: " "the privileged query is denied"
    ):
        assert_query_denied(token=token_after, query=privileged_query)

    with And(
        "basic auth still works on the fresh token "
        "(the user still exists at the IdP)"
    ):
        access_clickhouse(token=token_after, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
)
def disabled_user_rejected_after_cache(self):
    """A disabled IdP user's previously-cached token SHALL be rejected
    after the token cache expires.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"disuser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        provider_user(username=username)

    with And(
        "I configure a short token-cache lifetime so cache misses "
        "re-validate against userinfo (which Keycloak makes 401 for "
        "disabled users)"
    ):
        configure_openid_token_processor(token_cache_lifetime=cache_lifetime)

    with And(
        "I get a token while the user is enabled "
        "(scope=openid is required for Keycloak's userinfo_endpoint)"
    ):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123", scope="openid"
        ).access_token

    with Then("first request succeeds (populates the cache)"):
        access_clickhouse(token=token, status_code=200)

    with When(f"I disable user '{username}' at the IdP"):
        try:
            client.OAuthProvider.disable_user(username=username)
        except UnsupportedByProvider as e:
            skip(str(e))

    with And(f"I wait past the cache lifetime ({cache_lifetime + 1}s)"):
        time.sleep(cache_lifetime + 1)

    with Then("the cached token is rejected on the next request"):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
)
def deleted_user_rejected_after_cache(self):
    """A deleted IdP user's cached token SHALL be rejected after cache
    expiry.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"deluser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        provider_user(username=username)

    with And(
        "I configure a short token-cache lifetime so cache misses "
        "re-validate against userinfo (Keycloak rejects deleted users there)"
    ):
        configure_openid_token_processor(token_cache_lifetime=cache_lifetime)

    with And(
        f"I get a token for '{username}' "
        "(scope=openid is required for Keycloak's userinfo_endpoint)"
    ):
        token = client.OAuthProvider.get_oauth_token(
            username=username, password="testpass123", scope="openid"
        ).access_token

    with Then("first request succeeds"):
        access_clickhouse(token=token, status_code=200)

    with When(f"I delete '{username}' at the IdP"):
        try:
            client.OAuthProvider.delete_user(username=username)
        except UnsupportedByProvider as e:
            skip(str(e))

    with And(f"I wait past the cache lifetime ({cache_lifetime + 1}s)"):
        time.sleep(cache_lifetime + 1)

    with Then("the cached token is rejected on the next request"):
        assert_token_rejected(token=token)


@TestFeature
@Name("groups")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
)
def feature(self):
    """Group-based role mapping and identity-management actions."""
    Scenario(run=group_name_matches_clickhouse_role)
    Scenario(run=roles_filter_limits_groups)
    Scenario(run=roles_filter_excludes_user_groups)
    Scenario(run=user_with_no_groups_gets_common_roles)
    Scenario(run=user_with_no_groups_and_no_common_roles)
    Scenario(run=user_in_multiple_groups)
    Scenario(run=dynamic_group_membership_update)
    Scenario(run=disabled_user_rejected_after_cache)
    Scenario(run=deleted_user_rejected_after_cache)
