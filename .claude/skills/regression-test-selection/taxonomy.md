# Feature taxonomy

A leaf is a feature a pull request is about. Select ids from this list only.

A parent id includes every child. A child id is that child only.

## Query

- `query.parser` — SQL syntax and the parser.
- `query.analyzer` — the analyzer and query tree.
- `query.planner` — the planner and distributed plan.
- `query.execution` — the interpreter, processors, and query pipeline.
- `query.joins` — joins.
- `query.aggregates` — GROUP BY and aggregate execution.
- `query.window_functions` — window functions.
- `query.subqueries` — subqueries, CTEs, and scalar subqueries.
- `query.views` — normal views.
- `query.views.materialized` — materialized views.
- `query.views.live` — live and window views.
- `query.views.refreshable` — refreshable materialized views.
- `query.functions` — ordinary and table functions.
- `query.functions.aggregate` — aggregate function definitions.
- `query.settings` — settings, profiles, and compatibility.
- `query.distributed` — distributed queries, shards, and ON CLUSTER execution.
- `query.parallel_replicas` — parallel replicas.

## Data types

- `types.core` — numeric, string, date, enum, UUID, and IP types.
- `types.composite` — Nullable, Array, Tuple, Map, Nested, LowCardinality, Variant, and Dynamic.
- `types.json` — the JSON type.
- `types.datetime64` — DateTime64 and the extended range.
- `types.decimal` — Decimal and extended precision.
- `types.geo` — point, ring, polygon, and related functions.
- `types.domain` — fixed-string, IPv4, IPv6, and other domain types.
- `types.aggregate_state` — AggregateFunction and SimpleAggregateFunction states.

## Table engines

- `engines.mergetree` — the MergeTree family: plain, Replacing, Summing, Aggregating, Collapsing, VersionedCollapsing, and Graphite.
- `engines.mergetree.parts` — parts, merges, and compaction.
- `engines.mergetree.mutations` — mutations, including ALTER UPDATE and ALTER DELETE.
- `engines.mergetree.lightweight_delete` — lightweight delete.
- `engines.mergetree.replication` — ReplicatedMergeTree.
- `engines.mergetree.partitioning` — partition keys and partition pruning.
- `engines.mergetree.ttl` — column and table TTL.
- `engines.mergetree.projections` — projections.
- `engines.mergetree.indexes` — skipping indexes, text indexes, and statistics.
- `engines.mergetree.unique_key` — the unique-key engine.
- `engines.log` — Log, TinyLog, and StripeLog.
- `engines.special` — Memory, Buffer, Set, Join, Null, File, URL, Executable, and GenerateRandom.
- `engines.distributed` — the Distributed engine.
- `engines.merge` — the Merge engine.
- `engines.dictionary` — the Dictionary engine.
- `engines.external` — MySQL, PostgreSQL, MongoDB, SQLite, Redis, Hive, HDFS, and JDBC engines.
- `engines.kafka` — Kafka.
- `engines.queues` — NATS, RabbitMQ, and FileLog.
- `engines.keepermap` — KeeperMap.
- `engines.rocksdb` — EmbeddedRocksDB.
- `engines.timeseries` — the time series engine.
- `engines.hybrid` — hybrid tables.
- `engines.arrowflight` — ArrowFlight.
- `engines.ytsaurus` — YTsaurus.

## Databases

- `databases.atomic` — Atomic and Ordinary databases, including attach and detach.
- `databases.replicated` — DatabaseReplicated and replicated DDL.
- `databases.external` — MySQL, PostgreSQL, SQLite, and MaterializedPostgreSQL database engines.
- `databases.catalog` — data lake catalogs as databases.
- `databases.lazy` — the Lazy database engine.

## Object storage and data lakes

- `storage.s3` — the S3 disk, the s3 table function, and the S3 engine.
- `storage.s3.iam` — IAM and role-based authentication.
- `storage.gcs` — GCS.
- `storage.azure` — Azure Blob Storage.
- `storage.hdfs` — HDFS and Web disks.
- `storage.policies` — storage policies, volumes, and moves between disks.
- `storage.tiered` — tiered storage.
- `storage.zero_copy` — zero-copy replication.
- `storage.disk_encryption` — an encrypted disk wrapped around another disk.
- `storage.cas` — content-addressed storage. Run the suites CI starts with `--cas`.
- `storage.cas.cache` — the same suites CI starts with `--cas-s3-cache`.
- `storage.cas.gc` — CAS garbage collection.
- `storage.iceberg` — Iceberg reads.
- `storage.iceberg.engine` — the Iceberg table engine.
- `storage.iceberg.writes` — native Iceberg CREATE and writes.
- `storage.iceberg.catalog` — REST, Glue, and Hive catalogs.
- `storage.iceberg.cache` — the Iceberg metadata cache.
- `storage.iceberg.deletion_vectors` — deletion vectors.
- `storage.iceberg.export` — EXPORT PARTITION to Iceberg.
- `storage.iceberg.export_ttl` — export TTL.
- `storage.delta` — Delta Lake.
- `storage.hudi` — Hudi.
- `storage.paimon` — Paimon.
- `storage.hive_partitioning` — hive-style partition paths.
- `storage.parquet` — Parquet reads and writes through table functions and engines.

## Formats

- `formats.row` — CSV, TSV, JSONEachRow, Values, and similar row formats.
- `formats.columnar` — Parquet, ORC, Arrow, and Native.
- `formats.inference` — schema inference.
- `formats.output` — Pretty and other client output formats.

## DDL

- `ddl.create` — CREATE, DROP, RENAME, EXCHANGE, UNDROP, and TRUNCATE.
- `ddl.alter_columns` — ALTER of columns, comments, and settings.
- `ddl.attach` — ATTACH and DETACH of tables and partitions.
- `ddl.partition` — ALTER PARTITION, including move, replace, drop, and fetch.
- `ddl.partition.move_between_shards` — moving parts between shards.
- `ddl.export_part` — EXPORT PART.
- `ddl.export_partition` — EXPORT PARTITION.
- `ddl.on_cluster` — distributed DDL.
- `ddl.atomic_insert` — atomic insert.

## Replication and coordination

- `coordination.keeper` — ClickHouse Keeper.
- `coordination.keeper_failover` — Keeper failover.
- `coordination.zookeeper` — the ZooKeeper client protocol.
- `coordination.replication_queue` — the replication queue, fetches, and merges across replicas.
- `cluster.swarm` — swarm clusters.

## Access control

- `access.rbac` — users, roles, grants, quotas, and settings profiles.
- `access.rbac.privileges` — privilege checks.
- `access.rbac.row_policies` — row policies.
- `access.sql_security` — SQL security definers on views.
- `access.auth.password` — password authentication.
- `access.auth.ldap` — LDAP.
- `access.auth.kerberos` — Kerberos.
- `access.auth.jwt` — JWT.
- `access.auth.oauth` — OAuth.
- `access.auth.multiple` — multiple authentication methods.
- `access.tls` — server TLS and interserver HTTPS.
- `access.encryption` — the encrypt and decrypt SQL functions. Disk encryption is `storage.disk_encryption`.

## Dictionaries

- `dictionaries.sources` — dictionary sources.
- `dictionaries.layouts` — dictionary layouts and lifetime.

## Backup

- `backup.backup_restore` — BACKUP and RESTORE.
- `backup.freeze` — FREEZE and UNFREEZE.

## Interfaces

- `interfaces.native` — the native TCP protocol.
- `interfaces.http` — the HTTP interface.
- `interfaces.mysql` — the MySQL wire protocol.
- `interfaces.postgresql` — the PostgreSQL wire protocol.
- `interfaces.grpc` — gRPC.
- `interfaces.clients` — ODBC, JDBC, and other client drivers.

## Operations

- `ops.system_tables` — system tables.
- `ops.caches` — mark, uncompressed, query, and filesystem caches.
- `ops.async_insert` — asynchronous inserts.
- `ops.deduplication` — insert deduplication.
- `ops.background` — background pools, merges, and mutation scheduling.
- `ops.metrics` — Prometheus, OpenTelemetry, and query log.
- `ops.crash_recovery` — startup after a crash. Not BACKUP or RESTORE.

## Runtime

- `runtime.common` — shared code in Common, memory tracking, and threading. Selects the broad profile, which is not defined yet.
- `runtime.compression` — codecs.
- `runtime.io` — the IO and read-buffer stack.
- `runtime.dns` — DNS resolution.
