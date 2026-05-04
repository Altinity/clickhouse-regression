import json
import base64
from testflows.core import *
from oauth.requirements.requirements import *
from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)


@TestStep(Given)
def get_oauth_token(self, node=None, username=None, password=None):
    """Get an OAuth token from Keycloak for a user via bash_tools curl.

    Yields the full JSON response dict (caller should extract ``["access_token"]``).
    Raises a clear error when Keycloak returns an error response (e.g.
    disabled user, wrong password) so callers don't get an opaque KeyError.
    """
    if node is None:
        node = self.context.bash_tools
    if username is None:
        username = self.context.username
    if password is None:
        password = self.context.password

    curl_command = (
        f"curl -s --location "
        f"'{self.context.keycloak_url}/realms/{self.context.realm_name}"
        f"/protocol/openid-connect/token' "
        f"--header 'Content-Type: application/x-www-form-urlencoded' "
        f"--data-urlencode 'client_id={self.context.client_id}' "
        f"--data-urlencode 'grant_type=password' "
        f"--data-urlencode 'username={username}' "
        f"--data-urlencode 'password={password}' "
        f"--data-urlencode 'client_secret={self.context.client_secret}'"
    )

    result = node.command(command=curl_command)

    try:
        response = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak token response for user '{username}': "
            f"{e}. Raw output: {result.output[:500]}"
        )

    if "error" in response:
        raise Exception(
            f"Keycloak token request failed for user '{username}': "
            f"{response.get('error')} — {response.get('error_description', '')}"
        )

    yield response


@TestStep(Given)
def get_admin_token(self):
    """Get an admin token from Keycloak using the admin master realm.

    Returns an access token string suitable for Keycloak Admin REST API.
    """
    node = self.context.bash_tools

    curl_command = (
        f"curl -s --location "
        f"'{self.context.keycloak_url}/realms/master/protocol/openid-connect/token' "
        f"--header 'Content-Type: application/x-www-form-urlencoded' "
        f"--data-urlencode 'client_id=admin-cli' "
        f"--data-urlencode 'grant_type=password' "
        f"--data-urlencode 'username=admin' "
        f"--data-urlencode 'password=admin'"
    )

    result = node.command(command=curl_command)

    try:
        token_data = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak admin token response: {e}. "
            f"Raw output: {result.output[:500]}"
        )

    if "access_token" not in token_data:
        raise Exception(
            f"Keycloak admin token request failed: "
            f"{token_data.get('error', 'unknown')} — "
            f"{token_data.get('error_description', result.output[:200])}"
        )

    return token_data["access_token"]


@TestStep(Given)
def keycloak_admin_request(self, method, path, json_data=None, expected_statuses=None):
    """Execute an authenticated request against the Keycloak Admin REST API.

    Uses bash_tools curl to stay inside the Docker network.
    Returns (status_code, response_body_string).
    """
    node = self.context.bash_tools
    admin_token = get_admin_token()

    url = f"{self.context.keycloak_url}{path}"
    uid = getuid()[:8]
    tmp_file = f"/tmp/kc_resp_{uid}.txt"

    curl_cmd = (
        f"curl -s -o {tmp_file} -w '%{{http_code}}' "
        f"-X {method.upper()} "
        f"'{url}' "
        f"-H 'Authorization: Bearer {admin_token}' "
        f"-H 'Content-Type: application/json'"
    )

    if json_data is not None:
        payload = json.dumps(json_data).replace("'", "'\\''")
        curl_cmd += f" -d '{payload}'"

    result = node.command(command=curl_cmd)

    output = result.output.strip()
    try:
        status = int(output[-3:])
    except (ValueError, IndexError):
        raise Exception(
            f"Keycloak API {method} {path}: could not parse HTTP status "
            f"from curl output: {output[:200]}"
        )

    body_result = node.command(command=f"cat {tmp_file}")
    body = body_result.output.strip()

    if expected_statuses is not None:
        assert status in expected_statuses, (
            f"Keycloak API {method} {path}: expected {expected_statuses}, "
            f"got {status}. Body: {body}"
        )

    return status, body


@TestStep(Given)
def create_user(
    self,
    username,
    password=None,
    first_name=None,
    last_name=None,
    email=None,
    realm_name=None,
):
    """Create a user in Keycloak. Returns the user ID.

    Uses the Keycloak Admin REST API to create the user. Extracts the
    user ID from the ``Location`` response header returned by Keycloak
    on successful creation (HTTP 201).
    """
    if realm_name is None:
        realm_name = self.context.realm_name

    if email is None:
        email = f"{username}@example.com"
    if first_name is None:
        first_name = username
    if last_name is None:
        last_name = "User"

    user_data = {
        "username": username,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "enabled": True,
        "emailVerified": True,
    }

    if password is not None:
        user_data["credentials"] = [
            {"type": "password", "value": password, "temporary": False}
        ]

    node = self.context.bash_tools
    admin_token = get_admin_token()

    uid = getuid()[:8]
    headers_file = f"/tmp/kc_headers_{uid}.txt"
    resp_file = f"/tmp/kc_resp_{uid}.txt"

    url = f"{self.context.keycloak_url}/admin/realms/{realm_name}/users"
    payload = json.dumps(user_data).replace("'", "'\\''")

    curl_cmd = (
        f"curl -s -D {headers_file} -o {resp_file} -w '%{{http_code}}' "
        f"-X POST '{url}' "
        f"-H 'Authorization: Bearer {admin_token}' "
        f"-H 'Content-Type: application/json' "
        f"-d '{payload}'"
    )

    result = node.command(command=curl_cmd)

    output = result.output.strip()
    try:
        status = int(output[-3:])
    except (ValueError, IndexError):
        raise Exception(
            f"Failed to parse HTTP status creating user '{username}': {output[:200]}"
        )

    if status != 201:
        body_result = node.command(command=f"cat {resp_file}")
        raise Exception(
            f"Failed to create user '{username}': HTTP {status}. "
            f"Body: {body_result.output.strip()[:500]}"
        )

    headers_result = node.command(command=f"cat {headers_file}")
    for line in headers_result.output.split("\n"):
        if line.lower().startswith("location:"):
            user_id = line.strip().split("/")[-1]
            return user_id

    raise Exception(f"No Location header in create-user response for '{username}'")


@TestStep(Given)
def delete_user(self, username, realm_name=None):
    """Delete a user from Keycloak by username."""
    if realm_name is None:
        realm_name = self.context.realm_name

    user = get_user_by_username(username=username, realm_name=realm_name)
    if user is None:
        raise Exception(f"User '{username}' not found in realm '{realm_name}'")

    keycloak_admin_request(
        method="DELETE",
        path=f"/admin/realms/{realm_name}/users/{user['id']}",
        expected_statuses=[204],
    )


@TestStep(Given)
def disable_user(self, username, realm_name=None):
    """Disable a user in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    user = get_user_by_username(username=username, realm_name=realm_name)
    if user is None:
        raise Exception(f"User '{username}' not found")

    keycloak_admin_request(
        method="PUT",
        path=f"/admin/realms/{realm_name}/users/{user['id']}",
        json_data={"enabled": False},
        expected_statuses=[204],
    )


@TestStep(Given)
def enable_user(self, username, realm_name=None):
    """Re-enable a user in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    user = get_user_by_username(username=username, realm_name=realm_name)
    if user is None:
        raise Exception(f"User '{username}' not found")

    keycloak_admin_request(
        method="PUT",
        path=f"/admin/realms/{realm_name}/users/{user['id']}",
        json_data={"enabled": True},
        expected_statuses=[204],
    )


@TestStep(Given)
def get_user_by_username(self, username, realm_name=None):
    """Look up a Keycloak user by exact username. Returns dict or None."""
    if realm_name is None:
        realm_name = self.context.realm_name

    node = self.context.bash_tools
    admin_token = get_admin_token()

    url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/users"
        f"?username={username}&exact=true"
    )

    curl_cmd = f"curl -s '{url}' -H 'Authorization: Bearer {admin_token}'"

    result = node.command(command=curl_cmd)

    try:
        users = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak user lookup response for '{username}': "
            f"{e}. Raw output: {result.output[:500]}"
        )

    if users:
        return users[0]
    return None


@TestStep(Given)
def create_group(self, group_name, realm_name=None):
    """Create a group in Keycloak. Returns the group ID."""
    if realm_name is None:
        realm_name = self.context.realm_name

    status, body = keycloak_admin_request(
        method="POST",
        path=f"/admin/realms/{realm_name}/groups",
        json_data={"name": group_name},
        expected_statuses=[201, 409],
    )

    group = get_group_by_name(group_name=group_name, realm_name=realm_name)
    if group:
        return group["id"]
    raise Exception(f"Could not find group '{group_name}' after creation")


@TestStep(Given)
def delete_group(self, group_name, realm_name=None):
    """Delete a group from Keycloak by name."""
    if realm_name is None:
        realm_name = self.context.realm_name

    group = get_group_by_name(group_name=group_name, realm_name=realm_name)
    if group is None:
        note(f"Group '{group_name}' not found, nothing to delete")
        return

    keycloak_admin_request(
        method="DELETE",
        path=f"/admin/realms/{realm_name}/groups/{group['id']}",
        expected_statuses=[204],
    )


@TestStep(Given)
def get_group_by_name(self, group_name, realm_name=None):
    """Look up a Keycloak group by exact name. Returns dict or None.

    Uses Keycloak's ``?search=`` parameter (substring match) then filters
    results for an exact name match on the client side.
    """
    if realm_name is None:
        realm_name = self.context.realm_name

    node = self.context.bash_tools
    admin_token = get_admin_token()

    url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/groups"
        f"?search={group_name}&exact=true"
    )

    curl_cmd = f"curl -s '{url}' -H 'Authorization: Bearer {admin_token}'"

    result = node.command(command=curl_cmd)

    try:
        groups = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak group lookup response for '{group_name}': "
            f"{e}. Raw output: {result.output[:500]}"
        )

    for g in groups:
        if g["name"] == group_name:
            return g
    return None


@TestStep(Given)
def assign_user_to_group(self, user_id, group_id, realm_name=None):
    """Add a user to a group in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    keycloak_admin_request(
        method="PUT",
        path=f"/admin/realms/{realm_name}/users/{user_id}/groups/{group_id}",
        expected_statuses=[204],
    )


@TestStep(Given)
def remove_user_from_group(self, user_id, group_id, realm_name=None):
    """Remove a user from a group in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    keycloak_admin_request(
        method="DELETE",
        path=f"/admin/realms/{realm_name}/users/{user_id}/groups/{group_id}",
        expected_statuses=[204],
    )


@TestStep(Given)
def disable_client(self, client_id_name, realm_name=None):
    """Disable a client (application) in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    node = self.context.bash_tools
    admin_token = get_admin_token()

    url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients"
        f"?clientId={client_id_name}"
    )
    curl_cmd = f"curl -s '{url}' -H 'Authorization: Bearer {admin_token}'"
    result = node.command(command=curl_cmd)

    try:
        clients = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak client lookup for '{client_id_name}': "
            f"{e}. Raw output: {result.output[:500]}"
        )

    if not clients:
        raise Exception(f"Client '{client_id_name}' not found in realm '{realm_name}'")

    internal_id = clients[0]["id"]
    keycloak_admin_request(
        method="PUT",
        path=f"/admin/realms/{realm_name}/clients/{internal_id}",
        json_data={"enabled": False},
        expected_statuses=[204],
    )


@TestStep(Given)
def enable_client(self, client_id_name, realm_name=None):
    """Re-enable a client in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    node = self.context.bash_tools
    admin_token = get_admin_token()

    url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients"
        f"?clientId={client_id_name}"
    )
    curl_cmd = f"curl -s '{url}' -H 'Authorization: Bearer {admin_token}'"
    result = node.command(command=curl_cmd)

    try:
        clients = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak client lookup for '{client_id_name}': "
            f"{e}. Raw output: {result.output[:500]}"
        )

    if not clients:
        raise Exception(f"Client '{client_id_name}' not found in realm '{realm_name}'")

    internal_id = clients[0]["id"]
    keycloak_admin_request(
        method="PUT",
        path=f"/admin/realms/{realm_name}/clients/{internal_id}",
        json_data={"enabled": True},
        expected_statuses=[204],
    )


@TestStep(Given)
def invalidate_user_sessions(self, username, realm_name=None):
    """Logout (invalidate all sessions) for a user in Keycloak."""
    if realm_name is None:
        realm_name = self.context.realm_name

    user = get_user_by_username(username=username, realm_name=realm_name)
    if user is None:
        raise Exception(f"User '{username}' not found")

    keycloak_admin_request(
        method="POST",
        path=f"/admin/realms/{realm_name}/users/{user['id']}/logout",
        expected_statuses=[204],
    )


def _decode_jwt_token(token: str):
    """Decode a JWT token into (header_dict, payload_dict, signature_str)."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    header_data = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
    payload_data = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
    signature = parts[2]

    return header_data, payload_data, signature


def _encode_jwt_token(header: dict, payload: dict, signature: str):
    """Re-encode JWT components into a token string (signature is NOT recomputed)."""
    header_b64 = (
        base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode())
        .decode()
        .rstrip("=")
    )
    payload_b64 = (
        base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode())
        .decode()
        .rstrip("=")
    )
    return f"{header_b64}.{payload_b64}.{signature}"


@TestStep(Given)
def modify_jwt_token(
    self,
    token: str,
    header_changes: dict = None,
    payload_changes: dict = None,
    signature_change: str = None,
):
    """Modify a JWT token by changing header, payload, or signature components.

    Returns the modified token string. Signature is NOT recomputed so the token
    will fail verification unless only non-verified fields were changed.
    """
    header, payload, signature = _decode_jwt_token(token)

    if header_changes:
        header.update(header_changes)

    if payload_changes:
        payload.update(payload_changes)

    if signature_change is not None:
        signature = signature_change

    return _encode_jwt_token(header, payload, signature)


class OAuthProvider:
    """Modular provider interface for Keycloak.

    Tests access methods through ``self.context.provider_client.OAuthProvider``.
    """

    get_oauth_token = get_oauth_token
    get_admin_token = get_admin_token

    create_user = create_user
    delete_user = delete_user
    disable_user = disable_user
    enable_user = enable_user
    get_user_by_username = get_user_by_username

    create_group = create_group
    delete_group = delete_group
    get_group_by_name = get_group_by_name

    assign_user_to_group = assign_user_to_group
    remove_user_from_group = remove_user_from_group

    disable_client = disable_client
    enable_client = enable_client
    invalidate_user_sessions = invalidate_user_sessions

    modify_jwt_token = modify_jwt_token
