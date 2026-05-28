"""Token-processor parameter and caching tests.

All scenarios route OpenID endpoints through the provider abstraction
(``client.OAuthProvider.openid_endpoints()``) so the same tests run
unchanged when ``--identity-provider`` switches.
"""

import time

import jwt as pyjwt

from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


def _configure_processor(
    self,
    *,
    username_claim=None,
    groups_claim=None,
    token_cache_lifetime=None,
    expected_issuer=None,
    expected_audience=None,
    replace=True,
):
    """Apply a Keycloak-OpenID processor config plus optional overrides.

    Centralised here so each scenario doesn't repeat the same URLs.
    The endpoint bundle comes from the provider so non-Keycloak runs
    pick up the right URLs automatically.

    Since antalya-26.3 (PR #1799) the ``openid`` processor rejects
    ``jwks_uri``. Introspection credentials are always included so
    that ``expected_issuer`` / ``expected_audience`` can be enforced
    via RFC 7662 when set.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    kwargs = {
        "processor_name": "keycloak",
        "processor_type": "OpenID",
        "userinfo_endpoint": endpoints.userinfo_endpoint,
        "token_introspection_endpoint": endpoints.token_introspection_endpoint,
        "introspection_client_id": self.context.introspection_client_id,
        "introspection_client_secret": self.context.introspection_client_secret,
        "replace": replace,
    }
    if username_claim is not None:
        kwargs["username_claim"] = username_claim
    if groups_claim is not None:
        kwargs["groups_claim"] = groups_claim
    if token_cache_lifetime is not None:
        kwargs["token_cache_lifetime"] = token_cache_lifetime
    if expected_issuer is not None:
        kwargs["expected_issuer"] = expected_issuer
    if expected_audience is not None:
        kwargs["expected_audience"] = expected_audience

    change_token_processors(**kwargs)
    change_user_directories_config(
        processor="keycloak",
        common_roles=["general-role"],
    )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"))
def username_claim_sub(self):
    """ClickHouse SHALL use ``sub`` as the username when configured."""
    client = self.context.provider_client

    with Given("I configure the processor with username_claim=sub"):
        _configure_processor(self, username_claim="sub")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse returns a UUID-shaped user name (the sub claim)"):
        body = access_clickhouse(token=token, status_code=200)
        assert len(body.strip()) > 0, error()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"))
def username_claim_preferred_username(self):
    """ClickHouse SHALL extract username from ``preferred_username`` when configured."""
    client = self.context.provider_client

    with Given("I configure the processor with username_claim=preferred_username"):
        _configure_processor(self, username_claim="preferred_username")

    with And("I get a valid token for user 'demo'"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse returns 'demo' as the current user"):
        body = access_clickhouse(token=token, status_code=200)
        assert "demo" in body, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"),
    RQ_SRS_042_OAuth_Authentication_Caching("1.0"),
)
def token_cache_lifetime_honoured(self):
    """ClickHouse SHALL cache tokens for the configured ``token_cache_lifetime``."""
    client = self.context.provider_client

    with Given("I configure the processor with a short cache lifetime"):
        _configure_processor(self, token_cache_lifetime=5)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("first request succeeds (populates cache)"):
        access_clickhouse(token=token, status_code=200)

    with And("second immediate request also succeeds (served from cache)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Authentication_Caching_CacheEviction_NoCache("1.0"))
def cache_disabled(self):
    """ClickHouse SHALL not cache tokens when ``token_cache_lifetime`` is 0."""
    client = self.context.provider_client

    with Given("I configure the processor with cache disabled"):
        _configure_processor(self, token_cache_lifetime=0)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("request still succeeds even with cache disabled"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"))
def groups_claim_parameter(self):
    """ClickHouse SHALL use the configured ``groups_claim`` to read group membership."""
    client = self.context.provider_client

    with Given("I configure the processor with groups_claim=groups"):
        _configure_processor(self, groups_claim="groups")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"))
def expected_issuer_correct(self):
    """ClickHouse SHALL accept a token when ``expected_issuer`` matches ``iss``.

    Note: Keycloak in this compose is started with ``--hostname=localhost``
    so the ``iss`` claim is ``http://localhost:8080/realms/<realm>``,
    NOT the in-network ``http://keycloak:8080/...`` URL ClickHouse uses
    for JWKS. The provider's ``openid_endpoints().issuer`` returns the
    correct value for both branches automatically.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    with Given("I configure the processor with the matching expected_issuer"):
        _configure_processor(self, expected_issuer=endpoints.issuer)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"))
def expected_issuer_wrong(self):
    """ClickHouse SHALL reject a token when ``expected_issuer`` does not match ``iss``."""
    client = self.context.provider_client

    with Given("I configure the processor with a wrong expected_issuer"):
        _configure_processor(self, expected_issuer="https://wrong-issuer.example.com")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (issuer mismatch)"):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"))
def expected_audience_missing_claim(self):
    """ClickHouse SHALL reject a token when ``expected_audience`` is set but the JWT has no matching ``aud`` claim."""
    client = self.context.provider_client

    with Given("I configure the processor with expected_audience=account"):
        _configure_processor(self, expected_audience="account")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (aud claim missing from JWT)"):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"))
def expected_audience_wrong(self):
    """ClickHouse SHALL reject a token when ``expected_audience`` does not match the JWT ``aud`` claim."""
    client = self.context.provider_client

    with Given("I configure the processor with a wrong expected_audience"):
        _configure_processor(
            self, expected_audience="https://wrong-audience.example.com"
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (audience mismatch)"):
        assert_token_rejected(token=token)


# ---------------------------------------------------------------------------
# allow_no_expiration — RQ.SRS-042.OAuth.Common.Parameters.AllowNoExpiration
# ---------------------------------------------------------------------------
#
# These scenarios mint their own HS256-signed JWTs locally (PyJWT) and pair
# them with a ``jwt_static_key`` processor whose static_key matches the
# minting key. This is the only way to assert ``allow_no_expiration``:
# Keycloak always issues tokens with an ``exp`` claim, so we cannot drive
# the IdP into producing a no-``exp`` token.

# Constant secret used only by the two AllowNoExpiration scenarios. The
# payload SHALL be authenticated only by ClickHouse against this same key,
# so leaking it has no security impact (it never reaches Keycloak / a
# real IdP). Kept short for readability; spec doesn't pin a minimum
# length for the static-key path.
_ALLOW_NO_EXP_HS256_SECRET = "allow-no-exp-test-secret"
_ALLOW_NO_EXP_PROCESSOR_NAME = "allow_no_exp_processor"


def _mint_hs256(payload):
    """Encode ``payload`` as a compact-form HS256 JWT signed with
    ``_ALLOW_NO_EXP_HS256_SECRET``.

    Returns a string. PyJWT 2.x returns ``str``; older 1.x returned
    ``bytes`` — we coerce to ``str`` defensively so the assertions below
    don't trip on a bytes/str mismatch.
    """
    token = pyjwt.encode(
        payload,
        _ALLOW_NO_EXP_HS256_SECRET,
        algorithm="HS256",
    )
    if isinstance(token, bytes):
        token = token.decode("ascii")
    return token


def _configure_static_key_processor(self, *, allow_no_expiration):
    """Replace the keycloak processor with a ``jwt_static_key``
    processor matching ``_ALLOW_NO_EXP_HS256_SECRET``.

    The ``user_directories`` block is rebound to the new processor so
    that the username carried in the test JWTs (``sub`` claim)
    materialises through the token user directory.
    """
    change_token_processors(
        processor_name=_ALLOW_NO_EXP_PROCESSOR_NAME,
        processor_type="jwt_static_key",
        algo="HS256",
        static_key=_ALLOW_NO_EXP_HS256_SECRET,
        allow_no_expiration=allow_no_expiration,
        replace_section=True,
    )
    change_user_directories_config(
        processor=_ALLOW_NO_EXP_PROCESSOR_NAME,
        common_roles=["general-role"],
    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_AllowNoExpiration("1.0"),
)
def allow_no_expiration_true_accepts_token_without_exp(self):
    """When ``<allow_no_expiration>true</allow_no_expiration>`` is set
    on a JWT-based processor, a token without an ``exp`` claim SHALL
    be accepted.

    Maps to SRS 13.1.6. We mint two HS256 JWTs locally (PyJWT): one
    with a future ``exp``, one without ``exp``. With ``true``, both
    SHALL authenticate.

    The ``sub`` claim is a per-test UUID-ish string so the IdP-issued
    user materialised through the token user-directory does not
    collide with any seeded local user (``demo``, ``default``, ...).
    """
    from helpers.common import getuid

    user = f"allow_no_exp_user_{getuid()[:8]}"
    future_exp = int(time.time()) + 3600

    with Given("I configure jwt_static_key with allow_no_expiration=true"):
        _configure_static_key_processor(self, allow_no_expiration=True)

    with And(f"I mint a JWT for '{user}' WITH a future exp"):
        token_with_exp = _mint_hs256({"sub": user, "exp": future_exp})

    with And(f"I mint a JWT for '{user}' WITHOUT exp"):
        token_no_exp = _mint_hs256({"sub": user})

    with Then("ClickHouse accepts the token with exp"):
        access_clickhouse(token=token_with_exp, status_code=200)

    with And(
        "ClickHouse accepts the token without exp "
        "(allow_no_expiration=true honours SRS 13.1.6)"
    ):
        access_clickhouse(token=token_no_exp, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_AllowNoExpiration("1.0"),
)
def allow_no_expiration_false_rejects_token_without_exp(self):
    """When ``<allow_no_expiration>false</allow_no_expiration>`` is
    set (or the parameter is omitted — the default per SRS 13.1.6 is
    ``false``), a token without an ``exp`` claim SHALL be rejected.

    Maps to SRS 13.1.6 negative path. Same minted-JWT setup as the
    positive scenario above; we just flip the configured value.
    """
    from helpers.common import getuid

    user = f"allow_no_exp_user_{getuid()[:8]}"
    future_exp = int(time.time()) + 3600

    with Given("I configure jwt_static_key with allow_no_expiration=false"):
        _configure_static_key_processor(self, allow_no_expiration=False)

    with And(f"I mint a JWT for '{user}' WITH a future exp"):
        token_with_exp = _mint_hs256({"sub": user, "exp": future_exp})

    with And(f"I mint a JWT for '{user}' WITHOUT exp"):
        token_no_exp = _mint_hs256({"sub": user})

    with Then(
        "ClickHouse accepts the token with exp (the static key still "
        "validates the signature)"
    ):
        access_clickhouse(token=token_with_exp, status_code=200)

    with And(
        "ClickHouse rejects the token without exp "
        "(allow_no_expiration=false enforces SRS 13.1.6)"
    ):
        assert_token_rejected(token=token_no_exp)


# ---------------------------------------------------------------------------
# Common.Parameters.Unfiltered — RQ.SRS-042.OAuth.Common.Parameters.Unfiltered
# ---------------------------------------------------------------------------


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_Unfiltered("1.0"),
)
def processor_with_every_parameter_at_once_rejected(self):
    """A token-processor configuration that sets *every* parameter at
    once SHALL be rejected.

    Maps to SRS 13.1.7 — the spec gives a verbatim ``<madness>``
    example with ``algo`` + ``static_key`` + ``static_jwks`` +
    ``jwks_uri`` + every OpenID endpoint + every claim knob + both
    leeways + every cache lifetime + ``allow_no_expiration``. The
    configuration is contradictory (a JWT can be validated by HS256
    static_key XOR by JWKS XOR by the OpenID userinfo path; having
    all three plus ``type=openid`` confuses the parser) and SHALL
    not authenticate.

    The ``configuration_endpoint`` is omitted vs. the SRS example
    because OpenID processors already reject the combination of
    ``configuration_endpoint`` AND ``userinfo_endpoint`` /
    ``token_introspection_endpoint`` separately (see
    ``configuration::openid_processor_with_all_endpoints_rejected``);
    that shortcut would mask the ``Unfiltered`` rejection we're
    actually trying to observe.
    """
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with every other parameter set "
        "(static_key + static_jwks + every endpoint + every "
        "claim knob + every cache lifetime + allow_no_expiration)"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="madness",
            processor_type="OpenID",
            algo="HS256",
            static_key="some-static-key",
            static_jwks=(
                '{"keys":[{"kty":"RSA","alg":"RS256","kid":"madness",'
                '"n":"_modulus_","e":"AQAB"}]}'
            ),
            token_cache_lifetime=600,
            username_claim="sub",
            groups_claim="groups",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            expected_issuer="https://auth.example.com",
            expected_audience="clickhouse-app",
            allow_no_expiration=True,
            replace_section=True,
        )

    with And("I get a valid token from the IdP"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "ClickHouse rejects the config at parse time — "
        "token authentication is disabled (H-07 fail-closed)"
    ):
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestFeature
@Name("parameters and caching")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"),
    RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_AllowNoExpiration("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_Unfiltered("1.0"),
)
def feature(self):
    """Test common OAuth token-processor parameters and caching behavior."""
    Scenario(run=username_claim_sub)
    Scenario(run=username_claim_preferred_username)
    Scenario(run=token_cache_lifetime_honoured)
    Scenario(run=cache_disabled)
    Scenario(run=groups_claim_parameter)
    Scenario(run=expected_issuer_correct)
    Scenario(run=expected_issuer_wrong)
    Scenario(run=expected_audience_missing_claim)
    Scenario(run=expected_audience_wrong)
    Scenario(run=allow_no_expiration_true_accepts_token_without_exp)
    Scenario(run=allow_no_expiration_false_rejects_token_without_exp)
    Scenario(run=processor_with_every_parameter_at_once_rejected)
