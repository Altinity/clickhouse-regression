from testflows.core import *

from rbac.requirements import *

import rbac.tests.multiple_auth_methods.actions as actions
import rbac.tests.multiple_auth_methods.model as models
import rbac.tests.multiple_auth_methods.errors as errors
import rbac.tests.multiple_auth_methods.common as common

from helpers.common import getuid


@TestScenario
def check_changing_auth_methods(self, auth_methods):
    """Check that ALTER USER IDENTIFIED WITH statement with multiple authentication methods
    clears previous methods and sets new ones listed in the query."""

    with Given("create user with two plain text passwords"):
        user_name = f"user_{getuid()}"
        identified = f"plaintext_password BY '123', plaintext_password BY '456'"
        common.create_user(user_name=user_name, identified=identified)

    with And("create list of correct and wrong passwords for authentication"):
        correct_passwords = define("correct passwords", ["123", "456"])
        wrong_passwords = define("wrong passwords", [j[1] for j in auth_methods])

    with When("alter user with multiple authentication methods"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.alter_identified(
                user_name=user_name,
                identified=auth_methods_str,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.alter_identified(user_name=user_name, identified=auth_methods_str)
            if "no_password" in auth_methods_str:
                correct_passwords = define("new correct passwords", [""])
                wrong_passwords = define("new wrong passwords", [])
            else:
                correct_passwords, wrong_passwords = define(
                    "new correct passwords", wrong_passwords
                ), define("new wrong passwords", correct_passwords)

    with Then("check that user can login only with correct passwords"):
        common.check_login_with_correct_and_wrong_passwords(
            user_name=user_name,
            correct_passwords=correct_passwords,
            wrong_passwords=wrong_passwords,
        )

    with And("check that auth_type column in system.users table was updated"):
        common.check_changes_reflected_in_system_table(
            user_name=user_name, correct_passwords=correct_passwords
        )


@TestScenario
@Name("changing auth methods")
def changing_auth_methods(self):
    """Check that user can be altered with all combinations of multiple authentication methods."""
    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords, max_length=3
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"changing auth methods {num}",
                test=check_changing_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_changing_auth_methods_v2(self, auth_methods, node=None):
    """Check that ALTER USER IDENTIFIED WITH statement with multiple authentication methods
    clears previous methods and sets new ones listed in the query."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("create user with two plain text passwords"):
        user = common.create_user_with_two_plaintext_passwords(
            user_name=user_name, client=node
        )

    with When("alter user to change authentication methods"):
        altered_user = actions.alter_user(
            user=user, auth_methods=auth_methods, client=node
        )

    with Then("try to login"):
        common.check_login(user=user, altered_user=altered_user)


@TestScenario
@Name("changing auth methods v2")
def changing_auth_methods_v2(self):
    """Check that user can be altered with multiple authentication methods."""

    self.context.model = models.Model()
    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"#{num} {actions.names(auth_methods)}",
                test=check_changing_auth_methods_v2,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("alter identified")
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AlterUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AlterUser_NoPassword("1.0"),
)
def feature(self):
    """Check support of multiple authentication methods in ALTER USER IDENTIFIED WITH statement."""
    with Pool(2) as executor:
        Scenario(test=changing_auth_methods, parallel=True, executor=executor)()
        Scenario(test=changing_auth_methods_v2, parallel=True, executor=executor)()
        join()
