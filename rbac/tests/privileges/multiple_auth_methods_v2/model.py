import testflows.settings as settings
from testflows.core import current, debug

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions

from helpers.sql.create_user import CreateUser
from helpers.sql.query import Query


class States:
    CreateUser = CreateUser
    Query = Query


class Model:
    """Multiple user authentication methods model."""

    def expect_ok(self, behavior):
        """Expect no error."""
        return actions.expect_ok

    def expect_no_password_auth_cannot_coexist_with_others_error(self, behavior):
        """Check for no password authentication method coexisting with others error."""
        current = behavior[-1]

        if not isinstance(current, States.CreateUser):
            return

        auth_methods = [auth_method.method for auth_method in current.identification]

        if "no_password" in auth_methods and len(auth_methods) > 1:
            return actions.expect_no_password_auth_cannot_coexist_with_others_error

    def expect_password_or_user_is_incorrect_error(self, behavior):
        """Expect password or user is incorrect error."""
        current = behavior[-1]

        if not isinstance(current, States.Query):
            return

        if not current.connection_options:
            return

        for state in behavior[:-1]:
            # FIXME: handle ALTERs
            # FIXME: handle DROP USER
            if isinstance(state, States.CreateUser) and not state.errored:
                for username in state.usernames:
                    if username.name == current.connection_options.get(
                        "user", "default"
                    ):
                        for auth_method in state.identification:
                            if auth_method.method == "no_password":
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
            self.expect_no_password_auth_cannot_coexist_with_others_error(behavior)
            or self.expect_password_or_user_is_incorrect_error(behavior)
            or self.expect_ok(behavior)
        )
