# SRS-042 OAuth Authentication in ClickHouse
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Definitions](#definitions)
    * 2.1 [Structure of OAuth](#structure-of-oauth)
* 3 [Overview of the Functionality](#overview-of-the-functionality)
    * 3.1 [Access Token Processors](#access-token-processors)
    * 3.2 [Authentication Modes with OAuth Tokens](#authentication-modes-with-oauth-tokens)
* 4 [Authentication with OAuth](#authentication-with-oauth)
    * 4.1 [RQ.SRS-042.OAuth.Authentication](#rqsrs-042oauthauthentication)

    
## Introduction

This Software Requirements Specification (SRS) defines the requirements for OAuth 2.0 authentication support in ClickHouse.

OAuth 2.0 is an industry-standard authorization framework (defined in [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)) that enables third-party applications to obtain limited access to an HTTP service, either on behalf of a user or using application credentials. It decouples authentication from authorization, allowing for more secure and flexible access control mechanisms.

Integrating OAuth 2.0 in ClickHouse allows the system to delegate user authentication to trusted external identity providers (such as Google, Microsoft, or Okta), streamlining user management and enhancing security.

Through OAuth 2.0, ClickHouse can accept access tokens issued by an identity provider and validate them using static or dynamic JSON Web Key Sets (JWKS). The access token—typically a JWT—includes user identity and scope information that ClickHouse can use to authorize requests to resources.

This approach supports a wide range of identity federation use cases and enables ClickHouse to function within modern enterprise authentication ecosystems.

## Definitions

- **Identity Provider (IdP):** A service that issues access tokens after authenticating users. Examples include Azure Active Directory, Google Identity, and Okta.
- **Access Token:** A token issued by an IdP that grants access to protected resources. It is often a JSON Web Token (JWT) containing user identity and permissions.
- **[JWT (JSON Web Token)](https://github.com/Altinity/clickhouse-regression/blob/main/jwt_authentication/requirements/requirements.md):** A compact, URL-safe means of representing claims to be transferred between two parties. It is used in OAuth 2.0 for access tokens.

### Structure of OAuth

OAuth 2.0 defines several roles and token types used in the process of authorizing access to protected resources:

  * **Resource Owner:** The user or system that owns the data or resource.

  * **Client:** The application requesting access on behalf of the resource owner.
  * **Authorization Server:** The server that authenticates the resource owner and issues access tokens to the client.

  * **Resource Server:** The server (e.g., ClickHouse) that hosts the protected resources and verifies access tokens.

OAuth 2.0 typically issues two types of tokens:

  * **Access Token:** A short-lived token used by the client to access protected resources. In many implementations, the access token is a JWT that encodes user identity and scopes (permissions).

  * **Refresh Token:** An optional long-lived token used to obtain new access tokens without re-authenticating the user.


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
        </azure_ad>
    </access_token_processors>
</clickhouse>
```

Key Parameters:

- **provider:** Specifies the identity provider (for example, `azure`).

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

### RQ.SRS-042.OAuth.Authentication
version: 1.0

This requirement specifies that ClickHouse must support OAuth 2.0 authentication, allowing users to authenticate using access tokens issued by external identity providers.





[ClickHouse]: https://clickhouse.com
[Grafana]: https://grafana.com


