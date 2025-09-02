import json
import requests
from testflows.core import *
from oauth.requirements.requirements import *
from helpers.common import getuid


@TestStep(Given)
def get_oauth_token(self, username="demo", password="demo"):
    """Get an OAuth token from Keycloak for a user."""

    token_url = (
        f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/token"
    )

    data = {
        "grant_type": "password",
        "client_id": "grafana-client",
        "username": username,
        "password": password,
        "client_secret": "grafana-secret",
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()

    token_data = response.json()
    access_token = token_data["access_token"]
    expiration = token_data["expires_in"]
    refresh_expiration = token_data["refresh_expires_in"]

    return access_token


@TestStep(Given)
def get_admin_token(self):
    """Get an admin token from Keycloak."""

    token_url = (
        f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/token"
    )

    data = {
        "grant_type": "password",
        "client_id": "grafana-client",
        "username": "admin",
        "password": "admin",
        "client_secret": "grafana-secret",
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()

    token_data = response.json()
    access_token = token_data["access_token"]
    expiration = token_data["expires_in"]
    refresh_expiration = token_data["refresh_expires_in"]

    return access_token, expiration, refresh_expiration


@TestStep(Given)
def create_user(
    self,
    display_name: str,
    mail_nickname: str,
    user_principal_name: str,
    realm_name: str = "grafana",
    password: str = None,
):
    """Create a user in Keycloak."""
    users_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users"
    admin_token = get_oauth_token()

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    name_parts = display_name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    user_data = {
        "username": mail_nickname,
        "email": user_principal_name,
        "firstName": first_name,
        "lastName": last_name,
        "enabled": True,
        "emailVerified": True,
    }

    response = requests.post(users_url, json=user_data, headers=headers)
    response.raise_for_status()

    user_id = response.headers["Location"].split("/")[-1]

    if password:
        password_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user_id}/reset-password"
        password_data = {"type": "password", "value": password, "temporary": False}

        response = requests.put(password_url, json=password_data, headers=headers)
        response.raise_for_status()

    return user_id


@TestStep(Given)
def create_multiple_users(
    self,
    count: int,
    base_display_name: str = "User",
    base_mail_nickname: str = "user",
    base_user_principal_name: str = "user",
    realm_name: str = "grafana",
    base_password: str = None,
):
    """Create multiple users in Keycloak."""

    created_users = []

    for i in range(count):
        display_name = f"{base_display_name}_{i+1}"
        mail_nickname = f"{base_mail_nickname}_{i+1}"
        user_principal_name = f"{base_user_principal_name}_{i+1}@example.com"

        user_id = self.create_user(
            display_name=display_name,
            mail_nickname=mail_nickname,
            user_principal_name=user_principal_name,
            realm_name=realm_name,
            password=base_password,
        )

        created_users.append(user_id)

    return created_users


@TestStep(Given)
def create_group(
    self,
    display_name: str,
    mail_nickname: str,
    description: str = None,
    security_enabled: bool = True,
    mail_enabled: bool = False,
):
    """Create a group in Keycloak."""

    realm_name = getattr(self.context, "realm_name", "grafana")
    keycloak_url = getattr(self.context, "keycloak_url", "http://localhost:8080")
    admin_token = getattr(self.context, "admin_token", None)

    if admin_token is None:
        admin_token = get_admin_token()
        self.context.admin_token = admin_token

    groups_url = f"{keycloak_url}/admin/realms/{realm_name}/groups"

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    group_data = {
        "name": mail_nickname,
        "path": f"/{mail_nickname}",
    }

    attributes = {}
    if description:
        attributes["description"] = [description]
    attributes["displayName"] = [display_name]
    attributes["securityEnabled"] = [str(security_enabled).lower()]
    attributes["mailEnabled"] = [str(mail_enabled).lower()]

    if attributes:
        group_data["attributes"] = attributes

    response = requests.post(groups_url, json=group_data, headers=headers)
    response.raise_for_status()

    group_id = response.headers["Location"].split("/")[-1]

    return group_id


@TestStep(Given)
def assign_user_to_group(
    self,
    user_id: str,
    group_id: str,
):
    """Assign a user to a group in Keycloak."""

    realm_name = getattr(self.context, "realm_name", "grafana")
    keycloak_url = getattr(self.context, "keycloak_url", "http://localhost:8080")
    admin_token = getattr(self.context, "admin_token", None)

    if admin_token is None:
        admin_token = get_admin_token()
        self.context.admin_token = admin_token

    membership_url = (
        f"{keycloak_url}/admin/realms/{realm_name}/users/{user_id}/groups/{group_id}"
    )

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    response = requests.put(membership_url, headers=headers)
    response.raise_for_status()

    return True


@TestStep(Given)
def import_keycloak_realm(
    self,
    realm_config_path: str,
    keycloak_url: str = "http://localhost:8080",
    admin_token: str = None,
):
    """Import a realm configuration from a JSON file."""

    if admin_token is None:
        admin_token = get_admin_token()

    import_url = f"{keycloak_url}/admin/realms"

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    with open(realm_config_path, "r") as f:
        realm_data = json.load(f)

    response = requests.post(import_url, json=realm_data, headers=headers)

    if response.status_code != 409:
        response.raise_for_status()

    return True


@TestStep(Given)
def get_keycloak_user_by_username(
    self,
    realm_name: str,
    username: str,
    keycloak_url: str = "http://localhost:8080",
    admin_token: str = None,
):
    """Get a user by username from Keycloak realm."""

    if admin_token is None:
        admin_token = get_admin_token()

    users_url = f"{keycloak_url}/admin/realms/{realm_name}/users"

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    params = {"username": username, "exact": "true"}

    response = requests.get(users_url, params=params, headers=headers)
    response.raise_for_status()

    users = response.json()
    if users:
        return users[0]
    return None


@TestStep(Given)
def get_keycloak_group_by_name(
    self,
    realm_name: str,
    group_name: str,
    keycloak_url: str = "http://localhost:8080",
    admin_token: str = None,
):
    """Get a group by name from Keycloak realm."""

    if admin_token is None:
        admin_token = get_admin_token()

    groups_url = f"{keycloak_url}/admin/realms/{realm_name}/groups"

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    params = {"search": group_name}

    response = requests.get(groups_url, params=params, headers=headers)
    response.raise_for_status()

    groups = response.json()
    for group in groups:
        if group["name"] == group_name:
            return group
    return None


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def invalid_processor_type_configuration(self, node=None):
    """Configure ClickHouse with invalid Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_invalid",
        processor_type="invalid_type",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def missing_processor_type_configuration(self, node=None):
    """Configure ClickHouse with missing Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_missing_type",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def empty_processor_type_configuration(self, node=None):
    """Configure ClickHouse with empty Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_empty_type",
        processor_type="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def whitespace_processor_type_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_whitespace_type",
        processor_type="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def case_sensitive_processor_type_configuration(self, node=None):
    """Configure ClickHouse with case-sensitive Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_case_sensitive",
        processor_type="Keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def non_keycloak_processor_type_configuration(self, node=None):
    """Configure ClickHouse with non-Keycloak processor type."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_wrong_type",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def invalid_processor_name_configuration(self, node=None):
    """Configure ClickHouse with invalid processor name."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def whitespace_processor_name_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only processor name."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="   ",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def special_chars_processor_name_configuration(self, node=None):
    """Configure ClickHouse with special characters in processor name."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak@#$%",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    )
)
def missing_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with missing processor in user directories."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    )
)
def whitespace_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only processor in user directories."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def non_existent_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with non-existent processor in user directories."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="non_existent_processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def case_mismatch_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with case-mismatched processor in user directories."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="Keycloak_Processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def invalid_common_roles_configuration(self, node=None):
    """Configure ClickHouse with invalid common roles."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        common_roles=[""],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def whitespace_common_roles_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only common roles."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        common_roles=["   "],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def special_chars_common_roles_configuration(self, node=None):
    """Configure ClickHouse with special characters in common roles."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        common_roles=["role@#$%"],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def invalid_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with invalid roles filter regex."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        roles_filter="[invalid regex",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    )
)
def empty_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with empty roles filter."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        roles_filter="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    )
)
def whitespace_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only roles filter."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        roles_filter="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def malformed_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with malformed roles filter."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="keycloak",
        roles_filter="\\bkeycloak-[a-zA-Z0-9]+\\b\\",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserRoles_NoAccessTokenProcessors("1.0"),
)
def no_token_processors_configuration(self, node=None):
    """Configure ClickHouse without any token processors."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="empty_processor",
        processor_type=None,
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries(
        "1.0"
    )
)
def duplicate_processor_names_configuration(self, node=None):
    """Configure ClickHouse with duplicate processor names."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_duplicate",
        processor_type="keycloak",
        node=node,
    )
    change_token_processors(
        processor_name="keycloak_duplicate",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def invalid_processor_attributes_configuration(self, node=None):
    """Configure ClickHouse with invalid processor attributes."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_invalid_attrs",
        processor_type="keycloak",
        jwks_uri="invalid://url",
        jwks_cache_lifetime=-1,
        verifier_leeway="invalid",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    )
)
def missing_user_directories_configuration(self, node=None):
    """Configure ClickHouse with token processors but no user directories."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_no_user_dirs",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    )
)
def empty_user_directories_configuration(self, node=None):
    """Configure ClickHouse with empty user directories configuration."""
    from oauth.tests.steps.clikhouse import change_user_directories_config

    change_user_directories_config(
        processor="",
        common_roles=[],
        roles_filter="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def malformed_xml_structure_configuration(self, node=None):
    """Configure ClickHouse with malformed XML structure."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="<malformed>",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def null_values_configuration(self, node=None):
    """Configure ClickHouse with null values in configuration."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name=None,
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def extremely_long_values_configuration(self, node=None):
    """Configure ClickHouse with extremely long values."""
    from oauth.tests.steps.clikhouse import change_token_processors

    long_string = "a" * 10000
    change_token_processors(
        processor_name=long_string,
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def unicode_special_chars_configuration(self, node=None):
    """Configure ClickHouse with Unicode and special characters."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak_unicode_测试_🚀",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def sql_injection_attempt_configuration(self, node=None):
    """Configure ClickHouse with SQL injection attempt."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="keycloak'; DROP TABLE users; --",
        processor_type="keycloak",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def path_traversal_attempt_configuration(self, node=None):
    """Configure ClickHouse with path traversal attempt."""
    from oauth.tests.steps.clikhouse import change_token_processors

    change_token_processors(
        processor_name="../../../etc/passwd",
        processor_type="keycloak",
        node=node,
    )


# Combined negative configurations for comprehensive testing


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def completely_invalid_configuration(self, node=None):
    """Configure ClickHouse with completely invalid Keycloak configuration."""
    invalid_processor_type_configuration(self, node=node)
    missing_processor_user_directory_configuration(self, node=node)


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def partially_invalid_configuration(self, node=None):
    """Configure ClickHouse with partially invalid Keycloak configuration."""
    from oauth.tests.steps.clikhouse import (
        change_token_processors,
        change_user_directories_config,
    )

    change_token_processors(
        processor_name="keycloak_partial",
        processor_type="keycloak",
        node=node,
    )
    change_user_directories_config(
        processor="non_existent_processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    ),
)
def mixed_valid_invalid_configuration(self, node=None):
    """Configure ClickHouse with mixed valid and invalid configuration."""
    from oauth.tests.steps.clikhouse import (
        change_token_processors,
        change_user_directories_config,
    )

    change_token_processors(
        processor_name="keycloak_mixed",
        processor_type="keycloak",
        jwks_uri="invalid://url",
        node=node,
    )
    change_user_directories_config(
        processor="keycloak_mixed",
        common_roles=["valid_role", ""],
        node=node,
    )


class OAuthProvider:
    get_oauth_token = get_oauth_token
    create_application = import_keycloak_realm
    create_application_with_secret = import_keycloak_realm
    create_user = create_user
    create_group = create_group
    assign_user_to_group = assign_user_to_group

    # Negative configuration test steps
    invalid_processor_type_configuration = invalid_processor_type_configuration
    missing_processor_type_configuration = missing_processor_type_configuration
    empty_processor_type_configuration = empty_processor_type_configuration
    whitespace_processor_type_configuration = whitespace_processor_type_configuration
    case_sensitive_processor_type_configuration = (
        case_sensitive_processor_type_configuration
    )
    non_keycloak_processor_type_configuration = (
        non_keycloak_processor_type_configuration
    )
    invalid_processor_name_configuration = invalid_processor_name_configuration
    whitespace_processor_name_configuration = whitespace_processor_name_configuration
    special_chars_processor_name_configuration = (
        special_chars_processor_name_configuration
    )
    missing_processor_user_directory_configuration = (
        missing_processor_user_directory_configuration
    )
    whitespace_processor_user_directory_configuration = (
        whitespace_processor_user_directory_configuration
    )
    non_existent_processor_user_directory_configuration = (
        non_existent_processor_user_directory_configuration
    )
    case_mismatch_processor_user_directory_configuration = (
        case_mismatch_processor_user_directory_configuration
    )
    invalid_common_roles_configuration = invalid_common_roles_configuration
    whitespace_common_roles_configuration = whitespace_common_roles_configuration
    special_chars_common_roles_configuration = special_chars_common_roles_configuration
    invalid_roles_filter_configuration = invalid_roles_filter_configuration
    empty_roles_filter_configuration = empty_roles_filter_configuration
    whitespace_roles_filter_configuration = whitespace_roles_filter_configuration
    malformed_roles_filter_configuration = malformed_roles_filter_configuration
    no_token_processors_configuration = no_token_processors_configuration
    duplicate_processor_names_configuration = duplicate_processor_names_configuration
    invalid_processor_attributes_configuration = (
        invalid_processor_attributes_configuration
    )
    missing_user_directories_configuration = missing_user_directories_configuration
    empty_user_directories_configuration = empty_user_directories_configuration
    malformed_xml_structure_configuration = malformed_xml_structure_configuration
    null_values_configuration = null_values_configuration
    extremely_long_values_configuration = extremely_long_values_configuration
    unicode_special_chars_configuration = unicode_special_chars_configuration
    sql_injection_attempt_configuration = sql_injection_attempt_configuration
    path_traversal_attempt_configuration = path_traversal_attempt_configuration
    completely_invalid_configuration = completely_invalid_configuration
    partially_invalid_configuration = partially_invalid_configuration
    mixed_valid_invalid_configuration = mixed_valid_invalid_configuration
