"""[H-23 / M-27 / L-14] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
)


@TestScenario
@Name("H-23 / 1")
def scenario_1(self):
    """[H-23]"""
    with Given("two static-key processors with different secrets"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="secret_a_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="secret_b_for_tests",
            token_cache_lifetime=0,
        )

    with When("I mint two 'alice' tokens signed by different processors"):
        token_a = create_static_jwt(
            user_name="alice",
            secret="secret_a_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_b = create_static_jwt(
            user_name="alice",
            secret="secret_b_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )

    with And("both tokens authenticate successfully"):
        access_clickhouse(token=token_a, status_code=200)
        access_clickhouse(token=token_b, status_code=200)

    with Then("[H-23]"):
        node = self.context.node
        result = node.query("SELECT count() FROM system.users WHERE name = 'alice'")
        count = int(result.output.strip())
        assert count == 1, error()


@TestScenario
@Name("M-27 / 1")
def scenario_2(self):
    """[M-27]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I mint two tokens with empty sub"):
        token_1 = create_static_jwt(
            payload={"sub": ""},
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_2 = create_static_jwt(
            payload={"sub": "", "nonce": "distinguisher"},
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("[M-27]"):
        body_1 = access_clickhouse(token=token_1, status_code=200)
        body_2 = access_clickhouse(token=token_2, status_code=200)
        assert body_1 == body_2, error()


@TestScenario
@Name("L-14 / 1")
def scenario_3(self):
    """[L-14]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I authenticate as ascii 'alice' and as Cyrillic 'аlice' (U+0430)"):
        token_ascii = create_static_jwt(
            user_name="alice",
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_cyr = create_static_jwt(
            user_name="аlice",
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token_ascii, status_code=200)
        access_clickhouse(token=token_cyr, status_code=200)

    with Then("[L-14]"):
        node = self.context.node
        result = node.query(
            "SELECT count() FROM system.users " "WHERE name = 'alice' OR name = 'аlice'"
        )
        count = int(result.output.strip())
        assert count >= 2, error()


@TestFeature
@Name("H-23 M-27 L-14")
def feature(self):
    """[H-23 / M-27 / L-14]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
