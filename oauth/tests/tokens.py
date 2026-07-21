from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def openid_discovery_mode(self):
    """ClickHouse SHALL validate tokens using OpenID userinfo endpoint."""
    client = self.context.provider_client

    with Given("I configure a token processor with provider OpenID endpoints"):
        configure_openid_token_processor()

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_Configuration_Validation("1.0"),
)
def invalid_jwks_uri_rejected(self):
    """ClickHouse SHALL reject tokens when ``jwks_uri`` points to a non-existent endpoint.

    Since antalya-26.3 the ``openid`` processor no longer accepts
    ``jwks_uri``. This scenario uses ``jwt_dynamic_jwks`` instead to
    verify that an unreachable JWKS endpoint causes token rejection.
    """
    client = self.context.provider_client

    with Given("I configure a jwt_dynamic_jwks processor with an invalid jwks_uri"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="jwt_dynamic_jwks",
            jwks_uri="http://keycloak:8080/invalid/jwks",
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (AUTHENTICATION_FAILED)"):
        access_clickhouse(token=token, status_code=403)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def userinfo_only_accepts_valid_token(self):
    """An OpenID processor configured with only ``userinfo_endpoint``
    (no introspection) SHALL validate and accept a valid token."""
    client = self.context.provider_client

    with Given("I configure an OpenID processor with userinfo only"):
        configure_openid_token_processor(include_introspection=False)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token via userinfo validation"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def unreachable_introspection_rejects_token(self):
    """When introspection is configured but the endpoint is unreachable,
    authentication SHALL fail closed (introspection is not silently
    skipped) even though ``userinfo_endpoint`` is valid."""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a valid userinfo and an unreachable "
        "introspection endpoint"
    ):
        configure_openid_token_processor(
            token_introspection_endpoint=(
                "http://keycloak:8080/does-not-exist/introspect"
            ),
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects the token (introspection unreachable)"):
        assert_token_rejected(token=token)


@TestScenario
def auth_does_not_hang_on_unreachable_introspection(self):
    """ClickHouse SHALL NOT block indefinitely when the introspection
    endpoint is non-routable; the request returns and the server stays
    responsive."""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a non-routable introspection endpoint "
        "and a valid userinfo endpoint"
    ):
        configure_openid_token_processor(
            token_introspection_endpoint="http://10.255.255.1:9999/hang",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("the auth request completes instead of hanging"):
        assert_auth_request_completes(token=token)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
def auth_does_not_hang_on_unreachable_userinfo(self):
    """ClickHouse SHALL NOT block indefinitely when the userinfo endpoint
    is non-routable; the request returns and the server stays
    responsive."""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a non-routable userinfo endpoint and a "
        "valid introspection endpoint"
    ):
        configure_openid_token_processor(
            userinfo_endpoint="http://10.255.255.1:9999/hang",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("the auth request completes instead of hanging"):
        assert_auth_request_completes(token=token)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestFeature
@Name("tokens")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def feature(self):
    """Token validation tests that exercise the configured token processor."""
    Scenario(run=openid_discovery_mode)
    Scenario(run=invalid_jwks_uri_rejected)
    Scenario(run=userinfo_only_accepts_valid_token)
    Scenario(run=unreachable_introspection_rejects_token)
    Scenario(run=auth_does_not_hang_on_unreachable_introspection)
    Scenario(run=auth_does_not_hang_on_unreachable_userinfo)
