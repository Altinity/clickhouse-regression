# Taxonomy to regression tests

Paths under "Runs" are started by the suite. Paths under "Not started" exist on disk and are not part of the default run. Recommend "Runs" only.

MinIO, AWS, GCS, Hetzner, and Azure are run targets of the same `s3` tests. A `storage.gcs` or `storage.azure` selection still names those shared paths, and names the backend.

## query.aggregates

Runs:

- `aggregate_functions/tests/function_list.py`
- `aggregate_functions/tests/run_with_extra_data`
- `aggregate_functions/tests/state`
- `aggregate_functions/tests/merge`

## query.window_functions

Runs:

- `window_functions/`
- `aggregate_functions/tests/window_functions`

## query.functions

Runs:

- `functions/tests/plus.py`
- `functions/tests/insert`
- `functions/tests/math_functions`
- `functions/tests/throwIf_function`
- `base_58/`
- `key_value/`
- `session_timezone/tests/date_functions.py`

## query.functions.aggregate

Runs:

- `aggregate_functions/`

## query.settings

Runs:

- `settings/tests/default_values`

## query.execution

Runs:

- `selects/tests/final` — the FINAL modifier only

## query.distributed

Runs:

- `atomic_insert/tests/distributed_table`
- `lightweight_delete/tests/distributed_tables`
- `kafka/tests/distributed`
- `clickhouse_keeper/tests/alter_column_distributed`

No Distributed-engine suite.

## types.composite

Runs:

- `data_types/tests/map` — Map only

## types.json

Runs:

- `json_data_type/`

## types.datetime64

Runs:

- `datetime64_extended_range/`
- `session_timezone/`

## types.decimal

Runs:

- `extended_precision_data_types/`

## types.aggregate_state

Runs:

- `aggregate_functions/tests/state`
- `aggregate_functions/tests/merge`

## engines.mergetree

Runs:

- `engines/tests/replacing_merge_tree/`
- `engines/tests/summing_merge_tree/`
- `functions/tests/merge.py` — a CollapsingMergeTree merge

## engines.mergetree.mutations

Runs:

- `alter/stress/`
- `lightweight_delete/tests/alter_after_delete`

Not started:

- `cas/tests/alter/mutations.py` — `cas/regression.py` does not start `cas/tests/alter/`

## engines.mergetree.lightweight_delete

Runs:

- `lightweight_delete/`

## engines.mergetree.replication

Runs:

- `engines/tests/replacing_merge_tree/replicated_replacing_merge_tree.py`
- `lightweight_delete/tests/replicated_tables`
- `attach/tests/replica_path`
- `tiered_storage/tests/simple_replication_and_moves`

## engines.mergetree.partitioning

Runs:

- `alter/table/replace_partition`
- `alter/table/attach_partition`
- `alter/table/move_partition`

## engines.mergetree.ttl

Runs:

- `lightweight_delete/tests/acceptance_column_ttl`
- `lightweight_delete/tests/delete_and_column_ttl`
- `disk_level_encryption/tests/column_ttl`
- `tiered_storage/tests/ttl_moves`

Not started:

- `cas/tests/alter/ttl.py`

## engines.mergetree.projections

Runs:

- `functions/tests/projection_optimization`
- `lightweight_delete/tests/projections`

Not started:

- `cas/tests/alter/projection.py`

## engines.mergetree.indexes

Not started:

- `cas/tests/alter/index.py`
- `cas/tests/alter/statistics.py`

## engines.kafka

Runs:

- `kafka/`

## engines.external

Runs:

- `parquet/tests/mysql.py` — Parquet round-trip through the MySQL engine
- `parquet/tests/postgresql.py` — Parquet round-trip through the PostgreSQL engine

These do not test the MySQL or PostgreSQL wire protocols.

## engines.hybrid

Not started:

- `iceberg/tests/hybrid/` — `iceberg/regression.py` does not run it

## databases.atomic

Runs:

- `attach/`
- `atomic_insert/`

## databases.catalog

Not started:

- `iceberg/tests/catalogs/`

## storage.s3

Runs:

- `s3/tests/sanity.py`
- `s3/tests/table_function.py`
- `s3/tests/disk.py`
- `s3/tests/settings.py`
- `s3/tests/reconnect.py`
- `s3/tests/orphans.py`
- `s3/tests/cit.py`
- `s3/tests/combinatoric_table.py`
- `s3/tests/remote_s3_function.py`

## storage.s3.iam

Not started:

- `s3/tests/iam_auth.py`
- `s3/tests/ec2.py`

## storage.gcs

Runs: the GCS target of the `storage.s3` paths.

## storage.azure

Runs: the Azure target of the `storage.s3` paths.

## storage.policies

Runs:

- `tiered_storage/tests/keep_free_space`
- `tiered_storage/tests/round_robin`
- `tiered_storage/tests/jbod_overflow`
- `tiered_storage/tests/max_data_part_size`
- `tiered_storage/tests/alter_table_policy`

## storage.tiered

Runs:

- `tiered_storage/tests/alter_move`
- `tiered_storage/tests/background_move`
- `tiered_storage/tests/ttl_moves`
- `tiered_storage/tests/manual_move_with_downtime`
- `tiered_storage/tests/merge_parts_different_volumes`

## storage.zero_copy

Runs:

- `s3/tests/zero_copy_replication.py`

## storage.disk_encryption

Runs:

- `disk_level_encryption/`
- `lightweight_delete/tests/encrypted_disk`

## storage.cas

These are the `--cas` jobs in `run-regression.yml`. Scheduled Antalya runs start them with `run_cas_suites`. `tiered_storage` uses `--with-cas` and starts on every full regression. Do not recommend `cas/soak/`, `cas/jepsen/`, or `alter/stress/`. Those workflows are manual.

Runs:

- `cas/` — the CAS suite. The CI job passes no extra flag.
- `aggregate_functions/` with `--cas --only "/aggregate functions/part 1/*"`
- `aggregate_functions/` with `--cas --only "/aggregate functions/part 2/*"`
- `aggregate_functions/` with `--cas --only "/aggregate functions/part 3/*"`
- `atomic_insert/` with `--cas`
- `alter/` with `--cas --only "/alter/replace partition/*"`
- `alter/` with `--cas --only "/alter/attach partition/part 1/*"`
- `alter/` with `--cas --only "/alter/attach partition/part 2/*"`
- `alter/` with `--cas --only "/alter/attach partition/part 3/*"`
- `alter/` with `--cas --only "/alter/move partition/*"`
- `engines/` with `--cas`
- `lightweight_delete/` with `--cas --only "/lightweight delete/disk space/*"`
- `lightweight_delete/` with `--cas --only "/lightweight delete/hard restart/*"`
- `lightweight_delete/` with `--cas --skip "/lightweight delete/disk space/*" "/lightweight delete/hard restart/*" "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"`
- `lightweight_delete/` with `--cas --only "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"`
- `selects/` with `--cas`
- `tiered_storage/` with `--with-cas`

## storage.cas.cache

The same CI jobs as `storage.cas`, with `--cas-s3-cache` instead of `--cas`. `tiered_storage` has no cache job.

Runs:

- `cas/` with `--cas-s3-cache`
- `aggregate_functions/` with `--cas-s3-cache --only "/aggregate functions/part 1/*"`
- `aggregate_functions/` with `--cas-s3-cache --only "/aggregate functions/part 2/*"`
- `aggregate_functions/` with `--cas-s3-cache --only "/aggregate functions/part 3/*"`
- `atomic_insert/` with `--cas-s3-cache`
- `alter/` with `--cas-s3-cache --only "/alter/replace partition/*"`
- `alter/` with `--cas-s3-cache --only "/alter/attach partition/part 1/*"`
- `alter/` with `--cas-s3-cache --only "/alter/attach partition/part 2/*"`
- `alter/` with `--cas-s3-cache --only "/alter/attach partition/part 3/*"`
- `alter/` with `--cas-s3-cache --only "/alter/move partition/*"`
- `engines/` with `--cas-s3-cache`
- `lightweight_delete/` with `--cas-s3-cache --only "/lightweight delete/disk space/*"`
- `lightweight_delete/` with `--cas-s3-cache --only "/lightweight delete/hard restart/*"`
- `lightweight_delete/` with `--cas-s3-cache --skip "/lightweight delete/disk space/*" "/lightweight delete/hard restart/*" "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"`
- `lightweight_delete/` with `--cas-s3-cache --only "/lightweight delete/alter after delete/*" "/lightweight delete/concurrent alter and delete/*" "/lightweight delete/concurrent delete/*" "/lightweight delete/basic checks/*" "/lightweight delete/performance/*" "/lightweight delete/ontime tests/*"`
- `selects/` with `--cas-s3-cache`

## storage.iceberg

Runs:

- `iceberg/tests/iceberg_engine/`
- `iceberg/tests/icebergS3_table_function/`
- `ice/` — the Ice CLI

## storage.iceberg.engine

Runs:

- `iceberg/tests/iceberg_table_engine/`

## storage.iceberg.writes

Runs:

- `iceberg/tests/iceberg_engine/native_create/`

## storage.iceberg.cache

Runs:

- `iceberg/tests/cache/`

## storage.iceberg.catalog

Not started:

- `iceberg/tests/catalogs/`

## storage.iceberg.deletion_vectors

Not started:

- `iceberg/tests/deletion_vectors/`

## storage.iceberg.export

Runs:

- `iceberg/tests/export_partition/`

## storage.iceberg.export_ttl

Runs:

- `iceberg/tests/export_ttl/`

## storage.delta

Not started:

- `iceberg/tests/deletion_vectors/` — the Delta feature there is commented out

## storage.hive_partitioning

Runs:

- `hive_partitioning/`
- `s3/tests/hive_partitioning.py`

## storage.parquet

Runs:

- `parquet/tests/`
- `parquet/performance/`

## formats.columnar

Runs:

- `parquet/` — Parquet only. ORC, Arrow, and Native have no suite.

## ddl.alter_columns

Runs:

- `alter/stress/`

Not started:

- `cas/tests/alter/column.py`
- `cas/tests/alter/constraint.py`
- `cas/tests/alter/keys.py`

## ddl.attach

Runs:

- `attach/`
- `alter/table/attach_partition`

## ddl.partition

Runs:

- `alter/table/replace_partition`
- `alter/table/attach_partition`
- `alter/table/move_partition`

## ddl.partition.move_between_shards

Runs:

- `part_moves_between_shards/`

## ddl.export_part

Runs:

- `s3/tests/export_part/`

## ddl.export_partition

Runs:

- `s3/tests/export_partition/`

## ddl.on_cluster

Runs:

- `clickhouse_keeper/tests/alter_column_distributed`

## ddl.atomic_insert

Runs:

- `atomic_insert/`

## coordination.keeper

Runs:

- `clickhouse_keeper/`

## coordination.keeper_failover

Runs:

- `clickhouse_keeper_failover/`

## coordination.replication_queue

Runs:

- `lightweight_delete/tests/replication_queue`

## cluster.swarm

Runs:

- `swarms/`

## access.rbac

Runs:

- `rbac/tests/syntax`

## access.rbac.privileges

Runs:

- `rbac/tests/privileges`

## access.rbac.row_policies

Runs:

- `rbac/tests/privileges/show/show_row_policies.py`

Other row-policy privilege checks live in `rbac/tests/privileges`.

## access.sql_security

Runs:

- `rbac/tests/sql_security`
- `rbac/tests/views`

## access.auth.ldap

Runs:

- `ldap/authentication`
- `ldap/external_user_directory`
- `ldap/role_mapping`

## access.auth.kerberos

Runs:

- `kerberos/`

## access.auth.jwt

Runs:

- `jwt_authentication/`

## access.auth.oauth

Runs:

- `oauth/`

## access.auth.multiple

Runs:

- `rbac/tests/multiple_auth_methods`

## access.tls

Runs:

- `ssl_server/`
- `ssl_keeper/`
- `clickhouse_keeper/tests/ports_ssl_fips`

## access.encryption

Runs:

- `aes_encryption/`

## backup.backup_restore

Runs:

- `s3/tests/backup.py`
- `lightweight_delete/tests/backup`

## backup.freeze

Runs:

- `tiered_storage/tests/freeze`

## interfaces.clients

Runs:

- `lts/clickhouse_odbc`
- `lts/clickhouse_jdbc`
- `lts/clickhouse_driver`
- `lts/clickhouse_sqlalchemy`
- `lts/superset`
- `lts/grafana`
- `lts/dbeaver`
- `lts/dbeaver_ui`

## ops.system_tables

Runs:

- `part_moves_between_shards/tests/system_table`
- `tiered_storage/tests/system_tables`
- system-table checks inside `s3/tests/export_part` and `s3/tests/export_partition`

## ops.deduplication

Runs:

- `part_moves_between_shards/tests/deduplication`

## ops.background

Runs:

- `tiered_storage/tests/background_move`
- `alter/stress/`

## ops.crash_recovery

Runs:

- `atomic_insert/tests/hard_restart`
- `lightweight_delete/tests/hard_restart`

Restart cases inside `kafka/` and `clickhouse_keeper/tests/servers_start_up` cover those features, not general crash recovery.

## runtime.common

Runs:

- `memory/tests/test_memory_leak`

This is not the broad profile. A change whose only leaf is `runtime.common` still has no suite list.

## runtime.dns

Runs:

- `dns/`

## No regression coverage

`query.parser`, `query.analyzer`, `query.planner`, `query.joins`, `query.subqueries`, `query.views`, `query.views.materialized`, `query.views.live`, `query.views.refreshable`, `query.parallel_replicas`, `types.core`, `types.geo`, `types.domain`, `engines.log`, `engines.special`, `engines.dictionary`, `engines.queues`, `engines.keepermap`, `engines.rocksdb`, `engines.timeseries`, `engines.arrowflight`, `engines.ytsaurus`, `engines.mergetree.unique_key`, `engines.mergetree.parts`, `databases.replicated`, `databases.external`, `databases.lazy`, `storage.hdfs`, `storage.hudi`, `storage.paimon`, `storage.cas.gc`, `formats.row`, `formats.inference`, `formats.output`, `ddl.create`, `coordination.zookeeper`, `access.auth.password`, `dictionaries.sources`, `dictionaries.layouts`, `interfaces.native`, `interfaces.http`, `interfaces.mysql`, `interfaces.postgresql`, `interfaces.grpc`, `ops.caches`, `ops.async_insert`, `ops.metrics`, `runtime.compression`, `runtime.io`.

`version/` checks the build version string. `example/` is a template. Neither is a leaf.
