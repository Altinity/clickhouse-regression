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

random.seed(42)

@TestStep(Given)
def create_user_auth_methods_combinations(self):
    """Combinations of CREATE USER with different authentication methods and different expiration dates."""
    with By("defining two dates: expired and future"):
        future_date = define(
            "future date", self.context.node.query(f"SELECT now() + 24 * 3600").output
        )
        expired_date = define(
            "expired date", self.context.node.query(f"SELECT now() - 24 * 3600").output
        )

    create_auth_methods = [
        actions.partial(
            CreateUser.set_by_password, password="foo1", valid_until=future_date
        ),
        actions.partial(
            CreateUser.set_by_password, password="foo2", valid_until=expired_date
        ),
        actions.partial(
            CreateUser.set_with_plaintext_password,
            password="foo3",
            valid_until=future_date,
        ),
        actions.partial(
            CreateUser.set_with_plaintext_password,
            password="foo4",
            valid_until=expired_date,
        ),
        actions.partial(
            CreateUser.set_with_sha256_password,
            password="foo5",
            valid_until=future_date,
        ),
        actions.partial(
            CreateUser.set_with_sha256_password,
            password="foo6",
            valid_until=expired_date,
        ),
        # actions.partial(
        #     CreateUser.set_with_sha256_hash, password="foo7", valid_until=future_date
        # ),
        # actions.partial(
        #     CreateUser.set_with_sha256_hash, password="foo8", valid_until=expired_date
        # ),
        # actions.partial(
        #     CreateUser.set_with_sha256_hash_with_salt,
        #     password="foo9",
        #     salt="salt1",
        #     valid_until=future_date,
        # ),
        # actions.partial(
        #     CreateUser.set_with_sha256_hash_with_salt,
        #     password="foo10",
        #     salt="salt1",
        #     valid_until=expired_date,
        # ),
        actions.partial(
            CreateUser.set_with_double_sha1_password,
            password="foo11",
            valid_until=future_date,
        ),
        actions.partial(
            CreateUser.set_with_double_sha1_password,
            password="foo12",
            valid_until=expired_date,
        ),
        actions.partial(
            CreateUser.set_with_double_sha1_hash,
            password="foo13",
            valid_until=future_date,
        ),
        actions.partial(
            CreateUser.set_with_double_sha1_hash,
            password="foo14",
            valid_until=expired_date,
        ),
        # actions.partial(
        #     CreateUser.set_with_bcrypt_password,
        #     password="foo15",
        #     valid_until=future_date,
        # ),
        # actions.partial(
        #     CreateUser.set_with_bcrypt_password,
        #     password="foo16",
        #     valid_until=expired_date,
        # ),
        # actions.partial(
        #     CreateUser.set_with_bcrypt_hash, password="foo17", valid_until=future_date
        # ),
        # actions.partial(
        #     CreateUser.set_with_bcrypt_hash, password="foo18", valid_until=expired_date
        # ),
    ]

    auth_methods_combinations = actions.create_user_auth_combinations(
        max_length=2, auth_methods=create_auth_methods
    )
    auth_methods_combinations.append([CreateUser.set_with_no_password])

    return auth_methods_combinations


@TestStep(Given)
def alter_user_auth_methods_combinations(self):
    """Combinations of ALTER USER with different authentication methods and different expiration dates."""
    with By("defining two dates: expired and future"):
        future_date = define(
            "future date", self.context.node.query(f"SELECT now() + 24 * 3600").output
        )
        expired_date = define(
            "expired date", self.context.node.query(f"SELECT now() - 24 * 3600").output
        )

    alter_auth_methods = [
        actions.partial(
            AlterUser.set_by_password, password="foo21", valid_until=future_date
        ),
        actions.partial(
            AlterUser.set_by_password, password="foo22", valid_until=expired_date
        ),
        actions.partial(
            AlterUser.set_with_plaintext_password,
            password="foo23",
            valid_until=future_date,
        ),
        actions.partial(
            AlterUser.set_with_plaintext_password,
            password="foo24",
            valid_until=expired_date,
        ),
        actions.partial(
            AlterUser.set_with_sha256_password,
            password="foo25",
            valid_until=future_date,
        ),
        actions.partial(
            AlterUser.set_with_sha256_password,
            password="foo26",
            valid_until=expired_date,
        ),
        # actions.partial(
        #     AlterUser.set_with_sha256_hash, password="foo27", valid_until=future_date
        # ),
        # actions.partial(
        #     AlterUser.set_with_sha256_hash, password="foo28", valid_until=expired_date
        # ),
        # actions.partial(
        #     AlterUser.set_with_sha256_hash_with_salt,
        #     password="foo29",
        #     salt="salt1",
        #     valid_until=future_date,
        # ),
        # actions.partial(
        #     AlterUser.set_with_sha256_hash_with_salt,
        #     password="foo210",
        #     salt="salt1",
        #     valid_until=expired_date,
        # ),
        actions.partial(
            AlterUser.set_with_double_sha1_password,
            password="foo211",
            valid_until=future_date,
        ),
        actions.partial(
            AlterUser.set_with_double_sha1_password,
            password="foo212",
            valid_until=expired_date,
        ),
        actions.partial(
            AlterUser.set_with_double_sha1_hash,
            password="foo213",
            valid_until=future_date,
        ),
        actions.partial(
            AlterUser.set_with_double_sha1_hash,
            password="foo214",
            valid_until=expired_date,
        ),
        # actions.partial(
        #     AlterUser.set_with_bcrypt_password,
        #     password="foo215",
        #     valid_until=future_date,
        # ),
        # actions.partial(
        #     AlterUser.set_with_bcrypt_password,
        #     password="foo216",
        #     valid_until=expired_date,
        # ),
        # actions.partial(AlterUser.set_with_bcrypt_hash, password="foo217", valid_until=future_date),
        # actions.partial(AlterUser.set_with_bcrypt_hash, password="foo218", valid_until=expired_date),
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

    queries = []

    for i, action in enumerate(combination):
        with When(f"I perform action {i} {action.__name__}"):
            query = action(usernames=usernames, client=node)
            if not isinstance(query, DropUser):
                queries.append(query)

        with Then("try to login"):
            for user in queries:
                actions.login(user=user)


@TestScenario
@Name("different combinations of actions")
def different_combinations(self, number_of_actions=3):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods
    and different expiration dates for each method.
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
        combinations = random.sample(combinations, 10000)

    with Pool(10) as executor:
        for i, combination in enumerate(combinations):
            Scenario(
                f"#{i}", test=combination_of_actions, parallel=True, executor=executor
            )(combination=combination)
        join()


@TestFeature
@Name("valid until clause combinatorics")
@Requirements()
def feature(self):
    """Check `VALID UNTIL` clause in `CREATE USER` and `ALTER USER` statements."""
    Scenario(run=different_combinations)
