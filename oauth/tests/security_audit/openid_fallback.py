"""[M-05] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.keycloak_realm import keycloak_openid_processor_args


@TestScenario
@Name("M-05 / 1")
def scenario_1(self):
    """[M-05]"""
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with an unreachable jwks_uri "
        "but valid userinfo_endpoint"
    ):
        kc = keycloak_openid_processor_args()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            jwks_uri="http://keycloak:8080/invalid/jwks/does-not-exist",
            userinfo_endpoint=kc["userinfo_endpoint"],
            token_introspection_endpoint=kc["token_introspection_endpoint"],
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("[M-05]"):
        access_clickhouse(token=token, status_code=403)


@TestScenario
@Name("M-05 / 2")
def scenario_2(self):
    """[M-05]"""
    client = self.context.provider_client

    with Given(
        "I configure an OpenID processor with userinfo_endpoint only (no jwks_uri)"
    ):
        kc = keycloak_openid_processor_args()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=kc["userinfo_endpoint"],
            token_introspection_endpoint=kc["token_introspection_endpoint"],
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


@TestFeature
@Name("M-05")
def feature(self):
    """[M-05]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
