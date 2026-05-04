from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
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
):
    """
    Acquire an OAuth token from Google using refresh token.

    Note: Google OAuth requires user interaction for initial authorization.
    For automated testing, you need to obtain a refresh token first through
    the OAuth consent flow, then use it here to get access tokens.

    Alternatively, if you already have an access_token (e.g., from OAuth Playground),
    you can pass it directly and it will be returned as-is.
    """
    import requests

    if access_token is not None:
        return access_token

    if client_id is None:
        client_id = self.context.client_id

    if client_secret is None:
        client_secret = self.context.client_secret

    if refresh_token is None:
        refresh_token = getattr(self.context, "refresh_token", None)

    if refresh_token is None:
        raise ValueError(
            "No refresh_token provided. To get one:\n"
            "1. Go to https://developers.google.com/oauthplayground\n"
            "2. Click gear icon > 'Use your own OAuth credentials'\n"
            "3. Enter your Client ID and Client Secret\n"
            "4. Select scopes: openid, email, profile\n"
            "5. Authorize and exchange code for tokens\n"
            "6. Copy the refresh_token and pass it via --refresh-token"
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
    return token_data["access_token"]


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
    get_oauth_token = get_oauth_token
    get_user_info = get_user_info

    # Configuration steps
    default_configuration = default_configuration
    default_idp = default_idp

    # Negative configuration test steps
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
