"""[M-05] See ``oauth/new_audit_review/combined-issues.md``.

Since antalya-26.3 (PR #1799), the OpenID processor no longer accepts
``jwks_uri``. Validation always goes through ``userinfo_endpoint`` /
``token_introspection_endpoint``. The original M-05 scenarios tested
fallback from an unreachable ``jwks_uri`` to ``userinfo``; that
fallback path no longer exists. These scenarios now verify that
userinfo-based validation works correctly as the sole validation path.
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
)


@TestScenario
@Name("M-05 / 1")
def scenario_1(self):
    """[M-05] OpenID processor validates tokens via userinfo when
    introspection endpoint is unreachable."""
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with a valid userinfo_endpoint "
        "and an unreachable introspection URL"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint="http://keycloak:8080/does-not-exist/introspect",
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("[M-05] ClickHouse accepts the token via userinfo"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Name("M-05 / 2")
def scenario_2(self):
    """[M-05] OpenID processor validates tokens via userinfo and
    introspection with both endpoints configured."""
    client = self.context.provider_client

    with Given("I configure an OpenID processor with userinfo and introspection"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("ClickHouse accepts the token"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("M-05")
def feature(self):
    """[M-05]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
