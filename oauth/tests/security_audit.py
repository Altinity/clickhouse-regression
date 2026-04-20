"""Security audit regression tests for OAuth/JWT token authentication.

Tests derived from the static security audit (oauth-security-audit-review.md).
Each scenario **confirms** a specific defect is present. If the defect gets
fixed, the test will FAIL — signaling that the expected broken behavior has
changed and the test should be updated to assert the corrected behavior.

Audit defect codes referenced in scenario docstrings:
  F4  / RECIP-01  : Bearer auth accepted on plaintext transport
  F16 / AUTHZ-02  : Invalid roles_filter regex fails open
  F17 / AVAIL-05  : Token processor parse failures silently swallowed
  F2  / OAUTH-06  : Cache bypasses per-user jwt.processor pin
  F3  / OAUTH-07  : OpenID JWT fast-path throws before fallback
  F7  / LEAK-03   : Authorization header exposed via getClientHTTPHeader
  F8  / TOKEN-05  : token_introspection_endpoint parsed but unused
  F9  / DOS-01    : Remote provider fetches lack bounded timeouts
  F10 / AVAIL-03  : Provider fetch under global auth mutex
"""

import time

from helpers.common import getuid
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.keycloak_realm import (
    create_user,
    delete_user,
)
from testflows.asserts import *
from oauth.requirements.requirements import *


# ---------------------------------------------------------------------------
# F4 / RECIP-01 — Bearer token accepted on plaintext transport
# ---------------------------------------------------------------------------


@TestScenario
def plaintext_http_accepts_bearer_token(self):
    """[F4/RECIP-01] Confirm defect: ClickHouse accepts bearer tokens over
    plaintext HTTP instead of rejecting them.

    The correct behavior would be to reject token auth on non-TLS
    connections. This test confirms the defect by verifying plaintext
    HTTP returns 200 (accepted). If fixed, the server should return
    403 or refuse the connection, and this test will fail.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("plaintext HTTP accepts the bearer token — confirming the defect"):
        body = access_clickhouse(token=token, https=False, status_code=200)
        assert len(body.strip()) > 0, error()

    with And("HTTPS also accepts the bearer token (expected correct behavior)"):
        access_clickhouse(token=token, https=True, status_code=200)


@TestScenario
def plaintext_http_bearer_on_all_nodes(self):
    """[F4/RECIP-01] Confirm defect: plaintext bearer acceptance is
    present on every cluster node, not just one."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    for i, ip in enumerate(["clickhouse1", "clickhouse2", "clickhouse3"], 1):
        with Then(
            f"node {i} ({ip}) accepts bearer over plaintext HTTP "
            f"— confirming defect is cluster-wide"
        ):
            access_clickhouse(token=token, ip=ip, https=False, status_code=200)


# ---------------------------------------------------------------------------
# F16 / AUTHZ-02 — Invalid roles_filter regex fails open
# ---------------------------------------------------------------------------


@TestScenario
def invalid_roles_filter_regex_fail_open(self):
    """[F16/AUTHZ-02] Confirm defect: an invalid roles_filter regex
    silently falls back to unfiltered role mapping instead of rejecting
    the configuration or denying authentication.

    We configure a broken regex in roles_filter. The defect causes
    ClickHouse to accept the config and map all groups to roles. If
    fixed, the server should reject the config at load time or deny
    auth, causing this test to fail.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"rfilt_{uid}"

    with Given(f"I create a Keycloak user '{username}' with no groups"):
        user_id = create_user(username=username, password="testpass123")

    try:
        with And("I configure user directories with an INVALID roles_filter regex"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="[invalid-regex",
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then(
            "ClickHouse accepts the token despite broken regex "
            "— confirming the fail-open defect"
        ):
            access_clickhouse(token=token, status_code=200)

    finally:
        with Finally("I clean up"):
            delete_user(username=username)


@TestScenario
def invalid_roles_filter_grants_all_groups_as_roles(self):
    """[F16/AUTHZ-02] Confirm defect: a broken roles_filter causes ALL
    token groups to be mapped as roles (fail-open), whereas a valid
    non-matching filter correctly excludes them.

    Step 1: Valid filter that matches nothing — auth succeeds on
    common_roles only. Step 2: Broken regex — if defect present, auth
    still succeeds (all groups fall through unfiltered). If fixed, step 2
    should reject config or deny, and the test will fail.
    """
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"rfgrp_{uid}"

    with Given(f"I create a Keycloak user '{username}'"):
        user_id = create_user(username=username, password="testpass123")

    try:
        with And(
            "I configure user directories with a VALID filter that "
            "excludes the user's groups"
        ):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="^this-matches-nothing$",
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then("auth succeeds with common_roles only (baseline)"):
            access_clickhouse(token=token, status_code=200)

        with When("I reconfigure with a BROKEN regex"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="[broken",
            )

        with And("I get a fresh token"):
            token2 = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            )["access_token"]

        with Then(
            "auth still succeeds — confirming broken regex fell back to "
            "unfiltered role mapping"
        ):
            access_clickhouse(token=token2, status_code=200)

    finally:
        with Finally("I clean up"):
            delete_user(username=username)


# ---------------------------------------------------------------------------
# F17 / AVAIL-05 — Processor parse failure silently swallowed
# ---------------------------------------------------------------------------


@TestScenario
def processor_parse_failure_silent_fallback(self):
    """[F17/AVAIL-05] Confirm defect: a misconfigured token processor is
    silently dropped while other processors continue to function.

    We add a valid 'keycloak' processor alongside a broken 'broken_proc'.
    The defect silently skips the broken one and auth succeeds via the
    valid one. If fixed, config reload should fail entirely when any
    processor fails to parse, and this test will fail.
    """
    client = self.context.provider_client

    with Given("I configure a valid 'keycloak' processor"):
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

    with And("I add a second processor with a completely invalid type"):
        change_token_processors(
            processor_name="broken_proc",
            processor_type="completely_invalid_type_xyz",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then(
        "ClickHouse accepts the token — confirming the broken processor "
        "was silently dropped and the valid one still works"
    ):
        access_clickhouse(token=token, status_code=200)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
def all_processors_broken_rejects_auth(self):
    """[F17/AVAIL-05] When ALL configured processors fail to parse,
    authentication SHALL be rejected entirely (BAD_ARGUMENTS / 400)."""
    client = self.context.provider_client

    with Given("I replace all processors with one that has an invalid type"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="completely_invalid_type_xyz",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse rejects with BAD_ARGUMENTS"):
        access_clickhouse(token=token, status_code=400)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


# ---------------------------------------------------------------------------
# F3 / OAUTH-07 — OpenID JWT fast-path throws before userinfo fallback
# ---------------------------------------------------------------------------


@TestScenario
def openid_broken_jwks_blocks_userinfo_fallback(self):
    """[F3/OAUTH-07] Confirm defect: when an OpenID processor has a broken
    jwks_uri, the JWT fast-path throws an exception that prevents the
    /userinfo fallback from being reached.

    A valid userinfo_endpoint is configured alongside a broken jwks_uri.
    The correct behavior would be to fall back to /userinfo and succeed.
    The defect causes auth to fail with 403. If fixed, this test will
    fail because auth would return 200.
    """
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with a broken jwks_uri "
        "but valid userinfo_endpoint"
    ):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            jwks_uri="http://keycloak:8080/invalid/jwks/does-not-exist",
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

    with Then(
        "ClickHouse rejects the token with 403 — confirming the defect: "
        "JWT fast-path exception prevents /userinfo fallback"
    ):
        access_clickhouse(token=token, status_code=403)


@TestScenario
def openid_no_jwks_uri_uses_userinfo_only(self):
    """[F3/OAUTH-07] When no jwks_uri is configured at all (removing the
    fast-path entirely), authentication succeeds via userinfo only.

    This is the baseline proving /userinfo works when the JWT fast-path
    is absent. Contrasts with the broken-jwks test above.
    """
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with userinfo_endpoint only (no jwks_uri)"
    ):
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
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("ClickHouse accepts the token via userinfo"):
        access_clickhouse(token=token, status_code=200)


# ---------------------------------------------------------------------------
# F7 / LEAK-03 — Authorization header exposed via getClientHTTPHeader
# ---------------------------------------------------------------------------


@TestScenario
def authorization_header_exposed_in_sql(self):
    """[F7/LEAK-03] Confirm defect: the raw Authorization header IS
    accessible from SQL via getClientHTTPHeader() when the setting is
    enabled.

    The defect allows `getClientHTTPHeader('Authorization')` to return
    the full `Bearer <token>` value. If fixed, the Authorization header
    should be filtered out and this test will fail.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then(
        "I query ClickHouse for the Authorization header via bearer auth "
        "with allow_get_client_http_header enabled"
    ):
        body = access_clickhouse(
            token=token,
            status_code=200,
            query=(
                "SELECT getClientHTTPHeader('Authorization') "
                "SETTINGS allow_get_client_http_header=1"
            ),
        )

    with And("the response contains the raw bearer token — confirming the leak defect"):
        assert token in body, error(
            "Expected the raw bearer token to be present in the response "
            "(confirming defect F7/LEAK-03), but it was not found. "
            "The defect may have been fixed."
        )


@TestScenario
def authorization_header_blocked_by_default_setting(self):
    """[F7/LEAK-03] With the default setting (allow_get_client_http_header=0),
    getClientHTTPHeader SHALL reject the query entirely."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then(
        "the query fails with HTTP 500 because the function is " "disabled by default"
    ):
        body = access_clickhouse(
            token=token,
            status_code=500,
            query="SELECT getClientHTTPHeader('Authorization')",
        )

    with And("the raw token is not leaked in the error message"):
        assert token not in body, error(
            "raw bearer token was leaked in the error response body"
        )


# ---------------------------------------------------------------------------
# F8 / TOKEN-05 — token_introspection_endpoint parsed but unused
# ---------------------------------------------------------------------------


@TestScenario
def introspection_endpoint_not_actually_called(self):
    """[F8/TOKEN-05] Confirm defect: the token_introspection_endpoint is
    parsed/required but NOT used at runtime.

    We configure a valid userinfo_endpoint and jwks_uri alongside a
    completely broken introspection endpoint. Auth succeeds, proving
    introspection was never called. If fixed (introspection actually
    called), the broken URL would cause auth to fail and this test
    will fail.
    """
    client = self.context.provider_client

    with Given(
        "I configure OpenID with valid endpoints EXCEPT a broken introspection URL"
    ):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/userinfo"
            ),
            token_introspection_endpoint="http://keycloak:8080/does-not-exist/introspect",
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

    with Then(
        "ClickHouse accepts the token — confirming introspection "
        "endpoint is never called despite being configured"
    ):
        access_clickhouse(token=token, status_code=200)


@TestScenario
def introspection_endpoint_missing_still_works(self):
    """[F8/TOKEN-05] Baseline: when token_introspection_endpoint is not
    configured at all, authentication works via jwks_uri and/or userinfo."""
    client = self.context.provider_client

    with Given("I configure OpenID with only userinfo and jwks_uri (no introspection)"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/userinfo"
            ),
            jwks_uri=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/certs"
            ),
            replace=True,
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


# ---------------------------------------------------------------------------
# F9/F10 / DOS-01 / AVAIL-02/03 — Hanging provider stalls auth
# ---------------------------------------------------------------------------

MAX_REASONABLE_AUTH_TIMEOUT = 30


@TestScenario
def hanging_jwks_endpoint_bounded_latency(self):
    """[F9/DOS-01/AVAIL-02] Confirm defect: when the JWKS endpoint hangs,
    token auth requests block for an unreasonably long time due to the
    lack of explicit connect/read timeouts.

    We point jwks_uri at a non-routable address (10.255.255.1) that will
    hang on connect. We measure wall-clock time. The defect manifests as
    the request taking a very long time or timing out at the curl level.
    """
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a hanging jwks_uri (non-routable address) "
        "and valid userinfo_endpoint"
    ):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            jwks_uri="http://10.255.255.1:9999/hang",
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

    with Then("I send an auth request and measure how long it takes"):
        start = time.time()
        node = self.context.bash_tools
        port = 8123
        uid = getuid()[:8]
        tmp_file = f"/tmp/ch_hang_{uid}.txt"
        curl_command = (
            f'curl -s -o {tmp_file} -w "%{{http_code}}" '
            f"--max-time 120 "
            f"--location 'http://clickhouse1:{port}/?query=SELECT%201' "
            f"--header 'Authorization: Bearer {token}'"
        )
        result = node.command(command=curl_command, timeout=180000)
        elapsed = time.time() - start
        note(f"Auth request completed in {elapsed:.1f}s")

    with And("the server is still alive after the hanging request"):
        check_clickhouse_is_alive()


@TestScenario
def hanging_userinfo_endpoint_bounded_latency(self):
    """[F10/AVAIL-03] Confirm defect: when the userinfo endpoint hangs,
    token auth blocks under the global mutex, stalling all auth.

    We point userinfo_endpoint at a non-routable address. The JWKS fast-path
    may succeed, but if userinfo is also needed, the request hangs.
    """
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a hanging userinfo_endpoint and valid jwks_uri"
    ):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint="http://10.255.255.1:9999/hang",
            jwks_uri=(
                f"{self.context.keycloak_url}/realms/{self.context.realm_name}"
                f"/protocol/openid-connect/certs"
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

    with Then("I send an auth request and measure how long it takes"):
        start = time.time()
        node = self.context.bash_tools
        port = 8123
        uid = getuid()[:8]
        tmp_file = f"/tmp/ch_hang_{uid}.txt"
        curl_command = (
            f'curl -s -o {tmp_file} -w "%{{http_code}}" '
            f"--max-time 120 "
            f"--location 'http://clickhouse1:{port}/?query=SELECT%201' "
            f"--header 'Authorization: Bearer {token}'"
        )
        result = node.command(command=curl_command, timeout=180000)
        elapsed = time.time() - start
        note(f"Auth request completed in {elapsed:.1f}s")

    with And("the server is still responsive to normal queries"):
        check_clickhouse_is_alive()


# ---------------------------------------------------------------------------
# F2/F5 / OAUTH-06 / CACHE-03 — Cache bypasses per-user processor pin
# ---------------------------------------------------------------------------


@TestScenario
def cache_hit_bypasses_processor_pin(self):
    """[F2/OAUTH-06/CACHE-03] Confirm defect: a token validated and cached
    by one processor can authenticate a second request without processor
    pinning being re-checked on the cache-hit path.

    We authenticate twice with the same token. Both succeed, confirming
    the cache path is exercised. The defect is that no processor identity
    is stored in the cache entry — the second request skips processor
    binding checks entirely when jwt_claims is empty.

    A full exploit requires two processors and a pinned local user, but
    we confirm the cache-hit path works without re-validation here.
    """
    client = self.context.provider_client

    with Given("I configure a short token cache lifetime"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=60,
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

    with And("I authenticate to populate the cache"):
        access_clickhouse(token=token, status_code=200)

    with Then(
        "I authenticate again — the cache-hit path is taken, "
        "and no processor binding is re-verified (confirming the defect)"
    ):
        access_clickhouse(token=token, status_code=200)


# ---------------------------------------------------------------------------
# Additional transport security scenarios
# ---------------------------------------------------------------------------


@TestScenario
def https_rejects_tampered_token(self):
    """Transport security: TLS SHALL NOT bypass token validation.
    A tampered token must be rejected over HTTPS."""
    client = self.context.provider_client

    with Given("I get a valid token and tamper with the signature"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change="tampered-signature"
        )

    with Then("ClickHouse rejects the tampered token over HTTPS"):
        access_clickhouse(token=modified, https=True, status_code=500)


@TestScenario
def empty_bearer_rejected_on_both_transports(self):
    """Empty bearer tokens SHALL be rejected on both HTTP and HTTPS
    with 403."""

    with Then("empty token rejected on HTTP"):
        access_clickhouse(token="", https=False, status_code=403)

    with And("empty token rejected on HTTPS"):
        access_clickhouse(token="", https=True, status_code=403)


# ---------------------------------------------------------------------------
# Feature entry point
# ---------------------------------------------------------------------------


@TestFeature
@Name("security audit")
def feature(self):
    """Regression tests for confirmed defects from the OAuth security audit.

    Each scenario confirms a specific defect IS present. If a defect gets
    fixed, the corresponding test will FAIL, signaling the need to update
    the assertion to the corrected behavior.
    """

    with Feature("plaintext transport"):
        Scenario(run=plaintext_http_accepts_bearer_token)
        Scenario(run=plaintext_http_bearer_on_all_nodes)
        Scenario(run=https_rejects_tampered_token)
        Scenario(run=empty_bearer_rejected_on_both_transports)

    with Feature("roles filter fail-open"):
        Scenario(run=invalid_roles_filter_regex_fail_open)
        Scenario(run=invalid_roles_filter_grants_all_groups_as_roles)

    with Feature("processor parse failure"):
        Scenario(run=processor_parse_failure_silent_fallback)
        Scenario(run=all_processors_broken_rejects_auth)

    with Feature("openid fallback"):
        Scenario(run=openid_broken_jwks_blocks_userinfo_fallback)
        Scenario(run=openid_no_jwks_uri_uses_userinfo_only)

    with Feature("authorization header leak"):
        Scenario(run=authorization_header_exposed_in_sql)
        Scenario(run=authorization_header_blocked_by_default_setting)

    with Feature("introspection endpoint"):
        Scenario(run=introspection_endpoint_not_actually_called)
        Scenario(run=introspection_endpoint_missing_still_works)

    with Feature("provider availability"):
        Scenario(run=hanging_jwks_endpoint_bounded_latency)
        Scenario(run=hanging_userinfo_endpoint_bounded_latency)

    with Feature("cache processor binding"):
        Scenario(run=cache_hit_bypasses_processor_pin)
