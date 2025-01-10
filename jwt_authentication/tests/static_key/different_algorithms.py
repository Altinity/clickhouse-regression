from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestCheck
def check_validator_with_asymmetric_algorithms(self, algorithm):
    """Check adding new jwt validator with asymmetric algorithms."""
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", f"validator_{algorithm}")
        algorithm = define("algorithm", algorithm)
        public_key, private_key_path = steps.generate_ssh_keys(algorithm=algorithm)

    with And("add new validator to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            public_key=public_key,
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token"):
        token = steps.create_static_jwt(
            user_name=user_name,
            algorithm=algorithm,
            private_key_path=private_key_path,
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("adding validator asymmetric algorithm")
@Requirements(RQ_SRS_042_JWT_StaticKey)
def check_static_key_asymmetric_algorithms(self):
    """Check static key jwt authentication with different algorithms:
    | RSA   | ECDSA  | PSS   | EdDSA   |
    | ----- | ------ | ----- | ------- |
    | RS256 | ES256  | PS256 | Ed25519 |
    | RS384 | ES384  | PS384 | Ed448   |
    | RS512 | ES512  | PS512 |         |
    |       | ES256K |       |         |
    """

    algorithms = [
        "RS256",
        "RS384",
        "RS512",
        "ES256",
        "ES384",
        "ES512",
        "ES256K",
        "PS256",
        "PS384",
        "PS512",
        "Ed25519",
        "Ed448",
    ]

    for algorithm in algorithms:
        Check(
            f"check {algorithm} algorithm",
            test=check_validator_with_asymmetric_algorithms,
        )(algorithm=algorithm)


@TestCheck
def check_validator_with_symmetric_algorithms(self, algorithm):
    """Check adding new jwt validator with symmetric algorithms."""
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", f"validator_{algorithm}")
        algorithm = define("algorithm", algorithm)
        secret = f"secret_{algorithm}"

    with And("add new validator to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id,
            algorithm=algorithm,
            secret=secret,
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("create token"):
        token = steps.create_static_jwt(
            user_name=user_name,
            algorithm=algorithm,
            secret=secret,
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(user_name=user_name, token=token)


@TestScenario
@Name("adding validator symmetric algorithm")
def check_static_key_symmetric_algorithms(self):
    """Check static key jwt authentication with symmetric algorithms:
    HS256, HS384, HS512."""
    algorithms = [
        "HS256",
        "HS384",
        "HS512",
    ]

    for algorithm in algorithms:
        Check(
            f"check {algorithm} algorithm",
            test=check_validator_with_symmetric_algorithms,
        )(algorithm=algorithm)


@TestFeature
@Name("different algorithms")
@Requirements(RQ_SRS_042_JWT_StaticKey_SupportedAlgorithms("1.0"))
def feature(self):
    """Check static key jwt authentication with different algorithms."""
    Scenario(run=check_static_key_symmetric_algorithms)
    Scenario(run=check_static_key_asymmetric_algorithms)
