import random

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


def generate_auth_combinations(auth_methods_dict, max_length=2, with_replacement=True):
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
    self, user_name, password="", node=None, exitcode=None, message=None, expected=None
):
    if node is None:
        node = self.context.node

    if exitcode is None:
        message = user_name

    if expected is not None:
        exitcode, message = expected()

    node.query(
        f"SELECT currentUser()",
        settings=[("user", user_name), ("password", password)],
        exitcode=exitcode,
        message=message,
    )
