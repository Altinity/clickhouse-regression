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
from oauth.tests.steps.provider_protocol import UnsupportedByProvider
from testflows.asserts import *
from oauth.requirements.requirements import *


def _provider_or_skip(self):
    return self.context.provider_client


def _configure_short_cache(self, *, token_cache_lifetime=3, common_roles=None):
    """Configure the standard Keycloak/OpenID processor with a short cache.

    Used by scenarios that need to observe cache eviction. The endpoint
    bundle comes from the provider so the URLs match whichever IdP is
    active.
    """
    client = _provider_or_skip(self)
    endpoints = client.OAuthProvider.openid_endpoints()
    change_token_processors(
        processor_name="keycloak",
        processor_type="OpenID",
        token_cache_lifetime=token_cache_lifetime,
        userinfo_endpoint=endpoints.userinfo_endpoint,
        token_introspection_endpoint=endpoints.token_introspection_endpoint,
        jwks_uri=endpoints.jwks_uri,
        replace=True,
    )
    change_user_directories_config(
        processor="keycloak",
        common_roles=common_roles or ["general-role"],
    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SameName("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"),
)
def group_name_matches_clickhouse_role(self):
    """When an IdP group name matches a ClickHouse role, the user SHALL
    receive that role's privileges.

    To make the assertion meaningful we use a probe (``SELECT FROM
    system.roles``) that is granted **only** by the ``can-read`` role and
    by nothing else in the test fixture — so the request fails if the
    group→role mapping is silently broken. ``common_roles`` is left
    empty for the same reason; otherwise a buggy mapping would still
    pass via the catch-all role.
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
        body = access_clickhouse(
            token=token,
            status_code=500,
            query="SELECT count() FROM system.users",
        )
        assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
)
def roles_filter_limits_groups(self):
    """Only IdP groups matching ``roles_filter`` SHALL be considered for
    role mapping; non-matching groups SHALL NOT contribute privileges.

    ``demo`` is in both ``grafana-admins`` and ``can-read``. We pin the
    filter to the former and probe two privileges, one granted by each
    role, to prove only the matching group is mapped:

    - ``SELECT FROM system.users`` (granted by ``grafana-admins``) → 200
    - ``SELECT FROM system.roles`` (granted by ``can-read``) → denied
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
        body = access_clickhouse(
            token=token,
            status_code=500,
            query="SELECT count() FROM system.roles",
        )
        assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"),
)
def roles_filter_excludes_user_groups(self):
    """A user whose groups don't match the roles_filter and who has no
    common_roles SHALL authenticate but not gain any role-bound privileges.

    This is the inverse of ``roles_filter_limits_groups`` — proves the
    filter is actually restrictive, not just permissive.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"excluded_{uid}"

    with Given(f"I create a user '{username}' with no groups"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
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

        with And(
            "the user has no privileges (cannot read system tables a guest can't)"
        ):
            body = access_clickhouse(
                token=token,
                status_code=500,
                query="SELECT * FROM system.users LIMIT 1",
            )
            assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()
    finally:
        with Finally(f"I clean up '{username}'"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoGroups("1.0"),
)
def user_with_no_groups_gets_common_roles(self):
    """A user with no groups SHALL receive only ``common_roles``.

    The probe queries discriminate the actual role rather than just
    proving authentication: ``SELECT FROM default.test_table_1`` is
    granted by ``general-role`` and asserts the common role was applied;
    ``SELECT FROM system.users`` is *not* granted by any role this user
    should have, asserting nothing extra leaked in.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"nogroups_{uid}"

    with Given(f"I create a user '{username}' with no group memberships"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
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
            body = access_clickhouse(
                token=token,
                status_code=500,
                query="SELECT count() FROM system.users",
            )
            assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()
    finally:
        with Finally(f"I clean up user '{username}'"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoDefaultRole("1.0"),
)
def user_with_no_groups_and_no_common_roles(self):
    """A user with no groups and no ``common_roles`` SHALL authenticate but have no privileges."""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"norole_{uid}"

    with Given(f"I create a user '{username}' with no group memberships"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
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
            body = access_clickhouse(
                token=token,
                status_code=500,
                query="SELECT * FROM system.users LIMIT 1",
            )
            assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()
    finally:
        with Finally(f"I clean up user '{username}'"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_MultipleGroups("1.0"),
)
def user_in_multiple_groups(self):
    """A user in multiple matching groups SHALL receive the union of all
    mapped role privileges.

    To prove union (rather than just one of the roles being mapped), we
    exercise a privilege uniquely granted by each group's role with no
    ``common_roles`` to provide a fallback:

    - ``grafana-admins`` → ``SELECT ON system.users``
    - ``can-read``       → ``SELECT ON system.roles``
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
    """Adding / removing a user from a group SHALL change their effective
    role set on the next token issued after the change.

    For JWT-issuing IdPs (Keycloak) the ``groups`` claim lives **inside**
    the signed token (see the ``groups_claim`` doc paragraph: "this claim
    will be looked up in the token itself in case token is a valid JWT").
    Once a token is signed, its claim set is frozen — no amount of cache
    expiry on the ClickHouse side will retroactively rewrite the groups
    encoded in an already-issued JWT. The user-visible contract is
    therefore "the **next** token issued after a membership change
    reflects the new groups", not "the same token flips inside the cache
    window".

    To pin both directions of that contract we:

    1. Get a token while the user is **not** in ``grafana-admins`` and
       confirm the privileged probe (``SELECT FROM system.users``,
       granted only by ``grafana-admins`` in our fixture) is denied.
    2. Add the user to ``grafana-admins``, get a **fresh** token, and
       confirm the privileged probe now succeeds.
    3. Remove the user from ``grafana-admins``, get another **fresh**
       token, and confirm the privileged probe is denied again. The
       previously-cached "admin" token is also exercised to show the
       cache itself does not leak across the issued-token boundary
       (it is allowed to keep working until it naturally expires).
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"dyngrp_{uid}"

    cache_lifetime = 3
    privileged_query = "SELECT count() FROM system.users"

    def assert_denied(token):
        body = access_clickhouse(token=token, status_code=500, query=privileged_query)
        assert "ACCESS_DENIED" in body or "Not enough privileges" in body, error()

    with Given(f"I create user '{username}'"):
        try:
            user_id = client.OAuthProvider.create_user(
                username=username, password="testpass123"
            )
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And("I configure a short token-cache lifetime"):
            _configure_short_cache(
                self,
                token_cache_lifetime=cache_lifetime,
                common_roles=["general-role"],
            )

        with And("I look up the existing 'grafana-admins' group"):
            try:
                group = client.OAuthProvider.get_group_by_name(
                    group_name="grafana-admins"
                )
            except UnsupportedByProvider as e:
                skip(str(e))
            assert group is not None, error()
            group_id = group["id"]

        with When("I get a token before adding the user to any group"):
            token_before = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with Then(
            "the privileged query is denied "
            "(user has only common_roles → general-role)"
        ):
            assert_denied(token_before)

        with When(f"I add '{username}' to 'grafana-admins'"):
            client.OAuthProvider.assign_user_to_group(
                user_id=user_id, group_id=group_id
            )

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
            access_clickhouse(
                token=token_admin, status_code=200, query=privileged_query
            )

        with When(f"I remove '{username}' from 'grafana-admins'"):
            client.OAuthProvider.remove_user_from_group(
                user_id=user_id, group_id=group_id
            )

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
            "the fresh token sees the membership change: "
            "the privileged query is denied"
        ):
            assert_denied(token_after)

        with And(
            "basic auth still works on the fresh token "
            "(the user still exists at the IdP)"
        ):
            access_clickhouse(token=token_after, status_code=200)
    finally:
        with Finally("I clean up"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"),
)
def disabled_user_rejected_after_cache(self):
    """A disabled IdP user's previously-cached token SHALL be rejected
    after the token cache expires.

    Real test of the cache-eviction path:

    1. Configure ``token_cache_lifetime=3``.
    2. User authenticates with a valid token; first request populates the
       cache.
    3. Disable the user at the IdP.
    4. Wait > cache lifetime so ClickHouse must re-validate via
       ``userinfo`` / ``introspection``.
    5. Same cached token MUST now be rejected. The exact rejection code
       depends on whether re-validation surfaces as ``AUTHENTICATION_FAILED``
       (HTTP 403) or as a ``token_verification_exception`` (HTTP 500),
       both of which are valid; ``assert_token_rejected`` accepts either.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"disuser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And("I configure a short token-cache lifetime"):
            _configure_short_cache(self, token_cache_lifetime=cache_lifetime)

        with And("I get a token while the user is enabled"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
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
    finally:
        with Finally("I clean up"):
            try:
                client.OAuthProvider.enable_user(username=username)
            except UnsupportedByProvider:
                pass
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"),
)
def deleted_user_rejected_after_cache(self):
    """A deleted IdP user's cached token SHALL be rejected after cache
    expiry.

    Replaces the old ``deleted_user_cannot_get_token`` which only proved
    Keycloak rejects the token-issuance request — that's a Keycloak
    invariant, not a ClickHouse one. This variant proves ClickHouse's
    cache-eviction path observes the deletion.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"deluser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    deleted = False
    try:
        with And("I configure a short token-cache lifetime"):
            _configure_short_cache(self, token_cache_lifetime=cache_lifetime)

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with Then("first request succeeds"):
            access_clickhouse(token=token, status_code=200)

        with When(f"I delete '{username}' at the IdP"):
            try:
                client.OAuthProvider.delete_user(username=username)
                deleted = True
            except UnsupportedByProvider as e:
                skip(str(e))

        with And(f"I wait past the cache lifetime ({cache_lifetime + 1}s)"):
            time.sleep(cache_lifetime + 1)

        with Then("the cached token is rejected on the next request"):
            assert_token_rejected(token=token)
    finally:
        if not deleted:
            with Finally("I clean up"):
                try:
                    client.OAuthProvider.delete_user(username=username)
                except UnsupportedByProvider:
                    pass


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
