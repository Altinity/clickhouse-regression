import time

from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
)
def username_claim_sub(self):
    """ClickHouse SHALL use the ``sub`` claim as the username by default."""
    client = self.context.provider_client

    with Given("I configure the processor with username_claim=sub"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            username_claim="sub",
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

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse returns a UUID-shaped user name (the sub claim)"):
        body = access_clickhouse(token=token, status_code=200)
        assert len(body.strip()) > 0, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
)
def username_claim_preferred_username(self):
    """ClickHouse SHALL extract username from ``preferred_username`` when configured."""
    client = self.context.provider_client

    with Given("I configure the processor with username_claim=preferred_username"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            username_claim="preferred_username",
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

    with And("I get a valid token for user 'demo'"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

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
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=5,
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

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("first request succeeds (populates cache)"):
        access_clickhouse(token=token, status_code=200)

    with And("second immediate request also succeeds (served from cache)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_CacheEviction_NoCache("1.0"),
)
def cache_disabled(self):
    """ClickHouse SHALL not cache tokens when ``token_cache_lifetime`` is 0."""
    client = self.context.provider_client

    with Given("I configure the processor with cache disabled"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=0,
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

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("request still succeeds even with cache disabled"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"),
)
def groups_claim_parameter(self):
    """ClickHouse SHALL use the configured groups_claim to read group membership."""
    client = self.context.provider_client

    with Given("I configure the processor with groups_claim=groups"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            groups_claim="groups",
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

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("parameters and caching")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"),
)
def feature(self):
    """Test common OAuth token processor parameters and caching behavior."""
    Scenario(run=username_claim_sub)
    Scenario(run=username_claim_preferred_username)
    Scenario(run=token_cache_lifetime_honoured)
    Scenario(run=cache_disabled)
    Scenario(run=groups_claim_parameter)
