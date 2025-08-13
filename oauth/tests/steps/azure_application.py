from azure.identity import ClientSecretCredential
from msgraph.generated.models.application import Application
from msgraph.generated.models.implicit_grant_settings import ImplicitGrantSettings
from msgraph.generated.models.password_credential import PasswordCredential
from msgraph.generated.models.web_application import WebApplication
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
    cred = ClientSecretCredential(tenant_id, client_id, client_secret)
    client = GraphServiceClient(
        credentials=cred, scopes=["https://graph.microsoft.com/.default"]
    )

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
