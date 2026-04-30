"""[M-14 / L-11 / L-12] See ``oauth/new_audit_review/combined-issues.md``."""

import datetime

from testflows.core import *

from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
)


@TestScenario
@Name("M-14 / 1")
def scenario_1(self):
    """[M-14]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I mint a token with typ=id+jwt in the header"):
        token = create_static_jwt(
            user_name="alice",
            secret="shared_secret_for_tests",
            algorithm="HS256",
            headers={"typ": "id+jwt"},
            expiration_minutes=5,
        )

    with Then("[M-14]"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Name("L-11 / 1")
def scenario_2(self):
    """[L-11]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I mint a token with iat 5 minutes in the future"):
        future_iat = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=5
        )
        token = create_static_jwt(
            payload={"sub": "alice", "iat": future_iat},
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=15,
        )

    with Then("[L-11]"):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Name("L-12 / 1")
def scenario_3(self):
    """[L-12]"""
    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When("I mint a token with an unknown crit header extension"):
        token = create_static_jwt(
            user_name="alice",
            secret="shared_secret_for_tests",
            algorithm="HS256",
            headers={"crit": ["urn:example:unknown-extension"]},
            expiration_minutes=5,
        )

    with Then("[L-12]"):
        access_clickhouse(token=token, status_code=200)


@TestFeature
@Name("M-14 L-11 L-12")
def feature(self):
    """[M-14 / L-11 / L-12]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
