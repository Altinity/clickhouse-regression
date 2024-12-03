from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps

from cryptography.hazmat.primitives import serialization


@TestScenario
@Name("login fails with mismatched algorithm")
def test_login_fails_with_mismatched_algorithm(self):
    """Check that login fails when jwt algorithm does not match the one
    specified in config.xml."""

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create private and public keys with RS512"):
        public_key, private_key_file = steps.generate_ssh_keys(algorithm="RS512")

    with When("add new validator with RS512 algorithm to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        steps.add_static_jwks_validator_to_config_xml(
            validator_id="jwks_with_RS512_algorithm",
            algorithm="RS512",
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token using RS256 algorithm"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm="RS384",
                private_key_path=private_key_file,
                key_id=key_id,
            ),
        )

    with Then("check jwt authentication"):
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
def feature(self):
    """Sanity check jwt authentication with static jwks."""
    Scenario(run=test_login_fails_with_mismatched_algorithm)
