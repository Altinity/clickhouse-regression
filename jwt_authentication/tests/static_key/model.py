from functools import partial

import jwt_authentication.tests.steps as steps

SYMMETRIC_ALGORITHMS = ["HS256", "HS384", "HS512"]
ASYMMETRIC_ALGORITHMS = [
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


class User:
    def __init__(self, user_name, auth_type="jwt"):
        self.user_name = user_name
        self.auth_type = auth_type

    def create_user(self, node=None):
        if self.auth_type == "jwt":
            steps.create_user_with_jwt_auth(user_name=self.user_name, node=node)
        return self


class Validator:
    def __init__(
        self,
        validator_id,
        algorithm,
        secret=None,
        static_key_in_base64=None,
        config_static_key_in_base64=None,
        key=None,
    ):
        self.validator_id = validator_id
        self.algorithm = algorithm
        self.secret = secret
        self.static_key_in_base64 = static_key_in_base64
        self.config_static_key_in_base64 = config_static_key_in_base64
        self.key = key

    def add_to_config(self, restart=True, node=None):
        steps.add_static_key_validator_to_config_xml(
            validator_id=self.validator_id,
            algorithm=self.algorithm,
            secret=self.secret,
            static_key_in_base64=self.config_static_key_in_base64,
            public_key=self.key.public_key if self.key else None,
            restart=restart,
            node=node,
        )
        return self


class Token:
    def __init__(
        self,
        user_name,
        algorithm,
        secret=None,
        expiration_minutes=None,
        key=None,
        corrupted_token=None,
    ):
        self.user_name = user_name
        self.expiration_minutes = expiration_minutes
        self.secret = secret
        self.algorithm = algorithm
        self.key = key
        self.corrupted_token = corrupted_token

    def create_token(self):
        token = steps.create_static_jwt(
            user_name=self.user_name,
            secret=self.secret,
            algorithm=self.algorithm,
            expiration_minutes=self.expiration_minutes,
            private_key_path=self.key.private_key_path if self.key else None,
        )
        self.jwt_token = token
        return self


class Key:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.private_key_path = None
        self.public_key = None

    def generate_keys(self):
        self.public_key, self.private_key_path = steps.generate_ssh_keys(
            algorithm=self.algorithm
        )
        return self


class Model:
    """Behavior model of jwt authentication with static key validator."""

    def __init__(self, user, token, validator):
        self.user = user
        self.token = token
        self.validator = validator

    def expect_wrong_auth_type(self, expected_auth_type="jwt"):
        """Check for wrong authentication types."""
        if self.user.auth_type != expected_auth_type:
            return steps.expect_authentication_error

    def expect_expired_token(self):
        """Check for expired tokens."""
        if self.token.expiration_minutes is not None:
            if self.token.expiration_minutes < 0:
                return steps.expect_authentication_error

    def expect_mismatch_token_validator_algorithm(self):
        """Check for mismatched token algorithms."""
        if self.token.algorithm != self.validator.algorithm:
            return steps.expect_authentication_error

    def expect_mismatch_user_name(self):
        """Check for mismatched user names."""
        if self.token.user_name != self.user.user_name:
            return steps.expect_authentication_error

    def expect_mismatch_base64_settings(self):
        """Check for mismatched base64 settings if the algorithm is symmetric."""
        if (
            self.validator.static_key_in_base64
            != self.validator.config_static_key_in_base64
        ) and self.validator.algorithm in SYMMETRIC_ALGORITHMS:
            return steps.expect_authentication_error

    def expect_mismatch_secret(self):
        """Check for mismatched secrets if the algorithm is symmetric."""
        if self.validator.algorithm in SYMMETRIC_ALGORITHMS:
            token_secret = (
                steps.to_base64(self.token.secret)
                if self.validator.static_key_in_base64 == "true"
                else self.token.secret
            )
            if token_secret != self.validator.secret:
                return steps.expect_authentication_error

    def expect_wrong_key_pair(self):
        """Check for mismatched key pairs if the algorithm is asymmetric."""
        if self.validator.algorithm in ASYMMETRIC_ALGORITHMS:
            if self.validator.key.public_key != steps.get_public_key_from_private(
                self.token.key.private_key_path
            ):
                return steps.expect_authentication_error

    def expect_mismatch_key_validator_algorithm(self):
        """Check for mismatched key and validator algorithms if the algorithm
        is asymmetric. We don't care about key if algorithm is symmetric."""
        if self.validator.algorithm in ASYMMETRIC_ALGORITHMS:
            if not self.validator.algorithm.startswith("RS"):
                if self.validator.key.algorithm != self.validator.algorithm:
                    return steps.expect_authentication_error

            if self.validator.algorithm.startswith("RS"):
                if not self.validator.key.algorithm.startswith("RS"):
                    return steps.expect_authentication_error

    def expect_successful_login(self):
        """Check that if all conditions are met, the login is successful."""
        return partial(steps.expect_successful_login, user_name=self.user.user_name)

    def expect(self, node=None):
        """Main method to check for all conditions."""
        return (
            self.expect_expired_token()
            or self.expect_wrong_auth_type()
            or self.expect_mismatch_token_validator_algorithm()
            or self.expect_mismatch_user_name()
            or self.expect_mismatch_base64_settings()
            or self.expect_mismatch_secret()
            or self.expect_mismatch_key_validator_algorithm()
            or self.expect_wrong_key_pair()
            or self.expect_successful_login()
        )
