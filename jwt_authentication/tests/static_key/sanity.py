from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("check simple jwt authentication with static key")
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key(self):
    """Check jwt authentication with static key."""

    user_name = f"jwt_user_{getuid()}"

    with Given("create user with jwt authentication"):
        steps.add_jwt_user_to_users_xml(user_name=user_name)

    with When("create jwt token"):
        token = steps.create_static_jwt(user_name=user_name)

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestFeature
@Name("static key sanity")
def feature(self):
    """Sanity check jwt authentication with static key validator."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
