from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *

from helpers.common import getuid, get_settings_value, check_clickhouse_version

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors

import hashlib


@TestStep(Given)
def set_time(self, value="2025-01-01 12:00:00 UTC"):
    """Set time to some fixed value."""
    bash = self.context.cluster.bash(node=None)
    cmd = bash(f"apt-get install faketime")
    assert cmd.exitcode == 0, error()
    cmd = bash(f"faketime '{value}' bash")
    assert cmd.exitcode == 0, error()


@TestScenario
def sha_256_hash_auth_method(self):
    """Check that VALID UNTIL works with SHA256 hash authentication method."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("create user with expiration date"):
            password = "foo1"
            hash_value = hashlib.sha256(password.encode("utf-8")).hexdigest()
            query = f"CREATE USER {user_name} IDENTIFIED WITH sha256_hash BY '{hash_value}' VALID UNTIL '2025-12-12'"
            node.query(query)

        with When("login with specified password"):
            common.login(user_name=user_name, password=password)

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def bcrypt_auth_method(self):
    """Check that VALID UNTIL works with BCRYPT password authentication method."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("create user with expiration date"):
            password = "foo1"
            query = f"CREATE USER {user_name} IDENTIFIED WITH bcrypt_password BY '{password}' VALID UNTIL '2025-12-12'"
            node.query(query)

        with When("login with specified password"):
            common.login(user_name=user_name, password=password)

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def same_passwords_one_expired(self):
    """Check that if user has two same passwords and one of them is expired, user still can login."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("create user with two same passwords and one of them is expired"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '2025-12-12', "
                "BY '123' VALID UNTIL '2023-12-12'"
            )
            node.query(query)

        with When("check that user can login with this password"):
            common.login(user_name=user_name, password="123")

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def same_password_one_expired_different_auth_methods(self):
    """Check that if user has two same passwords for two different auth methods
    and one of them is expired, user still can login."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("create user with two same passwords and one of them is expired"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '2025-12-12', "
                "double_sha1_password BY '123' VALID UNTIL '2023-12-12'"
            )
            node.query(query)

        with When("check that user can login with this password"):
            common.login(user_name=user_name, password="123")

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestFeature
@Name("valid until")
def feature(self):
    """Check VALID UNTIL clause."""
    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE, parallel=True, executor=executor)
        join()
