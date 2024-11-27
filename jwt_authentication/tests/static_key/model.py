from itertools import product
import datetime
import jwt
import base64

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
        algorithm,
        secret,
        static_key_in_base64,
        config_static_key_in_base64,
    ):
        self.validator_id = validator_id
        self.algorithm = algorithm
        self.secret = secret
        self.static_key_in_base64 = static_key_in_base64
        self.config_static_key_in_base64 = config_static_key_in_base64

    def add_to_config(self, restart=True):
        steps.add_static_key_validator_to_config_xml(
            validator_id=self.validator_id,
            algorithm=self.algorithm,
            secret=self.secret,
            static_key_in_base64=self.config_static_key_in_base64,
            restart=restart,
        )
        return self


class Token:
    def __init__(self, user_name, secret, algorithm, expiration_minutes=None):
        self.user_name = user_name
        self.expiration_minutes = expiration_minutes
        self.secret = secret
        self.algorithm = algorithm

    def create_token(self):
        token = steps.create_static_jwt(
            user_name=self.user_name,
            secret=self.secret,
            algorithm=self.algorithm,
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
        if (
            self.token.algorithm == self.validator.algorithm
            and self.token.user_name == self.user.user_name
            and self.validator.static_key_in_base64
            == self.validator.config_static_key_in_base64
        ):
            if self.validator.static_key_in_base64 == "true":
                if steps.to_base64(self.token.secret) == self.validator.secret:
                    return 0, ""
            else:
                if self.token.secret == self.validator.secret:
                    return 0, ""

        return 4, "DB::Exception:"

    def expect(self):
        return (
            self.expect_expired_token()
            or self.expect_wrong_auth_type()
            or self.mismatch_data_between_token_and_validator()
        )
