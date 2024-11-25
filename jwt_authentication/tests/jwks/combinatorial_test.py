import random

from testflows.core import *
from testflows.combinatorics import product, combinations

from helpers.common import getuid

import jwt_authentication.tests.steps as steps
import jwt_authentication.tests.jwks.helpers as helpers

random.seed(42)


@TestStep(Given)
def create_tokens(
    self, user_names, token_algorithms, private_key_paths, key_ids, expiration_minutes
):
    """Create tokens for users."""
    tokens = []
    for user_name, token_algorithm, private_key_path, key_id, expiration in product(
        user_names, token_algorithms, private_key_paths, key_ids, expiration_minutes
    ):
        token = helpers.Token(
            user_name=user_name,
            private_key=private_key_path,
            algorithm=token_algorithm,
            key_id=key_id,
            expiration_minutes=expiration,
        )
        token.create_token()
        tokens.append(token)
    
    return tokens


@TestStep(Given)
def create_jwks_validators(
    self,
    validator_key_algorithms,
    validator_public_keys,
):
    """Create multiple validators with combinations of single keys and pairs of keys."""
    validators = []
    keys = []
    key_ids = []

    for algorithm, public_key in product(
        validator_key_algorithms, validator_public_keys
    ):
        key_id = f"key_id_{getuid()}"
        key_ids.append(key_id)
        key = steps.create_static_jwks_key_content(
            algorithm=algorithm,
            public_key_str=public_key,
            key_id=key_id,
        )
        keys.append(key)

    # Create validators with single keys
    for key in keys:
        validator_id = f"validator_{getuid()}"
        validator = helpers.Validator(
            validator_id=validator_id,
            keys=[key],
        )
        validators.append(validator)

    # Create validators with pairs of keys
    for key_pair in combinations(keys, 2):
        validator_id = f"validator_{getuid()}"
        validator = helpers.Validator(
            validator_id=validator_id,
            keys=list(key_pair),
        )
        validators.append(validator)

    return validators, key_ids


@TestCheck
def check_jwks_authentication(self, user_name, token, validator):
    """Check jwt authentication for given combination."""

    with Given("add validator to the config.xml"):
        validator.add_to_config()

    with And("create user with jwt authentication"):
        user = helpers.User(user_name=user_name, auth_type="jwt")
        user.create_user()

    with When("get expected exitcode and message from the model"):
        exitcode, message = helpers.model(user=user, token=token, validator=validator)

    with And("add debug notes"):
        note(f"token algorithm: {token.algorithm}")
        note(f"token user_name: {token.user_name}")
        note(f"user user_name: {user.user_name}")
        note(f"expiration_minutes: {token.expiration_minutes}")

    with Then("check jwt authentication"):
        steps.check_clickhouse_client_jwt_login(
            user_name=user.user_name,
            token=token.jwt_token,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def feature(self):
    """Check jwt authentication with static key validator."""
    user_names = [f"user1_{getuid()}", f"user2_{getuid()}"]
    token_algorithms = [
        "RS256",
        "RS384",
        "RS512",
    ]
    validator_key_algorithms = [
        "RS256",
        "RS384",
        "RS512",
    ]
    expiration_minutes = [5, -5, None]

    public_keys, private_key_paths = [], []

    with By("create keys"):
        public_key, private_key_path = steps.generate_ssh_keys(algorithm="RS256")

    public_keys.append(public_key)
    private_key_paths.append(private_key_path)

    with And("create validators"):
        validators, key_ids = create_jwks_validators(
            validator_key_algorithms=validator_key_algorithms,
            validator_public_keys=public_keys,
        )

    with Given("create tokens for users"):
        tokens = create_tokens(
            user_names=user_names,
            token_algorithms=token_algorithms,
            private_key_paths=private_key_paths,
            key_ids=key_ids,
            expiration_minutes=expiration_minutes,
        )

    combinations = list(product(user_names, tokens, validators))

    if not self.context.stress:
        combinations = random.sample(combinations, 30)

    for num, combination in enumerate(combinations):
        user_name, token, validator = combination
        Check(name=f"combination {num}", test=check_jwks_authentication)(
            user_name=user_name,
            token=token,
            validator=validator,
        )
