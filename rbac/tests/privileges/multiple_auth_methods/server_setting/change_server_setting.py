from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors

from rbac.tests.privileges.multiple_auth_methods.server_setting.common import *


@TestScenario
def check_reset_when_max_auth_methods_per_user_is_set_to_zero(self):
    """Check that ALTER RESET AUTHENTICATION METHODS TO NEW statement does not work
    when `max_authentication_methods_per_user` is set to 0."""
    with Given(
        "create user with three authentication methods and get correct passwords"
    ):
        user_name = "user_" + getuid()
        correct_passwords = define(
            "correct passwords",
            create_user_identified_with_three_methods(user_name=user_name),
        )

    with And("set `max_authentication_methods_per_user` to 0"):
        common.change_server_settings(
            setting="max_authentication_methods_per_user", value=0
        )

    with When("try to reset authentication methods, expect error message"):
        common.reset_auth_methods_to_new(
            user_name=user_name, expected=errors.user_can_not_be_created_updated()
        )

    with Then("check that user can login with all auth methods"):
        for password in correct_passwords:
            common.login(user_name=user_name, password=password)


@TestScenario
def check_reset_when_max_auth_methods_per_user_is_set_to_one(self):
    """Check that ALTER RESET AUTHENTICATION METHODS TO NEW statement is working
    correctly when `max_authentication_methods_per_user` is set to 1."""
    with Given(
        "create user with three authentication methods and get correct passwords"
    ):
        user_name = "user_" + getuid()
        initial_passwords = define(
            "initial passwords",
            create_user_identified_with_three_methods(user_name=user_name),
        )

    with And("set `max_authentication_methods_per_user` to 1"):
        common.change_server_settings(
            setting="max_authentication_methods_per_user", value=1
        )

    with When("reset authentication methods to new"):
        common.reset_auth_methods_to_new(user_name=user_name)

    with Then("check that user can only login with most recently added auth method"):
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
def check_add_auth_methods_when_max_auth_methods_was_reached(self):
    """Check that it is not possible to add auth methods when user already has
    `max_authentication_methods_per_user` authentication methods."""
    user_name = "user_" + getuid()
    with Given(
        "create user with three authentication methods and get correct passwords"
    ):
        initial_passwords = define(
            "initial passwords",
            create_user_identified_with_three_methods(user_name=user_name),
        )

    with And("set `max_authentication_methods_per_user` to 3"):
        common.change_server_settings(
            setting="max_authentication_methods_per_user", value=3
        )

    with When("try to add one more auth method to a user"):
        new_password = alter_user_add_one_auth_method(
            user_name=user_name,
            max_auth_methods_per_user=3,
            current_number_of_auth_methods=3,
        )

    with Then("check that user can only login with initial passwords"):
        for password in initial_passwords:
            common.login(user_name=user_name, password=password)

    with And("check that new auth method was not added"):
        common.login(
            user_name=user_name,
            password=new_password,
            expected=errors.wrong_password(user_name),
        )


@TestFeature
@Name("max auth methods server setting")
def feature(self):
    """Check that user can be created with no more than `max_authentication_methods_per_user`
    authentication methods."""
    Scenario(run=check_reset_when_max_auth_methods_per_user_is_set_to_zero)
    Scenario(run=check_reset_when_max_auth_methods_per_user_is_set_to_one)
    Scenario(run=check_add_auth_methods_when_max_auth_methods_was_reached)
