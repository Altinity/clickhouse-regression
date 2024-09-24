from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
from rbac.tests.multiple_auth_methods.server_setting.common import *
import rbac.tests.multiple_auth_methods.common as common


@TestScenario
def run_check_alter_user_with_multiple_auth_methods(self, max_auth_methods_per_user):
    """Check that user can be altered with no more than `max_authentication_methods_per_user`
    authentication methods."""
    with Given(
        f"set `max_authentication_methods_per_user` to {max_auth_methods_per_user}"
    ):
        common.change_server_settings(
            setting="max_authentication_methods_per_user",
            value=max_auth_methods_per_user,
        )

    checks = [
        alter_user_not_identified,
        alter_user_identified_with_no_password,
        alter_user_identified_by_one_method,
        alter_user_identified_with_ssh_keys,
        alter_user_identified_with_ssh_keys_and_plaintext_password,
        alter_user_identified_with_two_methods,
        alter_user_identified_with_three_methods,
        alter_user_identified_with_ten_methods,
    ]

    for check in checks:
        user_name = f"user_{getuid()}"
        common.create_user(user_name=user_name)
        Check(test=check)(
            user_name=user_name, max_auth_methods_per_user=max_auth_methods_per_user
        )


@TestScenario
def check_alter_user_with_zero_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 0."""
    run_check_alter_user_with_multiple_auth_methods(max_auth_methods_per_user=0)


@TestScenario   
def check_alter_user_with_one_auth_method_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 1."""
    run_check_alter_user_with_multiple_auth_methods(max_auth_methods_per_user=1)


@TestScenario
def check_alter_user_with_two_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 2."""
    run_check_alter_user_with_multiple_auth_methods(max_auth_methods_per_user=2)


@TestScenario
def check_alter_user_with_three_auth_methods_allowed(self):
    """Check different scenarios for creating a user when `max_authentication_methods_per_user` is set to 3."""
    run_check_alter_user_with_multiple_auth_methods(max_auth_methods_per_user=3)


@TestFeature
@Name("alter identified")
def feature(self):
    """Check that user can be altered with no more than `max_authentication_methods_per_user`
    authentication methods."""
    Scenario(run=check_alter_user_with_one_auth_method_allowed)
    Scenario(run=check_alter_user_with_two_auth_methods_allowed)
    Scenario(run=check_alter_user_with_three_auth_methods_allowed)
    Scenario(run=check_alter_user_with_zero_auth_methods_allowed)
