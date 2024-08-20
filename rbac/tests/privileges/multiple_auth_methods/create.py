from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.tests.privileges.multiple_auth_methods.common import (
    create_user,
    generate_auth_combinations,
    authentication_methods_with_passwords,
)
import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models

from helpers.common import getuid


# FIXME: add test to check login with another user's password
@TestScenario
def create_user_with_multiple_auth_methods_v2(self, auth_methods, node=None):
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

    with And("I try to login with slightly wrong password"):
        actions.login_with_wrong_password(user=user)

    with And("I try to login with slightly wrong username"):
        actions.login_with_wrong_username(user=user)


@TestScenario
@Name("check create user with multiple auth methods v2")
def check_create_user_v2(self, node=None):
    """Run create user with multiple auth methods test with all combinations of auth methods."""
    self.context.model = models.Model()

    if node is None:
        node = self.context.node

    auth_methods_combinations = actions.create_user_auth_combinations(max_length=2)

    with Pool(5) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"{num} {actions.names(auth_methods)}",
                test=create_user_with_multiple_auth_methods_v2,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()


@TestScenario
def create_user_with_multiple_auth_methods(self, auth_methods, node=None):
    """Check that user can be created with multiple authentication methods."""
    if node is None:
        node = self.context.node

    with Given("concatenate authentication methods"):
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        note(auth_methods_string)

    with And("create list of correct and wrong passwords for authentication"):
        correct_passwords = [j[1] for j in auth_methods]
        wrong_passwords = [
            j
            for j in authentication_methods_with_passwords.values()
            if j not in correct_passwords
        ]

    with When("create user with multiple authentication methods"):
        user_name = f"user_{getuid()}"
        user_created = False
        if "no_password" in auth_methods_string and len(auth_methods) > 1:
            create_user(
                user_name=user_name,
                identified=auth_methods_string,
                exitcode=36,
                message="DB::Exception: NO_PASSWORD Authentication method cannot co-exist with other authentication methods.",
            )
        else:
            create_user(user_name=user_name, identified=auth_methods_string)
            user_created = True

    with Then(
        "check that user can authenticate with correct passwords and can not authenticate with wrong passwords"
    ):
        if user_created:
            if "no_password" in auth_methods_string:
                exitcode, message = None, None
            else:
                exitcode = 4
                message = f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name."

            for password in correct_passwords:
                node.query(
                    f"SELECT 1", settings=[("user", user_name), ("password", password)]
                )
            for password in wrong_passwords:
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", password)],
                    exitcode=exitcode,
                    message=message,
                )

    with And(
        "check that creating a user with multiple authentication methods updates the system.users table"
    ):
        if user_created:
            auth_types = [
                j[0].split(" ")[0].replace("hash", "password") for j in auth_methods
            ]
            system_auth_types_length = node.query(
                f"SELECT length(auth_type) FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
            ).output
            assert system_auth_types_length == str(len(auth_types)), error()
            system_auth_types = []
            for i in range(int(system_auth_types_length)):
                system_auth_type = node.query(
                    f"SELECT auth_type[{i+1}] FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
                ).output
                system_auth_types.append(system_auth_type)

            assert sorted(system_auth_types) == sorted(auth_types), error()


@TestScenario
@Name("check create user with multiple auth methods")
def check_create_user_with_multiple_auth_methods(self):
    """Run create user with multiple auth methods test with all combinations of auth methods."""
    auth_methods_combinations = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(6) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"{num}",
                test=create_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("create user with multiple auth methods")
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser_NoPassword("1.0"),
)
def feature(self):
    """Check that user can be created with multiple authentication methods."""
    with Pool(2) as executor:
        # Scenario(test=check_create_user_v2, parallel=True, executor=executor)()
        Scenario(
            test=check_create_user_with_multiple_auth_methods,
            parallel=True,
            executor=executor,
        )()
        join()
