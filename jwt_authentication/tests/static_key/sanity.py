from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("check simple jwt authentication with static key")
@Requirements(RQ_SRS_042_JWT_UserCreation_Config("1.0"))
def check_static_key(self):
    """Check jwt authentication with static key when static key
    validator with static_key `my_secret_1234` is in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.add_jwt_user_to_users_xml(user_name=user_name)

    with When("create jwt for user"):
        token = steps.create_static_jwt(user_name=user_name, secret="my_secret_1234")

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check that two validators can work simultaneously")
@Requirements(RQ_SRS_042_JWT_ValidatorsConfiguration("1.0"))
def check_multiple_validators(self):
    """Check authentication with two validators with different static keys.
    Validators configuration is in config.xml, one with static key `my_secret_1234`
    and another with static key `another_secret_1234`."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create first jwt for user with secret `my_secret_1234`"):
        first_token = steps.create_static_jwt(
            user_name=user_name, secret="my_secret_1234"
        )

    with And("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=first_token)

    with And("create second jwt for user with secret `another_secret_1234`"):
        second_token = steps.create_static_jwt(
            user_name=user_name, secret="another_my_secret_1234"
        )

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=second_token)

    with And("create token with another secret"):
        wrong_token = steps.create_static_jwt(
            user_name=user_name, secret="another_my_secret_12345"
        )

    with And("check that jwt authentication is failing with wrong secret"):
        steps.expect_jwt_authentication_error(token=wrong_token)


@TestScenario
@Name("check simple jwt authentication with static key rbac user")
@Requirements(RQ_SRS_042_JWT_UserCreation_RBAC("1.0"))
def check_static_key_rbac(self):
    """Check jwt authentication with static key for RBAC user when static key
    validator with static_key `my_secret_1234` is in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create jwt"):
        token = steps.create_static_jwt(user_name=user_name, secret="my_secret_1234")

    with Then("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check adding new jwt validator")
@Requirements(RQ_SRS_042_JWT_ValidatorsConfiguration("1.0"))
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

    with And("create jwt for user"):
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
        steps.expect_jwt_authentication_error(token=token)

    with And("check that previous validator still works"):
        with By("create jwt with secret from previous validator"):
            token = steps.create_static_jwt(
                user_name=user_name, secret="my_secret_1234"
            )

        with And("check that jwt authentication is successful"):
            steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check support of validator secret in base64")
@Requirements(RQ_SRS_042_JWT_StaticKey_Parameters_StaticKeyInBase64("1.0"))
def secret_in_base64(self):
    """Check adding new jwt validator with secret(static key) in base64."""
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS384")
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

    with When("create user with jwt authentication and create jwt for user"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("check authentication with expired jwt")
def expired_token(self):
    """Check that user cannot login with expired token with validator with static key
    `my_secret_1234` in config.xml."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create expired jwt"):
        secret = "my_secret_1234"
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, expiration_minutes=0
        )

    with Then("check that jwt authentication is failing"):
        steps.expect_jwt_authentication_error(token=token)

    with And("create new valid token"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, expiration_minutes=5
        )

    with And("check that jwt authentication is successful"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
def mismatch_algorithm_RSA(self):
    """Check that login fails if the RSA algorithm of token and validator do not match."""
    with Given("create public and private keys with RSA algorithm"):
        validator_id = define("validator_id", f"validator_{getuid()}")
        public_key, private_key_path = steps.generate_ssh_keys(algorithm="RS384")

    with And("add new validator with RS512 algorithm to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm="RS512",
            public_key=public_key,
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token with RS384 algorithm"):
        token = steps.create_static_jwt(
            user_name=user_name,
            algorithm="RS384",
            private_key_path=private_key_path,
        )

    with Then("check that jwt authentication is failing"):
        steps.expect_jwt_authentication_error(token=token)


@TestScenario
def mismatch_algorithm_ECDSA(self):
    """Check that login fails if the ECDSA algorithm of key and token do not match."""
    with Given("create public and private keys with ES256 algorithm"):
        validator_id = define("validator_id", f"validator_{getuid()}")
        public_key, private_key_path = steps.generate_ssh_keys(algorithm="ES256")

    with And("add new validator with ES384 algorithm to the config.xml"):
        algorithm = define("algorithm", "ES384")
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            public_key=public_key,
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token with ES384 algorithm"):
        token = steps.create_static_jwt(
            user_name=user_name,
            algorithm=algorithm,
            private_key_path=private_key_path,
        )

    with Then("check that jwt authentication is failing"):
        steps.expect_jwt_authentication_error(token=token)


@TestFeature
@Name("static key sanity")
@Requirements(
    RQ_SRS_042_JWT_UserAuthentication_ClickhouseClient("1.0"),
    RQ_SRS_042_JWT_UserAuthentication_HTTPClient("1.0"),
    RQ_SRS_042_JWT_SubClaimValidation("1.0"),
    RQ_SRS_042_JWT_StaticKey("1.0"),
)
def feature(self):
    """Sanity check for jwt authentication with static key validator."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
