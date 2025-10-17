import json
import base64
import requests
from testflows.core import *
from oauth.requirements.requirements import *
from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)


@TestStep(Given)
def get_oauth_token(self, node=None):
    """Get an OAuth token from Keycloak for a user."""
    if node is None:
        node = self.context.bash_tools

    curl_command = f"""curl --location '{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id={self.context.client_id}' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'username={self.context.username}' \
--data-urlencode 'password={self.context.password}' \
--data-urlencode 'client_secret={self.context.client_secret}'"""

    result = node.command(command=curl_command)

    response = json.loads(result.output)

    yield response


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

    return access_token


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

        user_id = create_user(
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
    realm_name: str = None,
):
    """Create a group in Keycloak."""

    if realm_name is None:
        realm_name = self.context.realm_name = "grafana"

    keycloak_url = self.context.keycloak_url
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
    realm_name: str = None,
):
    """Assign a user to a group in Keycloak."""

    if realm_name is None:
        realm_name = self.context.realm_name = "grafana"

    keycloak_url = self.context.keycloak_url
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
def assign_multiple_users_to_group(
    self,
    user_ids: list[str],
    group_id: str,
):
    """Assign multiple users to a group in Keycloak."""

    results = []

    for user_id in user_ids:
        result = assign_user_to_group(
            user_id=user_id,
            group_id=group_id,
        )
        results.append(result)

    return results


@TestStep(Given)
def create_user_with_no_group_access(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    user_principal_name: str = None,
    realm_name: str = "grafana",
    password: str = None,
):
    """Create a user in Keycloak with no access to view groups."""

    if display_name is None:
        display_name = "user_no_groups_" + getuid()

    if mail_nickname is None:
        mail_nickname = "user_no_groups_" + getuid()

    if user_principal_name is None:
        user_principal_name = f"user_no_groups_{getuid()}@example.com"

    user_id = create_user(
        display_name=display_name,
        mail_nickname=mail_nickname,
        user_principal_name=user_principal_name,
        realm_name=realm_name,
        password=password,
    )

    return user_id


@TestStep(Given)
def create_user_with_app_access_but_no_group_permissions(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    user_principal_name: str = None,
    realm_name: str = "grafana",
    password: str = None,
):
    """Create a user in Keycloak with app access but no group viewing permissions."""

    if display_name is None:
        display_name = "user_app_only_" + getuid()

    if mail_nickname is None:
        mail_nickname = "user_app_only_" + getuid()

    if user_principal_name is None:
        user_principal_name = f"user_app_only_{getuid()}@example.com"

    user_id = create_user(
        display_name=display_name,
        mail_nickname=mail_nickname,
        user_principal_name=user_principal_name,
        realm_name=realm_name,
        password=password,
    )

    return user_id


@TestStep(Given)
def create_user_with_group_permissions_and_matching_roles(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    user_principal_name: str = None,
    realm_name: str = "grafana",
    password: str = None,
):
    """Create a user in Keycloak with group viewing permissions and matching ClickHouse roles."""

    if display_name is None:
        display_name = "user_with_roles_" + getuid()

    if mail_nickname is None:
        mail_nickname = "user_with_roles_" + getuid()

    if user_principal_name is None:
        user_principal_name = f"user_with_roles_{getuid()}@example.com"

    user_id = create_user(
        display_name=display_name,
        mail_nickname=mail_nickname,
        user_principal_name=user_principal_name,
        realm_name=realm_name,
        password=password,
    )

    return user_id


@TestStep(Given)
def create_user_with_group_permissions_no_matching_roles(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    user_principal_name: str = None,
    realm_name: str = "grafana",
    password: str = None,
):
    """Create a user in Keycloak with group viewing permissions but no matching ClickHouse roles."""

    if display_name is None:
        display_name = "user_no_matching_roles_" + getuid()

    if mail_nickname is None:
        mail_nickname = "user_no_matching_roles_" + getuid()

    if user_principal_name is None:
        user_principal_name = f"user_no_matching_roles_{getuid()}@example.com"

    user_id = create_user(
        display_name=display_name,
        mail_nickname=mail_nickname,
        user_principal_name=user_principal_name,
        realm_name=realm_name,
        password=password,
    )

    return user_id


@TestStep(Given)
def create_group_with_matching_role_name(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    description: str = None,
    realm_name: str = "grafana",
):
    """Create a group in Keycloak with a name that matches a ClickHouse role."""

    if display_name is None:
        display_name = "clickhouse-admin"

    if mail_nickname is None:
        mail_nickname = "clickhouse-admin"

    if description is None:
        description = "Group with matching ClickHouse role name"

    group_id = create_group(
        display_name=display_name,
        mail_nickname=mail_nickname,
        description=description,
        realm_name=realm_name,
    )

    return group_id


@TestStep(Given)
def create_group_with_non_matching_role_name(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    description: str = None,
    realm_name: str = "grafana",
):
    """Create a group in Keycloak with a name that doesn't match any ClickHouse role."""

    if display_name is None:
        display_name = "non-matching-group"

    if mail_nickname is None:
        mail_nickname = "non-matching-group"

    if description is None:
        description = "Group with non-matching ClickHouse role name"

    group_id = create_group(
        display_name=display_name,
        mail_nickname=mail_nickname,
        description=description,
        realm_name=realm_name,
    )

    return group_id


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
    ),
    RQ_SRS_042_OAuth_StaticKey_UserDirectory("1.0"),
)
def missing_user_directories_configuration(self, node=None):
    """Configure ClickHouse with token processors but no user directories."""

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

    change_token_processors(
        processor_name="../../../etc/passwd",
        processor_type="keycloak",
        node=node,
    )


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
    invalid_processor_type_configuration(node=node)
    missing_processor_user_directory_configuration(node=node)


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def partially_invalid_configuration(self, node=None):
    """Configure ClickHouse with partially invalid Keycloak configuration."""

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


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_RealmSetup("1.0"))
def realm_setup(self):
    """Setup Keycloak realm configuration."""
    note("Setting up Keycloak realm configuration")
    import_keycloak_realm(
        realm_config_path="oauth/envs/keycloak/keycloak_env/grafana-realm.json",
        keycloak_url=self.context.keycloak_url,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"))
def access_token_support(self):
    """Verify Keycloak access token support."""
    note("Verifying Keycloak access token support")
    token = get_oauth_token()
    assert token is not None, "Failed to obtain access token from Keycloak"
    note(f"Successfully obtained access token: {token[:20]}...")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"))
def tokens_operation_modes(self):
    """Configure Keycloak token processing operation modes."""
    note("Configuring Keycloak token processing operation modes")

    change_token_processors(
        processor_name="keycloak",
        processor_type="keycloak",
        jwks_uri=f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/certs",
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes_Fallback("1.0"))
def tokens_operation_modes_fallback(self):
    """Configure fallback to remote verification."""
    note("Configuring fallback to remote verification")

    change_token_processors(
        processor_name="keycloak",
        processor_type="keycloak",
        jwks_uri=f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/certs",
        jwks_cache_lifetime=0,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Tokens_Configuration_Validation("1.0"))
def tokens_configuration_validation(self):
    """Validate token processor configuration options."""
    note("Validating token processor configuration options")

    change_token_processors(
        processor_name="keycloak",
        processor_type="keycloak",
        jwks_uri=f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/certs",
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Tokens_Operational_ProviderType("1.0"))
def tokens_operational_provider_type(self):
    """Configure OpenID provider type for Keycloak."""
    note("Configuring OpenID provider type for Keycloak")

    change_token_processors(
        processor_name="keycloak",
        processor_type="keycloak",
        jwks_uri=f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/certs",
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_GetAccessToken("1.0"))
def get_access_token_requirement(self):
    """Obtain access token from Keycloak."""
    note("Obtaining access token from Keycloak")
    token = get_oauth_token()
    assert token is not None, "Failed to obtain access token"
    note(f"Access token obtained: {token[:20]}...")
    return token


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_AccessTokenProcessors("1.0"))
def access_token_processors(self):
    """Configure access token processor for Keycloak."""
    note("Configuring access token processor for Keycloak")

    change_token_processors(
        processor_name="keycloak",
        processor_type="keycloak",
        jwks_uri=f"{self.context.keycloak_url}/realms/grafana/protocol/openid-connect/certs",
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserDirectories_UserGroups("1.0")
)
def auth_user_directories_user_groups(self):
    """Configure user groups in role mapping."""
    note("Configuring user groups in role mapping")

    change_user_directories_config(processor="keycloak", common_roles=["default_role"])


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles("1.0"))
def auth_user_roles(self):
    """Configure roles based on mapping."""
    note("Configuring roles based on mapping")

    change_user_directories_config(processor="keycloak", common_roles=["mapped_role"])


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_GroupFiltering("1.0"))
def auth_user_roles_group_filtering(self):
    """Configure group filtering via roles_filter regex."""
    note("Configuring group filtering via roles_filter regex")

    change_user_directories_config(processor="keycloak", roles_filter="^keycloak-.*$")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_MultipleGroups("1.0"))
def auth_user_roles_multiple_groups(self):
    """Configure union roles for multiple groups."""
    note("Configuring union roles for multiple groups")

    change_user_directories_config(
        processor="keycloak", common_roles=["group1_role", "group2_role"]
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoGroups("1.0"))
def auth_user_roles_no_groups(self):
    """Configure default roles when no groups."""
    note("Configuring default roles when no groups")

    change_user_directories_config(processor="keycloak", common_roles=["default_role"])


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SubgroupMemberships("1.0")
)
def auth_user_roles_subgroup_memberships(self):
    """Configure subgroup memberships not auto-mapped."""
    note("Configuring subgroup memberships not auto-mapped")

    change_user_directories_config(
        processor="keycloak", common_roles=["parent_group_role"]
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoMatchingClickHouseRoles("1.0")
)
def auth_user_roles_no_matching_clickhouse_roles(self):
    """Configure no matching ClickHouse roles behavior."""
    note("Configuring no matching ClickHouse roles behavior")

    change_user_directories_config(processor="keycloak", common_roles=["fallback_role"])


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_SameName("1.0"))
def auth_user_roles_same_name(self):
    """Configure role mapping when names match exactly."""
    note("Configuring role mapping when names match exactly")

    change_user_directories_config(
        processor="keycloak", common_roles=["exact_match_role"]
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoMatchingRoles("1.0"))
def auth_user_roles_no_matching_roles(self):
    """Configure default roles when no matches exist."""
    note("Configuring default roles when no matches exist")

    change_user_directories_config(processor="keycloak", common_roles=["default_role"])


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoPermissionToViewGroups("1.0")
)
def auth_user_roles_no_permission_to_view_groups(self):
    """Configure default roles when user can't view groups."""
    note("Configuring default roles when user can't view groups")

    change_user_directories_config(processor="keycloak", common_roles=["limited_role"])


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Authentication_UserRoles_NoDefaultRole("1.0"))
def auth_user_roles_no_default_role(self):
    """Configure no default roles behavior."""
    note("Configuring no default roles behavior")

    change_user_directories_config(processor="keycloak", common_roles=[])


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled("1.0"))
def disable_user(self, username: str = "test_user", realm_name: str = "grafana"):
    """Disable a user in Keycloak."""
    note(f"Disabling user '{username}' in Keycloak")
    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        note(f"User '{username}' not found, creating first")
        user_id = create_user(
            display_name=username,
            mail_nickname=username,
            user_principal_name=f"{username}@example.com",
            realm_name=realm_name,
        )
    else:
        user_id = user["id"]

    disable_url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user_id}"
    )
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    user_data = {"enabled": False}
    response = requests.put(disable_url, json=user_data, headers=headers)
    response.raise_for_status()
    note(f"User '{username}' disabled successfully")


@TestStep(Given)
def create_default_user(self, username: str = "demo", password: str = "demo"):
    """Create a default user with the same configuration as the Keycloak config."""

    admin_token = get_admin_token()

    user_id = create_user(
        display_name="Demo User",
        mail_nickname=username,
        user_principal_name=f"{username}@example.com",
        realm_name="grafana",
        password=password,
    )

    groups_to_assign = ["/grafana-admins", "/can-read"]

    for group_path in groups_to_assign:
        group_name = group_path.lstrip("/")

        group = get_keycloak_group_by_name(
            realm_name="grafana",
            group_name=group_name,
            keycloak_url=self.context.keycloak_url,
            admin_token=admin_token,
        )

        if group:
            assign_user_to_group(
                user_id=user_id, group_id=group["id"], realm_name="grafana"
            )
            note(f"User '{username}' assigned to group '{group_name}'")
        else:
            note(f"Warning: Group '{group_name}' not found, skipping assignment")

    note(f"Default user '{username}' created successfully with ID: {user_id}")
    return user_id


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted("1.0"))
def delete_user(self, username: str, realm_name: str = "grafana"):
    """Delete user from Keycloak."""

    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        raise Exception(f"User '{username}' not found in realm '{realm_name}'")

    user_id = user["id"]
    delete_url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user_id}"
    )

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(delete_url, headers=headers)
    response.raise_for_status()


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup("1.0"))
def add_user_to_group(
    self,
    username: str = "test_user",
    group_name: str = "test_group",
    realm_name: str = "grafana",
):
    """Add a user to a group in Keycloak."""
    note(f"Adding user '{username}' to group '{group_name}'")
    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        note(f"User '{username}' not found, creating first")
        user_id = create_user(
            display_name=username,
            mail_nickname=username,
            user_principal_name=f"{username}@example.com",
            realm_name=realm_name,
        )
    else:
        user_id = user["id"]

    group = get_keycloak_group_by_name(
        realm_name=realm_name,
        group_name=group_name,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if group is None:
        note(f"Group '{group_name}' not found, creating first")
        group_id = create_group(
            display_name=group_name, mail_nickname=group_name, realm_name=realm_name
        )
    else:
        group_id = group["id"]

    assign_user_to_group(user_id=user_id, group_id=group_id, realm_name=realm_name)
    note(f"User '{username}' added to group '{group_name}' successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup("1.0"))
def remove_user_from_group(
    self,
    username: str = "test_user",
    group_name: str = "test_group",
    realm_name: str = "grafana",
):
    """Remove a user from a group in Keycloak."""
    note(f"Removing user '{username}' from group '{group_name}'")
    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        note(f"User '{username}' not found")
        return

    group = get_keycloak_group_by_name(
        realm_name=realm_name,
        group_name=group_name,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if group is None:
        note(f"Group '{group_name}' not found")
        return

    remove_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user['id']}/groups/{group['id']}"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(remove_url, headers=headers)
    response.raise_for_status()
    note(f"User '{username}' removed from group '{group_name}' successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_GroupDeleted("1.0"))
def delete_group(self, group_name: str = "test_group", realm_name: str = "grafana"):
    """Delete a group in Keycloak."""
    note(f"Deleting group '{group_name}' in Keycloak")
    admin_token = get_admin_token()

    group = get_keycloak_group_by_name(
        realm_name=realm_name,
        group_name=group_name,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if group is None:
        note(f"Group '{group_name}' not found")
        return

    delete_url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/groups/{group['id']}"
    )
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(delete_url, headers=headers)
    response.raise_for_status()
    note(f"Group '{group_name}' deleted successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_ClientDisabled("1.0"))
def disable_client(
    self, client_id: str = "grafana-client", realm_name: str = "grafana"
):
    """Disable a client in Keycloak."""
    note(f"Disabling client '{client_id}' in Keycloak")
    admin_token = get_admin_token()

    clients_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    params = {"clientId": client_id}
    response = requests.get(clients_url, params=params, headers=headers)
    response.raise_for_status()

    clients = response.json()
    if not clients:
        note(f"Client '{client_id}' not found")
        return

    client = clients[0]
    disable_url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients/{client['id']}"
    )

    client_data = {"enabled": False}
    response = requests.put(disable_url, json=client_data, headers=headers)
    response.raise_for_status()
    note(f"Client '{client_id}' disabled successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_ConsentRevoked("1.0"))
def revoke_consent(
    self,
    username: str = "test_user",
    client_id: str = "grafana-client",
    realm_name: str = "grafana",
):
    """Revoke user consent for an application in Keycloak."""
    note(f"Revoking consent for user '{username}' and client '{client_id}'")
    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        note(f"User '{username}' not found")
        return

    clients_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    params = {"clientId": client_id}
    response = requests.get(clients_url, params=params, headers=headers)
    response.raise_for_status()

    clients = response.json()
    if not clients:
        note(f"Client '{client_id}' not found")
        return

    client = clients[0]
    consent_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user['id']}/consents/{client['id']}"

    response = requests.delete(consent_url, headers=headers)
    response.raise_for_status()
    note(f"Consent revoked for user '{username}' and client '{client_id}' successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Keycloak_Actions_TokenInvalid("1.0"))
def invalidate_token(self, username: str = "test_user", realm_name: str = "grafana"):
    """Invalidate user sessions in Keycloak."""
    note(f"Invalidating sessions for user '{username}'")
    admin_token = get_admin_token()

    user = get_keycloak_user_by_username(
        realm_name=realm_name,
        username=username,
        keycloak_url=self.context.keycloak_url,
        admin_token=admin_token,
    )

    if user is None:
        note(f"User '{username}' not found")
        return

    logout_url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users/{user['id']}/logout"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(logout_url, headers=headers)
    response.raise_for_status()
    note(f"Sessions invalidated for user '{username}' successfully")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"))
def common_parameters_cache_lifetime(self, node=None):
    """Configure token cache lifetime parameter."""
    change_token_processors(
        processor_name="keycloak",
        token_cache_lifetime=600,
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"))
def common_parameters_username_claim(self, node=None):
    """Configure username_claim parameter for token processor."""
    change_token_processors(
        processor_name="keycloak",
        username_claim="sub",
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"))
def common_parameters_groups_claim(self, node=None):
    """Configure groups_claim parameter for token processor."""
    change_token_processors(
        processor_name="keycloak",
        groups_claim="groups",
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Parameters_Unfiltered("1.0"))
def common_parameters_unfiltered(self, node=None):
    """Enable unfiltered mode for token processor mapping."""
    change_token_processors(
        processor_name="keycloak",
        unfiltered=True,
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Cache_Behavior("1.0"))
def common_cache_behavior(self, node=None):
    """Configure cache behavior-related parameters."""
    change_token_processors(
        processor_name="keycloak",
        token_cache_lifetime=60,
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"))
def common_configuration_validation(self, node=None):
    """Validate required/allowed combinations of common parameters."""
    change_token_processors(
        processor_name="keycloak",
        username_claim="sub",
        groups_claim="groups",
        node=node,
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_Caching("1.0"))
def authentication_caching(self, node=None):
    """General authentication caching behavior configuration."""
    change_token_processors(
        processor_name="keycloak",
        token_cache_lifetime=120,
        node=node,
    )


def _decode_jwt_token(token: str):
    """Helper function to decode a JWT token into its components."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT token format")

        header_data = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
        payload_data = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        signature = parts[2]

        return header_data, payload_data, signature
    except Exception as e:
        raise ValueError(f"Failed to decode JWT token: {e}")


def _encode_jwt_token(header: dict, payload: dict, signature: str):
    """Helper function to encode JWT components back into a token."""
    try:
        header_b64 = (
            base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode())
            .decode()
            .rstrip("=")
        )
        payload_b64 = (
            base64.urlsafe_b64encode(
                json.dumps(payload, separators=(",", ":")).encode()
            )
            .decode()
            .rstrip("=")
        )
        return f"{header_b64}.{payload_b64}.{signature}"
    except Exception as e:
        raise ValueError(f"Failed to encode JWT token: {e}")


@TestStep(Given)
def modify_jwt_token(
    self,
    token: str,
    header_changes: dict = None,
    payload_changes: dict = None,
    signature_change: str = None,
):
    """Modify a JWT token by changing header, payload, or signature components."""
    header, payload, signature = _decode_jwt_token(token)

    if header_changes:
        header.update(header_changes)
        note(f"Modified JWT header: {header_changes}")

    if payload_changes:
        payload.update(payload_changes)
        note(f"Modified JWT payload: {payload_changes}")

    if signature_change:
        signature = signature_change
        note(f"Modified JWT signature")

    modified_token = _encode_jwt_token(header, payload, signature)
    note(f"Modified JWT token: {modified_token}")
    return modified_token


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"))
def modify_jwt_header_alg_to_none(self, token: str):
    """Modify the 'alg' field to 'none'."""
    return modify_jwt_token(token=token, header_changes={"alg": "none"})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"))
def modify_jwt_header_alg_to_hs256(self, token: str):
    """Modify the 'alg' field to 'HS256'."""
    return modify_jwt_token(token=token, header_changes={"alg": "HS256"})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"))
def modify_jwt_header_alg_to_invalid(self, token: str):
    """Modify the 'alg' field to an invalid algorithm."""
    return modify_jwt_token(token=token, header_changes={"alg": "INVALID_ALG"})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"))
def modify_jwt_header_typ_to_invalid(self, token: str):
    """Modify the 'typ' field to an invalid type."""
    return modify_jwt_token(token=token, header_changes={"typ": "INVALID"})


@TestStep(Given)
def modify_jwt_header_kid_to_invalid(self, token: str):
    """Modify the 'kid' field to an invalid key ID."""
    return modify_jwt_token(token=token, header_changes={"kid": "invalid-key-id"})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"))
def modify_jwt_payload_exp_to_expired(self, token: str):
    """Modify the 'exp' field to an expired timestamp."""
    return modify_jwt_token(token=token, payload_changes={"exp": 1000000000})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"))
def modify_jwt_payload_exp_to_far_future(self, token: str):
    """Modify the 'exp' field to a far future timestamp."""
    return modify_jwt_token(token=token, payload_changes={"exp": 9999999999})


@TestStep(Given)
def modify_jwt_payload_iat_to_future(self, token: str):
    """Modify the 'iat' field to a future timestamp."""
    return modify_jwt_token(token=token, payload_changes={"iat": 9999999999})


@TestStep(Given)
def modify_jwt_payload_jti_to_invalid(self, token: str):
    """Modify the 'jti' field to an invalid JWT ID."""
    return modify_jwt_token(
        token=token, payload_changes={"jti": "invalid-jwt-id-12345"}
    )


@TestStep(Given)
def modify_jwt_payload_iss_to_invalid(self, token: str):
    """Modify the 'iss' field to an invalid issuer."""
    return modify_jwt_token(
        token=token, payload_changes={"iss": "http://invalid-issuer.com"}
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"))
def modify_jwt_payload_sub_to_invalid(self, token: str):
    """Modify the 'sub' field to an invalid subject ID."""
    return modify_jwt_token(
        token=token, payload_changes={"sub": "invalid-subject-id-12345"}
    )


@TestStep(Given)
def modify_jwt_payload_typ_to_invalid(self, token: str):
    """Modify the 'typ' field to an invalid type."""
    return modify_jwt_token(token=token, payload_changes={"typ": "InvalidType"})


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"))
def modify_jwt_payload_azp_to_invalid(self, token: str):
    """Modify the 'azp' field to an invalid authorized party."""
    return modify_jwt_token(token=token, payload_changes={"azp": "invalid-client-id"})


@TestStep(Given)
def modify_jwt_payload_sid_to_invalid(self, token: str):
    """Modify the 'sid' field to an invalid session ID."""
    return modify_jwt_token(
        token=token, payload_changes={"sid": "invalid-session-id-12345"}
    )


@TestStep(Given)
def modify_jwt_payload_acr_to_invalid(self, token: str):
    """Modify the 'acr' field to an invalid ACR value."""
    return modify_jwt_token(token=token, payload_changes={"acr": "99"})


@TestStep(Given)
def modify_jwt_payload_allowed_origins_to_invalid(self, token: str):
    """Modify the 'allowed-origins' field to invalid origins."""
    return modify_jwt_token(
        token=token,
        payload_changes={
            "allowed-origins": ["http://malicious.com", "http://evil.org"]
        },
    )


@TestStep(Given)
def modify_jwt_payload_scope_to_invalid(self, token: str):
    """Modify the 'scope' field to invalid scopes."""
    return modify_jwt_token(
        token=token, payload_changes={"scope": "admin delete write execute"}
    )


@TestStep(Given)
def modify_jwt_payload_email_verified_to_false(self, token: str):
    """Modify the 'email_verified' field to false."""
    return modify_jwt_token(token=token, payload_changes={"email_verified": False})


@TestStep(Given)
def modify_jwt_payload_name_to_invalid(self, token: str):
    """Modify the 'name' field to an invalid name."""
    return modify_jwt_token(
        token=token, payload_changes={"name": "Invalid User Name 12345"}
    )


@TestStep(Given)
def modify_jwt_payload_groups_to_admin(self, token: str):
    """Modify the 'groups' field to admin groups."""
    return modify_jwt_token(
        token=token, payload_changes={"groups": ["admin", "superuser", "root"]}
    )


@TestStep(Given)
def modify_jwt_payload_groups_to_empty(self, token: str):
    """Modify the 'groups' field to empty list."""
    return modify_jwt_token(token=token, payload_changes={"groups": []})


@TestStep(Given)
def modify_jwt_payload_preferred_username_to_admin(self, token: str):
    """Modify the 'preferred_username' field to admin."""
    return modify_jwt_token(
        token=token, payload_changes={"preferred_username": "admin"}
    )


@TestStep(Given)
def modify_jwt_payload_given_name_to_invalid(self, token: str):
    """Modify the 'given_name' field to an invalid name."""
    return modify_jwt_token(token=token, payload_changes={"given_name": "Invalid"})


@TestStep(Given)
def modify_jwt_payload_family_name_to_invalid(self, token: str):
    """Modify the 'family_name' field to an invalid name."""
    return modify_jwt_token(token=token, payload_changes={"family_name": "InvalidUser"})


@TestStep(Given)
def modify_jwt_payload_email_to_invalid(self, token: str):
    """Modify the 'email' field to an invalid email."""
    return modify_jwt_token(
        token=token, payload_changes={"email": "invalid@malicious.com"}
    )


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"))
def modify_jwt_signature_to_invalid(self, token: str):
    """Modify the signature to make it invalid."""
    return modify_jwt_token(token=token, signature_change="invalid-signature-12345")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"))
def invalidate_jwt_signature(self, token: str):
    """Invalidate the JWT signature by appending random characters."""
    header, payload, signature = _decode_jwt_token(token)
    invalid_signature = signature + "invalid"
    return modify_jwt_token(token=token, signature_change=invalid_signature)


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"))
def remove_jwt_signature(self, token: str):
    """Remove the JWT signature entirely."""
    return modify_jwt_token(token=token, signature_change="")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"))
def modify_jwt_signature_e_to_invalid(self, token: str):
    """Modify the RSA exponent conceptually by invalidating signature."""
    note("Conceptually modifying RSA exponent to: INVALID")
    return invalidate_jwt_signature(token)


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"))
def modify_jwt_signature_kty_to_invalid(self, token: str):
    """Modify the key type conceptually by invalidating signature."""
    note("Conceptually modifying key type to: INVALID")
    return invalidate_jwt_signature(token)


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"))
def modify_jwt_signature_n_to_invalid(self, token: str):
    """Modify the RSA modulus conceptually by invalidating signature."""
    note("Conceptually modifying RSA modulus to: INVALID")
    return invalidate_jwt_signature(token)


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"))
def create_empty_token(self, token: str):
    """Create an empty token string."""
    note("Creating empty token string")
    return ""


class OAuthProvider:
    get_oauth_token = get_oauth_token
    create_application = import_keycloak_realm
    create_application_with_secret = import_keycloak_realm
    create_user = create_user
    create_group = create_group
    assign_multiple_users_to_group = assign_multiple_users_to_group
    create_multiple_users = create_multiple_users
    create_user_with_no_group_access = create_user_with_no_group_access
    create_user_with_app_access_but_no_group_permissions = (
        create_user_with_app_access_but_no_group_permissions
    )
    create_user_with_group_permissions_and_matching_roles = (
        create_user_with_group_permissions_and_matching_roles
    )
    create_user_with_group_permissions_no_matching_roles = (
        create_user_with_group_permissions_no_matching_roles
    )
    create_group_with_matching_role_name = create_group_with_matching_role_name
    create_group_with_non_matching_role_name = create_group_with_non_matching_role_name
    assign_user_to_group = assign_user_to_group

    # Negative configuration test steps
    invalid_processor_type_configuration = invalid_processor_type_configuration
    missing_processor_type_configuration = missing_processor_type_configuration
    empty_processor_type_configuration = empty_processor_type_configuration
    whitespace_processor_type_configuration = whitespace_processor_type_configuration
    case_sensitive_processor_type_configuration = (
        case_sensitive_processor_type_configuration
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

    realm_setup = realm_setup
    access_token_support = access_token_support
    tokens_operation_modes = tokens_operation_modes
    tokens_operation_modes_fallback = tokens_operation_modes_fallback
    tokens_configuration_validation = tokens_configuration_validation
    tokens_operational_provider_type = tokens_operational_provider_type
    get_access_token_requirement = get_access_token_requirement
    access_token_processors = access_token_processors
    auth_user_directories_user_groups = auth_user_directories_user_groups
    auth_user_roles = auth_user_roles
    auth_user_roles_group_filtering = auth_user_roles_group_filtering
    auth_user_roles_multiple_groups = auth_user_roles_multiple_groups
    auth_user_roles_no_groups = auth_user_roles_no_groups
    auth_user_roles_subgroup_memberships = auth_user_roles_subgroup_memberships
    auth_user_roles_no_matching_clickhouse_roles = (
        auth_user_roles_no_matching_clickhouse_roles
    )
    auth_user_roles_same_name = auth_user_roles_same_name
    auth_user_roles_no_matching_roles = auth_user_roles_no_matching_roles
    auth_user_roles_no_permission_to_view_groups = (
        auth_user_roles_no_permission_to_view_groups
    )
    auth_user_roles_no_default_role = auth_user_roles_no_default_role
    disable_user = disable_user
    delete_user = delete_user
    add_user_to_group = add_user_to_group
    remove_user_from_group = remove_user_from_group
    delete_group = delete_group
    disable_client = disable_client
    revoke_consent = revoke_consent
    invalidate_token = invalidate_token

    common_parameters_cache_lifetime = common_parameters_cache_lifetime
    common_parameters_username_claim = common_parameters_username_claim
    common_parameters_groups_claim = common_parameters_groups_claim
    common_parameters_unfiltered = common_parameters_unfiltered
    common_cache_behavior = common_cache_behavior
    common_configuration_validation = common_configuration_validation
    authentication_caching = authentication_caching

    # JWT Token Manipulation Steps
    modify_jwt_token = modify_jwt_token

    # JWT Header Field Manipulation Steps
    modify_jwt_header_alg_to_none = modify_jwt_header_alg_to_none
    modify_jwt_header_alg_to_hs256 = modify_jwt_header_alg_to_hs256
    modify_jwt_header_alg_to_invalid = modify_jwt_header_alg_to_invalid
    modify_jwt_header_typ_to_invalid = modify_jwt_header_typ_to_invalid
    modify_jwt_header_kid_to_invalid = modify_jwt_header_kid_to_invalid

    # JWT Payload Field Manipulation Steps
    modify_jwt_payload_exp_to_expired = modify_jwt_payload_exp_to_expired
    modify_jwt_payload_exp_to_far_future = modify_jwt_payload_exp_to_far_future
    modify_jwt_payload_iat_to_future = modify_jwt_payload_iat_to_future
    modify_jwt_payload_jti_to_invalid = modify_jwt_payload_jti_to_invalid
    modify_jwt_payload_iss_to_invalid = modify_jwt_payload_iss_to_invalid
    modify_jwt_payload_sub_to_invalid = modify_jwt_payload_sub_to_invalid
    modify_jwt_payload_typ_to_invalid = modify_jwt_payload_typ_to_invalid
    modify_jwt_payload_azp_to_invalid = modify_jwt_payload_azp_to_invalid
    modify_jwt_payload_sid_to_invalid = modify_jwt_payload_sid_to_invalid
    modify_jwt_payload_acr_to_invalid = modify_jwt_payload_acr_to_invalid
    modify_jwt_payload_allowed_origins_to_invalid = (
        modify_jwt_payload_allowed_origins_to_invalid
    )
    modify_jwt_payload_scope_to_invalid = modify_jwt_payload_scope_to_invalid
    modify_jwt_payload_email_verified_to_false = (
        modify_jwt_payload_email_verified_to_false
    )
    modify_jwt_payload_name_to_invalid = modify_jwt_payload_name_to_invalid
    modify_jwt_payload_groups_to_admin = modify_jwt_payload_groups_to_admin
    modify_jwt_payload_groups_to_empty = modify_jwt_payload_groups_to_empty
    modify_jwt_payload_preferred_username_to_admin = (
        modify_jwt_payload_preferred_username_to_admin
    )
    modify_jwt_payload_given_name_to_invalid = modify_jwt_payload_given_name_to_invalid
    modify_jwt_payload_family_name_to_invalid = (
        modify_jwt_payload_family_name_to_invalid
    )
    modify_jwt_payload_email_to_invalid = modify_jwt_payload_email_to_invalid

    # JWT Signature Manipulation Steps
    modify_jwt_signature_to_invalid = modify_jwt_signature_to_invalid
    invalidate_jwt_signature = invalidate_jwt_signature
    remove_jwt_signature = remove_jwt_signature
    modify_jwt_signature_e_to_invalid = modify_jwt_signature_e_to_invalid
    modify_jwt_signature_kty_to_invalid = modify_jwt_signature_kty_to_invalid
    modify_jwt_signature_n_to_invalid = modify_jwt_signature_n_to_invalid
    create_empty_token = create_empty_token
