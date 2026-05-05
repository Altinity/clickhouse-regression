"""[H-20] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from oauth.tests.steps.clikhouse import access_clickhouse


@TestScenario
@Name("H-20 / 1")
def scenario_1(self):
    """[H-20]"""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "I query ClickHouse for the Authorization header via bearer auth "
        "with allow_get_client_http_header enabled"
    ):
        body = access_clickhouse(
            token=token,
            status_code=200,
            query=(
                "SELECT getClientHTTPHeader('Authorization') "
                "SETTINGS allow_get_client_http_header=1"
            ),
        )

    with And("[H-20]"):
        assert token in body, error()


@TestScenario
@Name("H-20 / 2")
def scenario_2(self):
    """[H-20]"""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then(
        "the query fails with HTTP 500 because the function is disabled by default"
    ):
        body = access_clickhouse(
            token=token,
            status_code=500,
            query="SELECT getClientHTTPHeader('Authorization')",
        )

    with And("the raw token is not present in the error message"):
        assert token not in body, error()


@TestFeature
@Name("H-20")
def feature(self):
    """[H-20]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
