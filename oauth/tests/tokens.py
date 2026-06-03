"""Token validation tests that exercise the configured token processor.

JWT-mutation tests live in ``oauth.tests.jwt_manipulation``. This file
focuses on processor-configuration behaviour (OpenID discovery, invalid
JWKS endpoint, etc.) so we don't double-count the same coverage.
"""

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


@TestFeature
@Name("tokens")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def feature(self):
    """Token-processor configuration tests."""
    Scenario(run=openid_discovery_mode)
    Scenario(run=invalid_jwks_uri_rejected)
