"""[M-30] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
)
from oauth.tests.steps.keycloak_realm import keycloak_openid_processor_args


@TestScenario
@Name("M-30 / 1")
def scenario_1(self):
    """[M-30]"""
    client = self.context.provider_client
    sid = "sess_" + getuid()[:8]
    tbl = "t_" + getuid()[:8]

    with Given("a Keycloak OpenID processor"):
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=60,
            replace_section=True,
            **keycloak_openid_processor_args(),
        )

    with And("I get a valid Keycloak token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When(f"request 1 creates a temporary table '{tbl}' under session_id='{sid}'"):
        access_clickhouse(
            token=token,
            query=f"CREATE TEMPORARY TABLE {tbl} (x UInt8) ENGINE = Memory",
            query_params={"session_id": sid},
            status_code=200,
        )

    with Then("[M-30]"):
        body = access_clickhouse(
            token=token,
            query=f"SELECT count() FROM {tbl}",
            query_params={"session_id": sid},
            status_code=200,
        )
        assert body.strip() == "0", error()


@TestFeature
@Name("M-30")
def feature(self):
    """[M-30]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
