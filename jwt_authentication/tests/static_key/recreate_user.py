from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("jwt authentication after recreating user in config file")
def check_recreate_user_config(self):
    """Check jwt authentication after recreate user with jwt authentication
    in configuration file."""

    user_name = f"jwt_user_{getuid()}"

    with Given("create user with jwt authentication and a token for this user"):
        steps.add_jwt_user_to_users_xml(user_name=user_name)
        token = steps.create_static_jwt(user_name=user_name)

    with And("check that user can authenticate with jwt"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("drop user"):
        steps.remove_jwt_user_from_users_xml(user_name=user_name)

    with And("check that authentication is failing"):
        steps.check_jwt_login(
            user_name=user_name,
            token=token,
            exitcode=4,
            message=(
                f"DB::Exception: {user_name}: Authentication failed: password is "
                "incorrect, or there is no user with such name."
            ),
        )

    with And("assert that user is deleted and only default user is present"):
        res = self.context.node.query("SHOW USERS")
        assert res.output == "default", error()

    with Then("recreate user with jwt authentication with the same name"):
        steps.add_jwt_user_to_users_xml(user_name=user_name)

    with And("check that user can authenticate with jwt"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("jwt authentication after recreating user using rbac")
def check_recreate_user_rbac(self):
    """Check jwt authentication after recreate user with jwt authentication using RBAC."""
    user_name = f"jwt_user_{getuid()}"

    with Given("create user with jwt authentication and token for this user"):
        steps.create_user_with_jwt_auth(user_name=user_name)
        token = steps.create_static_jwt(user_name=user_name)

    with And("check that user can authenticate with jwt"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("drop user"):
        self.context.node.query(f"DROP USER {user_name}")

    with And("check that authentication is failing"):
        steps.check_jwt_login(
            user_name=user_name,
            token=token,
            exitcode=4,
            message=(
                f"DB::Exception: {user_name}: Authentication failed: password is "
                "incorrect, or there is no user with such name."
            ),
        )

    with Then("recreate user with jwt authentication with the same name"):
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("check that user can authenticate with jwt"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestFeature
@Name("static key sanity")
def feature(self):
    """Sanity check jwt authentication with static key validator."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
