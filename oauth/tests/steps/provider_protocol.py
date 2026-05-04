"""Provider-agnostic OAuth provider contract.

Every concrete OAuth provider (Keycloak, Azure, Google, ...) exposes the
same surface so test scenarios can run against any of them by swapping
``--identity-provider``.

Tests MUST go through ``self.context.provider_client.OAuthProvider`` and
MUST NOT import provider-specific symbols (``keycloak_realm.create_user``
etc.) directly. Anything not implemented by a given provider raises
``UnsupportedByProvider`` so the scenario is reported as ``Skip`` instead
of erroring.

The contract intentionally keeps token shape uniform: ``get_oauth_token``
ALWAYS returns an ``OAuthToken`` (defined below) regardless of provider.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class UnsupportedByProvider(Exception):
    """Raised when a method is not (yet) implemented for a provider.

    Test code should catch this and ``Skip`` the affected scenario rather
    than treat it as a failure.
    """


@dataclass
class OAuthToken:
    """Uniform token container returned by every provider.

    ``access_token`` is the only field guaranteed to be set across all
    providers. ``refresh_token`` and ``id_token`` may be ``None`` (e.g.
    Azure client-credentials only returns an access token; Google may
    skip refresh on subsequent token-endpoint calls).

    The container behaves like a dict for ``["access_token"]`` /
    ``.get("error")`` access so legacy call sites that already do
    ``token["access_token"]`` continue to work during the migration.
    """

    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key):
        if key in {"access_token", "refresh_token", "id_token", "token_type", "expires_in"}:
            return getattr(self, key)
        return self.raw[key]

    def __contains__(self, key):
        if key in {"access_token", "refresh_token", "id_token", "token_type", "expires_in"}:
            return getattr(self, key) is not None
        return key in self.raw

    def get(self, key, default=None):
        try:
            value = self[key]
        except KeyError:
            return default
        return value if value is not None else default


@dataclass
class OpenIDEndpoints:
    """OpenID-Connect endpoint bundle for a provider/realm/tenant.

    Tests use this instead of hardcoding Keycloak URLs so the same
    scenarios work against Azure (``login.microsoftonline.com``) or
    Google (``accounts.google.com``).
    """

    issuer: str
    jwks_uri: str
    userinfo_endpoint: str
    token_introspection_endpoint: Optional[str] = None
    configuration_endpoint: Optional[str] = None
    expected_audience: Optional[str] = None


def unsupported(method_name: str):
    """Helper to build ``Skip``-style ``OAuthProvider`` placeholders.

    Use as the value of an ``OAuthProvider`` attribute when a provider
    cannot implement a given method:

        delete_user = unsupported("delete_user")

    The returned callable raises ``UnsupportedByProvider`` immediately.
    """

    def _stub(*args, **kwargs):
        raise UnsupportedByProvider(
            f"{method_name!r} is not implemented for this OAuth provider"
        )

    _stub.__name__ = method_name
    _stub.unsupported = True  # marker for introspection
    return _stub


REQUIRED_METHODS = (
    # Core token + endpoint access — every provider must implement these.
    "get_oauth_token",
    "openid_endpoints",
    "default_idp",
    # JWT mutation (used heavily by tokens / jwt_manipulation / tls /
    # security_audit). Provider-agnostic implementation lives in
    # ``provider_protocol`` itself but providers re-export it for
    # discoverability.
    "modify_jwt_token",
)

OPTIONAL_METHODS = (
    "create_user",
    "delete_user",
    "disable_user",
    "enable_user",
    "get_user_by_username",
    "create_group",
    "delete_group",
    "get_group_by_name",
    "assign_user_to_group",
    "remove_user_from_group",
    "disable_client",
    "enable_client",
    "invalidate_user_sessions",
    # Authorization-negative testing: ability to mint tokens from a
    # *different* trust boundary (realm / tenant / org). Keycloak
    # implements these via the Admin API; Azure/Google can't easily
    # mock them, so dependent scenarios Skip.
    "create_realm",
    "delete_realm",
    "create_client_in_realm",
    "get_oauth_token_for_client",
)


def assert_provider_contract(provider_module):
    """Assert that ``provider_module.OAuthProvider`` exposes the contract.

    Required methods MUST be present and callable. Optional methods MUST
    be either present or explicitly marked unsupported via ``unsupported()``.
    Raises ``AssertionError`` if the contract is violated; this is meant
    to be called once at suite startup so a missing method fails fast
    instead of later in a confusing test step.
    """
    provider = getattr(provider_module, "OAuthProvider", None)
    assert provider is not None, (
        f"{provider_module.__name__!r} does not expose OAuthProvider"
    )

    missing_required = [m for m in REQUIRED_METHODS if not hasattr(provider, m)]
    assert not missing_required, (
        f"{provider_module.__name__!r}.OAuthProvider is missing required "
        f"methods: {missing_required}"
    )

    for m in OPTIONAL_METHODS:
        if not hasattr(provider, m):
            setattr(provider, m, unsupported(m))


def _decode_jwt_token(token: str):
    """Decode a JWT into ``(header_dict, payload_dict, signature_str)``.

    Provider-agnostic helper used by ``modify_jwt_token`` below.
    """
    import base64
    import json

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    def _b64(s):
        return base64.urlsafe_b64decode(s + "==")

    header = json.loads(_b64(parts[0]))
    payload = json.loads(_b64(parts[1]))
    return header, payload, parts[2]


def _encode_jwt_token(header: dict, payload: dict, signature: str):
    """Re-encode JWT components into a compact string.

    The signature is NOT recomputed; tests use this to assert that a
    server rejects mutated tokens.
    """
    import base64
    import json

    def _b64(d):
        return (
            base64.urlsafe_b64encode(json.dumps(d, separators=(",", ":")).encode())
            .decode()
            .rstrip("=")
        )

    return f"{_b64(header)}.{_b64(payload)}.{signature}"


def modify_jwt_token(
    token: str,
    header_changes: dict = None,
    payload_changes: dict = None,
    signature_change: str = None,
):
    """Provider-agnostic JWT mutation.

    Returns a new token string. The signature is NOT recomputed, so the
    server should reject the token unless only non-verified fields were
    changed. Re-exported by every provider's ``OAuthProvider`` so test
    code can keep calling ``client.OAuthProvider.modify_jwt_token``.
    """
    header, payload, signature = _decode_jwt_token(token)

    if header_changes:
        header.update(header_changes)
    if payload_changes:
        payload.update(payload_changes)
    if signature_change is not None:
        signature = signature_change

    return _encode_jwt_token(header, payload, signature)
