from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import combinations

from rbac.helper.common import *
from helpers.sql.create_user import CreateUser
import rbac.tests.multiple_auth_methods.actions as actions
import rbac.tests.multiple_auth_methods.errors as errors


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
bcrypt_hash = generate_bcrypt_hash(password=bcrypt_hash_password).replace("$", r"\$")
bcrypt_hash_password_2 = "some_password_16"
bcrypt_hash_2 = generate_bcrypt_hash(password=bcrypt_hash_password_2).replace(
    "$", r"\$"
)

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
    f"bcrypt_hash BY '{bcrypt_hash}'": bcrypt_hash_password,
    f"bcrypt_hash BY '{bcrypt_hash_2}'": bcrypt_hash_password_2,
    # f"ssh_key BY KEY '{ssh_pub_key}' TYPE 'ssh-ed25519', KEY '{ssh_pub_key}' TYPE 'ssh-ed25519',",
    # "kerberos",
    # "kerberos REALM 'realm'",
    # "ssl_certificate CN 'mysite.com:user'",
    # "http SERVER 'http_server'",
    # "http SERVER 'http_server' SCHEME 'basic'",
    # "IDENTIFIED BY 'qwerty'"
    # "ldap SERVER 'server_name'",
}


def generate_auth_combinations(auth_methods_dict, max_length=2, with_replacement=False):
    auth_combinations = []
    for length in range(1, max_length + 1):
        auth_combinations.extend(
            combinations(
                auth_methods_dict.items(), length, with_replacement=with_replacement
            )
        )
    return auth_combinations


@TestStep(Then)
def execute_query(self, query, expected=None, node=None, exitcode=None, message=None):
    if node is None:
        node = self.context.node

    if expected is not None:
        exitcode, message = expected()

    r = node.query(query, exitcode=exitcode, message=message)
    return r.output


@TestStep(Then)
def login(
    self,
    user_name,
    password="",
    node=None,
    exitcode=None,
    message=None,
    expected=None,
    nodes=None,
    session_timezone=None,
):
    settings = [("user", user_name), ("password", password)]

    if node is None:
        node = self.context.node

    if exitcode is None:
        message = user_name

    if expected is not None:
        exitcode, message = expected()

    if session_timezone is not None:
        settings.append(("session_timezone", session_timezone))

    nodes = nodes or [node]

    for node in nodes:
        node.query(
            f"SELECT currentUser()",
            settings=settings,
            exitcode=exitcode,
            message=message,
        )


@TestStep(Then)
def login_ssh(
    self,
    user_name,
    ssh_key_file="",
    ssh_key_passphrase="",
    node=None,
    exitcode=None,
    message=None,
    expected=None,
    nodes=None,
):
    if node is None:
        node = self.context.node

    if exitcode is None:
        message = user_name

    if expected is not None:
        exitcode, message = expected()

    nodes = nodes or [node]

    for node in nodes:
        node.query(
            f"SELECT currentUser()",
            settings=[
                ("user", user_name),
                ("ssh-key-file", f"{ssh_key_file}"),
                ("ssh-key-passphrase", f"{ssh_key_passphrase}"),
            ],
            exitcode=exitcode,
            message=message,
        )


@TestStep(Given)
def check_timezone(self, timezone="GMT", node=None):
    """Check that the server timezone is set to specified value."""
    if node is None:
        node = self.context.node

    current_timezone = node.query(
        f"SELECT timezone() FORMAT TabSeparated"
    ).output.strip()
    assert current_timezone == timezone, error()


@TestStep(Given)
def change_server_settings(
    self,
    entries=None,
    setting=None,
    value=None,
    modify=False,
    restart=True,
    format=None,
    user=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    preprocessed_name="config.xml",
    node=None,
):
    """Create configuration file and add it to the server."""
    if entries is None:
        entries = {
            f"{setting}": f"{value}",
        }
    with By("converting config file content to xml"):
        config = create_xml_config_content(
            entries,
            "change_settings.xml",
            config_d_dir=config_d_dir,
            preprocessed_name=preprocessed_name,
        )
        if format is not None:
            for key, value in format.items():
                config.content = config.content.replace(key, value)

    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user, node=node)


@TestStep(Given)
def create_user_with_two_plaintext_passwords(self, user_name, client=None):
    """I create user with two plain text passwords"""

    user_auth_methods = [
        actions.partial(CreateUser.set_with_plaintext_password, password="123"),
        actions.partial(CreateUser.set_with_plaintext_password, password="456"),
    ]

    return actions.create_user(
        user_name=user_name, auth_methods=user_auth_methods, client=client
    )


@TestStep(Then)
def check_login(self, user, altered_user=None):
    """Check login with old and new authentication methods."""

    with Then("I try to login using old authentication methods"):
        actions.login(user=user)

    if altered_user:
        with And("I try to login using new authentication methods"):
            actions.login(user=altered_user)

        with And("I try to login with slightly invalid passwords"):
            actions.login_with_wrong_password(user=altered_user)

        with And("I try to login with slightly wrong username"):
            actions.login_with_wrong_username(user=altered_user)


@TestStep(Then)
def check_changes_reflected_in_system_table(
    self, user_name, correct_passwords, node=None
):
    """Check that changes in user's authentication methods are reflected in the system.users table."""
    if node is None:
        node = self.context.node

    with By("check the number of authentication methods in system.users table"):
        system_auth_types_length = node.query(
            f"SELECT length(auth_type) FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
        ).output

    with And(
        "check that number of correct passwords is equal to the number of authentication methods"
    ):
        if len(correct_passwords) > 0:
            assert system_auth_types_length == str(len(correct_passwords)), error()
        else:
            assert system_auth_types_length == "", error()

    with And(
        "check that auth methods from system.users are the same as in SHOW CREATE USER"
    ):
        if len(correct_passwords) > 0:
            create_user_command = f"SHOW CREATE USER {user_name} FORMAT TabSeparated"
            create_user_query_output = node.query(create_user_command).output

            for i in range(len(correct_passwords)):
                system_auth_type = node.query(
                    f"SELECT auth_type[{i+1}] FROM system.users WHERE name='{user_name}' FORMAT TabSeparated"
                ).output
                assert system_auth_type in create_user_query_output, error()
        else:
            exitcode, message = errors.no_user(user_name)()
            node.query(
                f"SHOW CREATE USER {user_name} FORMAT TabSeparated",
                exitcode=exitcode,
                message=message,
            )


@TestStep(Then)
def check_login_with_correct_and_wrong_passwords(
    self, user_name, wrong_passwords=[], correct_passwords=[], node=None
):
    """Validate user login."""
    if node is None:
        node = self.context.node

    for password in correct_passwords:
        login(user_name=user_name, password=password, node=node)

    for password in wrong_passwords:
        login(
            user_name=user_name,
            password=password,
            expected=errors.wrong_password(user_name),
            node=node,
        )


@TestStep(Then)
def check_login_with_correct_and_wrong_passwords_on_cluster(
    self, user_name, wrong_passwords, correct_passwords
):
    """Validate user login on all nodes."""
    for password in correct_passwords:
        login(user_name=user_name, password=password, nodes=self.context.nodes)

    for password in wrong_passwords:
        login(
            user_name=user_name,
            password=password,
            nodes=self.context.nodes,
            expected=errors.wrong_password(user_name),
        )
