"""[M-06] OpenID introspection endpoint — runtime behaviour.

Fixed in antalya-26.3 (PR #1799): introspection is now actually
performed when ``introspection_client_id`` and
``introspection_client_secret`` are configured. An unreachable
introspection endpoint fails the authentication (no silent fallback
to userinfo-only).
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    assert_token_rejected,
    change_token_processors,
    change_user_directories_config,
)


@TestScenario
@Name("M-06 / 1")
def scenario_1(self):
    """An unreachable introspection endpoint SHALL cause authentication
    to fail even when userinfo is valid (introspection is not silently
    skipped).
    """
    client = self.context.provider_client

    with Given(
        "I configure OpenID with valid userinfo " "and an unreachable introspection URL"
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

    with Then("authentication fails because introspection is unreachable"):
        assert_token_rejected(token=token)


@TestScenario
@Name("M-06 / 2")
def scenario_2(self):
    """[M-06]"""
    client = self.context.provider_client

    with Given("I configure OpenID with only userinfo (no introspection)"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
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
@Name("M-06")
def feature(self):
    """[M-06]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
