from testflows.core import *

from rbac.requirements import *

from helpers.common import getuid
import rbac.tests.multiple_auth_methods.common as common
import rbac.tests.multiple_auth_methods.errors as errors


# create user


@TestCheck
def create_user_without_identified_clause(self, user_name, **kwargs):
    """Create a user without IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
    )


@TestCheck
def create_user_with_not_identified_clause(self, user_name, **kwargs):
    """Create a user with NOT IDENTIFIED clause."""
    common.create_user(
        user_name=user_name,
        not_identified=True,
    )


@TestCheck
def create_user_with_no_password(self, user_name, **kwargs):
    """Create a user with no_password authentication method."""
    common.create_user(
        user_name=user_name,
        identified="no_password",
    )


@TestCheck
def create_user_identified_by_one_password(self, user_name, **kwargs):
    """Create a user with IDENTIFIED BY clause and return the password."""
    common.create_user(
        user_name=user_name,
        identified_by="'1'",
    )
    return "1"


@TestCheck
def create_user_identified_with_ssh_key(self, user_name, **kwargs):
    """Create a user identified by ssh_key."""
    ssh_key = "AAAAC3NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    ssh_key2 = "AAAAC2NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    identified = f"ssh_key BY KEY '{ssh_key}' TYPE 'ssh-ed25519', KEY '{ssh_key2}' TYPE 'ssh-ed25519'"
    common.create_user(
        user_name=user_name,
        identified=identified,
    )


@TestCheck
def create_user_identified_with_ssh_keys_and_plaintext_password(
    self, user_name, max_auth_methods_per_user=100
):
    """Create a user identified with ssh keys and plaintext password."""
    ssh_key = "AAAAC3NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    ssh_key2 = "AAAAC2NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    identified = f"ssh_key BY KEY '{ssh_key}' TYPE 'ssh-ed25519', KEY '{ssh_key2}' TYPE 'ssh-ed25519', plaintext_password by '50'"
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user == 1
            else None
        ),
    )


@TestCheck
def create_user_identified_with_two_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Create a user with two authentication methods and return list of corresponding passwords."""
    identified = "plaintext_password by '2', by '3'"
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user < 2 and max_auth_methods_per_user > 0
            else None
        ),
    )
    return ["2", "3"]


@TestCheck
def create_user_identified_with_three_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Create a user with three authentication methods. Return list of corresponding passwords."""
    identified = (
        "bcrypt_password by '4', bcrypt_password by '5', sha256_password by '6'"
    )
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user < 3 and max_auth_methods_per_user > 0
            else None
        ),
    )
    return ["4", "5", "6"]


@TestCheck
def create_user_identified_with_ten_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Create a user with ten authentication methods."""
    identified = (
        "plaintext_password by '7', bcrypt_password by '8', plaintext_password by '9', "
        "bcrypt_password by '10', sha256_password by '11', bcrypt_password by '12', "
        "plaintext_password by '13', bcrypt_password by '14', sha256_password by '15', "
        "bcrypt_password by '16'"
    )
    common.create_user(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user < 10 and max_auth_methods_per_user > 0
            else None
        ),
    )


# alter user identified


@TestCheck
def alter_user_not_identified(self, user_name, **kwargs):
    """Change user authentication method to not_identified."""
    common.alter_identified(
        user_name=user_name,
        not_identified=True,
    )


@TestCheck
def alter_user_identified_with_no_password(self, user_name, **kwargs):
    """Change user's authentication method to no_password."""
    common.alter_identified(
        user_name=user_name,
        identified="no_password",
    )


@TestCheck
def alter_user_identified_by_one_method(self, user_name, **kwargs):
    """Change user's authentication method to identified by one default auth method."""
    common.alter_identified(
        user_name=user_name,
        identified_by="'17'",
    )
    return "17"


@TestCheck
def alter_user_identified_with_ssh_keys(self, user_name, **kwargs):
    """Change user's authentication method to ssh keys."""
    ssh_key = "AAAAC3NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    ssh_key2 = "AAAAC2NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"

    identified = f"ssh_key BY KEY '{ssh_key}' TYPE 'ssh-ed25519', KEY '{ssh_key2}' TYPE 'ssh-ed25519'"
    common.alter_identified(
        user_name=user_name,
        identified=identified,
    )


@TestCheck
def alter_user_identified_with_ssh_keys_and_plaintext_password(
    self, user_name, max_auth_methods_per_user=100
):
    """Change user's authentication method to ssh keys and plaintext password."""
    ssh_key = "AAAAC3NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    ssh_key2 = "AAAAC2NzaC1lZDI1NTE5AAAAIBzqa3duS0ce6QYkzUgko9W0Ux7i7d3xPoseFrwnhY4Y"
    identified = f"ssh_key BY KEY '{ssh_key}' TYPE 'ssh-ed25519', KEY '{ssh_key2}' TYPE 'ssh-ed25519', plaintext_password by '49'"
    common.alter_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user == 1
            else None
        ),
    )


@TestCheck
def alter_user_identified_with_two_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Change user's authentication method to two methods."""
    identified = "plaintext_password by '18', by '19'"
    common.alter_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user == 1
            else None
        ),
    )
    return ["18", "19"]


@TestCheck
def alter_user_identified_with_three_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Change user's authentication method to three methods."""
    identified = (
        "bcrypt_password by '20', bcrypt_password by '21', sha256_password by '22'"
    )
    common.alter_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user < 3 and max_auth_methods_per_user > 0
            else None
        ),
    )
    return ["20", "21", "22"]


@TestCheck
def alter_user_identified_with_ten_methods(
    self, user_name, max_auth_methods_per_user=100
):
    """Change user's authentication method to ten methods."""
    identified = (
        "plaintext_password by '23', bcrypt_password by '24', plaintext_password by '25', "
        "bcrypt_password by '26', sha256_password by '27', bcrypt_password by '28', "
        "plaintext_password by '29', bcrypt_password by '30', sha256_password by '31', "
        "bcrypt_password by '32'"
    )
    common.alter_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user < 10 and max_auth_methods_per_user > 0
            else None
        ),
    )


# alter user add identified


@TestCheck
def alter_user_add_one_auth_method(
    self, user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add new authentication method to a existing user."""
    identified = "bcrypt_password by '33'"
    common.add_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user - current_number_of_auth_methods < 1
            and max_auth_methods_per_user > 0
            else None
        ),
    )
    return "33"


@TestCheck
def alter_user_add_identified_by_one_password(
    self, user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add new authentication method to a existing user."""
    identified_by = "'51'"
    common.add_identified(
        user_name=user_name,
        identified_by=identified_by,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user - current_number_of_auth_methods < 1
            and max_auth_methods_per_user > 0
            else None
        ),
    )
    return "33"


@TestCheck
def alter_user_add_two_auth_methods(
    self, user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add two new authentication methods to a existing user."""
    identified = "bcrypt_password by '34', sha256_password by '35'"
    common.add_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user - current_number_of_auth_methods < 2
            and max_auth_methods_per_user > 0
            else None
        ),
    )
    return ["34", "35"]


@TestCheck
def alter_user_add_three_auth_methods(
    self, user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add three new authentication methods to a existing user."""
    identified = (
        "bcrypt_password by '36', sha256_password by '37', plaintext_password by '38'"
    )
    common.add_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user - current_number_of_auth_methods < 3
            and max_auth_methods_per_user > 0
            else None
        ),
    )
    return ["36", "37", "38"]


@TestCheck
def alter_user_add_ten_auth_methods(
    self, user_name, max_auth_methods_per_user=100, current_number_of_auth_methods=1
):
    """Add ten new authentication methods to a existing user."""
    identified = (
        "bcrypt_password by '39', sha256_password by '40', plaintext_password by '41', "
        "bcrypt_password by '42', sha256_password by '43', bcrypt_password by '44', "
        "plaintext_password by '45', bcrypt_password by '46', sha256_password by '47', "
        "bcrypt_password by '48'"
    )
    common.add_identified(
        user_name=user_name,
        identified=identified,
        expected=(
            errors.user_can_not_be_created_updated()
            if max_auth_methods_per_user - current_number_of_auth_methods < 10
            and max_auth_methods_per_user > 0
            else None
        ),
    )
