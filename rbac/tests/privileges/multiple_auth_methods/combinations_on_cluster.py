from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid
from helpers.sql.create_user import CreateUser, Username
from helpers.sql.alter_user import AlterUser
from helpers.sql.drop_user import DropUser

import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models


@TestStep(Given)
def create_user_auth_methods_combinations(self, max_length=2):
    """Combinations of CREATE USER with different authentication methods."""
    create_auth_methods = [
        actions.partial(CreateUser.set_with_plaintext_password, password="foo1"),
        actions.partial(CreateUser.set_with_sha256_password, password="foo2"),
        actions.partial(CreateUser.set_by_password, password="foo3"),
        actions.partial(CreateUser.set_with_sha256_hash, password="foo4"),
    ]

    auth_methods_combinations = actions.create_user_auth_combinations(
        max_length=max_length, auth_methods=create_auth_methods
    )
    auth_methods_combinations.append([CreateUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def alter_user_auth_methods_combinations(self, max_length=2):
    """Combinations of ALTER USER with different authentication methods."""
    alter_auth_methods = [
        actions.partial(AlterUser.set_with_plaintext_password, password="foo5"),
        actions.partial(AlterUser.set_with_sha256_password, password="foo6"),
        actions.partial(AlterUser.set_by_password, password="foo7"),
        actions.partial(AlterUser.set_with_sha256_hash, password="foo8"),
    ]

    auth_methods_combinations = actions.alter_user_auth_combinations(
        max_length=max_length, auth_methods=alter_auth_methods
    )
    auth_methods_combinations.append([AlterUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def ways_to_create_user(self, auth_methods_combinations=None, cluster=None):
    """Ways to create user with multiple authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = create_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(
            actions.partial(
                actions.create_user,
                auth_methods=auth_methods,
                on_cluster=cluster,
            )
        )

    return ways


@TestStep(Given)
def ways_to_change(self, auth_methods_combinations=None, cluster=None):
    """Ways to change user authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(
            actions.partial(
                actions.alter_user, auth_methods=auth_methods, on_cluster=cluster
            )
        )

    return ways


@TestStep(Given)
def ways_to_add(self, auth_methods_combinations=None, cluster=None):
    """Ways to add user authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(
            actions.partial(
                actions.alter_user_add, auth_methods=auth_methods, on_cluster=cluster
            )
        )

    return ways


@TestStep(Given)
def ways_to_reset_to_new(self, cluster=None):
    """A way to reset users authentications methods to new."""
    return [actions.partial(actions.alter_user_reset_to_new, on_cluster=cluster)]


@TestStep(Given)
def ways_to_drop(self, cluster=None):
    """A way to drop user."""
    return [actions.drop_user(on_cluster=cluster)]


@TestScenario
def combination_of_actions(self, combination, node=None):
    """Check combination of actions."""
    self.context.behavior = []
    usernames = [Username(name="user_" + getuid())]

    if node is None:
        node = self.context.node

    with Given("I have client"):
        self.context.client = actions.node_client()

    queries = []

    for i, action in enumerate(combination):
        with When(f"I perform action {i} {action.__name__}"):
            query = action(usernames=usernames)
            if not isinstance(query, DropUser):
                queries.append(query)

        with Then("try to login"):
            for user in queries:
                actions.login(user=user)


@TestScenario
@Name("different combinations of actions")
def different_combinations(self, cluster=None):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    ways_to_create = []
    ways_to_alter = []
    self.context.model = models.Model()

    with Given("ways to create user with multiple authentication methods"):
        ways_to_create += ways_to_create_user(cluster=cluster)

    with And("ways change users authentication methods"):
        ways_to_alter += ways_to_change(cluster=cluster)

    with And("ways to add authentication methods to existing user"):
        ways_to_alter += ways_to_add(cluster=cluster)

    with And("ways to reset users authentications methods to new"):
        ways_to_alter += ways_to_reset_to_new(cluster=cluster)

    combinations = product(ways_to_create, ways_to_alter, ways_to_alter)

    with Pool(10) as executor:
        for i, combination in enumerate(combinations):
            Scenario(
                f"#{i}",
                test=combination_of_actions,
                parallel=True,
                executor=executor,
            )(combination=combination)
        join()


@TestFeature
@Name("combinations")
def feature(self, number_of_actions=1):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    cluster = "replicated_cluster"
    Scenario(test=different_combinations)(cluster=cluster)
