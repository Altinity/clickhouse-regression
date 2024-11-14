from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("login with invalid token")
def jwt_authentication_with_invalid_token(self):
    """Check that authentication with invalid token fails."""
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with Then("check jwt authentication with None instead of correct token"):
        steps.check_jwt_login(
            user_name=user_name,
            token=None,
            exitcode=131,
            message=(f"DB::Exception: Failed to validate jwt."),
        )


@TestFeature
@Name("invalid token")
def feature(self):
    """Sanity check jwt authentication with static key validator."""

    Scenario(run=jwt_authentication_with_invalid_token)
