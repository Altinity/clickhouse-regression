# Native CREATE / DROP for DataLakeCatalog — findings from the first runs

Build under test: PR Altinity/ClickHouse#2305 (port of ClickHouse/ClickHouse#98670),
package `clickhouse-common-static_26.6.2.20001.altinityantalya_amd64.deb`, commit
`6ec36d21729a28815041df233317bd454908c5a0`. Catalog: `ice-rest-catalog` 0.16.0 over
MinIO, from `iceberg/iceberg_env`. Runs on 2026-09-15 with

```
python3 regression.py --clickhouse-binary-path <deb url> \
  --only "/iceberg/native create/rest catalog/sanity/*" -o classic
```

Two product findings, both pre-existing on the branch and both interacting with what
PR 2305 adds, plus three environment facts that shaped the suite. Each finding lists
the evidence from the run, the mechanism in the source, the effect on the suite, and
the xfail that covers it.

---

## Finding 1 — Partition transforms `day` and `hour` are written in the plural

**Symptom.** After `CREATE TABLE ... AS source` with the source partitioned by
`toRelativeDayNum(d)`, PyIceberg reads the registered partition spec back as
`[(3, 'unknown')]` instead of `[(3, 'day')]`.

**Mechanism.** `getPartitionField` in
`src/Storages/ObjectStorage/DataLakes/Iceberg/Utils.cpp` writes

| ClickHouse expression | Written transform | Iceberg spec name |
|---|---|---|
| `toYearNumSinceEpoch` | `year` | `year` |
| `toMonthNumSinceEpoch` | `month` | `month` |
| `toRelativeDayNum` | **`days`** | `day` |
| `toRelativeHourNum` | **`hours`** | `hour` |

The Iceberg spec defines only the singular names. PyIceberg 0.9 parses the plural as
`unknown`; Java Iceberg's `Transforms.fromString` accepts only the singular, so Spark
would reject the table too. ClickHouse's own reader accepts both spellings
(`Utils.cpp` transform parsing), which is why the tables still work from ClickHouse and
the bug went unnoticed. Introduced with Iceberg write support (commit `3a13793d741d`,
2025-07-18), so it is in every Antalya branch and not in PR 2305. The PR's own
documentation table lists `day` and `hour`.

**Upstream status.** Fixed by ClickHouse/ClickHouse#114864 "Fix Iceberg partition
transform names for day and hour" (merged 2026-08-28, closes #114848). Upstream master
writes `day` / `hour`. No Altinity PR or issue references the fix; it is not in
`antalya-26.6`.

**Suite handling.** Assertions keep the spec-correct values. `iceberg/regression.py`
xfails:

- `/iceberg/native create/*/sanity/create as source copies keys`
- `/iceberg/native create/*/schema/accepted transforms/PARTITION BY toRelativeDayNum*`
- `/iceberg/native create/*/schema/accepted transforms/PARTITION BY toRelativeHourNum*`
- `/iceberg/native create/*/metadata/initial file/*`
- `/iceberg/native create/*/lifecycle/insert alter select*/PyIceberg sees the final schema and rows`

**Ask.** Port ClickHouse/ClickHouse#114864 to `antalya-26.6` and earlier Antalya
branches. Once ported, the xfails above turn into unexpected passes and are removed.

---

## Finding 2 — Every REST commit leaves an orphan metadata file, so purge cannot empty the location

**Symptom.** `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1` on a table
with one committed row. Before the drop the location held six objects, among them:

```
metadata/00000-8e1f2e64-....metadata.json   written by the catalog server at CREATE
metadata/00001-c681bc1d-....metadata.json   written by the catalog server at the INSERT commit (current)
metadata/v1-dd8b961b-....metadata.json      written by ClickHouse during the INSERT
```

After the drop the catalog entry is gone, ClickHouse logged
`Dropped table ... (purge=true)`, and exactly one object remains:
`metadata/v1-dd8b961b-....metadata.json`.

**Mechanism.** From the server log of the INSERT
(`IcebergStorageSink: Writing new metadata file .../metadata/v1-<uuid>.metadata.json`)
and the source:

1. `IcebergStorageSink` (`IcebergWrites.cpp`, commit flow around
   `catalog->updateMetadata`) writes `metadata/vN-<uuid>.metadata.json` for a
   transactional catalog (`FileNamesGenerator.cpp`).
2. `RestCatalog::updateMetadata` (`RestCatalog.cpp`) ignores the file path argument
   (`/*new_metadata_path*/`) and sends a commit request carrying only
   `add-snapshot` and `set-snapshot-ref` updates.
3. The REST server persists the commit in its own `0000N-<uuid>.metadata.json` and
   points the table at it. Its `metadata-log` chains `00001` to `00000`.
4. ClickHouse's `vN-<uuid>` file is referenced by nothing in the catalog's metadata
   tree. A server-side purge (Java `CatalogUtil.dropTableData`) deletes the data
   files, manifests, manifest lists and the metadata files it knows, and leaves the
   orphan.

The keep-drop scenario shows the same three files after one INSERT, so one orphan is
left per commit. Upstream master (`IcebergWrites.cpp`) has the identical flow; this is
not a PR 2305 regression.

**Interaction with PR 2305.** Two of the PR's guarantees cannot hold on a REST catalog
while the orphan exists:

- a purge drop never yields an empty location (invariant B6);
- the PR's leftover-metadata probe in `IcebergMetadata::createInitial` sees
  `metadata/*.metadata.json` at the location and refuses an explicit-engine
  `CREATE TABLE` of the same name after a purge drop (invariant B9,
  `lifecycle/recreate after purge drop`). The engine-less path is unaffected because the
  server writes there.

**Spec check (2026-09-15).** Sources: `format/spec.md`, `open-api/rest-catalog-open-api.yaml`,
`docs/docs/maintenance.md`, `core/.../CatalogUtil.java`, all from `apache/iceberg` main.

- The table spec's "Metastore Tables" commit procedure is: "Write the new table metadata
  to a unique file: `<V+1>-<random-uuid>.metadata.json`. Request that the metastore swap
  the table's metadata pointer from the location of `V` to the location of `V+1`."
  The writer writes the file and the catalog only swaps the pointer. That is the model
  ClickHouse follows when it writes `vN-<uuid>.metadata.json`.
- The REST catalog API does not follow that model. `updateTable` is defined as
  "Commits have two parts, requirements and updates ... Updates are changes to make to
  table metadata", and the response "must" return "the corresponding file location of
  table metadata" in `metadata-location`. The server materialises the commit; a client
  cannot point the catalog at a file it wrote itself through this route (only
  `register` takes a `metadata-location`). So on REST the ClickHouse-written file is
  never the swapped-in version and is unreferenced by construction.
- The spec on `metadata-log`: "Each time a new metadata file is created, a new entry of
  the previous metadata file location should be added to the list." The server's log
  chains its own files (`00001` to `00000`); the ClickHouse file is not a previous
  version of anything the catalog knows.
- The spec does not forbid unreferenced files. The maintenance docs name them
  explicitly: "task or job failures can leave files that are not referenced by table
  metadata ... To clean up these 'orphan' files under a table location, use the
  `deleteOrphanFiles` action", and, on metadata, "Untracked metadata files are also
  deleted as part of orphan file deletion".
- `purgeRequested` is defined as "Whether the user requested to purge the underlying
  table's data and metadata". The reference implementation, `CatalogUtil.dropTableData`,
  deletes the data files, manifests, manifest lists, "previous metadata" from
  `metadata.previousFiles()`, statistics files and the current metadata file. It
  deletes only what the metadata tree references. Its own comment says the goal is to
  "avoid orphaned data or manifest files"; a file the tree never referenced is outside
  its reach by design.

Verdict: the leftover is a genuine orphan in the Iceberg sense, and the server's purge is
spec-conformant in leaving it. The defect is on the writer side: ClickHouse follows the
metastore-tables procedure (write the file, then ask for a pointer swap) against a REST
catalog whose commit route does not swap pointers to client files, so every commit
produces a file that is unreferenced from the moment it is written. The spec does not
forbid that, but the consequences are real: one orphan per commit, `DROP ... purge`
cannot honour its contract, and PR 2305's leftover probe blocks a re-CREATE. The
suggested fix stands: after a successful REST commit delete the scratch file, or do not
write it when the catalog persists metadata itself. Until then, the standard mitigation
is Iceberg's orphan-file cleanup with a retention interval longer than any in-flight write.

**Suite handling.** Invariant B6 is kept as the target with a "known violation" note.
`iceberg/regression.py` xfails:

- `/iceberg/native create/*/sanity/drop with purge`
- `/iceberg/native create/*/drop/drop routes/*`
- `/iceberg/native create/*/drop/server-wide default/*`
- `/iceberg/native create/*/lifecycle/recreate after purge drop*`

Examples in those outlines that keep data still have to pass: TestFlows applies an
xfail only when the test actually fails.

**Ask.** Either remove the scratch `vN-<uuid>.metadata.json` after a successful REST
commit, or do not write it for catalogs that persist the metadata themselves. Until
then a purge drop on a REST catalog leaves one small JSON per commit in the bucket, and
users cannot re-create a dropped table with an explicit engine at the same location.

---

## Finding 3 — `CREATE TABLE` in an existing namespace stalls for ~33 s retrying a 409

**Symptom.** In `explicit engine create` the second table in a namespace (the first was
made engine-less a moment earlier) took 32.9 s to create; the statement succeeded.

**Mechanism.** Both creation paths call `catalog->createNamespaceIfNotExists` on every
`CREATE` (`DatabaseDataLake::createTable` and `IcebergMetadata::createInitial`).
`RestCatalog::createNamespaceIfNotExists` does not check for the namespace first; it
posts `POST /v1/namespaces` and swallows whatever comes back with
`tryLogCurrentException`. The server answers `409 Conflict`
(`"Namespace already exists: ..."`). `sendRequest` goes through
`ReadWriteBufferFromHTTP`, whose retry loop treats every status outside the
non-retriable list in `isRetriableHTTPError` (`HTTPCommon.cpp`: 400, 401, 403, 404, 405,
501) as transient, and 409 is not on that list. With the defaults `http_max_tries = 10`,
`http_retry_initial_backoff_ms = 100`, `http_retry_max_backoff_ms = 10000` the client
retries with 0.1 + 0.2 + 0.4 + 0.8 + 1.6 + 3.2 + 6.4 + 10 + 10 s of backoff, then logs
the 409 at `Error` level and proceeds. Server log (query `7427de20`): ten
`Failed to make request to '.../v1/namespaces'` lines from 14:31:52.13 to 14:32:24.87,
then `<Error> RestCatalog ... HTTP status code: 409 'Conflict'`, then the metadata
write. The PR's Glue implementation avoids this by calling `GetDatabase` before
`CreateDatabase` ("must not be called when there is nothing to create"); the REST one
has no such check.

**Effect.** Every `CREATE TABLE` into a namespace that already exists costs about 33 s
and an `Error` log line, on both paths. In the suite this slows every scenario that
creates a second table in a namespace, and the three-node race in `idempotency.py`
(five rounds, all in one namespace) by several minutes. No assertion fails.

**Ask (PR 2305).** Check namespace existence before creating it in
`RestCatalog::createNamespaceIfNotExists` (`HEAD` or `GET /v1/namespaces/{ns}`), or
treat 409 as success there without going through the retrying request path.

---

## Finding 4 — On the explicit-engine path ClickHouse's initial metadata file is an orphan from birth

**Symptom.** After `CREATE TABLE ... ENGINE = IcebergS3(...)` in a REST catalog
database, B1 finds two new metadata files:

```
metadata/v1-3697eb89-....metadata.json      written by ClickHouse (createInitial)
metadata/00000-e60f0d6a-....metadata.json   written by the catalog server, and the one the catalog points at
```

**Mechanism.** `IcebergMetadata::createInitial` writes `v1-<table-uuid>.metadata.json`
(the table UUID it generated), then calls `catalog->createTable(ns, t, catalog_filename,
metadata_content, ...)`. `RestCatalog::createTable` ignores the file path
(`/*new_metadata_path*/`; the source comment says "the REST server writes and names the
initial metadata file itself") and sends a `CreateTableRequest`, which per the REST spec
carries only `name`, `location`, `schema`, `partition-spec`, `write-order`,
`stage-create`, `properties`. There is no way to pass a metadata location or a table
UUID on that route. The server therefore creates the table with its own UUID and its
own file. ClickHouse's file is never referenced, and it carries a different
`table-uuid` than the table the catalog knows. Right after the create, the storage
object built by the `CREATE` itself resolved "Latest metadata file path is
.../v1-3697..." by listing the directory, so at that moment ClickHouse read its own
file rather than the catalog's; later accesses go through the catalog's
`metadata-location`.

This is the same root cause as finding 2 (client-written metadata that the REST
commit route never adopts) applied to table creation, and it is what PR 2305's
explicit-engine path does on every REST catalog. Glue is different: there the PR
registers the ClickHouse-written file as `metadata_location`, so `v1.metadata.json` is
the real initial file.

**Effect.** On REST, invariant B1 ("exactly one initial metadata file") cannot hold on
the explicit-engine path, engine `SETTINGS` such as `iceberg_format_version` cannot reach
the file the catalog uses, and the leftover-metadata probe in `createInitial` will refuse
a later explicit-engine `CREATE` at that location even after a purge (finding 2).

**Suite handling.** xfails in `iceberg/regression.py`:

- `/iceberg/native create/*/sanity/explicit engine create`
- `/iceberg/native create/*/explicit engine/any iceberg engine accepted without fixed backend`
- `/iceberg/native create/*/explicit engine/initial file naming*`
- `/iceberg/native create/*/metadata/gzip metadata*`
- `/iceberg/native create/*/schema/engine settings with explicit engine*`

**Ask.** On a REST catalog the explicit-engine path should not write an initial
metadata file at all (let `createTable` register the schema, as the engine-less path
does), or it should delete the scratch file once the server has created the table.

---

## Finding 5 — ClickHouse-written manifest lists carry no Avro `field-id`s, so PyIceberg cannot scan the table

**Symptom.** Every `schema/accepted transforms` check that planned a PyIceberg scan on a
table ClickHouse had inserted into died with

```
ValueError: Cannot convert field, missing field-id: {'name': 'manifest_path', 'type': 'string', 'doc': 'Location URI with FS scheme'}
```

**Mechanism.** `generateManifestList` (`IcebergWrites.cpp`) writes the manifest list with
`avro::DataFileWriter`, whose compiled schema drops the Iceberg `field-id` attributes
from the Avro schema embedded in the file header. PyIceberg's `AvroSchemaConversion`
requires them (`if "field-id" not in field: raise ValueError`). The branch already works
around this for the empty-manifest-list case (`TRUNCATE`) by writing the container
header by hand with the id-carrying JSON, but every non-empty manifest list goes through
the plain writer. Metadata JSON is unaffected, so `load_table`, `schema()`, `spec()` and
`sort_order()` keep working; anything that walks manifests (`scan`, `plan_files`,
`to_arrow`) fails.

**Upstream status.** Fixed by ClickHouse/ClickHouse#111786 "Fix missing Iceberg
field-ids in ClickHouse-written manifest and manifest-list files" (merged 2026-07-27):
`writer.setMetadata(f_avro_schema, schema_representation)` writes the original
id-carrying schema JSON as the `avro.schema` header. Not in `antalya-26.6` / PR 2305. A
related, distinct gap for Parquet field-ids is tracked as Altinity/ClickHouse#2161.

**Effect.** No external reader can read data ClickHouse wrote through this feature,
which undercuts `Metadata.ExternalReader` directly. In the suite every PyIceberg scan
is affected; the partition-record oracle for transforms was split into its own scenario
so the fourteen transform checks stay green.

**Suite handling.** `Error` xfails in `iceberg/regression.py`:

- `/iceberg/native create/*/schema/partition values in manifest`
- `/iceberg/native create/*/metadata/first commit has no parent`
- `/iceberg/native create/*/metadata/pyiceberg reads clickhouse rows`
- `/iceberg/native create/*/lifecycle/insert alter select*/PyIceberg sees the final schema and rows`

**Ask.** Port ClickHouse/ClickHouse#111786.

---

## Backports required for the suite to pass on `antalya-26.6`

Verified 2026-09-15 against the branch source and upstream master. None of the three is
in `antalya-26.6` or in PR 2305; no Altinity PR references any of them.

| # | Upstream PR | Merged | Size | Unblocks (xfails removed) |
|---|---|---|---|---|
| 1 | ClickHouse/ClickHouse#114864 "Fix Iceberg partition transform names for day and hour" | 2026-08-28 | +48/-2, `Utils.cpp` | 5 xfails: `sanity/create as source copies keys`, `schema/accepted transforms` day and hour cases, `metadata/initial file`, `lifecycle/insert alter select` PyIceberg check |
| 2 | ClickHouse/ClickHouse#111786 "Fix missing Iceberg field-ids in ClickHouse-written manifest and manifest-list files" | 2026-07-27 | +138/-3, `IcebergWrites.cpp`, `Constant.h` | 4 xfails: `schema/partition values in manifest`, `metadata/first commit has no parent`, `metadata/pyiceberg reads clickhouse rows`, `lifecycle/insert alter select` PyIceberg check |
| 3 | ClickHouse/ClickHouse#109812 "Use Iceberg spec extension gz for gzip metadata file names" | 2026-07-17 | +302/-24, `FileNamesGenerator.*`, `IcebergMetadata.cpp`, `Utils.cpp` | `metadata/gzip metadata` (currently also blocked by finding 4 on the explicit path); the assertion there must change from `.gzip.` to `.gz.` when ported |

**Why #114864.** ClickHouse writes `days` / `hours` where the Iceberg spec defines
`day` / `hour`. Java Iceberg's `Transforms.fromString` and PyIceberg both reject the
plural, so every table partitioned by `toRelativeDayNum` or `toRelativeHourNum` is
unreadable by Spark, Trino and PyIceberg, while ClickHouse's own lenient reader hides
the problem. The PR's documentation table promises `day` / `hour`. This is the
smallest and most user-visible fix of the three: a one-file change that turns
spec-invalid metadata into valid metadata.

**Why #111786.** The manifest list is written through `avro::DataFileWriter`, whose
compiled schema drops the Iceberg `field-id` attributes; PyIceberg's Avro schema
conversion raises on the first field without one. The effect is not limited to one
partition transform: no external reader can plan a scan over any table ClickHouse has
inserted into, so the SRS requirement `Metadata.ExternalReader` cannot hold and the
"Iceberg" in the feature name is only true for ClickHouse-to-ClickHouse use. The fix
writes the original id-carrying schema JSON as the `avro.schema` header, which is what
the branch already does by hand for the empty-manifest-list case.

**Why #109812.** With `iceberg_metadata_compression_method = 'gzip'` the branch names the
file `v1.gzip.metadata.json`. PyIceberg selects its decompressor by the suffix
`.gz.metadata.json` (`pyiceberg/serializers.py`), and the Iceberg reference
implementation uses the same convention, so a `.gzip.` file is opened as plain JSON and
fails to parse. Any gzip-compressed table ClickHouse creates is therefore unreadable
externally until the extension is `gz`. Lower priority than the first two because it
affects only the compression option, and on REST the explicit-engine file is an orphan
anyway (finding 4).

**Not backports, but needed alongside them**

- **Finding 3 (409 retry storm) is a change to PR 2305 itself**: check namespace
  existence in `RestCatalog::createNamespaceIfNotExists` before posting, as the PR's
  Glue implementation already does. Without it every `CREATE` into an existing
  namespace costs ~33 s; no xfail, but the suite runtime roughly triples.
- **Findings 2 and 4 (orphan `vN-<uuid>.metadata.json` on REST) have no upstream fix**;
  master has the same code. They need a new change (delete the scratch file after a
  successful REST commit or do not write it for catalogs that persist metadata) and
  account for 9 xfails across the purge, explicit-engine, and recreate scenarios.
- **`FixedString` has no writer mapping upstream either**; no PR exists. The test was
  changed to assert the rejection, so nothing to port.

## Environment facts settled by the runs

These resolve the "first-run unknowns" in `native_create_drop_test_plan.md` §5.

1. **`ice-rest-catalog` advertises no `default-base-location`.** For a REST catalog
   without one, `getLocationSchemeForTableCreation` refuses to derive a storage scheme
   from `storage_endpoint`:
   `Cannot determine storage scheme for CREATE TABLE for catalog type 'ICEBERG_REST'`.
   Every fixture database on REST therefore sets
   `default_base_location = 's3://warehouse/data'` (`steps.database_base_location`).
   Derivation from `storage_endpoint` is testable only on Glue.
2. **Tables land at `s3://warehouse/data/<namespace>/<table>`**, and the catalog reports
   the namespace location `s3://warehouse/data/<namespace>`, so invariants A4 and A5 are
   observable on this catalog.
3. **The engine-less initial metadata file is named by the server**,
   `00000-<uuid>.metadata.json`, not `v1*.metadata.json`; the `v1` convention applies
   only where ClickHouse writes the file itself (explicit engine, Glue).
   `assert_table_created` accepts both.
4. **`ice-rest-catalog` honours `purgeRequested=true`** (finding 2 shows it deleting the
   whole metadata tree it knows).

5. **`FixedString` cannot be written to Iceberg.** The pre-existing `datatypes`
   scenarios `scalar fixed` and `all scalars in one table` expected a `FixedString(5)`
   column to round-trip; the server answers
   `Unsupported type for iceberg FixedString(5) (BAD_ARGUMENTS)`. The writer's type
   mapping (`Utils.cpp`) has no `FixedString` case on the PR branch, on
   `antalya-25.8`, or on upstream master, although the reader maps `fixed[N]` to
   `FixedString` (`SchemaProcessor.cpp`). A product gap, not a PR 2305 regression; the
   test was corrected to assert the rejection (`unsupported_types_rejected`).

## Harness lessons

- A `@TestStep` returns its value only when called inside a `Given`/`When`/`Then`/`And`/
  `By` block; called bare in a scenario body or directly in a `Check` body it returns the
  `Result` object. All value-returning calls are wrapped.
- `node.query` fails any output containing `Exception:` unless the expected `message`
  contains that word or `ignore_exception=True` is passed. `create_table` and
  `drop_table` pass it whenever an error is expected.
- A feature-level probe must use `steps=False`, or an `--only` filter skips it.
- A failing `Check` aborts its scenario unless the `Check` carries `flags=TE`; a failing
  `Scenario` likewise stops its feature loop without `TE` (verified with a probe script).
  Every `Check` and every feature-loop `Scenario` in the package carries `TE`.
- ClickHouse writes Iceberg data files as `data/data-<uuid>.parquet` with no Hive-style
  partition directory; the spec prescribes no layout, so partitioning is asserted from
  the manifest entry's partition record, not from the path.
- Snapshots taken before and after a drop must inspect the same prefix;
  `snapshot_state` remembers the location the catalog last reported for the table.
