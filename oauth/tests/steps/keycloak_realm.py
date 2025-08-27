import json
import requests
from testflows.core import *
from helpers.common import getuid


@TestStep(Given)
def get_oauth_token(self, username="demo", password="demo"):
    """Get an OAuth token from Keycloak for a user."""

    token_url = f"http://localhost:8080/realms/grafana/protocol/openid-connect/token"

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
    return token_data["access_token"]


@TestStep(Given)
def create_user(
    self,
    display_name: str,
    mail_nickname: str,
    user_principal_name: str,
    password: str = None,
):
    """Create a user in Keycloak."""

    realm_name = getattr(self.context, "realm_name", "grafana")
    keycloak_url = getattr(self.context, "keycloak_url", "http://localhost:8080")
    admin_token = getattr(self.context, "admin_token", None)

    if admin_token is None:
        admin_token = get_keycloak_admin_token(self, keycloak_url)

        self.context.admin_token = admin_token

    users_url = f"{keycloak_url}/admin/realms/{realm_name}/users"

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
        password_url = (
            f"{keycloak_url}/admin/realms/{realm_name}/users/{user_id}/reset-password"
        )
        password_data = {"type": "password", "value": password, "temporary": False}

        response = requests.put(password_url, json=password_data, headers=headers)
        response.raise_for_status()

    return user_id


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
        admin_token = get_keycloak_admin_token(self, keycloak_url)
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
        admin_token = get_keycloak_admin_token(self, keycloak_url)
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
        admin_token = get_keycloak_admin_token(self, keycloak_url)

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
        admin_token = get_keycloak_admin_token(self, keycloak_url)

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
        admin_token = get_keycloak_admin_token(self, keycloak_url)

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


class OAuthProvider:
    get_oauth_token = get_oauth_token
    create_application = import_keycloak_realm
    create_application_with_secret = import_keycloak_realm
    create_user = create_user
    create_group = create_group
    assign_user_to_group = assign_user_to_group
