from testflows.core import *
from testflows.asserts import error

from rbac.tests.privileges.multiple_auth_methods.common import (
    create_user,
    generate_auth_combinations,
    authentication_methods_with_passwords,
)
from rbac.requirements import *

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_ResetAuthenticationMethods(
        "1.0"
    ),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_System_Users("1.0"),
)
def check_reset_authentication_methods(self, auth_methods, node=None):
    """Check that ALTER USER RESET AUTHENTICATION METHODS TO NEW resets all authentication methods
    except the most recent added one."""
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
            password = auth_methods[-1][1]
            result = node.query(
                f"SELECT 1", settings=[("user", user_name), ("password", password)]
            )
            assert result.output == "1", error()

        with And(
            "check that user can not authenticate with other methods that were reset"
        ):
            reset_passwords = [j[1] for j in auth_methods[:-1]]
            for password in reset_passwords:
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


@TestFeature
@Name("reset authentication methods")
def feature(self, node="clickhouse1"):
    """Check support of ALTER USER RESET AUTHENTICATION METHODS TO NEW statement."""
    self.context.node = self.context.cluster.node(node)
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
        with_replacement=False,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_reset_authentication_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()
