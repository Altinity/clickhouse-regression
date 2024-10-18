from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *

from helpers.common import getuid

import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors

import random


@TestScenario
def same_passwords_one_expired(self):
    """Check that if user has two same passwords and one of them is expired,
    user still can login."""
    node = self.context.node
    user_name = f"user_{getuid()}"

    try:
        with Given("get future and past date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("create user with two same passwords, one of them is expired"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{future_date}', "
                f"BY '123' VALID UNTIL '{past_date}'"
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
        with Given("get future and past date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("create user with two same passwords and one of them is expired"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{future_date}', "
                f"double_sha1_password BY '123' VALID UNTIL '{past_date}'"
            )
            node.query(query)

        with When("check that user can login with this password"):
            common.login(user_name=user_name, password="123")

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def multiple_users(self):
    """Check that multiple users can be created with different authentication methods
    and different expiration dates for every authentication method."""
    user_name1 = f"user1_{getuid()}"
    user_name2 = f"user2_{getuid()}"
    user_name3 = f"user3_{getuid()}"
    password1 = "123"
    password2 = "456"

    node = self.context.node

    try:
        with Given("get future and past date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("create three users with multiple auth methods and expiration dates"):
            query = (
                f"CREATE USER {user_name1}, {user_name2}, {user_name3} IDENTIFIED WITH "
                f"double_sha1_password BY '{password1}' VALID UNTIL '{future_date}', "
                f"BY '{password2}' VALID UNTIL '{past_date}'"
            )

            node.query(query)

        with Then("check that users can login with non-expired password"):
            common.login(user_name=user_name1, password=password1)
            common.login(user_name=user_name2, password=password1)
            common.login(user_name=user_name3, password=password1)

        with And("check that users cannot login with expired password"):
            common.login(
                user_name=user_name1,
                password=password2,
                expected=errors.wrong_password(user_name1),
            )
            common.login(
                user_name=user_name2,
                password=password2,
                expected=errors.wrong_password(user_name2),
            )
            common.login(
                user_name=user_name3,
                password=password2,
                expected=errors.wrong_password(user_name3),
            )

        with And(
            "check that auth method and expiration date are reflected in SHOW CREATE USER"
        ):
            for user in [user_name1, user_name2, user_name3]:
                show_create_user = node.query(f"SHOW CREATE USER {user}").output
                assert "double_sha1_password" in show_create_user, error()
                assert f"VALID UNTIL \\'{future_date}\\'" in show_create_user, error()
                assert f"VALID UNTIL \\'{past_date}\\'" in show_create_user, error()

    finally:
        with Finally("drop users"):
            common.execute_query(
                query=f"DROP USER IF EXISTS {user_name1}, {user_name2}, {user_name3}"
            )


# executed from multi auth methods feature separately because of server setting
# change and restart
@TestCheck
def keep_adding_new_auth_methods_with_expiration_date(self):
    """Check that user can have many authentication methods with expiration date.
    The server should not crash during the process."""
    node = self.context.node
    user_name = f"user_{getuid()}"
    passwords = [f"foo{i}" for i in range(0, 2001)]
    num_auth_methods = 2000

    try:
        with Given("get future date"):
            get_future_date = node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output

        with Given("set max_authentication_methods_per_user to 1000"):
            common.change_server_settings(
                setting="max_authentication_methods_per_user",
                value=num_auth_methods,
            )

        with And(
            "create a user with initial authentication method and expiration date"
        ):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '{passwords[0]}'"
                f"VALID UNTIL '{future_date}'"
            )
            node.query(query)

        with When(
            f"adding {num_auth_methods} authentication methods with expiration date"
        ):
            for i in range(1, num_auth_methods):
                query = (
                    f"ALTER USER {user_name} ADD IDENTIFIED WITH sha256_password "
                    f"BY '{passwords[i]}' VALID UNTIL '{future_date}'"
                )
                node.query(query)

        with Then("check that user can login with any of the passwords"):
            password = random.choice(passwords)
            common.login(user_name=user_name, password=password)

    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def on_cluster(self):
    """Check that VALID UNTIL clause with multiple authentication methods works on a cluster."""
    user_name = f"user_{getuid()}"

    try:
        with Given("get future and past date"):
            get_future_date = self.context.node.query("SELECT now() + INTERVAL 1 DAY")
            future_date = get_future_date.output
            get_past_date = self.context.node.query("SELECT now() - INTERVAL 1 DAY")
            past_date = define("past date", get_past_date.output)

        with And("create user with two same passwords and one of them is expired"):
            query = (
                f"CREATE USER {user_name} IDENTIFIED BY '123' VALID UNTIL '{future_date}', "
                f"BY '123' VALID UNTIL '{past_date}' ON CLUSTER replicated_cluster"
            )
            common.execute_query(query=query)

        with When("change valid until on second node"):
            self.context.node_2.query(
                f"ALTER USER {user_name} VALID UNTIL '{past_date}'"
            )

        with Then(
            "check that user can login with this password on first and third nodes"
        ):
            common.login(user_name=user_name, password="123", node=self.context.node)
            common.login(user_name=user_name, password="123", node=self.context.node_3)

        with And("check that user cannot login with expired password on second node"):
            common.login(
                user_name=user_name,
                password="123",
                node=self.context.node_2,
                expected=errors.wrong_password(user_name),
            )
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestFeature
@Name("valid until")
def feature(self):
    """Check VALID UNTIL clause with multiple authentication methods."""
    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE, parallel=True, executor=executor)
        join()
