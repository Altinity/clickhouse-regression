"""[M-17] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
)


@TestScenario
@Name("M-17 / 1")
def scenario_1(self):
    """[M-17]"""
    uid = getuid()[:8]
    user = f"u_{uid}"

    with Given("a static-key processor"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="hs256",
            static_key="shared_secret_for_tests",
            token_cache_lifetime=0,
            replace_section=True,
        )

    with When(f"I authenticate as fresh user '{user}'"):
        token = create_static_jwt(
            user_name=user,
            secret="shared_secret_for_tests",
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token, status_code=200)

    with Then("[M-17]"):
        node = self.context.node
        result = node.query(
            "SELECT "
            "host_ip, host_names, host_names_regexp, host_names_like "
            f"FROM system.users WHERE name = '{user}' FORMAT TSV"
        )
        row = result.output.strip()
        note(f"system.users row for {user!r}: {row!r}")
        cells = row.split("\t")
        assert len(cells) == 4, error()
        non_empty = [c for c in cells if c.strip() not in ("", "[]")]
        assert not non_empty, error()


@TestFeature
@Name("M-17")
def feature(self):
    """[M-17]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
