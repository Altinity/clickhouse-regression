# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_042_OAuth_Azure_AccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Azure.AccessTokenProcessors",
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
    level=3,
    num="6.1.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Grafana] SHALL redirect users to the Azure AD authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.\n"
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
    num="7.1.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_SameName = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user has permission to view groups in Azure and [ClickHouse] has roles with the same names, [ClickHouse] SHALL map the user's Azure group membership to the corresponding [ClickHouse] roles.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.1.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoMatchingRoles = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user has permission to view groups in Azure but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.2.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoPermissionToViewGroups = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user does not have permission to view their groups in Azure, [ClickHouse] SHALL assign a default role to the user.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="7.2.3.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoDefaultRole = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole",
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
    num="7.2.4.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoAccessTokenProcessors = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoAccessTokenProcessors",
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
    num="7.2.5.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The user SHALL not receive a valid JWT token if the provided credentials are incorrect. In this case, [ClickHouse] SHALL return an HTTP 401 Unauthorized response to [Grafana].\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_MissingSecret = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The user SHALL not receive a valid JWT token if the `CLIENT_SECRET` is missing from the HTTP request.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.2",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_EmptyString = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The user SHALL not receive a valid JWT token if the provided credentials are an empty string.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.3",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_Null = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The user SHALL not receive a valid JWT token if the provided credentials are null.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.4",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_NonAlphanumericCharacters = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The user SHALL not receive a valid JWT token if the provided credentials contain non-alphanumeric characters such as emojis.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.5",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[Grafana] SHALL support forwarding the same `JWT` token used to authenticate a user in [Grafana] to [ClickHouse] when making requests to the [ClickHouse] data source. This behavior SHALL be configurable by enabling the `Forward OAuth Identity` option in the [Grafana] data source settings.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.4.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_Enabled = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.4.2",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_Disabled = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the `Forward OAuth Identity` option is disabled in [Grafana], [Grafana] SHALL NOT forward the user's JWT token to ClickHouse.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.4.3",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests",
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
    num="7.4.4.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header",
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
    num="7.4.4.2",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Alg = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Alg",
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
    num="7.4.4.3",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Typ = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Typ",
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
    num="7.4.4.4",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Signature = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature",
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
    num="7.4.4.5",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body",
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
    num="7.4.4.6",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Sub = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Sub",
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
    num="7.4.4.7",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Aud = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Aud",
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
    num="7.4.4.8",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Exp = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Exp",
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
    num="7.4.4.9",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ExpiredTokenHandling = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling",
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
    level=4,
    num="7.4.5.1",
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
        Heading(name="Azure", level=1, num="6"),
        Heading(name="Access Token Processors For Azure", level=2, num="6.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Azure.AccessTokenProcessors", level=3, num="6.1.1"
        ),
        Heading(
            name="Logging into ClickHouse from Grafana Using Azure ", level=1, num="7"
        ),
        Heading(name="Authentication", level=2, num="7.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication", level=3, num="7.1.1"
        ),
        Heading(name="User Role Mapping", level=2, num="7.2"),
        Heading(
            name="User Has Permission To View Groups in Azure and ClickHouse Has Roles With the Same Group Names",
            level=3,
            num="7.2.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName",
            level=4,
            num="7.2.1.1",
        ),
        Heading(
            name="User Can View Groups in Azure but There Are No Matching Roles in ClickHouse",
            level=3,
            num="7.2.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles",
            level=4,
            num="7.2.2.1",
        ),
        Heading(
            name="User Does Not Have Permission To View Their Groups in Azure",
            level=3,
            num="7.2.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups",
            level=4,
            num="7.2.3.1",
        ),
        Heading(
            name="In ClickHouse There Is No Default Role Specified",
            level=3,
            num="7.2.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole",
            level=4,
            num="7.2.4.1",
        ),
        Heading(
            name="Access Token Processors are Missing From ClickHouse Configuration ",
            level=3,
            num="7.2.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoAccessTokenProcessors",
            level=4,
            num="7.2.5.1",
        ),
        Heading(name="Invalid Credentials When Requesting a JWT", level=2, num="7.3"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials",
            level=3,
            num="7.3.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret",
            level=3,
            num="7.3.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString",
            level=3,
            num="7.3.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null",
            level=3,
            num="7.3.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters",
            level=3,
            num="7.3.5",
        ),
        Heading(name="Accessing ClickHouse from Grafana", level=2, num="7.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity",
            level=3,
            num="7.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled",
            level=3,
            num="7.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled",
            level=3,
            num="7.4.3",
        ),
        Heading(name="Incorrect Requests to ClickHouse", level=3, num="7.4.4"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests",
            level=4,
            num="7.4.4.1",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header",
            level=4,
            num="7.4.4.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Alg",
            level=4,
            num="7.4.4.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Typ",
            level=4,
            num="7.4.4.4",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature",
            level=4,
            num="7.4.4.5",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body",
            level=4,
            num="7.4.4.6",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Sub",
            level=4,
            num="7.4.4.7",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Aud",
            level=4,
            num="7.4.4.8",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Exp",
            level=4,
            num="7.4.4.9",
        ),
        Heading(name="Expired Token Handling", level=3, num="7.4.5"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling",
            level=4,
            num="7.4.5.1",
        ),
    ),
    requirements=(
        RQ_SRS_042_OAuth_Azure_AccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_SameName,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoMatchingRoles,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoPermissionToViewGroups,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoDefaultRole,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_UserRoleMapping_NoAccessTokenProcessors,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_MissingSecret,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_EmptyString,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_Null,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_InvalidCredentials_NonAlphanumericCharacters,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_Enabled,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_Disabled,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Alg,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Typ,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Header_Signature,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Sub,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Aud,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ClickHouse_ForwardOAuthIdentity_IncorrectRequests_Body_Exp,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ExpiredTokenHandling,
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
* 6 [Azure](#azure)
    * 6.1 [Access Token Processors For Azure](#access-token-processors-for-azure)
        * 6.1.1 [RQ.SRS-042.OAuth.Azure.AccessTokenProcessors](#rqsrs-042oauthazureaccesstokenprocessors)
* 7 [Logging into ClickHouse from Grafana Using Azure ](#logging-into-clickhouse-from-grafana-using-azure-)
    * 7.1 [Authentication](#authentication)
        * 7.1.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication](#rqsrs-042oauthgrafanaazureauthentication)
    * 7.2 [User Role Mapping](#user-role-mapping)
        * 7.2.1 [User Has Permission To View Groups in Azure and ClickHouse Has Roles With the Same Group Names](#user-has-permission-to-view-groups-in-azure-and-clickhouse-has-roles-with-the-same-group-names)
            * 7.2.1.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingsamename)
        * 7.2.2 [User Can View Groups in Azure but There Are No Matching Roles in ClickHouse](#user-can-view-groups-in-azure-but-there-are-no-matching-roles-in-clickhouse)
            * 7.2.2.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnomatchingroles)
        * 7.2.3 [User Does Not Have Permission To View Their Groups in Azure](#user-does-not-have-permission-to-view-their-groups-in-azure)
            * 7.2.3.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnopermissiontoviewgroups)
        * 7.2.4 [In ClickHouse There Is No Default Role Specified](#in-clickhouse-there-is-no-default-role-specified)
            * 7.2.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnodefaultrole)
        * 7.2.5 [Access Token Processors are Missing From ClickHouse Configuration ](#access-token-processors-are-missing-from-clickhouse-configuration-)
            * 7.2.5.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoAccessTokenProcessors](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnoaccesstokenprocessors)
    * 7.3 [Invalid Credentials When Requesting a JWT](#invalid-credentials-when-requesting-a-jwt)
        * 7.3.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentials)
        * 7.3.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsmissingsecret)
        * 7.3.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsemptystring)
        * 7.3.4 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsnull)
        * 7.3.5 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsnonalphanumericcharacters)
    * 7.4 [Accessing ClickHouse from Grafana](#accessing-clickhouse-from-grafana)
        * 7.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentity)
        * 7.4.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityenabled)
        * 7.4.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentitydisabled)
        * 7.4.4 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
            * 7.4.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequests)
            * 7.4.4.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheader)
            * 7.4.4.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Alg](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheaderalg)
            * 7.4.4.4 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Typ](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheadertyp)
            * 7.4.4.5 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheadersignature)
            * 7.4.4.6 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbody)
            * 7.4.4.7 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Sub](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodysub)
            * 7.4.4.8 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Aud](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodyaud)
            * 7.4.4.9 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Exp](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodyexp)
        * 7.4.5 [Expired Token Handling](#expired-token-handling)
            * 7.4.5.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling](#rqsrs-042oauthgrafanaazureauthenticationexpiredtokenhandling)

    
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
<token>
    <processor>azure_ad</processor>
    <roles>
        <read_only_role />
    </roles>
</token>
```

## Authentication with OAuth

To authenticate with OAuth, users must obtain an access token from the identity provider and present it to [ClickHouse].

## Supported Identity Providers

[ClickHouse] SHALL support OAuth 2.0 authentication with various identity providers, including but not limited to:

- Azure Active Directory
- Google Identity

## Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with Azure Active Directory (Azure AD) as an identity provider.

### Access Token Processors For Azure

#### RQ.SRS-042.OAuth.Azure.AccessTokenProcessors
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

## Logging into ClickHouse from Grafana Using Azure 

### Authentication

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication
version: 1.0

[Grafana] SHALL redirect users to the Azure AD authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>\nTENANT_ID=<Tenant ID>\nCLIENT_SECRET=<Client Secret>\n" > .env
```

### User Role Mapping

#### User Has Permission To View Groups in Azure and ClickHouse Has Roles With the Same Group Names

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName
version: 1.0

When a user has permission to view groups in Azure and [ClickHouse] has roles with the same names, [ClickHouse] SHALL map the user's Azure group membership to the corresponding [ClickHouse] roles.

#### User Can View Groups in Azure but There Are No Matching Roles in ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Azure but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

#### User Does Not Have Permission To View Their Groups in Azure

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Azure, [ClickHouse] SHALL assign a default role to the user.

#### In ClickHouse There Is No Default Role Specified

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole
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

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoAccessTokenProcessors
version: 1.0

When there are no access token processors defined in [ClickHouse] configuration, [ClickHouse] SHALL not allow the grafana user to authenticate and access resources.

### Invalid Credentials When Requesting a JWT

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are incorrect. In this case, [ClickHouse] SHALL return an HTTP 401 Unauthorized response to [Grafana].

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret
version: 1.0

The user SHALL not receive a valid JWT token if the `CLIENT_SECRET` is missing from the HTTP request.

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are an empty string.

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are null.

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials contain non-alphanumeric characters such as emojis.

### Accessing ClickHouse from Grafana

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity
version: 1.0

[Grafana] SHALL support forwarding the same `JWT` token used to authenticate a user in [Grafana] to [ClickHouse] when making requests to the [ClickHouse] data source. This behavior SHALL be configurable by enabling the `Forward OAuth Identity` option in the [Grafana] data source settings.

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

#### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled
version: 1.0

When the `Forward OAuth Identity` option is disabled in [Grafana], [Grafana] SHALL NOT forward the user's JWT token to ClickHouse.

#### Incorrect Requests to ClickHouse

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests
version: 1.0

When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header
version: 1.0

[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body
version: 1.0

[ClickHouse] SHALL reject requests that include incorrect or malformed body content.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.Exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.

#### Expired Token Handling

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].


[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
""",
)
