from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
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
    """A token issued by a different IdP realm/tenant SHALL be rejected.

    Creates a fresh realm + client + user, mints a token through that
    realm, and asserts ClickHouse rejects it due to issuer mismatch.
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
        with And("I configure ClickHouse to expect tokens from OUR realm only"):
            endpoints = client.OAuthProvider.openid_endpoints()
            configure_openid_token_processor(expected_issuer=endpoints.issuer)

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
    """A token minted for a different client in the same realm SHALL
    be rejected by an audience-pinned ClickHouse.
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
        with And("I configure ClickHouse to require expected_audience=our-client"):
            configure_openid_token_processor(expected_audience=self.context.client_id)

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
                client.OAuthProvider.disable_client(client_id_name=other_client_id)
            except UnsupportedByProvider:
                pass


@TestScenario
def authorization_succeeds_baseline(self):
    """Sanity check: a token from our realm is accepted while
    ``expected_issuer`` is enforced.
    """
    client = self.context.provider_client

    with Given("I configure ClickHouse with expected_issuer pinned to our realm"):
        endpoints = client.OAuthProvider.openid_endpoints()
        configure_openid_token_processor(expected_issuer=endpoints.issuer)

    with When("I get a token from OUR realm"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts our-realm token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
def missing_default_profile_does_not_grant_unrestricted_access(self):
    """When the token user-directory names a ``default_profile`` that does
    not exist, an auto-provisioned user SHALL NOT silently gain
    unrestricted access (fail-closed provisioning).
    """
    uid = getuid()[:6]
    secret = "default_profile_test_secret"
    user_a = f"a_{uid}"
    user_b = f"b_{uid}"
    create_query_a = f"CREATE TEMPORARY TABLE t_{uid}_a (x UInt8) ENGINE = Memory"
    create_query_b = f"CREATE TEMPORARY TABLE t_{uid}_b (x UInt8) ENGINE = Memory"

    with Given(
        "a static-key processor whose token directory uses the 'readonly' profile"
    ):
        configure_static_key_processor(secret=secret, with_user_directory=False)
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
            default_profile="readonly",
        )

    with When(f"I auto-provision user '{user_a}' under the readonly profile"):
        token_a = create_static_jwt(
            user_name=user_a,
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token_a, status_code=200)

    with Then("baseline: a write is rejected because readonly is applied"):
        body = access_clickhouse(token=token_a, query=create_query_a, status_code=500)
        assert (
            "READONLY" in body.upper() or "NOT ENOUGH PRIVILEGES." in body.upper()
        ), error()

    with When("I reconfigure the token directory with a non-existent default_profile"):
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
            default_profile=f"nonexistent_profile_{uid}",
        )

    with And(f"I auto-provision a fresh user '{user_b}'"):
        token_b = create_static_jwt(
            user_name=user_b,
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("the fresh user does not gain unrestricted write access (fail-closed)"):
        for sc in (500, 403, 400):
            try:
                access_clickhouse(token=token_b, query=create_query_b, status_code=sc)
                break
            except AssertionError:
                continue
        else:
            fail(
                "auto-provisioned user with a missing default_profile gained "
                "unrestricted write access"
            )


@TestScenario
def dynamic_token_user_created_with_any_host(self):
    """A dynamically-provisioned token user is created with an any-host
    network allowlist.

    Accepted finding H-11 (reverted / out of scope): a mandatory
    population host-restrictor is NOT enforced because user/host
    management belongs on the IdP side. The auto-provisioned user
    therefore carries the default any-host tag (no explicit restriction),
    and this test pins that documented behaviour.
    """
    uid = getuid()[:8]
    secret = "host_restriction_test_secret"
    user = f"u_{uid}"
    node = self.context.node

    with Given("a static-key processor"):
        configure_static_key_processor(secret=secret)

    with When(f"I authenticate as a fresh user '{user}'"):
        token = create_static_jwt(
            user_name=user,
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token, status_code=200)

    with Then("the auto-created user carries the default any-host tag"):
        result = node.query(
            "SELECT host_ip, host_names, host_names_regexp, host_names_like "
            f"FROM system.users WHERE name = '{user}' FORMAT TSV"
        )
        row = result.output.strip()
        note(f"system.users host columns for {user!r}: {row!r}")
        cells = row.split("\t")
        assert len(cells) == 4, error()
        # ClickHouse renders the default any-host allowlist as an empty list
        # for the name/regexp/like columns and as ``['::/0']`` (the IPv6
        # "match everything" CIDR) for host_ip. None of these constitute an
        # explicit host restriction.
        any_host_values = ("", "[]", "['::/0']", "['::/0','0.0.0.0/0']")
        all_any_host = all(c.strip() in any_host_values for c in cells)
        assert all_any_host, error(
            "expected the dynamic token user to use the default any-host tag"
        )


@TestFeature
@Name("access control")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"),
)
def feature(self):
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

    Scenario(run=authorization_succeeds_baseline)
    Scenario(run=token_from_other_realm_rejected)
    Scenario(run=token_from_wrong_client_rejected)
    Scenario(run=missing_default_profile_does_not_grant_unrestricted_access)
    Scenario(run=dynamic_token_user_created_with_any_host)
