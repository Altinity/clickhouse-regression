from testflows.core import *
from testflows.combinatorics import combinations

from functools import wraps

from helpers.common import getuid
from helpers.sql.create_user import CreateUser, Username
from helpers.sql.alter_user import AlterUser
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


def with_required(auth_methods):
    """Check if the first authentication method requires WITH keyword."""
    return "set_with" in auth_methods[0].__name__


def create_user_auth_combinations(
    auth_methods=None, max_length=3, with_replacement=False
):
    """Generate combinations of authentication methods."""
    if auth_methods is None:
        auth_methods = [
            CreateUser.set_with_no_password,
            partial(CreateUser.set_by_password, password="foo1"),
            partial(CreateUser.set_by_password, password="foo2"),
            partial(CreateUser.set_with_plaintext_password, password="foo3"),
            partial(CreateUser.set_with_sha256_password, password="foo4"),
            partial(CreateUser.set_with_sha256_hash, password="foo5"),
            partial(
                CreateUser.set_with_sha256_hash_with_salt, password="foo6", salt="salt1"
            ),
            partial(CreateUser.set_with_double_sha1_password, password="foo7"),
            partial(CreateUser.set_with_double_sha1_hash, password="foo8"),
            partial(CreateUser.set_with_bcrypt_password, password="foo9"),
            # partial(CreateUser.set_with_bcrypt_hash, password="foo10"),
        ]
    auth_combinations = []
    for length in range(1, max_length + 1):
        auth_combinations.extend(
            combinations(auth_methods, length, with_replacement=with_replacement)
        )
    return auth_combinations


def alter_user_auth_combinations(
    auth_methods=None, max_length=3, with_replacement=False
):
    """Generate combinations of alter user authentication methods."""
    if auth_methods is None:
        auth_methods = [
            AlterUser.set_with_no_password,
            partial(AlterUser.set_by_password, password="foo1"),
            partial(AlterUser.set_by_password, password="foo2"),
            partial(AlterUser.set_with_plaintext_password, password="foo3"),
            partial(AlterUser.set_with_sha256_password, password="foo4"),
            partial(AlterUser.set_with_sha256_hash, password="foo5"),
            partial(
                AlterUser.set_with_sha256_hash_with_salt, password="foo6", salt="salt1"
            ),
            partial(AlterUser.set_with_double_sha1_password, password="foo7"),
            partial(AlterUser.set_with_double_sha1_hash, password="foo8"),
            partial(AlterUser.set_with_bcrypt_password, password="foo9"),
            # partial(AlterUser.set_with_bcrypt_hash, password="foo10"),
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

    bash_tools = self.context.cluster.node("bash-tools")

    with bash_tools.client(client_args={"host": node.name}) as client:
        yield client


@TestStep(When)
def client_query(self, query, client=None, node=None, **kwargs):
    """Execute query on the client. Add query to the behavior.
    Use model to check the result."""

    if client is None:
        client = self.context.client

    if node is None:
        node = self.context.node

    r = client.query(str(query), no_checks=True, **kwargs)
    query.add_result(r)

    if hasattr(self.context, "behavior_appending_lock"):
        with self.context.behavior_appending_lock:
            self.context.behavior.append(query)
    else:
        self.context.behavior.append(query)

    Then(test=self.context.model.expect(node=node))(r=r)


@TestStep(When)
def node_query(self, query, node=None, **kwargs):
    """Execute query on the node. Add query to the behavior.
    Use model to check the result."""

    if node is None:
        node = self.context.node

    r = node.query(str(query), no_checks=True, steps=False, **kwargs)
    query.add_connection_options(kwargs.pop("settings", None))
    query.add_result(r)
    self.context.behavior.append(query)

    Then(test=self.context.model.expect(node=node))(r=r)


@TestStep(When)
def alter_user(
    self,
    auth_methods,
    user=None,
    usernames=None,
    client=None,
    on_cluster=None,
    node=None,
):
    """Alter user to set new authentication methods."""

    # FIXME: can you rename a user and change its authentication methods in one query?

    if client is None:
        client = self.context.client

    if node is None:
        node = self.context.node

    query = AlterUser()

    usernames = usernames or user.usernames

    for username in usernames:
        query = query.set_username(getattr(username, "renamed", None) or username.name)

    if on_cluster is not None:
        query.set_on_cluster(cluster_name=on_cluster)

    query = query.set_identified()

    for auth_method in auth_methods:
        query = auth_method(query, node=node, on_cluster=on_cluster)

    client_query(query=query, client=client, node=node)

    return query


@TestStep(When)
def alter_user_add(
    self,
    user=None,
    usernames=None,
    auth_methods=None,
    client=None,
    on_cluster=None,
    node=None,
):
    """Alter user to add new authentication methods."""

    if client is None:
        client = self.context.client

    if node is None:
        node = self.context.node

    query = AlterUser()

    usernames = usernames or user.usernames

    for username in usernames:
        query = query.set_username(getattr(username, "renamed", None) or username.name)

    if on_cluster is not None:
        query.set_on_cluster(cluster_name=on_cluster)

    query = query.set_add_identified()

    for auth_method in auth_methods:
        query = auth_method(query, node=node, on_cluster=on_cluster)

    client_query(query=query, client=client, node=node)

    return query


@TestStep(When)
def alter_user_reset_to_new(
    self,
    user=None,
    usernames=None,
    client=None,
    on_cluster=None,
    node=None,
):
    """Alter user to reset authentication methods to new (the last)."""

    if client is None:
        client = self.context.client

    if node is None:
        node = self.context.node

    query = AlterUser()

    usernames = usernames or user.usernames

    for username in usernames:
        query = query.set_username(getattr(username, "renamed", None) or username.name)

    if on_cluster is not None:
        query.set_on_cluster(cluster_name=on_cluster)

    query.set_reset_authentication_methods_to_new(node=node, on_cluster=on_cluster)

    client_query(query=query, client=client, node=node)

    return query


@TestStep(When)
def drop_user(
    self,
    user=None,
    usernames=None,
    if_exists=False,
    access_storage_type=None,
    client=None,
    on_cluster=None,
):
    """Drop user."""

    if client is None:
        client = self.context.client

    usernames = usernames or user.usernames

    for username in usernames:
        query = DropUser().set_username(username.name)

        if if_exists:
            query.set_if_exists()

        if on_cluster is not None:
            query.set_on_cluster(on_cluster)

        if access_storage_type:
            query.set_access_storage_type(access_storage_type)

        client_query(query=query, client=client)

    return query


@TestStep(Given)
def create_user(
    self,
    user_name=None,
    usernames=None,
    on_cluster=None,
    auth_methods=None,
    client=None,
    node=None,
):
    """Create user with given name and authentication methods.
    If name is not provided, it will be generated.
    """

    if client is None:
        client = self.context.client

    if node is None:
        node = self.context.node

    query = CreateUser()

    if user_name:
        usernames = [Username(name=user_name)]

    if not usernames:
        raise ValueError("usernames are not provided")

    for username in usernames:
        query.set_username(name=username.name)

    if on_cluster is not None:
        query.set_on_cluster(cluster_name=on_cluster)

    query.set_identified()

    for auth_method in auth_methods:
        query = auth_method(query, node=node, on_cluster=on_cluster)

    try:
        client_query(query=query, client=client, node=node)
        yield query
    finally:
        with Finally("drop the user if exists"):
            for username in usernames:
                drop_query = DropUser().set_if_exists().set_username(username.name)
                if on_cluster is not None:
                    drop_query.set_on_cluster(cluster_name=on_cluster)
                client_query(query=drop_query, client=client)


@TestStep(Then)
def successful_login(self, user: CreateUser, node=None):
    """Check user can login with valid passwords."""

    if node is None:
        node = self.context.node

    for auth_method in list(
        user.identification[node]
        + getattr(user, "add_identification", {}).get(node, [])
    ):
        for username in list(user.usernames):
            password = auth_method.password or ""
            with By(
                f"trying to login with {username.name} and {password} for {auth_method.method}"
            ):
                node_query(
                    query=Select().set_query("SELECT current_user()"),
                    settings=[("user", username.name), ("password", password)],
                    node=node,
                )


@TestStep(Then)
def login_with_wrong_password(self, user: CreateUser, node=None):
    """Check user trying to login with invalid passwords."""

    if node is None:
        node = self.context.node

    for auth_method in list(
        user.identification[node]
        + getattr(user, "add_identification", {}).get(node, [])
    ):
        for username in list(user.usernames):
            password = (auth_method.password or "") + "1"
            with By(
                f"trying to login with {username.name} and {password} for {auth_method.method}"
            ):
                node_query(
                    query=Select().set_query(f"SELECT current_user()"),
                    settings=[("user", username.name), ("password", password)],
                    node=node,
                )


@TestStep(Then)
def login_with_wrong_username(self, user: CreateUser, node=None):
    """Check user trying to login with invalid
    username but valid password for some user."""

    if node is None:
        node = self.context.node

    for auth_method in list(
        user.identification[node]
        + getattr(user, "add_identification", {}).get(node, [])
    ):
        for username in list(user.usernames):
            if auth_method.password:
                password = auth_method.password
                message = f"trying to login with {username.name} and {password} for {auth_method.method} auth method"
            else:
                password = ""
                message = f"trying to login with {username.name} and {auth_method.method} auth method"
            with By(message):
                node_query(
                    query=Select().set_query(f"SELECT current_user()"),
                    settings=[("user", username.name + "1"), ("password", password)],
                    node=node,
                )


@TestStep(Then)
def login_with_other_user_password(
    self, user1: CreateUser, user2: CreateUser, node=None
):
    """Check user trying to login with valid
    username but with valid password for another user."""

    if node is None:
        node = self.context.node

    def try_login(username, auth_method):
        password = auth_method.password or ""
        with By(
            f"trying to login with {username.name} and {password} for {auth_method.method}"
        ):
            node_query(
                query=Select().set_query(f"SELECT current_user()"),
                settings=[("user", username.name), ("password", password)],
                node=node,
            )

    for auth_method in list(
        user2.identification + getattr(user2, "add_identification", [])
    ):
        for username in list(user1.usernames):
            try_login(username, auth_method)

    for auth_method in list(
        user1.identification + getattr(user1, "add_identification", [])
    ):
        for username in list(user2.usernames):
            try_login(username, auth_method)


@TestStep(Then)
def login(self, user: CreateUser, node=None):
    """Check user trying to login with valid and invalid passwords."""

    successful_login(user=user, node=node)


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
def expect_syntax_error(self, r):
    """Expect syntax error."""

    exitcode = 62
    message = "DB::Exception: Syntax error: failed at position"
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_no_password_auth_cannot_coexist_with_others_error(self, r):
    """Expect NO_PASSWORD Authentication method cannot co-exist with other authentication methods error."""

    exitcode = 36
    message = "DB::Exception: Authentication method 'no_password' cannot co-exist with other authentication methods."
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_password_or_user_is_incorrect_error(self, r):
    """Expect Authentication failed: password is incorrect, or there is no user with such name error."""

    exitcode = 4
    message = f"Authentication failed: password is incorrect, or there is no user with such name."
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_user_already_exists_error(self, r):
    """Expect user already exists error."""

    exitcode = 493
    message = "already exists"
    expect_error(r=r, exitcode=exitcode, message=message)


@TestStep(Then)
def expect_there_is_no_user_error(self, r):
    exitcode = 192
    message = "There is no user"
    expect_error(r=r, exitcode=exitcode, message=message)
