# Native CREATE TABLE / DROP TABLE for DataLakeCatalog — Test Plan

Specification: `iceberg/requirements/native_create_drop.md` (SRS-049).
Package: `iceberg.tests.iceberg_engine.native_create`.

This plan replaces the earlier one, which described only the explicit
`ENGINE = IcebergS3(...)` form. The feature now has three creation paths and a
purge-capable `DROP TABLE`, and every scenario below is judged by what the
catalog and object storage contain, not only by what ClickHouse reports.

---

## 1. What the user does, and what can break

| User action | What they expect | What could break |
|---|---|---|
| `CREATE TABLE db.\`ns.t\` (cols) PARTITION BY ... ORDER BY ...` with no engine | Table appears in the catalog, is empty, accepts INSERT, other engines read it | Location derived wrongly, namespace nested inside a table, invalid transform registered, metadata file missing or malformed, first INSERT writes a null parent snapshot |
| `CREATE TABLE db.\`ns.t\` AS mt_table` | Same columns; partition/sort keys carried when Iceberg can express them | Source modifiers (DEFAULT, CODEC, TTL, COMMENT) silently dropped; source engine SETTINGS leak; explicit keys lose to inherited ones |
| `CREATE TABLE ... ENGINE = IcebergS3(...)` in the catalog db | Same result as engine-less, plus engine SETTINGS honoured | Backend mismatch produces an unreadable table; generic `Iceberg` engine accepted then unreadable; different validation than the engine-less path |
| Re-run a deployment script (`IF NOT EXISTS`) | Idempotent, never fills a table someone else created | Loser of a race leaves a staged metadata file; `IF NOT EXISTS` reports success for a table the catalog cannot see |
| `DROP TABLE` | Table gone from catalog, data kept | Data deleted when not asked; table not droppable because it was never loaded |
| `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1` | Data gone too | Setting lost on the way to the background drop; Glue silently orphans data; alias name stops working |
| Recreate a table after a drop | Works after purge; clear error after keep | Overwrites leftover metadata; adopts leftover metadata silently |
| `CREATE ... ON CLUSTER` out of habit | Clear rejection | Every node races on one catalog entry; worker without a guard creates the table anyway |
| Multi-node lakehouse | Table created on node1 readable on node2/3 and via cluster functions | Nodes disagree on schema or location |
| Restricted user | Standard grants apply; no S3 keys needed | Creates possible without grant; drop possible without grant |

---

## 2. Structure

```
iceberg/tests/iceberg_engine/native_create/
    feature.py        entry point; @Specifications(SRS_049...); iterates catalog modes
    steps.py          shared steps (extended, see §4)
    sanity.py         happy paths for all three creation forms and both drop modes
    datatypes.py      existing scalar round trip, extended to both paths + nested + required/optional
    schema.py         PARTITION BY / ORDER BY translation and the rejection matrix
    location.py       base-location precedence, storage_endpoint derivation, uri style, backend checks
    namespaces.py     auto-create, default location placement, nested and filtered namespaces
    explicit_engine.py engine family / backend mismatch / generic engine / initial file naming
    metadata.py       initial metadata content, compression, first commit, external readers
    idempotency.py    IF NOT EXISTS, concurrent creates, leftover metadata, no-trace on failure
    drop.py           keep vs purge, setting + alias, query-level capture, IF EXISTS, Glue, S3 Tables
    on_cluster.py     ON CLUSTER rejection (initiator + worker), shared-catalog visibility
    lifecycle.py      insert/alter/select after create, recreate after each drop mode, export destination
    rbac.py           CREATE TABLE / DROP TABLE privileges
```

`feature.py` follows `export_partition/feature.py`: it sets `self.context.catalog`
to each of `("rest", "glue")` and loads every module under a `Feature(f"{mode} catalog")`.
It is loaded directly from `iceberg/regression.py` (like `deletion_vectors`), not
from `iceberg_engine/feature.py`, because it owns its own catalog loop.

The old single-scenario `iceberg_engine/native_create_drop.py` is folded into
`sanity.py` and removed.

Catalog modes:

* `rest` — `ice-rest-catalog` on `:5000`, the suite's default REST catalog, reached
  through `iceberg_engine.create_experimental_iceberg_database`.
* `glue` — LocalStack Glue. Never reports a base location and is pinned to S3, so it
  is the clean place for `storage_endpoint` derivation and backend-mismatch scenarios.
* The Apache `iceberg-rest-fixture` on `rest:8181` is used only inside `metadata.py`
  for Spark interoperability (the Spark container's `demo` catalog points at it), via
  the `catalog_database` step pattern from `deletion_vectors/steps/common.py`.

Creation paths are a second dimension inside modules where behaviour must match:
`("engine_less", "explicit_engine", "as_source")`. Scenarios that vary both the
path and an input class use `testflows.combinatorics.product` and a `Check` per
combination, the way `iceberg_engine/row_policy.py` and `column_rbac.py` do.

---

## 3. Modules and scenarios

Legend: **S** single scenario, **O** outline with examples, **P** product loop with
one `Check` per combination. `RQ` names omit the `RQ.Iceberg.NativeCreateDrop.` prefix.

### 3.1 `sanity.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Engine-less create: `SHOW TABLES`, `system.tables`, `count() = 0`, PyIceberg `load_table`, INSERT then SELECT | S | CreateTable |
| 2 | Explicit `IcebergS3` create: same assertions; PyIceberg sees identical shape to engine-less | S | CreateTable.ExplicitEngine |
| 3 | `AS` a MergeTree source with `PARTITION BY toRelativeDayNum(d)` and `ORDER BY (a, b)`: keys copied; `INSERT ... SELECT` from source; row counts match | S | CreateTable.AsSource |
| 4 | `AS` source with explicit `PARTITION BY` / `ORDER BY` on the new table: explicit keys win | S | CreateTable.AsSource |
| 5 | `AS` source whose keys use `toYYYYMM`: rejected with `BAD_ARGUMENTS` ("Unsupported function for iceberg partitioning"), no trace. The server copies the source key unconditionally and `getPartitionField` rejects it | S | CreateTable.AsSource |
| 6 | Drop keeps data by default: object inventory identical before and after; PyIceberg no longer lists the table | S | Drop, Drop.KeepData |
| 7 | Drop with purge: zero objects under the table prefix | S | Drop.Purge |
| 8 | Drop a table created by PyIceberg, through a fresh database that never read it | S | Drop |
| 9 | Unsupported catalog type rejects both statements (`catalog_type = 'unity'` if the build can create it, else skip with reason) | S | SupportedCatalogs |

### 3.2 `datatypes.py` (extend existing)

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Scalar round trip, existing `SCALAR_TYPE_CONFIGS`, now run under both `engine_less` and `explicit_engine` | O | Schema.Columns |
| 2 | Nested: `Array(Int64)`, `Array(Array(String))`, `Map(String, Int64)`, `Tuple(a Int64, b String)`, `Array(Tuple(...))`; PyIceberg schema shows `list` / `map` / `struct` with element ids | O | Schema.Columns |
| 3 | `Nullable(T)` → optional, plain `T` → required, checked on the PyIceberg schema; NULL round trip | S | Schema.Columns |
| 4 | Empty column list → `INCORRECT_QUERY` (generic validation, before the DataLakeCatalog code; the PR's own "Cannot create table without columns" is unreachable from SQL) on the engine-less path; with an explicit engine a column-less CREATE is schema inference from the path and fails with `FILE_DOESNT_EXIST` when nothing is there (2026-09-15) | S | Schema.Columns |
| 5 | Unsupported writer types (`FixedString`) → `BAD_ARGUMENTS` "Unsupported type for iceberg", no trace; the former `scalar fixed` round trip could never pass (2026-09-15) | S | Schema.Columns |

### 3.3 `schema.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Accepted transforms × applicable column types: identity on Int64/String/Date; year/month/day/hour on Date and DateTime; `icebergTruncate(4, s)` on String and Int; `icebergBucket(8, x)` on Int and String; composite `(identity, bucket)`. Assert PyIceberg spec transform strings, insert one row per partition, `SELECT` with partition predicate returns the row, each data file's manifest entry carries the partition value (PyIceberg `plan_files`); ClickHouse writes flat `data/data-<uuid>.parquet` paths and the spec prescribes no directory layout (2026-09-15) | P | Schema.PartitionBy |
| 2 | No `PARTITION BY` → empty spec | S | Schema.PartitionBy |
| 3 | Rejected expressions: `toYYYYMM(d)`, `intDiv(x, 10)`, `x % 7`, `cityHash64(s)`, `toStartOfMonth(d)`, composite with one bad member. `BAD_ARGUMENTS`; table absent from catalog; prefix empty; namespace not created | O | Schema.PartitionBy.RejectedExpressions, FailedCreateLeavesNoTrace |
| 4 | `icebergBucket` / `icebergTruncate` × N in `{0, -1}`: `BAD_ARGUMENTS`, nothing registered | P | Schema.PartitionBy.TransformParameters |
| 5 | `ORDER BY` none / single / multi: PyIceberg sort order fields and non-zero `order-id` when non-empty | O | Schema.OrderBy |
| 6 | Storage clauses `PRIMARY KEY`, `SAMPLE BY`, `TTL`, engine `SETTINGS` × paths `engine_less`, `as_source` (explicit on the AS statement); plus the same clauses minus `SETTINGS` on `explicit_engine`. `BAD_ARGUMENTS` naming the clause | P | Schema.UnsupportedStorageClauses |
| 7 | Column modifiers `DEFAULT`, `MATERIALIZED`, `ALIAS`, `EPHEMERAL`, `COMMENT`, `CODEC`, `TTL`, `STATISTICS`, column `SETTINGS`, column `PRIMARY KEY` × paths `engine_less`, `explicit_engine`, `as_source` (modifier on the source table). `BAD_ARGUMENTS` naming the column | P | Schema.UnsupportedColumnModifiers |
| 8 | Index, constraint, projection, table-level `PRIMARY KEY` in column list, table `COMMENT`, `AS` source with a comment → `BAD_ARGUMENTS` | O | Schema.UnsupportedTableElements |
| 9 | `CREATE VIEW`, `CREATE MATERIALIZED VIEW`, `CREATE DICTIONARY`, `ATTACH TABLE`, `CLONE AS`, `CREATE OR REPLACE TABLE`, `REPLACE TABLE` → `NOT_IMPLEMENTED`, nothing in catalog | O | Schema.NonTableObjects |
| 10 | Explicit engine with `SETTINGS iceberg_format_version = 1` and `= 2`: metadata `format-version` matches (positive control for #6) | O | Schema.EngineSettings |

### 3.4 `location.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Database with `default_base_location = s3://warehouse/custom` (and the same with a trailing slash): PyIceberg `location == s3://warehouse/custom/<ns>/<t>`; `metadata/` and `data/` directly under it; `SHOW CREATE DATABASE` shows the setting | O | Location.DefaultBaseLocation, Location.Resolution |
| 2 | Glue, no base: `storage_endpoint = http://minio:9000/warehouse` → `s3://warehouse/<ns>/<t>`; `.../warehouse/prefix` → `s3://warehouse/prefix/<ns>/<t>` | O | Location.DerivedFromStorageEndpoint |
| 3 | Glue, `storage_endpoint = http://minio:9000/` → `BAD_ARGUMENTS` (no bucket) | S | Location.DerivedFromStorageEndpoint |
| 4 | Database with neither `default_base_location` nor `storage_endpoint` → `BAD_ARGUMENTS` naming both settings | S | Location.Resolution |
| 5 | REST catalog: if it reports a base, that base wins over `default_base_location` (assert whichever precedence the catalog makes observable; see §5) | S | Location.Resolution |
| 6 | `storage_uri_style = 'virtual_hosted'` without base → `BAD_ARGUMENTS` mentioning `default_base_location`; with base → registered in catalog at the expected location | O | Location.VirtualHostedStyle |
| 7 | Glue with `default_base_location = abfss://c@h.dfs.core.windows.net/x` → `BAD_ARGUMENTS`, no trace | S | Location.BackendConsistency |
| 8 | Azure derivation — skipped with reason (no Azure service) | S | Location.Azure |

### 3.5 `namespaces.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Namespace absent → created by the `CREATE`; PyIceberg lists it afterwards | S | Namespace.AutoCreate |
| 2 | Namespace pre-created by PyIceberg with custom properties → reused; properties unchanged after the `CREATE` | S | Namespace.AutoCreate |
| 3 | Rejected `CREATE` (bad transform) in a fresh namespace → namespace still absent | S | Namespace.AutoCreate, FailedCreateLeavesNoTrace |
| 4 | Engine-less first table, then second table in the same namespace without explicit location: `load_namespace_properties()['location'] == <base>/<ns>`; second table at `<base>/<ns>/<t2>`, not under `<t1>` | S | Namespace.DefaultLocation |
| 5 | Explicit engine whose URL follows `<base>/<ns>/<t>/` → namespace location registered; URL that does not (`warehouse/custom_<t>/`) → no namespace location, and a later engine-less table does not nest inside it | O | Namespace.DefaultLocation |
| 6 | Nested `a.b.c`: create, INSERT, `ALTER ADD COLUMN`, SELECT; PyIceberg `list_tables(("a","b","c"))` (REST only; Glue has flat databases → skip with reason) | S | Namespace.Nested |
| 7 | Database with `namespaces = '<allowed>'`: `CREATE` and `DROP` in another namespace → `CATALOG_NAMESPACE_DISABLED`; catalog untouched; the same statements in the allowed namespace work. Follow the pattern in `iceberg_engine/namespace_filtering.py` | O | Namespace.Filtered |

### 3.6 `explicit_engine.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | `ENGINE = MergeTree`, `Memory`, `S3(...)`, `DeltaLake(...)` → `BAD_ARGUMENTS` naming the engine | O | ExplicitEngine.IcebergFamilyOnly |
| 2 | Glue × `IcebergAzure`, `IcebergLocal`, `IcebergHDFS` → `BAD_ARGUMENTS` with "reopened ... unreadable" and "stores tables on S3"; `IcebergS3` accepted | O | ExplicitEngine.BackendMismatch |
| 3 | Glue × generic `Iceberg(...)` → `BAD_ARGUMENTS` directing to a backend-specific engine | S | ExplicitEngine.GenericIcebergEngine |
| 4 | REST: run #2 and #3 only if the catalog reports a base (fixed backend); otherwise assert any `Iceberg*` engine is accepted at DDL level | S | ExplicitEngine.BackendMismatch |
| 5 | Initial file naming: REST explicit → `metadata/v1-<uuid>.metadata.json`; Glue explicit → `metadata/v1.metadata.json`; REST engine-less → server-named `00000-<uuid>.metadata.json` (found 2026-09-15); `iceberg_use_version_hint = 1` → `version-hint.text` containing `1` | O | Metadata.InitialFile |

### 3.7 `metadata.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Initial file × paths `engine_less`, `explicit_engine`: exactly one object under `metadata/`; catalog `metadata_location` points at it; parsed JSON has the expected `format-version`, one schema with the declared fields, one partition spec, one sort order, empty `snapshots`, no current snapshot, empty `metadata-log` | P | Metadata.InitialFile |
| 2 | `iceberg_metadata_compression_method = 'gzip'` × `explicit_engine` (both catalogs) and `engine_less` on Glue: `metadata_location` ends `.gzip.metadata.json`, object starts with `1f 8b`, INSERT + SELECT work afterwards; `engine_less` on REST: setting has no effect, table still works | P | Metadata.Compression |
| 3 | First INSERT: new metadata's snapshot has no `parent-snapshot-id` key, `current-snapshot-id` set, `metadata-log[0].metadata-file` equals the initial file; second INSERT chains to the first snapshot | S | Metadata.FirstCommit |
| 4 | PyIceberg reads rows ClickHouse inserted; schema, spec, sort order, location match (both catalogs, both paths) | P | Metadata.ExternalReader |
| 5 | Spark (REST fixture on `rest:8181`): engine-less create in ClickHouse → Spark `SELECT` sees ClickHouse rows; Spark `INSERT` → ClickHouse sees Spark rows | S | Metadata.ExternalReader |

### 3.8 `idempotency.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | `IF NOT EXISTS` on a table created by ClickHouse and on one created by PyIceberg: success, `metadata_location` and rows unchanged; without → `TABLE_ALREADY_EXISTS` | O | IfNotExists |
| 2 | `CREATE TABLE IF NOT EXISTS ... AS SELECT` on an existing table → no rows added | S | IfNotExists |
| 3 | Concurrent creators: 3 nodes (each with its own database over the same catalog) × `IF NOT EXISTS` on/off, repeated several rounds through a `Pool`: exactly one success per round without `IF NOT EXISTS`, all succeed with it; catalog has one table; exactly one metadata file under the prefix | P | IfNotExists.ConcurrentCreate |
| 4 | Concurrent creators on one node (two parallel queries in the same database) | S | IfNotExists.ConcurrentCreate |
| 5 | Leftover metadata after keep-drop (ClickHouse-created and PyIceberg-created variants): recreate → `TABLE_ALREADY_EXISTS` naming `data_lake_delete_data_on_drop`; with `IF NOT EXISTS` → success and table absent from catalog; leftover files untouched | O | LeftoverMetadata |
| 6 | Contrast: path-based `ENGINE = IcebergS3` outside a catalog with `IF NOT EXISTS` over existing metadata attaches and reads the old rows | S | LeftoverMetadata |
| 7 | No trace after every rejection class (bad transform, bad modifier, bad clause, bad location, non-table object): catalog has no table, no namespace, prefix has zero objects. Implemented as a shared `Then` step reused by `schema.py` and `location.py` | S | FailedCreateLeavesNoTrace |

### 3.9 `drop.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | Keep (default) vs purge (`= 1`) on REST: object inventory identical / empty; PyIceberg no longer lists the table in both cases | O | Drop.KeepData, Drop.Purge |
| 2 | Purge via the alias `iceberg_delete_data_on_drop = 1` behaves identically; `system.settings` lists `data_lake_delete_data_on_drop` with the alias; `system.settings_changes` has the entry | S | Drop.Setting |
| 3 | Path-based tables outside a catalog: storage `{IcebergS3, IcebergLocal}` × setting `{0, 1}`, `DROP TABLE ... SYNC SETTINGS ...`: file count is zero or unchanged | P | Drop.QueryLevelSetting |
| 4 | Server-wide default `1` (users.d profile) with query-level `0` → data kept; with no query override → data deleted | O | Drop.QueryLevelSetting |
| 5 | `DROP TABLE IF EXISTS` on a table not in the catalog → success; on a table PyIceberg dropped a moment ago → success; without `IF EXISTS` → `UNKNOWN_TABLE` | O | Drop.IfExists |
| 6 | Glue: keep-drop removes the entry and keeps files; purge-drop → `NOT_IMPLEMENTED` ("not supported for the Glue catalog"), table still registered and readable; `IF EXISTS` + purge on a missing table → no-op | O | Drop.Glue |
| 7 | S3 Tables — skipped with reason (no service) | S | Drop.S3Tables |

### 3.10 `on_cluster.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | `CREATE TABLE`, `DROP TABLE`, `ALTER TABLE ADD COLUMN`, `RENAME TABLE` with `ON CLUSTER replicated_cluster` on a node that has the database → `NOT_IMPLEMENTED` mentioning "shared"; `system.distributed_ddl_queue` gains no entry; catalog unchanged | O | OnCluster.Rejected |
| 2 | Database only on node1; node2 issues `CREATE ... ON CLUSTER`: query fails; node1's task in `system.distributed_ddl_queue` shows `NOT_IMPLEMENTED`; catalog has no table. Control: plain `CREATE TABLE ... ON CLUSTER` in `default` from node2 succeeds on all nodes | S | OnCluster.WorkerGuard |
| 3 | Databases on all 3 nodes over the same catalog: create on node1 → `SHOW TABLES` and `SELECT` on node2/3; `icebergS3Cluster` read; `parallel_replicas_for_cluster_engines` read; drop on node1 → absent on node2 | S | SharedCatalogVisibility |

### 3.11 `lifecycle.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | After create × paths: INSERT, `ADD COLUMN`, `DROP COLUMN`, `MODIFY COLUMN`, `RENAME COLUMN`, SELECT with partition predicate, `ALTER DELETE` (format v2), `TRUNCATE`; catalog `metadata_location` advances after each; PyIceberg observes the change | P | Lifecycle.InsertAlterSelect |
| 2 | Purge-drop then recreate same name → succeeds, empty | S | Lifecycle.Recreate |
| 3 | Keep-drop then recreate same name → refused; recreate under a database with a different `default_base_location` → succeeds; old files untouched | S | Lifecycle.Recreate |
| 4 | Engine-less table as `EXPORT PARTITION` destination from a `MergeTree` source with a matching identity partition key; exported rows readable through the catalog and by PyIceberg (Antalya only, reuse `export_partition/steps`) | S | Lifecycle.ExportPartitionDestination |

### 3.12 `rbac.py`

| # | Scenario | Kind | RQ |
|---|---|---|---|
| 1 | User without `CREATE TABLE ON db.*` → `ACCESS_DENIED`, nothing in catalog; after `GRANT` → succeeds | S | RBAC |
| 2 | User without `DROP TABLE ON db.*` → `ACCESS_DENIED`, table stays; after `GRANT` → succeeds | S | RBAC |

---

## 4. Shared steps to add or extend

`iceberg/tests/steps/iceberg_engine.py`

* `create_experimental_iceberg_database_with_rest_catalog` and `..._with_glue_catalog`:
  new optional kwargs `default_base_location`, `storage_uri_style`, and the ability to
  pass `storage_endpoint=None` to omit the setting.

`iceberg/tests/iceberg_engine/native_create/steps.py`

* `create_table(path, ...)` — one step for the three paths: builds the DDL for
  `engine_less`, `explicit_engine` (reusing `iceberg_s3_engine`), or `as_source`
  (takes a source table name); accepts `if_not_exists`, `partition_by`, `order_by`,
  `storage_clauses`, `column_modifiers`, `settings`, `exitcode`, `message`; registers
  a `DROP TABLE IF EXISTS` finaliser.
* `drop_table(name, purge=None, if_exists=False, sync=False, alias=False)`.
* `catalog_has_table(catalog, namespace, table)`, `catalog_has_namespace(...)`,
  `table_location(catalog, namespace, table)`, `namespace_location(...)`.
* `metadata_location(catalog, namespace, table)` and `read_metadata_json(location)`.
* `object_inventory(prefix)` — lift `list_keys` / `object_inventory` from
  `deletion_vectors/steps/s3_objects.py` into `iceberg/tests/steps/s3_objects.py`
  so both suites share it.
* `assert_no_trace(catalog, namespace, table, prefix, namespace_expected=False)` —
  the `Then` step every rejection scenario ends with.
* `spark_rest_database()` — database over `rest:8181` for the Spark scenario, wrapping
  the `catalog_database` pattern from `deletion_vectors/steps/common.py`.

`iceberg/regression.py`

* Load `iceberg.tests.iceberg_engine.native_create.feature` after `iceberg engine`.
* `ffails`: skip the whole feature on builds without the capability. Until a version
  boundary is known, gate with a probe step in `feature.py` that issues an engine-less
  `CREATE TABLE` in a throwaway database and skips the feature when the server answers
  with the pre-feature error; replace with `check_clickhouse_version` once released.

---

## 5. First-run unknowns

Status (2026-09-15): every §4 step and every §3 module is written (`steps.py`,
`iceberg/tests/steps/s3_objects.py`, one file per module). Nothing has run yet
against a build carrying PR 2305; the image is
`altinityinfra/clickhouse-server:2305-26.6.2.20001.altinityantalya`. Items 6-8
below were added while writing the modules.

These decide assertions and must be established against the real environment before
the affected scenarios are finalised:

1. **RESOLVED 2026-09-15: `ice-rest-catalog` does not report `default-base-location`,
   and the server refuses to derive a scheme from `storage_endpoint` for a REST catalog
   (`Cannot determine storage scheme for CREATE TABLE for catalog type 'ICEBERG_REST'`).
   Every fixture database on REST therefore sets `default_base_location = s3://warehouse/data`
   (`steps.database_base_location`); §3.4 #2 stays Glue-only and #4 asserts the REST refusal.**
   Original question: does `ice-rest-catalog` report `default-base-location`? If yes, it is a
   fixed-backend catalog: location precedence (§3.4 #5) and backend-mismatch on REST
   (§3.6 #4) become testable there, and `default_base_location` on the database is
   ignored for it. If no, `storage_endpoint` derivation is testable on REST as well
   as Glue.
2. **Does `ice-rest-catalog` honour `purgeRequested=true`?** If not, §3.9 #1 can only
   assert the catalog entry is gone, and the purge-object assertions move to the Apache
   REST fixture, which does purge.
3. **RustFS and virtual-hosted requests.** RustFS rejects virtual-hosted style, so
   §3.4 #6 asserts registration only, not a subsequent read.
4. **Glue nested namespaces.** LocalStack Glue database names with dots may be
   rejected; §3.5 #6 is REST-only until proven otherwise.
5. **Race timing in §3.8 #3.** Three nodes issuing the same `CREATE` may serialise
   often enough that the loser path never fires; the scenario repeats rounds until a
   conflict is observed or a bounded number of rounds passes, and reports which
   detection path (`409`, `AlreadyExists`, `PreconditionFailed`) was exercised.

---

6. **Engine-less `CREATE` over leftover metadata on REST.** The leftover check
   lives in `IcebergMetadata::createInitial` (explicit engine only). On the
   engine-less path the REST server writes the metadata itself and may create the
   table beside the old files. `idempotency.py` asserts the strict behaviour on the
   explicit path and records the engine-less outcome; decide after the first run
   whether the SRS should require refusal there.
7. **`RENAME ... ON CLUSTER` has no initiator check** in the PR; it is stopped by
   the worker guard, so a DDL-queue entry does appear. `on_cluster.py` asserts the
   failure but not an empty queue for `RENAME`.
8. **Schema `ALTER`s on catalog tables.** `lifecycle.py` runs ADD / RENAME / MODIFY /
   DROP COLUMN and `ALTER DELETE` as separate checks; whichever the build under
   test does not support fails individually and should be moved to `xfails`.

9. **FOUND 2026-09-15: purge leaves ClickHouse's own metadata files behind on REST.**
   Every commit (INSERT) writes `metadata/vN-<uuid>.metadata.json`, then
   `RestCatalog::updateMetadata` sends only snapshot updates and ice-rest-catalog writes
   its own `0000N-<uuid>.metadata.json`. The ClickHouse file is an orphan, so the
   server-side purge deletes everything it knows and leaves `vN-*`. Same code in
   upstream master, so not a PR 2305 regression, but PR 2305's leftover probe then
   refuses an explicit-engine re-CREATE at that location. Registered as xfails on the
   purge scenarios; §5 #2 (does ice honour `purgeRequested=true`) is answered: yes.

10. **FOUND 2026-09-15: `CREATE` in an existing namespace takes ~33 s on REST.**
    `RestCatalog::createNamespaceIfNotExists` posts without checking, the server
    answers 409, and the HTTP layer retries it ten times with backoff before the error
    is swallowed. Slows every multi-table scenario; `findings.md` finding 3.
11. **FOUND 2026-09-15: explicit-engine CREATE on REST leaves ClickHouse's `v1-<uuid>`
    file as an orphan next to the server's `00000-<uuid>` file** (the REST create route
    cannot register a client-written file). B1 cannot hold on that path; xfailed.
    `findings.md` finding 4.

12. **FOUND 2026-09-15: manifest lists lack Avro `field-id`s; PyIceberg cannot scan any
    table ClickHouse inserted into** (upstream fix ClickHouse#111786, not ported). Every
    scan-based assertion is xfailed as `Error`; `findings.md` finding 5.
13. **Harness: an outline with `Examples` expands only when called with no arguments.**
    All scenarios read the MinIO credentials from `self.context` and feature loops use
    `Scenario(run=scenario, flags=TE)`.

## 6. Deliberately out of scope

* §3.1 #9 (unsupported catalog type rejects both statements): needs a reachable
  Unity/Hive/Paimon catalog. The refusal sits behind `isTableExist`, which calls the
  catalog and rethrows errors, so a dummy endpoint never reaches it (found 2026-09-15).
  Skipped with reason until such a service is in `iceberg_env`.
* Fault injection inside the create (failed `version-hint.text` write, Glue
  `CreateTable` failing after staging). The rollback code exists but the environment
  has no hook to trigger it deterministically; the no-trace requirement is covered
  through the validation-rejection classes instead.
* Azure, HDFS, S3 Tables, OneLake, BigLake backends — carried by their own
  requirements and skipped with an explicit reason.
* The `DataLakeCatalog` database's own `CREATE DATABASE` options beyond the ones the
  feature reads (`default_base_location`, `storage_endpoint`, `storage_uri_style`,
  `namespaces`).
