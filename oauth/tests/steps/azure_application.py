from azure.identity import ClientSecretCredential
from msgraph.generated.models.application import Application
from msgraph.generated.models.implicit_grant_settings import ImplicitGrantSettings
from msgraph.generated.models.password_credential import PasswordCredential
from msgraph.generated.models.web_application import WebApplication
from msgraph.generated.models.user import User
from msgraph.generated.models.group import Group
from msgraph.generated.models.reference_create import ReferenceCreate
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.graph_service_client import GraphServiceClient
from jwt_authentication.tests.steps import change_clickhouse_config
from testflows.core import *

from helpers.common import getuid


@TestStep(Given)
def change_token_processors(
    processor_name,
    algo=None,
    static_key=None,
    static_jwks=None,
    jwks_uri=None,
    jwks_cache_lifetime=None,
    claims=None,
    verifier_leeway=None,
    configuration_endpoint=None,
    userinfo_endpoint=None,
    token_introspection_endpoint=None,
    processor_type=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    node=None,
):
    entries = {"token_processor": {}}
    entries["jwt_validators"][processor_name] = {}

    if processor_type is not None:
        entries["token_processor"][processor_name]["type"] = processor_type

    if algo is not None:
        entries["token_processor"]["algo"] = algo

    if static_key is not None:
        entries["token_processor"][processor_name]["static_key"] = static_key

    if static_jwks is not None:
        entries["token_processor"][processor_name]["static_jwks"] = static_jwks

    if jwks_uri is not None:
        entries["token_processor"][processor_name]["jwks_uri"] = jwks_uri

    if jwks_cache_lifetime is not None:
        entries["token_processor"][processor_name][
            "jwks_cache_lifetime"
        ] = jwks_cache_lifetime

    if claims is not None:
        entries["jwt_validators"][processor_name]["claims"] = claims

    if verifier_leeway is not None:
        entries["jwt_validators"][processor_name]["verifier_leeway"] = verifier_leeway

    if configuration_endpoint is not None:
        entries["token_processor"][processor_name][
            "configuration_endpoint"
        ] = configuration_endpoint

    if userinfo_endpoint is not None:
        entries["token_processor"][processor_name][
            "userinfo_endpoint"
        ] = userinfo_endpoint

    if token_introspection_endpoint is not None:
        entries["token_processor"][processor_name][
            "token_introspection_endpoint"
        ] = token_introspection_endpoint

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"{processor_name}_config.xml",
        node=node,
    )


@TestStep(Given)
def change_user_directories_config(
    self,
    processor,
    common_roles=None,
    roles_filter=None,
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    entries = {"user_directories": {}}
    entries["user_directories"]["token"] = {}

    entries["user_directories"]["token"]["processor"] = processor

    if common_roles is not None:
        entries["user_directories"]["token"]["common_roles"] = common_roles

    if roles_filter is not None:
        entries["user_directories"]["token"]["roles_filter"] = roles_filter

    change_clickhouse_config(
        entires=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"user_directory_{processor}.xml",
        node=node,
    )


@TestStep(Given)
def get_oauth_token(
    self,
    tenant_id=None,
    client_id=None,
    client_secret=None,
    scope="https://graph.microsoft.com/.default",
):
    """
    Acquire an OAuth token from Azure AD using client credentials.
    """

    if tenant_id is None:
        tenant_id = self.context.tenant_id

    if client_id is None:
        client_id = self.context.client_id

    if client_secret is None:
        client_secret = self.context.client_secret

    credential = ClientSecretCredential(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
    )
    token = credential.get_token(scope)
    return token.token


@TestStep(Given)
async def create_azure_application(
    self,
    application_name: str,
    redirect_uris: list[str] = None,
    home_page_url: str = None,
    logout_url: str = None,
):
    """Create an Azure AD application."""

    secret_name = "secret_" + getuid()
    client = self.context.client

    app_config = {
        "display_name": application_name,
        "password_credentials": [
            PasswordCredential(
                display_name=secret_name,
            ),
        ],
    }

    if redirect_uris is not None or home_page_url is not None or logout_url is not None:
        web_config = {
            "implicit_grant_settings": ImplicitGrantSettings(
                enable_id_token_issuance=True, enable_access_token_issuance=False
            ),
        }

        if redirect_uris is not None:
            web_config["redirect_uris"] = redirect_uris
        if home_page_url is not None:
            web_config["home_page_url"] = home_page_url
        if logout_url is not None:
            web_config["logout_url"] = logout_url

        app_config["web"] = WebApplication(**web_config)

    app = Application(**app_config)

    application = await client.applications.post(app)

    return application


@TestStep(Given)
async def create_azure_application_with_secret(self):
    """Create an Azure AD application with a password credential."""

    application_name = "application_with_secret_" + getuid()
    application = await create_azure_application(
        application_name=application_name,
        redirect_uris=["http://localhost:3000/login/azuread"],
        home_page_url="http://localhost:3000",
        logout_url="https://localhost:3000/logout",
    )

    secret = application.password_credentials[0].secret_text
    app_id = application.app_id

    return application, secret, app_id


@TestStep(Given)
async def create_user(
    self,
    display_name: str,
    mail_nickname: str,
    user_principal_name: str,
    password: str = "TempPassword123!",
):
    """Create a user in Azure AD."""

    client = self.context.client

    user_config = {
        "account_enabled": True,
        "display_name": display_name,
        "mail_nickname": mail_nickname,
        "user_principal_name": user_principal_name,
        "password_profile": PasswordProfile(
            force_change_password_next_sign_in=True, password=password
        ),
    }

    user = User(**user_config)
    created_user = await client.users.post(user)

    return created_user


@TestStep(Given)
async def create_group(
    self,
    display_name: str = None,
    mail_nickname: str = None,
    description: str = None,
    security_enabled: bool = True,
    mail_enabled: bool = False,
):
    """Create a group in Azure AD."""

    client = self.context.client
    if display_name is None:
        display_name = "group_" + getuid()

    if mail_nickname is None:
        mail_nickname = "group_" + getuid()

    group_config = {
        "display_name": display_name,
        "mail_nickname": mail_nickname,
        "security_enabled": security_enabled,
        "mail_enabled": mail_enabled,
    }

    if description is not None:
        group_config["description"] = description

    group = Group(**group_config)
    created_group = await client.groups.post(group)

    return created_group


@TestStep(Given)
async def assign_user_to_group(
    self,
    user_id: str,
    group_id: str,
):
    """Assign a user to a group in Azure AD."""

    client = self.context.client

    user_reference = ReferenceCreate(
        odata_id=f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
    )

    await client.groups.by_group_id(group_id).members.ref.post(user_reference)

    return True


@TestStep(Then)
async def delete_application(self, application_id: str):
    """Delete an Azure AD application."""
    client = self.context.client
    await client.applications.by_application_id(application_id).delete()
    return True


@TestStep(Given)
def setup_azure_application(self):
    try:
        with Given("I create an Azure AD application with a secret"):
            application, secret, app_id = create_azure_application_with_secret()
            self.context.application = application
            self.context.secret = secret
            self.context.app_id = app_id

        yield application
    finally:
        delete_application(application_id=app_id)


class OAuthProvider:
    get_oauth_token = get_oauth_token
    create_application = create_azure_application
    create_application_with_secret = create_azure_application_with_secret
    create_user = create_user
    create_group = create_group
    assign_user_to_group = assign_user_to_group
    setup_azure_application = setup_azure_application
