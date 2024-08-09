from testflows.core import *

from helpers.common import getuid

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions
import rbac.tests.privileges.multiple_auth_methods_v2.model as models


@TestScenario
def check_create_user_with_multiple_auth_methods(self, auth_methods, node=None):
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


@TestFeature
@Name("create user")
def feature(self, node=None):
    """Check that user can be created with multiple authentication methods."""
    self.context.model = models.Model()

    if node is None:
        node = self.context.node

    auth_methods = actions.generate_auth_combinations()

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num} {actions.names(auth_methods)}",
                test=check_create_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()
