# Native CREATE / DROP TABLE Test Plan
## Feature: `iceberg/tests/iceberg_engine/native_create_drop.py`

This document lists every scenario that should be covered for **natively creating and dropping Iceberg tables from ClickHouse** via the `DataLakeCatalog` database engine (REST and Glue catalog variants).

"Native create" means issuing a `CREATE TABLE … ENGINE = IcebergS3(…)` inside a `DataLakeCatalog` database directly from ClickHouse—ClickHouse writes the Iceberg metadata and registers the table in the catalog—as opposed to creating the table first with PyIceberg and then reading it from ClickHouse.

---

## 1. Basic Create / Smoke

| # | Scenario | What to check |
|---|----------|---------------|
| 1.1 | Create table with minimal scalar columns (Int32, Float64, String) | Table exists in `SHOW TABLES`, data is readable |
| 1.2 | Insert rows immediately after creation and SELECT them back | Row count and values match |
| 1.3 | Table is visible from PyIceberg catalog after ClickHouse CREATE | `catalog.load_table()` succeeds; schema matches |
| 1.4 | Iceberg metadata files appear on S3 under the expected prefix | At least one `metadata/*.json` and `metadata/version-hint.text` object exists |

---

## 2. Column Type Coverage

Test `CREATE TABLE` with each ClickHouse type that maps to an Iceberg primitive type.

| # | ClickHouse type | Iceberg type |
|---|-----------------|--------------|
| 2.1  | `Int32`             | `integer`       |
| 2.2  | `Int64`             | `long`          |
| 2.3  | `Float32`           | `float`         |
| 2.4  | `Float64`           | `double`        |
| 2.5  | `Bool`              | `boolean`       |
| 2.6  | `String`            | `string`        |
| 2.7  | `FixedString(N)`    | `fixed(N)`      |
| 2.8  | `Date`              | `date`          |
| 2.9  | `DateTime64(6, 'UTC')` | `timestamptz` |
| 2.10 | `DateTime64(6)`     | `timestamp`     |
| 2.11 | `UUID`              | `uuid`          |
| 2.12 | `Decimal(P, S)`     | `decimal(P, S)` |
| 2.13 | `Nullable(T)` for each of the above | Iceberg `optional` field |
| 2.14 | `Array(T)` (flat)   | `list<T>`       |
| 2.15 | `Array(Array(T))`   | `list<list<T>>` |
| 2.16 | `Map(String, T)`    | `map<string, T>`|
| 2.17 | `Tuple(T1, T2, …)`  | `struct`        |

For each type: INSERT a row, SELECT it back, verify value round-trips correctly.

---

## 3. Partitioning

| # | Scenario | What to verify |
|---|----------|----------------|
| 3.1 | No `PARTITION BY` clause | Table created as unpartitioned Iceberg table; `partition-spec` is empty |
| 3.2 | `PARTITION BY` single integer column | One identity partition field in Iceberg spec |
| 3.3 | `PARTITION BY` single string column | One identity partition field |
| 3.4 | `PARTITION BY` single date column | One identity partition field |
| 3.5 | `PARTITION BY` multiple columns | Multiple identity partition fields |
| 3.6 | Data insert creates correct partition directories on S3 | S3 prefix contains `col=value/` directories |
| 3.7 | Partition pruning works after native create | SELECT with WHERE on partition column reads fewer files than full scan |

---

## 4. ORDER BY / Sort Order

| # | Scenario | What to verify |
|---|----------|----------------|
| 4.1 | No `ORDER BY` clause | Iceberg sort order is empty (`unsorted`) |
| 4.2 | `ORDER BY` single column | Iceberg sort order contains one field |
| 4.3 | `ORDER BY` multiple columns | Iceberg sort order contains multiple fields |
| 4.4 | `ORDER BY` column with `ASC`/`DESC` | Sort direction preserved in Iceberg metadata |

---

## 5. CREATE TABLE Modifiers

| # | Scenario | What to verify |
|---|----------|----------------|
| 5.1 | `CREATE TABLE IF NOT EXISTS` when table does not exist | Table is created normally |
| 5.2 | `CREATE TABLE IF NOT EXISTS` when table already exists | No error; original table unchanged |
| 5.3 | `CREATE TABLE` (no IF NOT EXISTS) when table already exists | Error returned (table already exists) |
| 5.4 | `CREATE OR REPLACE TABLE` | Old table overwritten; new schema visible |

---

## 6. `write_full_path_in_iceberg_metadata` Setting

| # | Scenario | What to verify |
|---|----------|----------------|
| 6.1 | `write_full_path_in_iceberg_metadata = 1` (enabled) | Metadata JSON contains full S3 URI for data files |
| 6.2 | `write_full_path_in_iceberg_metadata = 0` (disabled / default) | Metadata uses relative paths |
| 6.3 | Table created with full-path metadata is readable by PyIceberg | `catalog.load_table().scan()` returns rows |

---

## 7. Metadata Validation

| # | Scenario | What to verify |
|---|----------|----------------|
| 7.1 | `SHOW CREATE TABLE` output | Engine, column list, partition spec, order by match what was specified |
| 7.2 | `system.tables` row | `engine`, `engine_full`, `database`, `metadata_path`, `total_rows`, `total_bytes` are correct |
| 7.3 | Iceberg metadata JSON on S3 | `format-version`, `schema`, `partition-spec`, `sort-order` fields match the CREATE statement |
| 7.4 | `DESCRIBE TABLE` output | Column names and types match |

---

## 8. DROP TABLE

| # | Scenario | What to verify |
|---|----------|----------------|
| 8.1 | `DROP TABLE` removes ClickHouse table entry | Table absent from `SHOW TABLES` after drop |
| 8.2 | `DROP TABLE` removes Iceberg metadata from catalog | `catalog.list_tables()` no longer includes the table |
| 8.3 | `DROP TABLE IF EXISTS` on existing table | No error; table removed |
| 8.4 | `DROP TABLE IF EXISTS` on non-existing table | No error |
| 8.5 | `DROP TABLE` (no IF EXISTS) on non-existing table | Error returned |
| 8.6 | Re-CREATE after DROP using the same name | New table created successfully |
| 8.7 | `iceberg_delete_data_on_drop = 1` (default) | All S3 data and metadata files are deleted after DROP |
| 8.8 | `iceberg_delete_data_on_drop = 0` | S3 data and metadata files are **retained** after DROP; objects still present in bucket |
| 8.9 | Re-CREATE after DROP with `iceberg_delete_data_on_drop = 0` | New table starts empty; orphaned S3 files from the previous table do not surface |

---

## 9. Namespace Handling

| # | Scenario | What to verify |
|---|----------|----------------|
| 9.1 | Create in an existing namespace | Table created under `namespace.table_name` |
| 9.2 | Create in a namespace that does not exist in the catalog | Expected error or auto-creation behavior |
| 9.3 | Multiple tables in the same namespace | Each table is independent; no cross-contamination |
| 9.4 | Namespace with dots in its name | Correct escaping in ClickHouse SQL (`` `ns.name` ``) |
| 9.5 | Nested namespace (e.g. `a.b`) | Table created under `a.b.table_name`; ClickHouse and catalog agree on the full identifier |
| 9.6 | Three-level nested namespace (e.g. `a.b.c`) | Multi-level nesting is handled; identifier correctly resolved in catalog |
| 9.7 | DROP TABLE in nested namespace | Table removed from the correct nested namespace; sibling namespaces and tables unaffected |
| 9.8 | Two tables with the same short name in different nested namespaces | No confusion between `a.b.table` and `a.c.table` |

---

## 10. Naming Edge Cases

| # | Scenario | What to verify |
|---|----------|----------------|
| 10.1 | Table name with hyphens (`my-table`) | Created and accessible with backtick quoting |
| 10.2 | Table name with dots (`my.table`) | Created and accessible with backtick quoting |
| 10.3 | Table name with spaces | Created and accessible with backtick quoting |
| 10.4 | Very long table name (>64 chars) | No truncation or error |
| 10.5 | Column name that is a reserved ClickHouse keyword | Handled correctly |

---

## 11. Catalog Compatibility

| # | Scenario | What to verify |
|---|----------|----------------|
| 11.1 | Native CREATE via REST catalog | Full flow as described above |
| 11.2 | Native CREATE via Glue catalog | Full flow as described above |
| 11.3 | Table created via ClickHouse (REST) is readable via PyIceberg (REST) | Round-trip visibility |
| 11.4 | Table created via ClickHouse (Glue) is readable via PyIceberg (Glue) | Round-trip visibility |

---

## 12. Error / Negative Cases

| # | Scenario | Expected behavior |
|---|----------|-------------------|
| 12.1 | Create with unsupported column type (e.g. `LowCardinality(String)`) | Clear error message |
| 12.2 | Create with `PARTITION BY` column that is not in the column list | Error or no data files created |
| 12.3 | Create with `ORDER BY` column that is not in the column list | Error |
| 12.4 | Create without required `allow_experimental_database_iceberg` setting | Error about missing setting |
| 12.5 | Create when S3 credentials are wrong | Error propagated from S3 layer |
| 12.6 | Create when catalog is unavailable | Error with useful message |

---

## 13. Post-Create Operations Smoke

Verify that a natively created table supports all expected subsequent operations.

### 13a. Basic Read / Write

| # | Scenario |
|---|----------|
| 13a.1 | INSERT (via `allow_insert_into_iceberg = 1`) |
| 13a.2 | SELECT with WHERE / ORDER BY / LIMIT |
| 13a.3 | Concurrent SELECTs while inserting |

### 13b. Schema Evolution

| # | Scenario | What to verify |
|---|----------|----------------|
| 13b.1 | `ALTER TABLE ADD COLUMN` | New column visible in `DESCRIBE TABLE`; existing rows return NULL for the new column; Iceberg schema version incremented |
| 13b.2 | `ALTER TABLE DROP COLUMN` | Column absent from `DESCRIBE TABLE`; SELECT no longer returns dropped column; Iceberg schema updated |
| 13b.3 | `ALTER TABLE RENAME COLUMN` | Renamed column accessible under new name; old name no longer works; Iceberg field id preserved |
| 13b.4 | `ALTER TABLE MODIFY COLUMN` (type widening, e.g. `Int32` → `Int64`) | Data readable after type change; Iceberg schema reflects new type |
| 13b.5 | Add column then insert data into it | New column populated correctly in subsequent inserts; previously inserted rows still return NULL |
| 13b.6 | Drop partition column | Error or correct behavior (partitioning on a dropped column is undefined) |

### 13c. Partition Evolution

| # | Scenario | What to verify |
|---|----------|----------------|
| 13c.1 | Add a new partition field to an unpartitioned table | Iceberg `partition-spec` updated; new writes land in partitioned layout |
| 13c.2 | Add a partition field to an already-partitioned table | Second partition field added; old and new snapshots coexist; reads return all data |
| 13c.3 | Remove a partition field | Old partitioned data still readable; new writes use the updated spec |
| 13c.4 | Replace identity partition with a transform (e.g. `bucket[N]` or `truncate`) | Iceberg spec updated; writes use new transform; reads return consistent results |
| 13c.5 | Query after partition evolution | Partition pruning still works correctly on the active spec; no data loss or duplication |

---

## 14. Iceberg Format Version

Only Iceberg format v2 is supported for natively created tables.

| # | Scenario | What to verify |
|---|----------|----------------|
| 14.1 | Default format version used | `format-version: 2` in metadata JSON on S3 |

---

## 15. RBAC

Verify that access control works correctly on natively created tables. The existing `rbac.py` patterns apply: create a restricted user, attempt the operation, verify it is denied, grant the privilege, verify it is allowed.

| # | Scenario | What to verify |
|---|----------|----------------|
| 15.1 | User without `SELECT` privilege cannot read a natively created table | `DB::Exception: Not enough privileges` |
| 15.2 | After `GRANT SELECT`, user can read the table | Data returned correctly |
| 15.3 | User without `INSERT` privilege (`allow_insert_into_iceberg`) cannot insert into the table | Access denied error |
| 15.4 | After granting `INSERT`, user can insert and data appears on subsequent SELECT | Row count matches |
| 15.5 | User without `DROP TABLE` privilege cannot drop the table | `DB::Exception: Not enough privileges` |
| 15.6 | After `GRANT DROP`, user can drop the table (≥25.8 behavior) | Table removed from `SHOW TABLES` |
| 15.7 | `GRANT SELECT ON database.*` covers all tables in the database including natively created ones | User can read any table in the database |
| 15.8 | RBAC applies consistently after schema evolution (ADD COLUMN) | User still needs explicit privilege; no privilege escalation through schema change |

---

## 16. Swarm Sanity

Verify that a natively created table is queryable via the swarm `object_storage_cluster`.

| # | Scenario | What to verify |
|---|----------|----------------|
| 16.1 | SELECT from natively created table using `object_storage_cluster='swarm'` | Query distributes across swarm nodes; `hostName()` returns multiple distinct hosts |
| 16.2 | Row count via swarm SELECT matches row count via single-node SELECT | No data duplication or loss |
| 16.3 | INSERT data via ClickHouse, then SELECT via swarm | Freshly written data is visible through the swarm path |
| 16.4 | Partitioned natively created table read via swarm with WHERE on partition column | Partition pruning reduces scanned files; result is correct |

---

## 17. Deletes

Verify that row-level delete operations work correctly on natively created tables (Iceberg v2 equality and position deletes).

| # | Scenario | What to verify |
|---|----------|----------------|
| 17.1 | Delete all rows matching a simple equality condition (`EqualTo`) | Deleted rows absent from SELECT; non-matching rows intact |
| 17.2 | Delete rows with comparison operators (`GreaterThan`, `LessThan`, `GreaterThanOrEqual`, `LessThanOrEqual`, `NotEqualTo`) | Results match equivalent MergeTree reference table |
| 17.3 | Delete with compound condition (`And`, `Or`, `Not`) | Correct subset of rows removed |
| 17.4 | Delete with `In` / `NotIn` on a list of values | Only matching rows removed |
| 17.5 | Delete with `IsNull` / `NotNull` | Null-aware filtering works correctly |
| 17.6 | Delete on a partitioned natively created table | Only the correct partition files are rewritten; other partitions unaffected |
| 17.7 | Multiple sequential deletes | Each delete accumulates correctly; final row set matches reference |
| 17.8 | Delete all rows | Table returns empty result set; metadata snapshot still exists |
| 17.9 | INSERT after delete | New rows visible; previously deleted rows do not reappear |
| 17.10 | DELETE via ClickHouse `ALTER TABLE DELETE` (if supported) | Same outcome as PyIceberg-issued delete |

---

## Implementation Notes

- All scenarios should be parameterized to run under both **REST** and **Glue** catalog contexts via the `self.context.catalog` dispatch pattern already used in the suite.
- Each scenario that touches S3 should verify the object layout via `catalog_steps.list_objects_cli()` where relevant.
- Use `iceberg_engine.check_values_in_system_tables()` for `system.tables` assertions.
- Use `iceberg_engine.show_create_table()` for DDL round-trip checks.
- Negative tests should pass `exitcode` and `message` to `node.query()` rather than using bare try/except.
