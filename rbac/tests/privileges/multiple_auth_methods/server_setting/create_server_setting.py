from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors


def create_user_without_identified_clause(user_name, max_auth_methods_per_user):
    """Create a user without IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_with_not_identified_clause(user_name, max_auth_methods_per_user):
    """Create a user with NOT IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
        not_identified=True,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_with_no_password(user_name, max_auth_methods_per_user):
    """Create a user with no_password authentication method."""
    common.create_user(
        user_name=user_name,
        identified="no_password",
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_with_identified_by_clause(user_name, max_auth_methods_per_user):
    """Create a user with IDENTIFIED BY clause."""
    common.create_user(
        user_name=user_name,
        identified_by="'1'",
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_identified_with_ssh_key(user_name, max_auth_methods_per_user):
    """Create a user identified by ssh_key."""
    ssh_pub_key = "AAAAC3NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    ssh_pub_key2 = (
        "AAAAC2NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    )
    identified = f"ssh_key BY KEY '{ssh_pub_key}' TYPE 'ssh-ed25519', KEY '{ssh_pub_key2}' TYPE 'ssh-ed25519'"
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_identified_with_two_methods(user_name, max_auth_methods_per_user):
    """Create a user with two authentication methods."""
    identified = "plaintext_password by '1', by '3'"
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user < 2
        else None,
    )


def create_user_identified_with_three_methods(user_name, max_auth_methods_per_user):
    """Create a user with three authentication methods."""
    identified = (
        "bcrypt_password by '1', bcrypt_password by '2', sha256_password by '3'"
    )
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user < 3
        else None,
    )


def create_user_identified_with_ten_methods(user_name, max_auth_methods_per_user):
    """Create a user with ten authentication methods."""
    identified = (
        "plaintext_password by '1', bcrypt_password by '2', plaintext_password by '3', "
        "bcrypt_password by '4', sha256_password by '5', bcrypt_password by '6', "
        "plaintext_password by '7', bcrypt_password by '8', sha256_password by '9', "
        "bcrypt_password by '10'"
    )
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user < 10
        else None,
    )


def run_check_create_user_with_multiple_auth_methods(max_auth_methods_per_user):
    """Run tests for a given max_authentication_methods_per_user value."""
    with Given(
        f"set max_authentication_methods_per_user to {max_auth_methods_per_user}"
    ):
        common.change_server_settings(
            setting="max_authentication_methods_per_user",
            value=max_auth_methods_per_user,
        )

    checks = [
        create_user_without_identified_clause,
        create_user_with_not_identified_clause,
        create_user_with_no_password,
        create_user_with_identified_by_clause,
        create_user_identified_with_ssh_key,
        create_user_identified_with_two_methods,
        create_user_identified_with_three_methods,
        create_user_identified_with_ten_methods,
    ]

    for check in checks:
        user_name = f"user_{getuid()}"
        check(user_name, max_auth_methods_per_user)


@TestScenario
def check_create_user_with_zero_auth_methods_allowed(self):
    """Check different scenarios for creating a user when max_authentication_methods_per_user is set to 0."""
    run_check_create_user_with_multiple_auth_methods(max_auth_methods_per_user=0)


@TestScenario
def check_create_user_with_one_auth_method_allowed(self):
    """Check different scenarios for creating a user when max_authentication_methods_per_user is set to 1."""
    run_check_create_user_with_multiple_auth_methods(max_auth_methods_per_user=1)


@TestScenario
def check_create_user_with_two_auth_methods_allowed(self):
    """Check different scenarios for creating a user when max_authentication_methods_per_user is set to 2."""
    run_check_create_user_with_multiple_auth_methods(max_auth_methods_per_user=2)


@TestScenario
def check_create_user_with_three_auth_methods_allowed(self):
    """Check different scenarios for creating a user when max_authentication_methods_per_user is set to 3."""
    run_check_create_user_with_multiple_auth_methods(max_auth_methods_per_user=3)


@TestFeature
@Name("server setting create user")
def feature(self):
    """Check that user can be created with no more than max_authentication_methods_per_user
    authentication methods."""
    Scenario(run=check_create_user_with_zero_auth_methods_allowed)
    Scenario(run=check_create_user_with_one_auth_method_allowed)
    Scenario(run=check_create_user_with_two_auth_methods_allowed)
    Scenario(run=check_create_user_with_three_auth_methods_allowed)
