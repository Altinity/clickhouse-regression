from testflows.core import *

from helpers.common import getuid

import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors
import rbac.helper.common as helper


@TestScenario
def create_user_with_many_auth_methods(self):
    """Check that user can be created with 1000 authentication methods."""
    number_of_auth_methods = 1000
    try:
        with Given("set max_authentication_methods_per_user to 1000"):
            common.change_server_settings(
                setting="max_authentication_methods_per_user",
                value=number_of_auth_methods,
            )

        with And("construct a query with user having 1000 auth methods"):
            user_name = f"user_{getuid()}"
            passwords = [str(i) for i in range(number_of_auth_methods)]
            auth_methods = [
                f"plaintext_password by '{password}'" for password in passwords
            ]
            auth_methods_string = ",".join(auth_methods)
            query = f"CREATE USER {user_name} IDENTIFIED WITH {auth_methods_string}"

        with Then("execute CREATE USER query with 1000 auth methods"):
            common.execute_query(query=query)

        with And("login with every password"):
            for password in passwords:
                common.login(user_name=user_name, password=password)

        with And("login with NO_PASSWORD and expect error"):
            common.login(
                user_name=user_name,
                expected=errors.no_user_with_such_name(user_name),
            )

        with And("login with wrong password and expect error"):
            common.login(
                user_name=user_name,
                password="wrong_password",
                expected=errors.no_user_with_such_name(user_name),
            )
    finally:
        with Finally("drop user"):
            query = f"DROP USER IF EXISTS {user_name}"
            common.execute_query(query=query)


@TestScenario
def add_many_auth_methods_to_user(self):
    """Check that 1000 authentication methods can be added to user."""
    with Given("set max_authentication_methods_per_user to 1000"):
        number_of_auth_methods = 1000
        common.change_server_settings(
            setting="max_authentication_methods_per_user", value=number_of_auth_methods
        )

    with And("create user with NO_PASSWORD auth method"):
        user_name = f"user_{getuid()}"
        helper.create_user(user_name=user_name, identified="NO_PASSWORD")

    with And("add 1000 auth methods to user"):
        passwords = [str(i) for i in range(number_of_auth_methods)]
        queries = [
            f"ALTER USER {user_name} ADD IDENTIFIED WITH plaintext_password by '{password}'"
            for password in passwords
        ]
        combined_query = "; ".join(queries)
        common.execute_query(query=combined_query)

    with Then("login with every password"):
        for password in passwords:
            common.login(user_name=user_name, password=password)

    with And("login with NO_PASSWORD and expect error"):
        common.login(
            user_name=user_name,
            expected=errors.no_user_with_such_name(user_name),
        )

    with And("login with wrong password and expect error"):
        common.login(
            user_name=user_name,
            password="wrong_password",
            expected=errors.no_user_with_such_name(user_name),
        )


@TestFeature
@Name("many auth methods")
def feature(self):
    """Check that user can have 1000 authentication methods."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
