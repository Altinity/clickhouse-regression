"""[H-07] Token processor parse failure — fail-closed.

Fixed in antalya-26.3 (PR #1777, commit H-07): ``parseTokenProcessors``
is now all-or-nothing. If ANY processor fails to parse, ALL token
authentication is disabled for that config cycle.
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_config,
    check_clickhouse_is_alive,
)


@TestScenario
@Name("H-07 / 1")
def scenario_1(self):
    """A valid processor SHALL be disabled when a sibling processor
    fails to parse (all-or-nothing).
    """
    client = self.context.provider_client

    with Given("I configure a valid 'keycloak' processor"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
        )

    with And("I add a second processor with an invalid type"):
        change_token_processors(
            processor_name="proc_b",
            processor_type="completely_invalid_type_xyz",
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("token auth is disabled because proc_b failed to parse"):
        access_clickhouse(token=token, status_code=400)

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
        token = client.OAuthProvider.get_oauth_token().access_token

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
