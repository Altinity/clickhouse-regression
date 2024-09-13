from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors

from rbac.tests.privileges.multiple_auth_methods.server_setting.common import *


@TestScenario
def check_reset_when_max_auth_methods_per_user_is_set_to_some_value(self, value=0):
    """Check that ALTER RESET AUTHENTICATION METHODS TO NEW statement is working
    regardless of the value of `max_authentication_methods_per_user` setting."""
    with Given("create user with 3 authentication methods and get correct passwords"):
        user_name = "user_" + getuid()
        initial_passwords = define(
            "initial passwords",
            create_user_identified_with_three_methods(user_name=user_name),
        )

    with And(f"set `max_authentication_methods_per_user` to {value}"):
        common.change_server_settings(
            setting="max_authentication_methods_per_user", value=value
        )

    with When("reset authentication methods to new"):
        common.reset_auth_methods_to_new(user_name=user_name)

    with Then("check that user can login only with most recently added auth method"):
        correct_password = define("correct password", initial_passwords[-1])
        common.login(user_name=user_name, password=correct_password)

    with And("check that user can not login with other passwords"):
        for password in initial_passwords[:-1]:
            common.login(
                user_name=user_name,
                password=password,
                expected=errors.wrong_password(user_name),
            )

    with When("try to reset authentication methods to new again"):
        common.reset_auth_methods_to_new(user_name=user_name)

    with Then("check that user can login"):
        common.login(user_name=user_name, password=correct_password)


@TestScenario
def reset_with_different_values_of_max_auth_methods_per_user(self):
    """Run `check_reset_when_max_auth_methods_per_user_is_set_to_some_value` scenario
    with different values of `max_authentication_methods_per_user` setting."""
    values = [0, 1, 2, 3, 100, 200]
    for value in values:
        Scenario(
            name=f"max_authentication_methods_per_user={value}",
            test=check_reset_when_max_auth_methods_per_user_is_set_to_some_value,
        )(value=value)


@TestFeature
@Name("reset")
def feature(self):
    """Check that user can be created with no more than `max_authentication_methods_per_user`
    authentication methods."""
    Scenario(run=reset_with_different_values_of_max_auth_methods_per_user)
