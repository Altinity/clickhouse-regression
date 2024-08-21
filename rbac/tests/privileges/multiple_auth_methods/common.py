from testflows.core import *
from testflows.combinatorics import combinations

from rbac.helper.common import *
from helpers.sql.create_user import CreateUser
import rbac.tests.privileges.multiple_auth_methods.actions as actions


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
bcrypt_hash = generate_bcrypt_hash(password=bcrypt_hash_password).replace("$", "\$")
bcrypt_hash_password_2 = "some_password_16"
bcrypt_hash_2 = generate_bcrypt_hash(password=bcrypt_hash_password_2).replace("$", "\$")

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
    self, user_name, password="", node=None, exitcode=None, message=None, expected=None, nodes=None
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
            settings=[("user", user_name), ("password", password)],
            exitcode=exitcode,
            message=message,
        )


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
def create_user_with_two_plaintext_passwords(self, user_name):
    """I create user with two plain text passwords"""

    user_auth_methods = [
        actions.partial(CreateUser.set_with_plaintext_password, password="123"),
        actions.partial(CreateUser.set_with_plaintext_password, password="456"),
    ]

    return actions.create_user(user_name=user_name, auth_methods=user_auth_methods)


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