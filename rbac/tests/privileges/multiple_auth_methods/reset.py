from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.tests.privileges.multiple_auth_methods.common import (
    create_user,
    generate_auth_combinations,
    authentication_methods_with_passwords,
    check_login,
    create_user_with_two_plaintext_passwords,
)
import rbac.tests.privileges.multiple_auth_methods.actions as actions
import rbac.tests.privileges.multiple_auth_methods.model as models

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_ResetAuthenticationMethods(
        "1.0"
    ),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_System_Users("1.0"),
)
def check_reset_to_new(self, auth_methods, node=None):
    """Check that auth methods are being reset correctly to the most recent one
    with different auth methods combinations."""
    node = node or self.context.node

    user_created = False

    with Given("create user with multiple authentication methods"):
        user_name = f"user_{getuid()}"
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
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

    if user_created:
        with When("reset authentication methods"):
            node.query(f"ALTER USER {user_name} RESET AUTHENTICATION METHODS TO NEW")

        with Then(
            "check that user can authenticate with only the most recently added authentication method"
        ):
            recent_password = auth_methods[-1][1]
            result = node.query(
                f"SELECT 1",
                settings=[("user", user_name), ("password", recent_password)],
            )
            assert result.output == "1", error()

        with And(
            "check that user can not authenticate with other methods that were reset"
        ):
            reset_passwords = [j[1] for j in auth_methods[:-1]]
            for password in reset_passwords:
                if password != recent_password:
                    node.query(
                        f"SELECT 1",
                        settings=[("user", user_name), ("password", password)],
                        exitcode=4,
                        message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
                    )

        with And(
            "check that changes in authentication methods are reflected in system.users table"
        ):
            auth_type = auth_methods[-1][0]
            system_auth_types_length = node.query(
                f"SELECT length(auth_type) FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
            ).output
            assert system_auth_types_length == "1", error()
            system_auth_type = node.query(
                f"SELECT auth_type[1] FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
            ).output
            if "hash" in auth_type:
                auth_type = auth_type.replace("hash", "password")
            assert system_auth_type in auth_type, error()


@TestScenario
@Name("check alter user reset auth methods")
def resetting_auth_methods(self):
    """Run test that check RESET AUTHENTICATION METHODS TO NEW with different auth methods combinations."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_reset_to_new,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_reset_to_new_v2(self, auth_methods, node=None):
    """Check that auth methods are being reset correctly to the most recent one
    with different auth methods combinations."""
    if node is None:
        node = self.context.node

    user_name = f"user_{getuid()}"
    self.context.behavior = []

    with Given("I have client"):
        self.context.client = actions.node_client()

    with And("I create user with two plain text passwords"):
        user = create_user_with_two_plaintext_passwords(user_name=user_name)

    with When("I alter user to change authentication methods"):
        altered_user = actions.alter_user(user=user, auth_methods=auth_methods)

    with And("I alter user to reset authentication methods"):
        actions.alter_user_reset_to_new(user=altered_user)

    with Then("I try to login"):
        check_login(user=user, altered_user=altered_user)


@TestScenario
@Name("resetting auth methods")
def resetting_auth_methods_v2(self):
    """Run test that check RESET AUTHENTICATION METHODS TO NEW with different auth methods combinations."""
    self.context.model = models.Model()
    node = self.context.node

    auth_methods_combinations = actions.alter_user_auth_combinations(max_length=2)

    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods_combinations):
            Scenario(
                f"#{num} {actions.names(auth_methods)}",
                test=check_reset_to_new_v2,
                parallel=True,
                executor=executor,
            )(node=node, auth_methods=auth_methods)
        join()


@TestFeature
@Name("reset authentication methods")
def feature(self, node="clickhouse1"):
    """Check support of ALTER USER RESET AUTHENTICATION METHODS TO NEW statement."""
    self.context.node = self.context.cluster.node(node)
    with Pool(2) as executor:
        Scenario(test=resetting_auth_methods, parallel=True, executor=executor)()
        # Scenario(test=resetting_auth_methods_v2, parallel=True, executor=executor)()
        join()
