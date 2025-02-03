import testflows.settings as settings
from testflows.core import *

import rbac.tests.multiple_auth_methods.simple_combinatorics.actions as actions

from .create_user import CreateUser
from .alter_user import AlterUser
from helpers.sql.drop_user import DropUser
from helpers.sql.query import Query


class States:
    Query = Query
    CreateUser = CreateUser
    AlterUser = AlterUser
    DropUser = DropUser


class Model:
    """Multiple user authentication methods model."""

    def expect_ok(self):
        """Expect no error."""
        return actions.expect_ok

    def expect_there_no_user_error(self, behavior):
        """Expect there is no user error."""
        current_ = behavior[-1]

        if not isinstance(current_, (States.AlterUser)):
            return

        user_exists = False
        user_name = current_.username

        for state in behavior[:-1]:
            if isinstance(state, States.CreateUser) and not state.errored:
                if user_name == state.username:
                    user_exists = True

        if not user_exists:
            return actions.expect_there_is_no_user_error

    def expect_no_password_auth_cannot_coexist_with_others_error(self, behavior):
        """Check for no password authentication method coexisting with others error."""
        current_ = behavior[-1]

        if not isinstance(current_, States.Query):
            return

        auth_methods = []

        if isinstance(current_, States.CreateUser):
            auth_methods = [
                auth_method.method for auth_method in current_.identification
            ]

        elif isinstance(current_, States.AlterUser):
            if current_.identification:
                auth_methods = [
                    auth_method.method for auth_method in current_.identification
                ]

            if current_.add_identification:
                for state in behavior[:-1]:
                    if isinstance(state, States.CreateUser) and not state.errored:
                        auth_methods = [
                            auth_method.method for auth_method in state.identification
                        ]
                    elif isinstance(state, States.DropUser) and not state.errored:
                        auth_methods = {node: [] for node in current().context.nodes}
                    elif isinstance(state, States.AlterUser) and not state.errored:
                        if state.identification:
                            auth_methods = [
                                auth_method.method
                                for auth_method in state.identification
                            ]
                        elif state.add_identification and not state.errored:
                            for new_auth_method in state.add_identification:
                                auth_methods.append(new_auth_method)
                        elif state.reset_auth_methods_to_new:
                            auth_methods = [auth_methods[-1]]
                        else:
                            raise ValueError("Unexpected alter user state")

                auth_methods += current_.add_identification
        else:
            return

        if "no_password" in auth_methods and len(auth_methods) > 1:
            return actions.expect_no_password_auth_cannot_coexist_with_others_error

    def expect_no_password_cannot_be_used_with_add_keyword_error(self, behavior):
        """Expect no password cannot be used with add keyword error."""
        current = behavior[-1]

        if isinstance(current, States.AlterUser):
            if current.add_identification:
                if any(
                    auth_method.method == "no_password"
                    for auth_method in current.add_identification
                ):
                    return actions.expect_syntax_error

    def expect_password_or_user_is_incorrect_error(self, behavior):
        """Expect password or user is incorrect error."""
        current = behavior[-1]

        if not isinstance(current, States.Query):
            return

        if not current.connection_options:
            return

        auth_methods = None

        for state in behavior[:-1]:
            if isinstance(state, States.CreateUser) and not state.errored:
                for username in [state.username]:
                    if username == current.connection_options.get("user", "default"):
                        auth_methods = list(state.identification)

            elif isinstance(state, States.DropUser) and not state.errored:
                for username in [state.username]:
                    if username == current.connection_options.get("user", "default"):
                        auth_methods = None

            elif isinstance(state, States.AlterUser) and not state.errored:
                note(list(state.add_identification))
                for username in [state.username]:
                    if username == current.connection_options.get("user", "default"):
                        if state.reset_auth_methods_to_new:
                            auth_methods = list([auth_methods[-1]])
                        elif state.identification:
                            auth_methods = list(state.identification)
                        elif state.add_identification:
                            auth_methods += list(state.add_identification)
                        else:
                            pass

        if auth_methods:
            for auth_method in auth_methods:
                if auth_method.method == "no_password" and len(auth_methods) == 1:
                    return
                if auth_method.password == current.connection_options.get(
                    "password", ""
                ):
                    return

        return actions.expect_password_or_user_is_incorrect_error

    def expect(self, behavior=None):
        """Return expected result action for a given behavior."""

        if behavior is None:
            behavior = current().context.behavior

        if settings.debug:
            for i, state in enumerate(behavior):
                debug(f"{i}: {repr(state)}")

        return (
            self.expect_no_password_cannot_be_used_with_add_keyword_error(behavior)
            or self.expect_there_no_user_error(behavior)
            or self.expect_no_password_auth_cannot_coexist_with_others_error(behavior)
            or self.expect_password_or_user_is_incorrect_error(behavior)
            or self.expect_ok()
        )
