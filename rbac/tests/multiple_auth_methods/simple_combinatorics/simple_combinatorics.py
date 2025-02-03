import random

from testflows.core import *
from testflows.combinatorics import product

from helpers.common import getuid
from .create_user import CreateUser
from .alter_user import AlterUser

import rbac.tests.multiple_auth_methods.simple_combinatorics.actions as actions
import rbac.tests.multiple_auth_methods.simple_combinatorics.model as models

from functools import wraps

random.seed(42)


def partial(func, *args, **keywords):
    """Create a new function with partial application of the given arguments and keywords."""

    @wraps(func)
    def newfunc(*fargs, **fkeywords):
        newkeywords = {**keywords, **fkeywords}
        return func(*args, *fargs, **newkeywords)

    return newfunc


@TestStep(Given)
def create_user_auth_methods_combinations(self):
    """Combinations of CREATE USER with different authentication methods."""
    create_auth_methods = [
        CreateUser.set_with_no_password,
        partial(CreateUser.set_with_plaintext_password, password="foo1"),
        partial(CreateUser.set_with_sha256_hash_with_salt, password="foo2", salt="bar"),
        partial(CreateUser.set_with_bcrypt_password, password="foo3"),
        partial(CreateUser.set_with_double_sha1_hash, password="foo4"),
    ]

    auth_methods_combinations = actions.create_user_auth_combinations(
        max_length=2, auth_methods=create_auth_methods
    )
    # auth_methods_combinations.append([CreateUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def ways_to_create_user(self):
    """Ways to create user with multiple authentication methods."""
    ways = []

    auth_methods_combinations = create_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(partial(actions.create_user, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def alter_user_auth_methods_combinations(self):
    """Combinations of ALTER USER with different authentication methods."""
    alter_auth_methods = [
        AlterUser.set_with_no_password,
        partial(AlterUser.set_with_plaintext_password, password="foo5"),
        partial(AlterUser.set_with_sha256_hash_with_salt, password="foo6", salt="bar"),
        partial(AlterUser.set_with_bcrypt_password, password="foo1"),
        partial(AlterUser.set_with_double_sha1_hash, password="foo2"),
    ]

    auth_methods_combinations = actions.alter_user_auth_combinations(
        max_length=2, auth_methods=alter_auth_methods
    )
    # auth_methods_combinations.append([AlterUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def ways_to_change(self):
    """Ways to change user authentication methods."""
    ways = []

    auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(partial(actions.alter_user, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def ways_to_add(self):
    """Ways to add user authentication methods."""
    ways = []

    auth_methods_combinations = alter_user_auth_methods_combinations()

    for auth_methods in auth_methods_combinations:
        ways.append(partial(actions.alter_user_add, auth_methods=auth_methods))

    return ways


@TestStep(Given)
def ways_to_reset_to_new(self):
    """A way to reset users authentications methods to new."""
    return [actions.alter_user_reset_to_new]


@TestScenario
def check_sequence_of_actions(self, combination, node=None):
    """Check combination of actions."""
    self.context.behavior = []
    user_name = "user_" + getuid()

    if node is None:
        node = self.context.node

    queries = []

    for i, action in enumerate(combination):
        with When(f"I perform action {i} {action.__name__}"):
            query = action(user_name=user_name, client=node)
            queries.append(query)

        with Then("try to login"):
            for user in queries:
                actions.login(user=user)
                # pause()


@TestScenario
def different_sequences_starting_with_create(self):
    """Check different combinations of sequences of changing user's
    authentication methods."""
    self.context.model = models.Model()

    ways_to_create = []
    ways_to_alter = []

    with Given("define ways to create user with multiple authentication methods"):
        ways_to_create += ways_to_create_user()

    with And("define ways to change user's authentication methods"):
        ways_to_alter += ways_to_change()

    with And("define ways to add new authentication methods to existing user"):
        ways_to_alter += ways_to_add()

    with And("add reset authentication methods to new option"):
        ways_to_alter += ways_to_reset_to_new()

    combinations = list(
        product(ways_to_create, ways_to_alter, ways_to_alter, ways_to_alter)
    )

    if not self.context.stress:
        combinations = random.sample(combinations, 3000)

    with Pool(10) as executor:
        for i, combination in enumerate(combinations):
            Scenario(
                f"Sequence #{i}",
                test=check_sequence_of_actions,
                parallel=True,
                executor=executor,
            )(combination=combination)
        join()


@TestFeature
@Name("simple combinatorics")
def feature(self):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods.
    """
    Scenario(
        run=different_sequences_starting_with_create,
    )
