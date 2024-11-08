from testflows.core import *
from testflows.asserts import error

from jwt_authentication.requirements import *

from helpers.common import getuid

import jwt_authentication.tests.steps as steps


def curl_with_jwt(token, ip, https=False):
    http_prefix = "https" if https else "http"
    curl = f'curl -H "X-ClickHouse-JWT-Token: Bearer {token}" "{http_prefix}://{ip}:8123/?query=SELECT%20currentUser()"'
    return curl


def test_static_key():
    res = (
        current()
        .context.node.command(
            curl_with_jwt(
                token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqd3RfdXNlciJ9."
                "kfivQ8qD_oY0UvihydeadD7xvuiO3zSmhFOc_SGbEPQ",
                ip="localhost",
            ),
        )
        .output
    )
    assert res == "jwt_user"


def test_static_key_2():
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqd3RfdXNlciJ9.kfivQ8qD_oY0UvihydeadD7xvuiO3zSmhFOc_SGbEPQ"
    res = current().context.node.query(
        "SELECT currentUser()", settings=[("jwt", token)]
    )

    assert res.output == "jwt_user"


@TestScenario
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key(self):
    """Check jwt authentication with static key."""

    user_name = f"jwt_user_{getuid()}"

    with Given("create user with jwt authentication"):
        steps.add_jwt_user_to_users_xml(user_name=user_name)

    with When("create jwt token"):
        token = steps.create_jwt_token(user_name=user_name)

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)
        steps.check_curl_jwt_login(user_name=user_name, token=token)
        pause()


@TestScenario
@Name("jwt authentication")
def scenario(self, node="clickhouse1"):
    """Check jwt authentication."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_static_key)
