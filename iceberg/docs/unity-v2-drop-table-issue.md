# Unity v2 DataLakeCatalog: DROP TABLE on an Iceberg table returns "dropTable is not implemented"

Target: [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse). No existing issue tracks this. [#112234](https://github.com/ClickHouse/ClickHouse/issues/112234) is a different `RestCatalog` path bug, and [#105038](https://github.com/ClickHouse/ClickHouse/issues/105038) is the older mixed-format design note.

---

## Type of problem

**Bug report** — something's broken

## Describe the situation

`DROP TABLE` on an Iceberg table in a Unity v2 `DataLakeCatalog` fails with `NOT_IMPLEMENTED`. The privilege check succeeds. After `GRANT DROP`, ClickHouse still refuses the drop and leaves the table in the catalog.

This showed up while running the Altinity Iceberg regression suite against `clickhouse/clickhouse-server:head`. The same scenario passes for `catalog_type = 'rest'`, where `RestCatalog::dropTable` is implemented.

This issue:

- Returns error code 48, `dropTable is not implemented`, on `26.10.1.1720`.
- Is an upstream gap in `UnityV2Catalog`. The class implements `createTable` and does not override `dropTable`, so the call hits the stub in `ICatalog::dropTable`.
- Arrived with [#115879](https://github.com/ClickHouse/ClickHouse/pull/115879) (merged 2026-09-24), which added the Unity v2 catalog. That pull request added create, insert, and alter support. Drop was left unimplemented.
- Has no existing upstream issue. [#112234](https://github.com/ClickHouse/ClickHouse/issues/112234) is `RestCatalog::dropTable` omitting the catalog prefix (HTTP 404). [#105038](https://github.com/ClickHouse/ClickHouse/issues/105038) asks for Iceberg support in Unity, which v2 already provides for reads.

---

## How to reproduce the behavior

### Environment

- **Version:** `26.10.1.1720` (`docker://clickhouse/clickhouse-server:head`)
- **Catalog:** OSS Unity Catalog, Iceberg REST mounted at `/api/2.1/unity-catalog/iceberg-rest`, warehouse `unity`, static S3 credentials, `vended_credentials = false`
- **Table:** any Iceberg table already committed in that warehouse. In this run it was created with PyIceberg against the Unity Iceberg REST endpoint.

### Steps

1. Attach the catalog.

```sql
SET allow_database_unity_catalog = 1;

CREATE DATABASE unity_db
ENGINE = DataLakeCatalog('http://unity-catalog:8080/api/2.1/unity-catalog')
SETTINGS
    catalog_type = 'unity',
    use_unity_catalog_v2 = 1,
    warehouse = 'unity',
    vended_credentials = false,
    storage_endpoint = 'http://minio:9000/warehouse',
    aws_access_key_id = '...',
    aws_secret_access_key = '...';
```

2. Confirm the Iceberg table is visible, then try to drop it as a user who has no `DROP` privilege.

```sql
SHOW TABLES FROM unity_db;
CREATE USER test_user;

DROP TABLE unity_db.`namespace.table`; -- SETTINGS user = 'test_user'
```

3. Grant `DROP` and drop the table again as that user.

```sql
GRANT DROP ON unity_db.`namespace.table` TO test_user;

DROP TABLE unity_db.`namespace.table`; -- SETTINGS user = 'test_user'
SHOW TABLES FROM unity_db;
```

---

## Expected behavior

Step 2 returns `ACCESS_DENIED` (code 497, client exit code 241).

Step 3 drops the table. `SHOW TABLES` no longer lists `namespace.table`. A following `SELECT` returns `UNKNOWN_TABLE` (code 60). That is what `catalog_type = 'rest'` does on 25.8 and newer, through `RestCatalog::dropTable`.

---

## Actual behavior

Step 2 behaves as expected:

```text
Code: 497. DB::Exception: test_user: Not enough privileges. ... To execute this query, it's necessary to have the grant DROP TABLE ON unity_db.`namespace.table`. (ACCESS_DENIED)
```

Step 3 fails, and `SHOW TABLES` still lists the table:

```text
Code: 48. DB::Exception: dropTable is not implemented. (NOT_IMPLEMENTED)
```

---

## Root cause analysis

`DatabaseDataLake` dispatches `DROP TABLE` to `ICatalog::dropTable`. `RestCatalog` overrides it and sends `DELETE` to the Iceberg REST endpoint (`src/Databases/DataLake/RestCatalog.cpp`). `UnityV2Catalog` (`src/Databases/DataLake/UnityV2Catalog.h`) overrides `createTable`, `createNamespaceIfNotExists`, and `getTableMetadata`, and does not override `dropTable`. The base implementation throws:

```cpp
void ICatalog::dropTable(...) const
{
    throw DB::Exception(DB::ErrorCodes::NOT_IMPLEMENTED, "dropTable is not implemented");
}
```

The exception is raised before any request is sent, so the Iceberg table stays in Unity Catalog. Access control runs first, which is why the unprivileged attempt returns code 497 and the privileged attempt returns code 48.

---

## Additional context

### Where it was found

- Local Altinity Iceberg regression, scenario `/iceberg/iceberg engine/unity catalog/rbac/drop table privilege`
- ClickHouse `26.10.1.1720`
- Log: the privileged `DROP TABLE` is the failing step. Cleanup (`DROP DATABASE`, and a catalog drop through PyIceberg) succeeds afterwards.

### Workaround

Drop the table through the Iceberg REST API (PyIceberg, or `DELETE` on `/api/2.1/unity-catalog/iceberg-rest/v1/namespaces/{namespace}/tables/{table}`). ClickHouse SQL cannot drop it on this build.
