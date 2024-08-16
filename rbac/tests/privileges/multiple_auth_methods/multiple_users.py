import random

from testflows.core import *

from helpers.common import getuid

import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors


@TestScenario
@Name("create multiple users with same auth method")
def multiple_users_one_auth_method(self):
    """Check that I can create multiple users with same auth method."""
    with Given("construct a valid query"):
        number_of_users = random.randint(5, 20)
        user_names = [f"user_{i}_{getuid()}" for i in range(number_of_users)]
        users_string = ",".join(user_names)
        query = (
            f"CREATE USER {users_string} IDENTIFIED WITH plaintext_password BY '123'"
        )
        note(query)

    with Then("execute query"):
        common.execute_query(query=query)

    with And("login with every user"):
        for user_name in user_names:
            common.login(user_name=user_name, password="123")


@TestScenario
@Name("create multiple users with multiple auth methods")
def multiple_users_multiple_auth_methods(self):
    """Check that I can create multiple users with multiple auth methods."""
    with Given("construct a valid query"):
        number_of_users = random.randint(10, 100)
        user_names = [f"user_{i}_{getuid()}" for i in range(number_of_users)]
        users_string = ",".join(user_names)
        auth_methods = [
            "plaintext_password BY '123'",
            "plaintext_password BY '456'",
            "BY '789'",
        ]
        auth_methods_string = ",".join(auth_methods)
        query = f"CREATE USER {users_string} IDENTIFIED WITH {auth_methods_string}"
        note(query)

    with Then("execute query"):
        common.execute_query(query=query)

    with And("login with every user and with every auth method"):
        for user_name in user_names:
            for password in ["123", "456", "789"]:
                common.login(user_name=user_name, password=password)


@TestFeature
@Name("multiple users")
def feature(self, node="clickhouse1"):
    """Check multiple auth methods support when creating more that one user in same query."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
