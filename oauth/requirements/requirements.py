# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_042_OAuth_IdentityProviders_Concurrent = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `token_processors` section of `config.xml`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.1.1",
)

RQ_SRS_042_OAuth_IdentityProviders_Change = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.Change",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow changing the identity provider by updating the `token_processors` section in the `config.xml` file. After changing the identity provider, [ClickHouse] SHALL require a restart to apply the new configuration.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.1",
)

RQ_SRS_042_OAuth_IdentityProviders_TokenProcessors_Keycloak = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.TokenProcessors.Keycloak",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support OAuth 2.0 authentication with Keycloak as an identity provider.\n"
        "\n"
        "Example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <keycloak>\n"
        "            <provider>OpenID</provider>\n"
        "            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>\n"
        "            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>\n"
        "            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>\n"
        "            <token_cache_lifetime>60</token_cache_lifetime>\n"
        "        </keycloak>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.3.1.1",
)

RQ_SRS_042_OAuth_Credentials = Requirement(
    name="RQ.SRS-042.OAuth.Credentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Grafana] SHALL redirect grafana user to the Identity Provider authorization endpoint to obtain an access token if the grafana user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.\n"
        "\n"
        "The values SHALL be stored inside the `.env` file which can be generated as:\n"
        "\n"
        "```bash\n"
        'printf "CLIENT_ID=<Client ID (Application ID)>ClientnTENANT_ID=<Tenant ID>ClientnCLIENT_SECRET=<Client Secret>Clientn" > .env\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.1.1",
)

RQ_SRS_042_OAuth_Azure_GetAccessToken = Requirement(
    name="RQ.SRS-042.OAuth.Azure.GetAccessToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "To obtain an access token from Azure AD, you need to register an application in Azure AD and configure the necessary permissions. After that you must collect your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET`.\n"
        "\n"
        "You can obtain an access token using the following command:\n"
        "\n"
        "```bash\n"
        'TENANT_ID="<tenant-guid>"\n'
        'CLIENT_ID="<app-client-id>"\n'
        'CLIENT_SECRET="<app-client-secret>"\n'
        "\n"
        'curl -s -X POST "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \\\n'
        '  -H "Content-Type: application/x-www-form-urlencoded" \\\n'
        '  -d "client_id=${CLIENT_ID}" \\\n'
        '  -d "client_secret=${CLIENT_SECRET}" \\\n'
        '  -d "grant_type=client_credentials" \\\n'
        '  -d "scope=https://graph.microsoft.com/.default"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.1.1",
)

RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token’s issuer, audience, and cryptographic signature.\n"
        "\n"
        "Basic structure:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azure_ad>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>your-client-id</client_id>\n"
        "            <tenant_id>your-tenant-id</tenant_id>\n"
        "            <cache_lifetime>3600</cache_lifetime>\n"
        "        </azure_ad>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is disabled in Azure AD, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.1.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is permanently deleted from Azure AD, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.1.2",
)

RQ_SRS_042_OAuth_Azure_Actions_UserAttributesUpdated = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's attributes (such as `UPN`, `email`, or `name`) are updated in Azure AD, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.1.3",
)

RQ_SRS_042_OAuth_Azure_Actions_UserPasswordReset = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's password is reset in Azure AD, [ClickHouse] SHALL continue to validate access tokens without interruption, as password changes do not invalidate existing tokens.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.1.4",
)

RQ_SRS_042_OAuth_Azure_Actions_UserAddedToGroup = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is added to a group in Azure AD, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.2.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserRemovedFromGroup = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is removed from a group in Azure AD, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.2.2",
)

RQ_SRS_042_OAuth_Azure_Actions_GroupDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a group that is mapped to a [ClickHouse] role is deleted in Azure AD, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.2.3",
)

RQ_SRS_042_OAuth_Azure_Actions_ApplicationDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the client application (service principal) used for OAuth integration is disabled in Azure AD, [ClickHouse] SHALL reject all incoming access tokens issued for that application.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.3.1",
)

RQ_SRS_042_OAuth_Azure_Actions_AdminConsentRemoved = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If the admin consent for required permissions is revoked in Azure AD, [ClickHouse] SHALL reject authentication attempts until consent is granted again.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.3.2",
)

RQ_SRS_042_OAuth_Azure_Actions_ClientSecretRotated = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the client secret for the application is rotated in Azure AD, [ClickHouse] SHALL continue to validate tokens signed with the old secret until they expire, and seamlessly accept tokens signed with the new secret.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.3.3",
)

RQ_SRS_042_OAuth_Azure_Actions_UserSessionRevoked = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's sign-in sessions are revoked in Azure AD (for example, via the `revokeSignInSessions` API), [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.4.1",
)

RQ_SRS_042_OAuth_Azure_Actions_RefreshTokenExpired = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a refresh token expires as per the policy in Azure AD, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.4.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ForwardOAuthIdentity = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.\n"
        "\n"
        '<img width="1023" height="266" alt="Screenshot from 2025-07-28 16-12-02" src="https://github.com/user-attachments/assets/6c9f38f1-ceaf-480a-8ca4-6599968cbb61" />\n'
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is not defined locally, [ClickHouse] SHALL use the `Azure` as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azuure>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>$CLIENT_ID</client_id>\n"
        "            <tenant_id>$TENANT_ID</tenant_id>\n"
        "        </azuure>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>azuure</processor>\n"
        "            <common_roles>\n"
        "                <token_test_role_1 />\n"
        "            </common_roles>\n"
        "            <roles_filter>\n"
        "                \\bclickhouse-[a-zA-Z0-9]+\\b\n"
        "            </roles_filter>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.5.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_provider = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_clientId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_tenantId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token_processors` or `user_directories` sections contain multiple entries that are the same. \n"
        "\n"
        "For example, if there are multiple `<azuure>` entries in the `token_processors` section or multiple `<token>` entries in the `user_directories` section with the same `processor` attribute.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.1.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_clientId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_tenantId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.7",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.1.2.8",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_UserGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.UserGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support user groups defined in Azure Active Directory (Azure AD) for role-based access control. In order to create a user group in Azure AD, you must obtain an [access token with the necessary permissions](#getting-access-token-from-azure) to create groups.\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/groups" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "displayName": "My App Users",\n'
        '    "mailEnabled": false,\n'
        '    "mailNickname": "myAppUsersNickname",\n'
        '    "securityEnabled": true,\n'
        '    "description": "Users allowed to access My App"\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles \n"
        "assigned to the user in the `users_directories` section. Role mapping is based on the role name: \n"
        "if a user has a group or permission in Azure (or another IdP) and there is a role with the same name in \n"
        "ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.\n"
        "\n"
        "The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.\n"
        "\n"
        '<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />\n'
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_GroupFiltering = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.GroupFiltering",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the `Azure` based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>processor_name</processor>\n"
        "            <common_roles>\n"
        "                <token_test_role_1 />\n"
        "            </common_roles>\n"
        "            <roles_filter>\n"
        "                \\bclickhouse-[a-zA-Z0-9]+\\b\n"
        "            </roles_filter>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "The regex pattern `\\bclickhouse-[a-zA-Z0-9]+\\b` filters Azure AD group names to only match those that:\n"
        "\n"
        '* Begin with exactly "clickhouse-"\n'
        "* Are followed by one or more alphanumeric characters\n"
        "* Are complete words (not parts of larger words)\n"
        "\n"
        'This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.\n'
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.3.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_MultipleGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.MultipleGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to multiple groups in the `Azure`, [ClickHouse] SHALL combine all roles that match these group names.\n"
        "The user SHALL inherit the union of all permissions from these roles.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.4.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_OverlappingUsers = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.OverlappingUsers",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When multiple groups in the `Azure` contain the same user, [ClickHouse] SHALL not create duplicate role assignments.\n"
        "The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.5.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a grafana user is authenticated via OAuth and Azure does not return any groups for the user, \n"
        "[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.6.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SubgroupMemberships = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SubgroupMemberships",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to subgroups in the `Azure`, [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.7.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoMatchingClickHouseRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingClickHouseRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reflect changes in a user’s group memberships from the `Azure` dynamically during the next token validation or cache refresh.\n"
        "Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.8.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SameName = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.9.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoMatchingRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.10.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoPermissionToViewGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign a default role to the user.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.11.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoDefaultRole = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, grafana user will not be able to perform any actions after authentication.\n"
        "\n"
        "The role configuration example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azuure>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>$CLIENT_ID</client_id>\n"
        "            <tenant_id>$TENANT_ID</tenant_id>\n"
        "        </azuure>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>azuure</processor>\n"
        "            <common_roles>\n"
        "            </common_roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.5.2.12.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoAccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the grafana user to authenticate and access resources.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.3.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Alg = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Typ = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Signature = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include incorrect or malformed body content.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Sub = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.7",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Aud = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.8",
)

RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Exp = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.9",
)

RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_Expired = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].\n" "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_Incorrect = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject JWT tokens that are malformed, have an invalid signature, or do not conform to the expected structure.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_NonAlphaNumeric = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject JWT tokens that contain non-alphanumeric characters in the header or payload sections, as these are not valid according to the JWT specification.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_EmptyString = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject empty string values in the Authorization header or any other part of the request that expects a JWT token. An empty string is not a valid JWT and SHALL not be accepted.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Caching = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL cache the token provided by [Grafana] for a configurable period of time to reduce the load on the Identity Provider. The cache lifetime SHALL be defined in the `token_processors` configuration.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azuure>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>$CLIENT_ID</client_id>\n"
        "            <tenant_id>$TENANT_ID</tenant_id>\n"
        "            <cache_lifetime>60</cache_lifetime>\n"
        "        </azuure>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>azuure</processor>\n"
        "            <common_roles>\n"
        "                <token_test_role_1 />\n"
        "            </common_roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this case the cache will be valid for 60 seconds. After this period.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.3.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_NoCache = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If the value of `cache_lifetime` is `0` in the `token_processors` configuration, [ClickHouse] SHALL not cache the tokens and SHALL validate each token on every request.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.6.3.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_CacheLifetime = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL evict cached tokens after the `cache_lifetime` period defined in the `token_processors` configuration. If the cache was evicted, [ClickHouse] SHALL cache the new token provided by [Grafana] for the next requests.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.6.3.3.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_MaxCacheSize = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL limit the maximum size of the cache for access tokens. If the cache exceeds this size, [ClickHouse] SHALL evict the oldest tokens to make room for new ones.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.6.3.4.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_Policy = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use the Least Recently Used (LRU) cache eviction policy for access tokens. This means that when the cache reaches its maximum size, the least recently used tokens SHALL be removed to make space for new tokens.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.6.3.5.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Actions_Authentication = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via `HTTP` or `TCP` connection.\n"
        "\n"
        "For example,\n"
        "\n"
        "```bash\n"
        "curl 'http://localhost:8080/?' Client\n"
        " -H 'Authorization: Bearer <TOKEN>' Client\n"
        " -H 'Content type: text/plain;charset=UTF-8' Client\n"
        " --data-raw 'SELECT current_user()'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.4.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Actions_Authentication_Client = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via the `clickhouse client --jwt <token>` command.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.4.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Actions_SessionManagement = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL manage user sessions based on the validity of the access token. If the token is valid, the session SHALL remain active. If the token is invalid or expired, the session SHALL be terminated, and the user SHALL be required to log in again with a new token.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.5.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_Actions_SessionManagement_RefreshToken = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement.RefreshToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support refreshing user sessions using a refresh token if the identity provider supports it. If a refresh token is provided, [ClickHouse] SHALL use it to obtain a new access token without requiring the user to log in again.\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[Grafana]: https://grafana.com\n"
    ),
    link=None,
    level=4,
    num="7.6.5.2",
)

SRS_042_OAuth_Authentication_in_ClickHouse = Specification(
    name="SRS-042 OAuth Authentication in ClickHouse",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Structure of OAuth", level=2, num="1.1"),
        Heading(name="Definitions", level=1, num="2"),
        Heading(name="Overview of the Functionality", level=1, num="3"),
        Heading(name="Access Token Processors", level=2, num="3.1"),
        Heading(name="Authentication Modes with OAuth Tokens", level=2, num="3.2"),
        Heading(name="Authentication with OAuth", level=1, num="4"),
        Heading(name="Identity Providers", level=1, num="5"),
        Heading(
            name="Number of Identity Providers That Can Be Used Concurrently",
            level=2,
            num="5.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.Concurrent", level=3, num="5.1.1"
        ),
        Heading(name="Changing Identity Providers", level=2, num="5.2"),
        Heading(name="RQ.SRS-042.OAuth.IdentityProviders.Change", level=3, num="5.2.1"),
        Heading(name="Keycloak", level=2, num="5.3"),
        Heading(name="Access Token Processors For Keycloak", level=3, num="5.3.1"),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.TokenProcessors.Keycloak",
            level=4,
            num="5.3.1.1",
        ),
        Heading(name="Setting Up OAuth Authentication", level=1, num="6"),
        Heading(name="Credentials", level=2, num="6.1"),
        Heading(name="RQ.SRS-042.OAuth.Credentials", level=3, num="6.1.1"),
        Heading(name="Azure", level=1, num="7"),
        Heading(name="Getting Access Token from Azure", level=2, num="7.1"),
        Heading(name="RQ.SRS-042.OAuth.Azure.GetAccessToken", level=3, num="7.1.1"),
        Heading(name="Access Token Processors For Azure", level=2, num="7.2"),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors",
            level=3,
            num="7.2.1",
        ),
        Heading(name="Azure Identity Management Actions", level=2, num="7.3"),
        Heading(name="User State Changes", level=3, num="7.3.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserDisabled", level=4, num="7.3.1.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserDeleted", level=4, num="7.3.1.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated",
            level=4,
            num="7.3.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset",
            level=4,
            num="7.3.1.4",
        ),
        Heading(name="Group and Role Membership", level=3, num="7.3.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup",
            level=4,
            num="7.3.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup",
            level=4,
            num="7.3.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted", level=4, num="7.3.2.3"
        ),
        Heading(name="Application and Consent", level=3, num="7.3.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled",
            level=4,
            num="7.3.3.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved",
            level=4,
            num="7.3.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated",
            level=4,
            num="7.3.3.3",
        ),
        Heading(name="Token and Session Management", level=3, num="7.3.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked",
            level=4,
            num="7.3.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired",
            level=4,
            num="7.3.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity",
            level=2,
            num="7.4",
        ),
        Heading(name="User Directories", level=2, num="7.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories",
            level=3,
            num="7.5.1",
        ),
        Heading(
            name="Incorrect Configuration in User Directories", level=4, num="7.5.1.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider",
            level=5,
            num="7.5.1.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId",
            level=5,
            num="7.5.1.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId",
            level=5,
            num="7.5.1.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor",
            level=5,
            num="7.5.1.1.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles",
            level=5,
            num="7.5.1.1.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries",
            level=5,
            num="7.5.1.1.6",
        ),
        Heading(
            name="Missing Configuration in User Directories", level=4, num="7.5.1.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors",
            level=5,
            num="7.5.1.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider",
            level=5,
            num="7.5.1.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId",
            level=5,
            num="7.5.1.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId",
            level=5,
            num="7.5.1.2.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories",
            level=5,
            num="7.5.1.2.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token",
            level=5,
            num="7.5.1.2.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor",
            level=5,
            num="7.5.1.2.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles",
            level=5,
            num="7.5.1.2.8",
        ),
        Heading(name="User Groups in Azure", level=3, num="7.5.2"),
        Heading(name="Setting up User Groups in Azure", level=4, num="7.5.2.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.UserGroups",
            level=5,
            num="7.5.2.1.1",
        ),
        Heading(
            name="Query Execution Based on User Roles in ClickHouse",
            level=4,
            num="7.5.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles",
            level=5,
            num="7.5.2.2.1",
        ),
        Heading(
            name="Filtering Azure Groups for Role Assignment", level=4, num="7.5.2.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.GroupFiltering",
            level=5,
            num="7.5.2.3.1",
        ),
        Heading(name="User in Multiple Groups", level=4, num="7.5.2.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.MultipleGroups",
            level=5,
            num="7.5.2.4.1",
        ),
        Heading(
            name="No Duplicate Role Assignments for Overlapping Azure Groups",
            level=4,
            num="7.5.2.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.OverlappingUsers",
            level=5,
            num="7.5.2.5.1",
        ),
        Heading(name="No Azure Groups Returned for User", level=4, num="7.5.2.6"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoGroups",
            level=5,
            num="7.5.2.6.1",
        ),
        Heading(
            name="Azure Subgroup Memberships Not Considered", level=4, num="7.5.2.7"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SubgroupMemberships",
            level=5,
            num="7.5.2.7.1",
        ),
        Heading(name="Dynamic Group Membership Updates", level=4, num="7.5.2.8"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingClickHouseRoles",
            level=5,
            num="7.5.2.8.1",
        ),
        Heading(
            name="Azure Group Names Match Roles in ClickHouse", level=4, num="7.5.2.9"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName",
            level=5,
            num="7.5.2.9.1",
        ),
        Heading(name="No Matching Roles in ClickHouse", level=4, num="7.5.2.10"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles",
            level=5,
            num="7.5.2.10.1",
        ),
        Heading(name="User Cannot View Groups in Azure", level=4, num="7.5.2.11"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups",
            level=5,
            num="7.5.2.11.1",
        ),
        Heading(
            name="In ClickHouse There Is No Default Role Specified",
            level=4,
            num="7.5.2.12",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole",
            level=5,
            num="7.5.2.12.1",
        ),
        Heading(
            name="Access Token Processors are Missing From ClickHouse Configuration",
            level=3,
            num="7.5.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors",
            level=4,
            num="7.5.3.1",
        ),
        Heading(name="ClickHouse Actions After Token Validation", level=2, num="7.6"),
        Heading(name="Incorrect Requests to ClickHouse", level=3, num="7.6.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests",
            level=4,
            num="7.6.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header",
            level=4,
            num="7.6.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg",
            level=4,
            num="7.6.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ",
            level=4,
            num="7.6.1.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature",
            level=4,
            num="7.6.1.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body",
            level=4,
            num="7.6.1.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub",
            level=4,
            num="7.6.1.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud",
            level=4,
            num="7.6.1.8",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp",
            level=4,
            num="7.6.1.9",
        ),
        Heading(name="Token Handling", level=3, num="7.6.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired",
            level=4,
            num="7.6.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect",
            level=4,
            num="7.6.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric",
            level=4,
            num="7.6.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString",
            level=4,
            num="7.6.2.4",
        ),
        Heading(name="Caching", level=3, num="7.6.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching",
            level=4,
            num="7.6.3.1",
        ),
        Heading(name="Disable Caching", level=4, num="7.6.3.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache",
            level=5,
            num="7.6.3.2.1",
        ),
        Heading(name="Cache Lifetime", level=4, num="7.6.3.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime",
            level=5,
            num="7.6.3.3.1",
        ),
        Heading(name="Exceeding Max Cache Size", level=4, num="7.6.3.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize",
            level=5,
            num="7.6.3.4.1",
        ),
        Heading(name="Cache Eviction Policy", level=4, num="7.6.3.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy",
            level=5,
            num="7.6.3.5.1",
        ),
        Heading(name="Authentication and Login", level=3, num="7.6.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication",
            level=4,
            num="7.6.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client",
            level=4,
            num="7.6.4.2",
        ),
        Heading(name="Session Management", level=3, num="7.6.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement",
            level=4,
            num="7.6.5.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement.RefreshToken",
            level=4,
            num="7.6.5.2",
        ),
    ),
    requirements=(
        RQ_SRS_042_OAuth_IdentityProviders_Concurrent,
        RQ_SRS_042_OAuth_IdentityProviders_Change,
        RQ_SRS_042_OAuth_IdentityProviders_TokenProcessors_Keycloak,
        RQ_SRS_042_OAuth_Credentials,
        RQ_SRS_042_OAuth_Azure_GetAccessToken,
        RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors,
        RQ_SRS_042_OAuth_Azure_Actions_UserDisabled,
        RQ_SRS_042_OAuth_Azure_Actions_UserDeleted,
        RQ_SRS_042_OAuth_Azure_Actions_UserAttributesUpdated,
        RQ_SRS_042_OAuth_Azure_Actions_UserPasswordReset,
        RQ_SRS_042_OAuth_Azure_Actions_UserAddedToGroup,
        RQ_SRS_042_OAuth_Azure_Actions_UserRemovedFromGroup,
        RQ_SRS_042_OAuth_Azure_Actions_GroupDeleted,
        RQ_SRS_042_OAuth_Azure_Actions_ApplicationDisabled,
        RQ_SRS_042_OAuth_Azure_Actions_AdminConsentRemoved,
        RQ_SRS_042_OAuth_Azure_Actions_ClientSecretRotated,
        RQ_SRS_042_OAuth_Azure_Actions_UserSessionRevoked,
        RQ_SRS_042_OAuth_Azure_Actions_RefreshTokenExpired,
        RQ_SRS_042_OAuth_Grafana_Authentication_ForwardOAuthIdentity,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_provider,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_clientId,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_tenantId,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_clientId,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_tenantId,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_UserGroups,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_GroupFiltering,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_MultipleGroups,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_OverlappingUsers,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoGroups,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SubgroupMemberships,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoMatchingClickHouseRoles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SameName,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoMatchingRoles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoPermissionToViewGroups,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoDefaultRole,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoAccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Alg,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Typ,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Header_Signature,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Sub,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Aud,
        RQ_SRS_042_OAuth_Grafana_Authentication_IncorrectRequests_Body_Exp,
        RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_Expired,
        RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_Incorrect,
        RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_NonAlphaNumeric,
        RQ_SRS_042_OAuth_Grafana_Authentication_TokenHandling_EmptyString,
        RQ_SRS_042_OAuth_Grafana_Authentication_Caching,
        RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_NoCache,
        RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_CacheLifetime,
        RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_MaxCacheSize,
        RQ_SRS_042_OAuth_Grafana_Authentication_Caching_CacheEviction_Policy,
        RQ_SRS_042_OAuth_Grafana_Authentication_Actions_Authentication,
        RQ_SRS_042_OAuth_Grafana_Authentication_Actions_Authentication_Client,
        RQ_SRS_042_OAuth_Grafana_Authentication_Actions_SessionManagement,
        RQ_SRS_042_OAuth_Grafana_Authentication_Actions_SessionManagement_RefreshToken,
    ),
    content=r"""
# SRS-042 OAuth Authentication in ClickHouse
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Structure of OAuth](#structure-of-oauth)
* 2 [Definitions](#definitions)
* 3 [Overview of the Functionality](#overview-of-the-functionality)
    * 3.1 [Access Token Processors](#access-token-processors)
    * 3.2 [Authentication Modes with OAuth Tokens](#authentication-modes-with-oauth-tokens)
* 4 [Authentication with OAuth](#authentication-with-oauth)
* 5 [Identity Providers](#identity-providers)
    * 5.1 [Number of Identity Providers That Can Be Used Concurrently](#number-of-identity-providers-that-can-be-used-concurrently)
        * 5.1.1 [RQ.SRS-042.OAuth.IdentityProviders.Concurrent](#rqsrs-042oauthidentityprovidersconcurrent)
    * 5.2 [Changing Identity Providers](#changing-identity-providers)
        * 5.2.1 [RQ.SRS-042.OAuth.IdentityProviders.Change](#rqsrs-042oauthidentityproviderschange)
    * 5.3 [Keycloak](#keycloak)
        * 5.3.1 [Access Token Processors For Keycloak](#access-token-processors-for-keycloak)
            * 5.3.1.1 [RQ.SRS-042.OAuth.IdentityProviders.TokenProcessors.Keycloak](#rqsrs-042oauthidentityproviderstokenprocessorskeycloak)
* 6 [Setting Up OAuth Authentication](#setting-up-oauth-authentication)
    * 6.1 [Credentials](#credentials)
        * 6.1.1 [RQ.SRS-042.OAuth.Credentials](#rqsrs-042oauthcredentials)
* 7 [Azure](#azure)
    * 7.1 [Getting Access Token from Azure](#getting-access-token-from-azure)
        * 7.1.1 [RQ.SRS-042.OAuth.Azure.GetAccessToken](#rqsrs-042oauthazuregetaccesstoken)
    * 7.2 [Access Token Processors For Azure](#access-token-processors-for-azure)
        * 7.2.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors](#rqsrs-042oauthidentityprovidersaccesstokenprocessors)
    * 7.3 [Azure Identity Management Actions](#azure-identity-management-actions)
        * 7.3.1 [User State Changes](#user-state-changes)
            * 7.3.1.1 [RQ.SRS-042.OAuth.Azure.Actions.UserDisabled](#rqsrs-042oauthazureactionsuserdisabled)
            * 7.3.1.2 [RQ.SRS-042.OAuth.Azure.Actions.UserDeleted](#rqsrs-042oauthazureactionsuserdeleted)
            * 7.3.1.3 [RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated](#rqsrs-042oauthazureactionsuserattributesupdated)
            * 7.3.1.4 [RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset](#rqsrs-042oauthazureactionsuserpasswordreset)
        * 7.3.2 [Group and Role Membership](#group-and-role-membership)
            * 7.3.2.1 [RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup](#rqsrs-042oauthazureactionsuseraddedtogroup)
            * 7.3.2.2 [RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup](#rqsrs-042oauthazureactionsuserremovedfromgroup)
            * 7.3.2.3 [RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted](#rqsrs-042oauthazureactionsgroupdeleted)
        * 7.3.3 [Application and Consent](#application-and-consent)
            * 7.3.3.1 [RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled](#rqsrs-042oauthazureactionsapplicationdisabled)
            * 7.3.3.2 [RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved](#rqsrs-042oauthazureactionsadminconsentremoved)
            * 7.3.3.3 [RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated](#rqsrs-042oauthazureactionsclientsecretrotated)
        * 7.3.4 [Token and Session Management](#token-and-session-management)
            * 7.3.4.1 [RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked](#rqsrs-042oauthazureactionsusersessionrevoked)
            * 7.3.4.2 [RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired](#rqsrs-042oauthazureactionsrefreshtokenexpired)
    * 7.4 [RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaauthenticationforwardoauthidentity)
    * 7.5 [User Directories](#user-directories)
        * 7.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories](#rqsrs-042oauthgrafanaauthenticationuserdirectories)
            * 7.5.1.1 [Incorrect Configuration in User Directories](#incorrect-configuration-in-user-directories)
                * 7.5.1.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationprovider)
                * 7.5.1.1.2 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationclientid)
                * 7.5.1.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtenantid)
                * 7.5.1.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenprocessor)
                * 7.5.1.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenroles)
                * 7.5.1.1.6 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorsmultipleentries)
            * 7.5.1.2 [Missing Configuration in User Directories](#missing-configuration-in-user-directories)
                * 7.5.1.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationaccesstokenprocessors)
                * 7.5.1.2.2 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorsprovider)
                * 7.5.1.2.3 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorsclientid)
                * 7.5.1.2.4 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorstenantid)
                * 7.5.1.2.5 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectories)
                * 7.5.1.2.6 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestoken)
                * 7.5.1.2.7 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenprocessor)
                * 7.5.1.2.8 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenroles)
        * 7.5.2 [User Groups in Azure](#user-groups-in-azure)
            * 7.5.2.1 [Setting up User Groups in Azure](#setting-up-user-groups-in-azure)
                * 7.5.2.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.UserGroups](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesusergroups)
            * 7.5.2.2 [Query Execution Based on User Roles in ClickHouse](#query-execution-based-on-user-roles-in-clickhouse)
                * 7.5.2.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles](#rqsrs-042oauthgrafanaauthenticationuserroles)
            * 7.5.2.3 [Filtering Azure Groups for Role Assignment](#filtering-azure-groups-for-role-assignment)
                * 7.5.2.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.GroupFiltering](#rqsrs-042oauthgrafanaauthenticationuserrolesgroupfiltering)
            * 7.5.2.4 [User in Multiple Groups](#user-in-multiple-groups)
                * 7.5.2.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.MultipleGroups](#rqsrs-042oauthgrafanaauthenticationuserrolesmultiplegroups)
            * 7.5.2.5 [No Duplicate Role Assignments for Overlapping Azure Groups](#no-duplicate-role-assignments-for-overlapping-azure-groups)
                * 7.5.2.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.OverlappingUsers](#rqsrs-042oauthgrafanaauthenticationuserrolesoverlappingusers)
            * 7.5.2.6 [No Azure Groups Returned for User](#no-azure-groups-returned-for-user)
                * 7.5.2.6.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoGroups](#rqsrs-042oauthgrafanaauthenticationuserrolesnogroups)
            * 7.5.2.7 [Azure Subgroup Memberships Not Considered](#azure-subgroup-memberships-not-considered)
                * 7.5.2.7.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SubgroupMemberships](#rqsrs-042oauthgrafanaauthenticationuserrolessubgroupmemberships)
            * 7.5.2.8 [Dynamic Group Membership Updates](#dynamic-group-membership-updates)
                * 7.5.2.8.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingClickHouseRoles](#rqsrs-042oauthgrafanaauthenticationuserrolesnomatchingclickhouseroles)
            * 7.5.2.9 [Azure Group Names Match Roles in ClickHouse](#azure-group-names-match-roles-in-clickhouse)
                * 7.5.2.9.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName](#rqsrs-042oauthgrafanaauthenticationuserrolessamename)
            * 7.5.2.10 [No Matching Roles in ClickHouse](#no-matching-roles-in-clickhouse)
                * 7.5.2.10.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthgrafanaauthenticationuserrolesnomatchingroles)
            * 7.5.2.11 [User Cannot View Groups in Azure](#user-cannot-view-groups-in-azure)
                * 7.5.2.11.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthgrafanaauthenticationuserrolesnopermissiontoviewgroups)
            * 7.5.2.12 [In ClickHouse There Is No Default Role Specified](#in-clickhouse-there-is-no-default-role-specified)
                * 7.5.2.12.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthgrafanaauthenticationuserrolesnodefaultrole)
        * 7.5.3 [Access Token Processors are Missing From ClickHouse Configuration](#access-token-processors-are-missing-from-clickhouse-configuration)
            * 7.5.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationuserrolesnoaccesstokenprocessors)
    * 7.6 [ClickHouse Actions After Token Validation](#clickhouse-actions-after-token-validation)
        * 7.6.1 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
            * 7.6.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests](#rqsrs-042oauthgrafanaauthenticationincorrectrequests)
            * 7.6.1.2 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheader)
            * 7.6.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheaderalg)
            * 7.6.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheadertyp)
            * 7.6.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheadersignature)
            * 7.6.1.6 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbody)
            * 7.6.1.7 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodysub)
            * 7.6.1.8 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodyaud)
            * 7.6.1.9 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodyexp)
        * 7.6.2 [Token Handling](#token-handling)
            * 7.6.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired](#rqsrs-042oauthgrafanaauthenticationtokenhandlingexpired)
            * 7.6.2.2 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect](#rqsrs-042oauthgrafanaauthenticationtokenhandlingincorrect)
            * 7.6.2.3 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric](#rqsrs-042oauthgrafanaauthenticationtokenhandlingnonalphanumeric)
            * 7.6.2.4 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString](#rqsrs-042oauthgrafanaauthenticationtokenhandlingemptystring)
        * 7.6.3 [Caching](#caching)
            * 7.6.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching](#rqsrs-042oauthgrafanaauthenticationcaching)
            * 7.6.3.2 [Disable Caching](#disable-caching)
                * 7.6.3.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionnocache)
            * 7.6.3.3 [Cache Lifetime](#cache-lifetime)
                * 7.6.3.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictioncachelifetime)
            * 7.6.3.4 [Exceeding Max Cache Size](#exceeding-max-cache-size)
                * 7.6.3.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionmaxcachesize)
            * 7.6.3.5 [Cache Eviction Policy](#cache-eviction-policy)
                * 7.6.3.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionpolicy)
        * 7.6.4 [Authentication and Login](#authentication-and-login)
            * 7.6.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication](#rqsrs-042oauthgrafanaauthenticationactionsauthentication)
            * 7.6.4.2 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client](#rqsrs-042oauthgrafanaauthenticationactionsauthenticationclient)
        * 7.6.5 [Session Management](#session-management)
            * 7.6.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement](#rqsrs-042oauthgrafanaauthenticationactionssessionmanagement)
            * 7.6.5.2 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement.RefreshToken](#rqsrs-042oauthgrafanaauthenticationactionssessionmanagementrefreshtoken)

    
## Introduction

This Software Requirements Specification (SRS) defines the requirements for OAuth 2.0 authentication support in [ClickHouse].

OAuth 2.0 is an industry-standard authorization framework (defined in [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)) that enables third-party applications to obtain limited access to an HTTP service, either on behalf of a user or using application credentials. It decouples authentication from authorization, allowing for more secure and flexible access control mechanisms.

Integrating OAuth 2.0 in [ClickHouse] allows the system to delegate user authentication to trusted external identity providers (such as Google, Microsoft, or Okta), streamlining user management and enhancing security.

Through OAuth 2.0, [ClickHouse] can accept access tokens issued by an identity provider and validate them using static or dynamic JSON Web Key Sets (JWKS). The access token—typically a JWT—includes user identity and scope information that [ClickHouse] can use to authorize requests to resources.

This approach supports a wide range of identity federation use cases and enables [ClickHouse] to function within modern enterprise authentication ecosystems.

### Structure of OAuth

OAuth 2.0 defines several roles and token types used in the process of authorizing access to protected resources:

  * **Resource Owner:** The user or system that owns the data or resource.

  * **Client:** The application requesting access on behalf of the resource owner.
  * **Authorization Server:** The server that authenticates the resource owner and issues access tokens to the client.

  * **Resource Server:** The server (e.g., [ClickHouse]) that hosts the protected resources and verifies access tokens.

OAuth 2.0 typically issues two types of tokens:

  * **Access Token:** A short-lived token used by the client to access protected resources. In many implementations, the access token is a JWT that encodes user identity and scopes (permissions).

  * **Refresh Token:** An optional long-lived token used to obtain new access tokens without re-authenticating the user.

## Definitions

- **Identity Provider (IdP):** A service that issues access tokens after authenticating users. Examples include Azure Active Directory, Google Identity, and Okta.
- **Access Token:** A token issued by an IdP that grants access to protected resources. It is often a JSON Web Token (JWT) containing user identity and permissions.
- **[JWT (JSON Web Token)](https://github.com/Altinity/clickhouse-regression/blob/main/jwt_authentication/requirements/requirements.md):** A compact, URL-safe means of representing claims to be transferred between two parties. It is used in OAuth 2.0 for access tokens.

## Overview of the Functionality

To enable OAuth 2.0 authentication in [ClickHouse], one must define Access Token Processors, which allow [ClickHouse] to validate and trust OAuth 2.0 access tokens issued by external Identity Providers (IdPs), such as Azure AD.

OAuth-based authentication works by allowing users to authenticate using an access token (often a JWT) issued by the IdP. [ClickHouse] supports two modes of operation with these tokens:

**Locally Defined Users:** If a user is already defined in [ClickHouse] (via users.xml or SQL), their authentication method can be set to jwt, enabling token-based authentication.

**Externally Defined Users:** If a user is not defined locally, [ClickHouse] can still authenticate them by validating the token and retrieving user information from the Identity Provider. If valid, the user is granted access with predefined roles.

All OAuth 2.0 access tokens must be validated through one of the configured `token_processors` in `config.xml`.

### Access Token Processors

Key Parameters:

- **provider:** Specifies the identity provider (for example, `azure`).

- **cache_lifetime:** maximum lifetime of cached token (in seconds). Optional, default: 3600

- **client_id:** The registered application ID in Azure.

- **tenant_id:** The Azure tenant that issues the tokens.

### Authentication Modes with OAuth Tokens

1. **Locally Defined Users with JWT Authentication**
Users defined in `users.xml` or `SQL` can authenticate using tokens if `jwt` is specified as their method:

```xml
<clickhouse>
    <my_user>
        <jwt>
        </jwt>
    </my_user>
</clickhouse>
```

Or via SQL:

Without additional JWT payload checks

```sql
CREATE USER my_user IDENTIFIED WITH jwt;
```

And with additional JWT payload checks

```sql
CREATE USER my_user IDENTIFIED WITH jwt CLAIMS '{"resource_access":{"account": {"roles": ["view-profile"]}}}'
```

2. **External Identity Provider as a User Directory**

When a user is not defined locally, [ClickHouse] can use the `IdP` as a dynamic source of user info. This requires configuring the `<token>` section in `users_directories` and assigning roles:

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
            <cache_lifetime>60</cache_lifetime>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

## Authentication with OAuth

To authenticate with OAuth, grafana user must obtain an access token from the identity provider and present it to [ClickHouse].

## Identity Providers

[ClickHouse] SHALL support OAuth 2.0 authentication with various identity providers, including but not limited to:

- Azure Active Directory
- Google Identity
- Keycloak
- Remote JWKS
- Static JWKS
- Static key

### Number of Identity Providers That Can Be Used Concurrently

#### RQ.SRS-042.OAuth.IdentityProviders.Concurrent
version: 1.0

[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `token_processors` section of `config.xml`.

### Changing Identity Providers

#### RQ.SRS-042.OAuth.IdentityProviders.Change
version: 1.0

[ClickHouse] SHALL allow changing the identity provider by updating the `token_processors` section in the `config.xml` file. After changing the identity provider, [ClickHouse] SHALL require a restart to apply the new configuration.

### Keycloak

#### Access Token Processors For Keycloak

##### RQ.SRS-042.OAuth.IdentityProviders.TokenProcessors.Keycloak
version: 1.0

[ClickHouse] SHALL support OAuth 2.0 authentication with Keycloak as an identity provider.

Example,

```xml
<clickhouse>
    <token_processors>
        <keycloak>
            <provider>OpenID</provider>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>
            <token_cache_lifetime>60</token_cache_lifetime>
        </keycloak>
    </token_processors>
</clickhouse>
```

## Setting Up OAuth Authentication

### Credentials

#### RQ.SRS-042.OAuth.Credentials
version: 1.0

[Grafana] SHALL redirect grafana user to the Identity Provider authorization endpoint to obtain an access token if the grafana user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>ClientnTENANT_ID=<Tenant ID>ClientnCLIENT_SECRET=<Client Secret>Clientn" > .env
```

## Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with Azure Active Directory (Azure AD) as an identity provider.

### Getting Access Token from Azure

#### RQ.SRS-042.OAuth.Azure.GetAccessToken
version: 1.0

To obtain an access token from Azure AD, you need to register an application in Azure AD and configure the necessary permissions. After that you must collect your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET`.

You can obtain an access token using the following command:

```bash
TENANT_ID="<tenant-guid>"
CLIENT_ID="<app-client-id>"
CLIENT_SECRET="<app-client-secret>"

curl -s -X POST "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "grant_type=client_credentials" \
  -d "scope=https://graph.microsoft.com/.default"
```

### Access Token Processors For Azure

#### RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors
version: 1.0

An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token’s issuer, audience, and cryptographic signature.

Basic structure:

```xml
<clickhouse>
    <token_processors>
        <azure_ad>
            <provider>azure</provider>
            <client_id>your-client-id</client_id>
            <tenant_id>your-tenant-id</tenant_id>
            <cache_lifetime>3600</cache_lifetime>
        </azure_ad>
    </token_processors>
</clickhouse>
```

### Azure Identity Management Actions

This section outlines how [ClickHouse] SHALL respond to various actions performed in Azure Active Directory that affect user identity, group membership, and token validity.

#### User State Changes

##### RQ.SRS-042.OAuth.Azure.Actions.UserDisabled
version: 1.0

When a user is disabled in Azure AD, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.

##### RQ.SRS-042.OAuth.Azure.Actions.UserDeleted
version: 1.0

When a user is permanently deleted from Azure AD, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.

##### RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated
version: 1.0

When a user's attributes (such as `UPN`, `email`, or `name`) are updated in Azure AD, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.

##### RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset
version: 1.0

When a user's password is reset in Azure AD, [ClickHouse] SHALL continue to validate access tokens without interruption, as password changes do not invalidate existing tokens.

#### Group and Role Membership

##### RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup
version: 1.0

When a user is added to a group in Azure AD, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].

##### RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup
version: 1.0

When a user is removed from a group in Azure AD, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.

##### RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted
version: 1.0

When a group that is mapped to a [ClickHouse] role is deleted in Azure AD, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.

#### Application and Consent

##### RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled
version: 1.0

When the client application (service principal) used for OAuth integration is disabled in Azure AD, [ClickHouse] SHALL reject all incoming access tokens issued for that application.

##### RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved
version: 1.0

If the admin consent for required permissions is revoked in Azure AD, [ClickHouse] SHALL reject authentication attempts until consent is granted again.

##### RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated
version: 1.0

When the client secret for the application is rotated in Azure AD, [ClickHouse] SHALL continue to validate tokens signed with the old secret until they expire, and seamlessly accept tokens signed with the new secret.

#### Token and Session Management

##### RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked
version: 1.0

When a user's sign-in sessions are revoked in Azure AD (for example, via the `revokeSignInSessions` API), [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.

##### RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired
version: 1.0

When a refresh token expires as per the policy in Azure AD, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.

### RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

<img width="1023" height="266" alt="Screenshot from 2025-07-28 16-12-02" src="https://github.com/user-attachments/assets/6c9f38f1-ceaf-480a-8ca4-6599968cbb61" />

### User Directories

An `external user directory` in [ClickHouse] is a remote identity source (such as `LDAP`, `Kerberos`, or an `OAuth Identity Provider`) 
used to authenticate and retrieve user information that is not defined locally in [ClickHouse]. When enabled, [ClickHouse] dynamically 
validates user credentials and assigns roles based on data from this external system instead of relying solely on locally configured users.

#### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use the `Azure` as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.

For example,

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

##### Incorrect Configuration in User Directories

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token_processors` or `user_directories` sections contain multiple entries that are the same. 

For example, if there are multiple `<azuure>` entries in the `token_processors` section or multiple `<token>` entries in the `user_directories` section with the same `processor` attribute.

##### Missing Configuration in User Directories

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

#### User Groups in Azure

##### Setting up User Groups in Azure

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.UserGroups
version: 1.0

[ClickHouse] SHALL support user groups defined in Azure Active Directory (Azure AD) for role-based access control. In order to create a user group in Azure AD, you must obtain an [access token with the necessary permissions](#getting-access-token-from-azure) to create groups.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/groups" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "My App Users",
    "mailEnabled": false,
    "mailNickname": "myAppUsersNickname",
    "securityEnabled": true,
    "description": "Users allowed to access My App"
  }'
```

##### Query Execution Based on User Roles in ClickHouse

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles
version: 1.0

When a grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles 
assigned to the user in the `users_directories` section. Role mapping is based on the role name: 
if a user has a group or permission in Azure (or another IdP) and there is a role with the same name in 
ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.

The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.

<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />


##### Filtering Azure Groups for Role Assignment

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.GroupFiltering
version: 1.0

When a grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the `Azure` based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.

For example,

```xml
<clickhouse>
    <user_directories>
        <token>
            <processor>processor_name</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
            <roles_filter>
                \bclickhouse-[a-zA-Z0-9]+\b
            </roles_filter>
        </token>
    </user_directories>
</clickhouse>
```

The regex pattern `\bclickhouse-[a-zA-Z0-9]+\b` filters Azure AD group names to only match those that:

* Begin with exactly "clickhouse-"
* Are followed by one or more alphanumeric characters
* Are complete words (not parts of larger words)

This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.

##### User in Multiple Groups

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.MultipleGroups
version: 1.0

When a user belongs to multiple groups in the `Azure`, [ClickHouse] SHALL combine all roles that match these group names.
The user SHALL inherit the union of all permissions from these roles.

##### No Duplicate Role Assignments for Overlapping Azure Groups

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.OverlappingUsers
version: 1.0

When multiple groups in the `Azure` contain the same user, [ClickHouse] SHALL not create duplicate role assignments.
The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.

##### No Azure Groups Returned for User

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoGroups
version: 1.0

When a grafana user is authenticated via OAuth and Azure does not return any groups for the user, 
[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.

##### Azure Subgroup Memberships Not Considered

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SubgroupMemberships
version: 1.0

When a user belongs to subgroups in the `Azure`, [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.

##### Dynamic Group Membership Updates

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingClickHouseRoles
version: 1.0

[ClickHouse] SHALL reflect changes in a user’s group memberships from the `Azure` dynamically during the next token validation or cache refresh.
Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.

##### Azure Group Names Match Roles in ClickHouse

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

##### No Matching Roles in ClickHouse

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

##### User Cannot View Groups in Azure

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign a default role to the user.

##### In ClickHouse There Is No Default Role Specified

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole
version: 1.0

When a grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, grafana user will not be able to perform any actions after authentication.

The role configuration example,

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

#### Access Token Processors are Missing From ClickHouse Configuration

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors
version: 1.0

When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the grafana user to authenticate and access resources.

### ClickHouse Actions After Token Validation

#### Incorrect Requests to ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests
version: 1.0

When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header
version: 1.0

[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body
version: 1.0

[ClickHouse] SHALL reject requests that include incorrect or malformed body content.

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

##### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.

#### Token Handling

##### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].

##### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect
version: 1.0

[ClickHouse] SHALL reject JWT tokens that are malformed, have an invalid signature, or do not conform to the expected structure.

##### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric
version: 1.0

[ClickHouse] SHALL reject JWT tokens that contain non-alphanumeric characters in the header or payload sections, as these are not valid according to the JWT specification.

##### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString
version: 1.0

[ClickHouse] SHALL reject empty string values in the Authorization header or any other part of the request that expects a JWT token. An empty string is not a valid JWT and SHALL not be accepted.

#### Caching

##### RQ.SRS-042.OAuth.Grafana.Authentication.Caching
version: 1.0

[ClickHouse] SHALL cache the token provided by [Grafana] for a configurable period of time to reduce the load on the Identity Provider. The cache lifetime SHALL be defined in the `token_processors` configuration.

For example,

```xml
<clickhouse>
    <token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
            <cache_lifetime>60</cache_lifetime>
        </azuure>
    </token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <common_roles>
                <token_test_role_1 />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

In this case the cache will be valid for 60 seconds. After this period.

##### Disable Caching

###### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache
version: 1.0

If the value of `cache_lifetime` is `0` in the `token_processors` configuration, [ClickHouse] SHALL not cache the tokens and SHALL validate each token on every request.

##### Cache Lifetime

###### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime
version: 1.0

[ClickHouse] SHALL evict cached tokens after the `cache_lifetime` period defined in the `token_processors` configuration. If the cache was evicted, [ClickHouse] SHALL cache the new token provided by [Grafana] for the next requests.

##### Exceeding Max Cache Size

###### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize
version: 1.0

[ClickHouse] SHALL limit the maximum size of the cache for access tokens. If the cache exceeds this size, [ClickHouse] SHALL evict the oldest tokens to make room for new ones.

##### Cache Eviction Policy

###### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy
version: 1.0

[ClickHouse] SHALL use the Least Recently Used (LRU) cache eviction policy for access tokens. This means that when the cache reaches its maximum size, the least recently used tokens SHALL be removed to make space for new tokens.

#### Authentication and Login

##### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via `HTTP` or `TCP` connection.

For example,

```bash
curl 'http://localhost:8080/?' Client
 -H 'Authorization: Bearer <TOKEN>' Client
 -H 'Content type: text/plain;charset=UTF-8' Client
 --data-raw 'SELECT current_user()'
```

##### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via the `clickhouse client --jwt <token>` command.

#### Session Management

##### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement
version: 1.0

[ClickHouse] SHALL manage user sessions based on the validity of the access token. If the token is valid, the session SHALL remain active. If the token is invalid or expired, the session SHALL be terminated, and the user SHALL be required to log in again with a new token.

##### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement.RefreshToken
version: 1.0

[ClickHouse] SHALL support refreshing user sessions using a refresh token if the identity provider supports it. If a refresh token is provided, [ClickHouse] SHALL use it to obtain a new access token without requiring the user to log in again.

[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
""",
)
