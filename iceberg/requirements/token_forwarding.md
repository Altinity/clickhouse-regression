# SRS-050 ClickHouse Forwarding User Tokens to Data Lake Catalogs
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Terminology](#terminology)
* 2 [Server Setting](#server-setting)
    * 2.1 [RQ.Iceberg.TokenForwarding.ServerSetting](#rqicebergtokenforwardingserversetting)
    * 2.2 [RQ.Iceberg.TokenForwarding.ServerSetting.HotReload](#rqicebergtokenforwardingserversettinghotreload)
    * 2.3 [RQ.Iceberg.TokenForwarding.ServerSetting.ReportedAsHotReloadable](#rqicebergtokenforwardingserversettingreportedashotreloadable)
* 3 [Token Capture](#token-capture)
    * 3.1 [RQ.Iceberg.TokenForwarding.Capture.NativeJWT](#rqicebergtokenforwardingcapturenativejwt)
    * 3.2 [RQ.Iceberg.TokenForwarding.Capture.HTTPBearer](#rqicebergtokenforwardingcapturehttpbearer)
    * 3.3 [RQ.Iceberg.TokenForwarding.Capture.VerifiedTokensOnly](#rqicebergtokenforwardingcaptureverifiedtokensonly)
    * 3.4 [RQ.Iceberg.TokenForwarding.Capture.NonTokenUsers](#rqicebergtokenforwardingcapturenontokenusers)
    * 3.5 [RQ.Iceberg.TokenForwarding.Capture.Principal](#rqicebergtokenforwardingcaptureprincipal)
* 4 [Token Propagation](#token-propagation)
    * 4.1 [RQ.Iceberg.TokenForwarding.Propagation.EveryCatalogRequest](#rqicebergtokenforwardingpropagationeverycatalogrequest)
    * 4.2 [RQ.Iceberg.TokenForwarding.Propagation.Concurrency](#rqicebergtokenforwardingpropagationconcurrency)
    * 4.3 [RQ.Iceberg.TokenForwarding.Propagation.ExecuteAs](#rqicebergtokenforwardingpropagationexecuteas)
    * 4.4 [RQ.Iceberg.TokenForwarding.Propagation.HTTPSession](#rqicebergtokenforwardingpropagationhttpsession)
    * 4.5 [RQ.Iceberg.TokenForwarding.Propagation.LocalNodeOnly](#rqicebergtokenforwardingpropagationlocalnodeonly)
    * 4.6 [RQ.Iceberg.TokenForwarding.Propagation.RemoteNodeError](#rqicebergtokenforwardingpropagationremotenodeerror)
    * 4.7 [RQ.Iceberg.TokenForwarding.Propagation.Confidentiality](#rqicebergtokenforwardingpropagationconfidentiality)
* 5 [Database Configuration](#database-configuration)
    * 5.1 [RQ.Iceberg.TokenForwarding.Database.OptIn](#rqicebergtokenforwardingdatabaseoptin)
    * 5.2 [RQ.Iceberg.TokenForwarding.Database.SupportedCatalogs](#rqicebergtokenforwardingdatabasesupportedcatalogs)
    * 5.3 [RQ.Iceberg.TokenForwarding.Database.InvalidRESTSettings](#rqicebergtokenforwardingdatabaseinvalidrestsettings)
    * 5.4 [RQ.Iceberg.TokenForwarding.Database.ExchangeSettingsRequireForwarding](#rqicebergtokenforwardingdatabaseexchangesettingsrequireforwarding)
    * 5.5 [RQ.Iceberg.TokenForwarding.Database.TokenTypes](#rqicebergtokenforwardingdatabasetokentypes)
    * 5.6 [RQ.Iceberg.TokenForwarding.Database.InvalidGlueSettings](#rqicebergtokenforwardingdatabaseinvalidgluesettings)
    * 5.7 [RQ.Iceberg.TokenForwarding.Database.DetachAttach](#rqicebergtokenforwardingdatabasedetachattach)
    * 5.8 [RQ.Iceberg.TokenForwarding.Database.HostFilter](#rqicebergtokenforwardingdatabasehostfilter)
* 6 [REST Passthrough](#rest-passthrough)
    * 6.1 [RQ.Iceberg.TokenForwarding.REST.Passthrough](#rqicebergtokenforwardingrestpassthrough)
    * 6.2 [RQ.Iceberg.TokenForwarding.REST.NoServiceFallback](#rqicebergtokenforwardingrestnoservicefallback)
    * 6.3 [RQ.Iceberg.TokenForwarding.REST.PerUserAuthorization](#rqicebergtokenforwardingrestperuserauthorization)
    * 6.4 [RQ.Iceberg.TokenForwarding.REST.Config](#rqicebergtokenforwardingrestconfig)
    * 6.5 [RQ.Iceberg.TokenForwarding.REST.Passthrough.NoRetry](#rqicebergtokenforwardingrestpassthroughnoretry)
* 7 [REST Token Exchange](#rest-token-exchange)
    * 7.1 [RQ.Iceberg.TokenForwarding.REST.Exchange.Request](#rqicebergtokenforwardingrestexchangerequest)
    * 7.2 [RQ.Iceberg.TokenForwarding.REST.Exchange.CatalogReceivesExchangedToken](#rqicebergtokenforwardingrestexchangecatalogreceivesexchangedtoken)
    * 7.3 [RQ.Iceberg.TokenForwarding.REST.Exchange.ActorToken](#rqicebergtokenforwardingrestexchangeactortoken)
    * 7.4 [RQ.Iceberg.TokenForwarding.REST.Exchange.Cache](#rqicebergtokenforwardingrestexchangecache)
    * 7.5 [RQ.Iceberg.TokenForwarding.REST.Exchange.CacheLifetime](#rqicebergtokenforwardingrestexchangecachelifetime)
    * 7.6 [RQ.Iceberg.TokenForwarding.REST.Exchange.Failure](#rqicebergtokenforwardingrestexchangefailure)
    * 7.7 [RQ.Iceberg.TokenForwarding.REST.Exchange.RetryOnUnauthorized](#rqicebergtokenforwardingrestexchangeretryonunauthorized)
* 8 [Vended Credentials](#vended-credentials)
    * 8.1 [RQ.Iceberg.TokenForwarding.VendedCredentials.PerUser](#rqicebergtokenforwardingvendedcredentialsperuser)
* 9 [Writes](#writes)
    * 9.1 [RQ.Iceberg.TokenForwarding.Writes.Insert](#rqicebergtokenforwardingwritesinsert)
    * 9.2 [RQ.Iceberg.TokenForwarding.Writes.AsyncInsert](#rqicebergtokenforwardingwritesasyncinsert)
    * 9.3 [RQ.Iceberg.TokenForwarding.Writes.DropTable](#rqicebergtokenforwardingwritesdroptable)
* 10 [AWS Glue](#aws-glue)
    * 10.1 [RQ.Iceberg.TokenForwarding.Glue.AssumeRoleWithWebIdentity](#rqicebergtokenforwardingglueassumerolewithwebidentity)
    * 10.2 [RQ.Iceberg.TokenForwarding.Glue.RoleSessionName](#rqicebergtokenforwardinggluerolesessionname)
    * 10.3 [RQ.Iceberg.TokenForwarding.Glue.ClientCache](#rqicebergtokenforwardingglueclientcache)
    * 10.4 [RQ.Iceberg.TokenForwarding.Glue.RejectedToken](#rqicebergtokenforwardinggluerejectedtoken)
    * 10.5 [RQ.Iceberg.TokenForwarding.Glue.NonTokenUsers](#rqicebergtokenforwardinggluenontokenusers)
* 11 [Credential Rotation](#credential-rotation)
    * 11.1 [RQ.Iceberg.TokenForwarding.CredentialRotation](#rqicebergtokenforwardingcredentialrotation)
* 12 [Observability](#observability)
    * 12.1 [RQ.Iceberg.TokenForwarding.Observability.ProfileEvents](#rqicebergtokenforwardingobservabilityprofileevents)
    * 12.2 [RQ.Iceberg.TokenForwarding.Observability.Metrics](#rqicebergtokenforwardingobservabilitymetrics)
    * 12.3 [RQ.Iceberg.TokenForwarding.Observability.ErrorMessages](#rqicebergtokenforwardingobservabilityerrormessages)

## Introduction

A `DataLakeCatalog` database talks to its external catalog (Iceberg REST or AWS Glue) with one
service identity configured in the database definition: `catalog_credential` or `auth_header`
for REST, static AWS keys or the default AWS credential chain for Glue. Every [ClickHouse] user
querying the database reaches the catalog as that one identity, so the catalog cannot apply its
own per-user authorization, and its audit log records every access as [ClickHouse].

This specification covers **token forwarding**: a database created with
`oauth_forward_user_token = 1` reaches the catalog as the querying user, using the bearer token
the user authenticated to [ClickHouse] with. Three modes are covered:

* REST passthrough: the user token is sent to the REST catalog unchanged;
* REST exchange: the user token is exchanged at an RFC 8693 token endpoint
  (`oauth_token_exchange_uri`) for a catalog session token, which is sent instead;
* Glue: the user token is used as the web identity in `AssumeRoleWithWebIdentity` for
  `aws_role_arn`, and the resulting temporary credentials sign Glue and S3 requests.

Forwarding needs two switches. The server setting `enable_token_forwarding` allows sessions to
keep their token, and the database setting `oauth_forward_user_token` makes the database use it.

```xml
<clickhouse>
    <enable_token_forwarding>1</enable_token_forwarding>
</clickhouse>
```

```sql
CREATE DATABASE lake
ENGINE = DataLakeCatalog('http://catalog:8181/v1')
SETTINGS catalog_type = 'rest',
         warehouse = 'demo',
         storage_endpoint = 'http://minio:9000/warehouse',
         oauth_forward_user_token = 1;
```

The realistic setup is a shared lakehouse with an enforcing catalog: it accepts or rejects each
request by its token and grants different principals different namespaces. Every requirement
below is judged by what the catalog, the token endpoint, and STS receive, not only by what
[ClickHouse] reports.

Negative requirements name the expected error code:

| Code | Meaning |
|---|---|
| `CATALOG_USER_TOKEN_NOT_AVAILABLE` (780) | The query needs a user token and the session has none, forwarding is disabled on the server, or STS rejected the token. clickhouse-client exits with code 12 (780 mod 256). |
| `BAD_ARGUMENTS` | `CREATE DATABASE` carries an invalid combination of forwarding settings. |
| `UNACCEPTABLE_URL` | An endpoint that would receive a user token is outside `remote_url_allow_hosts`. |
| `AUTHENTICATION_FAILED` | The token failed verification at login (HTTP 403). |

Regression tests live under the TestFlows package `iceberg.tests.iceberg_engine.token_forwarding`
and run as `/iceberg/token forwarding`. The environment has an Iceberg REST fixture catalog behind
a recording proxy that can enforce a per-principal namespace allowlist, inject failures, and vend
per-principal storage credentials. It also has a mock RFC 8693 token endpoint and a mock STS.
Tokens are HS256 JWTs verified by a static-key token processor, and token users come from the
`token` user directory. Glue calls made after STS need LocalStack; without it, Glue scenarios
check only the STS side.

Out of scope: token authentication to [ClickHouse] itself (SRS-042), the catalogs' own
authorization models, and catalog types other than REST and Glue.

[ClickHouse]: https://clickhouse.com

### Terminology

| Term | Meaning |
|---|---|
| user token | The bearer token the client authenticated to [ClickHouse] with: `Authorization: Bearer` over HTTP, or `--jwt` over the native protocol. |
| principal | The canonical [ClickHouse] user name the token resolved to through the token user directory, not a name the client sent. |
| fingerprint | A hash of the user token. Every per-user cache keys on it. |
| service identity | What the database uses when forwarding is off: `catalog_credential` or `auth_header` (REST), static AWS keys or the default AWS chain (Glue). |
| forwarding database | A `DataLakeCatalog` database with `oauth_forward_user_token = 1`. |
| exchanged token | The catalog session token returned by the RFC 8693 token endpoint in exchange mode. |
| vended credentials | Table-scoped object storage credentials the REST catalog returns with `loadTable`. |
| enforcing catalog | A catalog that authorizes each request by its token, so it can tell users apart. |

## Server Setting

### RQ.Iceberg.TokenForwarding.ServerSetting
version: 1.0

[ClickHouse] SHALL provide the server setting `enable_token_forwarding` (`Bool`, default `0`).
With the setting off, no session SHALL keep a user token, whatever the authentication method, and
a query on a forwarding database SHALL fail with `CATALOG_USER_TOKEN_NOT_AVAILABLE` and a message
that tells the user to set `enable_token_forwarding = 1` and reconnect. No request SHALL be sent
to the catalog, the token endpoint, or STS.

### RQ.Iceberg.TokenForwarding.ServerSetting.HotReload
version: 1.0

[ClickHouse] SHALL apply a change of `enable_token_forwarding` on `SYSTEM RELOAD CONFIG` without
a restart:

* after the setting is turned on, sessions that authenticate afterwards keep their token and
  forwarding works for them;
* after the setting is turned off, the next catalog request of every session, including sessions
  that already hold a token, fails with `CATALOG_USER_TOKEN_NOT_AVAILABLE`, and nothing is sent
  out;
* turning the setting off clears the per-user caches (exchanged tokens and assumed-role clients),
  so after it is turned back on the next query exchanges or assumes the role again.

### RQ.Iceberg.TokenForwarding.ServerSetting.ReportedAsHotReloadable
version: 1.0

`system.server_settings` SHALL report `changeable_without_restart` for `enable_token_forwarding`
as a value that says no restart is needed, consistent with
RQ.Iceberg.TokenForwarding.ServerSetting.HotReload.

```sql
SELECT changeable_without_restart
FROM system.server_settings
WHERE name = 'enable_token_forwarding';
```

Reasoning: operators read this column to decide whether a change needs a restart.

## Token Capture

### RQ.Iceberg.TokenForwarding.Capture.NativeJWT
version: 1.0

When a user connects over the native protocol with `--jwt` and `enable_token_forwarding = 1`,
[ClickHouse] SHALL forward that user's token for catalog requests made by the user's queries on a
forwarding database.

### RQ.Iceberg.TokenForwarding.Capture.HTTPBearer
version: 1.0

When a user authenticates over HTTP with `Authorization: Bearer <token>` and
`enable_token_forwarding = 1`, [ClickHouse] SHALL forward that token for catalog requests made by
the request's query on a forwarding database.

### RQ.Iceberg.TokenForwarding.Capture.VerifiedTokensOnly
version: 1.0

[ClickHouse] SHALL forward only a token that passed verification at login. A token with an
invalid signature, an expired `exp`, or failing `iss`, `aud`, or claim checks SHALL be rejected at
login with `AUTHENTICATION_FAILED`, and no catalog, token endpoint, or STS SHALL receive it.

### RQ.Iceberg.TokenForwarding.Capture.NonTokenUsers
version: 1.0

A session that did not authenticate with a token SHALL hold no user token. This covers users
authenticated by password, `no_password` (including `default`), LDAP, Kerberos, SSL certificate,
and HTTP Basic. Their queries on a forwarding database SHALL fail with
`CATALOG_USER_TOKEN_NOT_AVAILABLE` and a message saying that the session carries no bearer token
and how to send one. [ClickHouse] SHALL NOT fall back to the service identity or to an
unauthenticated request.

### RQ.Iceberg.TokenForwarding.Capture.Principal
version: 1.0

The principal attached to a forwarded token SHALL be the canonical user name the token user
directory resolved (through `username_claim`), not a client-supplied `X-ClickHouse-User` or
`user=` value. The principal SHALL be the name used in log messages and in the Glue
`RoleSessionName` (RQ.Iceberg.TokenForwarding.Glue.RoleSessionName).

## Token Propagation

### RQ.Iceberg.TokenForwarding.Propagation.EveryCatalogRequest
version: 1.0

Every catalog request made for a query on a forwarding database SHALL carry a token derived from
that query's user: `/v1/config`, namespace and table listing, `EXISTS`, `loadTable`, vended
credential fetches, `INSERT` commits, `ALTER` schema commits, mutations, and `DROP TABLE`. When
user A and user B run the same statement against the same table in turn, A's requests SHALL carry
A's token and B's requests SHALL carry B's token.

### RQ.Iceberg.TokenForwarding.Propagation.Concurrency
version: 1.0

Concurrent queries from different users on the same forwarding database SHALL each reach the
catalog with their own token. No request SHALL carry another concurrent user's token.

### RQ.Iceberg.TokenForwarding.Propagation.ExecuteAs
version: 1.0

A context that runs as a different user than the one who authenticated SHALL have no user token.
A query run with `EXECUTE AS <user>`, as a statement or as a session switch, SHALL fail on a
forwarding database with `CATALOG_USER_TOKEN_NOT_AVAILABLE`, and the catalog SHALL receive no
request carrying the caller's token. A view with `SQL SECURITY DEFINER` reading a forwarding
database SHALL NOT run with the invoker's token.

### RQ.Iceberg.TokenForwarding.Propagation.HTTPSession
version: 1.0

Within one named HTTP session (`session_id`), [ClickHouse] SHALL forward the token presented with
the current request. When the same user sends a new token on a later request in the same session,
the catalog SHALL receive the new token. A native TCP session SHALL keep the token it logged in
with until it reconnects.

### RQ.Iceberg.TokenForwarding.Propagation.LocalNodeOnly
version: 1.0

The user token SHALL NOT leave the node the user authenticated to. It SHALL NOT be sent to other
[ClickHouse] nodes through `remote()`, `cluster()`, `Distributed` tables, `object_storage_cluster`
reads, or any interserver traffic. A query that makes another node access a forwarding database
SHALL NOT give that node the user's token, so that node's catalog access fails for lack of one.

### RQ.Iceberg.TokenForwarding.Propagation.RemoteNodeError
version: 1.0

When a query reaches another node (for example
`SELECT ... FROM remote('node2', forwarding_db, 'ns.t')`) and that node cannot access the
forwarding catalog because it has no user token, the initiator SHALL report
`CATALOG_USER_TOKEN_NOT_AVAILABLE` from the remote node. The remote node SHALL NOT close the
connection without an answer, and the initiator SHALL NOT report the failure as a network error
such as `ATTEMPT_TO_READ_AFTER_EOF` or `ALL_CONNECTION_TRIES_FAILED`.

### RQ.Iceberg.TokenForwarding.Propagation.Confidentiality
version: 1.0

The user token, any exchanged token, the actor token, and STS session credentials SHALL NOT appear
in any of:

* `metadata/*.sql` or `SHOW CREATE DATABASE`;
* `system.query_log`, `system.text_log`, `system.processes`, or `system.session_log`;
* the server log or error log;
* exception messages returned to the client, including errors caused by the token endpoint.

[ClickHouse] SHALL NOT include the token endpoint's error response body in errors or logs, because
that body may echo the subject token.

## Database Configuration

### RQ.Iceberg.TokenForwarding.Database.OptIn
version: 1.0

Forwarding SHALL be opt-in per database. With `enable_token_forwarding = 1`, a `DataLakeCatalog`
database without `oauth_forward_user_token = 1` SHALL behave as without forwarding: it uses its
service identity, it loads `/v1/config` at `CREATE`, it shares vended credentials between users as
before, and the catalog never receives a user token. Token users and password users SHALL get the
same results from such a database.

### RQ.Iceberg.TokenForwarding.Database.SupportedCatalogs
version: 1.0

[ClickHouse] SHALL support `oauth_forward_user_token = 1` only for `catalog_type = 'rest'` and
`catalog_type = 'glue'`. For any other catalog type, `CREATE DATABASE` SHALL fail with
`BAD_ARGUMENTS`.

### RQ.Iceberg.TokenForwarding.Database.InvalidRESTSettings
version: 1.0

For a REST catalog, `CREATE DATABASE` SHALL fail with `BAD_ARGUMENTS` when it combines
`oauth_forward_user_token = 1` with any of the following, and afterwards the database SHALL NOT
exist and the catalog SHALL have received no request:

| Combination | Reason |
|---|---|
| `auth_header` | A fixed header would bypass the user. |
| `oauth_token_exchange_uri` without `catalog_credential` | The exchange needs a client identity. |
| `oauth_forward_actor_token = 1` without `oauth_token_exchange_uri` | Delegation is an exchange feature. |
| `oauth_subject_token_type` empty or not an RFC 8693 token type URN | |
| `oauth_requested_token_type` not an RFC 8693 token type URN (empty is allowed) | |

### RQ.Iceberg.TokenForwarding.Database.ExchangeSettingsRequireForwarding
version: 1.0

`CREATE DATABASE` SHALL fail with `BAD_ARGUMENTS` and a message saying the setting has no effect
when any of `oauth_token_exchange_uri`, `oauth_subject_token_type`, `oauth_requested_token_type`,
`oauth_forward_actor_token`, or `oauth_user_token_cache_ttl` is set without
`oauth_forward_user_token = 1`. The same SHALL apply when any of these except
`oauth_token_exchange_uri` is set without `oauth_token_exchange_uri`.

### RQ.Iceberg.TokenForwarding.Database.TokenTypes
version: 1.0

[ClickHouse] SHALL accept each RFC 8693 token type URN as `oauth_subject_token_type` and as
`oauth_requested_token_type`:

* `urn:ietf:params:oauth:token-type:access_token`
* `urn:ietf:params:oauth:token-type:refresh_token`
* `urn:ietf:params:oauth:token-type:id_token`
* `urn:ietf:params:oauth:token-type:saml1`
* `urn:ietf:params:oauth:token-type:saml2`
* `urn:ietf:params:oauth:token-type:jwt`

### RQ.Iceberg.TokenForwarding.Database.InvalidGlueSettings
version: 1.0

For a Glue catalog, `CREATE DATABASE` with `oauth_forward_user_token = 1` SHALL fail with
`BAD_ARGUMENTS` when `aws_role_arn` is missing, when `aws_access_key_id` or
`aws_secret_access_key` is set, or when the REST-only settings `oauth_token_exchange_uri` or
`oauth_forward_actor_token` are set.

### RQ.Iceberg.TokenForwarding.Database.DetachAttach
version: 1.0

A forwarding database SHALL keep forwarding user tokens after `DETACH DATABASE` followed by
`ATTACH DATABASE`, and after a server restart. A database persisted with a setting that
`CREATE DATABASE` would now reject as having no effect SHALL still attach at startup.

### RQ.Iceberg.TokenForwarding.Database.HostFilter
version: 1.0

Every endpoint that may receive a user token SHALL be checked against `remote_url_allow_hosts`:
the catalog URL, `oauth_token_exchange_uri`, `oauth_server_uri`, and `aws_sts_endpoint`. For an
endpoint whose host is not allowed, [ClickHouse] SHALL fail with `UNACCEPTABLE_URL`, at
`CREATE DATABASE` or at the latest before the first request, and the endpoint SHALL NOT receive
the user token.

## REST Passthrough

### RQ.Iceberg.TokenForwarding.REST.Passthrough
version: 1.0

On a forwarding REST database with an empty `oauth_token_exchange_uri`, every catalog request
SHALL carry `Authorization: Bearer <user token>`, the token being byte for byte the one the client
presented. No token endpoint SHALL be contacted, and `DataLakeRestCatalogTokenExchange` SHALL stay
`0`.

### RQ.Iceberg.TokenForwarding.REST.NoServiceFallback
version: 1.0

A forwarding REST database SHALL NOT send the service identity to the catalog, neither instead of
a missing user token nor alongside a forwarded one. The catalog SHALL never receive a token
obtained with `catalog_credential` through `client_credentials`, and
`DataLakeRestCatalogAuthTokenRetrieve` SHALL stay `0` unless `oauth_forward_actor_token = 1`. A
query without a user token SHALL fail before any network request.

### RQ.Iceberg.TokenForwarding.REST.PerUserAuthorization
version: 1.0

Users querying one forwarding database through an enforcing catalog SHALL get the catalog's
authorization for their own principal:

* `SHOW TABLES` lists only the tables the user's principal may see;
* a `SELECT` from a table the catalog denies to the user fails with the catalog's denial and
  returns no data;
* a user's access never widens because another user queried the same table first.

Effective access SHALL be the intersection of the user's [ClickHouse] grants and the catalog's
grants to that principal. A user without the needed [ClickHouse] grant SHALL get `ACCESS_DENIED`
before the catalog is contacted.

### RQ.Iceberg.TokenForwarding.REST.Config
version: 1.0

A forwarding REST database SHALL NOT call `/v1/config` at `CREATE DATABASE` or `ATTACH DATABASE`.
The first catalog operation that has a user token SHALL load `/v1/config` with that token.

### RQ.Iceberg.TokenForwarding.REST.Passthrough.NoRetry
version: 1.0

In passthrough mode, when the catalog rejects the user token with `401` or `403`, [ClickHouse]
SHALL report the rejection to the user after one request. It SHALL NOT retry with another
credential.

## REST Token Exchange

### RQ.Iceberg.TokenForwarding.REST.Exchange.Request
version: 1.0

With `oauth_token_exchange_uri` set, [ClickHouse] SHALL exchange the user token with a
form-encoded `POST` to that URI that has no `Authorization` header and contains:

* `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`;
* `subject_token=<user token>`;
* `subject_token_type=<oauth_subject_token_type>`, by default
  `urn:ietf:params:oauth:token-type:access_token`;
* `requested_token_type=<oauth_requested_token_type>` when the setting is not empty, by default
  `urn:ietf:params:oauth:token-type:access_token`;
* `scope=<auth_scope>` when the setting is not empty, by default `PRINCIPAL_ROLE:ALL`;
* `client_id` and `client_secret` taken from `catalog_credential`.

### RQ.Iceberg.TokenForwarding.REST.Exchange.CatalogReceivesExchangedToken
version: 1.0

In exchange mode, every catalog request SHALL carry `Authorization: Bearer <exchanged token>`.
The catalog SHALL never receive the raw user token.

### RQ.Iceberg.TokenForwarding.REST.Exchange.ActorToken
version: 1.0

With `oauth_forward_actor_token = 1`, [ClickHouse] SHALL obtain a service token with
`catalog_credential` through `client_credentials` and send it in the exchange request as
`actor_token`, with
`actor_token_type=urn:ietf:params:oauth:token-type:access_token`. Without the setting, the
exchange request SHALL carry neither field.

### RQ.Iceberg.TokenForwarding.REST.Exchange.Cache
version: 1.0

[ClickHouse] SHALL cache exchanged tokens per user token:

* a repeated query with the same user token reuses the exchanged token, with no new exchange
  request, and counts `DataLakeRestCatalogUserTokenCacheHits`;
* a different token, of another user or of the same user, gets its own exchange;
* two users never share a cache entry.

### RQ.Iceberg.TokenForwarding.REST.Exchange.CacheLifetime
version: 1.0

An exchanged token SHALL NOT be reused after the earlier of:

* the `expires_in` returned by the token endpoint, minus a safety margin;
* `oauth_user_token_cache_ttl` seconds.

When the token endpoint omits `expires_in`, the exchanged token SHALL still expire after
`oauth_user_token_cache_ttl`. With `oauth_user_token_cache_ttl = 0`, [ClickHouse] SHALL exchange
the user token for every catalog request and cache nothing.

### RQ.Iceberg.TokenForwarding.REST.Exchange.Failure
version: 1.0

When the token exchange fails (an error status from the token endpoint, the endpoint rejecting
`catalog_credential`, or the endpoint unreachable), the query SHALL fail with an error that
identifies the OAuth token endpoint by scheme, host, port, and path only. The catalog SHALL
receive no request, and
`DataLakeRestCatalogTokenExchangeFailures` SHALL increase. [ClickHouse] SHALL NOT fall back to
passthrough or to the service identity, and the error SHALL NOT contain the user token
(RQ.Iceberg.TokenForwarding.Propagation.Confidentiality).

### RQ.Iceberg.TokenForwarding.REST.Exchange.RetryOnUnauthorized
version: 1.0

In exchange mode, when the catalog answers `401` to an exchanged token, [ClickHouse] SHALL
exchange the user token again and retry the request once. A `403` SHALL NOT be retried.

## Vended Credentials

### RQ.Iceberg.TokenForwarding.VendedCredentials.PerUser
version: 1.0

On a forwarding REST database, storage credentials vended by the catalog for one user SHALL NOT
be used for another user's query on the same table, whichever user reads first. Each user's object
storage reads SHALL use the credentials vended for that user's principal. A credential change
(RQ.Iceberg.TokenForwarding.CredentialRotation) SHALL clear the vended credentials cache.

## Writes

### RQ.Iceberg.TokenForwarding.Writes.Insert
version: 1.0

An `INSERT` into a table in a forwarding database SHALL commit to the catalog with the inserting
user's token.

### RQ.Iceberg.TokenForwarding.Writes.AsyncInsert
version: 1.0

With `async_insert = 1`, [ClickHouse] SHALL commit each batch with the token of the inserts it
contains:

* a batch SHALL be committed with the inserting user's token, even with
  `wait_for_async_insert = 0`, and even when the flush is triggered by a session without a token;
* inserts carrying different tokens, of different users or of the same user, SHALL NOT be
  merged into one batch, so each commit carries exactly one token.

### RQ.Iceberg.TokenForwarding.Writes.DropTable
version: 1.0

`DROP TABLE` on a table in a forwarding database SHALL reach the catalog with the querying user's
token, and SHALL NOT request a service token
(`DataLakeRestCatalogAuthTokenRetrieve` stays `0`).

## AWS Glue

### RQ.Iceberg.TokenForwarding.Glue.AssumeRoleWithWebIdentity
version: 1.0

On a forwarding Glue database, [ClickHouse] SHALL call STS `AssumeRoleWithWebIdentity` with
`RoleArn = aws_role_arn` and `WebIdentityToken = <user token>`, unsigned, at the STS endpoint given
by `aws_sts_endpoint` (or the default AWS STS endpoint). Each user SHALL assume the role with their
own token. The resulting temporary credentials SHALL sign every Glue request and every object
storage read for that user's queries, and the default AWS credential chain SHALL NOT be used.

### RQ.Iceberg.TokenForwarding.Glue.RoleSessionName
version: 1.0

The `RoleSessionName` SHALL identify the principal and SHALL be valid for AWS:

* a principal of 2 to 64 characters from `[\w+=,.@-]` is used unchanged;
* otherwise the allowed characters are kept, truncated, and followed by `-` and a hash of the full
  principal;
* a principal with no allowed characters becomes `ClickHouseUser-<hash>`;
* different principals SHALL get different session names.

### RQ.Iceberg.TokenForwarding.Glue.ClientCache
version: 1.0

[ClickHouse] SHALL reuse the assumed-role client for repeated queries with the same user token:
the second query SHALL make no STS call and SHALL count `DataLakeGlueCatalogUserClientCacheHits`.
A new token, even for the same user, SHALL cause a new STS call.

### RQ.Iceberg.TokenForwarding.Glue.RejectedToken
version: 1.0

When STS rejects the user's token, the query SHALL fail with `CATALOG_USER_TOKEN_NOT_AVAILABLE`
and a message that names the role, the principal, and the STS error. [ClickHouse] SHALL make
exactly one STS request and no Glue request, SHALL NOT fall back to other credentials, and SHALL
increase `DataLakeGlueCatalogAssumeRoleWithWebIdentityFailures`.

### RQ.Iceberg.TokenForwarding.Glue.NonTokenUsers
version: 1.0

On a forwarding Glue database, a user without a token SHALL get
`CATALOG_USER_TOKEN_NOT_AVAILABLE`, and [ClickHouse] SHALL NOT call STS.

## Credential Rotation

### RQ.Iceberg.TokenForwarding.CredentialRotation
version: 1.0

On a forwarding REST database, `ALTER DATABASE ... MODIFY SETTING catalog_credential` SHALL:

* require a user token, and otherwise fail with `CATALOG_USER_TOKEN_NOT_AVAILABLE` and change
  nothing;
* validate the new credential before applying it, and on failure leave the old settings, the
  persisted metadata, and every cache unchanged;
* on success, clear the exchanged-token cache and the vended credentials cache, so the next query
  exchanges the user token with the new credential.

## Observability

### RQ.Iceberg.TokenForwarding.Observability.ProfileEvents
version: 1.0

For each query, `system.query_log` `ProfileEvents` SHALL agree with the requests actually made:

| Profile event | Counts |
|---|---|
| `DataLakeRestCatalogTokenExchange` | Exchange requests sent to the token endpoint |
| `DataLakeRestCatalogTokenExchangeFailures` | Exchange requests that failed |
| `DataLakeRestCatalogUserTokenCacheHits` | Catalog requests that reused a cached exchanged token |
| `DataLakeGlueCatalogAssumeRoleWithWebIdentity` | STS requests |
| `DataLakeGlueCatalogAssumeRoleWithWebIdentityFailures` | STS requests that returned no credentials |
| `DataLakeGlueCatalogUserClientCacheHits` | Queries served by a cached assumed-role client |

Forwarded queries SHALL NOT count `DataLakeRestCatalogAuthTokenRetrieve` unless
`oauth_forward_actor_token = 1`.

### RQ.Iceberg.TokenForwarding.Observability.Metrics
version: 1.0

`system.metrics` SHALL report the number of entries in the exchanged-token cache as
`DataLakeCatalogUserTokenCacheEntries`, and in the assumed-role client cache as
`DataLakeCatalogUserClientCacheEntries`. Both SHALL drop to `0` after
`enable_token_forwarding` is turned off (RQ.Iceberg.TokenForwarding.ServerSetting.HotReload),
and the exchanged-token count SHALL drop to `0` after a credential rotation.

### RQ.Iceberg.TokenForwarding.Observability.ErrorMessages
version: 1.0

Every `CATALOG_USER_TOKEN_NOT_AVAILABLE` message SHALL name the catalog and tell the user what to
do: set `enable_token_forwarding = 1` and reconnect, or authenticate with an
`Authorization: Bearer` HTTP header or `--jwt` over the native protocol. No message SHALL contain a
token.
