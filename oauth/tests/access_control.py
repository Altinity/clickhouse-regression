"""Authorization-negative scenarios.

These tests prove ClickHouse correctly rejects tokens issued from a
trust boundary it should not accept:

- Wrong realm (Keycloak) / wrong tenant (Azure) — "user from another org"
- Wrong client / wrong audience — "user is in our IdP but not in our app"
- ``email_verified=false`` — identity exists but the email-ownership
  check failed at the IdP

Tokens are minted by the *actual IdP* (not by JWT mutation) so the
scenarios exercise the same code path that runs in production.
"""

from helpers.common import getuid
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.provider_protocol import UnsupportedByProvider
from testflows.asserts import *
from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer,
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience,
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"))
def token_from_other_realm_rejected(self):
    """A token issued by a *different* IdP realm/tenant SHALL be rejected.

    Concretely (Keycloak): we create a fresh realm + client + user via
    the Admin API, mint a token through that realm, and assert
    ClickHouse rejects it because the ``iss`` claim does not match the
    ``expected_issuer`` configured for our processor. This is the
    canonical "user from another organisation tries to log in" check.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    other_realm = f"other_realm_{uid}"
    other_client_id = f"other-client-{uid}"
    other_client_secret = f"other-secret-{uid}"
    other_username = f"outsider_{uid}"

    with Given("I create a separate realm + client + user at the IdP"):
        try:
            client.OAuthProvider.create_realm(realm_name=other_realm)
            client.OAuthProvider.create_client_in_realm(
                realm_name=other_realm,
                client_id=other_client_id,
                client_secret=other_client_secret,
                direct_access_grants_enabled=True,
            )
            client.OAuthProvider.create_user(
                username=other_username,
                password="testpass123",
                realm_name=other_realm,
            )
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And(
            "I configure ClickHouse to expect tokens from OUR realm only"
        ):
            endpoints = client.OAuthProvider.openid_endpoints()
            change_token_processors(
                processor_name="keycloak",
                processor_type="OpenID",
                expected_issuer=endpoints.issuer,
                userinfo_endpoint=endpoints.userinfo_endpoint,
                token_introspection_endpoint=endpoints.token_introspection_endpoint,
                jwks_uri=endpoints.jwks_uri,
                replace=True,
            )
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
            )

        with When("I get a token from the OTHER realm"):
            outsider_token = client.OAuthProvider.get_oauth_token_for_client(
                client_id=other_client_id,
                client_secret=other_client_secret,
                realm_name=other_realm,
                username=other_username,
                password="testpass123",
            ).access_token

        with Then("ClickHouse rejects the cross-realm token"):
            assert_token_rejected(token=outsider_token)
    finally:
        with Finally("I clean up the other realm"):
            try:
                client.OAuthProvider.delete_realm(realm_name=other_realm)
            except UnsupportedByProvider:
                pass


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"),
)
def token_from_wrong_client_rejected(self):
    """A token minted for a *different* client in the same realm SHALL
    be rejected by an audience-pinned ClickHouse.

    "Same IdP, different application." The user has a perfectly valid
    SSO identity, but their token's ``aud`` claim is for a different
    OAuth client — say, the marketing dashboard — and ClickHouse is
    pinned to ``expected_audience=our-client``.

    Status-code note: depending on how Keycloak shapes the token, the
    other client's token may either:

    - have an ``aud`` claim but with a different value → ClickHouse
      returns HTTP 403 (AUTHENTICATION_FAILED), or
    - have no ``aud`` claim at all (Keycloak default for a vanilla
      client without an Audience protocol mapper) → ClickHouse returns
      HTTP 500 with ``token_verification_exception: decoded JWT is
      missing required claim(s)``.

    Both outcomes prove the gate works. We assert on the body marker
    rather than only on the status code so the test isn't fragile
    against either shape.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    other_client_id = f"other-app-{uid}"
    other_client_secret = f"other-app-secret-{uid}"

    with Given("I register a second OIDC client in the same realm"):
        try:
            client.OAuthProvider.create_client_in_realm(
                realm_name=self.context.realm_name,
                client_id=other_client_id,
                client_secret=other_client_secret,
                direct_access_grants_enabled=True,
            )
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And(
            "I configure ClickHouse to require expected_audience=our-client"
        ):
            endpoints = client.OAuthProvider.openid_endpoints()
            change_token_processors(
                processor_name="keycloak",
                processor_type="OpenID",
                expected_audience=self.context.client_id,
                userinfo_endpoint=endpoints.userinfo_endpoint,
                token_introspection_endpoint=endpoints.token_introspection_endpoint,
                jwks_uri=endpoints.jwks_uri,
                replace=True,
            )
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
            )

        with When("I get a token issued for the OTHER client"):
            try:
                other_app_token = client.OAuthProvider.get_oauth_token_for_client(
                    client_id=other_client_id,
                    client_secret=other_client_secret,
                ).access_token
            except UnsupportedByProvider as e:
                skip(str(e))

        with Then("ClickHouse rejects the wrong-audience token"):
            assert_token_rejected(token=other_app_token)
    finally:
        with Finally("I clean up the second client"):
            try:
                client.OAuthProvider.disable_client(
                    client_id_name=other_client_id
                )
            except UnsupportedByProvider:
                pass


@TestScenario
def authorization_succeeds_baseline(self):
    """Sanity check: a token from OUR realm is accepted while
    ``expected_issuer`` is enforced.

    Pairs with ``token_from_other_realm_rejected`` to prove the
    issuer-pinning gate doesn't reject *legitimate* tokens.
    """
    client = self.context.provider_client

    with Given("I configure ClickHouse with expected_issuer pinned to our realm"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            expected_issuer=endpoints.issuer,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
            replace=True,
        )
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with When("I get a token from OUR realm"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts our-realm token"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("access control")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"),
)
def feature(self):
    """Authorization-negative scenarios using real IdP-issued tokens."""
    Scenario(run=authorization_succeeds_baseline)
    Scenario(run=token_from_other_realm_rejected)
    Scenario(run=token_from_wrong_client_rejected)
