"""[H-16 / M-01 / M-02 / M-13 / M-NEW-01] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
    change_user_jwt_auth,
    reload_clickhouse_config,
)
from oauth.tests.security_audit.common import search_server_log


@TestScenario
@Name("H-16 / 1")
def scenario_1(self):
    """[H-16]"""
    client = self.context.provider_client
    secret = "shared_secret_for_tests"

    with Given("a provider OpenID processor + a static-key processor"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=0,
            replace_section=True,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
        )
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret,
            token_cache_lifetime=0,
        )

    with When("I mint an HS256 token validatable only by proc_b"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("[H-16]"):
        access_clickhouse(token=token, status_code=403)


@TestScenario
@Name("M-01 / 1")
def scenario_2(self):
    """[M-01]"""
    secret_a = "secret_a_for_tests"
    secret_b = "secret_b_for_tests"
    secret_c = "secret_c_for_tests"

    with Given("three static-key processors all accepting HS256"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret_a,
            token_cache_lifetime=0,
            replace_section=True,
        )
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret_b,
            token_cache_lifetime=0,
        )
        change_token_processors(
            processor_name="proc_c",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret_c,
            token_cache_lifetime=0,
        )

    marker = "mp_" + getuid()[:6]

    with When(
        f"I mint a token signed by proc_b's secret (sub carries marker {marker!r})"
    ):
        token = create_static_jwt(
            user_name=marker,
            secret=secret_b,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token, status_code=200)

    with Then("[M-01]"):
        found = search_server_log(self.context.node, marker, lines=2000)
        note(f"Log lines mentioning {marker!r}: {found!r}")
        hits = [
            line
            for line in found.splitlines()
            if "proc_a" in line or "proc_b" in line or "proc_c" in line
        ]
        assert not hits, error()


@TestScenario
@Name("M-02 / 1")
def scenario_3(self):
    """[M-02]"""
    secret_1 = "secret_1_for_tests"
    secret_2 = "secret_2_for_tests"

    with Given("a static-key processor with a 5-minute token cache"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret_1,
            token_cache_lifetime=300,
            replace_section=True,
        )

    with When("I prime the cache with a token signed by secret_1"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret_1,
            algorithm="HS256",
            expiration_minutes=15,
        )
        access_clickhouse(token=token, status_code=200)

    with When(
        "I rewrite the processor to use a different secret and "
        "SYSTEM RELOAD CONFIG (no restart)"
    ):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret_2,
            token_cache_lifetime=300,
            replace_section=True,
        )
        reload_clickhouse_config()

    with Then("[M-02]"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Name("M-13 / 1")
def scenario_4(self):
    """[M-13]"""
    client = self.context.provider_client

    with Given("a provider OpenID processor"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=0,
            replace_section=True,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
        )

    with And(
        "a token directory with a valid transform that strips the 'grafana-' prefix"
    ):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
            roles_transform="s/^grafana-//",
        )

    with And("I get a valid token from Keycloak (user 'demo')"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("baseline auth succeeds with the valid transform"):
        access_clickhouse(token=token, status_code=200)

    with When("I reconfigure the token directory with a malformed transform regex"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
            roles_transform="s/[invalid(regex",
        )

    with And("I refresh the token"):
        token2 = client.OAuthProvider.get_oauth_token().access_token

    with Then("[M-13]"):
        access_clickhouse(token=token2, status_code=200)


@TestScenario
@Name("M-NEW-01 / 1")
def scenario_5(self):
    """[M-NEW-01]"""
    secret = "shared_secret_for_tests"
    uid = getuid()[:6]
    user_a = f"a_{uid}"
    user_b = f"b_{uid}"

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret,
            token_cache_lifetime=0,
            replace_section=True,
        )

    with And(
        "the token user directory points at that processor and names "
        "the existing 'readonly' profile as default_profile"
    ):
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
            default_profile="readonly",
        )

    with When(f"I auto-provision user '{user_a}'"):
        token_a = create_static_jwt(
            user_name=user_a,
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token_a, status_code=200)

    with Then("baseline: write rejected"):
        body = access_clickhouse(
            token=token_a,
            query=(f"CREATE TEMPORARY TABLE t_{uid}_a (x UInt8) ENGINE = Memory"),
            status_code=500,
        )
        assert "READONLY" in body.upper() or "CANNOT EXECUTE" in body.upper(), error()

    with When(
        "I reconfigure the token directory with a default_profile that "
        "DOES NOT EXIST"
    ):
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
            default_profile=f"nonexistent_profile_{uid}",
        )

    with And(f"I auto-provision a fresh user '{user_b}'"):
        token_b = create_static_jwt(
            user_name=user_b,
            secret=secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token_b, status_code=200)

    with Then("[M-NEW-01]"):
        access_clickhouse(
            token=token_b,
            query=(f"CREATE TEMPORARY TABLE t_{uid}_b (x UInt8) ENGINE = Memory"),
            status_code=200,
        )


@TestFeature
@Name("H-16 M-01 M-02 M-13 M-NEW-01")
def feature(self):
    """[H-16 / M-01 / M-02 / M-13 / M-NEW-01]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
