from dataclasses import dataclass
from testflows.core import current, debug

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions

from helpers.sql.create_user import CreateUser


@dataclass(slots=True)
class UserLogin:
    username: str
    password: str
    result: str


class States:
    CreateUser = CreateUser
    UserLogin = UserLogin


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

        if not isinstance(current, States.UserLogin):
            return

        for state in behavior[:-1]:
            # FIXME: handle ALTERs
            if (
                isinstance(state, States.CreateUser)
                and "DB::Exception" not in state.result.output
            ):
                for username in state.usernames:
                    if username.name == current.username:
                        for auth_method in state.identification:
                            if auth_method.method == "no_password":
                                return
                            if auth_method.password == current.password:
                                return

        return actions.expect_password_or_user_is_incorrect_error

    def expect(self, behavior=None):
        """Return expected result action for a given behavior."""

        if behavior is None:
            behavior = current().context.behavior

        for i, state in enumerate(behavior):
            debug(f"{i}: {repr(state)}")

        return (
            self.expect_no_password_auth_cannot_coexist_with_others_error(behavior)
            or self.expect_password_or_user_is_incorrect_error(behavior)
            or self.expect_ok(behavior)
        )
