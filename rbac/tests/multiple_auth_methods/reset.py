from testflows.core import *

from rbac.requirements import *

import rbac.tests.multiple_auth_methods.actions as actions
import rbac.tests.multiple_auth_methods.model as models
import rbac.tests.multiple_auth_methods.errors as errors
import rbac.tests.multiple_auth_methods.common as common

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_ResetAuthenticationMethods(
        "1.0"
    ),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_System_Users("1.0"),
)
def check_reset_to_new(self, auth_methods):
    """Check that auth methods are being reset correctly to the most recent one
    with different auth methods combinations."""

    user_name = f"user_{getuid()}"
    user_created = False

    with Given("create user with multiple authentication methods"):
        auth_methods_str = define("auth methods", ", ".join(j[0] for j in auth_methods))
        if "no_password" in auth_methods_str and len(auth_methods) > 1:
            common.create_user(
                user_name=user_name,
                identified=auth_methods_str,
                expected=errors.no_password_cannot_coexist_with_others(),
            )
        else:
            common.create_user(user_name=user_name, identified=auth_methods_str)
            user_created = True

    if user_created:
        with When("reset authentication methods"):
            common.reset_auth_methods_to_new(user_name=user_name)

        with Then(
            "check that user can login with only the most recently added authentication method"
        ):
            recent_password = auth_methods[-1][1]
            wrong_passwords = [j[1] for j in auth_methods[:-1]]
            common.check_login_with_correct_and_wrong_passwords(
                user_name=user_name,
                correct_passwords=[recent_password],
                wrong_passwords=wrong_passwords,
            )

        with And(
            "check that changes in authentication methods are reflected in system.users table"
        ):
            common.check_changes_reflected_in_system_table(
                user_name=user_name, correct_passwords=[recent_password]
            )


@TestScenario
@Name("check resetting auth methods")
def resetting_auth_methods(self):
    """Run test that checks `RESET AUTHENTICATION METHODS TO NEW` clause with
    different auth methods combinations."""

    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"check reset to new {num}",
                test=check_reset_to_new,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_reset_to_new_v2(self, auth_methods, node=None):
    """Check that auth methods are being reset correctly to the most recent one
    with different auth methods combinations."""
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

    with And("alter user to reset authentication methods"):
        actions.alter_user_reset_to_new(user=altered_user, client=node)

    with Then("try to login"):
        common.check_login(user=user, altered_user=altered_user)


@TestScenario
@Name("check resetting auth methods v2")
def resetting_auth_methods_v2(self):
    """Run test that checks `RESET AUTHENTICATION METHODS TO NEW` clause with
    different auth methods combinations."""

    self.context.model = models.Model()
    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"#{num} {actions.names(auth_methods)}",
                test=check_reset_to_new_v2,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("reset to new")
def feature(self):
    """Check support of ALTER USER RESET AUTHENTICATION METHODS TO NEW statement."""
    with Pool(2) as executor:
        Scenario(test=resetting_auth_methods, parallel=True, executor=executor)()
        Scenario(test=resetting_auth_methods_v2, parallel=True, executor=executor)()
        join()
