"""[H-02] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from oauth.tests.steps.clikhouse import access_clickhouse


@TestScenario
@Name("H-02 / 1")
def scenario_1(self):
    """[H-02]"""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("[H-02]"):
        body = access_clickhouse(token=token, https=False, status_code=200)
        assert len(body.strip()) > 0, error()

    with And("HTTPS path"):
        access_clickhouse(token=token, https=True, status_code=200)


@TestScenario
@Name("H-02 / 2")
def scenario_2(self):
    """[H-02]"""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    for i, ip in enumerate(["clickhouse1", "clickhouse2", "clickhouse3"], 1):
        with Then(f"[H-02] node {i} ({ip})"):
            access_clickhouse(token=token, ip=ip, https=False, status_code=200)


@TestScenario
@Name("H-02 / 3")
def scenario_3(self):
    """[H-02]"""
    client = self.context.provider_client

    with Given("I get a valid token and modify the signature"):
        token = client.OAuthProvider.get_oauth_token().access_token
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change="modified-signature"
        )

    with Then("[H-02]"):
        access_clickhouse(token=modified, https=True, status_code=500)


@TestScenario
@Name("H-02 / 4")
def scenario_4(self):
    """[H-02]"""

    with Then("empty token rejected on HTTP"):
        access_clickhouse(token="", https=False, status_code=403)

    with And("empty token rejected on HTTPS"):
        access_clickhouse(token="", https=True, status_code=403)


@TestFeature
@Name("H-02")
def feature(self):
    """[H-02]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
