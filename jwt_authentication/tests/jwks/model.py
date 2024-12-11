from testflows.core import *

import jwt_authentication.tests.steps as steps


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
        keys,
    ):
        self.validator_id = validator_id
        self.keys = keys

    def add_to_config(self, node=None):
        list_of_keys = [key.key for key in self.keys]
        steps.add_static_jwks_validator_to_config_xml(
            keys=list_of_keys,
            validator_id=self.validator_id,
            node=node,
        )
        return self


class Key:
    def __init__(self, algorithm, ssh_key, key_id, key_type="RSA"):
        self.algorithm = algorithm
        self.ssh_key = ssh_key
        self.key_id = key_id
        self.key_type = key_type
        self.key = None

    def create_key_content(self):
        key = steps.create_static_jwks_key_content(
            algorithm=self.algorithm,
            public_key_str=self.ssh_key.public_key_str if self.ssh_key else None,
            key_id=self.key_id,
            key_type=self.key_type,
        )
        self.key = key
        return self


class SSH_key:
    def __init__(self):
        self.private_key_path = None
        self.public_key_str = None

    def generate_keys(self):
        self.public_key_str, self.private_key_path = steps.generate_ssh_keys()
        return self


class Token:
    def __init__(self, user_name, ssh_key, algorithm, key_id, expiration_minutes=None):
        self.user_name = user_name
        self.expiration_minutes = expiration_minutes
        self.ssh_key = ssh_key
        self.algorithm = algorithm
        self.key_id = key_id

    def create_token(self):
        token = steps.create_static_jwt(
            user_name=self.user_name,
            algorithm=self.algorithm,
            private_key_path=self.ssh_key.private_key_path if self.ssh_key else None,
            key_id=self.key_id,
            expiration_minutes=self.expiration_minutes,
        )
        self.jwt_token = token
        return self


class Model:
    """Behavior model of jwt authentication with static jwks validator."""

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

    def mismatch_data_between_token_and_validator(self):
        """Search for perfect match between token and one of the keys in the validator."""
        for key in self.validator.keys:
            if key.ssh_key is None:
                continue
            if (
                self.token.key_id == key.key_id
                and self.token.algorithm == key.algorithm
                and self.token.user_name == self.user.user_name
                and key.ssh_key.private_key_path == self.token.ssh_key.private_key_path
                and key.ssh_key.public_key_str == self.token.ssh_key.public_key_str
            ):
                return partial(
                    steps.expect_successful_login, user_name=self.user.user_name
                )

        return steps.expect_authentication_error

    def expect(self):
        """Main method to check for all conditions."""
        return (
            self.expect_expired_token()
            or self.expect_wrong_auth_type()
            or self.mismatch_data_between_token_and_validator()
        )
