from testflows.core import *
from testflows.combinatorics import product

from rbac.requirements import *
from rbac.helper.common import *

from helpers.common import getuid


plaintext_password = "some_password_1"
sha256_password = "some_password_2"
sha256_hash_password = "some_password_3"
sha256_hash = generate_hashed_password(password=sha256_hash_password)
sha256_hash_salt_password = "some_password_4"
salt, sha256_hash_salt = generate_hashed_password_with_salt(
    password=sha256_hash_salt_password
)
double_sha1_password = "some_password_5"
double_sha1_hash_password = "some_password_6"
double_sha1_hash = generate_double_hashed_password(password=double_sha1_hash_password)
bycrypt_password = "some_password_7"
bycrypt_hash_password = "some_password_8"
bcrypt_hash = generate_bcrypt_hash(password=bycrypt_hash_password)

authentication_methods_with_passwords = {
    "no_password": "",
    f"plaintext_password BY '{plaintext_password}'": plaintext_password,
    f"sha256_password BY '{sha256_password}'": sha256_password,
    f"sha256_hash BY '{sha256_hash}'": sha256_hash_password,
    f"sha256_hash BY '{sha256_hash_salt}' SALT '{salt}'": sha256_hash_salt_password,
    f"double_sha1_password BY '{double_sha1_password}'": double_sha1_password,
    f"double_sha1_hash BY '{double_sha1_hash}'": double_sha1_hash_password,
    f"bcrypt_password BY '{bycrypt_password}'": bycrypt_password,
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


@TestScenario
def check_create_user_with_multiple_auth_methods(self, auth_methods, node=None):
    """Check that all authentication methods can be added to the user."""
    if node is None:
        node = self.context.node

    with Given("concatenate authentication methods"):
        auth_methods_string = ", ".join(j[0] for j in auth_methods)
        note(auth_methods_string)

    with And("create list of correct and wrong passwords for authentication"):
        correct_passwords = [j[1] for j in auth_methods if j[1]]
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
            for password in correct_passwords:
                node.query(
                    f"SELECT 1", settings=[("user", user_name), ("password", password)]
                )
            for password in wrong_passwords:
                node.query(
                    f"SELECT 1",
                    settings=[("user", user_name), ("password", password)],
                    exitcode=4,
                    message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
                )


@TestScenario
@Requirements(RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_CreateUser("1.0"))
def create_user_with_multiple_auth_methods(self):
    """Check that user can be created with multiple authentication methods."""
    with Pool(5) as executor:
        for num, auth_methods in enumerate(
            product(authentication_methods_with_passwords.items(), repeat=3)
        ):
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
        correct_passwords = [j[1] for j in auth_methods if j[1]]
        wrong_passwords = [
            j
            for j in authentication_methods_with_passwords.values()
            if j not in correct_passwords
        ] + ["123", "456"]

    with And("create user with two plain text passwords"):
        user_name = f"user_{getuid()}"
        identified = (
            f"IDENTIFIED WITH plaintext_password BY '123', plaintext_password BY '456'"
        )
        create_user(user_name=user_name, identified=identified)

    with When("alter user with multiple authentication methods"):
        node.query(f"ALTER USER {user_name} IDENTIFIED WITH {auth_methods_string}")

    with Then(
        "check that user can authenticate with correct passwords and can not authenticate with wrong passwords"
    ):
        for password in correct_passwords:
            node.query(
                f"SELECT 1", settings=[("user", user_name), ("password", password)]
            )
        for password in wrong_passwords:
            node.query(
                f"SELECT 1",
                settings=[("user", user_name), ("password", password)],
                exitcode=4,
                message=f"DB::Exception: {user_name}: Authentication failed: password is incorrect, or there is no user with such name.",
            )


@TestScenario
@Requirements(RQ_SRS_006_RBAC_User_MultipleAuthenticationMethods_AlterUser("1.0"))
def alter_user_with_multiple_auth_methods(self):
    """Check that user can be altered with multiple authentication methods."""
    with Pool(5) as executor:
        for num, auth_methods in enumerate(
            product(authentication_methods_with_passwords.items(), repeat=3)
        ):
            Scenario(
                f"{num}",
                test=check_alter_user_with_multiple_auth_methods,
                parallel=True,
                executor=executor,
            )(auth_methods=auth_methods)
        join()


@TestFeature
@Name("multiple authentication methods")
def feature(self, node="clickhouse1"):
    """Check support of multiple authentication methods."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=create_user_with_multiple_auth_methods)
    Scenario(run=alter_user_with_multiple_auth_methods)
