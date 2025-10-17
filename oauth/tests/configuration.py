from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def access_clickhouse_with_specific_config(self, set_clickhouse_configuration):
    """Attempt to access ClickHouse with incorrect OAuth configuration."""

    with Given("I set an incorrect OAuth configuration"):
        set_clickhouse_configuration()

    with Then("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestSketch(Scenario)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    ),
)
def check_incorrect_configuration(self):
    """Check ClickHouse behavior with incorrect OAuth configuration."""
    client = self.context.provider_client

    configurations = either(
        *[
            client.OAuthProvider.invalid_processor_type_configuration,
            client.OAuthProvider.missing_processor_type_configuration,
            client.OAuthProvider.empty_processor_type_configuration,
            client.OAuthProvider.whitespace_processor_type_configuration,
            client.OAuthProvider.case_sensitive_processor_type_configuration,
            client.OAuthProvider.invalid_processor_name_configuration,
            client.OAuthProvider.whitespace_processor_name_configuration,
            client.OAuthProvider.special_chars_processor_name_configuration,
            client.OAuthProvider.missing_processor_user_directory_configuration,
            client.OAuthProvider.whitespace_processor_user_directory_configuration,
            client.OAuthProvider.non_existent_processor_user_directory_configuration,
            client.OAuthProvider.case_mismatch_processor_user_directory_configuration,
            client.OAuthProvider.invalid_common_roles_configuration,
            client.OAuthProvider.whitespace_common_roles_configuration,
            client.OAuthProvider.special_chars_common_roles_configuration,
            client.OAuthProvider.invalid_roles_filter_configuration,
            client.OAuthProvider.empty_roles_filter_configuration,
            client.OAuthProvider.whitespace_roles_filter_configuration,
            client.OAuthProvider.malformed_roles_filter_configuration,
            client.OAuthProvider.no_token_processors_configuration,
            client.OAuthProvider.duplicate_processor_names_configuration,
            client.OAuthProvider.invalid_processor_attributes_configuration,
            client.OAuthProvider.missing_user_directories_configuration,
            client.OAuthProvider.empty_user_directories_configuration,
            client.OAuthProvider.malformed_xml_structure_configuration,
            client.OAuthProvider.null_values_configuration,
            client.OAuthProvider.extremely_long_values_configuration,
            client.OAuthProvider.unicode_special_chars_configuration,
            client.OAuthProvider.sql_injection_attempt_configuration,
            client.OAuthProvider.path_traversal_attempt_configuration,
            client.OAuthProvider.completely_invalid_configuration,
            client.OAuthProvider.partially_invalid_configuration,
            client.OAuthProvider.mixed_valid_invalid_configuration,
        ]
    )

    access_clickhouse_with_specific_config(set_clickhouse_configuration=configurations)


@TestFeature
@Name("configuration")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def feature(self):
    """Feature to test OAuth authentication flow with different configurations."""
    Scenario(run=check_incorrect_configuration)
