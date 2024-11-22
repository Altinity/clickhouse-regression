import random

from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid

import jwt_authentication.tests.steps as steps
import jwt_authentication.tests.static_key.helpers as helpers

random.seed(42)


@TestStep(Given)
def create_users(self, user_names):
    """Create users with jwt authentication."""
    users = []
    for user_name in user_names:
        user = helpers.User(user_name=user_name, auth_type="jwt")
        user.create_user()
        users.append(user)

    return users


@TestStep(Given)
def create_tokens(
    self, user_names, token_algorithms, token_secrets, expiration_minutes
):
    """Create tokens for users."""
    tokens = []
    for user_name, token_algorithm, token_secret, expiration in product(
        user_names, token_algorithms, token_secrets, expiration_minutes
    ):
        token = helpers.Token(
            user_name=user_name,
            secret=token_secret,
            algorithm=token_algorithm,
            expiration_minutes=expiration,
        )
        token.create_token()
        tokens.append(token)

    return tokens


@TestStep(Given)
def create_validators(
    self,
    validator_algorithms,
    validator_secrets,
    config_static_key_in_base64_values,
    static_key_in_base64_values,
):
    """Create validators."""
    validators = []
    for algorithm, secret, static_key_in_base64, config_static_key_in_base64 in product(
        validator_algorithms,
        validator_secrets,
        static_key_in_base64_values,
        config_static_key_in_base64_values,
    ):
        if static_key_in_base64 == "true":
            secret = steps.to_base64(secret)

        validator_id = f"validator_{getuid()}"
        validator = helpers.Validator(
            validator_id=validator_id,
            algorithm=algorithm,
            secret=secret,
            config_static_key_in_base64=config_static_key_in_base64,
            static_key_in_base64=static_key_in_base64,
        )
        validators.append(validator)

    return validators


@TestCheck
@Name("check jwt authentication for given combination")
def check_jwt_authentication(self, user_name, token, validator):
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
        note(f"validator algorithm: {validator.algorithm}")
        note(f"token secret: {token.secret}")
        note(f"validator secret: {validator.secret}")
        note(f"validator static_key_in_base64: {validator.static_key_in_base64}")
        note(
            f"validator config_static_key_in_base64: {validator.config_static_key_in_base64}"
        )
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
def jwt_authentication_combinatorics(self):
    """Check jwt authentication with static key validator."""
    user_names = [f"user1_{getuid()}", f"user2_{getuid()}"]
    token_algorithms = [
        "HS256",
        "HS384",
        "HS512",
        # "RS256",
        # "RS384",
        # "RS512",
        # "ES256",
        # "ES384",
        # "ES512",
        # "ES256K",
        # "PS256",
        # "PS384",
        # "PS512",
        # "Ed25519",
        # "Ed448",
    ]
    validator_algorithms = [
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        # "RS512",
        # "ES256",
        # "ES384",
        # "ES512",
        # "ES256K",
        # "PS256",
        # "PS384",
        # "PS512",
        # "Ed25519",
        # "Ed448",
    ]
    token_secrets = ["secret_1", "secret_2"]
    validator_secrets = ["secret_1", "secret_2"]
    config_static_key_in_base64_values = ["true", "false"]
    static_key_in_base64_values = ["true", "false"]
    expiration_minutes = [5, -5, None]
    
    # with Given("create users with jwt authentication"):
    #     users = create_users(user_names=user_names)

    with Given("create tokens for users"):
        tokens = create_tokens(
            user_names=user_names,
            token_algorithms=token_algorithms,
            token_secrets=token_secrets,
            expiration_minutes=expiration_minutes,
        )

    with And("create validators"):
        validators = create_validators(
            validator_algorithms=validator_algorithms,
            validator_secrets=validator_secrets,
            config_static_key_in_base64_values=config_static_key_in_base64_values,
            static_key_in_base64_values=static_key_in_base64_values,
        )

    combinations = list(product(user_names, tokens, validators))

    if not self.context.stress:
        combinations = random.sample(combinations, 30)

    for num, combination in enumerate(combinations):
        user_name, token, validator = combination
        Check(name=f"combination {num}", test=check_jwt_authentication)(
            user_name=user_name,
            token=token,
            validator=validator,
        )
