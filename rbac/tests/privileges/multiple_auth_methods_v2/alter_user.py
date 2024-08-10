from testflows.core import *

from helpers.common import getuid
from helpers.sql.create_user import CreateUser

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions
import rbac.tests.privileges.multiple_auth_methods_v2.model as models


@TestScenario
def check_alter_user(self, auth_methods, node=None):
    """Check that all authentication methods can be added to the user."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user_name = f"user_{getuid()}"
        user_auth_methods = [
            actions.partial(CreateUser.set_with_plaintext_password, password="123"),
            actions.partial(CreateUser.set_with_plaintext_password, password="456"),
        ]
        user = actions.create_user(user_name=user_name, auth_methods=user_auth_methods)

    with When("I alter user authentication methods"):
        altered_user = actions.alter_user(user=user, auth_methods=auth_methods)

    with Then("I try to login using old authentication methods"):
        actions.login(user=user)

    with And("I try to login using new authentication methods"):
        actions.login(user=altered_user)

    with And("I try to login with slightly invalid passwords"):
        actions.login_with_wrong_password(user=altered_user)

    with And("I try to login with slightly wrong username"):
        actions.login_with_wrong_username(user=user)


@TestFeature
@Name("alter user")
def feature(self, node=None):
    """Check user can be altered with multiple authentication methods."""
    self.context.model = models.Model()

    if node is None:
        node = self.context.node

    auth_methods = actions.generate_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num} {actions.names(auth_methods)}",
                test=check_alter_user,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()
