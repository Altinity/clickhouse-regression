from testflows.core import *
from testflows.combinatorics import combinations

from functools import wraps

from helpers.common import getuid
from helpers.sql.create_user import CreateUser


def partial(func, *args, **keywords):
    @wraps(func)
    def newfunc(*fargs, **fkeywords):
        newkeywords = {**keywords, **fkeywords}
        return func(*args, *fargs, **newkeywords)

    return newfunc


def names(methods):
    """Return names of functions or methods."""
    return ",".join([method.__name__ for method in methods])


def generate_auth_combinations(auth_methods=None, max_length=3, with_replacement=True):
    """Generate combinations of authentication methods."""
    if auth_methods is None:
        auth_methods = [
            CreateUser.set_with_no_password,
            partial(CreateUser.set_by_password, password="foo1"),
            partial(CreateUser.set_by_password, password="foo2"),
            partial(CreateUser.set_with_plaintext_password, password="foo3"),
            partial(CreateUser.set_with_sha256_password, password="foo4"),
            partial(CreateUser.set_with_sha256_hash, password="foo4"),
            partial(
                CreateUser.set_with_sha256_hash_with_salt, password="foo4", salt="salt1"
            ),
            partial(CreateUser.set_with_double_sha1_password, password="foo5"),
            partial(CreateUser.set_with_double_sha1_hash, password="foo5"),
            partial(CreateUser.set_with_bcrypt_password, password="foo6"),
            partial(CreateUser.set_with_bcrypt_hash, password="foo6"),
        ]
    auth_combinations = []

    for length in range(1, max_length + 1):
        auth_combinations.extend(
            combinations(auth_methods, length, with_replacement=with_replacement)
        )

    return auth_combinations


@TestStep(Given)
def node_client(self, node=None):
    """Create a client for the node."""
    if node is None:
        node = self.context.node

    with node.client() as client:
        yield client


@TestStep(Given)
def create_user(
    self,
    user_name=None,
    auth_methods=None,
    client=None,
):
    """Create user with given name and authentication methods.
    If name is not provided, it will be generated.
    """
    if client is None:
        client = self.context.client

    if user_name is None:
        user_name = "user_" + getuid()

    query = CreateUser().set_username(user_name).set_identified()

    for i, auth_method in enumerate(auth_methods):
        query = auth_method(query)

    try:
        r = client.query(str(query), no_checks=True)
        # FIXME: add model.expect
        yield query

    finally:
        with Finally("drop the user if exists"):
            client.query(f"DROP USER IF EXISTS {user_name}")


@TestStep(Then)
def check_login(self, user: CreateUser, node=None):
    """Check user login with valid and invalid passwords."""
    if node is None:
        node = self.context.node

    for auth_method in user.identification:
        for username in user.usernames:
            if auth_method.method == "no_password":
                password = ""
            else:
                password = auth_method.password
            r = node.query(
                f"SELECT current_user()",
                settings=[("user", username.name), ("password", password)],
                no_checks=True,
            )
            # FIXME: add model.expect
            # FIXME: I need a state for login {user, password, hostname, ip}
