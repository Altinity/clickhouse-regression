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
* [JWT token claims issued by Azure AD](#jwt-token-claims-issued-by-azure-ad)
* [Obtaining a Token for a User or Application](#obtaining-a-token-for-a-user-or-application)
* [Token Lifecycle Management](#token-lifecycle-management)
* [Automating Token and Policy Configuration](#automating-token-and-policy-configuration)
* [Supported Actions](#supported-actions)
* [User Management (`/users`) fileciteturn0file2](#user-management-users-fileciteturn0file2)
* [Group Management (`/groups`) fileciteturn0file1](#group-management-groups-fileciteturn0file1)
* [Application Management (`/applications`) fileciteturn0file0](#application-management-applications-fileciteturn0file0)
* [Service Principal Management (`/servicePrincipals`)](#service-principal-management-serviceprincipals)
* [Directory Role Management (`/directoryRoles`)](#directory-role-management-directoryroles)
* [Controlling Consent and Scopes via Application Manifest JSON](#controlling-consent-and-scopes-via-application-manifest-json)
<!-- TOC -->

# Application-relevant Azure AD actions affecting tokens

This section summarizes Azure AD actions that can affect how applications receive or validate tokens issued by Azure AD:

## Categories of actions

| Category               | Example actions                                                                          |
|------------------------|------------------------------------------------------------------------------------------|
| Token issuance         | Consent grant, scope modification, application registration changes                      |
| Identity changes       | User disable/enable, password reset                                                      |
| Group and role changes | Add/remove user to group or app-role assignment, role definition updates                |
| Application config     | Redirect URI changes, certificate and secret rotation                                    |

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

| Action                        | Effect                                                                                 |
|------------------------------|----------------------------------------------------------------------------------------|
| Disable user                 | Prevents new token issuance for user                                                  |
| Delete user                  | Removes user identity, invalidating refresh tokens                                     |
| Disable service principal    | Blocks token issuance for application                                                 |
| Remove admin consent         | Requires user or admin to re-consent                                                     |
| Rotate client secret/cert    | Breaks tokens signed with old key/cert if key rollover policy not configured            |
| Expire refresh token         | Tokens cannot be refreshed beyond expiry                                               |

## Actions affecting user identification claims

| Action                    | Affected claims in new tokens                                                |
|---------------------------|-------------------------------------------------------------------------------|
| Update user attributes    | `upn`, `email`, `name` in ID and access tokens                                |
| Enable/disable MFA        | Conditional access policies may affect `amr` claim                            |
| Add user to directory role| `roles` claim may include new role assignments                                |

## Actions affecting group membership and visibility

| Action                         | Effect on `groups` claim or group-based access                                 |
|--------------------------------|--------------------------------------------------------------------------------|
| Add/remove user to group       | Modifies group IDs returned in tokens if group claims are configured            |
| Configure `groupMembershipClaims` | Controls whether group IDs or names appear in token                          |
| Delete group                   | Removes group reference from tokens                                             |
| Update group owners or roles   | May affect role-based access if group is used in role assignment                |

# JWT token claims issued by Azure AD

This section lists common claims in tokens issued by Azure AD:

| Claim         | Description                                                   |
|---------------|---------------------------------------------------------------|
| `iss`         | Issuer – Azure AD v2.0 endpoint                               |
| `aud`         | Audience – application (client) ID                             |
| `exp`         | Expiration time                                               |
| `iat`         | Issued-at time                                                |
| `nbf`         | Not-before time                                               |
| `ip`          | Client IP address                                             |
| `sub`         | Subject – unique token subject (GUID)                         |
| `oid`         | Object ID – Azure AD user or service principal ID             |
| `upn`         | User principal name                                           |
| `email`       | User email address                                            |
| `name`        | Display name                                                  |
| `tid`         | Tenant ID                                                     |
| `scp`         | Delegated permission scopes                                   |
| `roles`       | Application roles (appRoleAssignments)                        |
| `wids`        | Directory role IDs (if assigned)                              |
| `groups`      | Group IDs (if groupMembershipClaims configured)               |

# Obtaining a Token for a User or Application

To acquire tokens from Azure AD using OAuth 2.0 or OpenID Connect:

```
POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
```

| Parameter            | Description                                               |
|----------------------|-----------------------------------------------------------|
| `grant_type`         | `authorization_code`, `password`, `client_credentials`, etc. |
| `client_id`          | Application (client) ID                                   |
| `client_secret`      | Client secret (if confidential client)                    |
| `code`               | Authorization code (for auth code flow)                   |
| `username`           | User UPN (for ROPC flow)                                  |
| `password`           | User password (for ROPC flow)                             |
| `scope`              | Space-separated scopes or resource URIs                   |

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

| Action                  | Method/Config                                              |
|-------------------------|------------------------------------------------------------|
| Refresh token expiry    | Configured in Azure AD for user flows                      |
| Access token expiry     | Generally 1 hour for v2.0 endpoint                         |
| Session revocation      | `POST /oauth2/v2.0/logout`                                 |
| Revoke user sessions    | `POST /users/{id}/revokeSignInSessions` fileciteturn0file2 |

# Automating Token and Policy Configuration

Azure AD token and policy settings are primarily managed via:

- Azure portal or PowerShell/Azure CLI
- Microsoft Graph API (limited for conditional access)
- ARM templates or Bicep for infrastructure as code

Example: Azure CLI to set access token lifetime policy:

```bash
az ad policy token-lifetime update --id <policy-id> --access-token-life-time 01:00:00
```

# Supported Actions

| Category       | Can Create | Can Read | Can Update | Can Delete | Can Assign          |
|----------------|------------|----------|------------|------------|---------------------|
| Users          | ✅          | ✅        | ✅          | ✅          | ✅ (roles/groups)    |
| Groups         | ✅          | ✅        | ✅          | ✅          | ✅ (members)         |
| Applications   | ✅          | ✅        | ✅          | ✅          | ✅ (roles/permissions) |
| Service Principals | ✅      | ✅        | ✅          | ✅          | ✅ (appRoles)        |
| Directory Roles| ✅          | ✅        | ✅          | ✅          | ✅ (to users/groups)|

# User Management (`/users`) fileciteturn0file2

| Action                        | Endpoint                                    | Description                                |
|-------------------------------|---------------------------------------------|--------------------------------------------|
| Create user                   | `POST /users`                               | Create a new Azure AD user                 |
| Get user by ID                | `GET /users/{id}`                           | Retrieve user object                       |
| Update user                   | `PATCH /users/{id}`                         | Update user attributes                     |
| Delete user                   | `DELETE /users/{id}`                        | Remove a user                              |
| List users                    | `GET /users`                                | List all users                             |
| Revoke sign-in sessions       | `POST /users/{id}/revokeSignInSessions`     | Invalidate user sessions                   |
| Reset user password           | `POST /users/{id}/authentication/passwordMethods/{method-id}/resetPassword` | Reset credential method             |

# Group Management (`/groups`) fileciteturn0file1

| Action                     | Endpoint                                        | Description                           |
|----------------------------|-------------------------------------------------|---------------------------------------|
| Create group               | `POST /groups`                                  | Add a new group                       |
| Get group by ID            | `GET /groups/{id}`                              | View group details                    |
| Update group               | `PATCH /groups/{id}`                            | Modify group properties               |
| Delete group               | `DELETE /groups/{id}`                           | Remove a group                        |
| List members               | `GET /groups/{id}/members`                      | List group members                    |
| Add member                 | `POST /groups/{id}/members/$ref`                | Add user or object to group           |
| Remove member              | `DELETE /groups/{id}/members/{member-id}/$ref`  | Remove from group                     |
| List transitive members    | `GET /groups/{id}/transitiveMembers`            | Recursive membership                   |

# Application Management (`/applications`) fileciteturn0file0

| Action                       | Endpoint                                    | Description                              |
|------------------------------|---------------------------------------------|------------------------------------------|
| Create application           | `POST /applications`                        | Register a new application (App Role)    |
| Get application by ID        | `GET /applications/{id}`                    | View application registration            |
| Update application           | `PATCH /applications/{id}`                  | Modify app manifest                      |
| Delete application           | `DELETE /applications/{id}`                 | Remove application                       |
| List app role assignments    | `GET /applications/{id}/appRoleAssignedTo`  | See which principals are assigned roles  |
| Add app role assignment      | `POST /applications/{id}/appRoleAssignedTo` | Assign app role to service principal     |
| Remove app role assignment   | `DELETE /applications/{id}/appRoleAssignedTo/{assignment-id}` | Remove assignment          |

# Service Principal Management (`/servicePrincipals`)

| Action                        | Endpoint                                   | Description                               |
|-------------------------------|--------------------------------------------|-------------------------------------------|
| Create service principal      | `POST /servicePrincipals`                  | Create SP for application                 |
| Get SP by ID                  | `GET /servicePrincipals/{id}`              | View service principal                    |
| Update SP                     | `PATCH /servicePrincipals/{id}`            | Modify SP settings                        |
| Delete SP                     | `DELETE /servicePrincipals/{id}`           | Remove SP                                 |

# Directory Role Management (`/directoryRoles`)

| Action                           | Endpoint                                             | Description                           |
|----------------------------------|------------------------------------------------------|---------------------------------------|
| List directory roles              | `GET /directoryRoles`                                | Retrieve all roles                   |
| Activate role                     | `POST /directoryRoles/activate`                      | Activate a role for assignment       |
| Assign role to principal          | `POST /directoryRoles/{role-id}/members/$ref`        | Assign to user/ group/ service sp    |
| Remove role from principal        | `DELETE /directoryRoles/{role-id}/members/{id}/$ref` | Remove assignment                    |

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

This manifest can be managed via Graph or Azure portal and ensures tokens include correct scopes, roles, and group claims.
