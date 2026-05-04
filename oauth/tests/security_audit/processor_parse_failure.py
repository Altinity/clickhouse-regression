"""[H-07] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
    check_clickhouse_is_alive,
)
from oauth.tests.steps.keycloak_realm import keycloak_openid_processor_args


@TestScenario
@Name("H-07 / 1")
def scenario_1(self):
    """[H-07]"""
    client = self.context.provider_client

    with Given("I configure a valid 'keycloak' processor"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            **keycloak_openid_processor_args(),
        )

    with And("I add a second processor with an invalid type"):
        change_token_processors(
            processor_name="proc_b",
            processor_type="completely_invalid_type_xyz",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with Then("[H-07]"):
        access_clickhouse(token=token, status_code=200)

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Name("H-07 / 2")
def scenario_2(self):
    """[H-07]"""
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


@TestFeature
@Name("H-07")
def feature(self):
    """[H-07]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
