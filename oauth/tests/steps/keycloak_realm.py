import json
import base64
from testflows.core import *
from oauth.requirements.requirements import *
from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.provider_protocol import (
    OAuthToken,
    OpenIDEndpoints,
    modify_jwt_token as _shared_modify_jwt_token,
)


def _keycloak_realm_base_url(self):
    """Return ``http://<keycloak_host>/realms/<realm>`` for the active realm.

    The ``iss`` claim Keycloak embeds in tokens uses
    ``KC_HOSTNAME`` (``localhost`` in our compose), not the in-network
    ``keycloak`` hostname. Tests that compare against ``iss`` MUST use
    this helper.
    """
    realm = getattr(self.context, "realm_name", "grafana")
    base = self.context.keycloak_url
    return f"{base}/realms/{realm}"


def _keycloak_token_endpoint(self):
    return f"{_keycloak_realm_base_url(self)}/protocol/openid-connect/token"


def _keycloak_issuer_for_token_validation(self):
    """Return the issuer string Keycloak puts into the ``iss`` claim.

    docker-compose starts Keycloak with ``--hostname=localhost`` so
    minted tokens carry ``iss=http://localhost:8080/realms/<realm>``,
    NOT the in-network hostname ``keycloak:8080``. ClickHouse, however,
    talks to Keycloak through the in-network hostname for JWKS /
    introspection. This split is intentional and these two helpers
    make it explicit so authz tests stop drifting.
    """
    realm = getattr(self.context, "realm_name", "grafana")
    return f"http://localhost:8080/realms/{realm}"


def keycloak_openid_processor_args(
    realm_name=None,
    keycloak_url=None,
    expected_audience=None,
    expected_issuer=None,
):
    """Return ``change_token_processors``-compatible kwargs for the
    standard Keycloak OpenID processor.

    NOT a ``@TestStep`` — this is a pure context-read that returns a
    dict. Decorating it would force callers into a ``with Given(...)``
    block just to compute four URLs and surface them as the wrapped
    step-result ``'OK'`` object instead of the dict tests expect.
    Centralised here so every security_audit / configuration scenario
    that wires up an OpenID processor against Keycloak doesn't repeat
    the same URLs inline.

    Since antalya-26.3 (PR #1799) the ``openid`` processor rejects
    ``jwks_uri`` — local JWT validation should use ``jwt_dynamic_jwks``
    instead. Introspection credentials are always included so that
    ``expected_issuer`` / ``expected_audience`` bindings can be enforced
    via RFC 7662.
    """
    ctx = current().context
    if realm_name is None:
        realm_name = ctx.realm_name
    if keycloak_url is None:
        keycloak_url = ctx.keycloak_url

    base = f"{keycloak_url}/realms/{realm_name}/protocol/openid-connect"

    args = {
        "processor_type": "OpenID",
        "userinfo_endpoint": f"{base}/userinfo",
        "token_introspection_endpoint": f"{base}/token/introspect",
        "introspection_client_id": ctx.introspection_client_id,
        "introspection_client_secret": ctx.introspection_client_secret,
    }
    if expected_audience is not None:
        args["expected_audience"] = expected_audience
    if expected_issuer is not None:
        args["expected_issuer"] = expected_issuer
    return args


def openid_endpoints(realm_name=None):
    """Return an ``OpenIDEndpoints`` bundle for the active Keycloak realm.

    NOT a ``@TestStep`` — see ``keycloak_openid_processor_args`` for
    the rationale. Tests use this instead of constructing URLs inline
    so swapping ``--identity-provider`` switches every endpoint at
    once.
    """
    ctx = current().context
    if realm_name is None:
        realm_name = ctx.realm_name

    base = f"{ctx.keycloak_url}/realms/{realm_name}/protocol/openid-connect"
    return OpenIDEndpoints(
        issuer=f"http://localhost:8080/realms/{realm_name}",
        jwks_uri=f"{base}/certs",
        userinfo_endpoint=f"{base}/userinfo",
        token_introspection_endpoint=f"{base}/token/introspect",
        configuration_endpoint=(
            f"{ctx.keycloak_url}/realms/{realm_name}"
            f"/.well-known/openid-configuration"
        ),
        expected_audience="account",
    )


@TestStep(Given)
def default_idp(self, node=None, common_roles=None, roles_filter=None):
    """Configure ClickHouse with the default Keycloak token processor.

    Provider-agnostic helper invoked from generic tests so the same
    scenario works against any IdP that implements the contract.
    """
    args = keycloak_openid_processor_args()
    change_token_processors(processor_name="keycloak", node=node, **args)
    change_user_directories_config(
        processor="keycloak",
        node=node,
        common_roles=common_roles,
        roles_filter=roles_filter,
    )


@TestStep(Given)
def get_oauth_token(self, node=None, username=None, password=None, scope="openid"):
    """Acquire an access token from Keycloak via Resource-Owner-Password-Credentials.

    Returns an :class:`OAuthToken` that ``access_token`` and friends can
    be read off of. Behaves dict-like so legacy
    ``token["access_token"]`` call sites keep working until they migrate
    to ``token.access_token``. Raises a clear ``Exception`` when Keycloak
    returns an error response (disabled user, wrong password, ...) so
    callers don't get an opaque ``KeyError``.

    ``scope`` defaults to ``"openid"`` because antalya-26.3 (PR #1799)
    removed ``jwks_uri`` from the ``openid`` processor — all OpenID tests
    now use ``userinfo_endpoint``, which requires the ``openid`` scope per
    OIDC spec. For ``jwt_dynamic_jwks`` tests (the base config) the extra
    scope is harmless. Pass ``scope=None`` only when you specifically need
    a token without the ``openid`` scope.
    """
    if node is None:
        node = self.context.bash_tools
    if username is None:
        username = self.context.username
    if password is None:
        password = self.context.password

    curl_command = (
        f"curl -s --location '{_keycloak_token_endpoint(self)}' "
        f"--header 'Content-Type: application/x-www-form-urlencoded' "
        f"--data-urlencode 'client_id={self.context.client_id}' "
        f"--data-urlencode 'grant_type=password' "
        f"--data-urlencode 'username={username}' "
        f"--data-urlencode 'password={password}' "
        f"--data-urlencode 'client_secret={self.context.client_secret}'"
    )

    if scope is not None:
        curl_command += f" --data-urlencode 'scope={scope}'"

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

    if "access_token" not in response:
        raise Exception(
            f"Keycloak token response for '{username}' is missing access_token: "
            f"{response!r}"
        )

    yield OAuthToken(
        access_token=response["access_token"],
        refresh_token=response.get("refresh_token"),
        id_token=response.get("id_token"),
        token_type=response.get("token_type"),
        expires_in=response.get("expires_in"),
        raw=response,
    )


@TestStep(Given)
def get_oauth_token_for_client(
    self,
    client_id,
    client_secret,
    realm_name=None,
    username=None,
    password=None,
    node=None,
):
    """Acquire a token from Keycloak for an arbitrary client/realm.

    Used by authorization-negative tests that need a token with a
    different ``aud`` / ``azp`` than the one ClickHouse expects.
    Returns an :class:`OAuthToken`.
    """
    if node is None:
        node = self.context.bash_tools
    if realm_name is None:
        realm_name = self.context.realm_name
    if username is None:
        username = self.context.username
    if password is None:
        password = self.context.password

    token_url = (
        f"{self.context.keycloak_url}/realms/{realm_name}"
        f"/protocol/openid-connect/token"
    )

    curl_command = (
        f"curl -s --location '{token_url}' "
        f"--header 'Content-Type: application/x-www-form-urlencoded' "
        f"--data-urlencode 'client_id={client_id}' "
        f"--data-urlencode 'grant_type=password' "
        f"--data-urlencode 'username={username}' "
        f"--data-urlencode 'password={password}' "
        f"--data-urlencode 'client_secret={client_secret}'"
    )

    result = node.command(command=curl_command)

    try:
        response = json.loads(result.output)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to parse Keycloak token response from "
            f"realm={realm_name!r} client_id={client_id!r}: {e}. "
            f"Raw output: {result.output[:500]}"
        )

    if "error" in response or "access_token" not in response:
        raise Exception(
            f"Keycloak token request failed for client_id={client_id!r} "
            f"realm={realm_name!r}: {response!r}"
        )

    return OAuthToken(
        access_token=response["access_token"],
        refresh_token=response.get("refresh_token"),
        id_token=response.get("id_token"),
        token_type=response.get("token_type"),
        expires_in=response.get("expires_in"),
        raw=response,
    )


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
def create_realm(self, realm_name, enabled=True):
    """Create a brand-new Keycloak realm via the Admin API.

    Used by authorization-negative tests that need a token issued by an
    issuer ClickHouse does not trust ("user from another tenant /
    organisation"). Idempotent: returns silently if the realm already
    exists.
    """
    keycloak_admin_request(
        method="POST",
        path="/admin/realms",
        json_data={"realm": realm_name, "enabled": enabled},
        expected_statuses=[201, 409],
    )


@TestStep(Given)
def delete_realm(self, realm_name):
    """Delete a Keycloak realm via the Admin API. Idempotent."""
    keycloak_admin_request(
        method="DELETE",
        path=f"/admin/realms/{realm_name}",
        expected_statuses=[204, 404],
    )


@TestStep(Given)
def create_client_in_realm(
    self,
    realm_name,
    client_id,
    client_secret,
    direct_access_grants_enabled=True,
    public_client=False,
):
    """Create an OIDC client in the given realm via the Admin API.

    Returns the Keycloak-internal client ``id`` (not ``clientId``)
    because subsequent role / scope updates need it.
    """
    keycloak_admin_request(
        method="POST",
        path=f"/admin/realms/{realm_name}/clients",
        json_data={
            "clientId": client_id,
            "secret": client_secret,
            "enabled": True,
            "publicClient": public_client,
            "protocol": "openid-connect",
            "directAccessGrantsEnabled": direct_access_grants_enabled,
            "standardFlowEnabled": True,
        },
        expected_statuses=[201, 409],
    )

    node = self.context.bash_tools
    admin_token = get_admin_token()
    url = (
        f"{self.context.keycloak_url}/admin/realms/{realm_name}/clients"
        f"?clientId={client_id}"
    )
    result = node.command(
        command=f"curl -s '{url}' -H 'Authorization: Bearer {admin_token}'"
    )
    clients = json.loads(result.output)
    if not clients:
        raise Exception(
            f"Failed to look up newly-created client {client_id!r} in realm {realm_name!r}"
        )
    return clients[0]["id"]


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


class OAuthProvider:
    """Provider implementation for Keycloak.

    Implements the contract defined in
    ``oauth.tests.steps.provider_protocol``. Tests MUST go through
    ``self.context.provider_client.OAuthProvider`` and never reach into
    this module directly so the same scenarios work against Azure/Google
    once those providers are wired up.
    """

    get_oauth_token = get_oauth_token
    get_oauth_token_for_client = get_oauth_token_for_client
    get_admin_token = get_admin_token

    openid_endpoints = staticmethod(openid_endpoints)
    default_idp = default_idp

    modify_jwt_token = staticmethod(_shared_modify_jwt_token)

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

    create_realm = create_realm
    delete_realm = delete_realm
    create_client_in_realm = create_client_in_realm
