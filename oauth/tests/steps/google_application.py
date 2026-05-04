from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)
from oauth.tests.steps.provider_protocol import (
    OAuthToken,
    OpenIDEndpoints,
    modify_jwt_token as _shared_modify_jwt_token,
    unsupported,
)
from testflows.core import *
from oauth.requirements.requirements import *

from helpers.common import getuid


@TestStep(Given)
def default_configuration(self, node=None):
    """Configure ClickHouse to use Google token processor (OpenID type)."""
    change_token_processors(
        processor_name="google",
        processor_type="openid",
        configuration_endpoint="https://accounts.google.com/.well-known/openid-configuration",
        username_claim="email",
        node=node,
    )


@TestStep(Given)
def default_idp(self, node=None, common_roles=None, roles_filter=None):
    """Set up default ClickHouse configuration for Google OAuth authentication."""
    default_configuration(self, node=node)
    change_user_directories_config(
        processor="google",
        node=node,
        common_roles=common_roles,
        roles_filter=roles_filter,
    )


@TestStep(Given)
def get_oauth_token(
    self,
    client_id=None,
    client_secret=None,
    refresh_token=None,
    access_token=None,
    username=None,
    password=None,
):
    """Acquire a Google OAuth token via refresh-token grant.

    Returns an :class:`OAuthToken`. ``username``/``password`` are
    accepted for signature compatibility with the Keycloak provider but
    are ignored — Google does not allow ROPC.

    Google OAuth requires user interaction for *initial* authorization,
    so this helper expects a long-lived refresh token to have been
    obtained out of band (see ``get_refresh_token_interactive`` below)
    and passed in via ``--refresh-token`` or
    ``self.context.refresh_token``. Alternatively, callers may pass
    ``access_token=`` directly when running ad-hoc.
    """
    import requests

    if access_token is not None:
        return OAuthToken(access_token=access_token, raw={"access_token": access_token})

    if client_id is None:
        client_id = self.context.client_id
    if client_secret is None:
        client_secret = self.context.client_secret
    if refresh_token is None:
        refresh_token = getattr(self.context, "refresh_token", None)

    if refresh_token is None:
        raise ValueError(
            "No refresh_token provided for Google. Either pass --refresh-token, "
            "set self.context.refresh_token, or pass access_token= directly. "
            "See get_refresh_token_interactive() for how to obtain one."
        )

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_data = response.json()

    return OAuthToken(
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token", refresh_token),
        id_token=token_data.get("id_token"),
        token_type=token_data.get("token_type"),
        expires_in=token_data.get("expires_in"),
        raw=token_data,
    )


@TestStep(Given)
def openid_endpoints(self):
    """Return Google's standard OpenID-Connect endpoints."""
    return OpenIDEndpoints(
        issuer="https://accounts.google.com",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
        token_introspection_endpoint="https://oauth2.googleapis.com/tokeninfo",
        configuration_endpoint=(
            "https://accounts.google.com/.well-known/openid-configuration"
        ),
        expected_audience=getattr(self, "client_id", None) or getattr(
            getattr(self, "context", None), "client_id", None
        ),
    )


def get_refresh_token_interactive(client_id, client_secret):
    """
    Interactive helper to get a refresh token from Google.

    This function guides the user through the OAuth flow to obtain a refresh token.
    Run this once to get a refresh token, then use it for automated testing.

    Usage:
        from oauth.tests.steps.google_application import get_refresh_token_interactive
        refresh_token = get_refresh_token_interactive("your-client-id", "your-client-secret")
    """
    import webbrowser
    from urllib.parse import urlencode, urlparse, parse_qs
    import requests

    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    scopes = "openid email profile"

    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

    print(f"\nOpening browser for Google authorization...")
    print(f"If browser doesn't open, go to:\n{auth_url}\n")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    auth_code = input("Enter the authorization code from Google: ").strip()

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
    response.raise_for_status()

    tokens = response.json()
    refresh_token = tokens.get("refresh_token")

    if refresh_token:
        print(f"\nSuccess! Your refresh token:\n{refresh_token}\n")
        print("Add this to your .env file or pass via --refresh-token")
        return refresh_token
    else:
        raise ValueError(
            "No refresh token received. Make sure to request 'offline' access."
        )


@TestStep(Given)
def get_user_info(self, access_token):
    """Get user information from Google using access token."""
    import requests

    userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(userinfo_url, headers=headers)
    response.raise_for_status()

    return response.json()


@TestStep(Given)
def invalid_processor_type_configuration(self, node=None):
    """Configure ClickHouse with invalid Google processor type."""
    change_token_processors(
        processor_name="google_invalid",
        processor_type="invalid_type",
        node=node,
    )


@TestStep(Given)
def missing_configuration_endpoint(self, node=None):
    """Configure ClickHouse with missing configuration endpoint for OpenID."""
    change_token_processors(
        processor_name="google_missing_endpoint",
        processor_type="openid",
        node=node,
    )


@TestStep(Given)
def invalid_configuration_endpoint(self, node=None):
    """Configure ClickHouse with invalid configuration endpoint."""
    change_token_processors(
        processor_name="google_invalid_endpoint",
        processor_type="openid",
        configuration_endpoint="https://invalid.example.com/.well-known/openid-configuration",
        node=node,
    )


@TestStep(Given)
def custom_username_claim_configuration(self, node=None, username_claim="sub"):
    """Configure ClickHouse with custom username claim for Google."""
    change_token_processors(
        processor_name="google_custom_claim",
        processor_type="openid",
        configuration_endpoint="https://accounts.google.com/.well-known/openid-configuration",
        username_claim=username_claim,
        node=node,
    )


@TestStep(Given)
def custom_cache_lifetime_configuration(
    self, node=None, token_cache_lifetime=3600, jwks_cache_lifetime=3600
):
    """Configure ClickHouse with custom cache lifetimes for Google."""
    change_token_processors(
        processor_name="google_custom_cache",
        processor_type="openid",
        configuration_endpoint="https://accounts.google.com/.well-known/openid-configuration",
        token_cache_lifetime=token_cache_lifetime,
        jwks_cache_lifetime=jwks_cache_lifetime,
        node=node,
    )


@TestStep(Given)
def explicit_endpoints_configuration(self, node=None):
    """Configure ClickHouse with explicit Google endpoints instead of configuration_endpoint."""
    change_token_processors(
        processor_name="google_explicit",
        processor_type="openid",
        userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
        token_introspection_endpoint="https://oauth2.googleapis.com/tokeninfo",
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
        node=node,
    )


@TestStep(Given)
def missing_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with missing processor in user directories."""
    change_user_directories_config(
        processor="",
        node=node,
    )


@TestStep(Given)
def non_existent_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with non-existent processor in user directories."""
    change_user_directories_config(
        processor="non_existent_processor",
        node=node,
    )


@TestStep(Given)
def invalid_common_roles_configuration(self, node=None):
    """Configure ClickHouse with invalid common roles."""
    change_user_directories_config(
        processor="google",
        common_roles=[""],
        node=node,
    )


@TestStep(Given)
def invalid_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with invalid roles filter regex."""
    change_user_directories_config(
        processor="google",
        roles_filter="[invalid regex",
        node=node,
    )


@TestStep(Given)
def no_token_processors_configuration(self, node=None):
    """Configure ClickHouse without any token processors."""
    change_token_processors(
        processor_name="empty_processor",
        processor_type=None,
        node=node,
    )


class OAuthProvider:
    """Provider implementation for Google Identity.

    Implements the contract defined in
    ``oauth.tests.steps.provider_protocol``. Most identity-management
    operations (``create_user``, ``disable_user``, ...) are not
    automated for Google, so they're explicitly marked unsupported
    here. Scenarios that depend on them ``Skip`` rather than crash.
    """

    get_oauth_token = get_oauth_token
    get_user_info = get_user_info
    openid_endpoints = openid_endpoints
    default_idp = default_idp
    modify_jwt_token = staticmethod(_shared_modify_jwt_token)

    default_configuration = default_configuration

    invalid_processor_type_configuration = invalid_processor_type_configuration
    missing_configuration_endpoint = missing_configuration_endpoint
    invalid_configuration_endpoint = invalid_configuration_endpoint
    custom_username_claim_configuration = custom_username_claim_configuration
    custom_cache_lifetime_configuration = custom_cache_lifetime_configuration
    explicit_endpoints_configuration = explicit_endpoints_configuration
    missing_processor_user_directory_configuration = (
        missing_processor_user_directory_configuration
    )
    non_existent_processor_user_directory_configuration = (
        non_existent_processor_user_directory_configuration
    )
    invalid_common_roles_configuration = invalid_common_roles_configuration
    invalid_roles_filter_configuration = invalid_roles_filter_configuration
    no_token_processors_configuration = no_token_processors_configuration

    create_user = unsupported("create_user")
    delete_user = unsupported("delete_user")
    disable_user = unsupported("disable_user")
    enable_user = unsupported("enable_user")
    get_user_by_username = unsupported("get_user_by_username")
    create_group = unsupported("create_group")
    delete_group = unsupported("delete_group")
    get_group_by_name = unsupported("get_group_by_name")
    assign_user_to_group = unsupported("assign_user_to_group")
    remove_user_from_group = unsupported("remove_user_from_group")
    disable_client = unsupported("disable_client")
    enable_client = unsupported("enable_client")
    invalidate_user_sessions = unsupported("invalidate_user_sessions")
    get_oauth_token_for_client = unsupported("get_oauth_token_for_client")
