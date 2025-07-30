# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

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
        "    <access_token_processors>\n"
        "        <azure_ad>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>your-client-id</client_id>\n"
        "            <tenant_id>your-tenant-id</tenant_id>\n"
        "            <cache_lifetime>3600</cache_lifetime>\n"
        "        </azure_ad>\n"
        "    </access_token_processors>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.1.1.1",
)

RQ_SRS_042_OAuth_IdentityProviders_Concurrent = Requirement(
    name="RQ.SRS-042.OAuth.IdentityProviders.Concurrent",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `access_token_processors` section of `config.xml`.\n"
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
        "[Grafana] SHALL redirect users to the Identity Provider authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.\n"
        "\n"
        "The values SHALL be stored inside the `.env` file which can be generated as:\n"
        "\n"
        "```bash\n"
        'printf "CLIENT_ID=<Client ID (Application ID)>\\nTENANT_ID=<Tenant ID>\\nCLIENT_SECRET=<Client Secret>\\n" > .env\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="6.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_ForwardOAuthIdentity = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.ForwardOAuthIdentity",
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
    num="7.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_UserDirectories = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is not defined locally, [ClickHouse] SHALL use the `IdP` as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.\n"
        "\n"
        "For example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <access_token_processors>\n"
        "        <azuure>\n"
        "            <provider>azure</provider>\n"
        "            <client_id>$CLIENT_ID</client_id>\n"
        "            <tenant_id>$TENANT_ID</tenant_id>\n"
        "        </azuure>\n"
        "    </access_token_processors>\n"
        "    <user_directories>\n"
        "        <token>\n"
        "            <processor>azuure</processor>\n"
        "            <roles>\n"
        "                <token_test_role_1 />\n"
        "            </roles>\n"
        "        </token>\n"
        "    </user_directories>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_UserRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user is authenticated via OAuth, [ClickHouse] SHALL execute queries based on the roles assigned to the user in the `users_directories` section. The roles defined in the `<roles>` section of the `<token>` SHALL determine the permissions granted to the user.\n"
        "\n"
        "PICTURE HERE!\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.1.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SameName = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with the same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.2.1",
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
    level=4,
    num="7.3.3.1",
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
    level=4,
    num="7.3.4.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoDefaultRole = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When there is no default role specified in [ClickHouse] configuration or created via SQL, [ClickHouse] SHALL not allow the user to access any resources and there SHALL be no crashes on [ClickHouse] side.\n"
        "\n"
        "The user configuration example,\n"
        "\n"
        "```xml\n"
        "<clickhouse>\n"
        "    <my_user>\n"
        "        <jwt>\n"
        "        </jwt>\n"
        "    </my_user>\n"
        "</clickhouse>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.3.5.1",
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
    num="7.3.6.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests",
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
    num="7.4.1",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header",
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
    num="7.4.2",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Alg = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Alg",
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
    num="7.4.3",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Typ = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Typ",
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
    num="7.4.4",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Signature = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Signature",
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
    num="7.4.5",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body",
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
    num="7.4.6",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Sub = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Sub",
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
    num="7.4.7",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Aud = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Aud",
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
    num="7.4.8",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Exp = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Exp",
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
    num="7.4.9",
)

RQ_SRS_042_OAuth_Grafana_Authentication_ExpiredTokenHandling = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Authentication.ExpiredTokenHandling",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[Grafana]: https://grafana.com\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.5.1",
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
        Heading(name="Supported Identity Providers", level=1, num="5"),
        Heading(name="Azure", level=2, num="5.1"),
        Heading(name="Access Token Processors For Azure", level=3, num="5.1.1"),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors",
            level=4,
            num="5.1.1.1",
        ),
        Heading(
            name="Number of Identity Providers That Can Be Used Concurrently",
            level=2,
            num="5.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.IdentityProviders.Concurrent", level=3, num="5.2.1"
        ),
        Heading(name="Setting Up OAuth Authentication", level=1, num="6"),
        Heading(name="Credentials", level=2, num="6.1"),
        Heading(name="RQ.SRS-042.OAuth.Credentials", level=3, num="6.1.1"),
        Heading(name="Accessing ClickHouse from Grafana", level=1, num="7"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.ForwardOAuthIdentity",
            level=2,
            num="7.1",
        ),
        Heading(name="User Directories", level=2, num="7.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories",
            level=3,
            num="7.2.1",
        ),
        Heading(name="User Roles", level=2, num="7.3"),
        Heading(name="Query Execution Based on User Roles", level=3, num="7.3.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserRoles",
            level=4,
            num="7.3.1.1",
        ),
        Heading(
            name="User Has Permission To View Groups in Identity Provider and ClickHouse Has Roles With the Same Group Names",
            level=3,
            num="7.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName",
            level=4,
            num="7.3.2.1",
        ),
        Heading(
            name="User Can View Groups in Identity Provider but There Are No Matching Roles in ClickHouse",
            level=3,
            num="7.3.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles",
            level=4,
            num="7.3.3.1",
        ),
        Heading(
            name="User Does Not Have Permission To View Their Groups in Identity Provider",
            level=3,
            num="7.3.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups",
            level=4,
            num="7.3.4.1",
        ),
        Heading(
            name="In ClickHouse There Is No Default Role Specified",
            level=3,
            num="7.3.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole",
            level=4,
            num="7.3.5.1",
        ),
        Heading(
            name="Access Token Processors are Missing From ClickHouse Configuration ",
            level=3,
            num="7.3.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors",
            level=4,
            num="7.3.6.1",
        ),
        Heading(name="Incorrect Requests to ClickHouse", level=2, num="7.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests",
            level=3,
            num="7.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header",
            level=3,
            num="7.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Alg",
            level=3,
            num="7.4.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Typ",
            level=3,
            num="7.4.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Signature",
            level=3,
            num="7.4.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body",
            level=3,
            num="7.4.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Sub",
            level=3,
            num="7.4.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Aud",
            level=3,
            num="7.4.8",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Exp",
            level=3,
            num="7.4.9",
        ),
        Heading(name="Expired Token Handling", level=2, num="7.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Authentication.ExpiredTokenHandling",
            level=3,
            num="7.5.1",
        ),
    ),
    requirements=(
        RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors,
        RQ_SRS_042_OAuth_IdentityProviders_Concurrent,
        RQ_SRS_042_OAuth_Credentials,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_ForwardOAuthIdentity,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_UserDirectories,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_UserRoles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_SameName,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoMatchingRoles,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoPermissionToViewGroups,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoDefaultRole,
        RQ_SRS_042_OAuth_Grafana_Authentication_UserRoles_NoAccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Alg,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Typ,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Header_Signature,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Sub,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Aud,
        RQ_SRS_042_OAuth_Grafana_Authentication_ClickHouse_IncorrectRequests_Body_Exp,
        RQ_SRS_042_OAuth_Grafana_Authentication_ExpiredTokenHandling,
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
* 5 [Supported Identity Providers](#supported-identity-providers)
    * 5.1 [Azure](#azure)
        * 5.1.1 [Access Token Processors For Azure](#access-token-processors-for-azure)
            * 5.1.1.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors](#rqsrs-042oauthidentityprovidersaccesstokenprocessors)
    * 5.2 [Number of Identity Providers That Can Be Used Concurrently](#number-of-identity-providers-that-can-be-used-concurrently)
        * 5.2.1 [RQ.SRS-042.OAuth.IdentityProviders.Concurrent](#rqsrs-042oauthidentityprovidersconcurrent)
* 6 [Setting Up OAuth Authentication](#setting-up-oauth-authentication)
    * 6.1 [Credentials](#credentials)
        * 6.1.1 [RQ.SRS-042.OAuth.Credentials](#rqsrs-042oauthcredentials)
* 7 [Accessing ClickHouse from Grafana](#accessing-clickhouse-from-grafana)
    * 7.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaauthenticationclickhouseforwardoauthidentity)
    * 7.2 [User Directories](#user-directories)
        * 7.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectories)
    * 7.3 [User Roles](#user-roles)
        * 7.3.1 [Query Execution Based on User Roles](#query-execution-based-on-user-roles)
            * 7.3.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserRoles](#rqsrs-042oauthgrafanaauthenticationclickhouseuserroles)
        * 7.3.2 [User Has Permission To View Groups in Identity Provider and ClickHouse Has Roles With the Same Group Names](#user-has-permission-to-view-groups-in-identity-provider-and-clickhouse-has-roles-with-the-same-group-names)
            * 7.3.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName](#rqsrs-042oauthgrafanaauthenticationuserrolessamename)
        * 7.3.3 [User Can View Groups in Identity Provider but There Are No Matching Roles in ClickHouse](#user-can-view-groups-in-identity-provider-but-there-are-no-matching-roles-in-clickhouse)
            * 7.3.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles](#rqsrs-042oauthgrafanaauthenticationuserrolesnomatchingroles)
        * 7.3.4 [User Does Not Have Permission To View Their Groups in Identity Provider](#user-does-not-have-permission-to-view-their-groups-in-identity-provider)
            * 7.3.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups](#rqsrs-042oauthgrafanaauthenticationuserrolesnopermissiontoviewgroups)
        * 7.3.5 [In ClickHouse There Is No Default Role Specified](#in-clickhouse-there-is-no-default-role-specified)
            * 7.3.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole](#rqsrs-042oauthgrafanaauthenticationuserrolesnodefaultrole)
        * 7.3.6 [Access Token Processors are Missing From ClickHouse Configuration ](#access-token-processors-are-missing-from-clickhouse-configuration-)
            * 7.3.6.1 [RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationuserrolesnoaccesstokenprocessors)
    * 7.4 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
        * 7.4.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequests)
        * 7.4.2 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsheader)
        * 7.4.3 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Alg](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsheaderalg)
        * 7.4.4 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Typ](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsheadertyp)
        * 7.4.5 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Signature](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsheadersignature)
        * 7.4.6 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsbody)
        * 7.4.7 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Sub](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsbodysub)
        * 7.4.8 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Aud](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsbodyaud)
        * 7.4.9 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Exp](#rqsrs-042oauthgrafanaauthenticationclickhouseincorrectrequestsbodyexp)
    * 7.5 [Expired Token Handling](#expired-token-handling)
        * 7.5.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ExpiredTokenHandling](#rqsrs-042oauthgrafanaauthenticationexpiredtokenhandling)

    
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

All OAuth 2.0 access tokens must be validated through one of the configured `access_token_processors` in `config.xml`.

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

```sql
CREATE USER my_user IDENTIFIED WITH jwt;
```

2. **External Identity Provider as a User Directory**

When a user is not defined locally, [ClickHouse] can use the `IdP` as a dynamic source of user info. This requires configuring the `<token>` section in `users_directories` and assigning roles:

```xml
<clickhouse>
    <access_token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
            <cache_lifetime>60</cache_lifetime>
        </azuure>
    </access_token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <roles>
                <token_test_role_1 />
            </roles>
        </token>
    </user_directories>
</clickhouse>
```

## Authentication with OAuth

To authenticate with OAuth, users must obtain an access token from the identity provider and present it to [ClickHouse].

## Supported Identity Providers

[ClickHouse] SHALL support OAuth 2.0 authentication with various identity providers, including but not limited to:

- Azure Active Directory
- Google Identity

### Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with Azure Active Directory (Azure AD) as an identity provider.

#### Access Token Processors For Azure

##### RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors
version: 1.0

An Access Token Processor defines how [ClickHouse] validates and interprets access tokens from a specific identity provider. This includes verifying the token’s issuer, audience, and cryptographic signature.

Basic structure:

```xml
<clickhouse>
    <access_token_processors>
        <azure_ad>
            <provider>azure</provider>
            <client_id>your-client-id</client_id>
            <tenant_id>your-tenant-id</tenant_id>
            <cache_lifetime>3600</cache_lifetime>
        </azure_ad>
    </access_token_processors>
</clickhouse>
```

### Number of Identity Providers That Can Be Used Concurrently

#### RQ.SRS-042.OAuth.IdentityProviders.Concurrent
version: 1.0

[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `access_token_processors` section of `config.xml`.

## Setting Up OAuth Authentication

### Credentials

#### RQ.SRS-042.OAuth.Credentials
version: 1.0

[Grafana] SHALL redirect users to the Identity Provider authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>\nTENANT_ID=<Tenant ID>\nCLIENT_SECRET=<Client Secret>\n" > .env
```

## Accessing ClickHouse from Grafana

### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.ForwardOAuthIdentity
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

<img width="1023" height="266" alt="Screenshot from 2025-07-28 16-12-02" src="https://github.com/user-attachments/assets/6c9f38f1-ceaf-480a-8ca4-6599968cbb61" />

### User Directories

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use the `IdP` as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.

For example,

```xml
<clickhouse>
    <access_token_processors>
        <azuure>
            <provider>azure</provider>
            <client_id>$CLIENT_ID</client_id>
            <tenant_id>$TENANT_ID</tenant_id>
        </azuure>
    </access_token_processors>
    <user_directories>
        <token>
            <processor>azuure</processor>
            <roles>
                <token_test_role_1 />
            </roles>
        </token>
    </user_directories>
</clickhouse>
```

### User Roles

#### Query Execution Based on User Roles

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserRoles
version: 1.0

When a user is authenticated via OAuth, [ClickHouse] SHALL execute queries based on the roles assigned to the user in the `users_directories` section. The roles defined in the `<roles>` section of the `<token>` SHALL determine the permissions granted to the user.

PICTURE HERE!

#### User Has Permission To View Groups in Identity Provider and ClickHouse Has Roles With the Same Group Names

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with the same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

#### User Can View Groups in Identity Provider but There Are No Matching Roles in ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Identity Provider but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

#### User Does Not Have Permission To View Their Groups in Identity Provider

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Identity Provider, [ClickHouse] SHALL assign a default role to the user.

#### In ClickHouse There Is No Default Role Specified

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoDefaultRole
version: 1.0

When there is no default role specified in [ClickHouse] configuration or created via SQL, [ClickHouse] SHALL not allow the user to access any resources and there SHALL be no crashes on [ClickHouse] side.

The user configuration example,

```xml
<clickhouse>
    <my_user>
        <jwt>
        </jwt>
    </my_user>
</clickhouse>
```

#### Access Token Processors are Missing From ClickHouse Configuration 

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.NoAccessTokenProcessors
version: 1.0

When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the grafana user to authenticate and access resources.

### Incorrect Requests to ClickHouse

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests
version: 1.0

When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header
version: 1.0

[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body
version: 1.0

[ClickHouse] SHALL reject requests that include incorrect or malformed body content.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.IncorrectRequests.Body.Exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.

### Expired Token Handling

#### RQ.SRS-042.OAuth.Grafana.Authentication.ExpiredTokenHandling
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].


[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
""",
)
