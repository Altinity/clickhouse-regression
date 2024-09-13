from testflows.core import *

from rbac.requirements import *

import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models
import rbac.tests.privileges.multiple_auth_methods.errors as errors
import rbac.tests.privileges.multiple_auth_methods.common as common

from helpers.common import getuid

# FIXME: add test to check login with another user's password
@TestScenario
def create_user_with_multiple_auth_methods_v2(self, auth_methods, node=None):
    """Check that all authentication methods can be added to the user."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with When("I create user with multiple authentication methods"):
        user = actions.create_user(user_name=user_name, auth_methods=auth_methods)

    with Then("I try to login"):
        actions.login(user=user)

    with And("I try to login with slightly wrong password"):
        actions.login_with_wrong_password(user=user)

    with And("I try to login with slightly wrong username"):
        actions.login_with_wrong_username(user=user)


@TestScenario
@Name("check create user with multiple auth methods v2")
def check_create_user_v2(self, node=None):
    """Run create user with multiple auth methods test with all combinations of auth methods."""
    self.context.model = models.Model()

    if node is None:
        node = self.context.node

    auth_methods_combinations = actions.create_user_auth_combinations(max_length=2)

    with Pool(5) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"{num} {actions.names(auth_methods)}",
                test=create_user_with_multiple_auth_methods_v2,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()


@TestScenario
def create_user_with_multiple_auth_methods(self, auth_methods):
    """Check that user can be created with multiple authentication methods."""

    user_name = f"user_{getuid()}"

    with Given("create list of correct and wrong passwords for authentication"):
        correct_passwords = define("correct passwords", [])
        wrong_passwords = define("wrong passwords", [j[1] for j in auth_methods])

    with When("create user with multiple authentication methods"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_str,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.create_user(user_name=user_name, identified=auth_methods_str)
            if "no_password" in auth_methods_str:
                correct_passwords = define("new correct passwords", [""])
                wrong_passwords = define("new wrong passwords", [])
            else:
                correct_passwords = define("new correct passwords", wrong_passwords)
                wrong_passwords = define(
                    "new wrong passwords",
                    [f"wrong_{password}" for password in correct_passwords],
                )

    with Then("check that user can only login with correct passwords"):
        common.check_login_with_correct_and_wrong_passwords(
            user_name=user_name,
            correct_passwords=correct_passwords,
            wrong_passwords=wrong_passwords,
        )

    with And(
        "check that creating a user with multiple auth methods updates the system.users table"
    ):
        common.check_changes_reflected_in_system_table(
            user_name=user_name, correct_passwords=correct_passwords
        )


@TestScenario
@Name("check create user with multiple auth methods")
def check_create_user_with_multiple_auth_methods(self):
    """Run create user with multiple auth methods test with all combinations of auth methods."""
    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords, max_length=3
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"{num}",
                test=create_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("create user with multiple auth methods")
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser_NoPassword("1.0"),
)
def feature(self):
    """Check that user can be created with multiple authentication methods."""
    with Pool(2) as executor:
        Scenario(test=check_create_user_v2, parallel=True, executor=executor)()
        Scenario(
            test=check_create_user_with_multiple_auth_methods,
            parallel=True,
            executor=executor,
        )()
        join()
