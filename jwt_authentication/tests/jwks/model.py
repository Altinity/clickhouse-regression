from testflows.core import *

import jwt_authentication.tests.steps as steps


class User:
    def __init__(self, user_name, auth_type="jwt"):
        self.user_name = user_name
        self.auth_type = auth_type

    def create_user(self):
        if self.auth_type == "jwt":
            steps.create_user_with_jwt_auth(user_name=self.user_name)
        return self


class Validator:
    def __init__(
        self,
        validator_id,
        keys,
    ):
        self.validator_id = validator_id
        self.keys = keys

    def add_to_config(self, restart=True):
        steps.add_static_jwks_validator_to_config_xml(
            keys=self.keys,
            validator_id=self.validator_id,
        )
        return self


class Token:
    def __init__(
        self, user_name, private_key, algorithm, key_id, expiration_minutes=None
    ):
        self.user_name = user_name
        self.expiration_minutes = expiration_minutes
        self.private_key = private_key
        self.algorithm = algorithm
        self.key_id = key_id

    def create_token(self):
        token = steps.create_static_jwt(
            user_name=self.user_name,
            algorithm=self.algorithm,
            private_key_path=self.private_key,
            key_id=self.key_id,
            expiration_minutes=self.expiration_minutes,
        )
        self.jwt_token = token
        return self


class Model:
    def __init__(self, user, token, validator):
        self.user = user
        self.token = token
        self.validator = validator

    def expect_wrong_auth_type(self, expected_auth_type="jwt"):
        if self.user.auth_type != expected_auth_type:
            return 4, "DB::Exception:"

    def expect_expired_token(self):
        if self.token.expiration_minutes is not None:
            if self.token.expiration_minutes < 0:
                return 4, "DB::Exception:"

    def mismatch_data_between_token_and_validator(self):
        for key in self.validator.keys:
            if (
                self.token.key_id == key["kid"]
                and self.token.algorithm == key["alg"]
                and self.token.user_name == self.user.user_name
            ):
                return 0, ""

        return 4, "DB::Exception:"

    def expect(self):
        return (
            self.expect_expired_token()
            or self.expect_wrong_auth_type()
            or self.mismatch_data_between_token_and_validator()
        )
