from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def invalid_processor_type(self):
    """ClickHouse SHALL reject auth when the token processor has an
    unsupported ``type``.
    """
    client = self.context.provider_client

    with Given("I replace the keycloak processor with one that has an invalid type"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="invalid_type",
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    ),
)
def missing_processor_type(self):
    """ClickHouse SHALL reject auth when the token processor ``type``
    is missing.
    """
    client = self.context.provider_client

    with Given(
        "I replace the keycloak processor with a complete OpenID config "
        "that is missing only the <type> element"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    ),
)
def non_existent_processor_in_user_directory(self):
    """ClickHouse SHALL reject auth when ``user_directories/token/processor``
    references a name not defined in ``token_processors``.

    Uses a ``jwt_static_key`` processor that cannot validate Keycloak JWTs
    to ensure the dangling reference is actually exercised.
    """
    client = self.context.provider_client

    with Given(
        "I replace all token processors with one named differently than "
        "'keycloak' and unable to validate the Keycloak-issued token"
    ):
        change_token_processors(
            processor_name="not_keycloak",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key="this-key-cannot-validate-keycloak-rs256-signed-tokens",
            replace_section=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "ClickHouse rejects: the only configured processor cannot validate "
        "the token, and the user_directories reference 'keycloak' is "
        "dangling so no fallback path can authenticate it",
        description="""
            HTTP layer rejects with AUTHENTICATION_FAILED (403) when no
            processor can validate the bearer token; that is the failure
            surface for any unverifiable token, including the dangling-
            reference case under test.
        """,
    ):
        body = access_clickhouse(token=token, status_code=403)
        assert (
            "AUTHENTICATION_FAILED" in body or "Token could not be verified" in body
        ), error(
            f"Expected an auth-rejection marker in the response body; "
            f"got: {body[:500]}"
        )

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def empty_processor_in_user_directory(self):
    """ClickHouse SHALL reject auth when the referenced processor is
    defined but has no fields (no ``type``, no endpoints).
    """
    client = self.context.provider_client

    with Given("I replace all token processors with an empty/typeless one"):
        change_token_processors(
            processor_name="placeholder",
            replace_section=True,
        )

    with And("I repoint user_directories/token at the empty processor"):
        change_user_directories_config(
            processor="placeholder",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects (the referenced processor failed parse)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def empty_processor_element_in_user_directory(self):
    """ClickHouse SHALL reject the configuration at startup when the
    ``<processor>`` element inside ``<user_directories>/<token>`` is
    present but empty.

    This is a fatal startup error, so the test uses
    ``apply_fatal_user_directories_config`` to verify the rejection
    message in the error log.
    """
    with Given(
        "I overlay user_directories/token with an empty <processor></processor> "
        "and expect ClickHouse to refuse to start"
    ):
        apply_fatal_user_directories_config(
            entries={"user_directories": {"token": {"processor": ""}}},
            expected_message="'processor' must be specified for Token user directory",
            config_file="user_directory_empty_processor.xml",
        )

    with Then("ClickHouse comes back up after the bad config is removed"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def openid_processor_with_no_endpoints_rejected(self):
    """An OpenID processor with neither ``configuration_endpoint`` nor
    ``userinfo_endpoint``+``token_introspection_endpoint`` SHALL be
    rejected at parse time.

    Docs: *"Either ``configuration_endpoint`` or both ``userinfo_endpoint``
    and ``token_introspection_endpoint`` (and, optionally, ``jwks_uri``)
    shall be set. If none of them are set or all three are set, this is
    an invalid configuration that will not be parsed."*
    """
    client = self.context.provider_client

    with Given("I replace the keycloak processor with type=OpenID and zero endpoints"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def openid_processor_with_all_endpoints_rejected(self):
    """An OpenID processor with both ``configuration_endpoint`` and
    ``userinfo_endpoint`` set SHALL be rejected at parse time
    (mutually exclusive).
    """
    client = self.context.provider_client

    with Given(
        "I replace the keycloak processor with type=OpenID and both "
        "configuration_endpoint and userinfo_endpoint present"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        if endpoints.configuration_endpoint is None:
            skip("provider does not expose a configuration_endpoint")
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            configuration_endpoint=endpoints.configuration_endpoint,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (ambiguous endpoint config)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_EnableTokenAuth("1.0"),
)
def enable_token_auth_disabled_rejects_tokens(self):
    """When ``<enable_token_auth>0</enable_token_auth>`` is set,
    ClickHouse SHALL reject all token-based authentication.
    """
    client = self.context.provider_client

    try:
        with Given("I disable token authentication globally and restart"):
            change_clickhouse_config(
                entries={"enable_token_auth": "0"},
                config_d_dir="/etc/clickhouse-server/config.d",
                preprocessed_name="config.xml",
                config_file="enable_token_auth.xml",
                restart=True,
            )

        with And("I get a valid token"):
            token = client.OAuthProvider.get_oauth_token().access_token

        with Then("ClickHouse refuses to accept the bearer token"):
            for sc in (400, 403, 500):
                try:
                    body = access_clickhouse(token=token, status_code=sc)
                    break
                except AssertionError:
                    continue
            else:
                fail("token auth was not rejected with HTTP 400, 403, or 500")
            assert any(
                marker in body
                for marker in (
                    "AUTHENTICATION_FAILED",
                    "Token authentication is disabled",
                    "token authentication is disabled",
                    "Authentication failed",
                    "BAD_ARGUMENTS",
                )
            ), error(
                f"Expected an auth-rejection marker in the response body; "
                f"got: {body[:500]}"
            )

        with And("the server is still alive"):
            check_clickhouse_is_alive()
    finally:
        with Finally("I re-enable token auth and restart"):
            change_clickhouse_config(
                entries={"enable_token_auth": "1"},
                config_d_dir="/etc/clickhouse-server/config.d",
                preprocessed_name="config.xml",
                config_file="enable_token_auth.xml",
                restart=True,
            )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Tokens_Operational_ProviderType("1.0"),
)
def valid_openid_processor_type(self):
    """ClickHouse SHALL accept the OpenID processor ``type`` in any
    letter case (case-insensitive).
    """
    client = self.context.provider_client

    with Given("I configure a token processor with type='OpEnId' (mixed case)"):
        configure_openid_token_processor(processor_type="OpEnId")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token (case-insensitive type parse)"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    ),
)
def invalid_roles_filter_regex_in_user_directory(self):
    """ClickHouse SHALL reject a user-directory config whose
    ``roles_filter`` contains an invalid regex at parse time.
    """
    with Given("I apply a user_directories config with an invalid roles_filter regex"):
        apply_fatal_user_directories_config(
            entries={
                "user_directories": {
                    "token": {
                        "processor": "keycloak",
                        "common_roles": {"general-role": {}},
                        "roles_filter": "[invalid regex",
                    }
                }
            },
            expected_message="Invalid 'roles_filter' regex",
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries(
        "1.0"
    ),
)
def multiple_token_entries_in_user_directories(self):
    """ClickHouse SHALL not allow auth when ``user_directories``
    contains multiple ``<token>`` entries resolving to the same processor.
    """
    client = self.context.provider_client

    with Given(
        "I overlay <user_directories replace> with two <token> blocks "
        "pointing at the same processor",
        description="""
            Pass the two <token> children as a list — the XML writer
            in helpers.common._create_xml_tree treats list-of-dicts as
            a request for sibling elements with the same tag.
        """,
    ):
        entries = {
            KeyWithAttributes("user_directories", {"replace": "replace"}): {
                "token": [
                    {
                        "processor": "keycloak",
                        "common_roles": {"general-role": {}},
                    },
                    {
                        "processor": "keycloak",
                        "common_roles": {"general-role": {}},
                    },
                ],
            }
        }
        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
            restart=True,
            config_file="user_directory_duplicate_token.xml",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "ClickHouse refuses the auth (duplicate <token> binding is an "
        "invalid configuration)"
    ):
        assert_token_rejected(token=token)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors(
        "1.0"
    ),
)
def empty_token_processors_section(self):
    """ClickHouse SHALL not allow auth when ``token_processors`` is
    present but empty (no processors defined).
    """
    client = self.context.provider_client

    with Given("I overlay an empty <token_processors replace> section"):
        entries = {KeyWithAttributes("token_processors", {"replace": "replace"}): {}}
        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
            restart=True,
            config_file="empty_token_processors.xml",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (token auth not configured)"):
        assert_misconfigured_processor_rejects(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    ),
)
def empty_user_directories_section(self):
    """ClickHouse SHALL not allow auth when ``user_directories`` is empty
    (no ``<token>`` binding).
    """
    client = self.context.provider_client

    with Given("I overlay an empty <user_directories replace> section"):
        entries = {KeyWithAttributes("user_directories", {"replace": "replace"}): {}}
        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
            restart=True,
            config_file="empty_user_directories.xml",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "ClickHouse refuses the auth (no <token> user directory is "
        "configured to back the IdP-issued user)"
    ):
        assert_token_rejected(token=token)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token(
        "1.0"
    ),
)
def user_directories_without_token_block(self):
    """ClickHouse SHALL not allow auth when ``user_directories`` has no
    ``<token>`` block.
    """
    client = self.context.provider_client

    with Given(
        "I overlay <user_directories replace> with a non-token entry only "
        "(users_xml pointing at the seeded local users file)"
    ):
        entries = {
            KeyWithAttributes("user_directories", {"replace": "replace"}): {
                "users_xml": {"path": "users.xml"},
            }
        }
        change_clickhouse_config(
            entries=entries,
            config_d_dir="/etc/clickhouse-server/config.d",
            preprocessed_name="config.xml",
            restart=True,
            config_file="user_directories_no_token.xml",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "ClickHouse refuses the auth (the IdP-issued user has no "
        "token user-directory to land in)"
    ):
        assert_token_rejected(token=token)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestFeature
@Name("configuration")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_EnableTokenAuth("1.0"),
    RQ_SRS_042_OAuth_Authentication_UserDirectories("1.0"),
    RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors("1.0"),
)
def feature(self):
    """Test OAuth token processor and user directory configuration validation."""
    Scenario(run=invalid_processor_type)
    Scenario(run=missing_processor_type)
    Scenario(run=non_existent_processor_in_user_directory)
    Scenario(run=empty_processor_in_user_directory)
    Scenario(run=empty_processor_element_in_user_directory)
    Scenario(run=openid_processor_with_no_endpoints_rejected)
    Scenario(run=openid_processor_with_all_endpoints_rejected)
    Scenario(run=valid_openid_processor_type)
    Scenario(run=invalid_roles_filter_regex_in_user_directory)
    Scenario(run=multiple_token_entries_in_user_directories)
    Scenario(run=empty_token_processors_section)
    Scenario(run=empty_user_directories_section)
    Scenario(run=user_directories_without_token_block)
    Scenario(run=enable_token_auth_disabled_rejects_tokens)
