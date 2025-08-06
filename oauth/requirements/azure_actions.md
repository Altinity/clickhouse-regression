# Azure AD Actions

This document describes possible actions and attributes for Azure Active Directory (Azure AD) users, groups, and applications, based on the Microsoft Graph REST API documentation.

<!-- TOC -->
* [Application-relevant Azure AD actions affecting tokens](#application-relevant-azure-ad-actions-affecting-tokens)
  * [Categories of actions](#categories-of-actions)
  * [Key attributes extracted from tokens](#key-attributes-extracted-from-tokens)
  * [Conditions for token validity](#conditions-for-token-validity)
  * [Actions affecting token validity](#actions-affecting-token-validity)
  * [Actions affecting user identification claims](#actions-affecting-user-identification-claims)
  * [Actions affecting group membership and visibility](#actions-affecting-group-membership-and-visibility)
  * [JWT Token Claims](#jwt-token-claims)
    * [Core Claims](#core-claims)
    * [Authentication Context](#authentication-context)
    * [Subject & Identity](#subject--identity)
    * [Application & Permissions](#application--permissions)
    * [Group Claims](#group-claims)
    * [Token Integrity](#token-integrity)
    * [Azure AD–Specific & Optional](#azure-adspecific--optional)
* [Obtaining a Token for a User or Application](#obtaining-a-token-for-a-user-or-application)
* [Token Lifecycle Management](#token-lifecycle-management)
  * [Refresh Token Management](#refresh-token-management)
  * [Logout and Token Revocation](#logout-and-token-revocation)
  * [Token Introspection](#token-introspection)
* [Automating Token and Policy Configuration](#automating-token-and-policy-configuration)
* [Supported Actions](#supported-actions)
* [User Management (`/users`)](#user-management-users)
* [Group Management (`/groups`)](#group-management-groups)
* [Application Management (`/applications`)](#application-management-applications)
* [Service Principal Management (`/servicePrincipals`)](#service-principal-management-serviceprincipals)
* [Directory Role Management (`/directoryRoles`)](#directory-role-management-directoryroles)
* [Controlling Consent and Scopes via Application Manifest JSON](#controlling-consent-and-scopes-via-application-manifest-json)
* [Register a Client Application](#register-a-client-application)
  * [Create Service Principal for the Application](#create-service-principal-for-the-application)
  * [Add a Client Secret (Confidential Client)](#add-a-client-secret-confidential-client)
<!-- TOC -->

# Application-relevant Azure AD actions affecting tokens

This section summarizes Azure AD actions that can affect how applications receive or validate tokens issued by Azure AD:

## Categories of actions

| Category               | Example actions                                                          |
|------------------------|--------------------------------------------------------------------------|
| Token issuance         | Consent grant, scope modification, application registration changes      |
| Identity changes       | User disable/enable, password reset                                      |
| Group and role changes | Add/remove user to group or app-role assignment, role definition updates |
| Application config     | Redirect URI changes, certificate and secret rotation                    |

## Key attributes extracted from tokens

- `iss`: token issuer (Azure AD endpoint)
- `aud`: audience (application/client ID)
- `exp`, `iat`, `nbf`: timing claims
- `sub`, `oid`: user object ID
- `upn`, `email`: user principal name and email
- `roles`: application roles or directory roles
- `scp`: delegated permission scopes
- `groups`: group IDs (if `groupMembershipClaims` configured)

## Conditions for token validity

A token issued by Azure AD will be considered **invalid** if any of the following occur:

- Token has **expired** (based on `exp` claim)
- **User** is deleted or disabled in Azure AD
- **Application** (service principal) is disabled
- **Client secret** or certificate used for signing has been **rotated** or **revoked**
- **Consent** for required scopes or application roles has been **revoked**

## Actions affecting token validity

| Action                    | Effect                                                                       |
|---------------------------|------------------------------------------------------------------------------|
| Disable user              | Prevents new token issuance for user                                         |
| Delete user               | Removes user identity, invalidating refresh tokens                           |
| Disable service principal | Blocks token issuance for application                                        |
| Remove admin consent      | Requires user or admin to re-consent                                         |
| Rotate client secret/cert | Breaks tokens signed with old key/cert if key rollover policy not configured |
| Expire refresh token      | Tokens cannot be refreshed beyond expiry                                     |

## Actions affecting user identification claims

| Action                     | Affected claims in new tokens                      |
|----------------------------|----------------------------------------------------|
| Update user attributes     | `upn`, `email`, `name` in ID and access tokens     |
| Enable/disable MFA         | Conditional access policies may affect `amr` claim |
| Add user to directory role | `roles` claim may include new role assignments     |

## Actions affecting group membership and visibility

| Action                            | Effect on `groups` claim or group-based access                       |
|-----------------------------------|----------------------------------------------------------------------|
| Add/remove user to group          | Modifies group IDs returned in tokens if group claims are configured |
| Configure `groupMembershipClaims` | Controls whether group IDs or names appear in token                  |
| Delete group                      | Removes group reference from tokens                                  |
| Update group owners or roles      | May affect role-based access if group is used in role assignment     |

## JWT Token Claims

Azure AD issues JSON Web Tokens (JWT) containing a variety of claims. Below is a table of standard, optional, and Azure AD–specific claims you may encounter in ID and access tokens.

### Core Claims

| Claim     | Type    | Description                                                              |
|-----------|---------|--------------------------------------------------------------------------|
| `aud`     | String  | Audience – intended recipient (your application’s client ID)             |
| `iss`     | URI     | Issuer – token-issuing authority (Azure AD endpoint)                     |
| `iat`     | Numeric | Issued At – time when token was issued                                   |
| `nbf`     | Numeric | Not Before – time before which token is not valid                        |
| `exp`     | Numeric | Expiration – time when token expires                                     |
| `jti`     | String  | JWT ID – unique identifier for the token                                 |

### Authentication Context

| Claim       | Type    | Description                                                          |
|-------------|---------|----------------------------------------------------------------------|
| `auth_time` | Numeric | Time of user authentication                                          |
| `amr`       | Array   | Authentication Methods References (e\.g\., \[`"pwd"`\], \[`"mfa"`\]) |
| `acr`       | String  | Authentication Context Class Reference                               |
| `nonce`     | String  | Cryptographic nonce for replay protection                            |
| `sid`       | String  | Session ID – used for single sign\-out                               |

### Subject & Identity

| Claim         | Type   | Description                                                                    |
|---------------|--------|--------------------------------------------------------------------------------|
| `sub`         | String | Subject – unique identifier for the token subject                              |
| `oid`         | GUID   | Object ID – unique identifier for user or service principal                    |
| `tid`         | GUID   | Tenant ID – Azure AD directory identifier                                      |
| `home_oid`    | GUID   | Home Object ID – original object ID if guest user                              |
| `upn`         | String | User Principal Name – usually \[user@domain\.com\]\(mailto\:user@domain\.com\) |
| `unique_name` | String | Preferred username                                                             |
| `email`       | String | User’s email address                                                           |
| `name`        | String | Display name                                                                   |
| `given_name`  | String | Given name                                                                     |
| `family_name` | String | Surname                                                                        |
| `idp`         | String | Identity Provider – origin of identity \(e\.g\., AzureAD\)                     |

### Application & Permissions

| Claim      | Type    | Description                                                        |
|------------|---------|--------------------------------------------------------------------|
| `appid`    | GUID    | Application ID – client ID of calling app \(v1\.0 tokens\)         |
| `azp`      | String  | Authorized Party – party to which token was issued                 |
| `appidacr` | String  | App Authentication Context Class Reference                         |
| `scp`      | String  | Delegated Permission Scopes \(space\-separated\)                   |
| `roles`    | Array   | Application Roles – roles assigned via appRoleAssignments          |
| `wids`     | Array   | Directory Role IDs – GUIDs of directory roles assigned             |

### Group Claims

| Claim    | Type  | Description                                                        |
|----------|-------|--------------------------------------------------------------------|
| `groups` | Array | Group IDs – if `groupMembershipClaims` enabled in app manifest     |

### Token Integrity

| Claim     | Type   | Description                                              |
|-----------|--------|----------------------------------------------------------|
| `at_hash` | String | Access Token Hash – for verifying integrity in ID tokens |
| `c_hash`  | String | Code Hash – for verifying integrity in ID tokens         |

### Azure AD–Specific & Optional

| Claim        | Type   | Description                                                        |
|--------------|--------|--------------------------------------------------------------------|
| `aio`        | String | Internal token indicator \(family/session hints\)                  |
| `uti`        | String | User Token Identifier – telemetry trace ID                         |
| `xms_mirid`  | String | Instance metadata \(in multi\-tenant applications\)                |
| `rh`         | String | Refresh Token hash \(in refresh token responses\)                  |
| `dir`        | String | Directory issuer reference                                         |

# Obtaining a Token for a User or Application

To acquire tokens from Azure AD using OAuth 2.0 or OpenID Connect:

```
POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
```

| Parameter       | Description                                                  |
|-----------------|--------------------------------------------------------------|
| `grant_type`    | `authorization_code`, `password`, `client_credentials`, etc. |
| `client_id`     | Application (client) ID                                      |
| `client_secret` | Client secret (if confidential client)                       |
| `code`          | Authorization code (for auth code flow)                      |
| `username`      | User UPN (for ROPC flow)                                     |
| `password`      | User password (for ROPC flow)                                |
| `scope`         | Space-separated scopes or resource URIs                      |

```bash
curl -X POST 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=your-client-id' \
  -d 'client_secret=your-secret' \
  -d 'username=user@domain.com' \
  -d 'password=Secret123' \
  -d 'scope=https://graph.microsoft.com/.default'
```

# Token Lifecycle Management

Azure AD supports token lifetimes via conditional access and policies:

| Action               | Method/Config                              |
|----------------------|--------------------------------------------|
| Refresh token expiry | Configured in Azure AD for user flows      |
| Access token expiry  | Generally 1 hour for v2.0 endpoint         |
| Session revocation   | `POST /oauth2/v2.0/logout`                 |
| Revoke user sessions | `POST /users/{id}/revokeSignInSessions`    |

## Refresh Token Management

Azure AD supports token refresh, revocation, and introspection mechanisms that are not currently detailed:

Use the refresh token to get a new access token:

```bash
curl -X POST 'https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id={client-id}' \
  -d 'client_secret={client-secret}' \
  -d 'grant_type=refresh_token' \
  -d 'refresh_token={refresh_token}' \
  -d 'scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'
```

## Logout and Token Revocation

Revoke a user's session and sign them out:

```bash
curl -X GET 'https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/logout'
```

## Token Introspection

For certain APIs and permissions, Azure AD provides a token introspection endpoint:

```bash
curl -X POST 'https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token/introspect' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id={client-id}' \
  -d 'client_secret={client-secret}' \
  -d 'token={access_or_refresh_token}'
```

# Automating Token and Policy Configuration

Azure AD token and policy settings are primarily managed via:

- Azure portal or PowerShell/Azure CLI
- Microsoft Graph API (limited for conditional access)
- ARM templates or Bicep for infrastructure as code

# Supported Actions

| Category           | Can Create | Can Read | Can Update | Can Delete | Can Assign            |
|--------------------|------------|----------|------------|------------|-----------------------|
| Users              | ✅          | ✅        | ✅          | ✅          | ✅ (roles/groups)      |
| Groups             | ✅          | ✅        | ✅          | ✅          | ✅ (members)           |
| Applications       | ✅          | ✅        | ✅          | ✅          | ✅ (roles/permissions) |
| Service Principals | ✅          | ✅        | ✅          | ✅          | ✅ (appRoles)          |
| Directory Roles    | ✅          | ✅        | ✅          | ✅          | ✅ (to users/groups)   |

# User Management (`/users`)

| Action                  | Endpoint                                                                    | Description                |
|-------------------------|-----------------------------------------------------------------------------|----------------------------|
| Create user             | `POST /users`                                                               | Create a new Azure AD user |
| Get user by ID          | `GET /users/{id}`                                                           | Retrieve user object       |
| Update user             | `PATCH /users/{id}`                                                         | Update user attributes     |
| Delete user             | `DELETE /users/{id}`                                                        | Remove a user              |
| List users              | `GET /users`                                                                | List all users             |
| Revoke sign-in sessions | `POST /users/{id}/revokeSignInSessions`                                     | Invalidate user sessions   |
| Reset user password     | `POST /users/{id}/authentication/passwordMethods/{method-id}/resetPassword` | Reset credential method    |

# Group Management (`/groups`)

| Action                  | Endpoint                                       | Description                 |
|-------------------------|------------------------------------------------|-----------------------------|
| Create group            | `POST /groups`                                 | Add a new group             |
| Get group by ID         | `GET /groups/{id}`                             | View group details          |
| Update group            | `PATCH /groups/{id}`                           | Modify group properties     |
| Delete group            | `DELETE /groups/{id}`                          | Remove a group              |
| List members            | `GET /groups/{id}/members`                     | List group members          |
| Add member              | `POST /groups/{id}/members/$ref`               | Add user or object to group |
| Remove member           | `DELETE /groups/{id}/members/{member-id}/$ref` | Remove from group           |
| List transitive members | `GET /groups/{id}/transitiveMembers`           | Recursive membership        |

# Application Management (`/applications`)

| Action                     | Endpoint                                                      | Description                             |
|----------------------------|---------------------------------------------------------------|-----------------------------------------|
| Create application         | `POST /applications`                                          | Register a new application (App Role)   |
| Get application by ID      | `GET /applications/{id}`                                      | View application registration           |
| Update application         | `PATCH /applications/{id}`                                    | Modify app manifest                     |
| Delete application         | `DELETE /applications/{id}`                                   | Remove application                      |
| List app role assignments  | `GET /applications/{id}/appRoleAssignedTo`                    | See which principals are assigned roles |
| Add app role assignment    | `POST /applications/{id}/appRoleAssignedTo`                   | Assign app role to service principal    |
| Remove app role assignment | `DELETE /applications/{id}/appRoleAssignedTo/{assignment-id}` | Remove assignment                       |

# Service Principal Management (`/servicePrincipals`)

| Action                        | Endpoint                                   | Description                               |
|-------------------------------|--------------------------------------------|-------------------------------------------|
| Create service principal      | `POST /servicePrincipals`                  | Create SP for application                 |
| Get SP by ID                  | `GET /servicePrincipals/{id}`              | View service principal                    |
| Update SP                     | `PATCH /servicePrincipals/{id}`            | Modify SP settings                        |
| Delete SP                     | `DELETE /servicePrincipals/{id}`           | Remove SP                                 |

# Directory Role Management (`/directoryRoles`)

| Action                     | Endpoint                                             | Description                       |
|----------------------------|------------------------------------------------------|-----------------------------------|
| List directory roles       | `GET /directoryRoles`                                | Retrieve all roles                |
| Activate role              | `POST /directoryRoles/activate`                      | Activate a role for assignment    |
| Assign role to principal   | `POST /directoryRoles/{role-id}/members/$ref`        | Assign to user/ group/ service sp |
| Remove role from principal | `DELETE /directoryRoles/{role-id}/members/{id}/$ref` | Remove assignment                 |

# Controlling Consent and Scopes via Application Manifest JSON

Azure AD applications use a JSON manifest to define required resource access, oauth2Permissions, and group membership claims:

```json
{
  "requiredResourceAccess": [
    {
      "resourceAppId": "00000003-0000-0000-c000-000000000000",
      "resourceAccess": [
        {
          "id": "scope-guid",
          "type": "Scope"
        }
      ]
    }
  ],
  "appRoles": [
    {
      "id": "role-guid",
      "allowedMemberTypes": ["User", "Application"],
      "displayName": "Reader",
      "value": "Reader"
    }
  ],
  "groupMembershipClaims": "SecurityGroup"
}
```

# Register a Client Application

Create an application (client) in Azure AD:

```bash
curl -X POST https://graph.microsoft.com/v1.0/applications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "displayName": "Grafana",
    "signInAudience": "AzureADMyOrg",
    "web": {
      "redirectUris": [
        "http://localhost:3000/login/generic_oauth"
      ]
    }
  }'
```

## Create Service Principal for the Application

To allow sign-ins and token issuance, create a service principal for the registered app:

```bash
curl -X POST https://graph.microsoft.com/v1.0/servicePrincipals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"appId": "{appId_from_previous_step}"}'
```

## Add a Client Secret (Confidential Client)

```bash
curl -X POST https://graph.microsoft.com/v1.0/applications/{application-id}/addPassword \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{
    "passwordCredential": {
      "displayName": "GrafanaSecret"
    }
  }'
```
