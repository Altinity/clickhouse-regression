import time

import jwt as pyjwt

from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"))
def username_claim_sub(self):
    """ClickHouse SHALL use ``sub`` as the username when configured."""
    client = self.context.provider_client

    with Given("I configure the processor with username_claim=sub"):
        configure_openid_token_processor(username_claim="sub")

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
        configure_openid_token_processor(username_claim="preferred_username")

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
        configure_openid_token_processor(token_cache_lifetime=5)

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
        configure_openid_token_processor(token_cache_lifetime=0)

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
        configure_openid_token_processor(groups_claim="groups")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"))
def expected_issuer_correct(self):
    """ClickHouse SHALL accept a token when ``expected_issuer`` matches ``iss``."""
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    with Given("I configure the processor with the matching expected_issuer"):
        configure_openid_token_processor(expected_issuer=endpoints.issuer)

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
        configure_openid_token_processor(
            expected_issuer="https://wrong-issuer.example.com"
        )

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
        configure_openid_token_processor(expected_audience="account")

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
        configure_openid_token_processor(
            expected_audience="https://wrong-audience.example.com"
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (audience mismatch)"):
        assert_token_rejected(token=token)

_ALLOW_NO_EXP_HS256_SECRET = "allow-no-exp-test-secret"
_ALLOW_NO_EXP_PROCESSOR_NAME = "allow_no_exp_processor"


def _mint_hs256(payload):
    """Encode ``payload`` as a compact HS256 JWT signed with the test secret."""
    token = pyjwt.encode(
        payload,
        _ALLOW_NO_EXP_HS256_SECRET,
        algorithm="HS256",
    )
    if isinstance(token, bytes):
        token = token.decode("ascii")
    return token


def _configure_static_key_processor(self, *, allow_no_expiration):
    """Replace the keycloak processor with a ``jwt_static_key`` processor
    matching the test secret.
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
    """When ``allow_no_expiration`` is ``true``, a token without an ``exp``
    claim SHALL be accepted.

    Mints two HS256 JWTs locally: one with ``exp``, one without. Both
    SHALL authenticate.
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

    with And("ClickHouse accepts the token without exp " "(allow_no_expiration=true)"):
        access_clickhouse(token=token_no_exp, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_AllowNoExpiration("1.0"),
)
def allow_no_expiration_false_rejects_token_without_exp(self):
    """When ``allow_no_expiration`` is ``false`` (the default), a token
    without an ``exp`` claim SHALL be rejected.
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

    with And("ClickHouse rejects the token without exp " "(allow_no_expiration=false)"):
        assert_token_rejected(token=token_no_exp)

@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_Unfiltered("1.0"),
)
def processor_with_every_parameter_at_once_rejected(self):
    """A token-processor configuration that sets every parameter at once
    SHALL be rejected.

    The configuration is contradictory (a JWT cannot be validated by
    static_key, JWKS, and OpenID userinfo simultaneously) and SHALL
    not authenticate.
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

    with Then("ClickHouse rejects the contradictory config at parse time"):
        assert_misconfigured_processor_rejects(token=token)


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
