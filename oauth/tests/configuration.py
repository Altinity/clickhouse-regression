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
    """ClickHouse SHALL reject auth when the token processor has an
    unsupported ``type``.

    The overlay uses ``replace=True`` so the base ``<keycloak>`` processor
    in ``config.xml`` is fully replaced, not merged into. Without
    ``replace`` the resulting processor would have two ``<type>`` children
    (``OpenID`` from the base + ``invalid_type`` from the overlay) and
    the test would exercise XML-merge behavior rather than the
    documented type-validation path.
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
    """ClickHouse SHALL reject auth when the token processor ``type``
    is missing.

    Per the docs: ``type`` is *Mandatory*. To isolate that single
    invariant, the overlay keeps the base processor's endpoints
    (``userinfo_endpoint``, ``token_introspection_endpoint``,
    ``jwks_uri``) so the only thing wrong with the resulting processor
    is the absence of ``<type>``. Otherwise a server that's broken on
    *any* missing-mandatory-field path would pass this test and the
    type-specific assertion would be hidden.
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
            jwks_uri=endpoints.jwks_uri,
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
    """ClickHouse SHALL reject auth when ``user_directories/token/processor``
    references a name that is not defined in ``token_processors``.

    The base config has ``<token><processor>keycloak</processor></token>``.
    We replace the entire ``<token_processors>`` section with a single
    differently-named processor (``not_keycloak``) so the reference
    becomes dangling. To make sure the rejection is for *that* reason
    (and not, e.g., the new processor failing parse for an unrelated
    cause) the response body is asserted to mention the missing name.
    """
    client = self.context.provider_client

    with Given(
        "I replace all token processors with one named differently than 'keycloak'"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="not_keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
            replace_section=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects (base user_directories still references 'keycloak')"):
        body = access_clickhouse(token=token, status_code=400)
        assert "keycloak" in body, error(
            f"Expected error body to mention the missing processor name "
            f"'keycloak'; got: {body[:500]}"
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
    """ClickHouse SHALL reject auth when the processor referenced by
    ``user_directories/token`` is defined but has no fields (no
    ``<type>``, no endpoints).

    Two overlays are applied: first the entire ``<token_processors>``
    section is replaced with a single empty ``<placeholder/>``; then
    the user directory is repointed at ``placeholder`` so the user
    directory references the configured-but-invalid processor. This is
    distinct from ``non_existent_processor_in_user_directory`` (which
    references a name that doesn't exist at all) because here the name
    *does* resolve, but to a processor that fails its own parse.
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
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def empty_processor_element_in_user_directory(self):
    """ClickHouse SHALL reject auth when the ``<processor>`` element
    inside ``<user_directories>/<token>`` is present but empty.

    The docs are explicit: *"This parameter is mandatory and cannot be
    empty"*. Distinct from ``empty_processor_in_user_directory`` which
    points at a real-but-empty processor — here the *reference itself*
    is empty.
    """
    client = self.context.provider_client

    with Given(
        "I overlay user_directories/token with an empty <processor></processor>"
    ):
        change_user_directories_config(processor="")

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects (empty processor reference)"):
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
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
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def openid_processor_with_all_endpoints_rejected(self):
    """An OpenID processor with all three endpoint kinds set
    (``configuration_endpoint`` + ``userinfo_endpoint`` +
    ``token_introspection_endpoint``) SHALL be rejected at parse time.

    Docs (verbatim): *"If none of them are set or all three are set,
    this is an invalid configuration that will not be parsed."*
    """
    client = self.context.provider_client

    with Given(
        "I replace the keycloak processor with type=OpenID and all three "
        "endpoint kinds present"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        if endpoints.configuration_endpoint is None:
            skip("provider does not expose a configuration_endpoint")
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            configuration_endpoint=endpoints.configuration_endpoint,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            replace=True,
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse rejects with BAD_ARGUMENTS (ambiguous endpoint config)"):
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_EnableTokenAuth("1.0"),
)
def enable_token_auth_disabled_rejects_tokens(self):
    """When ``<enable_token_auth>0</enable_token_auth>`` is set,
    ClickHouse SHALL reject all token-based authentication.

    Docs: *"When disabled, token processors are not parsed,
    TokenAccessStorage is not available, and authentication via tokens
    (``--jwt`` option or ``Authorization: Bearer`` header) is rejected."*

    The setting is applied at startup (``AccessControl::setupFromMainConfig``);
    ``change_clickhouse_config`` restarts the server by default so the
    new value takes effect. The cleanup branch restores the default and
    restarts to leave the suite in a working state for subsequent
    scenarios.

    Known related defect: M-02 — ``enable_token_auth`` is read once at
    startup and not re-read on ``SYSTEM RELOAD CONFIG``. This scenario
    exercises only the supported path (restart) and is not affected.
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
            # The exact failure surface for "token auth disabled" is not
            # pinned by the spec — depending on the build it can be a
            # plain ``AUTHENTICATION_FAILED`` (HTTP 403) or an explicit
            # ``Token authentication is disabled`` message (HTTP 500).
            # Both are valid rejections; we simply assert the request
            # did not succeed and that the body mentions an auth-style
            # error.
            for sc in (403, 500):
                try:
                    body = access_clickhouse(token=token, status_code=sc)
                    break
                except AssertionError:
                    continue
            else:
                fail("token auth was not rejected with HTTP 403 or 500")
            assert any(
                marker in body
                for marker in (
                    "AUTHENTICATION_FAILED",
                    "Token authentication is disabled",
                    "token authentication is disabled",
                    "Authentication failed",
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
    """ClickHouse SHALL accept the OpenID processor ``type`` written in
    any letter case (the docs explicitly call ``type`` out as
    *case-insensitive*).

    Using the canonical ``OpenID`` here would prove nothing about
    case-insensitivity, so we deliberately use a mixed-case spelling
    (``OpEnId``) and expect the processor to parse and authenticate
    normally.
    """
    client = self.context.provider_client

    with Given("I configure a token processor with type='OpEnId' (mixed case)"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpEnId",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
            replace=True,
        )

    with And("I configure user directories to use the processor"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token (case-insensitive type parse)"):
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
    RQ_SRS_042_OAuth_EnableTokenAuth("1.0"),
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
    # enable_token_auth disabled at startup — placed last because it
    # restarts the server twice (disable + cleanup-restore).
    Scenario(run=enable_token_auth_disabled_rejects_tokens)
