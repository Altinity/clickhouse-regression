from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
import rbac.tests.privileges.multiple_auth_methods.common as common
import rbac.tests.privileges.multiple_auth_methods.errors as errors


def create_user_without_identified_clause(user_name, max_auth_methods_per_user=100):
    """Create a user without IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_with_not_identified_clause(user_name, max_auth_methods_per_user=100):
    """Create a user with NOT IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
        not_identified=True,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_with_no_password(user_name, max_auth_methods_per_user=100):
    """Create a user with no_password authentication method."""
    common.create_user(
        user_name=user_name,
        identified="no_password",
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )


def create_user_identified_by_one_password(user_name, max_auth_methods_per_user=100):
    """Create a user with IDENTIFIED BY clause and return the password."""
    common.create_user(
        user_name=user_name,
        identified_by="'1'",
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user == 0
        else None,
    )
    return "1"


def create_user_identified_with_ssh_key(user_name, max_auth_methods_per_user=100):
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


def create_user_identified_with_two_methods(user_name, max_auth_methods_per_user=100):
    """Create a user with two authentication methods and return list of corresponding passwords."""
    identified = "plaintext_password by '1', by '3'"
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user < 2
        else None,
    )
    return ["1", "3"]


def create_user_identified_with_three_methods(user_name, max_auth_methods_per_user=100):
    """Create a user with three authentication methods. Return list of corresponding passwords."""
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
    return ["1", "2", "3"]


def alter_user_add_one_auth_method(
    user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add new authentication method to a existing user."""
    identified = "bcrypt_password by '10'"
    common.add_identified(
        user_name=user_name,
        identified=identified,
        expected=errors.user_can_not_be_created_updated()
        if max_auth_methods_per_user-current_number_of_auth_methods < 1
        else None,
    )
    return "10"
