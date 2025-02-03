from testflows.core import *
from testflows.combinatorics import combinations

from functools import wraps

from .create_user import CreateUser
from .alter_user import AlterUser
from helpers.sql.drop_user import DropUser
from helpers.sql.select import Select


def partial(func, *args, **keywords):
    """Create a new function with partial application of the given arguments and keywords."""

    @wraps(func)
    def newfunc(*fargs, **fkeywords):
        newkeywords = {**keywords, **fkeywords}
        return func(*args, *fargs, **newkeywords)

    return newfunc


def create_user_auth_combinations(
    auth_methods=None, max_length=3, with_replacement=False
):
    """Generate combinations of authentication methods."""
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
    auth_combinations = []
    for length in range(1, max_length + 1):
        auth_combinations.extend(
            combinations(auth_methods, length, with_replacement=with_replacement)
        )
    return auth_combinations


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

    r = node.query(str(query), no_checks=True, steps=False, **kwargs)
    query.add_connection_options(kwargs.pop("settings", None))
    query.add_result(r)
    self.context.behavior.append(query)

    Then(test=self.context.model.expect())(r=r)


@TestStep(When)
def alter_user(
    self,
    auth_methods,
    user_name=None,
    client=None,
):
    """Alter user to set new authentication methods."""
    query = AlterUser()

    query = query.set_username(user_name)

    query = query.set_identified()

    for auth_method in auth_methods:
        query = auth_method(query)

    client_query(query=query, client=client)

    return query


@TestStep(When)
def alter_user_add(
    self,
    user_name=None,
    auth_methods=None,
    client=None,
):
    """Alter user to add new authentication methods."""
    query = AlterUser()

    query = query.set_username(user_name)

    query = query.set_add_identified()

    for auth_method in auth_methods:
        query = auth_method(query)

    client_query(query=query, client=client)

    return query


@TestStep(When)
def alter_user_reset_to_new(
    self,
    user_name=None,
    client=None,
):
    """Alter user to reset authentication methods to new (the last)."""
    query = AlterUser()

    query = query.set_username(user_name)

    query.set_reset_authentication_methods_to_new()

    client_query(query=query, client=client)

    return query


@TestStep(Given)
def create_user(
    self,
    user_name=None,
    auth_methods=None,
    client=None,
):
    """Create user with given name and authentication methods."""

    query = CreateUser()

    query.set_username(name=user_name)

    query.set_identified()

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
def login(self, user: CreateUser, node=None):
    """Check user can login with valid passwords."""

    if node is None:
        node = self.context.node

    for auth_method in list(
        user.identification + getattr(user, "add_identification", [])
    ):
        password = auth_method.password or ""
        with By(
            f"trying to login with {user.username} and {password} for {auth_method.method}"
        ):
            query=Select().set_query("SELECT current_user()")
            connection_options=[("user", user.username), ("password", password)]
            query.add_connection_options(connection_options)
            
            r = node.query(str(query), no_checks=True, steps=False, settings=connection_options)
            query.add_result(r)
        
            self.context.behavior.append(query)

            Then(test=self.context.model.expect())(r=r)


@TestStep(Then)
def expect_ok(self, r):
    """Expect the query to be successful."""

    assert (
        "DB::Exception" not in r.output
    ), f"unexpected 'DB::Exception' in '{r.output}'"


@TestStep(Then)
def expect_error(self, r, exitcode, message):
    """Expect given exitcode and message in the output."""

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
