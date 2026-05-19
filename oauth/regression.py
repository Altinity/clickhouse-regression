#!/usr/bin/env python3
import sys
import os

from testflows.core import *


append_path(sys.path, "..")

from helpers.common import check_if_not_antalya_build
from helpers.cluster import create_cluster
from helpers.argparser import argparser as base_argparser
from helpers.argparser import CaptureClusterArgs
from oauth.requirements.requirements import *
from oauth.tests.steps import keycloak_realm as keycloak
from oauth.tests.steps.provider_protocol import assert_provider_contract


def argparser(parser):
    """Add arguments to the argument parser for OAuth tests."""
    base_argparser(parser)

    parser.add_argument(
        "--tenant-id",
        type=str,
        dest="tenant_id",
        help="Tenant ID for Azure AD",
        metavar="path",
        default=None,
    )

    parser.add_argument(
        "--client-id",
        type=str,
        dest="client_id",
        help="Client ID for Azure AD application",
        metavar="string",
        default=None,
    )

    parser.add_argument(
        "--client-secret",
        type=str,
        dest="client_secret",
        help="Client secret for Azure AD application",
        metavar="path",
        default=None,
    )

    parser.add_argument(
        "--identity-provider",
        type=str,
        dest="identity_provider",
        help="Identity provider to use for OAuth authentication",
        metavar="string",
        default="Keycloak",
    )

    parser.add_argument(
        "--refresh-token",
        type=str,
        dest="refresh_token",
        help="Refresh token for Google OAuth (obtained out of band)",
        metavar="string",
        default=None,
    )


xfails = {
    "/oauth/security audit/M-06 runtime revocation/M-06 / 3 disabled user accepted with jwks_uri": [
        (
            Fail,
            "DEFECT_M06 (alias F8 / TOKEN-05) — OpenID processor with "
            "jwks_uri uses the JWT-fastpath and never consults userinfo / "
            "introspection on cache miss, so the IdP's runtime decision "
            "to disable the user is not observed until the JWT's own exp "
            "passes. See src/Access/TokenProcessorsOpaque.cpp:339-414 "
            "(TODO at line 353).",
        )
    ],
    "/oauth/security audit/M-06 runtime revocation/M-06 / 4 deleted user accepted with jwks_uri": [
        (
            Fail,
            "DEFECT_M06 (alias F8 / TOKEN-05) — same root cause as "
            "M-06 / 3: the JWT-fastpath does not observe IdP user "
            "deletion either. userinfo_endpoint would 401 a deleted "
            "user but is never consulted while local JWKS verification "
            "of the issued JWT still succeeds.",
        )
    ],
    "/oauth/security audit/H-16 jwt decode uncaught/H-16 / 2 malformed signature base64 leaks runtime_error": [
        (
            Fail,
            "DEFECT_H16 (alias F20 / TOKEN-06) — JwksJwtProcessor::"
            "resolveAndValidate has no top-level try/catch around "
            "jwt::decode; a malformed-base64 JWT segment leaks "
            "std::runtime_error out as Code: 1001 (HTTP 500) with no "
            "AUTHENTICATION_FAILED marker. See "
            "src/Access/TokenProcessorsJWT.cpp.",
        )
    ],
    "/oauth/security audit/H-16 jwt decode uncaught/H-16 / 3 non-base64 signature leaks runtime_error": [
        (
            Fail,
            "DEFECT_H16 (alias F20 / TOKEN-06) — same root cause as "
            "H-16 / 2: any exception thrown by jwt::decode escapes "
            "JwksJwtProcessor::resolveAndValidate uncaught.",
        )
    ],
    "/oauth/jwt_manipulation/malformed token string": [
        (
            Fail,
            "DEFECT_H16 (alias F20 / TOKEN-06) — third reproducer of "
            "the same JwksJwtProcessor::resolveAndValidate uncaught-"
            "exception bug: ``not.a.valid-jwt`` parses to 3 segments "
            "but the second segment is not base64url-clean, so "
            "jwt::decode throws std::runtime_error which leaks as "
            "Code: 1001 (HTTP 500) instead of AUTHENTICATION_FAILED. "
            "Tracked alongside the security_audit/H-16 scenarios.",
        )
    ],
    "/oauth/configuration/invalid roles filter regex in user directory": [
        (
            Fail,
            "DEFECT_H06 (alias F16 / AUTHZ-02) — invalid <roles_filter> "
            "regex fails open: ClickHouse silently tolerates the "
            "malformed pattern and grants the token's <common_roles> "
            "as if no filter were configured. SRS 6.2.1.1.3 says auth "
            "SHALL fail when the roles section is incorrectly defined; "
            "the existing security_audit/H-06 scenarios already pin "
            "the buggy behaviour by asserting status_code=200, this "
            "new scenario asserts the SRS-correct behaviour and will "
            "go green when the upstream fix lands.",
        )
    ],
    "/oauth/configuration/multiple token entries in user directories": [
        (
            Fail,
            "DEFECT_M33 (alias CFG-04) — duplicate <token> entries "
            "inside <user_directories> are silently merged and auth "
            "proceeds with whichever entry won the merge. SRS "
            "6.2.1.1.4 says auth SHALL NOT be allowed when "
            "user_directories contains multiple duplicate entries. "
            "Same fail-open family as H-06 / H-07 (silent toleration "
            "of an invalid config). New finding from runtime audit-"
            "review pass — next available Series-A medium ID per "
            "all-issues.md §4. Will go green when the parser starts "
            "rejecting duplicate <token> children.",
        )
    ],
    "/oauth/cache semantics/cache entry capped at token exp when token expires first": [
        (
            Fail,
            "DEFECT_H_NEW_30 — JWT exp never propagated to cache TTL "
            "on the StaticKeyJwtProcessor / JwksJwtProcessor fastpaths. "
            "resolveAndValidate never calls "
            "credentials.setExpiresAt(decoded_jwt.get_expires_at()) on "
            "the JWT codepaths, so a token past its IdP-issued exp "
            "keeps authenticating for up to token_cache_lifetime. The "
            "opaque/OpenID-userinfo paths set it correctly; the bug "
            "is specific to the JWT fastpath this scenario exercises "
            "(OpenID processor with jwks_uri configured). Violates SRS "
            "13.1.5 'Common.Cache.Behavior' which mandates "
            "cache_entry_expires_at = min(token.exp, now + "
            "token_cache_lifetime). Will go green once "
            "TokenProcessorsJWT.cpp propagates exp to the cache write "
            "in ExternalAuthenticators.cpp:624-640.",
        )
    ],
    "/oauth/client oauth login/browser flow security/loopback /start must not leak oauth state in Location": [
        (
            Fail,
            "PR #1606 follow-up audit: loopback /start must not redirect with "
            "a Location header bearing oauth state= (see "
            "issue-pr-1606-oauth-audit-round2.md).",
        )
    ],
    "/oauth/client oauth login/browser flow security/oversized OIDC discovery document fails without hanging": [
        (
            Fail,
            "PR #1606 follow-up audit: OIDC discovery should bound download "
            "size (issue-pr-1606-oauth-audit-round2.md).",
        )
    ],
}

ffails = {
    "/oauth/*": (
        Skip,
        "OAuth not implemented in non Antalya build",
        check_if_not_antalya_build,
    ),
    "/oauth/client oauth login/connection block segfault/*": (
        Skip,
        "Waiting for upstream fix: Altinity/ClickHouse#1696 / "
        "ClickHouse/ClickHouse#103603 (Client::login segfault on empty "
        "hosts_and_ports when --login is combined with --connection and "
        "no explicit --host).",
    ),
}


def _load_provider_module(identity_provider):
    """Lazily import provider modules so Azure/Google deps are not required for Keycloak.

    Each loaded module is checked against the contract in
    ``provider_protocol`` so a missing/renamed method fails fast at
    suite startup rather than mid-scenario.
    """
    if identity_provider == "keycloak":
        module = keycloak
    elif identity_provider == "azure":
        from oauth.tests.steps import azure_application as azure

        module = azure
    elif identity_provider == "google":
        from oauth.tests.steps import google_application as google

        module = google
    else:
        raise ValueError(f"Unknown identity provider: {identity_provider}")

    assert_provider_contract(module)
    return module


@TestFeature
@Name("oauth")
@FFails(ffails)
@Specifications(SRS_042_OAuth_Authentication_in_ClickHouse)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    identity_provider=None,
    tenant_id=None,
    client_id=None,
    client_secret=None,
    refresh_token=None,
    run_security=False,
):
    """Run tests for OAuth in ClickHouse."""

    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
        "grafana": ("grafana",),
    }
    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    identity_provider_lower = str(identity_provider).lower()
    provider_module = _load_provider_module(identity_provider_lower)

    with Given("docker-compose cluster"):
        regression_dir = os.path.dirname(os.path.abspath(__file__))
        docker_compose_config = os.path.join(
            regression_dir, "envs", identity_provider_lower
        )
        docker_compose_project_dir = os.path.join(
            docker_compose_config, f"{identity_provider_lower}_env"
        )

        if identity_provider_lower == "azure":
            from azure.identity import ClientSecretCredential
            from msgraph import GraphServiceClient
            from oauth.tests.steps.azure_application import setup_azure_application

            cred = ClientSecretCredential(tenant_id, client_id, client_secret)
            self.context.client = GraphServiceClient(
                credentials=cred, scopes=["https://graph.microsoft.com/.default"]
            )
            application = setup_azure_application()

            self.context.tenant_id = tenant_id
            self.context.client_id = application.app_id
            self.context.client_secret = application.password_credentials[0].secret_text
        elif identity_provider_lower == "keycloak":
            self.context.keycloak_url = "http://keycloak:8080"
            self.context.username = "demo"
            self.context.password = "demo"
            self.context.client_secret = "grafana-secret"
            self.context.client_id = "grafana-client"
            self.context.realm_name = "grafana"
        elif identity_provider_lower == "google":
            self.context.client_id = client_id
            self.context.client_secret = client_secret
            self.context.refresh_token = refresh_token

        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=regression_dir,
            docker_compose_project_dir=docker_compose_project_dir,
        )

        self.context.cluster = cluster
        self.context.provider_client = provider_module
        self.context.provider_name = identity_provider

    self.context.bash_tools = self.context.cluster.node("bash-tools")
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [
        self.context.cluster.node(node) for node in nodes["clickhouse"]
    ]

    with Given(f"{identity_provider} is up and running"):
        if identity_provider_lower == "keycloak":
            for retry in retries(timeout=300, delay=20):
                with retry:
                    keycloak.OAuthProvider.get_oauth_token()

    Scenario(run=load("oauth.tests.sanity", "feature"))
    Scenario(run=load("oauth.tests.configuration", "feature"))
    Scenario(run=load("oauth.tests.authentication", "feature"))
    Scenario(run=load("oauth.tests.tokens", "feature"))
    Scenario(run=load("oauth.tests.parameters_and_caching", "feature"))
    Scenario(run=load("oauth.tests.access_control", "feature"))
    Scenario(run=load("oauth.tests.groups", "feature"))
    Scenario(run=load("oauth.tests.jwt_manipulation", "feature"))
    Scenario(run=load("oauth.tests.tls", "feature"))
    Scenario(run=load("oauth.tests.client_oauth_login.feature", "feature"))

    if run_security:
        Scenario(run=load("oauth.tests.security_audit.feature", "feature"))


if main():
    regression()
