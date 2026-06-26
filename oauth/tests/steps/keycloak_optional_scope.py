"""Keycloak admin-API automation for optional client scope assignments.

Attaches an optional scope (e.g. ``offline_access``) to a client
and grants the matching realm role to every user.

Loaded as text and executed inside the bash-tools container by the
``keycloak_enable_optional_scope`` step.
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def _admin_token(
    base: str, admin_user: str = "admin", admin_password: str = "admin"
) -> str:
    """Acquire an admin-cli access token for ``base``'s master realm."""

    data = urllib.parse.urlencode(
        dict(
            grant_type="password",
            client_id="admin-cli",
            username=admin_user,
            password=admin_password,
        )
    ).encode()
    req = urllib.request.Request(
        f"{base}/realms/master/protocol/openid-connect/token", data=data
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["access_token"]


def _get_json(url: str, auth):
    req = urllib.request.Request(url, headers=auth)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def _attach_optional_scope(
    base: str,
    realm: str,
    client_id: str,
    scope_name: str,
    auth,
) -> None:
    """Make sure ``scope_name`` is in ``client_id``'s optional client scopes."""

    clients = _get_json(
        f"{base}/admin/realms/{realm}/clients?clientId={client_id}", auth
    )
    if not clients:
        print(f"ERROR: client {client_id!r} not found in realm {realm!r}")
        sys.exit(1)
    client_uuid = clients[0]["id"]

    scope_map = {
        s["name"]: s["id"]
        for s in _get_json(f"{base}/admin/realms/{realm}/client-scopes", auth)
    }
    if scope_name not in scope_map:
        print(
            f"ERROR: scope {scope_name!r} not found in realm "
            f"(available: {sorted(scope_map)})"
        )
        sys.exit(1)
    scope_id = scope_map[scope_name]

    current_optional = {
        s["name"]
        for s in _get_json(
            f"{base}/admin/realms/{realm}/clients/{client_uuid}"
            f"/optional-client-scopes",
            auth,
        )
    }
    if scope_name in current_optional:
        print(f"{scope_name} already in optional scopes")
        return

    req = urllib.request.Request(
        f"{base}/admin/realms/{realm}/clients/{client_uuid}"
        f"/optional-client-scopes/{scope_id}",
        method="PUT",
        headers=auth,
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(f"Added {scope_name} to optional scopes ({r.status})")
    except urllib.error.HTTPError as exc:
        print(
            f"PUT optional-client-scopes failed {exc.code}: " f"{exc.read().decode()}"
        )
        sys.exit(1)


def _assign_realm_role_to_every_user(
    base: str,
    realm: str,
    role_name: str,
    auth,
) -> None:
    """Ensure every user in ``realm`` holds the ``role_name`` realm role."""

    role = _get_json(f"{base}/admin/realms/{realm}/roles/{role_name}", auth)
    users = _get_json(f"{base}/admin/realms/{realm}/users", auth)
    for user in users:
        uid = user["id"]
        uname = user.get("username", uid)
        assigned = {
            r["name"]
            for r in _get_json(
                f"{base}/admin/realms/{realm}/users/{uid}/role-mappings/realm",
                auth,
            )
        }
        if role_name in assigned:
            print(f"User {uname!r} already has {role_name} role")
            continue
        body = json.dumps([role]).encode()
        req = urllib.request.Request(
            f"{base}/admin/realms/{realm}/users/{uid}/role-mappings/realm",
            data=body,
            method="POST",
            headers={**auth, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as r:
                print(f"Assigned {role_name} role to user {uname!r} " f"({r.status})")
        except urllib.error.HTTPError as exc:
            print(
                f"POST role-mappings failed for {uname!r} "
                f"{exc.code}: {exc.read().decode()}"
            )
            sys.exit(1)


def enable_optional_scope_and_assign_role(
    base: str,
    realm: str,
    client_id: str,
    scope_name: str,
) -> None:
    """Attach ``scope_name`` to ``client_id`` and grant the matching realm role.

    Idempotent. ``base`` is the Keycloak root URL (e.g. ``http://keycloak:8080``).
    """

    token = _admin_token(base)
    auth = {"Authorization": f"Bearer {token}"}
    _attach_optional_scope(base, realm, client_id, scope_name, auth)
    _assign_realm_role_to_every_user(base, realm, scope_name, auth)
    print("Done")
