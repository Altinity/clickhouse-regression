# Unity Catalog in the Iceberg suite

The Iceberg suite can run its existing scenarios against a local Unity Catalog. Tables in this branch are Iceberg tables. ClickHouse attaches them with `catalog_type = 'unity'` and `use_unity_catalog_v2 = 1`.

## 1. The image is built locally

Released Unity Catalog images serve Iceberg REST as read-only. Create, commit, and drop exist in source after the v0.6.0 release, so the suite builds its own image instead of pulling one.

The image is `clickhouse-regression/unity-catalog:e648169`, built from [unitycatalog/unitycatalog](https://github.com/unitycatalog/unitycatalog) commit `e64816917eca9f3185e47a2b96351b0ad3a82f28`. The Dockerfile is `iceberg/unity/Dockerfile`. Compose sets `pull_policy: build` because that name is not in a registry.

`iceberg/unity/minio-static-credentials.patch` changes the stock server in three ways:

- Iceberg REST is mounted at `/iceberg-rest`. ClickHouse Unity v2 calls that path. Upstream OSS Unity mounts `/iceberg`.
- S3 uses the suite MinIO (`admin` / `password`, path-style access, no STS).
- The server classpath includes the AWS SDK `apache-client`, which those S3 calls need.

ClickHouse connects to `http://unity-catalog:8080/api/2.1/unity-catalog`. PyIceberg uses the same server at `/api/2.1/unity-catalog/iceberg-rest`.

## 2. Databricks, for read and write on a real catalog

Use a Databricks Premium workspace when the tables have to be created, read, and written through Databricks Unity Catalog. The local image is for Iceberg tests against OSS Unity on MinIO.

Unity Catalog has no separate license on Premium. You pay for the compute that runs and for the cloud storage that holds the files. [The catalog is included with Premium.](https://www.databricks.com/product/unity-catalog) Free Edition has no external locations, so it cannot register tables on your own bucket or on the suite MinIO.

On a paid workspace, with external data access enabled, external clients can create, read, and write managed Iceberg tables and Delta tables. Databricks documents that in [Access Databricks data using external systems](https://docs.databricks.com/aws/en/external-access/). The storage has to be S3, ADLS, or GCS in your cloud account.

The Python package `deltalake` can open an existing Databricks table with `uc://catalog.schema.table`. `write_deltalake` writes Delta files at a storage path and does not register the table in the catalog.

## 3. What 26.10 adds

`use_unity_catalog_v2` arrived in [ClickHouse#115879](https://github.com/ClickHouse/ClickHouse/pull/115879), merged on 2026-09-24. It is on current master (`26.10.1`). No 26.10 release is published yet.

ClickHouse 26.6, including Altinity 26.6, still has the older Unity catalog. That catalog is aimed at Delta and rejects `use_unity_catalog_v2` with `UNKNOWN_SETTING` (code 115). The suite runs Unity scenarios only when `version >= 26.10`.

Unity v2 reads Iceberg through an embedded `RestCatalog` pointed at Unity's Iceberg REST endpoint. Create, insert, and alter are implemented. `DROP TABLE` is not: `UnityV2Catalog` does not override `dropTable`, so the server returns code 48, `dropTable is not implemented`. A draft report is in `iceberg/docs/unity-v2-drop-table-issue.md`.

## 4. Delta is not tested

Every scenario here creates Iceberg tables with PyIceberg and reads them as Iceberg. Nothing creates a Delta table, and nothing selects one.

The same Unity server can hold Delta tables, and ClickHouse Unity v2 can read Delta. This suite does not cover that path.

## Known gaps

| Gap | What happens |
| --- | --- |
| `TIME` columns | Unity returns 400, `Iceberg type TIME is not supported`. The predicate-pushdown scenario is xfailed. |
| `DROP TABLE` | Privilege check returns code 497. After `GRANT DROP`, the drop returns code 48. |
| Position-delete re-register | The test calls Iceberg REST `POST .../register`. OSS Unity does not implement that route and returns 404. |
| `non partitioned table` | The `icebergS3` comparison still reads `s3://warehouse/data`. Unity stores the table at `s3://warehouse/data/<namespace>/<table>`. |

## Run

From `iceberg/`:

```bash
python3 regression.py \
  --clickhouse-binary-path docker://clickhouse/clickhouse-server:head \
  --clickhouse-version <SELECT version()> \
  --with-analyzer
```

`--clickhouse-version` has to be the exact string from `SELECT version()`. On macOS the suite cannot execute the Linux server binary to discover that version itself. `--with-analyzer` matches head, which enables the analyzer by default.
