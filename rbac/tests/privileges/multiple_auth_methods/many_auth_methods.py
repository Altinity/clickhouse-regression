from testflows.core import *

from helpers.common import getuid

import rbac.tests.privileges.multiple_auth_methods.common as common


@TestScenario
def many_auth_methods(self):
    """Check that user can have 1000 auth methods."""
    with Given("construct a query with user having 1000 auth methods"):
        user_name = f"user_{getuid()}"
        auth_methods = []
        passwords = []
        number_of_methods = 1000
        for i in range(number_of_methods):
            auth_methods.append(f"plaintext_password by '{i}'")
            passwords.append(f"{i}")

        auth_methods_string = ",".join(auth_methods)
        query = f"CREATE USER {user_name} IDENTIFIED WITH {auth_methods_string}"

    with Then("execute query"):
        common.execute_query(query=query)

    with And("login with every password"):
        for password in passwords:
            common.login(user_name=user_name, password=password)


@TestFeature
@Name("many auth methods")
def feature(self, node="clickhouse1"):
    """Check that user can have >= 1000 authentication methods."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
