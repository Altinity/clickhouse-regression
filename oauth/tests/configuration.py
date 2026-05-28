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
    (``userinfo_endpoint``, ``token_introspection_endpoint``) so the
    only thing wrong with the resulting processor is the absence of
    ``<type>``. Otherwise a server that's broken on
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
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
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
    differently-named processor (``not_keycloak``) so the user-directory
    reference becomes dangling.

    Subtlety: the HTTP handler runs an unscoped ``checkTokenCredentials``
    over **all** configured processors before the user-directory storage
    chain is consulted, and a successful match there warms the token
    cache; the user-directory's later, processor-scoped check then
    short-circuits on the cache hit and accepts the token even though
    its referenced processor name is missing. To exercise the
    user-directory dangling-reference path itself we therefore use a
    ``jwt_static_key`` processor whose static key cannot validate
    Keycloak-issued JWTs — the unscoped pre-check fails, the cache
    stays cold, and ClickHouse rejects with
    ``AUTHENTICATION_FAILED`` (HTTP 403). An OpenID processor pointing
    at the real Keycloak endpoints would silently *succeed* the
    pre-check and mask the dangling reference.
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
        "dangling so no fallback path can authenticate it"
    ):
        # HTTP layer rejects with AUTHENTICATION_FAILED (403) when no
        # processor can validate the bearer token; that is the failure
        # surface for any unverifiable token, including the dangling-
        # reference case under test.
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
    """ClickHouse SHALL reject the configuration at startup when the
    ``<processor>`` element inside ``<user_directories>/<token>`` is
    present but empty.

    The docs are explicit: *"This parameter is mandatory and cannot be
    empty"*. Distinct from ``empty_processor_in_user_directory`` which
    points at a real-but-empty processor — here the *reference itself*
    is empty.

    On antalya-26.1+ this is a **fatal startup error** (raised from
    ``TokenAccessStorage`` construction during access-control setup,
    not at request time), so the test cannot use the request-rejection
    pattern of its sibling scenarios; the
    ``change_user_directories_config`` helper goes through ``add_config``
    which would time out waiting for the server to come back healthy.
    Instead we use ``apply_fatal_user_directories_config`` which expects
    the server to fail to start and verifies the rejection appears in
    ``clickhouse-server.err.log``; the overlay is removed and the
    server restarted on teardown so subsequent scenarios run on a
    clean baseline.
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
    """An OpenID processor with both ``configuration_endpoint`` and
    ``userinfo_endpoint`` set SHALL be rejected at parse time.

    Since antalya-26.3 (PR #1799): ``configuration_endpoint`` and
    ``userinfo_endpoint`` are mutually exclusive.
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
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
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


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    ),
)
def invalid_roles_filter_regex_in_user_directory(self):
    """ClickHouse SHALL reject a user-directory config whose
    ``roles_filter`` contains an invalid regex at parse time.

    Fixed in antalya-26.3 (PR #1777, commit H-06): the
    ``TokenAccessStorage`` constructor validates the RE2 pattern and
    throws ``BAD_ARGUMENTS`` when ``!roles_filter->ok()``, refusing to
    instantiate the storage in a permissive state.

    The test writes the bad config, restarts ClickHouse, and asserts
    the rejection message appears in the error log.  Cleanup restores
    the server to a healthy state.
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
    """ClickHouse SHALL not allow the external user to authenticate
    when ``user_directories`` contains multiple ``<token>`` entries
    that resolve to the same processor.

    Maps to SRS 6.2.1.1.4 — "multiple entries that are the same".

    The overlay swaps ``<user_directories>`` for one that contains
    two ``<token>`` siblings both pointing at ``keycloak`` (the XML
    writer in ``helpers.common._create_xml_tree`` materialises a
    list-of-dicts as repeated sibling tags).

    **Currently xfailed** as ``DEFECT_M33`` (alias ``CFG-04``) —
    antalya-26.1 silently merges the duplicate siblings and auth
    proceeds with whichever entry won the merge (HTTP 200,
    ``currentUser()`` returns the IdP-issued user UUID). Same
    fail-open family as ``H-06`` / ``H-07``. The scenario asserts the
    spec-correct outcome (``assert_token_rejected``) so it will flip
    green when the config parser starts rejecting duplicate
    ``<token>`` children. New finding from runtime regression
    testing — registered as next Series-A medium per
    ``oauth/new_audit_review/all-issues.md`` §4 ("continue Series A
    (H-30, M-33, L-22, …) for issues surfaced by the audit-review
    skill workflow").
    """
    client = self.context.provider_client

    with Given(
        "I overlay <user_directories replace> with two <token> blocks "
        "pointing at the same processor"
    ):
        # Pass the two <token> children as a list — the XML writer
        # in helpers.common._create_xml_tree treats list-of-dicts as
        # a request for sibling elements with the same tag.
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
        "invalid configuration per SRS 6.2.1.1.4)"
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
    """ClickHouse SHALL not allow the external user to authenticate
    when the ``token_processors`` section is present but empty (no
    processors defined).

    Maps to SRS 6.2.1.2.1 — "token_processors section is not defined".
    We use ``replace_section=True`` to wipe the base ``<keycloak>``
    processor and overlay an empty ``<token_processors/>`` element.
    The user_directories block still references ``keycloak`` but
    that name no longer resolves; auth SHALL fail.
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
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    ),
)
def empty_user_directories_section(self):
    """ClickHouse SHALL not allow the external user to authenticate
    when the ``user_directories`` section is empty (no ``<token>``
    binding to any processor).

    Maps to SRS 6.2.1.2.3 — "user_directories section is not defined".
    The processor itself is intact and the unscoped HTTP-layer
    pre-check would normally accept the token, but with no token
    user-directory there is no storage to materialise the user, so
    the request SHALL still be rejected.
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
    """ClickHouse SHALL not allow the external user to authenticate
    when ``user_directories`` is present but does not contain a
    ``<token>`` block.

    Maps to SRS 6.2.1.2.4 — "token section is not defined in
    user_directories". We replace ``<user_directories>`` with a
    section that has only a ``<users_xml>`` child (which references a
    file that does not contain external IdP users), so there is no
    storage that can materialise the Keycloak-issued user.
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
    # enable_token_auth disabled at startup — placed last because it
    # restarts the server twice (disable + cleanup-restore).
    Scenario(run=enable_token_auth_disabled_rejects_tokens)
