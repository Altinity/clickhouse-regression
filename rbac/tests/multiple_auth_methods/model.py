import testflows.settings as settings
from testflows.core import *

import rbac.tests.privileges.multiple_auth_methods.actions as actions

from helpers.sql.create_user import CreateUser
from helpers.sql.alter_user import AlterUser
from helpers.sql.drop_user import DropUser
from helpers.sql.query import Query


class States:
    Query = Query
    CreateUser = CreateUser
    AlterUser = AlterUser
    DropUser = DropUser


class Model:
    """Multiple user authentication methods model."""

    def expect_ok(self, behavior):
        """Expect no error."""
        return actions.expect_ok

    def expect_user_already_exists_error(self, behavior):
        """Expect user already exists error."""
        current = behavior[-1]

        if not isinstance(current, States.CreateUser):
            return

        if current.if_not_exists:
            return

        user_exists = False
        user_names = [username.name for username in current.usernames]

        for state in behavior[:-1]:
            if isinstance(state, States.CreateUser) and not state.errored:
                for username in state.usernames:
                    if username.name in user_names:
                        user_exists = True

            elif isinstance(state, States.DropUser) and not state.errored:
                for username in state.usernames:
                    if username.name in user_names:
                        user_exists = False

        if user_exists:
            return actions.expect_user_already_exists_error

    def expect_no_password_auth_cannot_coexist_with_others_error(self, behavior):
        """Check for no password authentication method coexisting with others error."""
        current_ = behavior[-1]

        if not isinstance(current_, States.Query):
            return

        auth_methods = {node: [] for node in current().context.nodes}

        for node in current().context.nodes:
            if isinstance(current_, States.CreateUser):
                auth_methods[node] = [
                    auth_method.method for auth_method in current_.identification[node]
                ]

            elif isinstance(current_, States.AlterUser):
                if current_.identification[node]:
                    auth_methods[node] = [
                        auth_method.method
                        for auth_method in current_.identification[node]
                    ]

                if current_.add_identification[node]:
                    for state in behavior[:-1]:
                        if isinstance(state, States.CreateUser) and not state.errored:
                            auth_methods[node] = [
                                auth_method.method
                                for auth_method in state.identification[node]
                            ]
                        elif isinstance(state, States.DropUser) and not state.errored:
                            auth_methods = {
                                node: [] for node in current().context.nodes
                            }
                        elif isinstance(state, States.AlterUser) and not state.errored:
                            if state.identification[node]:
                                auth_methods[node] = [
                                    auth_method.method
                                    for auth_method in state.identification[node]
                                ]
                            elif state.add_identification[node]:
                                auth_methods_ = []
                                for auth_method_ in state.add_identification[node]:
                                    if auth_method_.method != "no_password":
                                        auth_methods_.append(auth_method_)
                                auth_methods[node] += auth_methods_
                            elif state.reset_auth_methods_to_new[node]:
                                auth_methods[node] = [auth_methods[node][-1]]
                            else:
                                raise ValueError("Unexpected alter user state")

                    auth_methods[node] += current_.add_identification[node]
            else:
                return

            if "no_password" in auth_methods[node] and len(auth_methods[node]) > 1:
                return actions.expect_no_password_auth_cannot_coexist_with_others_error

    def expect_no_password_cannot_be_used_with_add_keyword_error(self, behavior, node):
        """Expect syntax error when no password is used with add keyword."""
        current = behavior[-1]

        if isinstance(current, States.AlterUser):
            if current.add_identification[node]:
                if any(
                    auth_method.method == "no_password"
                    for auth_method in current.add_identification[node]
                ):
                    return actions.expect_syntax_error

    def expect_password_or_user_is_incorrect_error(self, behavior, node):
        """Expect password or user is incorrect error."""
        current_ = behavior[-1]

        if not isinstance(current_, States.Query):
            return

        if not current_.connection_options:
            return

        auth_methods = None

        for state in behavior[:-1]:
            if isinstance(state, States.CreateUser) and not state.errored:
                for username in state.usernames:
                    if username.name == current_.connection_options.get(
                        "user", "default"
                    ):
                        auth_methods = list(state.identification[node])

            elif isinstance(state, States.DropUser) and not state.errored:
                for username in state.usernames:
                    if username.name == current_.connection_options.get(
                        "user", "default"
                    ):
                        auth_methods = None

            elif isinstance(state, States.AlterUser) and not state.errored:
                for username in state.usernames:
                    if username.name == current_.connection_options.get(
                        "user", "default"
                    ):
                        if state.reset_auth_methods_to_new[node]:
                            auth_methods = list([auth_methods[-1]])
                        elif state.identification[node]:
                            auth_methods = list(state.identification[node])
                        elif state.add_identification[node]:
                            _auth_methods = []
                            for auth_method in auth_methods:
                                if auth_method.method != "no_password":
                                    _auth_methods.append(auth_method)
                            auth_methods = _auth_methods
                            auth_methods += list(state.add_identification[node])
                        else:
                            pass

        if auth_methods:
            for auth_method in auth_methods:
                if auth_method.method == "no_password":
                    return
                if auth_method.password == current_.connection_options.get(
                    "password", ""
                ):
                    return

        return actions.expect_password_or_user_is_incorrect_error

    def expect_there_no_user_error(self, behavior):
        """Expect there is no user error."""
        current_ = behavior[-1]

        if not isinstance(current_, (States.AlterUser, States.DropUser)):
            return

        if current_.if_exists:
            return

        user_exists = False
        user_names = [username.name for username in current_.usernames]

        for state in behavior[:-1]:
            if isinstance(state, States.CreateUser) and not state.errored:
                for username in state.usernames:
                    if username.name in user_names:
                        user_exists = True

            elif isinstance(state, States.DropUser) and not state.errored:
                for username in state.usernames:
                    if username.name in user_names:
                        user_exists = False

        if not user_exists:
            return actions.expect_there_is_no_user_error

    def expect(self, behavior=None, node=None):
        """Return expected result action for a given behavior."""

        if behavior is None:
            behavior = current().context.behavior

        if node is None:
            node = current().context.node

        if settings.debug:
            for i, state in enumerate(behavior):
                debug(f"{i}: {repr(state)}")

        return (
            self.expect_no_password_cannot_be_used_with_add_keyword_error(
                behavior, node
            )
            or self.expect_there_no_user_error(behavior)
            or self.expect_no_password_auth_cannot_coexist_with_others_error(behavior)
            or self.expect_password_or_user_is_incorrect_error(behavior, node)
            or self.expect_user_already_exists_error(behavior)
            or self.expect_ok(behavior)
        )


@TestStep(Then)
def dummy_expect_ok(self, r):
    """Dummy expect ok."""

    assert True


class Model2:
    """Multiple user authentication methods model."""

    def expect_ok(self, behavior):
        """Expect no error."""
        return dummy_expect_ok

    def expect(self, behavior=None, node=None):
        """Return expected result action for a given behavior."""

        if behavior is None:
            behavior = current().context.behavior

        if node is None:
            node = current().context.node

        if settings.debug:
            for i, state in enumerate(behavior):
                debug(f"{i}: {repr(state)}")

        return self.expect_ok(behavior)
