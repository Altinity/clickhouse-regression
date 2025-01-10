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

    with Then("check jwt authentication with 'abc instead of correct token"):
        steps.expect_corrupted_token_error(token="abc")


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

    with When("create jwt for this user"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check that user can authenticate with correct token"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And("corrupt different parts of token and check that authentication fails"):
        for part in ["header", "payload", "signature"]:
            with By(f"corrupting {part} by changing one character"):
                corrupted_token_flip = steps.corrupt_token_part(
                    token=token, part=part, flip=True
                )
                assert corrupted_token_flip != token, error()

            with And("check that user can not authenticate with corrupted token"):
                steps.expect_corrupted_token_error(token=corrupted_token_flip)

            with By(f"corrupting {part} by swapping two characters"):
                corrupted_token_swap = steps.corrupt_token_part(
                    token=token, part=part, swap=True
                )
                assert corrupted_token_swap != token, error()

            with And("check that user can not authenticate with corrupted token"):
                steps.expect_corrupted_token_error(token=corrupted_token_swap)


@TestScenario
@Name("using other user's token parts")
def other_users_token(self):
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
        user_two = f"jwt_user_two_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_one)
        steps.create_user_with_jwt_auth(user_name=user_two)

    with When("create tokens for both users with the same secret and algorithm"):
        token_one = steps.create_static_jwt(
            user_name=user_one, secret=secret, algorithm=algorithm
        )
        token_two = steps.create_static_jwt(
            user_name=user_two, secret=secret, algorithm=algorithm
        )

    with When(
        "split these two tokens into three parts and combine them in all possible ways"
    ):
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

    with Then("check that jwt authentication succeeds only with original tokens"):
        for token in all_combinations:
            if token == token_one:
                steps.check_jwt_login(user_name=user_one, token=token)
            elif token == token_two:
                steps.check_jwt_login(user_name=user_two, token=token)
            else:
                steps.expect_corrupted_token_error(token=token)


@TestScenario
def corrupt_token_by_swap_bits(self):
    """Corrupt token by swapping every bit in header, payload and signature
    and check that authentication with corrupted token fails."""
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with And("add new validator to the config.xml"):
        validator_id = define("validator_id", "new_validator")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "another_secret")
        steps.add_static_key_validator_to_config_xml(
            validator_id=validator_id, algorithm=algorithm, secret=secret
        )

    with When("create token and split it to parts"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm="HS256",
                secret=secret,
            ),
        )
        header, payload, signature = token.split(".")

    with Then("check that user can authenticate with correct token"):
        steps.check_jwt_login(user_name=user_name, token=token)

    with And(
        "convert header to binary, swap bits and try to login with corrupted token"
    ):
        header_bin = steps.base64_to_binary(header)
        for idx in range(len(header_bin)):
            corrupted_header_bin = steps.flip_bits(header_bin, idx)
            corrupted_header = steps.binary_to_base64(corrupted_header_bin)
            corrupted_token = ".".join([corrupted_header, payload, signature])
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)

    with And(
        "convert payload to binary, swap bits and try to login with corrupted token"
    ):
        payload_bin = steps.base64_to_binary(payload)
        for idx in range(len(payload_bin)):
            corrupted_payload_bin = steps.flip_bits(payload_bin, idx)
            corrupted_payload = steps.binary_to_base64(corrupted_payload_bin)
            corrupted_token = ".".join([header, corrupted_payload, signature])
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)

    with And(
        "convert signature to binary, swap bits and try to login with corrupted token"
    ):
        signature_bin = steps.base64_to_binary(signature)
        for idx in range(len(signature_bin)):
            corrupted_signature_bin = steps.flip_bits(signature_bin, idx)
            corrupted_signature = steps.binary_to_base64(corrupted_signature_bin)
            corrupted_token = ".".join([header, payload, corrupted_signature])
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)


@TestFeature
@Name("invalid token")
def feature(self):
    """Sanity check jwt authentication with static key validator."""
    Scenario(run=jwt_authentication_with_invalid_token)
    Scenario(run=jwt_authentication_with_corrupted_token)
    Scenario(run=other_users_token)
    Scenario(run=corrupt_token_by_swap_bits)
