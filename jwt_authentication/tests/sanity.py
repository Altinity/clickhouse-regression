from testflows.core import *
from testflows.asserts import error

from jwt_authentication.requirements import *

from helpers.common import getuid

import jwt_authentication.tests.steps as steps


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


@TestScenario
@Name("static key")
def scenario(self, node="clickhouse1"):
    """Check jwt authentication."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_static_key)
