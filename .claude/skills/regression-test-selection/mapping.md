# Taxonomy to regression tests

Each heading is a test directory. The leaves under it are the features that directory exercises. A directory covers many leaves.

To select tests, find every directory that lists the chosen leaf. Run that directory. When a leaf names a file or a flag, run that file with that flag.

A leaf that appears in no directory has no regression test. Paths marked "not started" exist on disk and the suite does not run them.

`storage.cas` and `storage.disk.cache` are listed on every directory CI runs with `--cas` or `--cas-s3-cache`. Copy the flag and any `--only` or `--skip`. Do not add `cas/soak/`, `cas/jepsen/`, or `alter/stress/`.

## aggregate_functions/

- `functions.aggregate` — `tests/function_list.py`, `tests/run_with_extra_data`
- `types.aggregate_state` — `tests/state`, `tests/merge`
- `query.planner.windows` — `tests/window_functions`
- `query.transforms` — `tests/window_functions`
- `storage.cas` — `--cas`, one job per `--only "/aggregate functions/part 1/*"`, `part 2`, `part 3`
- `storage.disk.cache` — the same three jobs with `--cas-s3-cache`

## window_functions/

- `query.planner.windows`
- `query.transforms`

## functions/

- `functions.arithmetic` — `tests/plus.py`, `tests/math_functions`
- `functions.throwIf` — `tests/throwIf_function`
- `engines.mergetree` — `tests/merge.py` is CollapsingMergeTree, not a function
- `engines.mergetree.projections` — `tests/projection_optimization`

## base_58/

- `functions.encoding`

## key_value/

- `functions.keyvaluepair`

## session_timezone/

- `types.datetime` — `tests/sanity`, `tests/basic`
- `functions.datetime` — `tests/date_functions.py`, `tests/tables_with_date_columns.py`

## settings/

- `runtime.settings` — `tests/default_values`

## selects/

- `query.select` — `tests/final` covers the FINAL modifier
- `query.analyzer.passes` — `tests/final`
- `storage.cas` — `--cas`
- `storage.disk.cache` — `--cas-s3-cache`

## data_types/

- `types.map` — `tests/map`

## json_data_type/

- `types.json`

## datetime64_extended_range/

- `types.datetime`

## extended_precision_data_types/

- `types.decimal`

## engines/

- `engines.mergetree` — `tests/replacing_merge_tree/replacing_merge_tree.py`, `tests/summing_merge_tree/`
- `engines.mergetree.replication` — `tests/replacing_merge_tree/replicated_replacing_merge_tree.py`
- `storage.cas` — `--cas`
- `storage.disk.cache` — `--cas-s3-cache`

## lightweight_delete/

- `engines.mergetree.lightweight_delete` — `tests/acceptance.py`, `basic_checks.py`, `specific_deletes.py`, `invalid_where_clause.py`, `immediate_removal.py`, `multiple_delete_limitations.py`, `drop_empty_part.py`, `efficient_physical_data_removal.py`, `compatibility.py`, `nondeterministic_functions.py`
- `engines.mergetree.lightweight_delete` — replicated cases in `tests/replicated_tables.py`, `replicated_tables_concurrent_deletes.py`, `replicated_table_with_concurrent_alter_and_delete.py`, `replicated_table_with_alter_after_delete_on_single_node.py`, `zookeeper_load.py`
- `coordination.replication.queue` — `tests/replication_queue.py`
- `engines.mergetree.replication` — the same replicated delete tests
- `engines.mergetree.mutations` — `tests/alter_after_delete.py`, `concurrent_alter_and_delete.py`, `random_concurrent_alter.py`
- `engines.mergetree.ttl` — `tests/acceptance_column_ttl.py`, `delete_and_column_ttl.py`, `acceptance_tiered_storage_ttl.py`, `delete_and_tiered_storage_ttl.py`
- `engines.mergetree.projections` — `tests/projections.py`
- `engines.view` — `tests/views.py`
- `query.distributed` — `tests/distributed_tables.py`
- `storage.policy` — `tests/multi_disk.py`, `disk_space.py`, `lack_of_disk_space.py`
- `storage.disk.encrypted` — `tests/encrypted_disk.py`
- `storage.s3` — `tests/s3.py`
- `backup.restore` — `tests/backup.py`
- `ops.crash_recovery` — `tests/hard_restart.py`
- `storage.cas` — four jobs: `--cas --only "/lightweight delete/disk space/*"`, `--cas --only "/lightweight delete/hard restart/*"`, the `--cas --skip` of those plus alter-after-delete, concurrent alter and delete, concurrent delete, basic checks, performance, and ontime tests, and `--cas --only` of that same second group
- `storage.disk.cache` — the same four jobs with `--cas-s3-cache`

## alter/

- `ddl.partition` — `table/replace_partition`, `table/attach_partition`, `table/move_partition`
- `engines.mergetree.mutations` — `stress/`
- `ops.background` — `stress/`
- `storage.cas` — `--cas` on replace partition, attach partition parts 1–3, and move partition
- `storage.disk.cache` — the same five jobs with `--cas-s3-cache`

`alter/stress/` is not part of the `--cas` selection. It is a manual workflow.

## attach/

- `databases.atomic` — `tests/active_path`
- `ddl.attach` — `tests/active_path`
- `engines.mergetree.replication` — `tests/replica_path`

## atomic_insert/

- `ddl.insert` — `tests/sanity`, `block_fail`, `insert_settings`, `transaction`
- `query.distributed` — `tests/distributed_table`
- `ops.crash_recovery` — `tests/hard_restart`
- `storage.cas` — `--cas`
- `storage.disk.cache` — `--cas-s3-cache`

## tiered_storage/

- `storage.policy` — `tests/keep_free_space`, `round_robin`, `jbod_overflow`, `max_data_part_size`, `alter_table_policy`
- `storage.volume` — `tests/alter_move`, `background_move`, `manual_move_with_downtime`, `merge_parts_different_volumes`
- `engines.mergetree.ttl` — `tests/ttl_moves`
- `engines.mergetree.replication` — `tests/simple_replication_and_moves`
- `backup.freeze` — `tests/freeze`
- `ops.system` — `tests/system_tables`
- `ops.background` — `tests/background_move`
- `storage.cas` — `--with-cas`. There is no `--cas-s3-cache` job.

## disk_level_encryption/

- `storage.disk.encrypted` — `tests/encrypted_disk`, `memory`, `application_of_changes`, `wide_access_permission`, `no_access_rights`
- `engines.mergetree.ttl` — `tests/column_ttl`

## s3/

- `storage.s3` — `tests/sanity.py`, `combinatoric_table.py`
- `storage.s3.disk` — `tests/disk.py`, `disk_invalid.py`, `reconnect.py`, `orphans.py`, `cit.py`
- `storage.s3.table_function` — `tests/table_function.py`, `table_function_invalid.py`, `remote_s3_function.py`
- `storage.s3.settings` — `tests/settings.py`
- `storage.gcs` — GCS target of the disk and table-function tests
- `storage.azure` — Azure target of those tests
- `storage.zero_copy` — `tests/zero_copy_replication.py`
- `storage.hive_partitioning` — `tests/hive_partitioning.py`
- `backup.engine.s3` — `tests/backup.py`
- `backup.impl` — `tests/backup.py`
- `backup.entries` — `tests/backup.py`
- `backup.restore` — `tests/backup.py`
- `ddl.export_part` — `tests/export_part/`
- `ddl.export_partition` — `tests/export_partition/`
- `ops.system` — system-table checks inside `tests/export_part` and `tests/export_partition`

Not started: `tests/iam_auth.py`, `tests/ec2.py` (`storage.s3.iam`).

## iceberg/

- `lakes.iceberg` — `tests/iceberg_engine/`, `tests/icebergS3_table_function/`, `tests/iceberg_table_engine/`
- `lakes.iceberg.writes` — `tests/iceberg_engine/native_create/`, `tests/export_partition/`
- `lakes.iceberg.cache` — `tests/cache/`
- `lakes.iceberg.expire_snapshots` — `tests/export_ttl/`
- `functions.table.object_storage` — `tests/s3_table_function/`

Not started: `tests/catalogs/` (`lakes.catalog`, `lakes.catalog.rest`, `lakes.catalog.glue`, `lakes.catalog.hive`), `tests/deletion_vectors/` (`lakes.iceberg.deletion_vectors`, `lakes.delta`), `tests/hybrid/` (`engines.hybrid`).

## ice/

- `lakes.iceberg` — the Ice CLI

## hive_partitioning/

- `storage.hive_partitioning`

## parquet/

- `formats.parquet` — `tests/file`, `query`, `read_and_write`, `columns`, `broken`, `datatypes`, `complex_datatypes`, `int_list_multiple_chunks`, `chunked_array`, `encoding`, `compression`, `rowgroups`, `url`, `remote`, `glob`, `encrypted`, `s3`, `fastparquet`, `multi_chunk_upload`, and `performance/`
- `formats.parquet.cache` — `tests/cache`
- `engines.mysql` — `tests/mysql.py`. Not the MySQL wire protocol.
- `engines.postgresql` — `tests/postgresql.py`. Not the PostgreSQL wire protocol.

Not started: `tests/indexing`, `native_reader`, `metadata`, `data_conversion`.

## cas/

- `storage.cas` — the suite itself. The CI job passes no extra flag.
- `storage.disk.cache` — `--cas-s3-cache`

`cas/tests/alter/` is not started. Those files cover `engines.mergetree.mutations`, `engines.mergetree.ttl`, `engines.mergetree.projections`, `engines.mergetree.indexes`, and `ddl.alter_columns`.

## kafka/

- `engines.kafka` — `tests/non_replicated`, `non_replicated_4_consumers`, `non_replicated_target_table_not_writable`, `replicated_stop_and_restart`, `non_replicated_clickhouse_restart`, `non_replicated_4_consumers_restart`
- `query.distributed` — `tests/distributed`
- `ops.crash_recovery` — the restart scenarios above

## clickhouse_keeper/

- `coordination.keeper.server` — `tests/sanity`, `cli`, `synchronization`, `keeper_cluster_tests`, `cli_converter`
- `coordination.keeper.settings` — `tests/coordination_settings`
- `coordination.keeper.migration` — `tests/migration`
- `coordination.keeper.four_letter` — `tests/four_letter_word_commands`
- `ddl.on_cluster` — `tests/alter_column_distributed`
- `query.distributed` — `tests/alter_column_distributed`
- `access.tls` — `tests/ports_ssl_fips`, `fips`
- `ops.crash_recovery` — `tests/servers_start_up`

## clickhouse_keeper_failover/

- `coordination.keeper_failover`

## swarms/

- `cluster.swarm`

## rbac/

- `access.user` — `tests/syntax`
- `access.grant` — `tests/syntax`, `tests/privileges/`
- `access.row_policy` — `tests/privileges/show/show_row_policies.py`
- `access.sql_security` — `tests/sql_security`, `tests/views`
- `access.auth` — `tests/multiple_auth_methods`

## ldap/

- `access.auth.ldap` — `authentication/`, `external_user_directory/`, `role_mapping/`

## kerberos/

- `access.auth.kerberos`

## jwt_authentication/

- `access.auth.jwt`

## oauth/

- `access.auth.oauth`

## ssl_server/

- `access.tls`

## ssl_keeper/

- `access.tls`

## aes_encryption/

- `functions.encryption`

## part_moves_between_shards/

- `ddl.partition` — `tests/part_moves`, `tests/sanity`
- `ops.system` — `tests/system_table`
- `ops.deduplication` — `tests/deduplication`

## lts/

- `interfaces.clients` — `clickhouse_odbc`, `clickhouse_jdbc`, `clickhouse_driver`, `clickhouse_sqlalchemy`, `superset`, `grafana`, `dbeaver`, `dbeaver_ui`

## memory/

- `runtime.memory` — `tests/test_memory_leak`

## dns/

- `runtime.dns`

`version/` checks the build version string. `example/` is a template. Neither covers a leaf.
