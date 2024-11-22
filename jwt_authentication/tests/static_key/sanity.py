from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("check simple jwt authentication with static key")
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key(self):
    """Check jwt authentication with static key when static key
    validator with static_key `my_secret` is in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.add_jwt_user_to_users_xml(user_name=user_name)

    with When("create jwt for user"):
        token = steps.create_static_jwt(user_name=user_name, secret="my_secret")

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check simple jwt authentication with static key rbac user")
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key_rbac(self):
    """Check jwt authentication with static key for RBAC user when static key
    validator with static_key `my_secret` is in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create jwt"):
        token = steps.create_static_jwt(user_name=user_name, secret="my_secret")

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check adding new jwt validator")
def add_new_validator(self):
    """Check adding new static key jwt validator to the config.xml."""

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

    with And("create jwt"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("create token with mismatched secret"):
        token = steps.create_static_jwt(
            user_name=user_name, secret="wrong_secret", algorithm=algorithm
        )

    with And("check that jwt authentication is failing"):
        message = (
            f"DB::Exception: {user_name}: Authentication failed: password is "
            "incorrect, or there is no user with such name."
        )
        steps.check_jwt_login(
            user_name=user_name,
            token=token,
            exitcode=4,
            message=message,
        )


@TestScenario
@Name("check support of validator secret in base64")
def secret_in_base64(self):
    """Check adding new jwt validator with secret(static key) in base64."""

    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "some_secret")

    with And("convert secret to base64"):
        base64_secret = define("secret in base64", steps.to_base64(secret))

    with And("add new validator with base64_secret to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            secret=base64_secret,
            static_key_in_base64="true",
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


@TestScenario
@Name("check authentication with expired jwt")
def expired_token(self):
    """Check that user cannot login with expired token with validator with static key
    `my_secret` in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create expired jwt"):
        token = steps.create_static_jwt(
            user_name=user_name, secret="my_secret", expiration_minutes=0
        )

    with Then("check that jwt authentication is failing"):
        message = (
            f"DB::Exception: {user_name}: Authentication failed: password is "
            "incorrect, or there is no user with such name."
        )
        steps.check_jwt_login(
            user_name=user_name, token=token, exitcode=4, message=message
        )

    with And("create new valid token"):
        token = steps.create_static_jwt(
            user_name=user_name, secret="my_secret", expiration_minutes=5
        )

    with And("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestFeature
@Name("static key sanity")
def feature(self):
    """Sanity check jwt authentication with static key validator."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
