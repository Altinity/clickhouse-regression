from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestCheck
def mismatch_algorithm(self):
    """Check adding new jwt validator with asymmetric algorithms."""
    with Given("create public and private keys with RS256 algorithm"):
        validator_id = define("validator_id", f"validator_{getuid()}")
        public_key, private_key_path = steps.generate_ssh_keys(algorithm="RS256")

    with And("define RS512 algorithm for validator and token creation"):
        algorithm = define("algorithm", "RS512")

    with And("add new validator with RS512 algorithm to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            public_key=public_key,
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token with RS512 algorithm"):
        token = steps.create_static_jwt(
            user_name=user_name,
            algorithm=algorithm,
            private_key_path=private_key_path,
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestFeature
def feature(self):
    """Check static key jwt authentication with different algorithms."""
    Scenario(run=mismatch_algorithm)
