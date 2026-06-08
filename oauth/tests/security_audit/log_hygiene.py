"""[M-29 / L-13 / L-16 / L-09] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
)
from oauth.tests.security_audit.common import search_server_log


@TestScenario
@Name("M-29 / 1")
def scenario_1(self):
    """[M-29]"""
    marker = "MARKER_" + getuid()[:8]

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I mint a token with a newline in sub and authenticate"):
        token = create_static_jwt(
            payload={"sub": f"alice\n{marker}"},
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token)

    with Then("[M-29]"):
        found = search_server_log(self.context.node, marker)
        assert marker in found, error()


@TestScenario
@Name("L-13 / 1")
def scenario_2(self):
    """[L-13]"""
    client = self.context.provider_client

    with Given("a provider-backed OpenID processor and a live token"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=0,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I authenticate"):
        access_clickhouse(token=token)

    with Then("[L-13]"):
        found = search_server_log(self.context.node, "demo", lines=1000)
        assert "demo" in found, error()


@TestScenario
@Name("L-16 / 1")
def scenario_3(self):
    """[L-16]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    kid_prefix = "probe_" + getuid()[:6] + "_"

    with When("I send 8 requests each with a unique kid header"):
        for i in range(8):
            token = create_static_jwt(
                user_name="alice",
                secret="shared_secret_for_tests",
                algorithm="HS256",
                key_id=f"{kid_prefix}{i}",
                expiration_minutes=5,
            )
            access_clickhouse(token=token)

    with Then("[L-16]"):
        found = search_server_log(self.context.node, kid_prefix, lines=2000)
        distinct = {
            line.split(kid_prefix)[1].split()[0] if kid_prefix in line else ""
            for line in found.splitlines()
        }
        distinct.discard("")
        note(f"Distinct kids observed in log: {sorted(distinct)}")
        assert len(distinct) >= 2, error()


@TestScenario
@Name("L-09 / 1")
def scenario_4(self):
    """[L-09]"""
    sentinel = "alice;DROP_" + getuid()[:6]

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I authenticate with a sub containing control characters"):
        token = create_static_jwt(
            user_name=sentinel,
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token)

    with Then("[L-09]"):
        node = self.context.node
        safe_name = sentinel.replace("'", "''")
        result = node.query(
            f"SELECT count() FROM system.users WHERE name = '{safe_name}'"
        )
        count = int(result.output.strip())
        assert count == 1, error()


@TestFeature
@Name("M-29 L-13 L-16 L-09")
def feature(self):
    """[M-29 / L-13 / L-16 / L-09]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
