import threading
import random

from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from helpers.sql.create_user import Username
from helpers.sql.drop_user import DropUser

from rbac.requirements import *

import rbac.tests.multiple_auth_methods.actions as actions
import rbac.tests.multiple_auth_methods.model as models
from rbac.tests.multiple_auth_methods.combinations import (
    ways_to_create_user,
    ways_to_change,
    ways_to_add,
    ways_to_reset_to_new,
    ways_to_drop,
)

random.seed(42)


@TestStep(Then)
def check_server_is_running(self, node=None):
    """Check if server is running after all actions."""
    current_user = node.query(f"SELECT current_user()").output
    assert current_user == "default", error()
    users = node.query(f"SHOW USERS").output.splitlines()
    if len(users) > 1:
        for user in users:
            node.query(f"SHOW CREATE USER {user}", ignore_exception=True)


@TestStep(Given)
def run_action_in_parallel(self, action, usernames, node=None):
    """Run action."""
    if node is None:
        node = self.context.node

    return action(usernames=usernames, client=node)


@TestScenario
def combination_of_actions(self, combination, node=None):
    """Check combination of actions."""
    self.context.behavior_appending_lock = threading.Lock()
    self.context.behavior = []
    usernames = [Username(name="user_" + getuid())]
    queries = []

    if node is None:
        node = self.context.node

    with Given("run statements of first action in parallel"):
        with Pool(5) as executor:
            for action in combination[0]:
                Step(test=run_action_in_parallel, parallel=True, executor=executor)(
                    action=action, usernames=usernames
                )
            join()

    with And("run other statements one by one"):
        for i, action in enumerate(combination[1:]):
            with By(f"I perform action {i} {action.__name__}"):
                query = action(usernames=usernames, client=node)
                if not isinstance(query, DropUser):
                    queries.append(query)

    with Then("check if server is running"):
        check_server_is_running(node=node)


@TestScenario
@Name("different combinations of actions with first action in parallel")
def action_one_in_parallel(self, number_of_parallel_actions=2):
    """Check different combinations of sequences of creating,
    altering and dropping users with multiple authentication methods
    when first action is executed in parallel.
    """
    ways = []

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

    with When("create first set of actions, which will be executed in parallel"):
        ways_for_first_action = product(ways, repeat=number_of_parallel_actions)

    with And(
        "create all possible combinations of three actions",
        description=(
            "First action is executed in parallel, "
            "the rest of the actions are executed one by one."
        ),
    ):
        combinations = list(
            product(ways_for_first_action, ways, ways)
        )  # 279841 combinations
        if not self.context.stress:
            combinations = random.sample(combinations, 100)

    with Pool(5) as executor:
        for i, combination in enumerate(combinations):
            Scenario(
                f"#{i}", test=combination_of_actions, parallel=True, executor=executor
            )(
                combination=combination,
            )
        join()


@TestFeature
@Name("parallel modification")
def feature(self):
    """Check that different combinations of sequences of creating, altering and
    dropping users with multiple authentication methods are working correctly
    when executed in parallel."""
    self.context.model = models.DummyModel()
    Scenario(run=action_one_in_parallel)
