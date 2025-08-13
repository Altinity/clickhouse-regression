# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

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
    level=3,
    num="4.1.1",
)

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

RQ_SRS_042_OAuth_Credentials = Requirement(
    name="RQ.SRS-042.OAuth.Credentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Grafana] SHALL redirect Grafana user to the Identity Provider authorization endpoint to obtain an access token if the Grafana userhas provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.\n"
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

RQ_SRS_042_OAuth_Azure_ApplicationSetup_ = Requirement(
    name="RQ.SRS-042.OAuth.Azure.ApplicationSetup ",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support integration with applications registered in [Azure] Active Directory. To set up an application in [Azure] for OAuth authentication, the following steps SHALL be performed:\n"
        "\n"
        "```bash\n"
        'ACCESS_TOKEN="<admin-access-token>"\n'
        "\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/applications" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "displayName": "ClickHouse OAuth App",\n'
        '    "signInAudience": "AzureADMyOrg",\n'
        '    "web": {\n'
        '      "redirectUris": ["http://localhost:3000/login/generic_oauth"]\n'
        "    }\n"
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.1.1",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support validating opaque access tokens issued by [Azure] AD using an Access Token Processor configured for OpenID. The processor SHALL be defined in `config.xml` as follows:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azure_opaque>\n"
        "            <provider>openid</provider>\n"
        "            <configuration_endpoint>https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration</configuration_endpoint>\n"
        "            <cache_lifetime>600</cache_lifetime>\n"
        "            <username_claim>sub</username_claim>\n"
        "            <groups_claim>groups</groups_claim>\n"
        "        </azure_opaque>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.1",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Constraints = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Constraints",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL assume that Azure-issued access tokens are JWT by default. If the token_processors entry for [Azure] is configured in opaque mode, [ClickHouse] SHALL still accept tokens that are JWT strings while performing validation via remote calls as configured by the processor.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.2.1",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When `<provider>azure</provider>` or `<provider>openid</provider>` is used for [Azure] in the `token_processors` section,  \n"
        "[ClickHouse] SHALL validate tokens by calling the configured discovery and/or `/userinfo` introspection endpoints instead  \n"
        'of verifying the token locally. This SHALL be treated as "opaque behavior" operationally, regardless of the underlying token format.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.2.2",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For [Azure] opaque-mode operation, exactly one of the following SHALL be configured per processor:\n"
        "\n"
        "1. `configuration_endpoint`\n"
        "\n"
        "2. both `userinfo_endpoint` and `token_introspection_endpoint`.\n"
        "\n"
        "If neither (or all three) are set, [ClickHouse] SHALL reject the configuration as invalid.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.2.3",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_ProviderType = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ProviderType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "In opaque mode, the provider parameter SHALL indicate the validation strategy and not the human-readable IdP name. \n"
        "For Azure-backed validation, provider MAY be set to [Azure] (Azure-specific flow) or `OpenID` (generic OpenID Connect flow). \n"
        "The chosen provider SHALL determine which endpoints and claims are used.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.3",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_ReferenceToken = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ReferenceToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support an external OAuth gateway that issues reference (opaque) tokens on behalf of [Azure]. In this pattern:\n"
        "\n"
        "* The gateway exchanges [Azure] JWTs for gateway-issued reference tokens.\n"
        "\n"
        "* [ClickHouse] is configured with `<provider>OpenID</provider>` pointing to the gateway's .well-known or its userinfo + `token_introspection` endpoints.\n"
        "\n"
        "* [ClickHouse] SHALL validate tokens exclusively via the gateway's `introspection/userinfo` responses.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.4",
)

RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_Failure = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.Failure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If the gateway's introspection or userinfo call fails, returns inactive/invalid status, or omits required claims, \n"
        "[ClickHouse] SHALL deny authentication and SHALL not fall back to local JWT verification for that request.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.4.1",
)

RQ_SRS_042_OAuth_Azure_GetAccessToken = Requirement(
    name="RQ.SRS-042.OAuth.Azure.GetAccessToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "To obtain an access token from [Azure] AD, you need to register an application in [Azure] AD and configure the necessary permissions. After that you must collect your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET`.\n"
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
    num="7.3.1",
)

RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token's issuer, audience, and cryptographic signature.\n"
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
    num="7.4.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserDirectories_UserGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserDirectories.UserGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support user groups defined in [Azure] Active Directory ([Azure] AD) for role-based access control. In order to create a user group in [Azure] AD, you must obtain an [access token with the necessary permissions](#getting-access-token-from-azure) to create groups.\n"
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
    level=4,
    num="7.5.1.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles \n"
        "assigned to the user in the `users_directories` section. Role mapping is based on the role name: \n"
        "if a user has a group or permission in [Azure] (or another IdP) and there is a role with the same name in\n"
        "ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.\n"
        "\n"
        "The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.\n"
        "\n"
        '<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />\n'
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.2.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_GroupFiltering = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.GroupFiltering",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the [Azure] based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.\n"
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
        "The regex pattern `\\bclickhouse-[a-zA-Z0-9]+\\b` filters [Azure] AD group names to only match those that:\n"
        "\n"
        '* Begin with exactly "clickhouse-"\n'
        "* Are followed by one or more alphanumeric characters\n"
        "* Are complete words (not parts of larger words)\n"
        "\n"
        'This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.3.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_MultipleGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.MultipleGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to multiple groups in the [Azure], [ClickHouse] SHALL combine all roles that match these group names.\n"
        "The user SHALL inherit the union of all permissions from these roles.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.4.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_OverlappingUsers = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.OverlappingUsers",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When multiple groups in the [Azure] contain the same user, [ClickHouse] SHALL not create duplicate role assignments.\n"
        "The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.5.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth and [Azure] does not return any groups for the user,\n"
        "[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.6.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_SubgroupMemberships = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SubgroupMemberships",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to subgroups in the [Azure], [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.7.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoMatchingClickHouseRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingClickHouseRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reflect changes in a user's group memberships from the [Azure] dynamically during the next token validation or cache refresh.\n"
        "Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.5.8.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_SameName = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SameName",
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
    level=4,
    num="7.5.9.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoMatchingRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingRoles",
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
    level=4,
    num="7.5.10.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoPermissionToViewGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoPermissionToViewGroups",
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
    level=4,
    num="7.5.11.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoDefaultRole = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoDefaultRole",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, Grafana userwill not be able to perform any actions after authentication.\n"
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
    level=4,
    num="7.5.12.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is disabled in [Azure] AD, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.\n"
        "\n"
        "```bash\n"
        'curl -s -X PATCH "https://graph.microsoft.com/v1.0/users/{user-id}" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "accountEnabled": false\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is permanently deleted from [Azure] AD, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.\n"
        "\n"
        "```bash\n"
        'curl -s -X DELETE "https://graph.microsoft.com/v1.0/users/{user-id}" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.2",
)

RQ_SRS_042_OAuth_Azure_Actions_UserAttributesUpdated = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's attributes (such as `UPN`, `email`, or `name`) are updated in [Azure] AD, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.\n"
        "\n"
        "```bash\n"
        'curl -s -X PATCH "https://graph.microsoft.com/v1.0/users/{user-id}" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "displayName": "New Name"\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.3",
)

RQ_SRS_042_OAuth_Azure_Actions_UserPasswordReset = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's password is reset in [Azure] AD, [ClickHouse] SHALL continue to validate access tokens without interruption, as password changes do not invalidate existing tokens.\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/authentication/passwordMethods/{method-id}/resetPassword" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "newPassword": "new-password"\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.1.4",
)

RQ_SRS_042_OAuth_Azure_Actions_UserAddedToGroup = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is added to a group in [Azure] AD, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/groups/{group-id}/members/$ref" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{user-id}"\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.1",
)

RQ_SRS_042_OAuth_Azure_Actions_UserRemovedFromGroup = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is removed from a group in [Azure] AD, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.\n"
        "\n"
        "```bash\n"
        'curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}/members/{user-id}/$ref" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.2",
)

RQ_SRS_042_OAuth_Azure_Actions_GroupDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a group that is mapped to a [ClickHouse] role is deleted in [Azure] AD, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.\n"
        "\n"
        "```bash\n"
        'curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.2.3",
)

RQ_SRS_042_OAuth_Azure_Actions_ApplicationDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the client application (service principal) used for OAuth integration is disabled in [Azure] AD, [ClickHouse] SHALL reject all incoming access tokens issued for that application.\n"
        "\n"
        "```bash\n"
        'curl -s -X PATCH "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "accountEnabled": false\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.3.1",
)

RQ_SRS_042_OAuth_Azure_Actions_AdminConsentRemoved = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If the admin consent for required permissions is revoked in [Azure] AD, [ClickHouse] SHALL reject authentication attempts until consent is granted again.\n"
        "\n"
        "```bash\n"
        'curl -s -X DELETE "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments/{assignment-id}" \\\n'
        '    -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.3.2",
)

RQ_SRS_042_OAuth_Azure_Actions_ClientSecretRotated = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the client secret for the application is rotated in [Azure] AD, [ClickHouse] SHALL continue to validate tokens signed with the old secret until they expire, and seamlessly accept tokens signed with the new secret.\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/applications/{app-id}/addPassword" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "passwordCredential": {\n'
        '      "displayName": "New-Secret"\n'
        "    }\n"
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.3.3",
)

RQ_SRS_042_OAuth_Azure_Actions_UserSessionRevoked = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's sign-in sessions are revoked in [Azure] AD (for example, via the `revokeSignInSessions` API), [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/revokeSignInSessions" \\\n'
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d ''\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.4.1",
)

RQ_SRS_042_OAuth_Azure_Actions_RefreshTokenExpired = Requirement(
    name="RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a refresh token expires as per the policy in [Azure] AD, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.\n"
        "\n"
        "```bash\n"
        'curl -s -X POST "https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token" \\\n'
        '  -H "Content-Type: application/x-www-form-urlencoded" \\\n'
        "  -d 'client_id={client-id}' \\\n"
        "  -d 'client_secret={client-secret}' \\\n"
        "  -d 'grant_type=refresh_token' \\\n"
        "  -d 'refresh_token={expired-refresh-token}'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.4.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoAccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the Grafana user to authenticate and access resources.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.6.5.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is not defined locally, [ClickHouse] SHALL use the [Azure] as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.\n"
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
    num="7.7.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_provider = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_clientId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `client_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_tenantId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `tenant_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_roles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_multipleEntries = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token_processors` or `user_directories` sections contain multiple entries that are the same.\n"
        "\n"
        "For example, if there are multiple `<azuure>` entries in the `token_processors` section or multiple `<token>` entries in the `user_directories` section with the same `processor` attribute.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.1.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_provider = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_clientId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `client_id` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_TokenProcessors_tenantId = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `tenant_id` attribute is not defined in the `token_processors` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_processor = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.7",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserDirectories_MissingConfiguration_UserDirectories_token_roles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="7.7.1.2.8",
)

RQ_SRS_042_OAuth_Keycloak_RealmSetup = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.RealmSetup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support integration with Keycloak realms. To set up a realm for OAuth authentication, the following steps SHALL be performed:\n"
        "\n"
        "1. Prepare Realm Configuration JSON:\n"
        "\n"
        "```json\n"
        "{\n"
        '  "realm": "grafana",\n'
        '  "enabled": true,\n'
        '  "clients": [\n'
        "    {\n"
        '      "clientId": "grafana-client",\n'
        '      "name": "Grafana",\n'
        '      "protocol": "openid-connect",\n'
        '      "publicClient": false,\n'
        '      "secret": "grafana-secret",\n'
        '      "redirectUris": ["http://localhost:3000/login/generic_oauth"],\n'
        '      "baseUrl": "http://localhost:3000",\n'
        '      "standardFlowEnabled": true,\n'
        '      "directAccessGrantsEnabled": true,\n'
        '      "protocolMappers": [\n'
        "        {\n"
        '          "name": "groups",\n'
        '          "protocol": "openid-connect",\n'
        '          "protocolMapper": "oidc-group-membership-mapper",\n'
        '          "consentRequired": false,\n'
        '          "config": {\n'
        '            "claim.name": "groups",\n'
        '            "jsonType.label": "String",\n'
        '            "full.path": "false",\n'
        '            "id.token.claim": "true",\n'
        '            "access.token.claim": "true",\n'
        '            "userinfo.token.claim": "true"\n'
        "          }\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "users": [\n'
        "    {\n"
        '      "username": "demo",\n'
        '      "enabled": true,\n'
        '      "email": "demo@example.com",\n'
        '      "firstName": "Demo",\n'
        '      "lastName": "User",\n'
        '      "emailVerified": true,\n'
        '      "groups": ["/grafana-admins", "/can-read"],\n'
        '      "credentials": [\n'
        "        {\n"
        '          "type": "password",\n'
        '          "value": "demo"\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "groups": [\n'
        "    {\n"
        '      "name": "grafana-admins",\n'
        '      "path": "/grafana-admins"\n'
        "    },\n"
        "    {\n"
        '      "name": "can-read",\n'
        '      "path": "/can-read"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n"
        "\n"
        "2. Import Realm into Keycloak Docker Container:\n"
        "\n"
        "```bash\n"
        "docker run --name keycloak \\\n"
        "  -v $(pwd)/realm-export.json:/opt/keycloak/data/import/realm-export.json \\\n"
        "  quay.io/keycloak/keycloak:latest \\\n"
        "  start-dev --import-realm\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.1.1",
)

RQ_SRS_042_OAuth_Keycloak_OpaqueTokenSupport = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.OpaqueTokenSupport",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support validating opaque access tokens issued by Keycloak using an Access Token Processor configured for OpenID. The processor SHALL be defined in config.xml as follows:\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <keycloak_opaque>\n"
        "            <provider>openid</provider>\n"
        "            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>\n"
        "            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>\n"
        "            <cache_lifetime>600</cache_lifetime>\n"
        "            <username_claim>sub</username_claim>\n"
        "            <groups_claim>groups</groups_claim>\n"
        "        </keycloak_opaque>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.2.1",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Constraints = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Constraints",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL assume that Keycloak-issued access tokens are JWT by default. If the `token_processors` entry for \n"
        "[Keycloak] is configured in opaque mode, [ClickHouse] SHALL still accept tokens that are JWT strings while performing validation via remote calls as configured by the processor.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.1",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When <provider>OpenID</provider> is used for Keycloak in the token_processors section, [ClickHouse] SHALL \n"
        "validate tokens by calling the configured discovery and/or user info / introspection endpoints instead of verifying the token locally. \n"
        'This SHALL be treated as "opaque behavior" operationally, regardless of the underlying token\'s format.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.2",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For Keycloak opaque-mode operation, exactly one of the following SHALL be configured per processor:\n"
        "\n"
        "1. `configuration_endpoint`\n"
        "2. both `userinfo_endpoint` and `token_introspection_endpoint`.\n"
        "\n"
        "If neither (or all three) are set, the configuration SHALL be rejected as invalid.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.3",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_ProviderType = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ProviderType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "In opaque mode for Keycloak, provider SHALL be set to OpenID. The processor SHALL obtain endpoints from the Keycloak \n"
        "realm's `.well-known/openid-configuration` or from explicitly provided userinfo and `token_introspection` endpoints.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.4",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_ReferenceToken = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ReferenceToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support an external OAuth gateway that issues reference (opaque) tokens on behalf of Keycloak. In this pattern:\n"
        "\n"
        "* The gateway exchanges Keycloak JWTs for gateway-issued reference tokens.\n"
        "\n"
        "* [ClickHouse] is configured with `<provider>OpenID</provider>` pointing to the gateway's .well-known or its userinfo + token_introspection endpoints.\n"
        "\n"
        "* [ClickHouse] SHALL validate tokens exclusively via the gateway's `introspection/userinfo` responses.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.5",
)

RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_Failure = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.Failure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If the gateway's introspection or userinfo call fails, returns inactive/invalid status, or omits required claims, \n"
        "[ClickHouse] SHALL deny authentication and SHALL not fall back to local JWT verification for that request.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.2.2.6",
)

RQ_SRS_042_OAuth_Keycloak_GetAccessToken = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.GetAccessToken",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "To obtain an access token from Keycloak, you need to have a configured realm, client, and user.\n"
        "\n"
        "You can obtain an access token using the following command:\n"
        "\n"
        "```bash\n"
        "curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token' \\\n"
        "  -H 'Content-Type: application/x-www-form-urlencoded' \\\n"
        "  -d 'grant_type=password' \\\n"
        "  -d 'client_id=my-client' \\\n"
        "  -d 'client_secret=xxxxxxx' \\\n"
        "  -d 'username=john' \\\n"
        "  -d 'password=secret'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.3.1",
)

RQ_SRS_042_OAuth_Keycloak_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "An Access Token Processor for Keycloak defines how [ClickHouse] validates and interprets access tokens. This includes specifying the OpenID provider details.\n"
        "\n"
        "Basic structure:\n"
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
    level=3,
    num="8.4.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserDirectories_UserGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserDirectories.UserGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support user groups defined in Keycloak for role-based access control. In order to create a user group in Keycloak, you must obtain an access token with the necessary permissions to create groups.\n"
        "\n"
        "```bash\n"
        "curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/groups' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "name": "clickhouse-admin",\n'
        '    "attributes": {\n'
        '      "description": ["Users with administrative access to ClickHouse"]\n'
        "    }\n"
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.1.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles \n"
        "assigned to the user in the `users_directories` section. Role mapping is based on the role name: \n"
        "if a user has a group or permission in Keycloak (or another IdP) and there is a role with the same name in\n"
        "ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.\n"
        "\n"
        "The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.2.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_GroupFiltering = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.GroupFiltering",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the `Keycloak` based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>keycloak_processor</processor>\n"
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
        "The regex pattern `\\bclickhouse-[a-zA-Z0-9]+\\b` filters Keycloak group names to only match those that:\n"
        "\n"
        '* Begin with exactly "clickhouse-"\n'
        "* Are followed by one or more alphanumeric characters\n"
        "* Are complete words (not parts of larger words)\n"
        "\n"
        'This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.3.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_MultipleGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.MultipleGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to multiple groups in the `Keycloak`, [ClickHouse] SHALL combine all roles that match these group names.\n"
        "The user SHALL inherit the union of all permissions from these roles.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.4.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_OverlappingUsers = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.OverlappingUsers",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When multiple groups in the `Keycloak` contain the same user, [ClickHouse] SHALL not create duplicate role assignments.\n"
        "The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.5.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth and Keycloak does not return any groups for the user,\n"
        "[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.6.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_SubgroupMemberships = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SubgroupMemberships",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user belongs to subgroups in the `Keycloak`, [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.7.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoMatchingClickHouseRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reflect changes in a user's group memberships from the `Keycloak` dynamically during the next token validation or cache refresh.\n"
        "Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.8.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_SameName = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SameName",
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
    level=4,
    num="8.5.9.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoMatchingRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingRoles",
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
    level=4,
    num="8.5.10.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoPermissionToViewGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups",
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
    level=4,
    num="8.5.11.1",
)

RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoDefaultRole = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoDefaultRole",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a Grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, Grafana userwill not be able to perform any actions after authentication.\n"
        "\n"
        "The role configuration example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <keycloak_processor>\n"
        "            <provider>OpenID</provider>\n"
        "            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>\n"
        "            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>\n"
        "            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>\n"
        "        </keycloak_processor>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>keycloak_processor</processor>\n"
        "            <common_roles>\n"
        "            </common_roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.5.12.1",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is disabled in Keycloak, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.\n"
        "\n"
        "```bash\n"
        "curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "enabled": false\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.1.1",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is permanently deleted from Keycloak, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.\n"
        "\n"
        "```bash\n"
        "curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.1.2",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserAttributesUpdated = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserAttributesUpdated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's attributes (such as `username`, `email`, or `firstName`) are updated in Keycloak, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.\n"
        "\n"
        "```bash\n"
        "curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "username": "new-username",\n'
        '    "email": "new-email@example.com"\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.1.3",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is added to a group in Keycloak, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].\n"
        "\n"
        "```bash\n"
        "curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.2.1",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is removed from a group in Keycloak, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.\n"
        "\n"
        "```bash\n"
        "curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.2.2",
)

RQ_SRS_042_OAuth_Keycloak_Actions_GroupDeleted = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a group that is mapped to a [ClickHouse] role is deleted in Keycloak, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.\n"
        "\n"
        "```bash\n"
        "curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/groups/{group-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.2.3",
)

RQ_SRS_042_OAuth_Keycloak_Actions_ClientDisabled = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the client application used for OAuth integration is disabled in Keycloak, [ClickHouse] SHALL reject all incoming access tokens issued for that client.\n"
        "\n"
        "```bash\n"
        "curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/clients/{client-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '{\n"
        '    "enabled": false\n'
        "  }'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.3.1",
)

RQ_SRS_042_OAuth_Keycloak_Actions_ConsentRevoked = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If a user's consent for the application is revoked in Keycloak, [ClickHouse] SHALL reject authentication attempts until consent is granted again.\n"
        "\n"
        "```bash\n"
        "curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/consents/{client-id}' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.3.2",
)

RQ_SRS_042_OAuth_Keycloak_Actions_UserSessionRevoked = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.UserSessionRevoked",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user's sign-in sessions are revoked in Keycloak, [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.\n"
        "\n"
        "```bash\n"
        "curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/logout' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.4.1",
)

RQ_SRS_042_OAuth_Keycloak_Actions_RefreshTokenRevoked = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.RefreshTokenRevoked",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a refresh token is revoked via the logout endpoint, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.\n"
        "\n"
        "```bash\n"
        "curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout' \\\n"
        "  -H 'Content-Type: application/x-www-form-urlencoded' \\\n"
        "  -d 'client_id=my-client' \\\n"
        "  -d 'client_secret=xxxxxx' \\\n"
        "  -d 'refresh_token=eyJ...'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.4.2",
)

RQ_SRS_042_OAuth_Keycloak_Actions_NotBeforePolicyUpdated = Requirement(
    name="RQ.SRS-042.OAuth.Keycloak.Actions.NotBeforePolicyUpdated",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a `not-before` policy is pushed for a realm or user in Keycloak, all tokens issued before this time SHALL be invalidated, and [ClickHouse] SHALL reject them.\n"
        "\n"
        "```bash\n"
        "curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/push-revocation' \\\n"
        '  -H "Authorization: Bearer ${ACCESS_TOKEN}"\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="8.6.4.3",
)

RQ_SRS_042_OAuth_StaticKey_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support validating JWTs using a static key. The configuration requires specifying the algorithm and the key.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_key_validator>\n"
        "          <algo>HS256</algo>\n"
        "          <static_key>my_static_secret</static_key>\n"
        "        </my_static_key_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.1.1",
)

RQ_SRS_042_OAuth_StaticKey_UserDirectory = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.UserDirectory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static key as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_key_validator>\n"
        "          <algo>HS256</algo>\n"
        "          <static_key>my_static_secret</static_key>\n"
        "        </my_static_key_validator>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>my_static_key_validator</processor>\n"
        "            <common_roles>\n"
        "                <my_role />\n"
        "            </common_roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.2.1",
)

RQ_SRS_042_OAuth_StaticKey_Algorithms = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Algorithms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following algorithms for static key validation:\n"
        "\n"
        "| HMAC  | RSA   | ECDSA  | PSS   | EdDSA   |\n"
        "|-------|-------|--------|-------|---------|\n"
        "| HS256 | RS256 | ES256  | PS256 | Ed25519 |\n"
        "| HS384 | RS384 | ES384  | PS384 | Ed448   |\n"
        "| HS512 | RS512 | ES512  | PS512 |         |\n"
        "|       |       | ES256K |       |         |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.3.1",
)

RQ_SRS_042_OAuth_StaticKey_Algorithm_None = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Algorithm.None",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL  support `None` algorithm.\n" "\n"),
    link=None,
    level=4,
    num="9.3.1.1",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_StaticKey = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `static_key` parameter for symmetric algorithms (HS* family). This parameter SHALL be mandatory for `HS*` family algorithms and SHALL contain the secret key used for signature validation.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_hs256_validator>\n"
        "            <algo>HS256</algo>\n"
        "            <static_key>my_secret_key_for_jwt_signing</static_key>\n"
        "        </my_hs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.1",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_StaticKeyBase64 = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `static_key_in_base64` parameter to indicate if the `static_key` is base64-encoded. This parameter SHALL be optional with a default value of `False`.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_hs256_validator>\n"
        "            <algo>HS256</algo>\n"
        "            <static_key>bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=</static_key>\n"
        "            <static_key_in_base64>true</static_key_in_base64>\n"
        "        </my_hs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, the base64-encoded string `bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=` decodes to `my_secret_key_for_jwt_signing`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.2",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_PublicKey = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `public_key` parameter for asymmetric algorithms. This parameter SHALL be mandatory except for `HS*` family algorithms and `None` algorithm. The public key SHALL be used to verify JWT signatures.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <public_key>-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
        "-----END PUBLIC KEY-----</public_key>\n"
        "        </my_rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.3",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_PrivateKey = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `private_key` parameter for asymmetric algorithms. This parameter SHALL be optional and SHALL be used when the private key is needed for additional operations.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <public_key>-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
        "-----END PUBLIC KEY-----</public_key>\n"
        "            <private_key>-----BEGIN PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n"
        "-----END PRIVATE KEY-----</private_key>\n"
        "        </my_rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.4",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_PublicKeyPassword = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `public_key_password` parameter to specify the password for the public key. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <public_key>-----BEGIN ENCRYPTED PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
        "-----END ENCRYPTED PUBLIC KEY-----</public_key>\n"
        "            <public_key_password>my_public_key_password</public_key_password>\n"
        "        </my_rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.5",
)

RQ_SRS_042_OAuth_StaticKey_Parameters_PrivateKeyPassword = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `private_key_password` parameter to specify the password for the private key. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <public_key>-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
        "-----END PUBLIC KEY-----</public_key>\n"
        "            <private_key>-----BEGIN ENCRYPTED PRIVATE KEY-----\n"
        "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n"
        "-----END ENCRYPTED PRIVATE KEY-----</private_key>\n"
        "            <private_key_password>my_private_key_password</private_key_password>\n"
        "        </my_rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.6",
)

RQ_SRS_042_OAuth_StaticKey_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.StaticKey.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate static key configuration as follows:\n"
        "\n"
        "* For `HS*` family algorithms: `static_key` SHALL be mandatory\n"
        "* For asymmetric algorithms (RS*, ES*, PS*, Ed*): `public_key` SHALL be mandatory\n"
        "* `algo` parameter SHALL be mandatory and SHALL contain a supported algorithm value\n"
        "* If `static_key_in_base64` is `True`, [ClickHouse] SHALL decode the `static_key` from base64 before use\n"
        "\n"
        "**Valid Configuration Examples:**\n"
        "\n"
        "**HS256 with static key:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <hs256_validator>\n"
        "            <algo>HS256</algo>\n"
        "            <static_key>my_secret_key</static_key>\n"
        "        </hs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**RS256 with public key:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <public_key>-----BEGIN PUBLIC KEY-----\n"
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n"
        "-----END PUBLIC KEY-----</public_key>\n"
        "        </rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Invalid Configuration Examples:**\n"
        "\n"
        "**Missing static_key for HS256:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_hs256_validator>\n"
        "            <algo>HS256</algo>\n"
        "            <!-- Missing static_key - will be rejected -->\n"
        "        </invalid_hs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Missing public_key for RS256:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_rs256_validator>\n"
        "            <algo>RS256</algo>\n"
        "            <!-- Missing public_key - will be rejected -->\n"
        "        </invalid_rs256_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.5.1",
)

RQ_SRS_042_OAuth_StaticJWKS_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support validating JWTs using a static JSON Web Key Set (JWKS). The configuration can be provided directly or from a file.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        '          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.1.1",
)

RQ_SRS_042_OAuth_StaticJWKS_UserDirectory = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.UserDirectory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static JWKS as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        '          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>my_static_jwks_validator</processor>\n"
        "            <common_roles>\n"
        "                <my_role />\n"
        "            </common_roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.2.1",
)

RQ_SRS_042_OAuth_StaticJWKS_Parameters_StaticJwks = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `static_jwks` parameter to specify the JWKS content directly in JSON format. This parameter SHALL contain a valid JSON Web Key Set structure.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        "            <static_jwks>{\n"
        '                "keys": [\n'
        "                    {\n"
        '                        "kty": "RSA",\n'
        '                        "alg": "RS256",\n'
        '                        "kid": "my-key-id-1",\n'
        '                        "use": "sig",\n'
        '                        "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",\n'
        '                        "e": "AQAB"\n'
        "                    }\n"
        "                ]\n"
        "            }</static_jwks>\n"
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.1",
)

RQ_SRS_042_OAuth_StaticJWKS_Parameters_StaticJwksFile = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `static_jwks_file` parameter to specify the path to a file containing the JWKS content. The file SHALL contain valid JSON Web Key Set data.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        "            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>\n"
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**File content example (`/etc/clickhouse-server/jwks.json`):**\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS256",\n'
        '            "kid": "my-key-id-1",\n'
        '            "use": "sig",\n'
        '            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",\n'
        '            "e": "AQAB"\n'
        "        },\n"
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS384",\n'
        '            "kid": "my-key-id-2",\n'
        '            "use": "sig",\n'
        '            "n": "another-modulus-value",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.2",
)

RQ_SRS_042_OAuth_StaticJWKS_Parameters_Claims = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        '            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        '            <claims>{"iss": "https://my-auth-server.com", "aud": "clickhouse-app"}</claims>\n'
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, tokens must contain both `iss` (issuer) and `aud` (audience) claims with the specified values to be considered valid.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.3",
)

RQ_SRS_042_OAuth_StaticJWKS_Parameters_VerifierLeeway = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_static_jwks_validator>\n"
        '            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "            <verifier_leeway>30</verifier_leeway>\n"
        "        </my_static_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, a 30-second clock skew tolerance is allowed, meaning tokens can be up to 30 seconds expired or not yet valid due to clock differences.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.4",
)

RQ_SRS_042_OAuth_StaticJWKS_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate static JWKS configuration as follows:\n"
        "\n"
        "* Only one of `static_jwks` or `static_jwks_file` SHALL be present in one verifier\n"
        "* If both or neither are specified, [ClickHouse] SHALL reject the configuration as invalid\n"
        "* Only RS* family algorithms SHALL be supported for static JWKS validation\n"
        "* The JWKS content SHALL be valid JSON format\n"
        "* If `static_jwks_file` is specified, the file SHALL exist and be readable\n"
        "\n"
        "**Valid Configuration Examples:**\n"
        "\n"
        "**Using static_jwks:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <valid_jwks_validator>\n"
        '            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "        </valid_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Using static_jwks_file:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <valid_jwks_file_validator>\n"
        "            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>\n"
        "        </valid_jwks_file_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Invalid Configuration Examples:**\n"
        "\n"
        "**Both static_jwks and static_jwks_file specified:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_jwks_validator>\n"
        '            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>\n"
        "            <!-- Both specified - will be rejected -->\n"
        "        </invalid_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Neither static_jwks nor static_jwks_file specified:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_jwks_validator>\n"
        "            <!-- Neither specified - will be rejected -->\n"
        "        </invalid_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Unsupported algorithm in JWKS:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_jwks_validator>\n"
        '            <static_jwks>{"keys": [{"kty": "RSA", "alg": "HS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "            <!-- HS256 not supported for JWKS - will be rejected -->\n"
        "        </invalid_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.4.1",
)

RQ_SRS_042_OAuth_StaticJWKS_Algorithms = Requirement(
    name="RQ.SRS-042.OAuth.StaticJWKS.Algorithms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support only RS* family algorithms for static JWKS validation:\n"
        "\n"
        "* RS256\n"
        "* RS384  \n"
        "* RS512\n"
        "\n"
        "[ClickHouse] SHALL reject JWKS entries with unsupported algorithms.\n"
        "\n"
        "**Supported Algorithm Examples:**\n"
        "\n"
        "**RS256:**\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS256",\n'
        '            "kid": "rs256-key",\n'
        '            "use": "sig",\n'
        '            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
        "\n"
        "**RS384:**\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS384",\n'
        '            "kid": "rs384-key",\n'
        '            "use": "sig",\n'
        '            "n": "another-modulus-value",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
        "\n"
        "**RS512:**\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS512",\n'
        '            "kid": "rs512-key",\n'
        '            "use": "sig",\n'
        '            "n": "third-modulus-value",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
        "\n"
        "**Unsupported Algorithm Example (will be rejected):**\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "HS256",\n'
        '            "kid": "hs256-key",\n'
        '            "use": "sig",\n'
        '            "n": "modulus-value",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "}\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.5.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support validating JWTs using a remote JSON Web Key Set (JWKS) fetched from a URI.\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <basic_auth_server>\n"
        "          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>\n"
        "          <jwks_refresh_timeout>300000</jwks_refresh_timeout>\n"
        "        </basic_auth_server>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.1.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_Setup = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Setup",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support custom JWKS setup for services that need to issue their own JWT tokens without using a full Identity Provider.\n"
        "\n"
        "**Generate RSA Key Pair for JWT Signing:**\n"
        "\n"
        "```bash\n"
        "openssl genrsa -out jwt-private.pem 2048\n"
        "\n"
        "openssl rsa -in jwt-private.pem -pubout -out jwt-public.pem\n"
        "```\n"
        "\n"
        "**Create JSON Web Key Set (JWKS) from Public Key:**\n"
        "\n"
        "A JWKS is a JSON document that includes your public key parameters. For RSA it looks like:\n"
        "\n"
        "```json\n"
        "{\n"
        '  "keys": [\n'
        "    {\n"
        '      "kty": "RSA",\n'
        '      "kid": "my-key-id-1",\n'
        '      "use": "sig",\n'
        '      "alg": "RS256",\n'
        '      "n": "<base64url-modulus>",\n'
        '      "e": "AQAB"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n"
        "\n"
        "**Deploy JWKS to HTTPS Web Server:**\n"
        "\n"
        "Drop `jwks.json` behind any HTTPS-capable web server (nginx, Caddy, even a tiny Flask/FastAPI app). Example path:\n"
        "\n"
        "```\n"
        "https://auth.example.com/.well-known/jwks.json\n"
        "```\n"
        "\n"
        "**Configure ClickHouse Token Processor:**\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "  <token_processors>\n"
        "    <my_service>\n"
        "      <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "      <jwks_refresh_timeout>300000</jwks_refresh_timeout>\n"
        "      <!-- Optional: claims / verifier_leeway -->\n"
        "    </my_service>\n"
        "  </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Sign JWT Tokens with Private Key:**\n"
        "\n"
        "Your token issuer must:\n"
        "\n"
        "* Sign with the matching private key (e.g., RS256)\n"
        "* Include the same `kid` in the JWT header as in your JWKS entry\n"
        "* (Optional) Include any claims you plan to enforce via ClickHouse's claims check\n"
        "\n"
        "**Important Notes:**\n"
        "\n"
        "* `kid` must match the `kid` you'll put in the JWT header when you sign tokens\n"
        "* `n` and `e` are the RSA public key params, base64url-encoded\n"
        "* You can generate that JSON with a tiny script using cryptography/pyjwt, or any JWK tool\n"
        "* The specifics aren't ClickHouse-specific; ClickHouse only needs the public JWKS\n"
        "* `jwks_uri`, `jwks_refresh_timeout`, `claims`, and `verifier_leeway` are exactly the supported params\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.2.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_Parameters_JwksUri = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `jwks_uri` parameter to specify the JWKS endpoint URI. This parameter SHALL be mandatory and SHALL point to a valid JWKS endpoint.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_remote_jwks_validator>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "            <jwks_refresh_timeout>300000</jwks_refresh_timeout>\n"
        "        </my_remote_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Common JWKS endpoint patterns:**\n"
        "* `https://auth.example.com/.well-known/jwks.json`\n"
        "* `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys`\n"
        "* `https://keycloak.example.com/realms/{realm}/protocol/openid-connect/certs`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.3.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_Parameters_JwksRefreshTimeout = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `jwks_refresh_timeout` parameter to specify the period for resending requests to refresh the JWKS. This parameter SHALL be optional with a default value of 300000 milliseconds.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_remote_jwks_validator>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "            <jwks_refresh_timeout>600000</jwks_refresh_timeout>\n"
        "        </my_remote_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, the JWKS will be refreshed every 10 minutes (600,000 milliseconds) instead of the default 5 minutes.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.3.2",
)

RQ_SRS_042_OAuth_RemoteJWKS_Parameters_Claims = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_remote_jwks_validator>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        '            <claims>{"iss": "https://auth.example.com", "aud": "clickhouse-app", "azp": "clickhouse-client"}</claims>\n'
        "        </my_remote_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, tokens must contain the specified `iss` (issuer), `aud` (audience), and `azp` (authorized party) claims to be considered valid.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.3.3",
)

RQ_SRS_042_OAuth_RemoteJWKS_Parameters_VerifierLeeway = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_remote_jwks_validator>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "            <verifier_leeway>60</verifier_leeway>\n"
        "        </my_remote_jwks_validator>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, a 60-second clock skew tolerance is allowed, providing more flexibility for environments with larger clock synchronization issues.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.3.4",
)

RQ_SRS_042_OAuth_RemoteJWKS_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate remote JWKS configuration as follows:\n"
        "\n"
        "* `jwks_uri` parameter SHALL be mandatory and SHALL contain a valid URI\n"
        "* The URI SHALL be accessible and return valid JWKS content\n"
        "* If `jwks_refresh_timeout` is specified, it SHALL be a positive integer value\n"
        "* [ClickHouse] SHALL validate the JWKS content format when fetched from the URI\n"
        "\n"
        "**Valid Configuration Examples:**\n"
        "\n"
        "**Basic configuration:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <valid_remote_jwks>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "        </valid_remote_jwks>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**With all optional parameters:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <complete_remote_jwks>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "            <jwks_refresh_timeout>600000</jwks_refresh_timeout>\n"
        '            <claims>{"iss": "https://auth.example.com"}</claims>\n'
        "            <verifier_leeway>30</verifier_leeway>\n"
        "        </complete_remote_jwks>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Invalid Configuration Examples:**\n"
        "\n"
        "**Missing jwks_uri:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_remote_jwks>\n"
        "            <!-- Missing jwks_uri - will be rejected -->\n"
        "            <jwks_refresh_timeout>300000</jwks_refresh_timeout>\n"
        "        </invalid_remote_jwks>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Invalid jwks_uri:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_remote_jwks>\n"
        "            <jwks_uri>not-a-valid-uri</jwks_uri>\n"
        "            <!-- Invalid URI format - will be rejected -->\n"
        "        </invalid_remote_jwks>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Negative refresh timeout:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_remote_jwks>\n"
        "            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>\n"
        "            <jwks_refresh_timeout>-1000</jwks_refresh_timeout>\n"
        "            <!-- Negative value - will be rejected -->\n"
        "        </invalid_remote_jwks>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.4.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_Network_Timeout = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL implement appropriate network timeouts when fetching JWKS from remote endpoints to prevent hanging requests.\n"
        "\n"
        "**Example timeout scenarios:**\n"
        "* Connection timeout: 10 seconds\n"
        "* Read timeout: 30 seconds\n"
        "* Total request timeout: 60 seconds\n"
        "\n"
        "**Behavior:**\n"
        "* If a JWKS fetch exceeds the timeout, [ClickHouse] SHALL log an error and continue using cached JWKS if available\n"
        "* If no cached JWKS is available, authentication SHALL be rejected until the endpoint becomes accessible\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.5.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_Network_Retry = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL implement retry logic for failed JWKS fetch attempts with exponential backoff to handle temporary network issues.\n"
        "\n"
        "**Retry behavior:**\n"
        "* Initial retry delay: 1 second\n"
        "* Maximum retry delay: 60 seconds\n"
        "* Maximum retry attempts: 3\n"
        "* Exponential backoff: delay = min(initial_delay * 2^attempt, max_delay)\n"
        "\n"
        "**Example retry sequence:**\n"
        "1. First attempt fails → wait 1 second\n"
        "2. Second attempt fails → wait 2 seconds  \n"
        "3. Third attempt fails → wait 4 seconds\n"
        "4. If all attempts fail, use cached JWKS or reject authentication\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.5.2",
)

RQ_SRS_042_OAuth_RemoteJWKS_Network_Cache = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL cache the fetched JWKS content for the duration specified by `jwks_refresh_timeout` to reduce network requests and improve performance.\n"
        "\n"
        "**Caching behavior:**\n"
        "* JWKS content SHALL be cached for the duration of `jwks_refresh_timeout`\n"
        "* Cache SHALL be shared across all token validation requests\n"
        "* Cache SHALL be refreshed in the background when the timeout expires\n"
        "* If refresh fails, the old cached content SHALL continue to be used\n"
        "\n"
        "**Example caching timeline:**\n"
        "```\n"
        "Time 0: Fetch JWKS from https://auth.example.com/.well-known/jwks.json\n"
        "Time 0-300s: Use cached JWKS for all token validations\n"
        "Time 300s: Background refresh attempt\n"
        "Time 300s+: Use updated JWKS if refresh succeeded, or continue with old cache if failed\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.5.3",
)

RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_NetworkFailure = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL handle network failures when fetching JWKS gracefully. If the JWKS endpoint is unreachable, [ClickHouse] SHALL use cached JWKS if available, or reject authentication if no cached JWKS exists.\n"
        "\n"
        "**Network failure scenarios:**\n"
        "* DNS resolution failure\n"
        "* Connection timeout\n"
        "* HTTP 5xx server errors\n"
        "* Network connectivity issues\n"
        "\n"
        "**Example behavior:**\n"
        "```\n"
        "Scenario: JWKS endpoint https://auth.example.com/.well-known/jwks.json is down\n"
        "\n"
        "1. First token validation: Use cached JWKS (if available)\n"
        "2. Subsequent validations: Continue using cached JWKS\n"
        "3. Background refresh attempts: Fail silently, keep using cache\n"
        "4. If no cache exists: Reject all authentication attempts\n"
        "5. When endpoint recovers: Resume normal operation\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.6.1",
)

RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_InvalidResponse = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject authentication attempts if the remote JWKS endpoint returns invalid or malformed JSON content.\n"
        "\n"
        "**Invalid response scenarios:**\n"
        "* Non-JSON content (HTML error pages, plain text)\n"
        "* Malformed JSON syntax\n"
        "* Missing required JWKS fields (`keys` array)\n"
        "* Invalid key format within JWKS\n"
        "\n"
        "**Example invalid responses:**\n"
        "\n"
        "**HTML error page:**\n"
        "```html\n"
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head><title>500 Internal Server Error</title></head>\n"
        "<body>Internal Server Error</body>\n"
        "</html>\n"
        "```\n"
        "\n"
        "**Malformed JSON:**\n"
        "\n"
        "```json\n"
        "{\n"
        '    "keys": [\n'
        "        {\n"
        '            "kty": "RSA",\n'
        '            "alg": "RS256",\n'
        '            "kid": "my-key",\n'
        '            "n": "modulus",\n'
        '            "e": "AQAB"\n'
        "        }\n"
        "    ]\n"
        "```\n"
        "\n"
        "Closing brace is missing, making it invalid JSON.\n"
        "\n"
        "**Missing keys array:**\n"
        "```json\n"
        "{\n"
        '    "error": "not_found",\n'
        '    "error_description": "JWKS not available"\n'
        "}\n"
        "```\n"
        "\n"
        "**Behavior:**\n"
        "* [ClickHouse] SHALL log the invalid response for debugging\n"
        "* Authentication SHALL be rejected for all tokens\n"
        "* Cached JWKS SHALL not be used if the current response is invalid\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.6.2",
)

RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_ExpiredCache = Requirement(
    name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL attempt to refresh the JWKS cache when it expires. If the refresh fails, [ClickHouse] SHALL continue using the expired cache for a limited time before rejecting authentication.\n"
        "\n"
        "**Cache expiration behavior:**\n"
        "* When cache expires, [ClickHouse] SHALL attempt to fetch fresh JWKS\n"
        "* If fetch succeeds: Use new JWKS immediately\n"
        "* If fetch fails: Continue using expired cache for up to 24 hours\n"
        "* After 24 hours of failed refreshes: Reject all authentication attempts\n"
        "\n"
        "**Example timeline:**\n"
        "```\n"
        "Time 0: JWKS cached successfully\n"
        "Time 300s: Cache expires, refresh attempt fails\n"
        "Time 300s-86400s: Use expired cache, continue refresh attempts\n"
        "Time 86400s+: Reject authentication if refresh still fails\n"
        "```\n"
        "\n"
        "**Graceful degradation:**\n"
        "* This allows for temporary network issues without immediate service disruption\n"
        "* Provides time for administrators to resolve connectivity problems\n"
        "* Prevents indefinite use of potentially outdated keys\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.6.3",
)

RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime = Requirement(
    name="RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `cache_lifetime` parameter for all token processor types. This parameter SHALL specify the maximum lifetime of cached tokens in seconds. This parameter SHALL be optional with a default value of 3600 seconds.\n"
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_token_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>my-client-id</client_id>\n"
        "            <tenant_id>my-tenant-id</tenant_id>\n"
        "            <cache_lifetime>1800</cache_lifetime>\n"
        "        </my_token_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, tokens will be cached for 30 minutes (1800 seconds) instead of the default 1 hour.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.1.1",
)

RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim = Requirement(
    name="RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `username_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that will be treated as the ClickHouse username. This parameter SHALL be optional with a default value of "sub".\n'
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_token_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>my-client-id</client_id>\n"
        "            <tenant_id>my-tenant-id</tenant_id>\n"
        "            <username_claim>preferred_username</username_claim>\n"
        "        </my_token_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, the `preferred_username` claim from the token will be used as the ClickHouse username instead of the default `sub` claim.\n"
        "\n"
        "**Common username claim values:**\n"
        "* `sub` (default) - Subject identifier\n"
        "* `preferred_username` - User's preferred username\n"
        "* `email` - User's email address\n"
        "* `upn` - User Principal Name (Azure AD)\n"
        "* `name` - User's display name\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.1.2",
)

RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim = Requirement(
    name="RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the `groups_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that contains the list of groups the user belongs to. This claim SHALL be looked up in the token itself (for valid JWTs) or in the response from `/userinfo` (for opaque tokens). This parameter SHALL be optional with a default value of "groups".\n'
        "\n"
        "**Example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_token_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>my-client-id</client_id>\n"
        "            <tenant_id>my-tenant-id</tenant_id>\n"
        "            <groups_claim>roles</groups_claim>\n"
        "        </my_token_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "In this example, the `roles` claim from the token will be used to determine user groups instead of the default `groups` claim.\n"
        "\n"
        "**Common groups claim values:**\n"
        "* `groups` (default) - Standard groups claim\n"
        "* `roles` - User roles\n"
        "* `app_roles` - Application-specific roles\n"
        "* `resource_access` - Resource access permissions\n"
        "* `wids` - Windows Identity Foundation claims (Azure AD)\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.1.3",
)

RQ_SRS_042_OAuth_Common_Parameters_Unfiltered = Requirement(
    name="RQ.SRS-042.OAuth.Common.Parameters.Unfiltered",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject a configuration inside `token_processors` that contains all possible parameters.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <madness>\n"
        "          <algo>HS256</algo>\n"
        "          <static_key>my_static_secret</static_key>\n"
        '          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>\n'
        "          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>\n"
        "          <jwks_refresh_timeout>300000</jwks_refresh_timeout>\n"
        "          <provider>openid</provider>\n"
        "          <cache_lifetime>600</cache_lifetime>\n"
        "          <username_claim>sub</username_claim>\n"
        "          <groups_claim>groups</groups_claim>\n"
        "          <configuration_endpoint></configuration_endpoint>\n"
        "          <userinfo_endpoint></userinfo_endpoint>\n"
        "          <token_introspection_endpoint></token_introspection_endpoint>\n"
        "        </madness>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.1.4",
)

RQ_SRS_042_OAuth_Common_Cache_Behavior = Requirement(
    name="RQ.SRS-042.OAuth.Common.Cache.Behavior",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL implement token caching behavior as follows:\n"
        "\n"
        "* Tokens SHALL be cached internally for no longer than `cache_lifetime` seconds\n"
        "* If a token expires sooner than `cache_lifetime`, the cache entry SHALL only be valid while the token is valid\n"
        "* If a token lifetime is longer than `cache_lifetime`, the cache entry SHALL be valid for `cache_lifetime`\n"
        "* Caching SHALL reduce the number of requests to Identity Providers\n"
        "\n"
        "**Example caching scenarios:**\n"
        "\n"
        "**Scenario 1: Token expires before cache_lifetime**\n"
        "```\n"
        "Token expiration: 30 minutes\n"
        "Cache lifetime: 60 minutes\n"
        "Result: Token cached for 30 minutes (until token expires)\n"
        "```\n"
        "\n"
        "**Scenario 2: Token expires after cache_lifetime**\n"
        "```\n"
        "Token expiration: 120 minutes\n"
        "Cache lifetime: 60 minutes\n"
        "Result: Token cached for 60 minutes (cache_lifetime limit)\n"
        "```\n"
        "\n"
        "**Scenario 3: Cache disabled**\n"
        "```\n"
        "Cache lifetime: 0\n"
        "Result: No caching, validate token on every request\n"
        "```\n"
        "\n"
        "**Configuration example:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>my-client-id</client_id>\n"
        "            <tenant_id>my-tenant-id</tenant_id>\n"
        "            <cache_lifetime>1800</cache_lifetime>\n"
        "        </my_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Cache behavior timeline:**\n"
        "```\n"
        "Time 0: Token received and validated\n"
        "Time 0-1800s: Token cached, no validation requests to IdP\n"
        "Time 1800s: Cache expires, next request triggers validation\n"
        "Time 1800s+: New token cached for next 1800 seconds\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.2.1",
)

RQ_SRS_042_OAuth_Common_Configuration_Validation = Requirement(
    name="RQ.SRS-042.OAuth.Common.Configuration.Validation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate token processor configurations as follows:\n"
        "\n"
        "* At least one token processor SHALL be defined in the `token_processors` section\n"
        "* Each token processor SHALL have a unique identifier\n"
        "* Required parameters for each processor type SHALL be present and valid\n"
        "* [ClickHouse] SHALL reject invalid configurations and log appropriate error messages\n"
        "\n"
        "**Valid Configuration Examples:**\n"
        "\n"
        "**Multiple token processors:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <azure_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>azure-client-id</client_id>\n"
        "            <tenant_id>azure-tenant-id</tenant_id>\n"
        "        </azure_processor>\n"
        "        <keycloak_processor>\n"
        "            <provider>openid</provider>\n"
        "            <userinfo_endpoint>https://keycloak.example.com/userinfo</userinfo_endpoint>\n"
        "            <token_introspection_endpoint>https://keycloak.example.com/introspect</token_introspection_endpoint>\n"
        "        </keycloak_processor>\n"
        "        <static_key_processor>\n"
        "            <algo>HS256</algo>\n"
        "            <static_key>my-secret-key</static_key>\n"
        "        </static_key_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Invalid Configuration Examples:**\n"
        "\n"
        "**No token processors defined:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <!-- Empty section - will be rejected -->\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Duplicate processor identifiers:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <my_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>client1</client_id>\n"
        "            <tenant_id>tenant1</tenant_id>\n"
        "        </my_processor>\n"
        "        <my_processor>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>client2</client_id>\n"
        "            <tenant_id>tenant2</tenant_id>\n"
        "            <!-- Duplicate identifier - will be rejected -->\n"
        "        </my_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Missing required parameters:**\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <token_processors>\n"
        "        <invalid_azure_processor>\n"
        "            <provider>azure</provider>\n"
        "            <!-- Missing client_id and tenant_id - will be rejected -->\n"
        "        </invalid_azure_processor>\n"
        "    </token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
        "**Error handling:**\n"
        "* [ClickHouse] SHALL log detailed error messages for configuration validation failures\n"
        "* [ClickHouse] SHALL refuse to start if any token processor configuration is invalid\n"
        "* Error messages SHALL include the specific parameter and reason for validation failure\n"
        "\n"
    ),
    link=None,
    level=3,
    num="12.3.1",
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
    level=3,
    num="13.1.1",
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
    level=3,
    num="13.1.2",
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
    level=3,
    num="13.1.3",
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
    level=3,
    num="13.1.4",
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
    level=3,
    num="13.1.5",
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
    level=3,
    num="13.1.6",
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
    level=3,
    num="13.1.7",
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
    level=3,
    num="13.1.8",
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
    level=3,
    num="13.1.9",
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
    level=3,
    num="13.2.1",
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
    level=3,
    num="13.2.2",
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
    level=3,
    num="13.2.3",
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
    level=3,
    num="13.2.4",
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
    level=3,
    num="13.3.1",
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
    level=4,
    num="13.3.2.1",
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
    level=4,
    num="13.3.3.1",
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
    level=4,
    num="13.3.4.1",
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
    level=4,
    num="13.3.5.1",
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
    level=3,
    num="13.4.1",
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
    level=3,
    num="13.4.2",
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
        "[ClickHouse]: https://clickhouse.com\n"
        "[Grafana]: https://grafana.com\n"
        "[Keycloak]: https://www.keycloak.org\n"
        "[Azure]: https://azure.microsoft.com\n"
    ),
    link=None,
    level=3,
    num="13.5.1",
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
        Heading(name="Forward OAuth Identity", level=2, num="4.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity",
            level=3,
            num="4.1.1",
        ),
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
        Heading(name="Setting Up OAuth Authentication", level=1, num="6"),
        Heading(name="Credentials", level=2, num="6.1"),
        Heading(name="RQ.SRS-042.OAuth.Credentials", level=3, num="6.1.1"),
        Heading(name="Azure", level=1, num="7"),
        Heading(name="Setting up an Application in Azure", level=2, num="7.1"),
        Heading(name="RQ.SRS-042.OAuth.Azure.ApplicationSetup ", level=3, num="7.1.1"),
        Heading(name="Opaque Token Support for Azure", level=2, num="7.2"),
        Heading(name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque", level=3, num="7.2.1"),
        Heading(
            name="Opaque Token Constraints and Gateway Workaround For Azure",
            level=3,
            num="7.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Constraints",
            level=4,
            num="7.2.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational",
            level=4,
            num="7.2.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Configuration.Validation",
            level=4,
            num="7.2.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ProviderType",
            level=3,
            num="7.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ReferenceToken",
            level=3,
            num="7.2.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.Failure",
            level=4,
            num="7.2.4.1",
        ),
        Heading(name="Getting Access Token from Azure", level=2, num="7.3"),
        Heading(name="RQ.SRS-042.OAuth.Azure.GetAccessToken", level=3, num="7.3.1"),
        Heading(name="Access Token Processors For Azure", level=2, num="7.4"),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors",
            level=3,
            num="7.4.1",
        ),
        Heading(name="User Groups in Azure", level=2, num="7.5"),
        Heading(name="Setting up User Groups in Azure", level=3, num="7.5.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserDirectories.UserGroups",
            level=4,
            num="7.5.1.1",
        ),
        Heading(
            name="Query Execution Based on User Roles in ClickHouse with Azure",
            level=3,
            num="7.5.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles",
            level=4,
            num="7.5.2.1",
        ),
        Heading(
            name="Filtering Azure Groups for Role Assignment", level=3, num="7.5.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.GroupFiltering",
            level=4,
            num="7.5.3.1",
        ),
        Heading(name="User in Multiple Azure Groups", level=3, num="7.5.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.MultipleGroups",
            level=4,
            num="7.5.4.1",
        ),
        Heading(
            name="No Duplicate Role Assignments for Overlapping Azure Groups",
            level=3,
            num="7.5.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.OverlappingUsers",
            level=4,
            num="7.5.5.1",
        ),
        Heading(name="No Azure Groups Returned for User", level=3, num="7.5.6"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoGroups",
            level=4,
            num="7.5.6.1",
        ),
        Heading(name="Azure Subgroup Memberships Not Considered", level=3, num="7.5.7"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SubgroupMemberships",
            level=4,
            num="7.5.7.1",
        ),
        Heading(
            name="Dynamic Group Membership Updates For Azure Users",
            level=3,
            num="7.5.8",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingClickHouseRoles",
            level=4,
            num="7.5.8.1",
        ),
        Heading(
            name="Azure Group Names Match Roles in ClickHouse", level=3, num="7.5.9"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SameName",
            level=4,
            num="7.5.9.1",
        ),
        Heading(
            name="No Matching Roles in ClickHouse for Azure Groups",
            level=3,
            num="7.5.10",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingRoles",
            level=4,
            num="7.5.10.1",
        ),
        Heading(name="User Cannot View Groups in Azure", level=3, num="7.5.11"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoPermissionToViewGroups",
            level=4,
            num="7.5.11.1",
        ),
        Heading(
            name="In ClickHouse There Is No Default Role Specified for Azure Users",
            level=3,
            num="7.5.12",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoDefaultRole",
            level=4,
            num="7.5.12.1",
        ),
        Heading(name="Azure Identity Management Actions", level=2, num="7.6"),
        Heading(name="Azure User State Changes", level=3, num="7.6.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserDisabled", level=4, num="7.6.1.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserDeleted", level=4, num="7.6.1.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated",
            level=4,
            num="7.6.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset",
            level=4,
            num="7.6.1.4",
        ),
        Heading(name="Azure Group and Role Membership", level=3, num="7.6.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup",
            level=4,
            num="7.6.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup",
            level=4,
            num="7.6.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted", level=4, num="7.6.2.3"
        ),
        Heading(name="Azure Application and Consent", level=3, num="7.6.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled",
            level=4,
            num="7.6.3.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved",
            level=4,
            num="7.6.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated",
            level=4,
            num="7.6.3.3",
        ),
        Heading(name="Azure Token and Session Management", level=3, num="7.6.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked",
            level=4,
            num="7.6.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired",
            level=4,
            num="7.6.4.2",
        ),
        Heading(
            name="Access Token Processors are Missing From ClickHouse Configuration",
            level=3,
            num="7.6.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors",
            level=4,
            num="7.6.5.1",
        ),
        Heading(name="Azure as an External User Directory", level=2, num="7.7"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories",
            level=3,
            num="7.7.1",
        ),
        Heading(
            name="Incorrect Configuration in User Directories", level=4, num="7.7.1.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider",
            level=5,
            num="7.7.1.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId",
            level=5,
            num="7.7.1.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId",
            level=5,
            num="7.7.1.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor",
            level=5,
            num="7.7.1.1.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles",
            level=5,
            num="7.7.1.1.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries",
            level=5,
            num="7.7.1.1.6",
        ),
        Heading(
            name="Missing Configuration in User Directories", level=4, num="7.7.1.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors",
            level=5,
            num="7.7.1.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider",
            level=5,
            num="7.7.1.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId",
            level=5,
            num="7.7.1.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId",
            level=5,
            num="7.7.1.2.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories",
            level=5,
            num="7.7.1.2.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token",
            level=5,
            num="7.7.1.2.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor",
            level=5,
            num="7.7.1.2.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles",
            level=5,
            num="7.7.1.2.8",
        ),
        Heading(name="Keycloak", level=1, num="8"),
        Heading(name="Setting up a Realm in Keycloak", level=2, num="8.1"),
        Heading(name="RQ.SRS-042.OAuth.Keycloak.RealmSetup", level=3, num="8.1.1"),
        Heading(name="Opaque Token Support for Keycloak", level=2, num="8.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.OpaqueTokenSupport", level=3, num="8.2.1"
        ),
        Heading(
            name="Opaque Token Constraints and Gateway Workaround For Keycloak",
            level=3,
            num="8.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Constraints", level=4, num="8.2.2.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational",
            level=4,
            num="8.2.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Configuration.Validation",
            level=4,
            num="8.2.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ProviderType",
            level=4,
            num="8.2.2.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ReferenceToken",
            level=4,
            num="8.2.2.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.Failure",
            level=4,
            num="8.2.2.6",
        ),
        Heading(name="Getting Access Token from Keycloak", level=2, num="8.3"),
        Heading(name="RQ.SRS-042.OAuth.Keycloak.GetAccessToken", level=3, num="8.3.1"),
        Heading(name="Access Token Processors For Keycloak", level=2, num="8.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors", level=3, num="8.4.1"
        ),
        Heading(name="User Groups in Keycloak", level=2, num="8.5"),
        Heading(name="Setting up User Groups in Keycloak", level=3, num="8.5.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserDirectories.UserGroups",
            level=4,
            num="8.5.1.1",
        ),
        Heading(
            name="Query Execution Based on User Roles in ClickHouse with Keycloak",
            level=3,
            num="8.5.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles",
            level=4,
            num="8.5.2.1",
        ),
        Heading(
            name="Filtering Keycloak Groups for Role Assignment", level=3, num="8.5.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.GroupFiltering",
            level=4,
            num="8.5.3.1",
        ),
        Heading(name="User in Multiple Keycloak Groups", level=3, num="8.5.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.MultipleGroups",
            level=4,
            num="8.5.4.1",
        ),
        Heading(
            name="No Duplicate Role Assignments for Overlapping Keycloak Groups",
            level=3,
            num="8.5.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.OverlappingUsers",
            level=4,
            num="8.5.5.1",
        ),
        Heading(name="No Keycloak Groups Returned for User", level=3, num="8.5.6"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoGroups",
            level=4,
            num="8.5.6.1",
        ),
        Heading(
            name="Keycloak Subgroup Memberships Not Considered", level=3, num="8.5.7"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SubgroupMemberships",
            level=4,
            num="8.5.7.1",
        ),
        Heading(
            name="Dynamic Group Membership Updates For Keycloak", level=3, num="8.5.8"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles",
            level=4,
            num="8.5.8.1",
        ),
        Heading(
            name="Keycloak Group Names Match Roles in ClickHouse", level=3, num="8.5.9"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SameName",
            level=4,
            num="8.5.9.1",
        ),
        Heading(
            name="No Matching Roles in ClickHouse for Keycloak Groups",
            level=3,
            num="8.5.10",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingRoles",
            level=4,
            num="8.5.10.1",
        ),
        Heading(name="User Cannot View Groups in Keycloak", level=3, num="8.5.11"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups",
            level=4,
            num="8.5.11.1",
        ),
        Heading(
            name="In ClickHouse There Is No Default Role Specified for Keycloak Users",
            level=3,
            num="8.5.12",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoDefaultRole",
            level=4,
            num="8.5.12.1",
        ),
        Heading(name="Keycloak Identity Management Actions", level=2, num="8.6"),
        Heading(name="Keycloak User State Changes", level=3, num="8.6.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled",
            level=4,
            num="8.6.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted", level=4, num="8.6.1.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserAttributesUpdated",
            level=4,
            num="8.6.1.3",
        ),
        Heading(name="Keycloak Group and Role Membership", level=3, num="8.6.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup",
            level=4,
            num="8.6.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup",
            level=4,
            num="8.6.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted",
            level=4,
            num="8.6.2.3",
        ),
        Heading(name="Keycloak Application and Consent", level=3, num="8.6.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled",
            level=4,
            num="8.6.3.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked",
            level=4,
            num="8.6.3.2",
        ),
        Heading(name="Keycloak Token and Session Management", level=3, num="8.6.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.UserSessionRevoked",
            level=4,
            num="8.6.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.RefreshTokenRevoked",
            level=4,
            num="8.6.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Keycloak.Actions.NotBeforePolicyUpdated",
            level=4,
            num="8.6.4.3",
        ),
        Heading(name="Static Key", level=1, num="9"),
        Heading(name="Access Token Processors For Static Key", level=2, num="9.1"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors",
            level=3,
            num="9.1.1",
        ),
        Heading(name="Static Key as an External User Directory", level=2, num="9.2"),
        Heading(name="RQ.SRS-042.OAuth.StaticKey.UserDirectory", level=3, num="9.2.1"),
        Heading(name="Static Key Algorithm Support", level=2, num="9.3"),
        Heading(name="RQ.SRS-042.OAuth.StaticKey.Algorithms", level=3, num="9.3.1"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Algorithm.None", level=4, num="9.3.1.1"
        ),
        Heading(name="Static Key Configuration Parameters", level=2, num="9.4"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey", level=3, num="9.4.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64",
            level=3,
            num="9.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey", level=3, num="9.4.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey",
            level=3,
            num="9.4.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword",
            level=3,
            num="9.4.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword",
            level=3,
            num="9.4.6",
        ),
        Heading(name="Static Key Configuration Validation", level=2, num="9.5"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticKey.Configuration.Validation",
            level=3,
            num="9.5.1",
        ),
        Heading(name="Static JWKS", level=1, num="10"),
        Heading(name="Access Token Processors For Static JWKS", level=2, num="10.1"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors",
            level=3,
            num="10.1.1",
        ),
        Heading(name="Static JWKS as an External User Directory", level=2, num="10.2"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.UserDirectory", level=3, num="10.2.1"
        ),
        Heading(name="Static JWKS Configuration Parameters", level=2, num="10.3"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks",
            level=3,
            num="10.3.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile",
            level=3,
            num="10.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims", level=3, num="10.3.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway",
            level=3,
            num="10.3.4",
        ),
        Heading(name="Static JWKS Configuration Validation", level=2, num="10.4"),
        Heading(
            name="RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation",
            level=3,
            num="10.4.1",
        ),
        Heading(name="Static JWKS Algorithm Support", level=2, num="10.5"),
        Heading(name="RQ.SRS-042.OAuth.StaticJWKS.Algorithms", level=3, num="10.5.1"),
        Heading(name="Remote JWKS", level=1, num="11"),
        Heading(name="Access Token Processors For Remote JWKS", level=2, num="11.1"),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors",
            level=3,
            num="11.1.1",
        ),
        Heading(name="Setting up Remote JWKS", level=2, num="11.2"),
        Heading(name="RQ.SRS-042.OAuth.RemoteJWKS.Setup", level=3, num="11.2.1"),
        Heading(name="Remote JWKS Configuration Parameters", level=2, num="11.3"),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri", level=3, num="11.3.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout",
            level=3,
            num="11.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims", level=3, num="11.3.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway",
            level=3,
            num="11.3.4",
        ),
        Heading(name="Remote JWKS Configuration Validation", level=2, num="11.4"),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation",
            level=3,
            num="11.4.1",
        ),
        Heading(name="Remote JWKS Network Handling", level=2, num="11.5"),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout", level=3, num="11.5.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry", level=3, num="11.5.2"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache", level=3, num="11.5.3"
        ),
        Heading(name="Remote JWKS Error Handling", level=2, num="11.6"),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure",
            level=3,
            num="11.6.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse",
            level=3,
            num="11.6.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache",
            level=3,
            num="11.6.3",
        ),
        Heading(name="Token Processor", level=1, num="12"),
        Heading(name="Common Configuration Parameters", level=2, num="12.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime",
            level=3,
            num="12.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim",
            level=3,
            num="12.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim", level=3, num="12.1.3"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Common.Parameters.Unfiltered", level=3, num="12.1.4"
        ),
        Heading(name="Token Cache Behavior", level=2, num="12.2"),
        Heading(name="RQ.SRS-042.OAuth.Common.Cache.Behavior", level=3, num="12.2.1"),
        Heading(name="Configuration Validation", level=2, num="12.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Common.Configuration.Validation",
            level=3,
            num="12.3.1",
        ),
        Heading(name="ClickHouse Actions After Token Validation", level=1, num="13"),
        Heading(name="Incorrect Requests to ClickHouse", level=2, num="13.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests",
            level=3,
            num="13.1.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header",
            level=3,
            num="13.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg",
            level=3,
            num="13.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ",
            level=3,
            num="13.1.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature",
            level=3,
            num="13.1.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body",
            level=3,
            num="13.1.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub",
            level=3,
            num="13.1.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud",
            level=3,
            num="13.1.8",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp",
            level=3,
            num="13.1.9",
        ),
        Heading(name="Token Handling", level=2, num="13.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired",
            level=3,
            num="13.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect",
            level=3,
            num="13.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric",
            level=3,
            num="13.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString",
            level=3,
            num="13.2.4",
        ),
        Heading(name="Caching", level=2, num="13.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching",
            level=3,
            num="13.3.1",
        ),
        Heading(name="Disable Caching", level=3, num="13.3.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache",
            level=4,
            num="13.3.2.1",
        ),
        Heading(name="Cache Lifetime", level=3, num="13.3.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime",
            level=4,
            num="13.3.3.1",
        ),
        Heading(name="Exceeding Max Cache Size", level=3, num="13.3.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize",
            level=4,
            num="13.3.4.1",
        ),
        Heading(name="Cache Eviction Policy", level=3, num="13.3.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy",
            level=4,
            num="13.3.5.1",
        ),
        Heading(name="Authentication and Login", level=2, num="13.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication",
            level=3,
            num="13.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client",
            level=3,
            num="13.4.2",
        ),
        Heading(name="Session Management", level=2, num="13.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement",
            level=3,
            num="13.5.1",
        ),
    ),
    requirements=(
        RQ_SRS_042_OAuth_Grafana_Authentication_ForwardOAuthIdentity,
        RQ_SRS_042_OAuth_IdentityProviders_Concurrent,
        RQ_SRS_042_OAuth_IdentityProviders_Change,
        RQ_SRS_042_OAuth_Credentials,
        RQ_SRS_042_OAuth_Azure_ApplicationSetup_,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Constraints,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Configuration_Validation,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_ProviderType,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_ReferenceToken,
        RQ_SRS_042_OAuth_Azure_Tokens_Opaque_Operational_Failure,
        RQ_SRS_042_OAuth_Azure_GetAccessToken,
        RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserDirectories_UserGroups,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_GroupFiltering,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_MultipleGroups,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_OverlappingUsers,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoGroups,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_SubgroupMemberships,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoMatchingClickHouseRoles,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_SameName,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoMatchingRoles,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoPermissionToViewGroups,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoles_NoDefaultRole,
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
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoAccessTokenProcessors,
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
        RQ_SRS_042_OAuth_Keycloak_RealmSetup,
        RQ_SRS_042_OAuth_Keycloak_OpaqueTokenSupport,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Constraints,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Configuration_Validation,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_ProviderType,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_ReferenceToken,
        RQ_SRS_042_OAuth_Keycloak_Tokens_Opaque_Operational_Failure,
        RQ_SRS_042_OAuth_Keycloak_GetAccessToken,
        RQ_SRS_042_OAuth_Keycloak_AccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserDirectories_UserGroups,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_GroupFiltering,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_MultipleGroups,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_OverlappingUsers,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoGroups,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_SubgroupMemberships,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoMatchingClickHouseRoles,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_SameName,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoMatchingRoles,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoPermissionToViewGroups,
        RQ_SRS_042_OAuth_Grafana_Keycloak_Authentication_UserRoles_NoDefaultRole,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserDisabled,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserDeleted,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserAttributesUpdated,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserAddedToGroup,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserRemovedFromGroup,
        RQ_SRS_042_OAuth_Keycloak_Actions_GroupDeleted,
        RQ_SRS_042_OAuth_Keycloak_Actions_ClientDisabled,
        RQ_SRS_042_OAuth_Keycloak_Actions_ConsentRevoked,
        RQ_SRS_042_OAuth_Keycloak_Actions_UserSessionRevoked,
        RQ_SRS_042_OAuth_Keycloak_Actions_RefreshTokenRevoked,
        RQ_SRS_042_OAuth_Keycloak_Actions_NotBeforePolicyUpdated,
        RQ_SRS_042_OAuth_StaticKey_AccessTokenProcessors,
        RQ_SRS_042_OAuth_StaticKey_UserDirectory,
        RQ_SRS_042_OAuth_StaticKey_Algorithms,
        RQ_SRS_042_OAuth_StaticKey_Algorithm_None,
        RQ_SRS_042_OAuth_StaticKey_Parameters_StaticKey,
        RQ_SRS_042_OAuth_StaticKey_Parameters_StaticKeyBase64,
        RQ_SRS_042_OAuth_StaticKey_Parameters_PublicKey,
        RQ_SRS_042_OAuth_StaticKey_Parameters_PrivateKey,
        RQ_SRS_042_OAuth_StaticKey_Parameters_PublicKeyPassword,
        RQ_SRS_042_OAuth_StaticKey_Parameters_PrivateKeyPassword,
        RQ_SRS_042_OAuth_StaticKey_Configuration_Validation,
        RQ_SRS_042_OAuth_StaticJWKS_AccessTokenProcessors,
        RQ_SRS_042_OAuth_StaticJWKS_UserDirectory,
        RQ_SRS_042_OAuth_StaticJWKS_Parameters_StaticJwks,
        RQ_SRS_042_OAuth_StaticJWKS_Parameters_StaticJwksFile,
        RQ_SRS_042_OAuth_StaticJWKS_Parameters_Claims,
        RQ_SRS_042_OAuth_StaticJWKS_Parameters_VerifierLeeway,
        RQ_SRS_042_OAuth_StaticJWKS_Configuration_Validation,
        RQ_SRS_042_OAuth_StaticJWKS_Algorithms,
        RQ_SRS_042_OAuth_RemoteJWKS_AccessTokenProcessors,
        RQ_SRS_042_OAuth_RemoteJWKS_Setup,
        RQ_SRS_042_OAuth_RemoteJWKS_Parameters_JwksUri,
        RQ_SRS_042_OAuth_RemoteJWKS_Parameters_JwksRefreshTimeout,
        RQ_SRS_042_OAuth_RemoteJWKS_Parameters_Claims,
        RQ_SRS_042_OAuth_RemoteJWKS_Parameters_VerifierLeeway,
        RQ_SRS_042_OAuth_RemoteJWKS_Configuration_Validation,
        RQ_SRS_042_OAuth_RemoteJWKS_Network_Timeout,
        RQ_SRS_042_OAuth_RemoteJWKS_Network_Retry,
        RQ_SRS_042_OAuth_RemoteJWKS_Network_Cache,
        RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_NetworkFailure,
        RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_InvalidResponse,
        RQ_SRS_042_OAuth_RemoteJWKS_ErrorHandling_ExpiredCache,
        RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime,
        RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim,
        RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim,
        RQ_SRS_042_OAuth_Common_Parameters_Unfiltered,
        RQ_SRS_042_OAuth_Common_Cache_Behavior,
        RQ_SRS_042_OAuth_Common_Configuration_Validation,
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
    * 4.1 [Forward OAuth Identity](#forward-oauth-identity)
        * 4.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaauthenticationforwardoauthidentity)
* 5 [Identity Providers](#identity-providers)
    * 5.1 [Number of Identity Providers That Can Be Used Concurrently](#number-of-identity-providers-that-can-be-used-concurrently)
        * 5.1.1 [RQ.SRS-042.OAuth.IdentityProviders.Concurrent](#rqsrs-042oauthidentityprovidersconcurrent)
    * 5.2 [Changing Identity Providers](#changing-identity-providers)
        * 5.2.1 [RQ.SRS-042.OAuth.IdentityProviders.Change](#rqsrs-042oauthidentityproviderschange)
* 6 [Setting Up OAuth Authentication](#setting-up-oauth-authentication)
    * 6.1 [Credentials](#credentials)
        * 6.1.1 [RQ.SRS-042.OAuth.Credentials](#rqsrs-042oauthcredentials)
* 7 [Azure](#azure)
    * 7.1 [Setting up an Application in Azure](#setting-up-an-application-in-azure)
        * 7.1.1 [RQ.SRS-042.OAuth.Azure.ApplicationSetup ](#rqsrs-042oauthazureapplicationsetup-)
    * 7.2 [Opaque Token Support for Azure](#opaque-token-support-for-azure)
        * 7.2.1 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque](#rqsrs-042oauthazuretokensopaque)
        * 7.2.2 [Opaque Token Constraints and Gateway Workaround For Azure](#opaque-token-constraints-and-gateway-workaround-for-azure)
            * 7.2.2.1 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Constraints](#rqsrs-042oauthazuretokensopaqueconstraints)
            * 7.2.2.2 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational](#rqsrs-042oauthazuretokensopaqueoperational)
            * 7.2.2.3 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Configuration.Validation](#rqsrs-042oauthazuretokensopaqueconfigurationvalidation)
        * 7.2.3 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ProviderType](#rqsrs-042oauthazuretokensopaqueoperationalprovidertype)
        * 7.2.4 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ReferenceToken](#rqsrs-042oauthazuretokensopaqueoperationalreferencetoken)
            * 7.2.4.1 [RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.Failure](#rqsrs-042oauthazuretokensopaqueoperationalfailure)
    * 7.3 [Getting Access Token from Azure](#getting-access-token-from-azure)
        * 7.3.1 [RQ.SRS-042.OAuth.Azure.GetAccessToken](#rqsrs-042oauthazuregetaccesstoken)
    * 7.4 [Access Token Processors For Azure](#access-token-processors-for-azure)
        * 7.4.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors](#rqsrs-042oauthidentityprovidersaccesstokenprocessors)
    * 7.5 [User Groups in Azure](#user-groups-in-azure)
        * 7.5.1 [Setting up User Groups in Azure](#setting-up-user-groups-in-azure)
            * 7.5.1.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserDirectories.UserGroups](#rqsrs-042oauthgrafanaazureauthenticationuserdirectoriesusergroups)
        * 7.5.2 [Query Execution Based on User Roles in ClickHouse with Azure](#query-execution-based-on-user-roles-in-clickhouse-with-azure)
            * 7.5.2.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles](#rqsrs-042oauthgrafanaazureauthenticationuserroles)
        * 7.5.3 [Filtering Azure Groups for Role Assignment](#filtering-azure-groups-for-role-assignment)
            * 7.5.3.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.GroupFiltering](#rqsrs-042oauthgrafanaazureauthenticationuserrolesgroupfiltering)
        * 7.5.4 [User in Multiple Azure Groups](#user-in-multiple-azure-groups)
            * 7.5.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.MultipleGroups](#rqsrs-042oauthgrafanaazureauthenticationuserrolesmultiplegroups)
        * 7.5.5 [No Duplicate Role Assignments for Overlapping Azure Groups](#no-duplicate-role-assignments-for-overlapping-azure-groups)
            * 7.5.5.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.OverlappingUsers](#rqsrs-042oauthgrafanaazureauthenticationuserrolesoverlappingusers)
        * 7.5.6 [No Azure Groups Returned for User](#no-azure-groups-returned-for-user)
            * 7.5.6.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoGroups](#rqsrs-042oauthgrafanaazureauthenticationuserrolesnogroups)
        * 7.5.7 [Azure Subgroup Memberships Not Considered](#azure-subgroup-memberships-not-considered)
            * 7.5.7.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SubgroupMemberships](#rqsrs-042oauthgrafanaazureauthenticationuserrolessubgroupmemberships)
        * 7.5.8 [Dynamic Group Membership Updates For Azure Users](#dynamic-group-membership-updates-for-azure-users)
            * 7.5.8.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingClickHouseRoles](#rqsrs-042oauthgrafanaazureauthenticationuserrolesnomatchingclickhouseroles)
        * 7.5.9 [Azure Group Names Match Roles in ClickHouse](#azure-group-names-match-roles-in-clickhouse)
            * 7.5.9.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SameName](#rqsrs-042oauthgrafanaazureauthenticationuserrolessamename)
        * 7.5.10 [No Matching Roles in ClickHouse for Azure Groups](#no-matching-roles-in-clickhouse-for-azure-groups)
            * 7.5.10.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthgrafanaazureauthenticationuserrolesnomatchingroles)
        * 7.5.11 [User Cannot View Groups in Azure](#user-cannot-view-groups-in-azure)
            * 7.5.11.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthgrafanaazureauthenticationuserrolesnopermissiontoviewgroups)
        * 7.5.12 [In ClickHouse There Is No Default Role Specified for Azure Users](#in-clickhouse-there-is-no-default-role-specified-for-azure-users)
            * 7.5.12.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthgrafanaazureauthenticationuserrolesnodefaultrole)
    * 7.6 [Azure Identity Management Actions](#azure-identity-management-actions)
        * 7.6.1 [Azure User State Changes](#azure-user-state-changes)
            * 7.6.1.1 [RQ.SRS-042.OAuth.Azure.Actions.UserDisabled](#rqsrs-042oauthazureactionsuserdisabled)
            * 7.6.1.2 [RQ.SRS-042.OAuth.Azure.Actions.UserDeleted](#rqsrs-042oauthazureactionsuserdeleted)
            * 7.6.1.3 [RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated](#rqsrs-042oauthazureactionsuserattributesupdated)
            * 7.6.1.4 [RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset](#rqsrs-042oauthazureactionsuserpasswordreset)
        * 7.6.2 [Azure Group and Role Membership](#azure-group-and-role-membership)
            * 7.6.2.1 [RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup](#rqsrs-042oauthazureactionsuseraddedtogroup)
            * 7.6.2.2 [RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup](#rqsrs-042oauthazureactionsuserremovedfromgroup)
            * 7.6.2.3 [RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted](#rqsrs-042oauthazureactionsgroupdeleted)
        * 7.6.3 [Azure Application and Consent](#azure-application-and-consent)
            * 7.6.3.1 [RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled](#rqsrs-042oauthazureactionsapplicationdisabled)
            * 7.6.3.2 [RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved](#rqsrs-042oauthazureactionsadminconsentremoved)
            * 7.6.3.3 [RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated](#rqsrs-042oauthazureactionsclientsecretrotated)
        * 7.6.4 [Azure Token and Session Management](#azure-token-and-session-management)
            * 7.6.4.1 [RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked](#rqsrs-042oauthazureactionsusersessionrevoked)
            * 7.6.4.2 [RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired](#rqsrs-042oauthazureactionsrefreshtokenexpired)
        * 7.6.5 [Access Token Processors are Missing From ClickHouse Configuration](#access-token-processors-are-missing-from-clickhouse-configuration)
            * 7.6.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationuserrolesnoaccesstokenprocessors)
    * 7.7 [Azure as an External User Directory](#azure-as-an-external-user-directory)
        * 7.7.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories](#rqsrs-042oauthgrafanaauthenticationuserdirectories)
            * 7.7.1.1 [Incorrect Configuration in User Directories](#incorrect-configuration-in-user-directories)
                * 7.7.1.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.provider](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationprovider)
                * 7.7.1.1.2 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationclientid)
                * 7.7.1.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtenantid)
                * 7.7.1.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenprocessor)
                * 7.7.1.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorstokenroles)
                * 7.7.1.1.6 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesincorrectconfigurationtokenprocessorsmultipleentries)
            * 7.7.1.2 [Missing Configuration in User Directories](#missing-configuration-in-user-directories)
                * 7.7.1.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationaccesstokenprocessors)
                * 7.7.1.2.2 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorsprovider)
                * 7.7.1.2.3 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorsclientid)
                * 7.7.1.2.4 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationtokenprocessorstenantid)
                * 7.7.1.2.5 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectories)
                * 7.7.1.2.6 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestoken)
                * 7.7.1.2.7 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenprocessor)
                * 7.7.1.2.8 [RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles](#rqsrs-042oauthgrafanaauthenticationuserdirectoriesmissingconfigurationuserdirectoriestokenroles)
* 8 [Keycloak](#keycloak)
    * 8.1 [Setting up a Realm in Keycloak](#setting-up-a-realm-in-keycloak)
        * 8.1.1 [RQ.SRS-042.OAuth.Keycloak.RealmSetup](#rqsrs-042oauthkeycloakrealmsetup)
    * 8.2 [Opaque Token Support for Keycloak](#opaque-token-support-for-keycloak)
        * 8.2.1 [RQ.SRS-042.OAuth.Keycloak.OpaqueTokenSupport](#rqsrs-042oauthkeycloakopaquetokensupport)
        * 8.2.2 [Opaque Token Constraints and Gateway Workaround For Keycloak](#opaque-token-constraints-and-gateway-workaround-for-keycloak)
            * 8.2.2.1 [RQ.SRS-042.OAuth.Keycloak.Tokens.Constraints](#rqsrs-042oauthkeycloaktokensconstraints)
            * 8.2.2.2 [RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational](#rqsrs-042oauthkeycloaktokensopaqueoperational)
            * 8.2.2.3 [RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Configuration.Validation](#rqsrs-042oauthkeycloaktokensopaqueconfigurationvalidation)
            * 8.2.2.4 [RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ProviderType](#rqsrs-042oauthkeycloaktokensopaqueoperationalprovidertype)
            * 8.2.2.5 [RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ReferenceToken](#rqsrs-042oauthkeycloaktokensopaqueoperationalreferencetoken)
            * 8.2.2.6 [RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.Failure](#rqsrs-042oauthkeycloaktokensopaqueoperationalfailure)
    * 8.3 [Getting Access Token from Keycloak](#getting-access-token-from-keycloak)
        * 8.3.1 [RQ.SRS-042.OAuth.Keycloak.GetAccessToken](#rqsrs-042oauthkeycloakgetaccesstoken)
    * 8.4 [Access Token Processors For Keycloak](#access-token-processors-for-keycloak)
        * 8.4.1 [RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors](#rqsrs-042oauthkeycloakaccesstokenprocessors)
    * 8.5 [User Groups in Keycloak](#user-groups-in-keycloak)
        * 8.5.1 [Setting up User Groups in Keycloak](#setting-up-user-groups-in-keycloak)
            * 8.5.1.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserDirectories.UserGroups](#rqsrs-042oauthgrafanakeycloakauthenticationuserdirectoriesusergroups)
        * 8.5.2 [Query Execution Based on User Roles in ClickHouse with Keycloak](#query-execution-based-on-user-roles-in-clickhouse-with-keycloak)
            * 8.5.2.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles](#rqsrs-042oauthgrafanakeycloakauthenticationuserroles)
        * 8.5.3 [Filtering Keycloak Groups for Role Assignment](#filtering-keycloak-groups-for-role-assignment)
            * 8.5.3.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.GroupFiltering](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesgroupfiltering)
        * 8.5.4 [User in Multiple Keycloak Groups](#user-in-multiple-keycloak-groups)
            * 8.5.4.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.MultipleGroups](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesmultiplegroups)
        * 8.5.5 [No Duplicate Role Assignments for Overlapping Keycloak Groups](#no-duplicate-role-assignments-for-overlapping-keycloak-groups)
            * 8.5.5.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.OverlappingUsers](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesoverlappingusers)
        * 8.5.6 [No Keycloak Groups Returned for User](#no-keycloak-groups-returned-for-user)
            * 8.5.6.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoGroups](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesnogroups)
        * 8.5.7 [Keycloak Subgroup Memberships Not Considered](#keycloak-subgroup-memberships-not-considered)
            * 8.5.7.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SubgroupMemberships](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolessubgroupmemberships)
        * 8.5.8 [Dynamic Group Membership Updates For Keycloak](#dynamic-group-membership-updates-for-keycloak)
            * 8.5.8.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesnomatchingclickhouseroles)
        * 8.5.9 [Keycloak Group Names Match Roles in ClickHouse](#keycloak-group-names-match-roles-in-clickhouse)
            * 8.5.9.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SameName](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolessamename)
        * 8.5.10 [No Matching Roles in ClickHouse for Keycloak Groups](#no-matching-roles-in-clickhouse-for-keycloak-groups)
            * 8.5.10.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesnomatchingroles)
        * 8.5.11 [User Cannot View Groups in Keycloak](#user-cannot-view-groups-in-keycloak)
            * 8.5.11.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesnopermissiontoviewgroups)
        * 8.5.12 [In ClickHouse There Is No Default Role Specified for Keycloak Users](#in-clickhouse-there-is-no-default-role-specified-for-keycloak-users)
            * 8.5.12.1 [RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthgrafanakeycloakauthenticationuserrolesnodefaultrole)
    * 8.6 [Keycloak Identity Management Actions](#keycloak-identity-management-actions)
        * 8.6.1 [Keycloak User State Changes](#keycloak-user-state-changes)
            * 8.6.1.1 [RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled](#rqsrs-042oauthkeycloakactionsuserdisabled)
            * 8.6.1.2 [RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted](#rqsrs-042oauthkeycloakactionsuserdeleted)
            * 8.6.1.3 [RQ.SRS-042.OAuth.Keycloak.Actions.UserAttributesUpdated](#rqsrs-042oauthkeycloakactionsuserattributesupdated)
        * 8.6.2 [Keycloak Group and Role Membership](#keycloak-group-and-role-membership)
            * 8.6.2.1 [RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup](#rqsrs-042oauthkeycloakactionsuseraddedtogroup)
            * 8.6.2.2 [RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup](#rqsrs-042oauthkeycloakactionsuserremovedfromgroup)
            * 8.6.2.3 [RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted](#rqsrs-042oauthkeycloakactionsgroupdeleted)
        * 8.6.3 [Keycloak Application and Consent](#keycloak-application-and-consent)
            * 8.6.3.1 [RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled](#rqsrs-042oauthkeycloakactionsclientdisabled)
            * 8.6.3.2 [RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked](#rqsrs-042oauthkeycloakactionsconsentrevoked)
        * 8.6.4 [Keycloak Token and Session Management](#keycloak-token-and-session-management)
            * 8.6.4.1 [RQ.SRS-042.OAuth.Keycloak.Actions.UserSessionRevoked](#rqsrs-042oauthkeycloakactionsusersessionrevoked)
            * 8.6.4.2 [RQ.SRS-042.OAuth.Keycloak.Actions.RefreshTokenRevoked](#rqsrs-042oauthkeycloakactionsrefreshtokenrevoked)
            * 8.6.4.3 [RQ.SRS-042.OAuth.Keycloak.Actions.NotBeforePolicyUpdated](#rqsrs-042oauthkeycloakactionsnotbeforepolicyupdated)
* 9 [Static Key](#static-key)
    * 9.1 [Access Token Processors For Static Key](#access-token-processors-for-static-key)
        * 9.1.1 [RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors](#rqsrs-042oauthstatickeyaccesstokenprocessors)
    * 9.2 [Static Key as an External User Directory](#static-key-as-an-external-user-directory)
        * 9.2.1 [RQ.SRS-042.OAuth.StaticKey.UserDirectory](#rqsrs-042oauthstatickeyuserdirectory)
    * 9.3 [Static Key Algorithm Support](#static-key-algorithm-support)
        * 9.3.1 [RQ.SRS-042.OAuth.StaticKey.Algorithms](#rqsrs-042oauthstatickeyalgorithms)
            * 9.3.1.1 [RQ.SRS-042.OAuth.StaticKey.Algorithm.None](#rqsrs-042oauthstatickeyalgorithmnone)
    * 9.4 [Static Key Configuration Parameters](#static-key-configuration-parameters)
        * 9.4.1 [RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey](#rqsrs-042oauthstatickeyparametersstatickey)
        * 9.4.2 [RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64](#rqsrs-042oauthstatickeyparametersstatickeybase64)
        * 9.4.3 [RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey](#rqsrs-042oauthstatickeyparameterspublickey)
        * 9.4.4 [RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey](#rqsrs-042oauthstatickeyparametersprivatekey)
        * 9.4.5 [RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword](#rqsrs-042oauthstatickeyparameterspublickeypassword)
        * 9.4.6 [RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword](#rqsrs-042oauthstatickeyparametersprivatekeypassword)
    * 9.5 [Static Key Configuration Validation](#static-key-configuration-validation)
        * 9.5.1 [RQ.SRS-042.OAuth.StaticKey.Configuration.Validation](#rqsrs-042oauthstatickeyconfigurationvalidation)
* 10 [Static JWKS](#static-jwks)
    * 10.1 [Access Token Processors For Static JWKS](#access-token-processors-for-static-jwks)
        * 10.1.1 [RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors](#rqsrs-042oauthstaticjwksaccesstokenprocessors)
    * 10.2 [Static JWKS as an External User Directory](#static-jwks-as-an-external-user-directory)
        * 10.2.1 [RQ.SRS-042.OAuth.StaticJWKS.UserDirectory](#rqsrs-042oauthstaticjwksuserdirectory)
    * 10.3 [Static JWKS Configuration Parameters](#static-jwks-configuration-parameters)
        * 10.3.1 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks](#rqsrs-042oauthstaticjwksparametersstaticjwks)
        * 10.3.2 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile](#rqsrs-042oauthstaticjwksparametersstaticjwksfile)
        * 10.3.3 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims](#rqsrs-042oauthstaticjwksparametersclaims)
        * 10.3.4 [RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway](#rqsrs-042oauthstaticjwksparametersverifierleeway)
    * 10.4 [Static JWKS Configuration Validation](#static-jwks-configuration-validation)
        * 10.4.1 [RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation](#rqsrs-042oauthstaticjwksconfigurationvalidation)
    * 10.5 [Static JWKS Algorithm Support](#static-jwks-algorithm-support)
        * 10.5.1 [RQ.SRS-042.OAuth.StaticJWKS.Algorithms](#rqsrs-042oauthstaticjwksalgorithms)
* 11 [Remote JWKS](#remote-jwks)
    * 11.1 [Access Token Processors For Remote JWKS](#access-token-processors-for-remote-jwks)
        * 11.1.1 [RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors](#rqsrs-042oauthremotejwksaccesstokenprocessors)
    * 11.2 [Setting up Remote JWKS](#setting-up-remote-jwks)
        * 11.2.1 [RQ.SRS-042.OAuth.RemoteJWKS.Setup](#rqsrs-042oauthremotejwkssetup)
    * 11.3 [Remote JWKS Configuration Parameters](#remote-jwks-configuration-parameters)
        * 11.3.1 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri](#rqsrs-042oauthremotejwksparametersjwksuri)
        * 11.3.2 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout](#rqsrs-042oauthremotejwksparametersjwksrefreshtimeout)
        * 11.3.3 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims](#rqsrs-042oauthremotejwksparametersclaims)
        * 11.3.4 [RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway](#rqsrs-042oauthremotejwksparametersverifierleeway)
    * 11.4 [Remote JWKS Configuration Validation](#remote-jwks-configuration-validation)
        * 11.4.1 [RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation](#rqsrs-042oauthremotejwksconfigurationvalidation)
    * 11.5 [Remote JWKS Network Handling](#remote-jwks-network-handling)
        * 11.5.1 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout](#rqsrs-042oauthremotejwksnetworktimeout)
        * 11.5.2 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry](#rqsrs-042oauthremotejwksnetworkretry)
        * 11.5.3 [RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache](#rqsrs-042oauthremotejwksnetworkcache)
    * 11.6 [Remote JWKS Error Handling](#remote-jwks-error-handling)
        * 11.6.1 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure](#rqsrs-042oauthremotejwkserrorhandlingnetworkfailure)
        * 11.6.2 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse](#rqsrs-042oauthremotejwkserrorhandlinginvalidresponse)
        * 11.6.3 [RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache](#rqsrs-042oauthremotejwkserrorhandlingexpiredcache)
* 12 [Token Processor](#token-processor)
    * 12.1 [Common Configuration Parameters](#common-configuration-parameters)
        * 12.1.1 [RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime](#rqsrs-042oauthcommonparameterscachelifetime)
        * 12.1.2 [RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim](#rqsrs-042oauthcommonparametersusernameclaim)
        * 12.1.3 [RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim](#rqsrs-042oauthcommonparametersgroupsclaim)
        * 12.1.4 [RQ.SRS-042.OAuth.Common.Parameters.Unfiltered](#rqsrs-042oauthcommonparametersunfiltered)
    * 12.2 [Token Cache Behavior](#token-cache-behavior)
        * 12.2.1 [RQ.SRS-042.OAuth.Common.Cache.Behavior](#rqsrs-042oauthcommoncachebehavior)
    * 12.3 [Configuration Validation](#configuration-validation)
        * 12.3.1 [RQ.SRS-042.OAuth.Common.Configuration.Validation](#rqsrs-042oauthcommonconfigurationvalidation)
* 13 [ClickHouse Actions After Token Validation](#clickhouse-actions-after-token-validation)
    * 13.1 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
        * 13.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests](#rqsrs-042oauthgrafanaauthenticationincorrectrequests)
        * 13.1.2 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheader)
        * 13.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheaderalg)
        * 13.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheadertyp)
        * 13.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsheadersignature)
        * 13.1.6 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbody)
        * 13.1.7 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodysub)
        * 13.1.8 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodyaud)
        * 13.1.9 [RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp](#rqsrs-042oauthgrafanaauthenticationincorrectrequestsbodyexp)
    * 13.2 [Token Handling](#token-handling)
        * 13.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired](#rqsrs-042oauthgrafanaauthenticationtokenhandlingexpired)
        * 13.2.2 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect](#rqsrs-042oauthgrafanaauthenticationtokenhandlingincorrect)
        * 13.2.3 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric](#rqsrs-042oauthgrafanaauthenticationtokenhandlingnonalphanumeric)
        * 13.2.4 [RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString](#rqsrs-042oauthgrafanaauthenticationtokenhandlingemptystring)
    * 13.3 [Caching](#caching)
        * 13.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching](#rqsrs-042oauthgrafanaauthenticationcaching)
        * 13.3.2 [Disable Caching](#disable-caching)
            * 13.3.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionnocache)
        * 13.3.3 [Cache Lifetime](#cache-lifetime)
            * 13.3.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictioncachelifetime)
        * 13.3.4 [Exceeding Max Cache Size](#exceeding-max-cache-size)
            * 13.3.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionmaxcachesize)
        * 13.3.5 [Cache Eviction Policy](#cache-eviction-policy)
            * 13.3.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy](#rqsrs-042oauthgrafanaauthenticationcachingcacheevictionpolicy)
    * 13.4 [Authentication and Login](#authentication-and-login)
        * 13.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication](#rqsrs-042oauthgrafanaauthenticationactionsauthentication)
        * 13.4.2 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client](#rqsrs-042oauthgrafanaauthenticationactionsauthenticationclient)
    * 13.5 [Session Management](#session-management)
        * 13.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement](#rqsrs-042oauthgrafanaauthenticationactionssessionmanagement)

    
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

- **Identity Provider (IdP):** A service that issues access tokens after authenticating users. Examples include [Azure] Active Directory, Google Identity, and Okta.
- **Access Token:** A token issued by an IdP that grants access to protected resources. It is often a JSON Web Token (JWT) containing user identity and permissions.
- **[JWT (JSON Web Token)](https://github.com/Altinity/clickhouse-regression/blob/main/jwt_authentication/requirements/requirements.md):** A compact, URL-safe means of representing claims to be transferred between two parties. It is used in OAuth 2.0 for access tokens.
- [Grafana] User: A user in [Grafana] who can authenticate with [ClickHouse] using OAuth 2.0.
- [ClickHouse] User: A user defined in [ClickHouse] who can authenticate using OAuth 2.0 access tokens.
- **User Directory:** A source of user information that [ClickHouse] can query to retrieve user details and roles. This can be an external IdP or a locally defined user directory.
- User: A person or system that interacts with [ClickHouse] and can authenticate using OAuth 2.0 access tokens.

## Overview of the Functionality

To enable OAuth 2.0 authentication in [ClickHouse], one must define Access Token Processors, which allow [ClickHouse] to validate and trust OAuth 2.0 access tokens issued by external Identity Providers (IdPs), such as [Azure] AD.

OAuth-based authentication works by allowing users to authenticate using an access token (often a JWT) issued by the IdP. [ClickHouse] supports two modes of operation with these tokens:

**Locally Defined Users:** If a user is already defined in [ClickHouse] (via users.xml or SQL), their authentication method can be set to jwt, enabling token-based authentication.

**Externally Defined Users:** If a user is not defined locally, [ClickHouse] can still authenticate them by validating the token and retrieving user information from the Identity Provider. If valid, the user is granted access with predefined roles.

All OAuth 2.0 access tokens must be validated through one of the configured `token_processors` in `config.xml`.

### Access Token Processors

Key Parameters:

- **provider:** Specifies the identity provider (for example, `azure`).

- **cache_lifetime:** maximum lifetime of cached token (in seconds). Optional, default: 3600

- **client_id:** The registered application ID in Azure.

- **tenant_id:** The [Azure] tenant that issues the tokens.

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

To authenticate with OAuth, Grafana usermust obtain an access token from the identity provider and present it to [ClickHouse].

### Forward OAuth Identity

#### RQ.SRS-042.OAuth.Grafana.Authentication.ForwardOAuthIdentity
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

<img width="1023" height="266" alt="Screenshot from 2025-07-28 16-12-02" src="https://github.com/user-attachments/assets/6c9f38f1-ceaf-480a-8ca4-6599968cbb61" />

## Identity Providers

[ClickHouse] SHALL support OAuth 2.0 authentication with various identity providers, including but not limited to:

- [Azure] Active Directory
- Google Identity
- Keycloak

### Number of Identity Providers That Can Be Used Concurrently

#### RQ.SRS-042.OAuth.IdentityProviders.Concurrent
version: 1.0

[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `token_processors` section of `config.xml`.

### Changing Identity Providers

#### RQ.SRS-042.OAuth.IdentityProviders.Change
version: 1.0

[ClickHouse] SHALL allow changing the identity provider by updating the `token_processors` section in the `config.xml` file. After changing the identity provider, [ClickHouse] SHALL require a restart to apply the new configuration.

## Setting Up OAuth Authentication

### Credentials

#### RQ.SRS-042.OAuth.Credentials
version: 1.0

[Grafana] SHALL redirect Grafana user to the Identity Provider authorization endpoint to obtain an access token if the Grafana userhas provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>ClientnTENANT_ID=<Tenant ID>ClientnCLIENT_SECRET=<Client Secret>Clientn" > .env
```

## Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with [Azure] Active Directory ([Azure] AD) as an identity provider.

### Setting up an Application in Azure

#### RQ.SRS-042.OAuth.Azure.ApplicationSetup 
version: 1.0

[ClickHouse] SHALL support integration with applications registered in [Azure] Active Directory. To set up an application in [Azure] for OAuth authentication, the following steps SHALL be performed:

```bash
ACCESS_TOKEN="<admin-access-token>"

curl -s -X POST "https://graph.microsoft.com/v1.0/applications" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "ClickHouse OAuth App",
    "signInAudience": "AzureADMyOrg",
    "web": {
      "redirectUris": ["http://localhost:3000/login/generic_oauth"]
    }
  }'
```

### Opaque Token Support for Azure

#### RQ.SRS-042.OAuth.Azure.Tokens.Opaque
version: 1.0

[ClickHouse] SHALL support validating opaque access tokens issued by [Azure] AD using an Access Token Processor configured for OpenID. The processor SHALL be defined in `config.xml` as follows:

```xml
<clickhouse>
    <token_processors>
        <azure_opaque>
            <provider>openid</provider>
            <configuration_endpoint>https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration</configuration_endpoint>
            <cache_lifetime>600</cache_lifetime>
            <username_claim>sub</username_claim>
            <groups_claim>groups</groups_claim>
        </azure_opaque>
    </token_processors>
</clickhouse>
```

#### Opaque Token Constraints and Gateway Workaround For Azure

##### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Constraints
version: 1.0

[ClickHouse] SHALL assume that Azure-issued access tokens are JWT by default. If the token_processors entry for [Azure] is configured in opaque mode, [ClickHouse] SHALL still accept tokens that are JWT strings while performing validation via remote calls as configured by the processor.

##### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational
version: 1.0

When `<provider>azure</provider>` or `<provider>openid</provider>` is used for [Azure] in the `token_processors` section,  
[ClickHouse] SHALL validate tokens by calling the configured discovery and/or `/userinfo` introspection endpoints instead  
of verifying the token locally. This SHALL be treated as "opaque behavior" operationally, regardless of the underlying token format.

##### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Configuration.Validation
version: 1.0

For [Azure] opaque-mode operation, exactly one of the following SHALL be configured per processor:

1. `configuration_endpoint`

2. both `userinfo_endpoint` and `token_introspection_endpoint`.

If neither (or all three) are set, [ClickHouse] SHALL reject the configuration as invalid.

#### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ProviderType
version: 1.0

In opaque mode, the provider parameter SHALL indicate the validation strategy and not the human-readable IdP name. 
For Azure-backed validation, provider MAY be set to [Azure] (Azure-specific flow) or `OpenID` (generic OpenID Connect flow). 
The chosen provider SHALL determine which endpoints and claims are used.

#### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.ReferenceToken
version: 1.0

[ClickHouse] SHALL support an external OAuth gateway that issues reference (opaque) tokens on behalf of [Azure]. In this pattern:

* The gateway exchanges [Azure] JWTs for gateway-issued reference tokens.

* [ClickHouse] is configured with `<provider>OpenID</provider>` pointing to the gateway's .well-known or its userinfo + `token_introspection` endpoints.

* [ClickHouse] SHALL validate tokens exclusively via the gateway's `introspection/userinfo` responses.

##### RQ.SRS-042.OAuth.Azure.Tokens.Opaque.Operational.Failure
version: 1.0

If the gateway's introspection or userinfo call fails, returns inactive/invalid status, or omits required claims, 
[ClickHouse] SHALL deny authentication and SHALL not fall back to local JWT verification for that request.

### Getting Access Token from Azure

#### RQ.SRS-042.OAuth.Azure.GetAccessToken
version: 1.0

To obtain an access token from [Azure] AD, you need to register an application in [Azure] AD and configure the necessary permissions. After that you must collect your `CLIENT_ID`, `TENANT_ID`, and `CLIENT_SECRET`.

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

An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token's issuer, audience, and cryptographic signature.

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

### User Groups in Azure

#### Setting up User Groups in Azure

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserDirectories.UserGroups
version: 1.0

[ClickHouse] SHALL support user groups defined in [Azure] Active Directory ([Azure] AD) for role-based access control. In order to create a user group in [Azure] AD, you must obtain an [access token with the necessary permissions](#getting-access-token-from-azure) to create groups.

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

#### Query Execution Based on User Roles in ClickHouse with Azure

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles
version: 1.0

When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles 
assigned to the user in the `users_directories` section. Role mapping is based on the role name: 
if a user has a group or permission in [Azure] (or another IdP) and there is a role with the same name in
ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.

The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.

<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />


#### Filtering Azure Groups for Role Assignment

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.GroupFiltering
version: 1.0

When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the [Azure] based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.

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

The regex pattern `\bclickhouse-[a-zA-Z0-9]+\b` filters [Azure] AD group names to only match those that:

* Begin with exactly "clickhouse-"
* Are followed by one or more alphanumeric characters
* Are complete words (not parts of larger words)

This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.

#### User in Multiple Azure Groups

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.MultipleGroups
version: 1.0

When a user belongs to multiple groups in the [Azure], [ClickHouse] SHALL combine all roles that match these group names.
The user SHALL inherit the union of all permissions from these roles.

#### No Duplicate Role Assignments for Overlapping Azure Groups

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.OverlappingUsers
version: 1.0

When multiple groups in the [Azure] contain the same user, [ClickHouse] SHALL not create duplicate role assignments.
The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.

#### No Azure Groups Returned for User

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoGroups
version: 1.0

When a Grafana user is authenticated via OAuth and [Azure] does not return any groups for the user,
[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.

#### Azure Subgroup Memberships Not Considered

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SubgroupMemberships
version: 1.0

When a user belongs to subgroups in the [Azure], [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.

#### Dynamic Group Membership Updates For Azure Users

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingClickHouseRoles
version: 1.0

[ClickHouse] SHALL reflect changes in a user's group memberships from the [Azure] dynamically during the next token validation or cache refresh.
Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.

#### Azure Group Names Match Roles in ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

#### No Matching Roles in ClickHouse for Azure Groups

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

#### User Cannot View Groups in Azure

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign a default role to the user.

#### In ClickHouse There Is No Default Role Specified for Azure Users

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoles.NoDefaultRole
version: 1.0

When a Grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, Grafana userwill not be able to perform any actions after authentication.

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

### Azure Identity Management Actions

This section outlines how [ClickHouse] SHALL respond to various actions performed in [Azure] Active Directory that affect user identity, group membership, and token validity.

#### Azure User State Changes

##### RQ.SRS-042.OAuth.Azure.Actions.UserDisabled
version: 1.0

When a user is disabled in [Azure] AD, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/users/{user-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "accountEnabled": false
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserDeleted
version: 1.0

When a user is permanently deleted from [Azure] AD, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/users/{user-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserAttributesUpdated
version: 1.0

When a user's attributes (such as `UPN`, `email`, or `name`) are updated in [Azure] AD, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/users/{user-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "New Name"
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserPasswordReset
version: 1.0

When a user's password is reset in [Azure] AD, [ClickHouse] SHALL continue to validate access tokens without interruption, as password changes do not invalidate existing tokens.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/authentication/passwordMethods/{method-id}/resetPassword" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "newPassword": "new-password"
  }'
```

#### Azure Group and Role Membership

##### RQ.SRS-042.OAuth.Azure.Actions.UserAddedToGroup
version: 1.0

When a user is added to a group in [Azure] AD, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/groups/{group-id}/members/$ref" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "@odata.id": "https://graph.microsoft.com/v1.0/directoryObjects/{user-id}"
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.UserRemovedFromGroup
version: 1.0

When a user is removed from a group in [Azure] AD, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}/members/{user-id}/$ref" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.GroupDeleted
version: 1.0

When a group that is mapped to a [ClickHouse] role is deleted in [Azure] AD, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/groups/{group-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Azure Application and Consent

##### RQ.SRS-042.OAuth.Azure.Actions.ApplicationDisabled
version: 1.0

When the client application (service principal) used for OAuth integration is disabled in [Azure] AD, [ClickHouse] SHALL reject all incoming access tokens issued for that application.

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "accountEnabled": false
  }'
```

##### RQ.SRS-042.OAuth.Azure.Actions.AdminConsentRemoved
version: 1.0

If the admin consent for required permissions is revoked in [Azure] AD, [ClickHouse] SHALL reject authentication attempts until consent is granted again.

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/servicePrincipals/{sp-id}/appRoleAssignments/{assignment-id}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Azure.Actions.ClientSecretRotated
version: 1.0

When the client secret for the application is rotated in [Azure] AD, [ClickHouse] SHALL continue to validate tokens signed with the old secret until they expire, and seamlessly accept tokens signed with the new secret.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/applications/{app-id}/addPassword" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "passwordCredential": {
      "displayName": "New-Secret"
    }
  }'
```

#### Azure Token and Session Management

##### RQ.SRS-042.OAuth.Azure.Actions.UserSessionRevoked
version: 1.0

When a user's sign-in sessions are revoked in [Azure] AD (for example, via the `revokeSignInSessions` API), [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/users/{user-id}/revokeSignInSessions" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d ''
```

##### RQ.SRS-042.OAuth.Azure.Actions.RefreshTokenExpired
version: 1.0

When a refresh token expires as per the policy in [Azure] AD, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.

```bash
curl -s -X POST "https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'client_id={client-id}' \
  -d 'client_secret={client-secret}' \
  -d 'grant_type=refresh_token' \
  -d 'refresh_token={expired-refresh-token}'
```

#### Access Token Processors are Missing From ClickHouse Configuration

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors
version: 1.0

When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the Grafana user to authenticate and access resources.


### Azure as an External User Directory

An `external user directory` in [ClickHouse] is a remote identity source (such as `LDAP`, `Kerberos`, or an `OAuth Identity Provider`)
used to authenticate and retrieve user information that is not defined locally in [ClickHouse]. When enabled, [ClickHouse] dynamically
validates user credentials and assigns roles based on data from this external system instead of relying solely on locally configured users.

#### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use the [Azure] as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.

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

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.clientId
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `client_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.tenantId
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `tenant_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.processor
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.token.roles
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.IncorrectConfiguration.TokenProcessors.multipleEntries
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token_processors` or `user_directories` sections contain multiple entries that are the same.

For example, if there are multiple `<azuure>` entries in the `token_processors` section or multiple `<token>` entries in the `user_directories` section with the same `processor` attribute.

##### Missing Configuration in User Directories

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.provider
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.clientId
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `client_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.TokenProcessors.tenantId
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `tenant_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.processor
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.UserDirectories.MissingConfiguration.UserDirectories.token.roles
version: 1.0

[ClickHouse] SHALL not allow the Grafana user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.


## Keycloak

[ClickHouse] SHALL support OAuth 2.0 authentication with Keycloak as an identity provider.

### Setting up a Realm in Keycloak

#### RQ.SRS-042.OAuth.Keycloak.RealmSetup
version: 1.0

[ClickHouse] SHALL support integration with Keycloak realms. To set up a realm for OAuth authentication, the following steps SHALL be performed:

1. Prepare Realm Configuration JSON:

```json
{
  "realm": "grafana",
  "enabled": true,
  "clients": [
    {
      "clientId": "grafana-client",
      "name": "Grafana",
      "protocol": "openid-connect",
      "publicClient": false,
      "secret": "grafana-secret",
      "redirectUris": ["http://localhost:3000/login/generic_oauth"],
      "baseUrl": "http://localhost:3000",
      "standardFlowEnabled": true,
      "directAccessGrantsEnabled": true,
      "protocolMappers": [
        {
          "name": "groups",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-group-membership-mapper",
          "consentRequired": false,
          "config": {
            "claim.name": "groups",
            "jsonType.label": "String",
            "full.path": "false",
            "id.token.claim": "true",
            "access.token.claim": "true",
            "userinfo.token.claim": "true"
          }
        }
      ]
    }
  ],
  "users": [
    {
      "username": "demo",
      "enabled": true,
      "email": "demo@example.com",
      "firstName": "Demo",
      "lastName": "User",
      "emailVerified": true,
      "groups": ["/grafana-admins", "/can-read"],
      "credentials": [
        {
          "type": "password",
          "value": "demo"
        }
      ]
    }
  ],
  "groups": [
    {
      "name": "grafana-admins",
      "path": "/grafana-admins"
    },
    {
      "name": "can-read",
      "path": "/can-read"
    }
  ]
}
```

2. Import Realm into Keycloak Docker Container:

```bash
docker run --name keycloak \
  -v $(pwd)/realm-export.json:/opt/keycloak/data/import/realm-export.json \
  quay.io/keycloak/keycloak:latest \
  start-dev --import-realm
```

### Opaque Token Support for Keycloak

#### RQ.SRS-042.OAuth.Keycloak.OpaqueTokenSupport
version: 1.0

[ClickHouse] SHALL support validating opaque access tokens issued by Keycloak using an Access Token Processor configured for OpenID. The processor SHALL be defined in config.xml as follows:

```xml
<clickhouse>
    <token_processors>
        <keycloak_opaque>
            <provider>openid</provider>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <cache_lifetime>600</cache_lifetime>
            <username_claim>sub</username_claim>
            <groups_claim>groups</groups_claim>
        </keycloak_opaque>
    </token_processors>
</clickhouse>
```

#### Opaque Token Constraints and Gateway Workaround For Keycloak

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Constraints
version: 1.0

[ClickHouse] SHALL assume that Keycloak-issued access tokens are JWT by default. If the `token_processors` entry for 
[Keycloak] is configured in opaque mode, [ClickHouse] SHALL still accept tokens that are JWT strings while performing validation via remote calls as configured by the processor.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational
version: 1.0

When <provider>OpenID</provider> is used for Keycloak in the token_processors section, [ClickHouse] SHALL 
validate tokens by calling the configured discovery and/or user info / introspection endpoints instead of verifying the token locally. 
This SHALL be treated as "opaque behavior" operationally, regardless of the underlying token's format.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Configuration.Validation
version: 1.0

For Keycloak opaque-mode operation, exactly one of the following SHALL be configured per processor:

1. `configuration_endpoint`
2. both `userinfo_endpoint` and `token_introspection_endpoint`.

If neither (or all three) are set, the configuration SHALL be rejected as invalid.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ProviderType
version: 1.0

In opaque mode for Keycloak, provider SHALL be set to OpenID. The processor SHALL obtain endpoints from the Keycloak 
realm's `.well-known/openid-configuration` or from explicitly provided userinfo and `token_introspection` endpoints.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.ReferenceToken
version: 1.0

[ClickHouse] SHALL support an external OAuth gateway that issues reference (opaque) tokens on behalf of Keycloak. In this pattern:

* The gateway exchanges Keycloak JWTs for gateway-issued reference tokens.

* [ClickHouse] is configured with `<provider>OpenID</provider>` pointing to the gateway's .well-known or its userinfo + token_introspection endpoints.

* [ClickHouse] SHALL validate tokens exclusively via the gateway's `introspection/userinfo` responses.

##### RQ.SRS-042.OAuth.Keycloak.Tokens.Opaque.Operational.Failure
version: 1.0

If the gateway's introspection or userinfo call fails, returns inactive/invalid status, or omits required claims, 
[ClickHouse] SHALL deny authentication and SHALL not fall back to local JWT verification for that request.

### Getting Access Token from Keycloak

#### RQ.SRS-042.OAuth.Keycloak.GetAccessToken
version: 1.0

To obtain an access token from Keycloak, you need to have a configured realm, client, and user.

You can obtain an access token using the following command:

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxxx' \
  -d 'username=john' \
  -d 'password=secret'
```

### Access Token Processors For Keycloak

#### RQ.SRS-042.OAuth.Keycloak.AccessTokenProcessors
version: 1.0

An Access Token Processor for Keycloak defines how [ClickHouse] validates and interprets access tokens. This includes specifying the OpenID provider details.

Basic structure:

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

### User Groups in Keycloak

#### Setting up User Groups in Keycloak

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserDirectories.UserGroups
version: 1.0

[ClickHouse] SHALL support user groups defined in Keycloak for role-based access control. In order to create a user group in Keycloak, you must obtain an access token with the necessary permissions to create groups.

```bash
curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/groups' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "clickhouse-admin",
    "attributes": {
      "description": ["Users with administrative access to ClickHouse"]
    }
  }'
```

#### Query Execution Based on User Roles in ClickHouse with Keycloak

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles
version: 1.0

When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL be able to execute queries based on the roles 
assigned to the user in the `users_directories` section. Role mapping is based on the role name: 
if a user has a group or permission in Keycloak (or another IdP) and there is a role with the same name in
ClickHouse (e.g., `Admin`), the user will receive the permissions defined by the ClickHouse role.

The roles defined in the `<common_roles>` section of the `<token>` SHALL determine the permissions granted to the user.

#### Filtering Keycloak Groups for Role Assignment

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.GroupFiltering
version: 1.0

When a Grafana user is authenticated via OAuth, [ClickHouse] SHALL filter the groups returned by the `Keycloak` based on the `roles_filter` regular expression defined in the `<token>` section of the `config.xml` file.

For example,

```xml
<clickhouse>
    <user_directories>
        <token>
            <processor>keycloak_processor</processor>
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

The regex pattern `\bclickhouse-[a-zA-Z0-9]+\b` filters Keycloak group names to only match those that:

* Begin with exactly "clickhouse-"
* Are followed by one or more alphanumeric characters
* Are complete words (not parts of larger words)

This filter ensures only groups with names like "clickhouse-admin" or "clickhouse-reader" will be mapped to ClickHouse roles, allowing for controlled role-based access.

#### User in Multiple Keycloak Groups

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.MultipleGroups
version: 1.0

When a user belongs to multiple groups in the `Keycloak`, [ClickHouse] SHALL combine all roles that match these group names.
The user SHALL inherit the union of all permissions from these roles.

#### No Duplicate Role Assignments for Overlapping Keycloak Groups

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.OverlappingUsers
version: 1.0

When multiple groups in the `Keycloak` contain the same user, [ClickHouse] SHALL not create duplicate role assignments.
The system SHALL merge roles and ensure no duplicated permissions are assigned to the same user.

#### No Keycloak Groups Returned for User

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoGroups
version: 1.0

When a Grafana user is authenticated via OAuth and Keycloak does not return any groups for the user,
[ClickHouse] SHALL assign only the default role if it is specified in the `<common_roles>` section of the `<token>` configuration. If no default role is specified, the user SHALL not be able to perform any actions after authentication.

#### Keycloak Subgroup Memberships Not Considered

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SubgroupMemberships
version: 1.0

When a user belongs to subgroups in the `Keycloak`, [ClickHouse] SHALL not automatically assign roles based on subgroup memberships. Only direct group memberships SHALL be considered for role assignments.

#### Dynamic Group Membership Updates For Keycloak

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingClickHouseRoles
version: 1.0

[ClickHouse] SHALL reflect changes in a user's group memberships from the `Keycloak` dynamically during the next token validation or cache refresh.
Permissions SHALL update automatically without requiring ClickHouse restart or manual reconfiguration.

#### Keycloak Group Names Match Roles in ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

#### No Matching Roles in ClickHouse for Keycloak Groups

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

#### User Cannot View Groups in Keycloak

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign a default role to the user.

#### In ClickHouse There Is No Default Role Specified for Keycloak Users

##### RQ.SRS-042.OAuth.Grafana.Keycloak.Authentication.UserRoles.NoDefaultRole
version: 1.0

When a Grafana user is authenticated via OAuth and no roles are specified in the `<common_roles>` section of the `<token>`, Grafana userwill not be able to perform any actions after authentication.

The role configuration example,

```xml
<clickhouse>
    <token_processors>
        <keycloak_processor>
            <provider>OpenID</provider>
            <userinfo_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>http://keycloak:8080/realms/grafana/protocol/openid-connect/token/introspect</token_introspection_endpoint>
            <jwks_uri>http://keycloak:8080/realms/grafana/protocol/openid-connect/certs</jwks_uri>
        </keycloak_processor>
    </token_processors>
    <user_directories>
        <token>
            <processor>keycloak_processor</processor>
            <common_roles>
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Keycloak Identity Management Actions

This section outlines how [ClickHouse] SHALL respond to various actions performed in Keycloak that affect user identity, group membership, and token validity.

#### Keycloak User State Changes

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserDisabled
version: 1.0

When a user is disabled in Keycloak, [ClickHouse] SHALL reject any subsequent authentication attempts with that user's existing access tokens and SHALL prevent the issuance of new tokens for that user.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserDeleted
version: 1.0

When a user is permanently deleted from Keycloak, [ClickHouse] SHALL invalidate all of that user's existing sessions and reject any authentication attempts using their tokens.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserAttributesUpdated
version: 1.0

When a user's attributes (such as `username`, `email`, or `firstName`) are updated in Keycloak, [ClickHouse] SHALL recognize the updated claims in newly issued tokens and reflect these changes upon the user's next authentication.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new-username",
    "email": "new-email@example.com"
  }'
```

#### Keycloak Group and Role Membership

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserAddedToGroup
version: 1.0

When a user is added to a group in Keycloak, [ClickHouse] SHALL grant the user the corresponding role and associated permissions on their next login, provided the group is mapped to a role in [ClickHouse].

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserRemovedFromGroup
version: 1.0

When a user is removed from a group in Keycloak, [ClickHouse] SHALL revoke the corresponding role and its permissions from the user on their next login.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.GroupDeleted
version: 1.0

When a group that is mapped to a [ClickHouse] role is deleted in Keycloak, users who were members of that group SHALL lose the associated permissions in [ClickHouse] upon their next authentication.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/groups/{group-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Keycloak Application and Consent

##### RQ.SRS-042.OAuth.Keycloak.Actions.ClientDisabled
version: 1.0

When the client application used for OAuth integration is disabled in Keycloak, [ClickHouse] SHALL reject all incoming access tokens issued for that client.

```bash
curl -X PUT 'https://keycloak.example.com/admin/realms/myrealm/clients/{client-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.ConsentRevoked
version: 1.0

If a user's consent for the application is revoked in Keycloak, [ClickHouse] SHALL reject authentication attempts until consent is granted again.

```bash
curl -X DELETE 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/consents/{client-id}' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### Keycloak Token and Session Management

##### RQ.SRS-042.OAuth.Keycloak.Actions.UserSessionRevoked
version: 1.0

When a user's sign-in sessions are revoked in Keycloak, [ClickHouse] SHALL reject the user's access and refresh tokens upon the next validation attempt.

```bash
curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/users/{user-id}/logout' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.RefreshTokenRevoked
version: 1.0

When a refresh token is revoked via the logout endpoint, [ClickHouse] SHALL require the user to re-authenticate to obtain a new access token.

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxx' \
  -d 'refresh_token=eyJ...'
```

##### RQ.SRS-042.OAuth.Keycloak.Actions.NotBeforePolicyUpdated
version: 1.0

When a `not-before` policy is pushed for a realm or user in Keycloak, all tokens issued before this time SHALL be invalidated, and [ClickHouse] SHALL reject them.

```bash
curl -X POST 'https://keycloak.example.com/admin/realms/myrealm/push-revocation' \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

## Static Key

### Access Token Processors For Static Key

#### RQ.SRS-042.OAuth.StaticKey.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a static key. The configuration requires specifying the algorithm and the key.

```xml
<clickhouse>
    <token_processors>
        <my_static_key_validator>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
        </my_static_key_validator>
    </token_processors>
</clickhouse>
```

### Static Key as an External User Directory

#### RQ.SRS-042.OAuth.StaticKey.UserDirectory
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static key as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.

```xml
<clickhouse>
    <token_processors>
        <my_static_key_validator>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
        </my_static_key_validator>
    </token_processors>
    <user_directories>
        <token>
            <processor>my_static_key_validator</processor>
            <common_roles>
                <my_role />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Static Key Algorithm Support

#### RQ.SRS-042.OAuth.StaticKey.Algorithms
version: 1.0

[ClickHouse] SHALL support the following algorithms for static key validation:

| HMAC  | RSA   | ECDSA  | PSS   | EdDSA   |
|-------|-------|--------|-------|---------|
| HS256 | RS256 | ES256  | PS256 | Ed25519 |
| HS384 | RS384 | ES384  | PS384 | Ed448   |
| HS512 | RS512 | ES512  | PS512 |         |
|       |       | ES256K |       |         |

##### RQ.SRS-042.OAuth.StaticKey.Algorithm.None
version: 1.0

[ClickHouse] SHALL  support `None` algorithm.

### Static Key Configuration Parameters

#### RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKey
version: 1.0

[ClickHouse] SHALL support the `static_key` parameter for symmetric algorithms (HS* family). This parameter SHALL be mandatory for `HS*` family algorithms and SHALL contain the secret key used for signature validation.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_hs256_validator>
            <algo>HS256</algo>
            <static_key>my_secret_key_for_jwt_signing</static_key>
        </my_hs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.StaticKeyBase64
version: 1.0

[ClickHouse] SHALL support the `static_key_in_base64` parameter to indicate if the `static_key` is base64-encoded. This parameter SHALL be optional with a default value of `False`.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_hs256_validator>
            <algo>HS256</algo>
            <static_key>bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=</static_key>
            <static_key_in_base64>true</static_key_in_base64>
        </my_hs256_validator>
    </token_processors>
</clickhouse>
```

In this example, the base64-encoded string `bXlfc2VjcmV0X2tleV9mb3Jfand0X3NpZ25pbmc=` decodes to `my_secret_key_for_jwt_signing`.

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKey
version: 1.0

[ClickHouse] SHALL support the `public_key` parameter for asymmetric algorithms. This parameter SHALL be mandatory except for `HS*` family algorithms and `None` algorithm. The public key SHALL be used to verify JWT signatures.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKey
version: 1.0

[ClickHouse] SHALL support the `private_key` parameter for asymmetric algorithms. This parameter SHALL be optional and SHALL be used when the private key is needed for additional operations.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
            <private_key>-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----</private_key>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PublicKeyPassword
version: 1.0

[ClickHouse] SHALL support the `public_key_password` parameter to specify the password for the public key. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <algo>RS256</algo>
            <public_key>-----BEGIN ENCRYPTED PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END ENCRYPTED PUBLIC KEY-----</public_key>
            <public_key_password>my_public_key_password</public_key_password>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticKey.Parameters.PrivateKeyPassword
version: 1.0

[ClickHouse] SHALL support the `private_key_password` parameter to specify the password for the private key. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_rs256_validator>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
            <private_key>-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END ENCRYPTED PRIVATE KEY-----</private_key>
            <private_key_password>my_private_key_password</private_key_password>
        </my_rs256_validator>
    </token_processors>
</clickhouse>
```

### Static Key Configuration Validation

#### RQ.SRS-042.OAuth.StaticKey.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate static key configuration as follows:

* For `HS*` family algorithms: `static_key` SHALL be mandatory
* For asymmetric algorithms (RS*, ES*, PS*, Ed*): `public_key` SHALL be mandatory
* `algo` parameter SHALL be mandatory and SHALL contain a supported algorithm value
* If `static_key_in_base64` is `True`, [ClickHouse] SHALL decode the `static_key` from base64 before use

**Valid Configuration Examples:**

**HS256 with static key:**
```xml
<clickhouse>
    <token_processors>
        <hs256_validator>
            <algo>HS256</algo>
            <static_key>my_secret_key</static_key>
        </hs256_validator>
    </token_processors>
</clickhouse>
```

**RS256 with public key:**
```xml
<clickhouse>
    <token_processors>
        <rs256_validator>
            <algo>RS256</algo>
            <public_key>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----</public_key>
        </rs256_validator>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Missing static_key for HS256:**
```xml
<clickhouse>
    <token_processors>
        <invalid_hs256_validator>
            <algo>HS256</algo>
            <!-- Missing static_key - will be rejected -->
        </invalid_hs256_validator>
    </token_processors>
</clickhouse>
```

**Missing public_key for RS256:**
```xml
<clickhouse>
    <token_processors>
        <invalid_rs256_validator>
            <algo>RS256</algo>
            <!-- Missing public_key - will be rejected -->
        </invalid_rs256_validator>
    </token_processors>
</clickhouse>
```


## Static JWKS

### Access Token Processors For Static JWKS

#### RQ.SRS-042.OAuth.StaticJWKS.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a static JSON Web Key Set (JWKS). The configuration can be provided directly or from a file.

```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

### Static JWKS as an External User Directory

#### RQ.SRS-042.OAuth.StaticJWKS.UserDirectory
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use a JWT validated with a static JWKS as a dynamic source of user information. This requires configuring the `<token>` section in `user_directories`.

```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
    <user_directories>
        <token>
            <processor>my_static_jwks_validator</processor>
            <common_roles>
                <my_role />
            </common_roles>
        </token>
    </user_directories>
</clickhouse>
```

### Static JWKS Configuration Parameters

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwks
version: 1.0

[ClickHouse] SHALL support the `static_jwks` parameter to specify the JWKS content directly in JSON format. This parameter SHALL contain a valid JSON Web Key Set structure.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <static_jwks>{
                "keys": [
                    {
                        "kty": "RSA",
                        "alg": "RS256",
                        "kid": "my-key-id-1",
                        "use": "sig",
                        "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
                        "e": "AQAB"
                    }
                ]
            }</static_jwks>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.StaticJwksFile
version: 1.0

[ClickHouse] SHALL support the `static_jwks_file` parameter to specify the path to a file containing the JWKS content. The file SHALL contain valid JSON Web Key Set data.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

**File content example (`/etc/clickhouse-server/jwks.json`):**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "my-key-id-1",
            "use": "sig",
            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
            "e": "AQAB"
        },
        {
            "kty": "RSA",
            "alg": "RS384",
            "kid": "my-key-id-2",
            "use": "sig",
            "n": "another-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.Claims
version: 1.0

[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <claims>{"iss": "https://my-auth-server.com", "aud": "clickhouse-app"}</claims>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, tokens must contain both `iss` (issuer) and `aud` (audience) claims with the specified values to be considered valid.

#### RQ.SRS-042.OAuth.StaticJWKS.Parameters.VerifierLeeway
version: 1.0

[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_static_jwks_validator>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <verifier_leeway>30</verifier_leeway>
        </my_static_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, a 30-second clock skew tolerance is allowed, meaning tokens can be up to 30 seconds expired or not yet valid due to clock differences.

### Static JWKS Configuration Validation

#### RQ.SRS-042.OAuth.StaticJWKS.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate static JWKS configuration as follows:

* Only one of `static_jwks` or `static_jwks_file` SHALL be present in one verifier
* If both or neither are specified, [ClickHouse] SHALL reject the configuration as invalid
* Only RS* family algorithms SHALL be supported for static JWKS validation
* The JWKS content SHALL be valid JSON format
* If `static_jwks_file` is specified, the file SHALL exist and be readable

**Valid Configuration Examples:**

**Using static_jwks:**
```xml
<clickhouse>
    <token_processors>
        <valid_jwks_validator>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
        </valid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Using static_jwks_file:**
```xml
<clickhouse>
    <token_processors>
        <valid_jwks_file_validator>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
        </valid_jwks_file_validator>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Both static_jwks and static_jwks_file specified:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <static_jwks_file>/etc/clickhouse-server/jwks.json</static_jwks_file>
            <!-- Both specified - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Neither static_jwks nor static_jwks_file specified:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <!-- Neither specified - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

**Unsupported algorithm in JWKS:**
```xml
<clickhouse>
    <token_processors>
        <invalid_jwks_validator>
            <static_jwks>{"keys": [{"kty": "RSA", "alg": "HS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
            <!-- HS256 not supported for JWKS - will be rejected -->
        </invalid_jwks_validator>
    </token_processors>
</clickhouse>
```

### Static JWKS Algorithm Support

#### RQ.SRS-042.OAuth.StaticJWKS.Algorithms
version: 1.0

[ClickHouse] SHALL support only RS* family algorithms for static JWKS validation:

* RS256
* RS384  
* RS512

[ClickHouse] SHALL reject JWKS entries with unsupported algorithms.

**Supported Algorithm Examples:**

**RS256:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "rs256-key",
            "use": "sig",
            "n": "t6Q8P-vqQ9KpSWmo1-bqR6ySVRKcJEFNNXmWFQKPVTOw",
            "e": "AQAB"
        }
    ]
}
```

**RS384:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS384",
            "kid": "rs384-key",
            "use": "sig",
            "n": "another-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

**RS512:**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS512",
            "kid": "rs512-key",
            "use": "sig",
            "n": "third-modulus-value",
            "e": "AQAB"
        }
    ]
}
```

**Unsupported Algorithm Example (will be rejected):**
```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "HS256",
            "kid": "hs256-key",
            "use": "sig",
            "n": "modulus-value",
            "e": "AQAB"
        }
    ]
}
```

## Remote JWKS

### Access Token Processors For Remote JWKS

#### RQ.SRS-042.OAuth.RemoteJWKS.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL support validating JWTs using a remote JSON Web Key Set (JWKS) fetched from a URI.

```xml
<clickhouse>
    <token_processors>
        <basic_auth_server>
          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>
          <jwks_refresh_timeout>300000</jwks_refresh_timeout>
        </basic_auth_server>
    </token_processors>
</clickhouse>
```

### Setting up Remote JWKS

#### RQ.SRS-042.OAuth.RemoteJWKS.Setup
version: 1.0

[ClickHouse] SHALL support custom JWKS setup for services that need to issue their own JWT tokens without using a full Identity Provider.

**Generate RSA Key Pair for JWT Signing:**

```bash
openssl genrsa -out jwt-private.pem 2048

openssl rsa -in jwt-private.pem -pubout -out jwt-public.pem
```

**Create JSON Web Key Set (JWKS) from Public Key:**

A JWKS is a JSON document that includes your public key parameters. For RSA it looks like:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "my-key-id-1",
      "use": "sig",
      "alg": "RS256",
      "n": "<base64url-modulus>",
      "e": "AQAB"
    }
  ]
}
```

**Deploy JWKS to HTTPS Web Server:**

Drop `jwks.json` behind any HTTPS-capable web server (nginx, Caddy, even a tiny Flask/FastAPI app). Example path:

```
https://auth.example.com/.well-known/jwks.json
```

**Configure ClickHouse Token Processor:**

```xml
<clickhouse>
  <token_processors>
    <my_service>
      <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
      <jwks_refresh_timeout>300000</jwks_refresh_timeout>
      <!-- Optional: claims / verifier_leeway -->
    </my_service>
  </token_processors>
</clickhouse>
```

**Sign JWT Tokens with Private Key:**

Your token issuer must:

* Sign with the matching private key (e.g., RS256)
* Include the same `kid` in the JWT header as in your JWKS entry
* (Optional) Include any claims you plan to enforce via ClickHouse's claims check

**Important Notes:**

* `kid` must match the `kid` you'll put in the JWT header when you sign tokens
* `n` and `e` are the RSA public key params, base64url-encoded
* You can generate that JSON with a tiny script using cryptography/pyjwt, or any JWK tool
* The specifics aren't ClickHouse-specific; ClickHouse only needs the public JWKS
* `jwks_uri`, `jwks_refresh_timeout`, `claims`, and `verifier_leeway` are exactly the supported params

### Remote JWKS Configuration Parameters

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksUri
version: 1.0

[ClickHouse] SHALL support the `jwks_uri` parameter to specify the JWKS endpoint URI. This parameter SHALL be mandatory and SHALL point to a valid JWKS endpoint.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>300000</jwks_refresh_timeout>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

**Common JWKS endpoint patterns:**
* `https://auth.example.com/.well-known/jwks.json`
* `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys`
* `https://keycloak.example.com/realms/{realm}/protocol/openid-connect/certs`

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.JwksRefreshTimeout
version: 1.0

[ClickHouse] SHALL support the `jwks_refresh_timeout` parameter to specify the period for resending requests to refresh the JWKS. This parameter SHALL be optional with a default value of 300000 milliseconds.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>600000</jwks_refresh_timeout>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, the JWKS will be refreshed every 10 minutes (600,000 milliseconds) instead of the default 5 minutes.

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.Claims
version: 1.0

[ClickHouse] SHALL support the `claims` parameter as a string containing a JSON object that should be contained in the token payload. If this parameter is defined, tokens without corresponding payload SHALL be considered invalid. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <claims>{"iss": "https://auth.example.com", "aud": "clickhouse-app", "azp": "clickhouse-client"}</claims>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, tokens must contain the specified `iss` (issuer), `aud` (audience), and `azp` (authorized party) claims to be considered valid.

#### RQ.SRS-042.OAuth.RemoteJWKS.Parameters.VerifierLeeway
version: 1.0

[ClickHouse] SHALL support the `verifier_leeway` parameter to specify clock skew tolerance in seconds. This parameter SHALL be useful for handling small differences in system clocks between ClickHouse and the token issuer. This parameter SHALL be optional.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_remote_jwks_validator>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <verifier_leeway>60</verifier_leeway>
        </my_remote_jwks_validator>
    </token_processors>
</clickhouse>
```

In this example, a 60-second clock skew tolerance is allowed, providing more flexibility for environments with larger clock synchronization issues.

### Remote JWKS Configuration Validation

#### RQ.SRS-042.OAuth.RemoteJWKS.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate remote JWKS configuration as follows:

* `jwks_uri` parameter SHALL be mandatory and SHALL contain a valid URI
* The URI SHALL be accessible and return valid JWKS content
* If `jwks_refresh_timeout` is specified, it SHALL be a positive integer value
* [ClickHouse] SHALL validate the JWKS content format when fetched from the URI

**Valid Configuration Examples:**

**Basic configuration:**
```xml
<clickhouse>
    <token_processors>
        <valid_remote_jwks>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
        </valid_remote_jwks>
    </token_processors>
</clickhouse>
```

**With all optional parameters:**
```xml
<clickhouse>
    <token_processors>
        <complete_remote_jwks>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>600000</jwks_refresh_timeout>
            <claims>{"iss": "https://auth.example.com"}</claims>
            <verifier_leeway>30</verifier_leeway>
        </complete_remote_jwks>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**Missing jwks_uri:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <!-- Missing jwks_uri - will be rejected -->
            <jwks_refresh_timeout>300000</jwks_refresh_timeout>
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

**Invalid jwks_uri:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <jwks_uri>not-a-valid-uri</jwks_uri>
            <!-- Invalid URI format - will be rejected -->
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

**Negative refresh timeout:**
```xml
<clickhouse>
    <token_processors>
        <invalid_remote_jwks>
            <jwks_uri>https://auth.example.com/.well-known/jwks.json</jwks_uri>
            <jwks_refresh_timeout>-1000</jwks_refresh_timeout>
            <!-- Negative value - will be rejected -->
        </invalid_remote_jwks>
    </token_processors>
</clickhouse>
```

### Remote JWKS Network Handling

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Timeout
version: 1.0

[ClickHouse] SHALL implement appropriate network timeouts when fetching JWKS from remote endpoints to prevent hanging requests.

**Example timeout scenarios:**
* Connection timeout: 10 seconds
* Read timeout: 30 seconds
* Total request timeout: 60 seconds

**Behavior:**
* If a JWKS fetch exceeds the timeout, [ClickHouse] SHALL log an error and continue using cached JWKS if available
* If no cached JWKS is available, authentication SHALL be rejected until the endpoint becomes accessible

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Retry
version: 1.0

[ClickHouse] SHALL implement retry logic for failed JWKS fetch attempts with exponential backoff to handle temporary network issues.

**Retry behavior:**
* Initial retry delay: 1 second
* Maximum retry delay: 60 seconds
* Maximum retry attempts: 3
* Exponential backoff: delay = min(initial_delay * 2^attempt, max_delay)

**Example retry sequence:**
1. First attempt fails → wait 1 second
2. Second attempt fails → wait 2 seconds  
3. Third attempt fails → wait 4 seconds
4. If all attempts fail, use cached JWKS or reject authentication

#### RQ.SRS-042.OAuth.RemoteJWKS.Network.Cache
version: 1.0

[ClickHouse] SHALL cache the fetched JWKS content for the duration specified by `jwks_refresh_timeout` to reduce network requests and improve performance.

**Caching behavior:**
* JWKS content SHALL be cached for the duration of `jwks_refresh_timeout`
* Cache SHALL be shared across all token validation requests
* Cache SHALL be refreshed in the background when the timeout expires
* If refresh fails, the old cached content SHALL continue to be used

**Example caching timeline:**
```
Time 0: Fetch JWKS from https://auth.example.com/.well-known/jwks.json
Time 0-300s: Use cached JWKS for all token validations
Time 300s: Background refresh attempt
Time 300s+: Use updated JWKS if refresh succeeded, or continue with old cache if failed
```

### Remote JWKS Error Handling

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.NetworkFailure
version: 1.0

[ClickHouse] SHALL handle network failures when fetching JWKS gracefully. If the JWKS endpoint is unreachable, [ClickHouse] SHALL use cached JWKS if available, or reject authentication if no cached JWKS exists.

**Network failure scenarios:**
* DNS resolution failure
* Connection timeout
* HTTP 5xx server errors
* Network connectivity issues

**Example behavior:**
```
Scenario: JWKS endpoint https://auth.example.com/.well-known/jwks.json is down

1. First token validation: Use cached JWKS (if available)
2. Subsequent validations: Continue using cached JWKS
3. Background refresh attempts: Fail silently, keep using cache
4. If no cache exists: Reject all authentication attempts
5. When endpoint recovers: Resume normal operation
```

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.InvalidResponse
version: 1.0

[ClickHouse] SHALL reject authentication attempts if the remote JWKS endpoint returns invalid or malformed JSON content.

**Invalid response scenarios:**
* Non-JSON content (HTML error pages, plain text)
* Malformed JSON syntax
* Missing required JWKS fields (`keys` array)
* Invalid key format within JWKS

**Example invalid responses:**

**HTML error page:**
```html
<!DOCTYPE html>
<html>
<head><title>500 Internal Server Error</title></head>
<body>Internal Server Error</body>
</html>
```

**Malformed JSON:**

```json
{
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "kid": "my-key",
            "n": "modulus",
            "e": "AQAB"
        }
    ]
```

Closing brace is missing, making it invalid JSON.

**Missing keys array:**
```json
{
    "error": "not_found",
    "error_description": "JWKS not available"
}
```

**Behavior:**
* [ClickHouse] SHALL log the invalid response for debugging
* Authentication SHALL be rejected for all tokens
* Cached JWKS SHALL not be used if the current response is invalid

#### RQ.SRS-042.OAuth.RemoteJWKS.ErrorHandling.ExpiredCache
version: 1.0

[ClickHouse] SHALL attempt to refresh the JWKS cache when it expires. If the refresh fails, [ClickHouse] SHALL continue using the expired cache for a limited time before rejecting authentication.

**Cache expiration behavior:**
* When cache expires, [ClickHouse] SHALL attempt to fetch fresh JWKS
* If fetch succeeds: Use new JWKS immediately
* If fetch fails: Continue using expired cache for up to 24 hours
* After 24 hours of failed refreshes: Reject all authentication attempts

**Example timeline:**
```
Time 0: JWKS cached successfully
Time 300s: Cache expires, refresh attempt fails
Time 300s-86400s: Use expired cache, continue refresh attempts
Time 86400s+: Reject authentication if refresh still fails
```

**Graceful degradation:**
* This allows for temporary network issues without immediate service disruption
* Provides time for administrators to resolve connectivity problems
* Prevents indefinite use of potentially outdated keys

## Token Processor

### Common Configuration Parameters

#### RQ.SRS-042.OAuth.Common.Parameters.CacheLifetime
version: 1.0

[ClickHouse] SHALL support the `cache_lifetime` parameter for all token processor types. This parameter SHALL specify the maximum lifetime of cached tokens in seconds. This parameter SHALL be optional with a default value of 3600 seconds.

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <provider>azure</provider>
            <client_id>my-client-id</client_id>
            <tenant_id>my-tenant-id</tenant_id>
            <cache_lifetime>1800</cache_lifetime>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, tokens will be cached for 30 minutes (1800 seconds) instead of the default 1 hour.

#### RQ.SRS-042.OAuth.Common.Parameters.UsernameClaim
version: 1.0

[ClickHouse] SHALL support the `username_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that will be treated as the ClickHouse username. This parameter SHALL be optional with a default value of "sub".

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <provider>azure</provider>
            <client_id>my-client-id</client_id>
            <tenant_id>my-tenant-id</tenant_id>
            <username_claim>preferred_username</username_claim>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, the `preferred_username` claim from the token will be used as the ClickHouse username instead of the default `sub` claim.

**Common username claim values:**
* `sub` (default) - Subject identifier
* `preferred_username` - User's preferred username
* `email` - User's email address
* `upn` - User Principal Name (Azure AD)
* `name` - User's display name

#### RQ.SRS-042.OAuth.Common.Parameters.GroupsClaim
version: 1.0

[ClickHouse] SHALL support the `groups_claim` parameter for all token processor types. This parameter SHALL specify the name of the claim (field) that contains the list of groups the user belongs to. This claim SHALL be looked up in the token itself (for valid JWTs) or in the response from `/userinfo` (for opaque tokens). This parameter SHALL be optional with a default value of "groups".

**Example:**
```xml
<clickhouse>
    <token_processors>
        <my_token_processor>
            <provider>azure</provider>
            <client_id>my-client-id</client_id>
            <tenant_id>my-tenant-id</tenant_id>
            <groups_claim>roles</groups_claim>
        </my_token_processor>
    </token_processors>
</clickhouse>
```

In this example, the `roles` claim from the token will be used to determine user groups instead of the default `groups` claim.

**Common groups claim values:**
* `groups` (default) - Standard groups claim
* `roles` - User roles
* `app_roles` - Application-specific roles
* `resource_access` - Resource access permissions
* `wids` - Windows Identity Foundation claims (Azure AD)

#### RQ.SRS-042.OAuth.Common.Parameters.Unfiltered
version: 1.0

[ClickHouse] SHALL reject a configuration inside `token_processors` that contains all possible parameters.

For example,

```xml
<clickhouse>
    <token_processors>
        <madness>
          <algo>HS256</algo>
          <static_key>my_static_secret</static_key>
          <static_jwks>{"keys": [{"kty": "RSA", "alg": "RS256", "kid": "mykid", "n": "_public_key_mod_", "e": "AQAB"}]}</static_jwks>
          <jwks_uri>http://localhost:8000/.well-known/jwks.json</jwks_uri>
          <jwks_refresh_timeout>300000</jwks_refresh_timeout>
          <provider>openid</provider>
          <cache_lifetime>600</cache_lifetime>
          <username_claim>sub</username_claim>
          <groups_claim>groups</groups_claim>
          <configuration_endpoint></configuration_endpoint>
          <userinfo_endpoint></userinfo_endpoint>
          <token_introspection_endpoint></token_introspection_endpoint>
        </madness>
    </token_processors>
</clickhouse>
```

### Token Cache Behavior

#### RQ.SRS-042.OAuth.Common.Cache.Behavior
version: 1.0

[ClickHouse] SHALL implement token caching behavior as follows:

* Tokens SHALL be cached internally for no longer than `cache_lifetime` seconds
* If a token expires sooner than `cache_lifetime`, the cache entry SHALL only be valid while the token is valid
* If a token lifetime is longer than `cache_lifetime`, the cache entry SHALL be valid for `cache_lifetime`
* Caching SHALL reduce the number of requests to Identity Providers

**Example caching scenarios:**

**Scenario 1: Token expires before cache_lifetime**
```
Token expiration: 30 minutes
Cache lifetime: 60 minutes
Result: Token cached for 30 minutes (until token expires)
```

**Scenario 2: Token expires after cache_lifetime**
```
Token expiration: 120 minutes
Cache lifetime: 60 minutes
Result: Token cached for 60 minutes (cache_lifetime limit)
```

**Scenario 3: Cache disabled**
```
Cache lifetime: 0
Result: No caching, validate token on every request
```

**Configuration example:**
```xml
<clickhouse>
    <token_processors>
        <my_processor>
            <provider>azure</provider>
            <client_id>my-client-id</client_id>
            <tenant_id>my-tenant-id</tenant_id>
            <cache_lifetime>1800</cache_lifetime>
        </my_processor>
    </token_processors>
</clickhouse>
```

**Cache behavior timeline:**
```
Time 0: Token received and validated
Time 0-1800s: Token cached, no validation requests to IdP
Time 1800s: Cache expires, next request triggers validation
Time 1800s+: New token cached for next 1800 seconds
```

### Configuration Validation

#### RQ.SRS-042.OAuth.Common.Configuration.Validation
version: 1.0

[ClickHouse] SHALL validate token processor configurations as follows:

* At least one token processor SHALL be defined in the `token_processors` section
* Each token processor SHALL have a unique identifier
* Required parameters for each processor type SHALL be present and valid
* [ClickHouse] SHALL reject invalid configurations and log appropriate error messages

**Valid Configuration Examples:**

**Multiple token processors:**
```xml
<clickhouse>
    <token_processors>
        <azure_processor>
            <provider>azure</provider>
            <client_id>azure-client-id</client_id>
            <tenant_id>azure-tenant-id</tenant_id>
        </azure_processor>
        <keycloak_processor>
            <provider>openid</provider>
            <userinfo_endpoint>https://keycloak.example.com/userinfo</userinfo_endpoint>
            <token_introspection_endpoint>https://keycloak.example.com/introspect</token_introspection_endpoint>
        </keycloak_processor>
        <static_key_processor>
            <algo>HS256</algo>
            <static_key>my-secret-key</static_key>
        </static_key_processor>
    </token_processors>
</clickhouse>
```

**Invalid Configuration Examples:**

**No token processors defined:**
```xml
<clickhouse>
    <token_processors>
        <!-- Empty section - will be rejected -->
    </token_processors>
</clickhouse>
```

**Duplicate processor identifiers:**
```xml
<clickhouse>
    <token_processors>
        <my_processor>
            <provider>azure</provider>
            <client_id>client1</client_id>
            <tenant_id>tenant1</tenant_id>
        </my_processor>
        <my_processor>
            <provider>azure</provider>
            <client_id>client2</client_id>
            <tenant_id>tenant2</tenant_id>
            <!-- Duplicate identifier - will be rejected -->
        </my_processor>
    </token_processors>
</clickhouse>
```

**Missing required parameters:**
```xml
<clickhouse>
    <token_processors>
        <invalid_azure_processor>
            <provider>azure</provider>
            <!-- Missing client_id and tenant_id - will be rejected -->
        </invalid_azure_processor>
    </token_processors>
</clickhouse>
```

**Error handling:**
* [ClickHouse] SHALL log detailed error messages for configuration validation failures
* [ClickHouse] SHALL refuse to start if any token processor configuration is invalid
* Error messages SHALL include the specific parameter and reason for validation failure

## ClickHouse Actions After Token Validation

### Incorrect Requests to ClickHouse

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests
version: 1.0

When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header
version: 1.0

[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body
version: 1.0

[ClickHouse] SHALL reject requests that include incorrect or malformed body content.

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

#### RQ.SRS-042.OAuth.Grafana.Authentication.IncorrectRequests.Body.Exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.

### Token Handling

#### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Expired
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].

#### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.Incorrect
version: 1.0

[ClickHouse] SHALL reject JWT tokens that are malformed, have an invalid signature, or do not conform to the expected structure.

#### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.NonAlphaNumeric
version: 1.0

[ClickHouse] SHALL reject JWT tokens that contain non-alphanumeric characters in the header or payload sections, as these are not valid according to the JWT specification.

#### RQ.SRS-042.OAuth.Grafana.Authentication.TokenHandling.EmptyString
version: 1.0

[ClickHouse] SHALL reject empty string values in the Authorization header or any other part of the request that expects a JWT token. An empty string is not a valid JWT and SHALL not be accepted.

### Caching

#### RQ.SRS-042.OAuth.Grafana.Authentication.Caching
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

#### Disable Caching

##### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.NoCache
version: 1.0

If the value of `cache_lifetime` is `0` in the `token_processors` configuration, [ClickHouse] SHALL not cache the tokens and SHALL validate each token on every request.

#### Cache Lifetime

##### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.CacheLifetime
version: 1.0

[ClickHouse] SHALL evict cached tokens after the `cache_lifetime` period defined in the `token_processors` configuration. If the cache was evicted, [ClickHouse] SHALL cache the new token provided by [Grafana] for the next requests.

#### Exceeding Max Cache Size

##### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.MaxCacheSize
version: 1.0

[ClickHouse] SHALL limit the maximum size of the cache for access tokens. If the cache exceeds this size, [ClickHouse] SHALL evict the oldest tokens to make room for new ones.

#### Cache Eviction Policy

##### RQ.SRS-042.OAuth.Grafana.Authentication.Caching.CacheEviction.Policy
version: 1.0

[ClickHouse] SHALL use the Least Recently Used (LRU) cache eviction policy for access tokens. This means that when the cache reaches its maximum size, the least recently used tokens SHALL be removed to make space for new tokens.

### Authentication and Login

#### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via `HTTP` or `TCP` connection.

For example,

```bash
curl 'http://localhost:8080/?' Client
 -H 'Authorization: Bearer <TOKEN>' Client
 -H 'Content type: text/plain;charset=UTF-8' Client
 --data-raw 'SELECT current_user()'
```

#### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.Authentication.Client
version: 1.0

[ClickHouse] SHALL allow a [ClickHouse] user to log in directly using an `OAuth` access token via the `clickhouse client --jwt <token>` command.

### Session Management

#### RQ.SRS-042.OAuth.Grafana.Authentication.Actions.SessionManagement
version: 1.0

[ClickHouse] SHALL manage user sessions based on the validity of the access token. If the token is valid, the session SHALL remain active. If the token is invalid or expired, the session SHALL be terminated, and the user SHALL be required to log in again with a new token.

[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
[Keycloak]: https://www.keycloak.org
[Azure]: https://azure.microsoft.com
""",
)
