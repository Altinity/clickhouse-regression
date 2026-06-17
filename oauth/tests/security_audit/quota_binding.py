"""[L-08 / L-17] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_jwt_auth,
    change_user_quota,
)


@TestScenario
@Name("L-08 L-17 / 1")
def scenario_1(self):
    """[L-08 / L-17]"""
    uid = getuid()[:6]
    target_user = f"u_{uid}"
    other_secret = "other_secret"
    processor_secret = "shared_secret_for_tests"

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=processor_secret,
            token_cache_lifetime=0,
            replace_section=True,
        )

    with And(f"a local user '{target_user}' pinned to the processor"):
        change_user_jwt_auth(username=target_user, processor="proc_a")

    with And(f"a quota limiting '{target_user}' to 3 failed auths per hour"):
        change_user_quota(username=target_user, failed_sequential_authentications=3)

    with When("I send 3 tokens with this sub signed by a non-matching secret"):
        for i in range(3):
            token = create_static_jwt(
                user_name=target_user,
                secret=other_secret,
                algorithm="HS256",
                expiration_minutes=5,
            )
            access_clickhouse(token=token, status_code=403)

    with Then("[L-08 / L-17]"):
        valid_token = create_static_jwt(
            user_name=target_user,
            secret=processor_secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        body = access_clickhouse(token=valid_token, status_code=403)
        assert (
            "QUOTA" in body.upper() or "EXCEED" in body.upper() or "403" in body
        ), error()


@TestFeature
@Name("L-08 L-17")
def feature(self):
    """[L-08 / L-17]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
