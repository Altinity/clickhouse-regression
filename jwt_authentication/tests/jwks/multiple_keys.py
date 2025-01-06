import random

from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps

random.seed(42)

algorithms = [
    "RS256",
    "RS384",
    "RS512",
]


@TestCheck
def multiple_keys(self):
    """Check adding jwks validator with multiple keys."""

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create multiple keys for jwks validator"):
        keys = []
        private_key_paths = []
        key_ids = []
        keys_algorithms = []
        for i in range(6):
            algorithm = random.choice(algorithms)
            public_key, private_key_path = steps.generate_ssh_keys(algorithm=algorithm)
            key_id = f"key_id_{i}_{getuid()}"
            key = steps.create_static_jwks_key_content(
                algorithm=algorithm,
                public_key_str=public_key,
                key_id=key_id,
            )
            keys.append(key)
            private_key_paths.append(private_key_path)
            key_ids.append(key_id)
            keys_algorithms.append(algorithm)

    with When("add new validator to the config.xml"):
        validator_id = define("validator id", f"jwks_with_RS256")
        steps.add_static_jwks_validator_to_config_xml(
            keys=keys,
            validator_id=validator_id,
        )

    with And("create token"):
        tokens = []
        for private_key_path, key_id, keys_algorithm in zip(
            private_key_paths, key_ids, keys_algorithms
        ):
            token = steps.create_static_jwt(
                user_name=user_name,
                algorithm=keys_algorithm,
                private_key_path=private_key_path,
                key_id=key_id,
                expiration_minutes=5,
            )
            tokens.append(token)

    with Then("check jwt authentication"):
        for token in tokens:
            steps.check_jwt_login(user_name=user_name, token=token)


@TestFeature
@Name("multiple keys")
def feature(self):
    """Sanity check jwt authentication with static jwks."""
    Scenario(run=multiple_keys)
