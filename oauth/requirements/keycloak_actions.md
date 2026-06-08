# Keycloak Actions

This document describes possible actions and attributes for Keycloak realms, clients, and users, based on the official Keycloak REST API documentation: [Keycloak REST API 22.0.5](https://www.keycloak.org/docs-api/22.0.5/rest-api/index.html).

## [Table of Contents](#keycloak-actions)

<!-- TOC -->
* [Application-relevant Keycloak actions affecting tokens](#application-relevant-keycloak-actions-affecting-tokens)
  * [Categories of actions](#categories-of-actions)
  * [Key attributes extracted from tokens](#key-attributes-extracted-from-tokens)
  * [Conditions for token validity](#conditions-for-token-validity)
  * [Actions affecting token validity](#actions-affecting-token-validity)
  * [Actions affecting user identification claims](#actions-affecting-user-identification-claims)
  * [Actions affecting group membership and visibility](#actions-affecting-group-membership-and-visibility)
* [JWT token claims issued by Keycloak](#jwt-token-claims-issued-by-keycloak)
  * [Standard OIDC claims](#standard-oidc-claims)
  * [User identity claims (optional)](#user-identity-claims-optional)
  * [Roles and access claims](#roles-and-access-claims)
  * [Group claims (optional)](#group-claims-optional)
  * [Keycloak-specific claims](#keycloak-specific-claims)
  * [Custom claims (via mappers)](#custom-claims-via-mappers)
  * [Example: simplified access token](#example-simplified-access-token)
* [Obtaining a Token for a User](#obtaining-a-token-for-a-user)
* [Token Lifecycle Management](#token-lifecycle-management)
  * [Token Expiration Settings](#token-expiration-settings)
  * [Token Renewal (Using Refresh Token)](#token-renewal-using-refresh-token)
  * [Token Revocation (Logout & Revoke)](#token-revocation-logout--revoke)
  * [Token Introspection (Validity Check)](#token-introspection-validity-check)
* [Automating Token Expiration and Other Settings](#automating-token-expiration-and-other-settings)
  * [Configurable via REST](#configurable-via-rest)
  * [Alternative: Bootstrap Using Realm JSON Import](#alternative-bootstrap-using-realm-json-import)
* [Supported Actions](#supported-actions)
  * [User Management](#user-management)
  * [Realm Management](#realm-management)
  * [Group Management](#group-management)
  * [Role Management](#role-management)
    * [Realm Roles](#realm-roles)
    * [Client Roles](#client-roles)
  * [Client Management](#client-management)
  * [Client Scope Management](#client-scope-management)
* [Controlling client scopes and consent via realm JSON](#controlling-client-scopes-and-consent-via-realm-json)
  * [What can be configured](#what-can-be-configured)
  * [Group claim and client scopes](#group-claim-and-client-scopes)
  * [Resulting token structure](#resulting-token-structure)
<!-- TOC -->

# Application-relevant Keycloak actions affecting tokens

This section summarizes Keycloak actions that can affect the behavior of an application that:

- Accepts and validates Keycloak-issued tokens (JWT access tokens)
- Extracts user identification (`sub`, `preferred_username`, `email`)
- Reads user group memberships (`groups` claim)
- Maps user identity and groups to internal user roles or permissions

## Categories of actions

| Category            | Example actions                                                             |
|---------------------|------------------------------------------------------------------------------|
| Token invalidation  | Realm deletion, logout, notBefore update, key rotation, expiration          |
| Identity changes    | Username, email, or protocol mapper updates                                 |
| Group visibility    | Group membership changes, mapper/scope removal, consent withdrawal          |

## Key attributes extracted from tokens

The following attributes are commonly used by relying applications:

- `sub`: unique user ID (immutable)
- `preferred_username`: human-readable identifier
- `email`: user email address
- `groups`: list of group paths (if exposed by mapper)
- `realm_access.roles`: list of realm-level roles (if mapped)
- `resource_access`: client-specific roles (if mapped)

## Conditions for token validity

A token issued by Keycloak will be considered **invalid** if any of the following conditions occur:

- The token has **expired** (based on `exp` claim)
- The **realm is deleted**
- The **client is deleted**
- The **user is deleted or disabled**
- The user **logs out** (explicit session termination)
- The realm or user-level **notBefore** value is updated
- The realm’s **signing keys are rotated or revoked**
- The client configuration no longer includes required **scopes or mappers**

## Actions affecting token validity

| Action                       | Effect                                                                 |
|-----------------------------|------------------------------------------------------------------------|
| Delete realm                | All tokens issued in that realm become invalid                         |
| Delete client               | Tokens issued for the client are no longer accepted                    |
| Logout user                 | Invalidates user session and access tokens                             |
| Disable user                | Prevents future logins, invalidates refresh tokens                     |
| Delete user                 | Breaks identity references, tokens become invalid                      |
| Update `notBefore` for realm or user | All tokens issued before the new time become invalid        |
| Rotate realm keys           | If old keys are removed, existing tokens may fail signature validation |
| Token expiration            | Token becomes invalid after `exp` time (defined by realm/client config)|
| Revoke offline session      | Prevents refresh token reuse                                           |

## Actions affecting user identification claims

| Action                       | Affected attributes in token                            |
|-----------------------------|----------------------------------------------------------|
| Change username             | Updates `preferred_username` in new tokens              |
| Change email or attributes  | Affects `email`, `name`, `given_name`, etc.             |
| Modify protocol mappers     | Changes what is included in the token                   |
| Remove claim mappers        | Attributes may disappear from token                     |
| Remove client scopes        | Claims linked to those scopes will no longer be issued  |

## Actions affecting group membership and visibility

| Action                             | Effect on `groups` claim                                      |
|-----------------------------------|----------------------------------------------------------------|
| Add/remove user from group        | Modifies group membership in future tokens                     |
| Rename group                      | Updates group path in tokens if full path is used             |
| Delete group                      | Removes group from user's token claim                         |
| Add/remove group-mapper protocol  | Controls whether groups are included in tokens                |
| Remove scope containing group mapper | Tokens will not include groups unless scope is present     |
| Require consent for group scope   | If consent is revoked, group info will be omitted             |

# JWT token claims issued by Keycloak

This section lists possible claims (attributes) that may appear in tokens issued by Keycloak — including access tokens, ID tokens, and userinfo responses.
These claims follow the [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) specification, with additional Keycloak-specific fields.

The actual set of claims in a token depends on:

- Token type (Access Token vs ID Token)
- Client scopes assigned to the client
- Protocol mappers configured in the realm
- Consent and user profile settings

Notes:

- **ID tokens** are typically used by frontends for authentication and user profile info.
- **Access tokens** are used to authorize access to APIs or resources.
- **Userinfo endpoint** can return claims dynamically (based on scopes and consent).

Reference:

- [OpenID Connect Core 1.0 – Standard Claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims)
- [Keycloak Protocol Mappers Documentation](https://www.keycloak.org/docs/latest/server_admin/#protocol-mappers)

## Standard OIDC claims

These are defined by the OIDC specification:

| Claim              | Description                                         | Token Type       |
|--------------------|-----------------------------------------------------|------------------|
| `iss`              | Issuer (realm base URL)                             | Access, ID       |
| `aud`              | Audience (usually the client ID)                    | Access, ID       |
| `exp`              | Expiration time (UNIX timestamp)                    | Access, ID       |
| `iat`              | Issued-at time                                      | Access, ID       |
| `nbf`              | Not-before time                                     | Access, ID       |
| `jti`              | JWT ID — unique token ID                            | Access, ID       |
| `sub`              | Subject — unique user ID                            | Access, ID       |
| `typ`              | Token type (e.g., "Bearer")                         | Access           |
| `azp`              | Authorized party — usually the client ID            | Access, ID       |
| `auth_time`        | Time of user authentication                         | ID               |
| `nonce`            | Nonce to prevent replay attacks                     | ID               |
| `acr`              | Authentication context class reference              | ID               |
| `session_state`    | Keycloak session ID                                 | Access, ID       |

See: [OIDC Core Claims Section 5.1](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims)

## User identity claims (optional)

These may appear in ID tokens, access tokens (if mappers enabled), or userinfo endpoint responses.

| Claim               | Description                        |
|---------------------|------------------------------------|
| `preferred_username`| User’s login name                  |
| `email`             | Email address                      |
| `email_verified`    | Boolean — if email is verified     |
| `name`              | Full name                          |
| `given_name`        | First name                         |
| `family_name`       | Last name                          |
| `locale`            | Locale (e.g., "en")                |
| `zoneinfo`          | Timezone of user                   |
| `phone_number`      | Phone number (if mapped)           |

## Roles and access claims

Keycloak adds the following to support role-based access control:

| Claim                 | Description                                      |
|-----------------------|--------------------------------------------------|
| `realm_access.roles`  | Realm-level roles assigned to user               |
| `resource_access`     | Client-level roles mapped per client             |
| Example:              | `"resource_access": { "app": { "roles": [...] } }`|

These claims only appear if roles are enabled and mapped for the client or client scope.

## Group claims (optional)

| Claim     | Description                                               |
|-----------|-----------------------------------------------------------|
| `groups`  | List of group paths for user (e.g., ["/dev", "/admin"])   |

- Only present if group membership is mapped via a protocol mapper.
- May require `consentRequired = true` to appear in tokens.

## Keycloak-specific claims

| Claim            | Description                                      |
|------------------|--------------------------------------------------|
| `session_state`  | Unique session ID assigned by Keycloak           |
| `sid`            | Session ID (OIDC `sid` claim)                    |
| `trusted-certs`  | Present if mutual TLS is configured              |

## Custom claims (via mappers)

You can define custom mappers to include arbitrary data:

| Claim               | Description                              |
|---------------------|------------------------------------------|
| `department`        | Mapped user attribute                    |
| `is_admin`          | Derived flag from role/group membership  |
| `any_custom_claim`  | Anything defined via protocol mapper     |

## Example: simplified access token

```json
{
  "exp": 1691257190,
  "iat": 1691256890,
  "jti": "uuid",
  "iss": "https://auth.example.com/realms/myrealm",
  "aud": "my-client",
  "sub": "f14d1234-56ab-4cde-8912-9a99d3ee4b33",
  "typ": "Bearer",
  "azp": "my-client",
  "session_state": "b7a7...ef2",
  "preferred_username": "johndoe",
  "email": "john@example.com",
  "groups": ["/engineering", "/qa"],
  "realm_access": {
    "roles": ["offline_access", "user"]
  },
  "resource_access": {
    "my-client": {
      "roles": ["reader", "editor"]
    }
  }
}
```

# Obtaining a Token for a User

To authenticate a user and retrieve an access token using the [OpenID Connect Token Endpoint](https://datatracker.ietf.org/doc/html/rfc6749#section-4.3):

```
POST /realms/{realm}/protocol/openid-connect/token
```

| Parameter       | Description                        |
|-----------------|------------------------------------|
| `grant_type`    | Must be `password`                 |
| `client_id`     | Client ID registered in Keycloak   |
| `client_secret` | Required if client is confidential |
| `username`      | Username of the user               |
| `password`      | Password of the user               |

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxxx' \
  -d 'username=john' \
  -d 'password=secret'
```

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "scope": "profile email"
}
```

> ⚠️ The client must have **Direct Access Grants Enabled** in the Keycloak Admin Console.

# Token Lifecycle Management

Keycloak supports full token lifecycle control through OpenID Connect endpoints and realm/client settings.

| Action           | Method | Endpoint                                    |
|------------------|--------|---------------------------------------------|
| Get Token        | POST   | `/protocol/openid-connect/token`            |
| Refresh Token    | POST   | `/protocol/openid-connect/token`            |
| Revoke Token     | POST   | `/protocol/openid-connect/logout`           |
| Introspect       | POST   | `/protocol/openid-connect/token/introspect` |
| Configure Expiry | PUT    | `/admin/realms/{realm}` (e.g. `accessTokenLifespan`) |

## Token Expiration Settings

Token lifetimes can be configured using realm JSON configuration file:

| Setting                  | Description                               | Default |
|--------------------------|-------------------------------------------|---------|
| Access Token Lifespan    | Time before access token expires          | 5 min   |
| Refresh Token Lifespan   | Absolute time refresh token remains valid | 30 min  |
| SSO Session Idle Timeout | Idle timeout before re-authentication     | 30 min  |
| SSO Session Max Lifespan | Max total session duration                | 10 hr   |

## Token Renewal (Using Refresh Token)

You can renew the access token before it expires using the refresh token.

```
POST /realms/{realm}/protocol/openid-connect/token
```

| Name           | Description               |
|----------------|---------------------------|
| grant_type     | `refresh_token`           |
| client_id      | Client ID                 |
| client_secret  | (If confidential client)  |
| refresh_token  | The valid refresh token   |

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=refresh_token' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxx' \
  -d 'refresh_token=eyJ...'
```

## Token Revocation (Logout & Revoke)

To revoke a token and logout the user:

```
POST /realms/{realm}/protocol/openid-connect/logout
```

| Name          | Description                 |
|---------------|-----------------------------|
| client_id     | Client ID                   |
| client_secret | (If confidential client)    |
| refresh_token | The refresh token to revoke |

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/logout' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxx' \
  -d 'refresh_token=eyJ...'
```

> 🔐 This revokes both the refresh and access tokens associated with the session.

## Token Introspection (Validity Check)

Use this to validate whether a token is active.

```
POST /realms/{realm}/protocol/openid-connect/token/introspect
```

| Name           | Description               |
|----------------|---------------------------|
| client_id      | Client ID                 |
| client_secret  | Required                  |
| token          | Access or refresh token   |

```bash
curl -X POST 'https://keycloak.example.com/realms/myrealm/protocol/openid-connect/token/introspect' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id=my-client' \
  -d 'client_secret=xxxxxx' \
  -d 'token=eyJ...'
```

```json
{
  "active": true,
  "exp": 1699029999,
  "scope": "openid email profile",
  "username": "john"
}
```

# Automating Token Expiration and Other Settings

Keycloak exposes token-lifecycle settings through its Admin REST API. The
realm-level token lifespans can be updated with `PUT /admin/realms/{realm}`,
including:

- Access token lifespan (`accessTokenLifespan`)
- Access token lifespan for implicit flow (`accessTokenLifespanForImplicitFlow`)
- Refresh / SSO session timeouts (`ssoSessionIdleTimeout`, `ssoSessionMaxLifespan`)
- Action token lifespans (e.g. email verification, password reset)

## Configurable via REST

`RealmRepresentation` fields such as `accessTokenLifespan` **can** be updated
via `PUT /admin/realms/{realm}`; this is the same endpoint the Keycloak admin
console uses. Example:

```bash
curl -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"accessTokenLifespan": 30}'
```

Caveats to be aware of when the issued token's `exp - iat` does not match the
value you set:

- **Client-level override.** A client attribute `access.token.lifespan` takes
  precedence over the realm setting for tokens issued to that client.
- **Session cap.** The effective lifespan is
  `min(accessTokenLifespan, remaining SSO session lifetime)`. With a fresh
  direct-access (`password`) grant the session is new, so the realm value
  applies.

See `oauth/tests/cache_semantics.py::cache_entry_capped_at_token_exp_when_token_expires_first`,
which sets `accessTokenLifespan` over REST and then decodes the JWT to confirm
the change took effect.

---

## Alternative: Bootstrap Using Realm JSON Import

You can automate token expiration and other settings by exporting the realm to a JSON file, modifying it, and re-importing it.

**Step 1: Export Realm**

From the server root:

```bash
bin/kc.sh export --realm=myrealm --file=realm-export.json --users=skip
```

This will generate a JSON file representing your realm, including token settings.

**Step 2: Edit the File**

Open `realm-export.json` and locate fields like:

```json
{
  "realm": "myrealm",
  "accessTokenLifespan": 600,
  "refreshTokenMaxReuse": 0,
  "ssoSessionIdleTimeout": 1800,
  "ssoSessionMaxLifespan": 36000,
  ...
}
```

Edit the values as needed.

**Step 3: Re-import Realm**

If you're setting up a new server or bootstrapping a test environment:

```bash
bin/kc.sh import --file=realm-export.json
```

This imports the full realm, including token settings, roles, users (if not skipped), and more.

# Supported Actions

**Summary Table of Core Capabilities**

| Category       | Can Create | Can Read | Can Update | Can Delete | Can Assign          |
|----------------|------------|----------|------------|------------|---------------------|
| Users          | ✅          | ✅        | ✅          | ✅          | ✅ (roles/groups)    |
| Groups         | ✅          | ✅        | ✅          | ✅          | ✅ (to users)        |
| Realms         | ✅          | ✅        | ✅          | ✅          | ❌                   |
| Roles (Realm)  | ✅          | ✅        | ✅          | ✅          | ✅ (to users/groups) |
| Roles (Client) | ✅          | ✅        | ✅          | ✅          | ✅                   |
| Clients        | ✅          | ✅        | ✅          | ✅          | ✅ (scopes/roles)    |
| Client Scopes  | ✅          | ✅        | ✅          | ✅          | ✅ (to clients)      |

## User Management

| Action                          | Endpoint                                                   | Description                                     |
|---------------------------------|------------------------------------------------------------|-------------------------------------------------|
| ✅ Create user                   | `POST /{realm}/users`                                      | Create a new user in a realm                    |
| ✅ Get user by ID                | `GET /{realm}/users/{id}`                                  | Fetch user details                              |
| ✅ Update user                   | `PUT /{realm}/users/{id}`                                  | Update user attributes                          |
| ✅ Delete user                   | `DELETE /{realm}/users/{id}`                               | Remove a user from the realm                    |
| ✅ Search users                  | `GET /{realm}/users`                                       | List users with filters (username, email, etc.) |
| ✅ Send verification email       | `PUT /{realm}/users/{id}/send-verify-email`                | Trigger email verification                      |
| ✅ Get user sessions             | `GET /{realm}/users/{id}/sessions`                         | List active sessions                            |
| ✅ Logout user                   | `POST /{realm}/users/{id}/logout`                          | Logout user and invalidate sessions             |
| ✅ Get user consents             | `GET /{realm}/users/{id}/consents`                         | List client consents                            |
| ✅ Revoke user consent           | `DELETE /{realm}/users/{id}/consents/{client}`             | Remove a client's consent                       |

## Realm Management

| Action           | Endpoint                       | Description                  |
|------------------|--------------------------------|------------------------------|
| ✅ Create realm   | `POST /admin/realms`           | Create a new realm           |
| ✅ Get realm      | `GET /admin/realms/{realm}`    | Retrieve realm configuration |
| ✅ Update realm   | `PUT /admin/realms/{realm}`    | Update realm settings        |
| ✅ Delete realm   | `DELETE /admin/realms/{realm}` | Delete the realm             |
| ✅ Get all realms | `GET /admin/realms`            | List all realms              |

## Group Management

| Action                   | Endpoint                                       | Description                       |
|--------------------------|------------------------------------------------|-----------------------------------|
| ✅ Create group           | `POST /{realm}/groups`                         | Add a new group                   |
| ✅ Get group              | `GET /{realm}/groups/{id}`                     | View group details                |
| ✅ Update group           | `PUT /{realm}/groups/{id}`                     | Rename or update group attributes |
| ✅ Delete group           | `DELETE /{realm}/groups/{id}`                  | Remove a group                    |
| ✅ Add subgroup           | `POST /{realm}/groups/{id}/children`           | Add a child group                 |
| ✅ List all groups        | `GET /{realm}/groups`                          | List all top-level groups         |
| ✅ Get user groups        | `GET /{realm}/users/{id}/groups`               | List groups a user belongs to     |
| ✅ Add user to group      | `PUT /{realm}/users/{id}/groups/{group-id}`    | Add user to a group               |
| ✅ Remove user from group | `DELETE /{realm}/users/{id}/groups/{group-id}` | Remove user from a group          |

## Role Management

### Realm Roles

| Action                    | Endpoint                                         | Description              |
|---------------------------|--------------------------------------------------|--------------------------|
| ✅ Create realm role       | `POST /{realm}/roles`                            | Add new realm-level role |
| ✅ List all realm roles    | `GET /{realm}/roles`                             | List realm-level roles   |
| ✅ Get role by name        | `GET /{realm}/roles/{role-name}`                 | Retrieve role details    |
| ✅ Update realm role       | `PUT /{realm}/roles/{role-name}`                 | Modify role attributes   |
| ✅ Delete realm role       | `DELETE /{realm}/roles/{role-name}`              | Delete a role            |
| ✅ Assign role to user     | `POST /{realm}/users/{id}/role-mappings/realm`   | Add realm role to user   |
| ✅ Remove role from user   | `DELETE /{realm}/users/{id}/role-mappings/realm` | Remove role from user    |
| ✅ List user’s realm roles | `GET /{realm}/users/{id}/role-mappings/realm`    |                          |

### Client Roles

| Action                         | Endpoint                                                       | Description                   |
|--------------------------------|----------------------------------------------------------------|-------------------------------|
| ✅ Create client role           | `POST /{realm}/clients/{id}/roles`                             | Add a role scoped to a client |
| ✅ Assign client role to user   | `POST /{realm}/users/{id}/role-mappings/clients/{client-id}`   |                               |
| ✅ Remove client role from user | `DELETE /{realm}/users/{id}/role-mappings/clients/{client-id}` |                               |

## Client Management

| Action                     | Endpoint                                                     | Description                         |
|----------------------------|--------------------------------------------------------------|-------------------------------------|
| ✅ Create client            | `POST /{realm}/clients`                                      | Register a new client (application) |
| ✅ Get client by ID         | `GET /{realm}/clients/{id}`                                  |                                     |
| ✅ Update client            | `PUT /{realm}/clients/{id}`                                  |                                     |
| ✅ Delete client            | `DELETE /{realm}/clients/{id}`                               |                                     |
| ✅ Get client secret        | `GET /{realm}/clients/{id}/client-secret`                    |                                     |
| ✅ Regenerate client secret | `POST /{realm}/clients/{id}/client-secret`                   |                                     |
| ✅ Get client scopes        | `GET /{realm}/clients/{id}/default-client-scopes`            |                                     |
| ✅ Assign client scopes     | `PUT /{realm}/clients/{id}/default-client-scopes/{scope-id}` |                                     |

## Client Scope Management

| Action                          | Endpoint                                                     | Description |
|---------------------------------|--------------------------------------------------------------|-------------|
| ✅ Create client scope           | `POST /{realm}/client-scopes`                                |             |
| ✅ Get client scope by ID        | `GET /{realm}/client-scopes/{id}`                            |             |
| ✅ Update client scope           | `PUT /{realm}/client-scopes/{id}`                            |             |
| ✅ Delete client scope           | `DELETE /{realm}/client-scopes/{id}`                         |             |
| ✅ Assign client scope to client | `PUT /{realm}/clients/{id}/default-client-scopes/{scope-id}` |             |

# Controlling client scopes and consent via realm JSON

Keycloak supports configuring client scopes, consent settings, and protocol mappers using the realm JSON file. This configuration is typically used in:

- Realm exports and imports (`kc.sh export`, `kc.sh import`)
- Automated or containerized deployments (e.g., `KEYCLOAK_IMPORT=/path/to/realm.json`)

## What can be configured

| Setting                     | Description                                                          |
|-----------------------------|----------------------------------------------------------------------|
| `defaultClientScopes`       | Assigns client scopes that are always included for a client          |
| `consentRequired`           | When true, forces the user to grant consent before token issuance    |
| `clientScopes` with mappers | Defines what claims are added to tokens, such as groups, roles, etc. |

## Group claim and client scopes

To include a user's group membership in tokens, you must:

1. Define a client scope that includes a protocol mapper for group membership.
2. Assign that client scope to a client.
3. Optionally require user consent.

```json
{
  "realm": "myrealm",
  "enabled": true,
  "clients": [
    {
      "clientId": "my-client",
      "protocol": "openid-connect",
      "consentRequired": true,
      "publicClient": false,
      "standardFlowEnabled": true,
      "defaultClientScopes": ["profile", "email", "groups"]
    }
  ],
  "clientScopes": [
    {
      "name": "groups",
      "protocol": "openid-connect",
      "protocolMappers": [
        {
          "name": "group-membership",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-group-membership-mapper",
          "consentRequired": false,
          "config": {
            "claim.name": "groups",
            "access.token.claim": "true",
            "id.token.claim": "true",
            "userinfo.token.claim": "true",
            "full.path": "true"
          }
        }
      ]
    }
  ]
}
```

## Resulting token structure

If the client is issued an ID or access token with the `groups` scope, it will include:

```json
{
  "sub": "user-id",
  "preferred_username": "johndoe",
  "groups": [
    "/engineering",
    "/admin"
  ]
}
```

**Notes**:

- User consent records cannot be preconfigured in JSON. If `consentRequired` is true, users must approve access at login time.
- This configuration can be automated as part of infrastructure provisioning, CI/CD, or local testing environments.
