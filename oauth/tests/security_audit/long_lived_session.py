"""[H-05 / M-28] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    open_native_jwt_session,
)


@TestScenario
@Name("M-28 / 1")
def scenario_1(self):
    """[M-28]"""
    secret = "shared_secret_for_tests"

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret,
            token_cache_lifetime=0,
            replace_section=True,
        )

    with And("I mint an HS256 token for 'alice'"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret,
            algorithm="HS256",
            expiration_minutes=15,
        )

    with When("I open a native TCP session on clickhouse1 with --jwt"):
        session = open_native_jwt_session(
            token=token, container_node="clickhouse1", target_host="clickhouse1"
        )

    with And("the session is live"):
        body = session.query("SELECT currentUser()")
        assert "alice" in body, error()

    with When(
        "I REPLACE the processors with a different one whose secret "
        "cannot validate the existing token"
    ):
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="completely_different_secret",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with Then("[M-28]"):
        body = session.query("SELECT 1")
        assert "1" in body, error()


@TestScenario
@Name("H-05 / 1")
def scenario_2(self):
    """[H-05]"""
    import time

    secret = "shared_secret_for_tests"

    with Given("a static-key processor with token_cache_lifetime=0"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key=secret,
            token_cache_lifetime=0,
            replace_section=True,
        )

    with And("I mint a short-lived token (expires in 1 minute)"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret,
            algorithm="HS256",
            expiration_minutes=1,
        )

    with When("I open a TCP session"):
        session = open_native_jwt_session(
            token=token, container_node="clickhouse1", target_host="clickhouse1"
        )

    with And("the session is live"):
        body = session.query("SELECT currentUser()")
        assert "alice" in body, error()

    with And("I sleep past the token's exp (~70s)"):
        time.sleep(70)

    with Then("[H-05]"):
        body = session.query("SELECT 1")
        assert "1" in body, error()


@TestFeature
@Name("H-05 M-28")
def feature(self):
    """[H-05 / M-28]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
