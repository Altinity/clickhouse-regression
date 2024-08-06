from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations

from rbac.requirements import *
from rbac.helper.common import *

from helpers.common import getuid


plaintext_password = "some_password_1"
plaintext_password_2 = "some_password_2"
sha256_password = "some_password_3"
sha256_password_2 = "some_password_4"
sha256_hash_password = "some_password_5"
sha256_hash = generate_hashed_password(password=sha256_hash_password)
sha256_hash_password_2 = "some_password_6"
sha256_hash_2 = generate_hashed_password(password=sha256_hash_password_2)
sha256_hash_salt_password = "some_password_7"
salt, sha256_hash_salt = generate_hashed_password_with_salt(
    password=sha256_hash_salt_password
)
sha256_hash_salt_password_2 = "some_password_8"
salt_2, sha256_hash_salt_2 = generate_hashed_password_with_salt(
    password=sha256_hash_salt_password_2
)
double_sha1_password = "some_password_9"
double_sha1_password_2 = "some_password_10"
double_sha1_hash_password = "some_password_11"
double_sha1_hash = generate_double_hashed_password(password=double_sha1_hash_password)
double_sha1_hash_password_2 = "some_password_12"
double_sha1_hash_2 = generate_double_hashed_password(
    password=double_sha1_hash_password_2
)
bcrypt_password = "some_password_13"
bcrypt_password_2 = "some_password_14"
bcrypt_hash_password = "some_password_15"
bcrypt_hash = generate_bcrypt_hash(password=bcrypt_hash_password)
bcrypt_hash_password_2 = "some_password_16"
bcrypt_hash_2 = generate_bcrypt_hash(password=bcrypt_hash_password_2)

authentication_methods_with_passwords = {
    "no_password": "",
    f"plaintext_password BY '{plaintext_password}'": plaintext_password,
    f"plaintext_password BY '{plaintext_password_2}'": plaintext_password_2,
    f"sha256_password BY '{sha256_password}'": sha256_password,
    f"sha256_password BY '{sha256_password_2}'": sha256_password_2,
    f"sha256_hash BY '{sha256_hash}'": sha256_hash_password,
    f"sha256_hash BY '{sha256_hash_2}'": sha256_hash_password_2,
    f"sha256_hash BY '{sha256_hash_salt}' SALT '{salt}'": sha256_hash_salt_password,
    f"sha256_hash BY '{sha256_hash_salt_2}' SALT '{salt_2}'": sha256_hash_salt_password_2,
    f"double_sha1_password BY '{double_sha1_password}'": double_sha1_password,
    f"double_sha1_password BY '{double_sha1_password_2}'": double_sha1_password_2,
    f"double_sha1_hash BY '{double_sha1_hash}'": double_sha1_hash_password,
    f"double_sha1_hash BY '{double_sha1_hash_2}'": double_sha1_hash_password_2,
    f"bcrypt_password BY '{bcrypt_password}'": bcrypt_password,
    f"bcrypt_password BY '{bcrypt_password_2}'": bcrypt_password_2,
    # f"bcrypt_hash BY '$2a$12$6ioB1bATbU/GFVDi35HWiuMwi7.yCiFBGcRSmHdYMtsv9NuOT0TUS'": bycrypt_hash_password,
    # f"ssh_key BY KEY '{ssh_pub_key}' TYPE 'ssh-ed25519', KEY '{ssh_pub_key}' TYPE 'ssh-ed25519',",
    # "kerberos",
    # "kerberos REALM 'realm'",
    # "ssl_certificate CN 'mysite.com:user'",
    # "http SERVER 'http_server'",
    # "http SERVER 'http_server' SCHEME 'basic'",
    # "IDENTIFIED BY 'qwerty'"
    # "ldap SERVER 'server_name'",
}


def generate_auth_combinations(auth_methods_dict, max_length=3, with_replacement=True):
    auth_combinations = []
    for length in range(1, max_length + 1):
        auth_combinations.extend(
            combinations(
                auth_methods_dict.items(), length, with_replacement=with_replacement
            )
        )
    return auth_combinations


@TestScenario
def check_create_user_with_multiple_auth_methods(self, auth_methods, node=None):
    """Check that all authentication methods can be added to the user."""
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


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser_NoPassword("1.0"),
)
def create_user_with_multiple_auth_methods(self):
    """Check that user can be created with multiple authentication methods."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(3) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_create_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
def check_alter_user_with_multiple_auth_methods(self, auth_methods, node=None):
    """Check that alter user with multiple authentication methods clears previous methods
    and sets new ones listed in the query."""
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
        ] + ["123", "456"]

    with And("create user with two plain text passwords"):
        user_name = f"user_{getuid()}"
        identified = f"plaintext_password BY '123', plaintext_password BY '456'"
        create_user(user_name=user_name, identified=identified)

    with When("alter user with multiple authentication methods"):
        user_altered = False
        if "no_password" in auth_methods_string and len(auth_methods) > 1:
            node.query(
                f"ALTER USER {user_name} IDENTIFIED WITH {auth_methods_string}",
                exitcode=36,
                message="DB::Exception: NO_PASSWORD Authentication method cannot co-exist with other authentication methods.",
            )
        else:
            node.query(f"ALTER USER {user_name} IDENTIFIED WITH {auth_methods_string}")
            user_altered = True

    with Then(
        "check that user can authenticate with correct passwords and can not authenticate with wrong passwords"
    ):
        if user_altered:
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
        else:
            for passwords in ["123", "456"]:
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", passwords)],
                )
            for passwords in authentication_methods_with_passwords.values():
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", passwords)],
                    exitcode=4,
                    message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
                )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AlterUser("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AlterUser_NoPassword("1.0"),
)
def alter_user_with_multiple_auth_methods(self):
    """Check that user can be altered with multiple authentication methods."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(3) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_alter_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified("1.0"),
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AddIdentified_NoPassword("1.0"),
)
def check_add_identified(self, auth_methods, node=None):
    """Check that one or more authentication methods can be added to the existing user."""
    if node is None:
        node = self.context.node

    with Given("create user with one authentication method"):
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


@TestScenario
def add_identified_with_multiple_auth_methods(self):
    """Check that one or more authentication methods can be added to the existing user."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
    )
    with Pool(3) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_add_identified,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_ResetAuthenticationMethods("1.0")
)
def check_reset_authentication_methods(self, auth_methods, node=None):
    """Check that ALTER USER RESET AUTHENTICATION METHODS TO NEW resets all authentication methods
    and  keeps the most recent added one."""
    if node is None:
        node = self.context.node

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
            "check that user can authenticate with only the most recent added method"
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


@TestScenario
def reset_authentication_methods(self):
    """Check that ALTER USER RESET AUTHENTICATION METHODS TO NEW resets all authentication methods
    and  keeps the most recent added one."""
    auth_methods = generate_auth_combinations(
        auth_methods_dict=authentication_methods_with_passwords,
        with_replacement=False,
    )
    with Pool(3) as executor:
        for num, auth_methods in enumerate(auth_methods):
            Scenario(
                f"{num}",
                test=check_reset_authentication_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("multiple authentication methods")
def feature(self, node="clickhouse1"):
    """Check support of multiple authentication methods."""
    self.context.node = self.context.cluster.node(node)

    with Pool(4) as executor:
        Scenario(
            test=create_user_with_multiple_auth_methods,
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=alter_user_with_multiple_auth_methods, parallel=True, executor=executor
        )()
        Scenario(
            test=add_identified_with_multiple_auth_methods,
            parallel=True,
            executor=executor,
        )()
        Scenario(test=reset_authentication_methods, parallel=True, executor=executor)()
        join()
