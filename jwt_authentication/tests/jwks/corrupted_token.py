import random

from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
def corrupt_token_by_swap_symbols(self):
    """Corrupt token by swapping symbols in header, payload and signature
    and check that authentication with corrupted token fails."""
    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("add new validator to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        public_key, private_key_file = steps.generate_ssh_keys()
        steps.add_static_jwks_validator_to_config_xml(
            validator_id="some_jwks_validator",
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm="RS256",
                private_key_path=private_key_file,
                key_id=key_id,
            ),
        )

    with Then(
        "corrupt every single symbol in header and try to login with corrupted token"
    ):
        header_length = len(token.split(".")[0])
        for idx in range(header_length):
            corrupted_token = steps.corrupt_token_part(
                token=token, part="header", flip=True, flip_idx=idx
            )
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)

    with And(
        "corrupt every single symbol in payload and try to login with corrupted token"
    ):
        payload_length = len(token.split(".")[1])
        for idx in range(payload_length):
            corrupted_token = steps.corrupt_token_part(
                token=token, part="payload", flip=True, flip_idx=idx
            )
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)

    with And(
        "corrupt every single symbol in signature and try to login with corrupted token"
    ):
        signature_length = len(token.split(".")[2])
        for idx in range(signature_length)[:-1]:
            corrupted_token = steps.corrupt_token_part(
                token=token, part="signature", flip=True, flip_idx=idx
            )
            note(public_key)
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)


@TestScenario
def corrupt_token_by_swap_bits(self):
    """Corrupt token by swapping every bit in header, payload and signature
    and check that authentication with corrupted token fails."""
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

    with Then(
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


@TestScenario
def corrupt_token_by_swap_random_bits(self):
    """Corrupt token by swapping random multiple bits in header, payload and signature
    and check that authentication with corrupted token fails."""
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

    with Then(
        "convert all parts to binary, swap random bits and try to login with corrupted token"
    ):
        header_bin = steps.base64_to_binary(header)
        payload_bin = steps.base64_to_binary(payload)
        signature_bin = steps.base64_to_binary(signature)
        for _ in range(100):
            corruptions_in_header = random.randint(0, 6)
            corruptions_in_payload = random.randint(0, 6)
            corruptions_in_signature = random.randint(0, 6)
            corrupted_header_bin = steps.flip_bits(header_bin, corruptions_in_header)
            corrupted_payload_bin = steps.flip_bits(payload_bin, corruptions_in_payload)
            corrupted_signature_bin = steps.flip_bits(
                signature_bin, corruptions_in_signature
            )
            corrupted_header = steps.binary_to_base64(corrupted_header_bin)
            corrupted_payload = steps.binary_to_base64(corrupted_payload_bin)
            corrupted_signature = steps.binary_to_base64(corrupted_signature_bin)
            corrupted_token = ".".join(
                [corrupted_header, corrupted_payload, corrupted_signature]
            )
            note(f"Corrupted token: {corrupted_token}")
            note(f"Original token: {token}")
            steps.expect_corrupted_token_error(token=corrupted_token)


@TestFeature
@Name("static jwks with corrupted token")
def feature(self):
    """Check jwt authentication with dynamic jwks validator and corrupted token."""
    Scenario(run=corrupt_token_by_swap_symbols)
    Scenario(run=corrupt_token_by_swap_bits)
    Scenario(run=corrupt_token_by_swap_random_bits)
