from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.tests.privileges.multiple_auth_methods.common import (
    create_user,
    generate_auth_combinations,
    authentication_methods_with_passwords,
    check_login,
    create_user_with_two_plaintext_passwords,
    add_identified,
)
import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified_NoPassword("1.0"),
)
def check_adding_auth_methods(self, auth_methods, node=None):
    """Check that one or more authentication methods can be added to the user
    using ALTER USER ADD IDENTIFIED statement."""
    node = node or self.context.node

    with Given("create user with one plaintext password authentication method"):
        user_name = f"user_{getuid()}"
        create_user(user_name=user_name, identified="plaintext_password BY '123'")

    with When("add one or more authentication methods"):
        user_altered = False
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        if "no_password" in auth_methods_string:
            exitcode = 36
            message = "DB::Exception: NO_PASSWORD Authentication method cannot co-exist with other authentication methods."
            if len(auth_methods) == 1:  # auth_methods_string == "no_password"
                message = "DB::Exception: The authentication method 'no_password' cannot be used with the ADD keyword."
            add_identified(
                user=user_name,
                identified=auth_methods_string,
                exitcode=exitcode,
                message=message,
            )
        else:
            add_identified(user=user_name, identified=auth_methods_string)
            user_altered = True

    with And("create a list of correct and wrong passwords for authentication"):
        correct_passwords = [j[1] for j in auth_methods] + ["123"]
        wrong_passwords = [
            j
            for j in authentication_methods_with_passwords.values()
            if j not in correct_passwords
        ]

    with Then("check that user can authenticate with correct passwords"):
        if user_altered:
            for password in correct_passwords:
                result = node.query(
                    f"SELECT 1", settings=[("user", user_name), ("password", password)]
                )
                assert result.output == "1", error()
        else:
            result = node.query(
                f"SELECT 1", settings=[("user", user_name), ("password", "123")]
            )
            assert result.output == "1", error()

    with And("check that user can not authenticate with wrong passwords"):
        if user_altered:
            for password in wrong_passwords:
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", password)],
                    exitcode=4,
                    message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
                )
        else:
            for password in authentication_methods_with_passwords.values():
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", password)],
                    exitcode=4,
                    message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
                )

    with And(
        "check that changes in authentication methods are reflected in system.users table"
    ):
        if user_altered:
            auth_types = [
                j[0].split(" ")[0].replace("hash", "password") for j in auth_methods
            ] + ["plaintext_password"]
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
        else:
            system_auth_types_length = node.query(
                f"SELECT length(auth_type) FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
            ).output
            assert system_auth_types_length == "1", error()
            system_auth_type = node.query(
                f"SELECT auth_type[1] FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
            ).output
            assert system_auth_type == "plaintext_password", error()


@TestScenario
@Name("adding auth methods")
def adding_auth_methods(self):
    """Check that multiple authentication methods can be added to a user."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_adding_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_adding_auth_methods_v2(self, auth_methods, node=None):
    """Check adding new authentication methods."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to add authentication methods"):
        altered_user = actions.alter_user_add(user=user, auth_methods=auth_methods)

    with Then("I try to login"):
        check_login(user=user, altered_user=altered_user)


@TestScenario
@Name("adding auth methods v2")
def adding_auth_methods_v2(self):
    """Check that multiple authentication methods can be added to a user."""
    self.context.model = models.Model()
    node = self.context.node

    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"#{num} {actions.names(auth_methods)}",
                test=check_adding_auth_methods_v2,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()


@TestFeature
@Name("alter add identified")
def feature(self):
    """Check support of ALTER USER ADD IDENTIFIED statement with one or multiple
    authentication methods."""
    with Pool(2) as executor:
        Scenario(test=adding_auth_methods, parallel=True, executor=executor)()
        # Scenario(test=adding_auth_methods_v2, parallel=True, executor=executor)()
        join()
