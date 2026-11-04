# Delta Lake suite — test plan

Specification: `delta_lake/requirements/requirements.md` (SRS-050).
Package: `delta_lake.tests`.

The cluster is one ClickHouse node, RustFS, and the OSS Unity Catalog image
`unitycatalog/unitycatalog:v0.7.0`. `delta_lake/tests/steps.py` writes a table
with the `deltalake` package, registers it as an external `DELTA` table, and
opens that catalog with `vended_credentials = false`. `sanity.py` already
checks one case: a `String` and `Int64` table is `ENGINE = DeltaLake` with
`use_unity_catalog_v2` off and on, and `SELECT` returns the three written rows.

Write the five modules below first, in this order. Each one reuses `steps.py`.
Tag every scenario with `@Requirements` from `delta_lake.requirements.requirements`.
`RQ` names in the tables omit the `RQ.SRS-050.ClickHouse.DeltaLake.` prefix.

`regression.py` currently skips the whole module on servers older than 26.10.
Move that skip onto the scenarios that set `use_unity_catalog_v2 = 1`. Direct
`deltaLake()` and `ENGINE = DeltaLake` reads have existed since 22.11. Unity
without the v2 setting is the older Delta catalog. Only the v2 flag needs 26.10.

---

## 1. First modules

```
delta_lake/tests/
    sanity.py     already written; keep it as the smoke test
    access.py     table function and table engine on the RustFS path
    schema.py     type mapping, including the Unity varchar name
    snapshot.py   overwrite, append, empty table, column projection
    unity.py      catalog statements on the sanity table (backticks, SHOW, bad key)
    writes.py     INSERT gate, append, and the rejected mutations
```

Load them from `regression.py` after `sanity`. A failure in `access.py` means
the later modules are not worth reading: the catalog is only a pointer at this
path.

### 1.1 `access.py`

`deltalake` writes the table. These scenarios do not create a Unity database.
ClickHouse reaches RustFS at `http://rustfs:9000/warehouse/...` with the suite
keys. The host-side writer uses `http://localhost:9002`.

| # | Scenario | Assert | RQ |
|---|---|---|---|
| 1 | `deltaLake(url, key, secret)` with no `format` or `structure` | Rows match the writer. `DESCRIBE` names the columns from `_delta_log` | Access.TableFunction |
| 2 | `CREATE TABLE ... ENGINE = DeltaLake(url, key, secret)` with no column list | `SHOW CREATE` lists the log schema and `DeltaLake`. `SELECT` matches scenario 1 | Access.Engine |
| 3 | Same URL, wrong secret, through the function and the engine | The read fails. The prefix in the bucket is unchanged | Access.Credentials |
| 4 | Function and engine pointed at a prefix that has no `_delta_log` | The query fails. The prefix gains no `_delta_log` | Access.TableFunction, Create.AttachExisting |
| 5 | Named collection holding `url`, `access_key_id`, `secret_access_key` | `deltaLake(collection)` and `ENGINE = DeltaLake(collection)` return the same rows | Access.NamedCollection |

Leave GCS, Azure, `deltaLakeLocal`, `gs://`, and `role_arn` out. This cluster
has none of those backends.

### 1.2 `schema.py`

Write one Delta table per group with `deltalake`, register it, and read it
twice: once with `deltaLake()`, once through Unity with `use_unity_catalog_v2 = 0`.
The two results must match. `SHOW CREATE` on the catalog table must use the
ClickHouse type in the Assert column.

Run the Unity read again with `use_unity_catalog_v2 = 1` on 26.10 and newer.
The types must be the same. `sanity.py` already checks that v2 keeps
`ENGINE = DeltaLake`; here the check is the type string.

| # | Delta type | Values to write | ClickHouse type | RQ |
|---|---|---|---|---|
| 1 | `string`, `long`, `integer`, `short`, `byte` | empty string; min and max of each integer | `String`, `Int64`, `Int32`, `Int16`, `Int8` | Schema.PrimitiveTypes |
| 2 | `float`, `double`, `boolean` | `0`, a fraction, `true`, `false` | `Float32`, `Float64`, `Bool` | Schema.PrimitiveTypes |
| 3 | `date`, `timestamp` | `1970-01-01`; a microsecond timestamp | `Date32`, `DateTime64(6)` | Schema.PrimitiveTypes |
| 4 | `decimal(10, 2)`, `decimal(38, 10)` | a negative value and a value that uses the full scale | `Decimal(10, 2)`, `Decimal(38, 10)` | Schema.Decimal |
| 5 | `binary` | raw bytes, including a zero byte | `String` | Schema.PrimitiveTypes |
| 6 | nullable `long` | one row with a value, one row with null | `Nullable(Int64)`; the null row is `NULL` | Schema.Nulls |
| 7 | `struct`, `array`, `map` | a struct field, an array element that is null, a map entry | `Tuple`, `Array` of `Nullable`, `Map` | Schema.Nested |
| 8 | log type `string`, Unity `type_json` says `varchar(32)` | a short string | Catalog `SELECT` returns that string. `deltaLake()` still sees `String` | Schema.Varchar |

Scenario 8 is the case that used to throw `Unsupported DeltaLake type: varchar(256)`
on the catalog path. Register the column through the Unity tables API with
`type_json` containing `varchar(32)`. Leave the Parquet field as a plain string.

One negative scenario belongs in this module because it uses the same reader:

| # | Scenario | Assert | RQ |
|---|---|---|---|
| 9 | Hand-written `_delta_log` whose schema type is `variant` | The read fails and the error names `variant`. No rows come back | Schema.Unsupported |

`timestamp_ntz` and `void` wait. Both need a table feature the first writer
path does not turn on.

### 1.3 `snapshot.py`

Start from the table in scenario 1 of `schema.py`. Commit again with
`deltalake`, then read the latest snapshot through `deltaLake()` and through
Unity.

| # | Scenario | Assert | RQ |
|---|---|---|---|
| 1 | `mode="overwrite"` with a new set of rows | The next `SELECT` returns only the new rows | Read.Snapshot |
| 2 | `mode="append"` | The next `SELECT` returns the previous rows and the new rows | Read.Snapshot |
| 3 | Write a schema and zero rows | `count()` is 0. `DESCRIBE` still lists the columns | Read.Snapshot |
| 4 | `SELECT` one column | That column only. Values match `SELECT *` of the same snapshot | Read.Projection |

Compare the function result and the Unity result after each commit. A catalog
that keeps the first snapshot fails here even when `sanity.py` is green.

### 1.4 `unity.py`

These scenarios use the table from the sanity scenario `read rows`:
columns `name` and `value`, rows Alice, Bob, and Charlie. They check the
catalog statements around that table. The row values themselves are already
covered by `sanity.py`.

| # | Scenario | Assert | RQ |
|---|---|---|---|
| 1 | `CREATE DATABASE` with `allow_database_unity_catalog = 0` | The statement fails. `SHOW DATABASES` does not list it | Unity.Enable |
| 2 | `SELECT` from `schema.table` without backticks, then with backticks | The bare name fails. The backtick form returns the rows | Unity.Names |
| 3 | `SHOW TABLES`, `SHOW CREATE`, `SHOW COLUMNS`, `DESCRIBE` | The table is listed as `schema.table`. `SHOW CREATE` contains `DeltaLake` and the storage prefix. Column types match `schema.py` | Unity.Show, Unity.DeltaTable |
| 4 | Database created with a wrong `aws_secret_access_key` | `CREATE DATABASE` succeeds. `SELECT` fails | Unity.CreateDatabase, Unity.StorageKeys |
| 5 | `CHECK DATABASE` on the suite database | The check succeeds | Unity.Check |
| 6 | `system.tables` with the default setting, then with `show_remote_databases_in_system_tables = 1` | The Delta table is absent, then present | Unity.SystemTables |

Run 2, 3, and 6 with `use_unity_catalog_v2` off and, on 26.10 and newer, on.
Scenario 3 with the flag on is `Unity.V2`: the engine name stays `DeltaLake`
and the rows stay the same.

Skip personal-access tokens, OAuth client secrets, vended credentials, and
Databricks managed storage. The OSS server in this cluster does not issue them.

### 1.5 `writes.py`

Read the table back with `deltalake` as well as with ClickHouse. The log check
is the list of `*.json` files under `_delta_log` before and after the statement.

| # | Scenario | Assert | RQ |
|---|---|---|---|
| 1 | `INSERT` into the engine table while `allow_delta_lake_writes` is off | The statement fails. The set of log files is unchanged | Writes.Setting |
| 2 | `SET allow_delta_lake_writes = 1` and `INSERT` one row into the engine table | `SELECT` returns the old rows plus the new row. `deltalake` reads that row from the same path. A new log file exists and no old log file was replaced | Writes.Insert, Writes.AppendVisible |
| 3 | Same insert through `unity.\`schema.table\`` | The catalog `SELECT` and `deltalake` both return the new row | Unity.Insert |
| 4 | `DELETE`, `UPDATE`, and `ALTER TABLE ... DELETE` | Each statement fails. The set of log files is unchanged | Writes.NoMutation |
| 5 | `INSERT` of `300` into a `byte` column with `delta_lake_accurate_write_cast = 1`, then again with `= 0` | The first insert fails and adds no log file. The second insert commits | Writes.Cast |

`INSERT SELECT` can be the statement in scenario 2: select the new row from a
`MergeTree` table. That is the form a user actually runs.

---

## 2. What comes after

Write these only after the five modules above pass. Each one needs a writer
option or a server setting the first tests do not use.

| Order | Module | What it adds | RQ |
|---|---|---|---|
| 6 | `partitions.py` | `deltalake` writes `partition_by`. A filter on the partition column returns the right rows. `_path` lists only files from that partition. The same filter with `delta_lake_enable_engine_predicate = 0` returns the same rows. An empty partition value comes back as `NULL` | Read.PartitionPruning, Schema.PartitionColumns |
| 7 | `column_mapping.py` | A table written with `delta.columnMapping.mode` of `name` and of `id`, including a rename. `SELECT` uses the logical name | Read.ColumnMapping, Read.SchemaEvolution |
| 8 | `deletes.py` | A deletion vector drops the marked rows. `count()` matches the live rows. A `remove` action drops the whole file | Read.DeletionVectors, Read.Snapshot |
| 9 | `time_travel.py` | `delta_lake_snapshot_version = 0` returns the first commit. `-1` returns the latest. A missing version fails. `allow_delta_kernel_rs = 0` makes a pinned version fail instead of returning the latest table | Read.TimeTravel, Read.Kernel |
| 10 | `cdf.py` | Change data feed between two versions returns `_change_type`, `_commit_version`, and `_commit_timestamp`. Setting only the end version fails. A table without the feed fails | Read.ChangeDataFeed |
| 11 | `checkpoint.py` | After `deltalake` writes a checkpoint, `SELECT` matches the JSON-only snapshot | Read.Checkpoint |
| 12 | `create_table.py` | `allow_delta_lake_create_table = 1` writes a log that `deltalake` can open, and `SELECT` returns zero rows. `PARTITION BY` is rejected and leaves no log. The same create inside the Unity database shows up in `SHOW TABLES` | Create.NewTable, Create.NoPartition, Create.RegisterInUnity |

`deltaLakeCluster('test_shard_localhost', ...)` can sit at the end of
`access.py` once scenario 1 is stable. That cluster name is two shards on
this same node, so the test only checks that the cluster function returns the
same rows. It does not show work spread across machines.

Azure, GCS, `deltaLakeLocal`, vended credentials, and managed-storage failures
need endpoints this compose file does not start. Leave them out until the
environment grows.

Cache and `system.delta_lake_metadata_log` are real requirements and small
tests. They do not tell you whether a table is readable, so they wait until
the read path above is in place.
