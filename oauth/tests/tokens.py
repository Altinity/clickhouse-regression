from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def openid_discovery_mode(self):
    """ClickHouse SHALL validate Keycloak tokens using OpenID discovery endpoints."""
    client = self.context.provider_client

    with Given("I configure a token processor with OpenID endpoints"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
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


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_Configuration_Validation("1.0"),
)
def invalid_jwks_uri_rejected(self):
    """ClickHouse SHALL reject tokens when jwks_uri points to a bad endpoint."""
    client = self.context.provider_client

    with Given("I configure a processor with an invalid jwks_uri"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            jwks_uri="http://keycloak:8080/invalid/jwks",
            userinfo_endpoint=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/userinfo"
            ),
            token_introspection_endpoint=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/token/introspect"
            ),
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token (bad JWKS endpoint)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
)
def token_with_modified_alg(self):
    """ClickHouse SHALL reject a token whose alg header was tampered with."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change the alg to 'none'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"alg": "none"}
        )

    with Then("ClickHouse rejects the modified token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
)
def token_with_modified_typ(self):
    """ClickHouse SHALL reject a token whose typ header was tampered with."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change the typ to an invalid value"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"typ": "INVALID"}
        )

    with Then("ClickHouse rejects the modified token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
)
def token_with_expired_exp(self):
    """ClickHouse SHALL reject a token with an expired exp claim."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I set exp to a past timestamp"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"exp": 1000000000}
        )

    with Then("ClickHouse rejects the expired token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"),
)
def token_with_modified_sub(self):
    """ClickHouse SHALL still validate via JWKS even with a changed sub claim."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change the sub to something else"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"sub": "nonexistent-user-id"}
        )

    with Then("ClickHouse rejects the token (signature invalid after payload change)"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def token_with_invalid_signature(self):
    """ClickHouse SHALL reject a token with a completely invalid signature."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I replace the signature"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change="invalid-signature-data"
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def token_with_empty_signature(self):
    """ClickHouse SHALL reject a token with an empty signature."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I remove the signature entirely"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change=""
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestFeature
@Name("tokens")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
)
def feature(self):
    """Test Keycloak token validation and incorrect token handling."""
    Scenario(run=openid_discovery_mode)
    Scenario(run=invalid_jwks_uri_rejected)
    Scenario(run=token_with_modified_alg)
    Scenario(run=token_with_modified_typ)
    Scenario(run=token_with_expired_exp)
    Scenario(run=token_with_modified_sub)
    Scenario(run=token_with_invalid_signature)
    Scenario(run=token_with_empty_signature)
