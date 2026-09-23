#!/usr/bin/env python3
import os
import sys
import warnings
from testflows.core import *

append_path(sys.path, "..")

from iceberg.requirements.requirements import *
from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import (
    check_if_not_antalya_build,
    check_clickhouse_version,
    check_monotonic_export_partition_compat,
    experimental_analyzer,
    check_if_antalya_build,
)


xfails = {
    "/iceberg/native create/*/idempotency/concurrent creators on three nodes*/one table, one initial metadata file, visible everywhere": [
        (
            Fail,
            "After a CREATE TABLE race on ice-rest-catalog the table directory holds two server-written `00000-<uuid>.metadata.json` files: the catalog points at the winner's, the other was written for a loser's conflicting createTable. Apache Iceberg core `JdbcTableOperations.doCommit` writes the new metadata file before the INSERT that detects the name conflict and does not delete it on AlreadyExistsException; ClickHouse's ten retries of the 409 (PR 2305 issue 1/3) repeat the request. Not a ClickHouse write; B1 cannot hold for a raced table on this catalog. iceberg/tests/iceberg_engine/native_create/findings.md finding 7.",
        )
    ],
    "/iceberg/native create/*/idempotency/concurrent creators on three nodes*/exactly one creator won": [
        (
            Fail,
            "A CREATE TABLE that loses the race at the catalog (REST answers 409 to POST .../tables because another client registered the table after the existence check) is reported as DATALAKE_DATABASE_ERROR (736) 'Failed to create table ... 409 Conflict' after ~33 s of HTTP retries, instead of TABLE_ALREADY_EXISTS (57): RestCatalog::createTable maps the 409 only when IF NOT EXISTS is set. Timing-dependent: a loser that trips the existence check gets 57 as expected. PR 2305 issue 3 in iceberg/tests/iceberg_engine/native_create/pr-2305-issues.md.",
        )
    ],
    "/iceberg/native create/*/idempotency/concurrent creators on one node/one OK, one TABLE_ALREADY_EXISTS, one table": [
        (
            Fail,
            "A CREATE TABLE that loses the race at the catalog (REST answers 409 to POST .../tables because another client registered the table after the existence check) is reported as DATALAKE_DATABASE_ERROR (736) 'Failed to create table ... 409 Conflict' after ~33 s of HTTP retries, instead of TABLE_ALREADY_EXISTS (57): RestCatalog::createTable maps the 409 only when IF NOT EXISTS is set. Timing-dependent: a loser that trips the existence check gets 57 as expected. PR 2305 issue 3 in iceberg/tests/iceberg_engine/native_create/pr-2305-issues.md.",
        )
    ],
    "/iceberg/native create/*/schema/partition values in manifest": [
        (
            Error,
            "PyIceberg cannot scan a ClickHouse-written table: the manifest list is written through avro-cpp, which drops the Iceberg `field-id` attributes from the Avro schema, so pyiceberg raises `ValueError: Cannot convert field, missing field-id: {'name': 'manifest_path' ...}`. Fixed upstream in ClickHouse/ClickHouse#111786 (merged 2026-07-27, writes the id-carrying schema JSON as the avro.schema header); not in antalya-26.6 / PR 2305. See iceberg/tests/iceberg_engine/native_create/findings.md finding 5.",
        )
    ],
    "/iceberg/native create/*/metadata/first commit has no parent": [
        (
            Error,
            "PyIceberg cannot scan a ClickHouse-written table: the manifest list is written through avro-cpp, which drops the Iceberg `field-id` attributes from the Avro schema, so pyiceberg raises `ValueError: Cannot convert field, missing field-id: {'name': 'manifest_path' ...}`. Fixed upstream in ClickHouse/ClickHouse#111786 (merged 2026-07-27, writes the id-carrying schema JSON as the avro.schema header); not in antalya-26.6 / PR 2305. See iceberg/tests/iceberg_engine/native_create/findings.md finding 5.",
        )
    ],
    "/iceberg/native create/*/metadata/pyiceberg reads clickhouse rows*": [
        (
            Error,
            "PyIceberg cannot scan a ClickHouse-written table: the manifest list is written through avro-cpp, which drops the Iceberg `field-id` attributes from the Avro schema, so pyiceberg raises `ValueError: Cannot convert field, missing field-id: {'name': 'manifest_path' ...}`. Fixed upstream in ClickHouse/ClickHouse#111786 (merged 2026-07-27, writes the id-carrying schema JSON as the avro.schema header); not in antalya-26.6 / PR 2305. See iceberg/tests/iceberg_engine/native_create/findings.md finding 5.",
        )
    ],
    "/iceberg/native create/*/sanity/explicit engine create": [
        (
            Fail,
            "On a REST catalog the explicit-engine CREATE writes `metadata/v1-<uuid>.metadata.json` (IcebergMetadata::createInitial) and then RestCatalog::createTable ignores that path and sends a CreateTableRequest, so the server creates the table with its own UUID and its own `00000-<uuid>.metadata.json`. The ClickHouse file is an orphan from birth: B1 sees two initial files, engine SETTINGS never reach the file the catalog uses. See iceberg/tests/iceberg_engine/native_create/findings.md finding 4.",
        )
    ],
    "/iceberg/native create/*/explicit engine/any iceberg engine accepted without fixed backend": [
        (
            Fail,
            "On a REST catalog the explicit-engine CREATE writes `metadata/v1-<uuid>.metadata.json` (IcebergMetadata::createInitial) and then RestCatalog::createTable ignores that path and sends a CreateTableRequest, so the server creates the table with its own UUID and its own `00000-<uuid>.metadata.json`. The ClickHouse file is an orphan from birth: B1 sees two initial files, engine SETTINGS never reach the file the catalog uses. See iceberg/tests/iceberg_engine/native_create/findings.md finding 4.",
        )
    ],
    "/iceberg/native create/*/explicit engine/initial file naming*": [
        (
            Fail,
            "On a REST catalog the explicit-engine CREATE writes `metadata/v1-<uuid>.metadata.json` (IcebergMetadata::createInitial) and then RestCatalog::createTable ignores that path and sends a CreateTableRequest, so the server creates the table with its own UUID and its own `00000-<uuid>.metadata.json`. The ClickHouse file is an orphan from birth: B1 sees two initial files, engine SETTINGS never reach the file the catalog uses. See iceberg/tests/iceberg_engine/native_create/findings.md finding 4.",
        )
    ],
    "/iceberg/native create/*/metadata/gzip metadata*": [
        (
            Fail,
            "On a REST catalog the explicit-engine CREATE writes `metadata/v1-<uuid>.metadata.json` (IcebergMetadata::createInitial) and then RestCatalog::createTable ignores that path and sends a CreateTableRequest, so the server creates the table with its own UUID and its own `00000-<uuid>.metadata.json`. The ClickHouse file is an orphan from birth: B1 sees two initial files, engine SETTINGS never reach the file the catalog uses. See iceberg/tests/iceberg_engine/native_create/findings.md finding 4.",
        )
    ],
    "/iceberg/native create/*/schema/engine settings with explicit engine*": [
        (
            Fail,
            "On a REST catalog the explicit-engine CREATE writes `metadata/v1-<uuid>.metadata.json` (IcebergMetadata::createInitial) and then RestCatalog::createTable ignores that path and sends a CreateTableRequest, so the server creates the table with its own UUID and its own `00000-<uuid>.metadata.json`. The ClickHouse file is an orphan from birth: B1 sees two initial files, engine SETTINGS never reach the file the catalog uses. See iceberg/tests/iceberg_engine/native_create/findings.md finding 4.",
        )
    ],
    "/iceberg/native create/*/sanity/drop with purge": [
        (
            Fail,
            "Every Iceberg commit through a REST catalog leaves an orphan metadata file: IcebergStorageSink writes `metadata/vN-<uuid>.metadata.json`, then RestCatalog::updateMetadata sends only add-snapshot / set-snapshot-ref and the server writes its own `0000N-<uuid>.metadata.json`; the ClickHouse file is never referenced, so `DROP TABLE ... data_lake_delete_data_on_drop = 1` (server-side purge of the metadata tree) cannot remove it and the location is not empty. Pre-existing upstream behaviour (same in master IcebergWrites.cpp); with PR 2305 the leftover then also blocks an explicit-engine re-CREATE at the same location.",
        )
    ],
    "/iceberg/native create/*/drop/drop routes/*": [
        (
            Fail,
            "Every Iceberg commit through a REST catalog leaves an orphan metadata file: IcebergStorageSink writes `metadata/vN-<uuid>.metadata.json`, then RestCatalog::updateMetadata sends only add-snapshot / set-snapshot-ref and the server writes its own `0000N-<uuid>.metadata.json`; the ClickHouse file is never referenced, so `DROP TABLE ... data_lake_delete_data_on_drop = 1` (server-side purge of the metadata tree) cannot remove it and the location is not empty. Pre-existing upstream behaviour (same in master IcebergWrites.cpp); with PR 2305 the leftover then also blocks an explicit-engine re-CREATE at the same location.",
        )
    ],
    "/iceberg/native create/*/drop/server wide default/*": [
        (
            Fail,
            "Every Iceberg commit through a REST catalog leaves an orphan metadata file: IcebergStorageSink writes `metadata/vN-<uuid>.metadata.json`, then RestCatalog::updateMetadata sends only add-snapshot / set-snapshot-ref and the server writes its own `0000N-<uuid>.metadata.json`; the ClickHouse file is never referenced, so `DROP TABLE ... data_lake_delete_data_on_drop = 1` (server-side purge of the metadata tree) cannot remove it and the location is not empty. Pre-existing upstream behaviour (same in master IcebergWrites.cpp); with PR 2305 the leftover then also blocks an explicit-engine re-CREATE at the same location.",
        )
    ],
    "/iceberg/native create/*/lifecycle/recreate after purge drop*": [
        (
            Fail,
            "Every Iceberg commit through a REST catalog leaves an orphan metadata file: IcebergStorageSink writes `metadata/vN-<uuid>.metadata.json`, then RestCatalog::updateMetadata sends only add-snapshot / set-snapshot-ref and the server writes its own `0000N-<uuid>.metadata.json`; the ClickHouse file is never referenced, so `DROP TABLE ... data_lake_delete_data_on_drop = 1` (server-side purge of the metadata tree) cannot remove it and the location is not empty. Pre-existing upstream behaviour (same in master IcebergWrites.cpp); with PR 2305 the leftover then also blocks an explicit-engine re-CREATE at the same location.",
        )
    ],
    "/iceberg/native create/*/sanity/create as source copies keys": [
        (
            Fail,
            "ClickHouse writes non-spec plural partition transform names `days` / `hours` for toRelativeDayNum / toRelativeHourNum (Utils.cpp getPartitionField), so PyIceberg parses the spec as `unknown`. Fixed upstream in ClickHouse/ClickHouse#114864 (closes #114848, merged 2026-08-28); not yet in antalya-26.6 / PR 2305.",
        )
    ],
    "/iceberg/native create/*/schema/accepted transforms/PARTITION BY toRelativeDayNum*": [
        (
            Fail,
            "ClickHouse writes non-spec plural partition transform names `days` / `hours` for toRelativeDayNum / toRelativeHourNum (Utils.cpp getPartitionField), so PyIceberg parses the spec as `unknown`. Fixed upstream in ClickHouse/ClickHouse#114864 (closes #114848, merged 2026-08-28); not yet in antalya-26.6 / PR 2305.",
        )
    ],
    "/iceberg/native create/*/schema/accepted transforms/PARTITION BY toRelativeHourNum*": [
        (
            Fail,
            "ClickHouse writes non-spec plural partition transform names `days` / `hours` for toRelativeDayNum / toRelativeHourNum (Utils.cpp getPartitionField), so PyIceberg parses the spec as `unknown`. Fixed upstream in ClickHouse/ClickHouse#114864 (closes #114848, merged 2026-08-28); not yet in antalya-26.6 / PR 2305.",
        )
    ],
    "/iceberg/native create/*/metadata/initial file/*": [
        (
            Fail,
            "ClickHouse writes non-spec plural partition transform names `days` / `hours` for toRelativeDayNum / toRelativeHourNum (Utils.cpp getPartitionField), so PyIceberg parses the spec as `unknown`. Fixed upstream in ClickHouse/ClickHouse#114864 (closes #114848, merged 2026-08-28); not yet in antalya-26.6 / PR 2305.",
        )
    ],
    "/iceberg/native create/*/lifecycle/insert alter select*/PyIceberg sees the final schema and rows": [
        (
            Fail,
            "ClickHouse writes non-spec plural partition transform names `days` / `hours` for toRelativeDayNum / toRelativeHourNum (Utils.cpp getPartitionField), so PyIceberg parses the spec as `unknown`. Fixed upstream in ClickHouse/ClickHouse#114864 (closes #114848, merged 2026-08-28); not yet in antalya-26.6 / PR 2305.",
        ),
        (
            Error,
            "PyIceberg cannot scan a ClickHouse-written table: the manifest list is written through avro-cpp, which drops the Iceberg `field-id` attributes from the Avro schema, so pyiceberg raises `ValueError: Cannot convert field, missing field-id: {'name': 'manifest_path' ...}`. Fixed upstream in ClickHouse/ClickHouse#111786 (merged 2026-07-27, writes the id-carrying schema JSON as the avro.schema header); not in antalya-26.6 / PR 2305. See iceberg/tests/iceberg_engine/native_create/findings.md finding 5.",
        ),
    ],
    "/iceberg/export partition/: catalog/*/manifest integrity/value_counts across data files sum to source row count": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION never populates `value_counts` in "
            "manifest entries (IcebergWrites.cpp / IcebergDataFileEntry.h "
            "only track column_sizes / null_value_counts / lower_bounds / "
            "upper_bounds). The Avro field is left null.",
        )
    ],
    "/iceberg/export partition/: catalog/*/manifest integrity/data file paths live under the table prefix": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION writes `path_in_storage` (bucket-"
            "relative path) to manifest entry `file_path`, ignoring "
            "`write_full_path_in_iceberg_metadata`. Per Iceberg spec the "
            "field is a 'Location URI with FS scheme' and should be "
            "`path_in_metadata` (e.g. s3://<bucket>/...). See "
            "MultipleFileWriter::startNewFile in MultipleFileWriter.cpp.",
        )
    ],
    "/iceberg/export partition/: catalog/*/manifest integrity/external iceberg reader round-trips exported data": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/2161 — "
            "PyIceberg cannot scan EXPORT PARTITION data files: Parquet "
            "written by ClickHouse lacks Iceberg field-ids and IcebergS3 "
            "tables have no schema.name-mapping.default, so strict readers "
            "raise ValueError during schema resolution. On builds that "
            "still write bucket-relative data_file.file_path, the scenario "
            "may instead fail with FileNotFoundError (local FileIO fallback).",
        )
    ],
    "/iceberg/export partition/: catalog/*/catalogs/catalog: external reader round-trips exported data": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/2161 — "
            "Same Parquet field-id / name-mapping gap as the no_catalog "
            "external-reader scenario: catalog-backed tables get a proper "
            "Iceberg schema from PyIceberg at CREATE time, but EXPORT "
            "PARTITION still writes Parquet without embedded field-ids. "
            "Older builds may instead hit FileNotFoundError when "
            "data_file.file_path lacks a URI scheme.",
        )
    ],
    "/iceberg/export partition/ice catalog/*/truncate/export after truncate repopulates destination": [
        (
            Fail,
            "ClickHouse bug: TRUNCATE and EXPORT disagree on the Iceberg "
            "metadata path format under Ice (ice-rest-catalog / Iceberg REST "
            "Catalog Spec). EXPORT commits manifest / manifest-list entries "
            "as bucket-relative paths "
            "(`/data/<table>/metadata/snap-...avro`). "
            "`IcebergMetadata::truncate` instead serialises those same "
            "entries as full `s3://bucket/...` URIs. When the next "
            "EXPORT runs after a TRUNCATE, IcebergWrites.cpp refuses "
            "to commit with `Paths in Iceberg must use a consistent "
            "format — either /your/path or s3://your/path. Use the "
            "write_full_path_in_iceberg_metadata setting to control "
            "this behavior`, and the background scheduler retries "
            "forever (task stuck in PENDING). Glue does not trip this "
            "because `apply_glue_metadata_path_workaround` already "
            "forces `write_full_path_in_iceberg_metadata=1` on both "
            "EXPORT and TRUNCATE there, so both sides write full "
            "URIs. Fix is upstream: either `IcebergMetadata::truncate` "
            "must honour the same path-format default as EXPORT, or "
            "the consistency check in IcebergWrites needs to look at "
            "new writes only instead of the inherited snapshot chain.",
        )
    ],
    "/iceberg/export partition/: catalog/*/datatypes/*/accepted/accepted*UInt64*": [
        (
            Fail,
            "ClickHouse maps UInt64 to Iceberg long (signed). Values above "
            "INT64_MAX (e.g. 18446744073709551615) round-trip as -1 on "
            "IcebergS3 read-back; byte-compare fails until export/read uses "
            "a type that preserves the full unsigned range or rejects "
            "out-of-range values at export time.",
        )
    ],
    "/iceberg/export partition/: catalog/*/settings/output_format_parquet_compression_method flows to data files": [
        (
            Fail,
            "ClickHouse EXPORT PARTITION does not propagate format-level "
            "settings from the `ALTER ... EXPORT PARTITION ... SETTINGS` "
            "clause to the background export task. "
            "ExportReplicatedMergeTreePartitionManifest has no generic "
            "settings blob and "
            "ExportPartitionUtils::getContextCopyWithTaskSettings uses a "
            "hardcoded allowlist that omits format settings, so "
            "`output_format_parquet_compression_method` is dropped before "
            "ExportPartTask::executeStep calls getFormatSettings and the "
            "Parquet writer always falls back to the server-profile "
            "default codec. Intentional for now per dev; remove this "
            "entry once the manifest carries format settings end-to-end.",
        )
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery alias/subquery select alias": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery nested/cte with alias": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery nested/cte with group by": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery nested/cte with order by": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery nested/cte with limit": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/subquery nested/cte with order by and limit": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/union alias/union all with alias": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/query context/set operations alias/intersect except with alias/*": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/1424"),
    ],
    "/iceberg/hybrid/hybrid alias/constants/default json/*": [
        (Fail, "https://github.com/Altinity/ClickHouse/issues/2122"),
    ],
    "/iceberg/icebergS3 table function/recreate table/scan and display data with pyiceberg, expect empty table": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/75187")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/rest catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/glue catalog/icebergS3 table function/recreate table and insert new data multiple times/verify that ClickHouse reads the new data （one row）/try #10": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/87574")
    ],
    "/iceberg/icebergS3 table function/*": [
        (Fail, "Need to investigate", check_clickhouse_version("<=24")),
    ],
    "/iceberg/iceberg table engine/deletes/position delete smoke": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/114183",
        ),
    ],
    "/iceberg/iceberg engine/* catalog/position delete reads/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/114183",
        ),
    ],
    "/iceberg/iceberg table engine/compaction/compaction smoke": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/114183",
            check_clickhouse_version("<26.6"),
        ),
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/113745",
            check_clickhouse_version(">=26.6"),
        ),
    ],
    "/iceberg/iceberg engine/* catalog/swarm/*": [
        (Fail, "Only works with antalya build", check_if_not_antalya_build),
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/2139",
            check_if_antalya_build,
        ),
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg cache/glue catalog/iceberg table engine/*": [
        (Fail, "Need to investigate"),
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with decimal column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/predicate push down/issue with float column": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/80200")
    ],
    "/iceberg/iceberg engine/* catalog/feature/multiple tables": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/75187",
            check_clickhouse_version("<25.3"),
        ),
    ],
    "/iceberg/iceberg engine/glue catalog/schema evolution/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81272",
            check_clickhouse_version("<25.7"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/nested datatypes/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/81301",
            check_clickhouse_version("<25.5"),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/sanity/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/82601",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_clickhouse_version("<25.4")(test),
        )
    ],
    "/iceberg/iceberg engine/: catalog/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter:/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/86024",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg table engine/feature/alter comment columns": [
        (
            Fail,
            "Need to investigate",
            check_clickhouse_version(">=25.6"),
        )
    ],
    "/iceberg/iceberg engine/rest catalog/feature/show databases queries/*": [
        (
            Fail,
            "https://github.com/Altinity/clickhouse-regression/issues/86",
            lambda test: check_clickhouse_version(">=25.8")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg table engine/write min max pruning/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/91363",
            lambda test: (
                check_if_not_antalya_build(test)
                and check_clickhouse_version("<26.1")(test)
            )
            or (
                check_if_antalya_build(test)
                and check_clickhouse_version("<=25.8.9")(test)
            ),
        )
    ],
    "/iceberg/iceberg engine/glue catalog/feature/show data lake catalogs in system tables/*": [
        (
            Fail,
            "https://github.com/clickhouse/clickhouse/issues/91363",
            check_clickhouse_version(">=25.8"),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/rest catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/glue catalog/iceberg database engine/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg cache/glue catalog/icebergS3 table function/cache": [
        (
            Fail,
            "https://github.com/Altinity/ClickHouse/issues/1277",
            lambda test: check_clickhouse_version(">=25.3")(test)
            and check_if_antalya_build(test),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check iceberg partition pruning with integer type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/check partition pruning with complex where clause": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/iceberg partition pruning/partition pruning with date type": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/93416",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/predicate push down/check input format parquet filter push down/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/97172",
            check_clickhouse_version(">=26.1"),
        )
    ],
    "/iceberg/iceberg engine/: catalog/feature/select from system databases/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/103542",
            lambda test: check_clickhouse_version("<26.4")(test)
            and check_if_not_antalya_build(),
        )
    ],
    "/iceberg/export partition/: catalog/*/catalogs/drop with purge allows recreating same table": [
        (
            Fail,
            "DROP with iceberg_delete_data_on_drop does not remove warehouse "
            "metadata; recreate hits TABLE_ALREADY_EXISTS "
            "(https://github.com/Altinity/ClickHouse/issues/1906)",
        )
    ],
    "/iceberg/export partition/: catalog/*/disaster recovery/KILL EXPORT PARTITION during commit transitions to KILLED": [
        (
            Fail,
            "Altinity/ClickHouse#1984 per-part backoff removed "
            "export_merge_tree_partition_max_retries; failpoint harness "
            "needs a dev update on >=26.3.13.20001",
            check_clickhouse_version(">=26.3.13.20001"),
        )
    ],
    "/iceberg/export partition/: catalog/*/transactions/commit survives pre-publish failure": [
        (
            Fail,
            "Altinity/ClickHouse#1984 changed non-retryable pre-publish "
            "classification; iceberg_writes_non_retry_cleanup failpoint "
            "harness needs a dev update on >=26.3.13.20001",
            check_clickhouse_version(">=26.3.13.20001"),
        )
    ],
    "/iceberg/export partition/: catalog/plain merge tree/disaster recovery/KILL EXPORT PARTITION while moves are stopped transitions to KILLED": [
        (
            Fail,
            "Plain MergeTree KILL EXPORT PARTITION: "
            "MergeTreePartitionExportScheduler::kill uses "
            "tasks.find(transaction_id) but the registry map is keyed by "
            "composite_key (partition + destination) "
            "(Altinity/ClickHouse#2032)",
            check_clickhouse_version(">=26.3.13.20001"),
        )
    ],
    "/iceberg/export partition/: catalog/plain merge tree/system monitoring/KILL EXPORT preserves provenance fields": [
        (
            Fail,
            "Plain MergeTree KILL EXPORT PARTITION: same scheduler kill() "
            "lookup bug as disaster recovery/KILL while moves stopped "
            "(Altinity/ClickHouse#2032)",
            check_clickhouse_version(">=26.3.13.20001"),
        )
    ],
    "/iceberg/export partition/: catalog/*/partition compatibility/reversed destination column order maps values by name": [
        (
            Fail,
            "EXPORT PARTITION matches source columns to the destination "
            "positionally (like INSERT SELECT *), so permuted destination "
            "column order mis-assigns values and can break partition "
            "semantics (https://github.com/Altinity/ClickHouse/issues/2123)",
        )
    ],
}

ffails = {
    "/iceberg/native create": (
        Skip,
        "Native CREATE TABLE / DROP TABLE for DataLakeCatalog is an Antalya feature "
        "introduced in Antalya 26.6 (Altinity/ClickHouse#2305)",
        lambda test: not (
            check_if_antalya_build(test) and check_clickhouse_version(">=26.6")(test)
        ),
    ),
    "/iceberg/iceberg engine": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/iceberg cache": (
        Skip,
        "Iceberg engine was introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/iceberg/icebergS3 table function": (
        Skip,
        "Iceberg engine was introduced in 23.2",
        check_clickhouse_version("<=23.2"),
    ),
    "/iceberg/s3 table function": (
        Skip,
        "Support for codec 'zstd' not built",
        check_clickhouse_version("<23.8"),
    ),
    "/iceberg/iceberg table engine": (
        Skip,
        "Iceberg table engine was introduced in 23.2",
        check_clickhouse_version("<24.2"),
    ),
    "/iceberg/iceberg cache/*": (
        Skip,
        "Metadata caching was introduced in antalya build from 24.12",
        check_if_not_antalya_build,
    ),
    "/iceberg/iceberg engine/: catalog/feature/show data lake catalogs in system tables": (
        Skip,
        "show_data_lake_catalogs_in_system_tables setting is not supported before 25.3 and on 25.4",
        lambda test: check_clickhouse_version("<25.3")(test)
        or check_clickhouse_version("==25.4")(test),
    ),
    "/iceberg/icebergS3 table function/: catalog/several iceberg tables in one dir": (
        Skip,
        "setting used for test introduced in 25.8",
        check_clickhouse_version("<25.8"),
    ),
    "/iceberg/iceberg engine/: catalog/iceberg iterator race condition/iceberg iterator race condition": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/issues/92120",
        lambda test: check_clickhouse_version("<=25.8.12")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/iceberg engine/: catalog/namespace filtering": (
        Skip,
        "namespace filtering is supported only in antalya build from >= 25.8",
        lambda test: check_clickhouse_version("<=25.8.15")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/iceberg engine/: catalog/sort key timezone/*": (
        Skip,
        "iceberg_partition_timezone sort key support introduced in antalya-26.1",
        lambda test: check_if_not_antalya_build(test)
        or check_clickhouse_version("<26.1")(test),
    ),
    "/iceberg/iceberg engine/: catalog/dot separated column names/*": (
        Skip,
        "dot-separated column names broken before 25.7 and in 25.11-26.1 (https://github.com/ClickHouse/ClickHouse/issues/94196)",
        lambda test: check_clickhouse_version("<25.7")(test)
        or (
            check_clickhouse_version(">=25.11")(test)
            and check_clickhouse_version("<26.2")(test)
        ),
    ),
    "/iceberg/iceberg engine/: catalog/show_data_lake_catalogs hint/*": (
        Skip,
        "Pending https://github.com/ClickHouse/ClickHouse/pull/100452 — Antalya 26.1+ for now; revise when merged",
        lambda test: check_clickhouse_version("<26.1")(test)
        or check_if_not_antalya_build(test),
    ),
    "/iceberg/export partition": (
        Skip,
        "EXPORT PARTITION TO Apache Iceberg is only supported on Antalya builds > 26.1",
        lambda test: check_if_not_antalya_build(test)
        or check_clickhouse_version("<26.1")(test),
    ),
    "/iceberg/export partition/: catalog/*/schema evolution/rename column between exports": (
        Skip,
        "RENAME COLUMN on IcebergS3 destination is NOT_IMPLEMENTED before 26.3",
        check_clickhouse_version("<26.3"),
    ),
    "/iceberg/export partition/: catalog/plain merge tree/*": (
        Skip,
        "Plain MergeTree EXPORT PARTITION is not merged yet "
        "(Altinity/ClickHouse#2032)",
        lambda test: True,
    ),
    "/iceberg/export partition/: catalog/*/settings/schema match mode/*": (
        Skip,
        "export_merge_tree_part_schema_match_mode is not merged yet "
        "(Altinity/ClickHouse#2220)",
        lambda test: True,
    ),
    "/iceberg/export partition/: catalog/*/schema compatibility/*": (
        Skip,
        "create-time schema compatibility matrix is not merged yet "
        "(Altinity/ClickHouse#2134, #2220)",
        lambda test: True,
    ),
    "/iceberg/export partition/: catalog/*/system monitoring/commit-info columns name Iceberg files after success": (
        Skip,
        "commit-info persistence is not in a released build yet "
        "(Altinity/ClickHouse#2290)",
        lambda test: True,
    ),
    "/iceberg/export partition/: catalog/*/system monitoring/commit-info columns stay empty before commit": (
        Skip,
        "commit-info persistence is not in a released build yet "
        "(Altinity/ClickHouse#2290)",
        lambda test: True,
    ),
    # Altinity/ClickHouse#2157: getIcebergType gained Int8/UInt8/Bool/Decimal
    # on 26.6. Older builds still reject those types.
    "/iceberg/export partition/: catalog/*/datatypes/*/accepted/* Int8": (
        Skip,
        "Int8 -> Iceberg int requires 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version("<26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/accepted/* UInt8": (
        Skip,
        "UInt8 -> Iceberg int requires 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version("<26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/accepted/* Bool": (
        Skip,
        "Bool -> Iceberg boolean requires 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version("<26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/accepted/* Decimal*": (
        Skip,
        "Decimal -> Iceberg decimal requires 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version("<26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/rejected/* Int8": (
        Skip,
        "Int8 is accepted from 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version(">=26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/rejected/* UInt8": (
        Skip,
        "UInt8 is accepted from 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version(">=26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/rejected/* Bool": (
        Skip,
        "Bool is accepted from 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version(">=26.6"),
    ),
    "/iceberg/export partition/: catalog/*/datatypes/*/rejected/* Decimal*10*": (
        Skip,
        "Decimal(p<=38) is accepted from 26.6 (Altinity/ClickHouse#2157)",
        check_clickhouse_version(">=26.6"),
    ),
    # After #2074 (26.3.17+) / #2253 (26.6.2+) Iceberg export no longer
    # rejects these spec mismatches (returns 0 instead of BAD_ARGUMENTS).
    # Identity column mismatch and icebergBucket width mismatch still reject.
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*compound field order reversed": (
        Skip,
        "compound field-order mismatch is not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*transform vs identity*": (
        Skip,
        "transform-vs-identity mismatch is not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*truncate width mismatch*": (
        Skip,
        "truncate width mismatch is not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*field-count mismatch*": (
        Skip,
        "partition field-count mismatch is not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*unsupported MergeTree expression*": (
        Skip,
        "unsupported MergeTree partition expressions are not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/partition compatibility/rejected/*unpartitioned destination": (
        Skip,
        "partitioned-source / unpartitioned-destination is not rejected after "
        "Altinity/ClickHouse#2074 (26.3.17+) / #2253 (26.6.2+)",
        check_monotonic_export_partition_compat,
    ),
    "/iceberg/export partition/: catalog/*/casting": (
        Skip,
        "Altinity/ClickHouse#1779 export auto-cast requires > 26.3.10.20001",
        check_clickhouse_version("<=26.3.10.20001"),
    ),
    "/iceberg/export partition/glue catalog/*/casting": (
        Skip,
        "PR 1779 casting uses CH-native Iceberg DDL destinations (no_catalog and "
        "ice-rest-catalog); Glue/LocalStack DataLakeCatalog is out of scope.",
        lambda test: True,
    ),
    "/iceberg/hybrid": (
        Skip,
        "Hybrid table engine is Antalya-only",
        check_if_not_antalya_build,
    ),
    "/iceberg/cluster join filter": (
        Skip,
        "icebergS3Cluster JOIN filter pushdown lands in Antalya 26.6 "
        "(Altinity/ClickHouse#2249)",
        lambda test: check_if_not_antalya_build(test)
        or check_clickhouse_version("<26.6")(test),
    ),
    # "/iceberg/iceberg engine/: catalog/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),
    # "/iceberg/iceberg table engine/feature/alter:/*": (
    #     Skip,
    #     "https://github.com/clickhouse/clickhouse/issues/86024",
    #     check_clickhouse_version(">=25.8"),
    # ),
}


_RUNTIME_USERS_D_FILES = (
    "allow_experimental_insert_into_iceberg.xml",
    "allow_experimental_hybrid_table.xml",
)


def _sweep_runtime_users_d_overlays():
    """Remove leftover runtime-pushed users.d files from a previous run."""
    users_d_dir = os.path.join(current_dir(), "configs", "clickhouse", "users.d")
    for name in _RUNTIME_USERS_D_FILES:
        path = os.path.join(users_d_dir, name)
        if os.path.exists(path):
            try:
                os.remove(path)
            except PermissionError:
                # Container-written overlays are often root-owned on the host.
                # Hybrid feature still forces enable_analyzer via query settings.
                pass


@TestModule
@Name("iceberg")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser_minio)
@Specifications(Apache_Iceberg_Table)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
):
    """Run tests for Iceberg tables."""
    warnings.filterwarnings(
        "ignore", message="Delete operation did not match any records"
    )

    nodes = {
        "clickhouse": (
            "clickhouse1",
            "clickhouse2",
            "clickhouse3",
        ),
    }

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value

    with Given("sweep stale runtime users.d overlays"):
        _sweep_runtime_users_d_overlays()

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
            environ={
                "MINIO_ROOT_USER": minio_root_user,
                "MINIO_ROOT_PASSWORD": minio_root_password,
            },
        )
        self.context.cluster = cluster

    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node2 = self.context.cluster.node("clickhouse2")
    self.context.node3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node2, self.context.node3]

    with And("enable or disable experimental analyzer if needed"):
        for node in self.context.nodes:
            experimental_analyzer(node=node, with_analyzer=with_analyzer)

    Feature(
        test=load("iceberg.tests.iceberg_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.iceberg_engine.native_create.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.iceberg_table_engine.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.s3_table_function.s3_table_function", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.icebergS3_table_function.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.cache.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    Feature(
        test=load("iceberg.tests.export_partition.feature", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.deletion_vectors.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    #
    # Feature(
    #     test=load("iceberg.tests.deletion_vectors.delta_feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    #
    # Feature(
    #     test=load("iceberg.tests.cluster_join_filter.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.hybrid.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)

    # Feature(
    #     test=load("iceberg.tests.catalogs.feature", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)


if main():
    regression()
