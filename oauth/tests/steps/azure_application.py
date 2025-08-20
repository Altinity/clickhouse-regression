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
from testflows.core import *

from helpers.common import getuid


@TestStep(Given)
async def create_azure_application(
    self,
    tenant_id: str,
    client_id: str,
    client_secret: str,
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
async def create_azure_application_with_secret(
    self, tenant_id, client_secret, client_id
):
    """Create an Azure AD application with a password credential."""

    application_name = "application_with_secret_" + getuid()
    application = await create_azure_application(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        application_name=application_name,
        redirect_uris=["http://localhost:3000/login/azuread"],
        home_page_url="http://localhost:3000",
        logout_url="http://localhost:3000/logout",
    )

    secret = application.password_credentials[0].secret_text
    app_id = application.app_id

    return application, secret, app_id


@TestStep(Given)
async def create_user_in_application(
    self,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    display_name: str,
    mail_nickname: str,
    user_principal_name: str,
    password: str = None,
):
    """Create a user in Azure AD application."""

    client = self.context.client

    if password is None:
        password = "TempPassword123!"

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
    tenant_id: str,
    client_id: str,
    client_secret: str,
    display_name: str,
    mail_nickname: str,
    description: str = None,
    security_enabled: bool = True,
    mail_enabled: bool = False,
):
    """Create a group in Azure AD."""

    client = self.context.client

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
    tenant_id: str,
    client_id: str,
    client_secret: str,
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
