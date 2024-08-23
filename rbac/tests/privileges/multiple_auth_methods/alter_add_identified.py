from testflows.core import *

from rbac.requirements import *

import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models
import rbac.tests.privileges.multiple_auth_methods.errors as errors
import rbac.tests.privileges.multiple_auth_methods.common as common

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified_NoPassword("1.0"),
)
def check_adding_auth_methods(self, auth_methods):
    """Check that one or more authentication methods can be added to a user
    using ALTER USER ADD IDENTIFIED statement."""

    correct_passwords = ["123"]
    wrong_passwords = [j[1] for j in auth_methods]

    with Given("create user with one plaintext password authentication method"):
        user_name = f"user_{getuid()}"
        common.create_user(
            user_name=user_name, identified="plaintext_password BY '123'"
        )

    with When("add one or more authentication methods"):
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string:
            exitcode, message = errors.no_password_cannot_coexist_with_others()
            common.add_identified(
                user_name=user_name,
                identified=auth_methods_string,
                exitcode=exitcode,
                message=message,
            )
        else:
            common.add_identified(user_name=user_name, identified=auth_methods_string)
            correct_passwords = define(
                "new_correct_passwords", correct_passwords + wrong_passwords
            )
            wrong_passwords = define(
                "new wrong passwords",
                [f"wrong_{password}" for password in correct_passwords],
            )

    with Then("check that user can authenticate only with correct passwords"):
        common.check_login_with_correct_and_wrong_passwords(
            user_name=user_name,
            correct_passwords=correct_passwords,
            wrong_passwords=wrong_passwords,
        )

    with And(
        "check that changes in user's authentication methods are reflected in system.users table"
    ):
        common.check_changes_reflected_in_system_table(
            user_name=user_name, correct_passwords=correct_passwords
        )


@TestScenario
@Name("adding auth methods")
def adding_auth_methods(self):
    """Check that multiple authentication methods can be added to a user."""
    auth_methods_combinations = common.generate_auth_combinations(
        auth_methods_dict=common.authentication_methods_with_passwords,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"{num}",
                test=check_adding_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_adding_auth_methods_v2(self, auth_methods, node=None):
    """Check adding new authentication methods."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = common.create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to add authentication methods"):
        altered_user = actions.alter_user_add(user=user, auth_methods=auth_methods)

    with Then("I try to login"):
        common.check_login(user=user, altered_user=altered_user)


@TestScenario
@Name("adding auth methods v2")
def adding_auth_methods_v2(self):
    """Check that multiple authentication methods can be added to a user."""
    self.context.model = models.Model()
    node = self.context.node

    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"#{num} {actions.names(auth_methods)}",
                test=check_adding_auth_methods_v2,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()


@TestFeature
@Name("alter add identified")
def feature(self):
    """Check support of ALTER USER ADD IDENTIFIED statement with one or multiple
    authentication methods."""
    with Pool(2) as executor:
        Scenario(test=adding_auth_methods, parallel=True, executor=executor)()
        # Scenario(test=adding_auth_methods_v2, parallel=True, executor=executor)()
        join()
