import random

from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid
from helpers.sql.create_user import CreateUser, Username
from helpers.sql.alter_user import AlterUser
from helpers.sql.drop_user import DropUser

from rbac.requirements import *

import rbac.tests.multiple_auth_methods.actions as actions
import rbac.tests.multiple_auth_methods.model as models


@TestStep(Given)
def create_user_auth_methods_combinations(self):
    """Combinations of CREATE USER with different authentication methods."""
    create_auth_methods = [
        actions.partial(CreateUser.set_with_plaintext_password, password="foo3"),
        actions.partial(CreateUser.set_with_sha256_password, password="foo4"),
        actions.partial(CreateUser.set_by_password, password="foo5"),
    ]

    auth_methods_combinations = actions.create_user_auth_combinations(
        max_length=2, auth_methods=create_auth_methods
    )
    auth_methods_combinations.append([CreateUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def alter_user_auth_methods_combinations(self):
    """Combinations of ALTER USER with different authentication methods."""
    alter_auth_methods = [
        actions.partial(AlterUser.set_with_plaintext_password, password="foo3"),
        actions.partial(AlterUser.set_with_sha256_password, password="foo4"),
        actions.partial(AlterUser.set_by_password, password="foo5"),
    ]

    auth_methods_combinations = actions.alter_user_auth_combinations(
        max_length=2, auth_methods=alter_auth_methods
    )
    auth_methods_combinations.append([AlterUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def ways_to_create_user(self, auth_methods_combinations=None):
    """Ways to create user with multiple authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = create_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(actions.partial(actions.create_user, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def ways_to_change(self, auth_methods_combinations=None):
    """Ways to change user authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(actions.partial(actions.alter_user, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def ways_to_add(self, auth_methods_combinations=None):
    """Ways to add user authentication methods."""
    ways = []

    if auth_methods_combinations is None:
        auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(actions.partial(actions.alter_user_add, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def ways_to_reset_to_new(self):
    """A way to reset users authentications methods to new."""
    return [actions.alter_user_reset_to_new]


@TestStep(Given)
def ways_to_drop(self):
    """A way to drop user."""
    return [actions.drop_user]


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
def different_combinations(self, number_of_actions=3):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    ways = []
    self.context.model = models.Model()

    with Given("ways to create user with multiple authentication methods"):
        ways += ways_to_create_user()

    with And("ways change users authentication methods"):
        ways += ways_to_change()

    with And("ways to add authentication methods to existing user"):
        ways += ways_to_add()

    with And("ways to reset users authentications methods to new"):
        ways += ways_to_reset_to_new()

    with And("a way to drop user"):
        ways += ways_to_drop()

    combinations = list(product(ways, repeat=number_of_actions))
    if not self.context.stress:
        combinations = random.sample(combinations, 1000)

    with Pool(4) as executor:
        for i, combination in enumerate(product(ways, repeat=number_of_actions)):
            Scenario(
                f"#{i}", test=combination_of_actions, parallel=True, executor=executor
            )(combination=combination)
        join()


@TestScenario
@Name("different combinations of actions starting with create")
def different_combinations_starting_with_create(self):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    ways_to_create = []
    ways_to_alter = []
    self.context.model = models.Model()

    with Given("ways to create user with multiple authentication methods"):
        ways_to_create += ways_to_create_user()

    with And("ways change users authentication methods"):
        ways_to_alter += ways_to_change()

    with And("ways to add authentication methods to existing user"):
        ways_to_alter += ways_to_add()

    with And("ways to reset users authentications methods to new"):
        ways_to_alter += ways_to_reset_to_new()

    combinations = list(
        product(ways_to_create, ways_to_alter, ways_to_alter, ways_to_alter)
    )

    if not self.context.stress:
        combinations = random.sample(combinations, 1000)

    with Pool(4) as executor:
        for i, combination in enumerate(combinations):
            Scenario(
                f"#{i}", test=combination_of_actions, parallel=True, executor=executor
            )(combination=combination)
        join()


@TestFeature
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_MixedWithAndWithoutWith("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_PlaintextPassword("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_Sha256Password("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_BcryptPassword("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_DoubleSha1Password("1.0"),
)
@Name("combinations")
def feature(self):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    with Pool(2) as executor:
        Scenario(run=different_combinations, parallel=True, executor=executor)
        Scenario(
            run=different_combinations_starting_with_create,
            parallel=True,
            executor=executor,
        )
        join()
