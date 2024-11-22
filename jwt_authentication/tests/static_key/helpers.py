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


def model(user, token, validator):
    if user.auth_type != "jwt":
        exitcode = 4
        message = f"DB::Exception:"
        return exitcode, message

    if (
        token.algorithm == validator.algorithm
        and token.user_name == user.user_name
        and validator.static_key_in_base64 == validator.config_static_key_in_base64
    ):
        if validator.static_key_in_base64 == "true":
            if steps.to_base64(token.secret) == validator.secret:
                exitcode = 0
                message = None
                return exitcode, message
        else:
            if token.secret == validator.secret:
                exitcode = 0
                message = None
                return exitcode, message

    return 4, "DB::Exception:"
