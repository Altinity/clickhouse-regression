"""[H-03 / H-14 / H-17 / H-22 / M-32] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_user_jwt_auth,
)
from oauth.tests.security_audit.common import two_processor_setup


@TestScenario
@Name("H-03 H-14 M-32 H-22 / 1")
def scenario_1(self):
    """[H-03 / H-14 / M-32 / H-22]"""
    with Given("a two-processor setup"):
        setup = two_processor_setup()

    with And("jwt_user is pinned to processor A in users.d"):
        change_user_jwt_auth(
            username="jwt_user",
            processor=setup["strict_name"],
        )

    with When("I mint an HS256 token with sub=jwt_user signed by processor B's secret"):
        token = create_static_jwt(
            user_name="jwt_user",
            secret=setup["lenient_secret"],
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("[H-03 / H-14 / M-32 / H-22]"):
        body = access_clickhouse(token=token, status_code=200)
        assert "jwt_user" in body, error()


@TestScenario
@Name("H-17 / 1")
def scenario_2(self):
    """[H-17]"""
    with Given("a two-processor setup"):
        setup = two_processor_setup()

    with And("I pin jwt_user to processor B with a claim requirement"):
        change_user_jwt_auth(
            username="jwt_user",
            processor=setup["lenient_name"],
            claims={"expected_sub": "alice"},
        )

    with When("I submit a token whose sub does not match the claim requirement"):
        token = create_static_jwt(
            user_name="bob",
            secret=setup["lenient_secret"],
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token, status_code=403)

    with When("I re-submit the same token"):
        access_clickhouse(token=token, status_code=403)

    with Then("[H-17]"):
        note("see oauth/new_audit_review/combined-issues.md")


@TestFeature
@Name("H-03 H-14 H-17 H-22 M-32")
def feature(self):
    """[H-03 / H-14 / H-17 / H-22 / M-32]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
