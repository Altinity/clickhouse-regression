from testflows.core import *

from helpers.common import getuid
from helpers.sql.create_user import CreateUser

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions
import rbac.tests.privileges.multiple_auth_methods_v2.model as models


@TestStep(Given)
def create_user_with_two_plaintext_passwords(self, user_name):
    """I create user with two plain text passwords"""

    user_auth_methods = [
        actions.partial(CreateUser.set_with_plaintext_password, password="123"),
        actions.partial(CreateUser.set_with_plaintext_password, password="456"),
    ]

    return actions.create_user(user_name=user_name, auth_methods=user_auth_methods)


@TestStep(Then)
def check_login(self, user, altered_user=None):
    """Check login with old and new authentication methods."""

    with Then("I try to login using old authentication methods"):
        actions.login(user=user)

    if altered_user:
        with And("I try to login using new authentication methods"):
            actions.login(user=altered_user)

        with And("I try to login with slightly invalid passwords"):
            actions.login_with_wrong_password(user=altered_user)

        with And("I try to login with slightly wrong username"):
            actions.login_with_wrong_username(user=altered_user)


@TestScenario
def check_changing(self, auth_methods, node=None):
    """Check changing user authentication methods."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to change authentication methods"):
        altered_user = actions.alter_user(user=user, auth_methods=auth_methods)

    with Then("I try to login"):
        check_login(user=user, altered_user=altered_user)


@TestScenario
def check_adding(self, auth_methods, node=None):
    """Check adding new authentication methods."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to add authentication methods"):
        altered_user = actions.alter_user_add(user=user, auth_methods=auth_methods)

    with Then("I try to login"):
        check_login(user=user, altered_user=altered_user)


@TestScenario
def check_reset_to_new(self, auth_methods, node=None):
    """Check reseting auth methods to new."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to change authentication methods"):
        altered_user = actions.alter_user(user=user, auth_methods=auth_methods)

    with And("I alter user to reset authentication methods"):
        actions.alter_user_reset_to_new(user=altered_user)

    with Then("I try to login"):
        check_login(user=user, altered_user=altered_user)


@TestFeature
@Name("alter user")
def feature(self, node=None):
    """Check user can be altered with multiple authentication methods."""
    self.context.model = models.Model()

    if node is None:
        node = self.context.node

    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            for scenario in loads(current_module(), Scenario):
                Scenario(
                    f"#{num} {actions.names(auth_methods)} {scenario.name}",
                    test=scenario,
                    parallel=True,
                    executor=executor,
                )(node=node, auth_methods=auth_methods)

        join()
