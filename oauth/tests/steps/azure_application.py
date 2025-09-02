from azure.identity import ClientSecretCredential
from msgraph.generated.models.application import Application
from msgraph.generated.models.implicit_grant_settings import ImplicitGrantSettings
from msgraph.generated.models.password_credential import PasswordCredential
from msgraph.generated.models.web_application import WebApplication
from msgraph.generated.models.user import User
from msgraph.generated.models.group import Group
from msgraph.generated.models.reference_create import ReferenceCreate
from msgraph.generated.models.password_profile import PasswordProfile
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
)
from testflows.core import *
from oauth.requirements.requirements import *

from helpers.common import getuid


@TestStep(Given)
def default_configuration(self, node=None):
    """Configure ClickHouse to use Azure token processor."""
    change_token_processors(
        processor_name="azure",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
def default_idp(self, node=None, common_roles=None, roles_filter=None):
    """Set up default ClickHouse configuration for Azure OAuth authentication."""
    default_configuration(self, node=node)
    change_user_directories_config(
        processor="azure",
        node=node,
        common_roles=common_roles,
        roles_filter=roles_filter,
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
async def create_multiple_users(
    self,
    count: int,
    base_display_name: str = "User",
    base_mail_nickname: str = "user",
    base_user_principal_name: str = "user",
    base_password: str = "TempPassword123!",
):
    """Create multiple users in Azure AD."""

    created_users = []

    for i in range(count):
        display_name = f"{base_display_name}_{i+1}"
        mail_nickname = f"{base_mail_nickname}_{i+1}"
        user_principal_name = (
            f"{base_user_principal_name}_{i+1}@{self.context.tenant_domain}"
        )

        user = await self.create_user(
            display_name=display_name,
            mail_nickname=mail_nickname,
            user_principal_name=user_principal_name,
            password=base_password,
        )

        created_users.append(user)

    return created_users


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
        with Finally("I delete the Azure AD application"):
            delete_application(application_id=app_id)


# Negative Test Steps for Azure OAuth Configuration


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def invalid_processor_type_configuration(self, node=None):
    """Configure ClickHouse with invalid Azure processor type."""
    change_token_processors(
        processor_name="azure_invalid",
        processor_type="invalid_type",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def missing_processor_type_configuration(self, node=None):
    """Configure ClickHouse with missing Azure processor type."""
    change_token_processors(
        processor_name="azure_missing_type",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def empty_processor_type_configuration(self, node=None):
    """Configure ClickHouse with empty Azure processor type."""
    change_token_processors(
        processor_name="azure_empty_type",
        processor_type="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def whitespace_processor_type_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only Azure processor type."""
    change_token_processors(
        processor_name="azure_whitespace_type",
        processor_type="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def case_sensitive_processor_type_configuration(self, node=None):
    """Configure ClickHouse with case-sensitive Azure processor type."""
    change_token_processors(
        processor_name="azure_case_sensitive",
        processor_type="Azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def non_azure_processor_type_configuration(self, node=None):
    """Configure ClickHouse with non-Azure processor type."""
    change_token_processors(
        processor_name="azure_wrong_type",
        processor_type="google",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def invalid_processor_name_configuration(self, node=None):
    """Configure ClickHouse with invalid processor name."""
    change_token_processors(
        processor_name="",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def whitespace_processor_name_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only processor name."""
    change_token_processors(
        processor_name="   ",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def special_chars_processor_name_configuration(self, node=None):
    """Configure ClickHouse with special characters in processor name."""
    change_token_processors(
        processor_name="azure@#$%",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    )
)
def missing_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with missing processor in user directories."""
    change_user_directories_config(
        processor="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    )
)
def whitespace_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only processor in user directories."""
    change_user_directories_config(
        processor="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def non_existent_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with non-existent processor in user directories."""
    change_user_directories_config(
        processor="non_existent_processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def case_mismatch_processor_user_directory_configuration(self, node=None):
    """Configure ClickHouse with case-mismatched processor in user directories."""
    change_user_directories_config(
        processor="Azure_Processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def invalid_common_roles_configuration(self, node=None):
    """Configure ClickHouse with invalid common roles."""
    change_user_directories_config(
        processor="azure",
        common_roles=[""],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def whitespace_common_roles_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only common roles."""
    change_user_directories_config(
        processor="azure",
        common_roles=["   "],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def special_chars_common_roles_configuration(self, node=None):
    """Configure ClickHouse with special characters in common roles."""
    change_user_directories_config(
        processor="azure",
        common_roles=["role@#$%"],
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def invalid_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with invalid roles filter regex."""
    change_user_directories_config(
        processor="azure",
        roles_filter="[invalid regex",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    )
)
def empty_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with empty roles filter."""
    change_user_directories_config(
        processor="azure",
        roles_filter="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles(
        "1.0"
    )
)
def whitespace_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with whitespace-only roles filter."""
    change_user_directories_config(
        processor="azure",
        roles_filter="   ",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    )
)
def malformed_roles_filter_configuration(self, node=None):
    """Configure ClickHouse with malformed roles filter."""
    change_user_directories_config(
        processor="azure",
        roles_filter="\\bclickhouse-[a-zA-Z0-9]+\\b\\",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserRoles_NoAccessTokenProcessors("1.0"),
)
def no_token_processors_configuration(self, node=None):
    """Configure ClickHouse without any token processors."""
    change_token_processors(
        processor_name="empty_processor",
        processor_type=None,
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries(
        "1.0"
    )
)
def duplicate_processor_names_configuration(self, node=None):
    """Configure ClickHouse with duplicate processor names."""
    change_token_processors(
        processor_name="azure_duplicate",
        processor_type="azure",
        node=node,
    )
    change_token_processors(
        processor_name="azure_duplicate",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def invalid_processor_attributes_configuration(self, node=None):
    """Configure ClickHouse with invalid processor attributes."""
    change_token_processors(
        processor_name="azure_invalid_attrs",
        processor_type="azure",
        jwks_uri="invalid://url",
        jwks_cache_lifetime=-1,
        verifier_leeway="invalid",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    )
)
def missing_user_directories_configuration(self, node=None):
    """Configure ClickHouse with token processors but no user directories."""
    change_token_processors(
        processor_name="azure_no_user_dirs",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories(
        "1.0"
    )
)
def empty_user_directories_configuration(self, node=None):
    """Configure ClickHouse with empty user directories configuration."""
    change_user_directories_config(
        processor="",
        common_roles=[],
        roles_filter="",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def malformed_xml_structure_configuration(self, node=None):
    """Configure ClickHouse with malformed XML structure."""
    change_token_processors(
        processor_name="<malformed>",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider(
        "1.0"
    )
)
def null_values_configuration(self, node=None):
    """Configure ClickHouse with null values in configuration."""
    change_token_processors(
        processor_name=None,
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def extremely_long_values_configuration(self, node=None):
    """Configure ClickHouse with extremely long values."""
    long_string = "a" * 10000
    change_token_processors(
        processor_name=long_string,
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def unicode_special_chars_configuration(self, node=None):
    """Configure ClickHouse with Unicode and special characters."""
    change_token_processors(
        processor_name="azure_unicode_测试_🚀",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def sql_injection_attempt_configuration(self, node=None):
    """Configure ClickHouse with SQL injection attempt."""
    change_token_processors(
        processor_name="azure'; DROP TABLE users; --",
        processor_type="azure",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    )
)
def path_traversal_attempt_configuration(self, node=None):
    """Configure ClickHouse with path traversal attempt."""
    change_token_processors(
        processor_name="../../../etc/passwd",
        processor_type="azure",
        node=node,
    )


# Combined negative configurations for comprehensive testing


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor(
        "1.0"
    ),
)
def completely_invalid_configuration(self, node=None):
    """Configure ClickHouse with completely invalid Azure configuration."""
    invalid_processor_type_configuration(self, node=node)
    missing_processor_user_directory_configuration(self, node=node)


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def partially_invalid_configuration(self, node=None):
    """Configure ClickHouse with partially invalid Azure configuration."""
    change_token_processors(
        processor_name="azure_partial",
        processor_type="azure",
        node=node,
    )
    change_user_directories_config(
        processor="non_existent_processor",
        node=node,
    )


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles(
        "1.0"
    ),
)
def mixed_valid_invalid_configuration(self, node=None):
    """Configure ClickHouse with mixed valid and invalid configuration."""
    change_token_processors(
        processor_name="azure_mixed",
        processor_type="azure",
        jwks_uri="invalid://url",
        node=node,
    )
    change_user_directories_config(
        processor="azure_mixed",
        common_roles=["valid_role", ""],
        node=node,
    )


class OAuthProvider:
    get_oauth_token = get_oauth_token
    create_application = create_azure_application
    create_application_with_secret = create_azure_application_with_secret
    create_user = create_user
    create_group = create_group
    assign_user_to_group = assign_user_to_group
    setup_azure_application = setup_azure_application

    # Negative configuration test steps
    invalid_processor_type_configuration = invalid_processor_type_configuration
    missing_processor_type_configuration = missing_processor_type_configuration
    empty_processor_type_configuration = empty_processor_type_configuration
    whitespace_processor_type_configuration = whitespace_processor_type_configuration
    case_sensitive_processor_type_configuration = (
        case_sensitive_processor_type_configuration
    )
    non_azure_processor_type_configuration = non_azure_processor_type_configuration
    invalid_processor_name_configuration = invalid_processor_name_configuration
    whitespace_processor_name_configuration = whitespace_processor_name_configuration
    special_chars_processor_name_configuration = (
        special_chars_processor_name_configuration
    )
    missing_processor_user_directory_configuration = (
        missing_processor_user_directory_configuration
    )
    whitespace_processor_user_directory_configuration = (
        whitespace_processor_user_directory_configuration
    )
    non_existent_processor_user_directory_configuration = (
        non_existent_processor_user_directory_configuration
    )
    case_mismatch_processor_user_directory_configuration = (
        case_mismatch_processor_user_directory_configuration
    )
    invalid_common_roles_configuration = invalid_common_roles_configuration
    whitespace_common_roles_configuration = whitespace_common_roles_configuration
    special_chars_common_roles_configuration = special_chars_common_roles_configuration
    invalid_roles_filter_configuration = invalid_roles_filter_configuration
    empty_roles_filter_configuration = empty_roles_filter_configuration
    whitespace_roles_filter_configuration = whitespace_roles_filter_configuration
    malformed_roles_filter_configuration = malformed_roles_filter_configuration
    no_token_processors_configuration = no_token_processors_configuration
    duplicate_processor_names_configuration = duplicate_processor_names_configuration
    invalid_processor_attributes_configuration = (
        invalid_processor_attributes_configuration
    )
    missing_user_directories_configuration = missing_user_directories_configuration
    empty_user_directories_configuration = empty_user_directories_configuration
    malformed_xml_structure_configuration = malformed_xml_structure_configuration
    null_values_configuration = null_values_configuration
    extremely_long_values_configuration = extremely_long_values_configuration
    unicode_special_chars_configuration = unicode_special_chars_configuration
    sql_injection_attempt_configuration = sql_injection_attempt_configuration
    path_traversal_attempt_configuration = path_traversal_attempt_configuration
    completely_invalid_configuration = completely_invalid_configuration
    partially_invalid_configuration = partially_invalid_configuration
    mixed_valid_invalid_configuration = mixed_valid_invalid_configuration
