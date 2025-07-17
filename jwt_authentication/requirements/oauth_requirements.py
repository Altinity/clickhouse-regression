# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.240708.1162538.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_042_OAuth_Grafana_Azure_Authentication = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL redirect users to the Azure AD authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.\n"
        "\n"
        "The values SHALL be stored inside the `.env` file which can be generated as:\n"
        "\n"
        "```bash\n"
        'printf "CLIENT_ID=<Client ID (Application ID)>\\nTENANT_ID=<Tenant ID>\\nCLIENT_SECRET=<Client Secret>\\n" > .env\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="6.1.1.1",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity",
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
    level=4,
    num="6.1.1.2",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity_Enabled = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Enabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to ClickHouse. The token SHALL be used by ClickHouse to validate the user's identity and permissions.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="6.1.1.3",
)

RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity_Disabled = Requirement(
    name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Disabled",
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
    level=4,
    num="6.1.1.4",
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
        "[ClickHouse]: https://clickhouse.com\n"
        "[Grafana]: https://grafana.com\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="6.1.2.1",
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
        Heading(name="Grafana Integration Support", level=2, num="6.1"),
        Heading(name="Authentication", level=3, num="6.1.1"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication", level=4, num="6.1.1.1"
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity",
            level=4,
            num="6.1.1.2",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Enabled",
            level=4,
            num="6.1.1.3",
        ),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Disabled",
            level=4,
            num="6.1.1.4",
        ),
        Heading(name="Expired Token Handling", level=3, num="6.1.2"),
        Heading(
            name="RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling",
            level=4,
            num="6.1.2.1",
        ),
    ),
    requirements=(
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity_Enabled,
        RQ_SRS_042_OAuth_Grafana_Azure_Authentication_ForwardOAuthIdentity_Disabled,
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
    * 6.1 [Grafana Integration Support](#grafana-integration-support)
        * 6.1.1 [Authentication](#authentication)
            * 6.1.1.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication](#rqsrs-042oauthgrafanaazureauthentication)
            * 6.1.1.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaazureauthenticationforwardoauthidentity)
            * 6.1.1.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Enabled](#rqsrs-042oauthgrafanaazureauthenticationforwardoauthidentityenabled)
            * 6.1.1.4 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Disabled](#rqsrs-042oauthgrafanaazureauthenticationforwardoauthidentitydisabled)
        * 6.1.2 [Expired Token Handling](#expired-token-handling)
            * 6.1.2.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling](#rqsrs-042oauthgrafanaazureauthenticationexpiredtokenhandling)

    
## Introduction

This Software Requirements Specification (SRS) defines the requirements for OAuth 2.0 authentication support in ClickHouse.

OAuth 2.0 is an industry-standard authorization framework (defined in [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)) that enables third-party applications to obtain limited access to an HTTP service, either on behalf of a user or using application credentials. It decouples authentication from authorization, allowing for more secure and flexible access control mechanisms.

Integrating OAuth 2.0 in ClickHouse allows the system to delegate user authentication to trusted external identity providers (such as Google, Microsoft, or Okta), streamlining user management and enhancing security.

Through OAuth 2.0, ClickHouse can accept access tokens issued by an identity provider and validate them using static or dynamic JSON Web Key Sets (JWKS). The access token—typically a JWT—includes user identity and scope information that ClickHouse can use to authorize requests to resources.

This approach supports a wide range of identity federation use cases and enables ClickHouse to function within modern enterprise authentication ecosystems.

### Structure of OAuth

OAuth 2.0 defines several roles and token types used in the process of authorizing access to protected resources:

  * **Resource Owner:** The user or system that owns the data or resource.

  * **Client:** The application requesting access on behalf of the resource owner.
  * **Authorization Server:** The server that authenticates the resource owner and issues access tokens to the client.

  * **Resource Server:** The server (e.g., ClickHouse) that hosts the protected resources and verifies access tokens.

OAuth 2.0 typically issues two types of tokens:

  * **Access Token:** A short-lived token used by the client to access protected resources. In many implementations, the access token is a JWT that encodes user identity and scopes (permissions).

  * **Refresh Token:** An optional long-lived token used to obtain new access tokens without re-authenticating the user.

## Definitions

- **Identity Provider (IdP):** A service that issues access tokens after authenticating users. Examples include Azure Active Directory, Google Identity, and Okta.
- **Access Token:** A token issued by an IdP that grants access to protected resources. It is often a JSON Web Token (JWT) containing user identity and permissions.
- **[JWT (JSON Web Token)](https://github.com/Altinity/clickhouse-regression/blob/main/jwt_authentication/requirements/requirements.md):** A compact, URL-safe means of representing claims to be transferred between two parties. It is used in OAuth 2.0 for access tokens.

## Overview of the Functionality

To enable OAuth 2.0 authentication in ClickHouse, one must define Access Token Processors, which allow ClickHouse to validate and trust OAuth 2.0 access tokens issued by external Identity Providers (IdPs), such as Azure AD.

OAuth-based authentication works by allowing users to authenticate using an access token (often a JWT) issued by the IdP. ClickHouse supports two modes of operation with these tokens:

**Locally Defined Users:** If a user is already defined in ClickHouse (via users.xml or SQL), their authentication method can be set to jwt, enabling token-based authentication.

**Externally Defined Users:** If a user is not defined locally, ClickHouse can still authenticate them by validating the token and retrieving user information from the Identity Provider. If valid, the user is granted access with predefined roles.

All OAuth 2.0 access tokens must be validated through one of the configured `access_token_processors` in `config.xml`.

### Access Token Processors

An Access Token Processor defines how ClickHouse validates and interprets access tokens from a specific identity provider. This includes verifying the token’s issuer, audience, and cryptographic signature.

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

Key Parameters:

- **provider:** Specifies the identity provider (for example, `azure`).

- **cache_lifetime:** maximum lifetime of cached token (in seconds). Optional, default: 3600

- **client_id:** The registered application ID in Azure.

- **tenant_id:** The Azure tenant that issues the tokens.

### Authentication Modes with OAuth Tokens

1. **Locally Defined Users with JWT Authentication**
Users defined in `users.xml` or `SQL` can authenticate using tokens if `jwt` is specified as their method:

```xml
<users>
    <alice>
        <jwt/>
    </alice>
</users>
```

Or via SQL:

```sql
CREATE USER my_user IDENTIFIED WITH jwt;
```

2. **External Identity Provider as a User Directory**

When a user is not defined locally, ClickHouse can use the `IdP` as a dynamic source of user info. This requires configuring the `<token>` section in `users_directories` and assigning roles:

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

### Grafana Integration Support


#### Authentication

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication
version: 1.0

[ClickHouse] SHALL redirect users to the Azure AD authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>\nTENANT_ID=<Tenant ID>\nCLIENT_SECRET=<Client Secret>\n" > .env
```

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity
version: 1.0

[Grafana] SHALL support forwarding the same `JWT` token used to authenticate a user in [Grafana] to [ClickHouse] when making requests to the [ClickHouse] data source. This behavior SHALL be configurable by enabling the `Forward OAuth Identity` option in the [Grafana] data source settings.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Enabled
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to ClickHouse. The token SHALL be used by ClickHouse to validate the user's identity and permissions.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ForwardOAuthIdentity.Disabled
version: 1.0

When the `Forward OAuth Identity` option is disabled in [Grafana], [Grafana] SHALL NOT forward the user's JWT token to ClickHouse.

#### Expired Token Handling

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].

[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com
""",
)
