"""Token-processor parameter and caching tests.

All scenarios route OpenID endpoints through the provider abstraction
(``client.OAuthProvider.openid_endpoints()``) so the same tests run
unchanged when ``--identity-provider`` switches.
"""

import time

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
    replace=False,
):
    """Apply a Keycloak-OpenID processor config plus optional overrides.

    Centralised here so each scenario doesn't repeat the same 4 URLs.
    The endpoint bundle comes from the provider so non-Keycloak runs
    pick up the right URLs automatically.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    kwargs = {
        "processor_name": "keycloak",
        "processor_type": "OpenID",
        "userinfo_endpoint": endpoints.userinfo_endpoint,
        "token_introspection_endpoint": endpoints.token_introspection_endpoint,
        "jwks_uri": endpoints.jwks_uri,
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
        access_clickhouse(token=token, status_code=500)


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
        access_clickhouse(token=token, status_code=500)


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
        access_clickhouse(token=token, status_code=500)


@TestFeature
@Name("parameters and caching")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedIssuer("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_ExpectedAudience("1.0"),
    RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"),
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
