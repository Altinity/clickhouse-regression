from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("login with invalid token")
def jwt_authentication_with_invalid_token(self):
    """Check that authentication with invalid token fails."""
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with Then("check jwt authentication with None instead of correct token"):
        steps.check_jwt_login(
            user_name=user_name,
            token=None,
            exitcode=131,
            message=(f"DB::Exception: Failed to validate jwt."),
        )


@TestScenario
@Name("corrupted token")
def jwt_authentication_with_corrupted_token(self):
    """Check that authentication with corrupted token fails."""
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "some_simple_secret")

    with And("add new validator to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id, algorithm=algorithm, secret=secret
        )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("create token"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check that user can authenticate with correct token"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("corrupt different parts of token and check that authentication fails"):
        for part in ["header", "payload", "signature"]:
            with By(f"corrupting {part} by changing one character"):
                corrupted_token_flip = steps.corrupt_token(
                    token=token, part=part, flip=True
                )
                assert corrupted_token_flip != token, error()

            with And("check that user can not authenticate with corrupted token"):
                steps.check_jwt_login_with_corrupted_token(token=corrupted_token_flip)

            with By(f"corrupting {part} by swapping two characters"):
                corrupted_token_swap = steps.corrupt_token(
                    token=token, part=part, swap=True
                )
                assert corrupted_token_swap != token, error()

            with And("check that user can not authenticate with corrupted token"):
                steps.check_jwt_login_with_corrupted_token(token=corrupted_token_swap)


@TestScenario
@Name("using other user's token parts")
def other_user_token(self):
    """Check that user can not use other user's token parts to authenticate."""
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "another_secret")

    with And("add new validator to the config.xml"):
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id, algorithm=algorithm, secret=secret
        )

    with When("create two users with jwt authentication"):
        user_one = f"jwt_user_one_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_one)
        user_two = f"jwt_user_two_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_two)

    with When("create tokens for both users"):
        token_one = steps.create_static_jwt(
            user_name=user_one, secret=secret, algorithm=algorithm
        )
        token_two = steps.create_static_jwt(
            user_name=user_two, secret=secret, algorithm=algorithm
        )

    with When("create all possible combinations of tokens"):
        token_one_header, token_one_payload, token_one_signature = token_one.split(".")
        token_two_header, token_two_payload, token_two_signature = token_two.split(".")

        all_combinations = define(
            "all combinations",
            [
                ".".join(parts)
                for parts in product(
                    [token_one_header, token_two_header],
                    [token_one_payload, token_two_payload],
                    [token_one_signature, token_two_signature],
                )
            ],
        )

    with Then("check jwt authentication with all possible combinations of tokens"):
        for token in all_combinations:
            if token == token_one:
                steps.check_jwt_login(user_name=user_one, token=token)
            elif token == token_two:
                steps.check_jwt_login(user_name=user_two, token=token)
            else:
                steps.check_jwt_login_with_corrupted_token(token=token)


@TestFeature
@Name("invalid token")
def feature(self):
    """Sanity check jwt authentication with static key validator."""

    Scenario(run=jwt_authentication_with_invalid_token)
    Scenario(run=jwt_authentication_with_corrupted_token)
    Scenario(run=other_user_token)