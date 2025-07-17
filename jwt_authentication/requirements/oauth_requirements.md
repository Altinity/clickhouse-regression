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
        * 6.1.2 [User Role Mapping](#user-role-mapping)
            * 6.1.2.1 [User has permission to view groups in Azure and ClickHouse has roles with the same names](#user-has-permission-to-view-groups-in-azure-and-clickhouse-has-roles-with-the-same-names)
                * 6.1.2.1.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingsamename)
            * 6.1.2.2 [User can view groups in Azure but there are no matching roles in ClickHouse](#user-can-view-groups-in-azure-but-there-are-no-matching-roles-in-clickhouse)
                * 6.1.2.2.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnomatchingroles)
            * 6.1.2.3 [User does NOT have permission to view their groups in Azure](#user-does-not-have-permission-to-view-their-groups-in-azure)
                * 6.1.2.3.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnopermissiontoviewgroups)
            * 6.1.2.4 [In ClickHouse there is no default role specified](#in-clickhouse-there-is-no-default-role-specified)
                * 6.1.2.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole](#rqsrs-042oauthgrafanaazureauthenticationuserrolemappingnodefaultrole)
        * 6.1.3 [Invalid Credentials When Requesting a JWT](#invalid-credentials-when-requesting-a-jwt)
            * 6.1.3.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentials)
            * 6.1.3.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsmissingsecret)
            * 6.1.3.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsemptystring)
            * 6.1.3.4 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsnull)
            * 6.1.3.5 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters](#rqsrs-042oauthgrafanaazureauthenticationinvalidcredentialsnonalphanumericcharacters)
        * 6.1.4 [Accessing ClickHouse from Grafana](#accessing-clickhouse-from-grafana)
            * 6.1.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentity)
            * 6.1.4.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityenabled)
            * 6.1.4.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentitydisabled)
            * 6.1.4.4 [Incorrect Requests to ClickHouse](#incorrect-requests-to-clickhouse)
                * 6.1.4.4.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequests)
                * 6.1.4.4.2 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheader)
                * 6.1.4.4.3 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.alg](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheaderalg)
                * 6.1.4.4.4 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.typ](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheadertyp)
                * 6.1.4.4.5 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsheadersignature)
                * 6.1.4.4.6 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbody)
                * 6.1.4.4.7 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.sub](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodysub)
                * 6.1.4.4.8 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.aud](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodyaud)
                * 6.1.4.4.9 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.exp](#rqsrs-042oauthgrafanaazureauthenticationclickhouseforwardoauthidentityincorrectrequestsbodyexp)
            * 6.1.4.5 [Expired Token Handling](#expired-token-handling)
                * 6.1.4.5.1 [RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling](#rqsrs-042oauthgrafanaazureauthenticationexpiredtokenhandling)

    
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

### Grafana Integration Support

#### Authentication

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication
version: 1.0

[Grafana] SHALL redirect users to the Azure AD authorization endpoint to obtain an access token if the user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

The values SHALL be stored inside the `.env` file which can be generated as:

```bash
printf "CLIENT_ID=<Client ID (Application ID)>\nTENANT_ID=<Tenant ID>\nCLIENT_SECRET=<Client Secret>\n" > .env
```

#### User Role Mapping

##### User has permission to view groups in Azure and ClickHouse has roles with the same names

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.SameName
version: 1.0

When a user has permission to view groups in Azure and [ClickHouse] has roles with the same names, [ClickHouse] SHALL map the user's Azure group membership to the corresponding [ClickHouse] roles.

##### User can view groups in Azure but there are no matching roles in ClickHouse

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoMatchingRoles
version: 1.0

When a user has permission to view groups in Azure but there are no matching roles in [ClickHouse], [ClickHouse] SHALL assign a default role to the user.

##### User does NOT have permission to view their groups in Azure

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoPermissionToViewGroups
version: 1.0

When a user does not have permission to view their groups in Azure, [ClickHouse] SHALL assign a default role to the user

##### In ClickHouse there is no default role specified

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.UserRoleMapping.NoDefaultRole
version: 1.0

When there is no default role specified in [ClickHouse] configuration or created via SQL,[ClickHouse] SHALL not allow the user to access any resources and there SHALL be no crashes on [ClickHouse] side.

The user configuration example,

```xml
<clickhouse>
    <my_user>
        <jwt>
        </jwt>
    </my_user>
</clickhouse>
```

#### Invalid Credentials When Requesting a JWT

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are incorrect. In this case, [ClickHouse] SHALL return an HTTP 401 Unauthorized response to [Grafana].

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.MissingSecret
version: 1.0

The user SHALL not receive a valid JWT token if the `CLIENT_SECRET` is missing from the HTTP request.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.EmptyString
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are an empty string.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.Null
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials are null.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.InvalidCredentials.NonAlphanumericCharacters
version: 1.0

The user SHALL not receive a valid JWT token if the provided credentials contain non-alphanumeric characters such as emojis.

#### Accessing ClickHouse from Grafana

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity
version: 1.0

[Grafana] SHALL support forwarding the same `JWT` token used to authenticate a user in [Grafana] to [ClickHouse] when making requests to the [ClickHouse] data source. This behavior SHALL be configurable by enabling the `Forward OAuth Identity` option in the [Grafana] data source settings.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Enabled
version: 1.0

When the `Forward OAuth Identity` option is enabled in [Grafana], [Grafana] SHALL include the JWT token in the HTTP Authorization header for requests sent to [ClickHouse]. The token SHALL be used by [ClickHouse] to validate the user's identity and permissions.

##### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.Disabled
version: 1.0

When the `Forward OAuth Identity` option is disabled in [Grafana], [Grafana] SHALL NOT forward the user's JWT token to ClickHouse.

##### Incorrect Requests to ClickHouse

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests
version: 1.0

When [Grafana] makes requests to [ClickHouse] without a valid JWT token in the Authorization header, [ClickHouse] SHALL return an HTTP 401 Unauthorized response.

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header
version: 1.0

[ClickHouse] SHALL reject requests that do not include the Authorization header with a valid JWT token.

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.alg
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `alg` value that is not supported by [ClickHouse].

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.typ
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `typ` value that is not supported by [ClickHouse].

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Header.Signature
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a JWT token that has an invalid signature.

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body
version: 1.0

[ClickHouse] SHALL reject requests that include incorrect or malformed body content.

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.sub
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with a `sub` value that does not match any user in [ClickHouse].

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.aud
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `aud` value that does not match the expected audience for the JWT token.

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ClickHouse.ForwardOAuthIdentity.IncorrectRequests.Body.exp
version: 1.0

[ClickHouse] SHALL reject requests that include an Authorization header with an `exp` value that indicates the token has expired.


##### Expired Token Handling

###### RQ.SRS-042.OAuth.Grafana.Azure.Authentication.ExpiredTokenHandling
version: 1.0

[ClickHouse] SHALL reject expired JWT tokens sent by [Grafana].


[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com


