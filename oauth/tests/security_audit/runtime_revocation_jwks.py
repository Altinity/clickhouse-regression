"""[M-06] OpenID runtime revocation — disabled/deleted user rejection.

See ``oauth/new_audit_review/all-issues.md`` (Series A, M-06) and
``DEFECT_M06`` in ``oauth/tests/defects_catalogue.py``.

Since antalya-26.3 (PR #1799), the OpenID processor no longer accepts
``jwks_uri``. All token validation goes through ``userinfo_endpoint`` /
``token_introspection_endpoint``, which consult the IdP on every
non-cached request. The original M-06 defect (JWT-fastpath bypassing
runtime revocation when ``jwks_uri`` was set) is inherently fixed by
this removal.

These scenarios now verify the correct behavior: after the token cache
expires, a disabled or deleted IdP user's token SHALL be rejected
because the userinfo/introspection endpoints reflect the IdP's current
state.

Companion scenarios in ``oauth/tests/groups.py``
(``disabled_user_rejected_after_cache``,
``deleted_user_rejected_after_cache``) exercise the same eviction path.

Companion scenarios in ``introspection_endpoint.py`` (M-06 / 1, M-06 / 2)
test endpoint reachability from a configuration angle.
"""

import time

from testflows.core import *

from helpers.common import getuid

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    assert_token_rejected,
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.provider_protocol import UnsupportedByProvider


def _configure_short_cache(self, *, token_cache_lifetime):
    """Configure OpenID with userinfo and introspection endpoints."""
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()
    change_token_processors(
        processor_name="keycloak",
        processor_type="OpenID",
        token_cache_lifetime=token_cache_lifetime,
        userinfo_endpoint=endpoints.userinfo_endpoint,
        token_introspection_endpoint=endpoints.token_introspection_endpoint,
        introspection_client_id=self.context.introspection_client_id,
        introspection_client_secret=self.context.introspection_client_secret,
        replace=True,
    )
    change_user_directories_config(
        processor="keycloak",
        common_roles=["general-role"],
    )


@TestScenario
@Name("M-06 / 3 disabled user rejected after cache expiry")
def disabled_user_rejected_after_cache(self):
    """[M-06]
    After the token cache expires, a disabled IdP user's token SHALL
    be rejected because the OpenID processor now always consults
    ``userinfo_endpoint`` / ``token_introspection_endpoint`` which
    reflect the user's current state at the IdP.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"m06disuser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And("I configure OpenID with userinfo and introspection"):
            _configure_short_cache(self, token_cache_lifetime=cache_lifetime)

        with And(f"I get a token for '{username}' while enabled"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with And("the first request succeeds (populates the cache)"):
            access_clickhouse(token=token, status_code=200)

        with When(f"I disable user '{username}' at the IdP"):
            try:
                client.OAuthProvider.disable_user(username=username)
            except UnsupportedByProvider as e:
                skip(str(e))

        with And(f"I wait past the cache lifetime ({cache_lifetime + 1}s)"):
            time.sleep(cache_lifetime + 1)

        with Then(
            "ClickHouse SHALL reject the cached token "
            "(the IdP has revoked the user's authority to authenticate)"
        ):
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
@Name("M-06 / 4 deleted user rejected after cache expiry")
def deleted_user_rejected_after_cache(self):
    """[M-06]
    After the token cache expires, a deleted IdP user's token SHALL
    be rejected because the OpenID processor consults
    ``userinfo_endpoint`` / ``token_introspection_endpoint`` which
    return an error for a non-existent user.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"m06deluser_{uid}"
    cache_lifetime = 3

    with Given(f"I create user '{username}'"):
        try:
            client.OAuthProvider.create_user(username=username, password="testpass123")
        except UnsupportedByProvider as e:
            skip(str(e))

    deleted = False
    try:
        with And("I configure OpenID with userinfo and introspection"):
            _configure_short_cache(self, token_cache_lifetime=cache_lifetime)

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with And("the first request succeeds (populates the cache)"):
            access_clickhouse(token=token, status_code=200)

        with When(f"I delete user '{username}' at the IdP"):
            try:
                client.OAuthProvider.delete_user(username=username)
                deleted = True
            except UnsupportedByProvider as e:
                skip(str(e))

        with And(f"I wait past the cache lifetime ({cache_lifetime + 1}s)"):
            time.sleep(cache_lifetime + 1)

        with Then(
            "ClickHouse SHALL reject the cached token "
            "(the user no longer exists at the IdP)"
        ):
            assert_token_rejected(token=token)
    finally:
        with Finally("I clean up"):
            if not deleted:
                try:
                    client.OAuthProvider.delete_user(username=username)
                except UnsupportedByProvider:
                    pass


@TestFeature
@Name("M-06 runtime revocation")
def feature(self):
    """[M-06] OpenID runtime revocation — disabled/deleted user rejection.

    Distinct feature name from ``introspection_endpoint.py``'s
    ``M-06`` feature so testflows can host both at the same level.
    """
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
