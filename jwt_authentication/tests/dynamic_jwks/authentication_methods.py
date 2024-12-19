from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
def change_authentication_method(self):
    """Check that jwt authentication fails when user's authentication method is changed
    from jwt to password."""

    node = self.context.node

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("add new validator with RS384 algorithm to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        algorithm = "RS384"
        public_key, private_key_file = steps.generate_ssh_keys()
        steps.add_dynamic_jwks_validator_to_config_xml(
            validator_id="jwks_with_RS384_algorithm",
            algorithm=algorithm,
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token using RS384 algorithm"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm=algorithm,
                private_key_path=private_key_file,
                key_id=key_id,
            ),
        )

    with Then("check jwt authentication"):
        steps.check_jwt_login(
            user_name=user_name,
            token=token,
        )

    with And("change user's authentication method to password"):
        password = "some_password"
        node.query(f"ALTER USER {user_name} IDENTIFIED BY '{password}'")
        node.query(f"SHOW CREATE USER {user_name}")

    with Then("check that jwt authentication fails"):
        steps.expect_jwt_authentication_error(token=token)

    with And("check password authentication"):
        steps.check_clickhouse_client_password_login(
            user_name=user_name, password=password
        )


@TestScenario
def not_jwt_authentication(self):
    """Check that jwt authentication fails when user's authentication method
    is not jwt."""

    node = self.context.node

    with Given("create user with password authentication"):
        user_name = f"password_user_{getuid()}"
        password = "some_password"
        node.query(
            f"CREATE USER {user_name} IDENTIFIED WITH PLAINTEXT_PASSWORD BY '{password}'"
        )

    with When("add new validator with RS384 algorithm to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        algorithm = "RS384"
        public_key, private_key_file = steps.generate_ssh_keys()
        steps.add_dynamic_jwks_validator_to_config_xml(
            validator_id="jwks_with_RS384_algorithm",
            algorithm=algorithm,
            public_key_str=public_key,
            key_id=key_id,
        )

    with And("create token using RS384 algorithm"):
        token = define(
            "jwt",
            steps.create_static_jwt(
                user_name=user_name,
                algorithm=algorithm,
                private_key_path=private_key_file,
                key_id=key_id,
            ),
        )

    with And("check that user can login with password"):
        steps.check_clickhouse_client_password_login(
            user_name=user_name, password=password
        )

    with Then("check that jwt authentication fails"):
        steps.expect_jwt_authentication_error(token=token)


@TestScenario
def login_without_token(self):
    """Check that jwt authentication fails when user tries to login without token."""

    with Given("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(user_name=user_name)

    with When("add some validator to the config.xml"):
        key_id = f"some_key_id_{getuid()}"
        algorithm = "RS384"
        public_key, _ = steps.generate_ssh_keys()
        steps.add_dynamic_jwks_validator_to_config_xml(
            validator_id="jwks_with_RS384_algorithm",
            algorithm=algorithm,
            public_key_str=public_key,
            key_id=key_id,
        )

    with Then("check login without token"):
        steps.check_clickhouse_client_password_login(user_name=user_name, password="")


@TestFeature
def feature(self):
    """Check that jwt authentication fails when user's authentication method is not jwt."""
    Scenario(run=change_authentication_method)
    Scenario(run=not_jwt_authentication)
    Scenario(run=login_without_token)
