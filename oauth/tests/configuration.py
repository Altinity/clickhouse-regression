from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def invalid_processor_type(self):
    """ClickHouse SHALL reject auth when token processor has an invalid type."""
    client = self.context.provider_client

    with Given("I configure a token processor with an invalid type"):
        change_token_processors(
            processor_name="keycloak_bad",
            processor_type="invalid_type",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=token, status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    ),
)
def missing_processor_type(self):
    """ClickHouse SHALL reject auth when token processor type is missing."""
    client = self.context.provider_client

    with Given("I configure a token processor without a type"):
        change_token_processors(
            processor_name="keycloak_no_type",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=token, status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    ),
)
def non_existent_processor_in_user_directory(self):
    """ClickHouse SHALL reject auth when user_directories references a processor that does not exist."""
    client = self.context.provider_client

    with Given("I configure user directories pointing to a non-existent processor"):
        change_user_directories_config(
            processor="does_not_exist",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=token, status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def empty_processor_in_user_directory(self):
    """ClickHouse SHALL reject auth when user_directories processor is empty."""
    client = self.context.provider_client

    with Given("I configure user directories with an empty processor"):
        change_user_directories_config(
            processor="",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=token, status_code=500)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_Operational_ProviderType("1.0"),
)
def valid_openid_processor_type(self):
    """ClickHouse SHALL accept auth when token processor type is OpenID (case-insensitive)."""
    client = self.context.provider_client

    with Given("I configure a token processor with type OpenID"):
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

    with And("I configure user directories to use the processor"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("configuration")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    ),
)
def feature(self):
    """Test OAuth token processor and user directory configuration validation."""
    Scenario(run=invalid_processor_type)
    Scenario(run=missing_processor_type)
    Scenario(run=non_existent_processor_in_user_directory)
    Scenario(run=empty_processor_in_user_directory)
    Scenario(run=valid_openid_processor_type)
