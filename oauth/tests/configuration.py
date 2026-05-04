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
            processor_name="keycloak",
            processor_type="invalid_type",
        )

    with And("I configure user directories to use the broken processor"):
        change_user_directories_config(
            processor="keycloak",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        access_clickhouse(token=token, status_code=400)

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

    with Given("I replace the keycloak processor with one that has no type"):
        change_token_processors(
            processor_name="keycloak",
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        access_clickhouse(token=token, status_code=400)

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

    with Given(
        "I replace all token processors with one named differently than 'keycloak'"
    ):
        change_token_processors(
            processor_name="not_keycloak",
            processor_type="OpenID",
            replace_section=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects (base user_directories still references 'keycloak')"):
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def empty_processor_in_user_directory(self):
    """ClickHouse SHALL reject auth when no token processors are available."""
    client = self.context.provider_client

    with Given("I replace all token processors with an empty/typeless one"):
        change_token_processors(
            processor_name="placeholder",
            replace_section=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects (no valid processor for 'keycloak' reference)"):
        access_clickhouse(token=token, status_code=400)

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
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
        )

    with And("I configure user directories to use the processor"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

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
