from testflows.core import *

from helpers.common import getuid, get_settings_value

import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors


@TestScenario
@Name("omit WITH and auth type")
def omit_with_and_auth_type(self):
    """Check that it is possible to omit WITH keyword and auth type when creating user identified
    by some passwords. Default auth type should be used."""
    try:
        with Given("construct a valid query"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED BY '123'"
            note(query)

        with Then("execute query"):
            common.execute_query(query=query)

        with And("login with specified password"):
            common.login(user_name=user_name, password="123")
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user with NO_PASSWORD upper case")
def no_password_upper_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH NO_PASSWORD clause."""
    try:
        with Given("construct CREATE USER query with NO_PASSWORD auth method"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED WITH NO_PASSWORD"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user with no_password lower case")
def no_password_lower_case(self):
    """Check that user can be created with no password using IDENTIFIED WITH no_password clause."""
    try:
        with Given("construct CREATE USER query with no_password auth method"):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} IDENTIFIED WITH no_password"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
@Name("create user not identified")
def create_user_not_identified(self):
    """Check that user can be created with no password by using NOT IDENTIFIED clause."""
    try:
        with Given(
            "construct CREATE USER query with no_password using NOT IDENTIFIED clause"
        ):
            user_name = f"user_{getuid()}"
            query = f"CREATE USER {user_name} NOT IDENTIFIED"
            note(query)

        with Then("execute query, expect success"):
            common.execute_query(query=query)

        with And("login without password"):
            common.login(user_name=user_name)
    finally:
        with Finally("drop user"):
            common.execute_query(query=f"DROP USER IF EXISTS {user_name}")


@TestScenario
def check_default_value_of_setting(self):
    """Check that default value of `max_authentication_methods_per_user` is 100."""
    with Given("get default value of `max_authentication_methods_per_user`"):
        default_value = get_settings_value(
            "max_authentication_methods_per_user", table="system.server_settings"
        )

    with Then("check that default value is 100"):
        assert default_value == "100", f"expected 100, got {default_value}"


@TestFeature
@Name("sanity check")
def feature(self):
    """Check syntax when creating or altering user with one or multiple auth methods."""
    with Pool(3) as executor:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE, parallel=True, executor=executor)
        join()
