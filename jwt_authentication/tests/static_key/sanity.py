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


@TestScenario
@Name("check simple jwt authentication with static key rbac user")
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key_rbac(self):
    """Check jwt authentication with static key for RBAC user."""

    user_name = f"jwt_user_{getuid()}"

    with Given("create user with jwt authentication"):
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create jwt token"):
        token = steps.create_static_jwt(user_name=user_name)

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check adding new jwt validator")
def add_new_validator(self):
    """Check adding new jwt validator."""

    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "some_secret")

    with And("add new validator to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id, algorithm=algorithm, secret=secret
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("create wrong token"):
        token = steps.create_static_jwt(
            user_name=user_name, secret="wrong_secret", algorithm=algorithm
        )

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


@TestFeature
@Name("static key sanity")
def feature(self):
    """Sanity check jwt authentication with static key validator."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
