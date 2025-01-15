from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestCheck
def check_jwt_auth(self, algorithm):
    """Check adding jwks validator with specified algorithm
    and jwt authentication with this validator."""

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create private and public keys"):
        public_key, private_key_path = steps.generate_ssh_keys(algorithm=algorithm)

    with When("add new validator to the config.xml"):
        validator_id = define("validator id", f"jwks_with_{algorithm}")
        key_id = define("key id", f"some_key_id_{getuid()}")
        steps.add_static_jwks_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm=algorithm,
                private_key_path=private_key_path,
                key_id=key_id,
            ),
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("jwks authentication with different algorithms")
def jwks_with_different_algorithms(self):
    algorithms = [
        "RS256",
        "RS384",
        "RS512",
    ]
    for algorithm in algorithms:
        Check(f"check {algorithm} algorithm", test=check_jwt_auth)(algorithm=algorithm)


@TestFeature
@Name("static JWKS")
@Requirements(RQ_SRS_042_JWT_StaticJWKS_SupportedAlgorithms("1.0"))
def feature(self):
    """Check jwt authentication with static jwks validator with different algorithms."""
    Scenario(run=jwks_with_different_algorithms)
