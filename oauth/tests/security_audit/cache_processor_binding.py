"""[H-03] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
)


@TestScenario
@Name("H-03 / 1")
def scenario_1(self):
    """[H-03]"""
    client = self.context.provider_client

    with Given("I configure a token cache lifetime"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=60,
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

    with And("I authenticate to populate the cache"):
        access_clickhouse(token=token, status_code=200)

    with Then("[H-03]"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("H-03")
def feature(self):
    """[H-03]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
