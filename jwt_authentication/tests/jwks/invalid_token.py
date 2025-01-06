from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
def jwt_authentication_with_invalid_token(self):
    """Check that jwt authentication with invalid token fails."""
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with Then("check jwt authentication with None instead of correct token"):
        steps.expect_corrupted_token_error(
            token=None,
        )


@TestScenario
def invalid_parts_in_token(self):
    """Corrupt that jwt authentication with invalid token parts fails."""
    random_symbols_instead_of_token_part = [
        "_",
        "a",
        ".",
        "1",
        ":",
        "...",
        "?",
        " ",
        ")",
    ]
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("add new validator to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        public_key, private_key_file = steps.generate_ssh_keys()
        steps.add_static_jwks_validator_to_config_xml(
            validator_id="jwks_with_RS512_algorithm",
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token and split it to parts"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm="RS256",
                private_key_path=private_key_file,
                key_id=key_id,
            ),
        )
        header, payload, signature = token.split(".")

    with Then("create token with corrupted header and check that authentication fails"):
        for symbol in random_symbols_instead_of_token_part:
            corrupted_token = f"{symbol}.{payload}.{signature}"
            steps.expect_corrupted_token_error(
                token=corrupted_token,
            )

    with And("create token with corrupted payload and check that authentication fails"):
        for symbol in random_symbols_instead_of_token_part:
            corrupted_token = f"{header}.{symbol}.{signature}"
            steps.expect_corrupted_token_error(
                token=corrupted_token,
            )

    with And(
        "create token with corrupted signature and check that authentication fails"
    ):
        for symbol in random_symbols_instead_of_token_part:
            corrupted_token = f"{header}.{payload}.{symbol}"
            steps.expect_corrupted_token_error(
                token=corrupted_token,
            )


@TestFeature
@Name("invalid token")
def feature(self):
    """Check that authentication with invalid token fails."""
    Scenario(run=jwt_authentication_with_invalid_token)
    Scenario(run=invalid_parts_in_token)
