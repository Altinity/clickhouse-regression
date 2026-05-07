"""[M-06] OpenID runtime revocation gap when ``jwks_uri`` is set.

See ``oauth/new_audit_review/all-issues.md`` (Series A, M-06) and
``DEFECT_M06`` in ``oauth/tests/defects_catalogue.py``. Legacy aliases:
F8 / TOKEN-05 in ``audit-gist.md`` — same defect.

These scenarios exercise the production-default OpenID configuration
(``jwks_uri`` + ``userinfo_endpoint`` + ``token_introspection_endpoint``
all set). In that setup,
``OpenIdTokenProcessor::resolveAndValidate``
(``src/Access/TokenProcessorsOpaque.cpp:339-414``) takes the local
JWT-fastpath and consults ``userinfo_endpoint`` only as a fallback when
local JWT decode fails. ``token_introspection_endpoint`` is parsed but
never read.

Concrete consequence: once the IdP has issued a JWT, ClickHouse keeps
accepting it for the lesser of (a) the JWT's ``exp`` and (b) any
explicit ``token_cache_lifetime`` cap that itself only bounds in-memory
cache entries — neither of which observes the IdP's runtime decisions
(disable, delete, force-revoke, group removal).

These scenarios are expected to FAIL on current antalya-26.1
(``DEFECT_M06``). They are registered in ``oauth/regression.py`` under
``xfails`` so CI surfaces them as expected failures, not regressions.
Remove the xfail entries once the upstream fix lands.

Companion scenarios in ``oauth/tests/groups.py``
(``disabled_user_rejected_after_cache``,
``deleted_user_rejected_after_cache``) exercise the same eviction path
*without* ``jwks_uri`` — i.e. they prove the fallback path works. The
scenarios here pin the bug on the production path.

Companion scenarios in ``introspection_endpoint.py`` (M-06 / 1, M-06 / 2)
pin the same defect from the config-time / endpoint-never-called angle;
the scenarios in this file (M-06 / 3, M-06 / 4) pin the runtime
security-impact angle (revocation / deletion not observed).
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


def _configure_short_cache_with_jwks(self, *, token_cache_lifetime):
    """Configure OpenID with the production-default endpoint trio.

    Uses ``jwks_uri`` + ``userinfo_endpoint`` + ``token_introspection_endpoint``,
    which is the most common deployer configuration and the path on
    which M-06 (alias F8 / TOKEN-05) manifests.
    """
    client = self.context.provider_client
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
        common_roles=["general-role"],
    )


@TestScenario
@Name("M-06 / 3 disabled user accepted with jwks_uri")
def disabled_user_accepted_after_cache_with_jwks(self):
    """[M-06]
    With ``jwks_uri`` set, a disabled IdP user's previously-cached
    token SHOULD be rejected after the token cache expires, but
    ClickHouse keeps accepting it because the JWT-fastpath re-decodes
    the still-signature-valid, still-unexpired token without consulting
    ``userinfo_endpoint`` or ``token_introspection_endpoint``.

    Asserts the *correct* security behavior (rejection). Currently
    expected to fail until M-06 is fixed upstream.
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
        with And(
            "I configure OpenID with jwks_uri set "
            "(production default — exercises the JWT-fastpath)"
        ):
            _configure_short_cache_with_jwks(self, token_cache_lifetime=cache_lifetime)

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
@Name("M-06 / 4 deleted user accepted with jwks_uri")
def deleted_user_accepted_after_cache_with_jwks(self):
    """[M-06]
    Same as scenario M-06 / 3 but the IdP user is deleted rather than
    disabled. The JWT-fastpath does not observe the deletion either —
    ``userinfo_endpoint`` would 401 for a deleted user, but it is never
    consulted while local JWKS verification still succeeds against the
    issued JWT.
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
        with And(
            "I configure OpenID with jwks_uri set "
            "(production default — exercises the JWT-fastpath)"
        ):
            _configure_short_cache_with_jwks(self, token_cache_lifetime=cache_lifetime)

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
    """[M-06] OpenID runtime revocation gap with ``jwks_uri`` set.

    Distinct feature name from ``introspection_endpoint.py``'s
    ``M-06`` feature so testflows can host both at the same level.
    Both features pin the same defect from different angles.
    """
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
