from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
from rbac.tests.multiple_auth_methods.server_setting.common import *
import rbac.tests.multiple_auth_methods.common as common


@TestScenario
def run_check_alter_user_add_auth_methods(self, max_auth_methods_per_user):
    """Check that new authentication methods can be added to a user only if the number of
    authentication methods does not exceed `max_authentication_methods_per_user`."""

    checks = [
        alter_user_add_identified_by_one_password,
        alter_user_add_one_auth_method,
        alter_user_add_two_auth_methods,
        alter_user_add_three_auth_methods,
        alter_user_add_ten_auth_methods,
    ]

    with Given("create users with 2 auth methods each"):
        user_names = [f"user{i}_{getuid()}" for i in range(len(checks))]
        for user_name in user_names:
            create_user_identified_with_ssh_keys_and_plaintext_password(
                user_name=user_name
            )

    with And(
        f"set `max_authentication_methods_per_user` to {max_auth_methods_per_user}"
    ):
        common.change_server_settings(
            setting="max_authentication_methods_per_user",
            value=max_auth_methods_per_user,
        )

    for check, user_name in zip(checks, user_names):
        Check(test=check)(
            user_name=user_name,
            max_auth_methods_per_user=max_auth_methods_per_user,
            current_number_of_auth_methods=2,
        )


@TestScenario
def check_alter_user_add_auth_methods_with_zero_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 0."""
    run_check_alter_user_add_auth_methods(max_auth_methods_per_user=0)


@TestScenario
def check_alter_user_add_auth_methods_with_one_auth_method_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 1."""
    run_check_alter_user_add_auth_methods(max_auth_methods_per_user=1)


@TestScenario
def check_alter_user_add_auth_methods_with_two_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 2."""
    run_check_alter_user_add_auth_methods(max_auth_methods_per_user=2)


@TestScenario
def check_alter_user_add_auth_methods_with_three_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 3."""
    run_check_alter_user_add_auth_methods(max_auth_methods_per_user=3)


@TestScenario
def check_alter_user_add_auth_methods_with_twelve_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 3."""
    run_check_alter_user_add_auth_methods(max_auth_methods_per_user=12)


@TestFeature
@Name("alter add identified")
def feature(self):
    """Check that user can be altered with no more than `max_authentication_methods_per_user`
    authentication methods."""
    Scenario(run=check_alter_user_add_auth_methods_with_zero_auth_methods_allowed)
    Scenario(run=check_alter_user_add_auth_methods_with_one_auth_method_allowed)
    Scenario(run=check_alter_user_add_auth_methods_with_two_auth_methods_allowed)
    Scenario(run=check_alter_user_add_auth_methods_with_three_auth_methods_allowed)
    Scenario(run=check_alter_user_add_auth_methods_with_twelve_auth_methods_allowed)
