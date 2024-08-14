from rbac.tests.privileges.multiple_auth_methods.common import *


@TestScenario
def check_create_user_with_multiple_auth_methods(self, auth_methods, node=None):
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


@TestFeature
@Name("create")
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser_NoPassword("1.0"),
)
def feature(self, node="clickhouse1"):
    """Check that user can be created with multiple authentication methods."""
    self.context.node = self.context.cluster.node(node)
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(4) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_create_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()
