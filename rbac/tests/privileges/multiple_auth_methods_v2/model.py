from testflows.core import current

import rbac.tests.privileges.multiple_auth_methods_v2.actions as actions

from helpers.sql.create_user import CreateUser


class States:
    CreateUser = CreateUser


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

    def expect(self, behavior=None):
        """Return expected result action for a given behavior."""

        if behavior is None:
            behavior = current().context.behavior

        return self.expect_no_password_auth_cannot_coexist_with_others_error(
            behavior
        ) or self.expect_ok(behavior)
