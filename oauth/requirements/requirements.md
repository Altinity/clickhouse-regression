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
    * 5.1 [Azure](#azure)
        * 5.1.1 [Access Token Processors For Azure](#access-token-processors-for-azure)
            * 5.1.1.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors](#rqsrs-042oauthidentityprovidersaccesstokenprocessors)
    * 5.2 [Keycloak](#keycloak)
        * 5.2.1 [Access Token Processors For Keycloak](#access-token-processors-for-keycloak)
            * 5.2.1.1 [RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors.Keycloak](#rqsrs-042oauthidentityprovidersaccesstokenprocessorskeycloak)
    * 5.3 [Number of Identity Providers](#number-of-identity-providers)
    * 5.4 [Number of Identity Providers That Can Be Used Concurrently](#number-of-identity-providers-that-can-be-used-concurrently)
        * 5.4.1 [RQ.SRS-042.OAuth.IdentityProviders.Concurrent](#rqsrs-042oauthidentityprovidersconcurrent)
* 6 [Setting Up OAuth Authentication](#setting-up-oauth-authentication)
    * 6.1 [Credentials](#credentials)
        * 6.1.1 [RQ.SRS-042.OAuth.Credentials](#rqsrs-042oauthcredentials)
* 7 [Accessing ClickHouse from Grafana](#accessing-clickhouse-from-grafana)
    * 7.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.ForwardOAuthIdentity](#rqsrs-042oauthgrafanaauthenticationclickhouseforwardoauthidentity)
    * 7.2 [User Directories](#user-directories)
        * 7.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectories)
            * 7.2.1.1 [Incorrect Configuration in User Directories](#incorrect-configuration-in-user-directories)
                * 7.2.1.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.provider](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesincorrectconfigurationprovider)
                * 7.2.1.1.2 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.clientId](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesincorrectconfigurationclientid)
                * 7.2.1.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.tenantId](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesincorrectconfigurationtenantid)
                * 7.2.1.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.accessTokenProcessors.token.processor](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesincorrectconfigurationaccesstokenprocessorstokenprocessor)
                * 7.2.1.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.accessTokenProcessors.token.roles](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesincorrectconfigurationaccesstokenprocessorstokenroles)
            * 7.2.1.2 [Missing Configuration in User Directories](#missing-configuration-in-user-directories)
                * 7.2.1.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationaccesstokenprocessors)
                * 7.2.1.2.2 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.provider](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationaccesstokenprocessorsprovider)
                * 7.2.1.2.3 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.clientId](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationaccesstokenprocessorsclientid)
                * 7.2.1.2.4 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.tenantId](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationaccesstokenprocessorstenantid)
                * 7.2.1.2.5 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationuserdirectories)
            * 7.2.1.3 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationuserdirectoriestoken)
            * 7.2.1.4 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token.processor](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationuserdirectoriestokenprocessor)
            * 7.2.1.5 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token.roles](#rqsrs-042oauthgrafanaauthenticationclickhouseuserdirectoriesmissingconfigurationuserdirectoriestokenroles)
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
    * 7.6 [Caching](#caching)
        * 7.6.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.Caching](#rqsrs-042oauthgrafanaauthenticationclickhousecaching)
        * 7.6.2 [Disable Caching](#disable-caching)
            * 7.6.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.NoCache](#rqsrs-042oauthgrafanaauthenticationclickhousecacheevictionnocache)
        * 7.6.3 [Cache Eviction](#cache-eviction)
            * 7.6.3.1 [Cache Lifetime](#cache-lifetime)
                * 7.6.3.1.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.CacheLifetime](#rqsrs-042oauthgrafanaauthenticationclickhousecacheevictioncachelifetime)
            * 7.6.3.2 [Exceeding Max Cache Size](#exceeding-max-cache-size)
                * 7.6.3.2.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.MaxCacheSize](#rqsrs-042oauthgrafanaauthenticationclickhousecacheevictionmaxcachesize)
            * 7.6.3.3 [Cache Eviction Policy](#cache-eviction-policy)
                * 7.6.3.3.1 [RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.Policy](#rqsrs-042oauthgrafanaauthenticationclickhousecacheevictionpolicy)

    
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

```sql
CREATE USER my_user IDENTIFIED WITH jwt;
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
            <roles>
                <token_test_role_1 />
            </roles>
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

### Azure

[ClickHouse] SHALL support OAuth 2.0 authentication with Azure Active Directory (Azure AD) as an identity provider.

#### Access Token Processors For Azure

##### RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors
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

### Keycloak

#### Access Token Processors For Keycloak

##### RQ.SRS-042.OAuth.IdentityProviders.AccessTokenProcessors.Keycloak
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


### Number of Identity Providers

### Number of Identity Providers That Can Be Used Concurrently

#### RQ.SRS-042.OAuth.IdentityProviders.Concurrent
version: 1.0

[ClickHouse] SHALL support the use of only one identity provider at a time for OAuth 2.0 authentication. This means that all access tokens must be issued by the same identity provider configured in the `token_processors` section of `config.xml`.

## Setting Up OAuth Authentication

### Credentials

#### RQ.SRS-042.OAuth.Credentials
version: 1.0

[Grafana] SHALL redirect grafana user to the Identity Provider authorization endpoint to obtain an access token if the grafana user has provided a valid `CLIENT_ID`, `TENANT_ID` and the `CLIENT_SECRET`.

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

An `external user directory` in [ClickHouse] is a remote identity source (such as `LDAP`, `Kerberos`, or an `OAuth Identity Provider`) 
used to authenticate and retrieve user information that is not defined locally in [ClickHouse]. When enabled, [ClickHouse] dynamically 
validates user credentials and assigns roles based on data from this external system instead of relying solely on locally configured users.

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories
version: 1.0

When a user is not defined locally, [ClickHouse] SHALL use the `IdP` as a dynamic source of user information. This requires configuring the `<token>` section in `users_directories` and assigning appropriate roles.

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
            <roles>
                <token_test_role_1 />
            </roles>
        </token>
    </user_directories>
</clickhouse>
```

##### Incorrect Configuration in User Directories

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.provider
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.clientId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.tenantId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is incorrectly defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.accessTokenProcessors.token.processor
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.IncorrectConfiguration.accessTokenProcessors.token.roles
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is incorrectly defined in the `token` section of the `user_directories` section of the `config.xml` file.

##### Missing Configuration in User Directories

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token_processors` section is not defined in the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.provider
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `provider` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.clientId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `client_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.AccessTokenProcessors.tenantId
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `tenant_id` attribute is not defined in the `token_processors` section of the `config.xml` file.

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `user_directories` section is not defined in the `config.xml` file.

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `token` section is not defined in the `user_directories` section of the `config.xml` file.

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token.processor
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `processor` attribute is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserDirectories.MissingConfiguration.UserDirectories.token.roles
version: 1.0

[ClickHouse] SHALL not allow the grafana user to authenticate and access resources if the `roles` section is not defined in the `token` section of the `user_directories` section of the `config.xml` file.

### User Roles

#### Query Execution Based on User Roles

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.UserRoles
version: 1.0

When a grafana user is authenticated via OAuth, [ClickHouse] SHALL execute queries based on the roles assigned to the user in the `users_directories` section. The roles defined in the `<roles>` section of the `<token>` SHALL determine the permissions granted to the user.

<img width="1480" height="730" alt="Screenshot from 2025-07-30 16-08-58" src="https://github.com/user-attachments/assets/fbd4b3c5-3f8e-429d-8bb6-141c240d0384" />

#### User Has Permission To View Groups in Identity Provider and ClickHouse Has Roles With the Same Group Names

##### RQ.SRS-042.OAuth.Grafana.Authentication.UserRoles.SameName
version: 1.0

When a user has permission to view groups in the Identity Provider and [ClickHouse] has roles with same names, [ClickHouse] SHALL map the user's Identity Provider group membership to the corresponding [ClickHouse] roles.

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

When a grafana user is authenticated via OAuth and no roles are specified in the `<roles>` section of the `<token>`, grafana user will not be able to perform any actions after authentication.

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
            <roles>
            </roles>
        </token>
    </user_directories>
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

### Caching

#### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.Caching
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
            <roles>
                <token_test_role_1 />
            </roles>
        </token>
    </user_directories>
</clickhouse>
```

In this case the cache will be valid for 60 seconds. After this period.

#### Disable Caching

##### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.NoCache
version: 1.0

If the value of `cache_lifetime` is `0` in the `token_processors` configuration, [ClickHouse] SHALL not cache the tokens and SHALL validate each token on every request.

#### Cache Eviction

##### Cache Lifetime

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.CacheLifetime
version: 1.0

[ClickHouse] SHALL evict cached tokens after the `cache_lifetime` period defined in the `token_processors` configuration. If the cache was evicted, [ClickHouse] SHALL cache the new token provided by [Grafana] for the next requests.

##### Exceeding Max Cache Size

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.MaxCacheSize
version: 1.0

[ClickHouse] SHALL limit the maximum size of the cache for access tokens. If the cache exceeds this size, [ClickHouse] SHALL evict the oldest tokens to make room for new ones.

##### Cache Eviction Policy

###### RQ.SRS-042.OAuth.Grafana.Authentication.ClickHouse.CacheEviction.Policy
version: 1.0

[ClickHouse] SHALL use a Least Recently Used (LRU) cache eviction policy for access tokens. This means that when the cache reaches its maximum size, the least recently used tokens SHALL be removed to make space for new tokens.

[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com


