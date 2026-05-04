"""[M-06] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.keycloak_realm import keycloak_openid_processor_args


@TestScenario
@Name("M-06 / 1")
def scenario_1(self):
    """[M-06]"""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with valid endpoints "
        "and an unreachable introspection URL"
    ):
        kc = keycloak_openid_processor_args()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=kc["userinfo_endpoint"],
            token_introspection_endpoint="http://keycloak:8080/does-not-exist/introspect",
            jwks_uri=kc["jwks_uri"],
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("[M-06]"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Name("M-06 / 2")
def scenario_2(self):
    """[M-06]"""
    client = self.context.provider_client

    with Given("I configure OpenID with only userinfo and jwks_uri (no introspection)"):
        kc = keycloak_openid_processor_args()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=kc["userinfo_endpoint"],
            jwks_uri=kc["jwks_uri"],
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


@TestFeature
@Name("M-06")
def feature(self):
    """[M-06]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
