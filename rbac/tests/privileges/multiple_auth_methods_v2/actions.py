from testflows.core import *
from testflows.combinatorics import combinations

from functools import wraps

from helpers.common import getuid
from helpers.sql.create_user import CreateUser
from helpers.sql.drop_user import DropUser
from helpers.sql.select import Select


def partial(func, *args, **keywords):
    """Create a new function with partial application of the given arguments and keywords."""

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


@TestStep(When)
def client_query(self, query, client=None, **kwargs):
    """Execute query on the client. Add query to the behavior.
    Use model to check the result."""

    if client is None:
        client = self.context.client

    r = client.query(str(query), no_checks=True, **kwargs)
    query.add_result(r)
    self.context.behavior.append(query)

    Then(test=self.context.model.expect())(r=r)


@TestStep(When)
def node_query(self, query, node=None, **kwargs):
    """Execute query on the node. Add query to the behavior.
    Use model to check the result."""

    if node is None:
        node = self.context.node

    r = node.query(str(query), no_checks=True, **kwargs)
    query.add_connection_options(kwargs.pop("settings", None))
    query.add_result(r)
    self.context.behavior.append(query)

    Then(test=self.context.model.expect())(r=r)


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

    for auth_method in auth_methods:
        query = auth_method(query)

    try:
        client_query(query=query, client=client)
        yield query
    finally:
        with Finally("drop the user if exists"):
            query = DropUser().set_if_exists().set_username(user_name)
            client_query(query=query, client=client)


@TestStep(Then)
def successful_login(self, user: CreateUser, node=None):
    """Check user can login with valid passwords."""

    if node is None:
        node = self.context.node

    for auth_method in user.identification:
        for username in user.usernames:
            password = auth_method.password
            node_query(
                query=Select().set_query("SELECT current_user()"),
                settings=[("user", username.name), ("password", password or "")],
            )


@TestStep(Then)
def wrong_password_login(self, user: CreateUser, node=None):
    """Check user trying to login with invalid passwords."""

    if node is None:
        node = self.context.node

    for auth_method in user.identification:
        for username in user.usernames:
            password = (auth_method.password or "") + "1"
            node_query(
                query=Select().set_query(f"SELECT current_user()"),
                settings=[("user", username.name), ("password", password)],
            )


# FIXME: try to login with old password after changing it
# FIXME: try to login with password for a different user
# FIXME: try to login with valid password but invalid username


@TestStep(Then)
def login(self, user: CreateUser, node=None):
    """Check user trying to login with valid and invalid passwords."""

    successful_login(user=user, node=node)
    wrong_password_login(user=user, node=node)


@TestStep(Then)
def expect_ok(self, r):
    """Expect the query to be successful."""

    # assert r.exitcode == 0, f"unexpected exitcode {r.exitcode}"
    assert (
        "DB::Exception" not in r.output
    ), f"unexpected 'DB::Exception' in '{r.output}'"


@TestStep(Then)
def expect_error(self, r, exitcode, message):
    """Expect given exitcode and message in the output."""

    # assert r.exitcode == exitcode, f"expected exitcode {exitcode} but got {r.exitcode}"
    assert "DB::Exception" in r.output, f"expected 'DB::Exception' in '{r.output}'"
    assert message in r.output, f"expected '{message}' in '{r.output}'"


@TestStep(Then)
def expect_no_password_auth_cannot_coexist_with_others_error(self, r):
    """Expect NO_PASSWORD Authentication method cannot co-exist with other authentication methods error."""

    exitcode = 36
    message = "NO_PASSWORD Authentication method cannot co-exist with other authentication methods."
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_no_password_cannot_be_used_with_add_keyword_error(self, r):
    """Expect The authentication method 'no_password' cannot be used with the ADD keyword error."""

    exitcode = 36
    message = (
        "The authentication method 'no_password' cannot be used with the ADD keyword."
    )
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_password_or_user_is_incorrect_error(self, r):
    """Expect Authentication failed: password is incorrect, or there is no user with such name error."""

    exitcode = 4
    message = f"Authentication failed: password is incorrect, or there is no user with such name."
    expect_error(r=r, exitcode=exitcode, message=message)
