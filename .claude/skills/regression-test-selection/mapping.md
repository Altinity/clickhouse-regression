# Taxonomy to regression tests

Each heading is a test directory. The entries under it are features from [taxonomy.yaml](taxonomy.yaml) that the directory exercises. An id is a child. A directory covers many children.

To select tests, find every directory that lists the chosen feature. Run that directory. When a feature names a file or a flag, run that file with that flag.

A feature that appears in no directory has no regression test. Paths marked "not started" exist on disk and the suite does not run them. Paths marked "not in the default CI split" are loaded by `regression.py` and skipped by the workflow `--only`.

`storage.cas` and `storage.disk.cache` are listed on every directory CI runs with `--cas` or `--cas-s3-cache`. Copy the flag and any `--only` or `--skip`. Do not add `cas/soak/`, `cas/jepsen/`, or `alter/stress/`. Those are manual workflows.

MinIO, AWS, and Hetzner are run targets of the same S3 tests. `storage.gcs` and `storage.azure` name the jobs that talk to those backends.

## aggregate_functions/

- `functions.aggregate` — part 1 (`tests/function_list.py` and the per-function scenarios) and part 2 (`tests/finalizeAggregation`, `tests/run_with_extra_data`)
- `functions.aggregate.combinators` — part 3, `tests/state` and `tests/merge` (`-State` and `-Merge`)
- `types.aggregate_function` — the same part 3 tests
- `query.planner.windows` — `tests/window_functions`
- `query.transforms` — `tests/window_functions`
- `storage.cas` — `--cas`, one job per `--only "/aggregate functions/part 1/*"`, `part 2`, `part 3`
- `storage.disk.cache` — the same three jobs with `--cas-s3-cache`

## window_functions/

- `query.planner.windows`
- `query.transforms`

## functions/

- `functions.arithmetic.plus` — `tests/plus.py`
- `functions.mathematical.exp` — `tests/math_functions.py`
- `functions.mathematical.log` — `tests/math_functions.py`
- `functions.mathematical.exp2` — `tests/math_functions.py`
- `functions.mathematical.int_exp2` — `tests/math_functions.py`
- `functions.mathematical.log2` — `tests/math_functions.py`
- `functions.mathematical.exp10` — `tests/math_functions.py`
- `functions.mathematical.int_exp10` — `tests/math_functions.py`
- `functions.mathematical.log10` — `tests/math_functions.py`
- `functions.mathematical.sqrt` — `tests/math_functions.py`
- `functions.mathematical.cbrt` — `tests/math_functions.py`
- `functions.mathematical.erf` — `tests/math_functions.py`
- `functions.mathematical.erfc` — `tests/math_functions.py`
- `functions.mathematical.lgamma` — `tests/math_functions.py`
- `functions.mathematical.tgamma` — `tests/math_functions.py`
- `functions.mathematical.sin` — `tests/math_functions.py`
- `functions.mathematical.cos` — `tests/math_functions.py`
- `functions.mathematical.tan` — `tests/math_functions.py`
- `functions.mathematical.asin` — `tests/math_functions.py`
- `functions.mathematical.acos` — `tests/math_functions.py`
- `functions.mathematical.atan` — `tests/math_functions.py`
- `functions.mathematical.cosh` — `tests/math_functions.py`
- `functions.mathematical.acosh` — `tests/math_functions.py`
- `functions.mathematical.sinh` — `tests/math_functions.py`
- `functions.mathematical.asinh` — `tests/math_functions.py`
- `functions.mathematical.tanh` — `tests/math_functions.py`
- `functions.mathematical.atanh` — `tests/math_functions.py`
- `functions.mathematical.log1p` — `tests/math_functions.py`
- `functions.mathematical.sign` — `tests/math_functions.py`
- `functions.mathematical.sigmoid` — `tests/math_functions.py`
- `functions.mathematical.degrees` — `tests/math_functions.py`
- `functions.mathematical.radians` — `tests/math_functions.py`
- `functions.other.throw_if` — `tests/throwIf_function`
- `engines.mergetree` — `tests/merge.py` is CollapsingMergeTree
- `engines.mergetree.replication` — `tests/insert.py` (ReplicatedMergeTree and ReplicatedSummingMergeTree)
- `engines.mergetree.ttl` — `tests/insert.py`
- `engines.mergetree.projections` — `tests/projection_optimization`

## base_58/

- `functions.string.base58_encode`
- `functions.string.base58_decode`

## key_value/

- `functions.keyvaluepair`

## session_timezone/

- `types.datetime` — `tests/sanity`, `tests/basic`, `tests/clickhouse_local`, `tests/tables_with_date_columns.py`
- `functions.type_conversion.to_date` — `tests/date_functions.py`
- `functions.type_conversion.to_date32` — `tests/date_functions.py`
- `functions.type_conversion.to_date_time` — `tests/date_functions.py`
- `functions.type_conversion.to_date_time32` — `tests/date_functions.py`
- `functions.type_conversion.to_date_time64` — `tests/date_functions.py`

## settings/

- `runtime.settings` — `tests/default_values`

## selects/

- `query.plan` — `tests/final`. FINAL is applied in `ReadFromMergeTree`. `tests/final/modifier.py` is an xfail and does not run.
- `engines.mergetree` — `tests/final/force`
- `engines.alias` — `tests/final/force/alias`
- `access.grant` — `tests/final/force/user_rights`
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

- `engines.mergetree.lightweight_delete` — `tests/acceptance.py`, `basic_checks.py`, `specific_deletes.py`, `invalid_where_clause.py`, `immediate_removal.py`, `multiple_delete_limitations.py`, `drop_empty_part.py`, `efficient_physical_data_removal.py`, `compatibility.py`, `nondeterministic_functions.py`, `ontime_tests.py`, `performance.py`, `load.py`, `hard_restart.py`, and the replicated files below
- `engines.mergetree.replication` — `tests/replicated_tables.py`, `replicated_tables_concurrent_deletes.py`, `replicated_table_with_concurrent_alter_and_delete.py`, `replicated_table_with_alter_after_delete_on_single_node.py`, `zookeeper_load.py`
- `coordination.replication.queue` — `tests/replication_queue.py`
- `engines.mergetree.mutations` — `tests/alter_after_delete.py`, `concurrent_alter_and_delete.py`, `random_concurrent_alter.py`
- `engines.mergetree.ttl` — `tests/acceptance_column_ttl.py`, `delete_and_column_ttl.py`, `acceptance_tiered_storage_ttl.py`, `delete_and_tiered_storage_ttl.py`
- `engines.mergetree.projections` — `tests/projections.py`
- `engines.view` — normal views in `tests/views.py`
- `engines.view.materialized` — materialized views in `tests/views.py`
- `engines.view.window` — window views in `tests/views.py`. The live view scenario has no child.
- `engines.distributed` — `tests/distributed_tables.py`
- `storage.policy` — `tests/multi_disk.py`, `disk_space.py`, `lack_of_disk_space.py`
- `storage.disk.encrypted` — `tests/encrypted_disk.py`
- `storage.s3` — `tests/s3.py`
- `backup.statement` — `tests/backup.py`
- `backup.restore` — `tests/backup.py`
- `storage.cas` — four jobs: `--cas --only "/lightweight delete/disk space/*"`, `--cas --only "/lightweight delete/hard restart/*"`, `--cas --skip` of disk space, hard restart, alter after delete, concurrent alter and delete, concurrent delete, basic checks, performance, and ontime tests, and `--cas --only` of that same skipped group
- `storage.disk.cache` — the same four jobs with `--cas-s3-cache`

## alter/

- `ddl.partition` — `table/replace_partition`, `table/attach_partition`, `table/move_partition`
- `storage.cas` — `--cas` on replace partition, attach partition parts 1–3, and move partition
- `storage.disk.cache` — the same five jobs with `--cas-s3-cache`

`alter/stress/` covers `engines.mergetree.mutations` and `ops.background`. It is a manual workflow. Do not select it with `--cas`.

## attach/

- `databases.atomic` — `tests/active_path`
- `ddl.attach` — `tests/active_path`
- `engines.mergetree.replication` — `tests/replica_path`

## atomic_insert/

- `ddl.insert` — `tests/sanity`, `block_fail`, `insert_settings`, `dependent_tables`, `transaction`, `hard_restart`
- `engines.view.materialized` — `tests/dependent_tables`
- `query.transactions` — `tests/transaction`
- `query.distributed` — `tests/distributed_table`
- `access.grant` — `tests/user_rights`
- `storage.cas` — `--cas`
- `storage.disk.cache` — `--cas-s3-cache`

## tiered_storage/

- `storage.policy` — `tests/keep_free_space`, `round_robin`, `jbod_overflow`, `max_data_part_size`, `alter_table_policy`, `startup_and_queries`, `metadata`, `query_parser`, `no_changes_to_queries`
- `storage.volume` — `tests/alter_move`, `background_move`, `manual_move_with_downtime`, `merge_parts_different_volumes`, `merge_parts_different_volumes_no_space`, `volume_config_either_max_data_part_size_bytes_or_ratio`
- `storage.disk.object_storage` — the `--with-minio`, `--with-s3amazon`, and `--with-s3hetzner` jobs
- `storage.s3` — those same three jobs
- `storage.gcs` — the `--with-s3gcs` job
- `engines.mergetree.ttl` — `tests/ttl_moves`
- `engines.mergetree.replication` — `tests/simple_replication_and_moves`, `download_appropriate_disk`, `download_appropriate_disk_advanced`, `download_appropriate_disk_max_data_part_size`
- `engines.mergetree.mutations` — `tests/mutate_to_another_disk`
- `ddl.partition` — `tests/attach_or_replace_partition_different_policies`
- `ddl.rename` — `tests/rename`
- `backup.freeze` — `tests/freeze`
- `ops.system.parts` — `tests/system_tables`, `system_detached_parts`
- `ops.background` — `tests/background_move`, `start_stop_moves`
- `storage.cas` — `--with-cas`. There is no `--cas-s3-cache` job.

## disk_level_encryption/

- `storage.disk.encrypted` — the suite
- `engines.mergetree.ttl` — `tests/column_ttl`
- `engines.distributed` — `tests/distributed_table`
- `engines.mergetree.replication` — `tests/replicated_table`
- `storage.policy` — `tests/multi_volume_policy`
- `storage.volume` — `tests/multi_disk_volume`

## s3/

- `storage.s3` — `tests/sanity.py`, `combinatoric_table.py`, `settings.py`, `reconnect.py`, `orphans.py`, `cit.py`, `hive_partitioning.py`
- `storage.disk.object_storage` — `tests/disk.py`, `disk_invalid.py`, `reconnect.py`, `orphans.py`, `cit.py`
- `engines.object_storage` — `tests/sanity.py`, `combinatoric_table.py`, `hive_partitioning.py`
- `functions.table.object_storage` — `tests/table_function.py`, `table_function_invalid.py`, `table_function_performance.py`, `remote_s3_function.py`
- `storage.gcs` — the GCS job of the disk, table-function, backup, and alter tests
- `storage.azure` — the Azure job of those tests
- `storage.zero_copy` — `tests/zero_copy_replication.py`
- `ddl.alter` — `tests/alter.py`
- `ddl.alter_columns` — `tests/alter.py`
- `ddl.partition` — detach, drop, move, fetch, attach, replace, and freeze in `tests/alter.py`
- `ddl.create.index` — index clauses in `tests/alter.py`
- `engines.mergetree.indexes` — index clauses in `tests/alter.py`
- `engines.mergetree.projections` — projection clauses in `tests/alter.py`
- `engines.mergetree.mutations` — `ALTER UPDATE` and `ALTER DELETE` in `tests/alter.py`
- `backup.freeze` — `FREEZE` in `tests/alter.py`
- `backup.statement` — `tests/backup.py`
- `backup.engine.s3` — `tests/backup.py` on MinIO, AWS, and Hetzner
- `backup.engine.azure` — `tests/backup.py` on Azure
- `backup.restore` — `tests/backup.py`
- `ddl.export_part` — `tests/export_part/`
- `ddl.export_partition` — `tests/export_partition/`
- `ops.system.parts` — system-table checks inside `tests/export_part` and `tests/export_partition`

Not started: `tests/iam_auth.py`, `tests/ec2.py` (`storage.s3.auth`).

`tests/hive_partitioning.py` and `hive_partitioning/` also exercise Hive-style paths. `src/Storages/HivePartitioningUtils.cpp` is the parent `engines` and has no child, so a change that matches only that parent does not select these tests.

## iceberg/

Default CI runs two jobs:

- `--only "/iceberg/iceberg engine/rest catalog/*" "/iceberg/s3 table function/*" "/iceberg/icebergS3 table function/*" "/iceberg/iceberg cache/*"`
- `--only "/iceberg/iceberg engine/glue catalog/*" "/iceberg/iceberg table engine/*" "/iceberg/export partition/*"`

- `lakes.catalog` — `tests/iceberg_engine/`
- `lakes.catalog.rest` — the rest catalog half of `tests/iceberg_engine/`
- `lakes.catalog.glue` — the glue catalog half of `tests/iceberg_engine/`
- `lakes.iceberg` — `tests/iceberg_engine/`, `tests/iceberg_table_engine/`, `tests/icebergS3_table_function/`
- `lakes.iceberg.schema` — `schema_evolution`, `partition_evolution`, `nested_datatypes`, `check_datatypes`, `dot_separated_column_names` inside `tests/iceberg_engine/`
- `lakes.iceberg.writes` — `overwrite` inside `tests/iceberg_engine/`, `tests/export_partition/`, and `tests/iceberg_engine/native_create/`
- `lakes.iceberg.deletion_vectors` — `equality_deletes` and `position_delete_reads` inside `tests/iceberg_engine/`
- `lakes.iceberg.cache` — `tests/cache/`
- `functions.table.object_storage` — `tests/s3_table_function/`, `tests/icebergS3_table_function/`
- `ddl.export_partition` — `tests/export_partition/`
- `access.grant` — `rbac` and `column_rbac` inside `tests/iceberg_engine/`
- `access.row_policy` — `row_policy` inside `tests/iceberg_engine/`
- `query.distributed` — `swarm_examples` inside `tests/iceberg_engine/`
- `lakes.iceberg.expire_snapshots` — `tests/export_ttl/`. Not in the default CI split.
- `lakes.catalog.auth` — `tests/iceberg_engine/token_forwarding/`. Not in the default CI split. It also hits `lakes.catalog.rest` and `lakes.catalog.glue`.

`tests/iceberg_engine/native_create/` is not in the default CI split.

Not started: `tests/catalogs/` (`lakes.catalog` beyond the engine tests above, including `lakes.catalog.hive`), `tests/deletion_vectors/` (`lakes.delta` as well as `lakes.iceberg.deletion_vectors`), `tests/hybrid/` (`engines.hybrid`), `row_lineage`, `timestamp_ns_pruning`, `alter_support`, `cluster_join_filter`.

## ice/

- `lakes.iceberg` — the Ice CLI

## hive_partitioning/

- `storage.s3`
- `engines.object_storage`
- `functions.table.object_storage` — writes through the S3 table engine and the `s3` table function

Hive partitioning itself has no child. See the note under `s3/`.

## parquet/

- `formats.parquet` — `tests/file`, `query`, `read_and_write`, `columns`, `broken`, `datatypes`, `complex_datatypes`, `int_list_multiple_chunks`, `chunked_array`, `encoding`, `compression`, `rowgroups`, `url`, `remote`, `glob`, `encrypted`, `fastparquet`, `multi_chunk_upload`, and `performance/`
- `formats.parquet.cache` — `tests/cache`
- `formats.parquet.v3` — the same started tests with `--native-parquet-reader-v3`. Scheduled runs turn this on. A pull request does not, unless the workflow input `parquet_native_v3` is set.
- `engines.mysql` — `tests/mysql.py`. This is the MySQL table engine, not the MySQL wire protocol.
- `engines.postgresql` — `tests/postgresql.py`. This is the PostgreSQL table engine, not the PostgreSQL wire protocol.
- `storage.s3` — `tests/s3` on the MinIO, AWS, and Hetzner jobs

Not started: `tests/indexing`, `native_reader`, `metadata`, `data_conversion`.

## cas/

- `storage.cas` — `tests/ref_collision.py` and `tests/export.py`. The CI job passes no extra flag.
- `storage.disk.cache` — `--cas-s3-cache`
- `ddl.export_partition` — `tests/export.py`
- `lakes.iceberg.writes` — `tests/export.py`

Not started: `cas/tests/alter/`. Those files cover `engines.mergetree.mutations`, `engines.mergetree.ttl`, `engines.mergetree.projections`, `engines.mergetree.indexes`, `ddl.alter_columns`, `ddl.alter`, and `ddl.create.index`.

## kafka/

- `engines.kafka` — `tests/non_replicated`, `non_replicated_4_consumers`, `non_replicated_target_table_not_writable`, `replicated_stop_and_restart`, `non_replicated_clickhouse_restart`, `non_replicated_4_consumers_restart`
- `query.distributed` — `tests/distributed`

## clickhouse_keeper/

- `coordination.keeper.server` — `tests/sanity`, `synchronization`, `keeper_cluster_tests`, `servers_start_up`
- `coordination.keeper_cli` — `tests/cli`, `cli_converter`
- `coordination.keeper.settings` — `tests/coordination_settings`
- `coordination.keeper.migration` — `tests/migration`
- `coordination.keeper.four_letter` — `tests/four_letter_word_commands`
- `coordination.replication` — `tests/non_distributed_ddl_queries`
- `ddl.rename` — `tests/non_distributed_ddl_queries`
- `ddl.on_cluster` — `tests/alter_column_distributed`, `alter_partition_distributed`
- `ddl.alter_columns` — `tests/alter_column_distributed`
- `ddl.partition` — `tests/alter_partition_distributed`
- `access.tls` — `tests/ports_ssl_fips`, `fips`, and the `--ssl` jobs

## clickhouse_keeper_failover/

- `coordination.keeper_failover`

## swarms/

- `query.distributed` — swarm dispatch lives in `src/Interpreters/ClusterProxy/`
- `functions.table.object_storage` — `icebergS3` and `icebergS3Cluster`
- `lakes.iceberg` — the Iceberg reads in the swarm scenarios
- `query.joins` — `tests/joins`, `tests/swarm_join_sanity`

Not started: `tests/swarm_iceberg_partition_pruning`, `performance`, `schema_evolution`.

The swarm on/off flag in `src/Interpreters/Context.cpp` is the parent `query` and has no child. `src/Storages/IStorageCluster.cpp` is the parent `engines` and has no child. A change that matches only one of those parents does not select this directory.

## rbac/

CI splits the suite into part 1 (syntax, privileges, views), part 2 (`sql_security`), and part 3 (`multiple_auth_methods`).

- `access.user` — `tests/syntax/create_user`, `alter_user`, `drop_user`, `show_create_user`; `tests/privileges/create/create_user.py`, `alter/alter_user.py`, `drop/drop_user.py`, `show/show_users.py`
- `access.role` — `tests/syntax/create_role`, `alter_role`, `drop_role`, `show_create_role`, `grant_role`, `revoke_role`, `set_role`, `set_default_role`; `tests/privileges/create/create_role.py`, `alter/alter_role.py`, `drop/drop_role.py`, `show/show_roles.py`, `role_admin.py`, `orphaned_role.py`, `all_role.py`
- `access.grant` — `tests/syntax/grant_privilege`, `revoke_privilege`, `show_grants`; `tests/privileges/`
- `access.row_policy` — `tests/syntax/create_row_policy`, `alter_row_policy`, `drop_row_policy`, `show_create_row_policy`, `show_row_policies`; `tests/privileges/row_policy.py`, `create/create_row_policy.py`, `alter/alter_row_policy.py`, `drop/drop_row_policy.py`, `show/show_row_policies.py`
- `access.quota` — `tests/syntax/create_quota`, `alter_quota`, `drop_quota`, `show_create_quota`, `show_quotas`; `tests/privileges/create/create_quota.py`, `alter/alter_quota.py`, `drop/drop_quota.py`, `show/show_quotas.py`
- `access.settings_profile` — `tests/syntax/create_settings_profile`, `alter_settings_profile`, `drop_settings_profile`, `show_create_settings_profile`; `tests/privileges/create/create_settings_profile.py`, `alter/alter_settings_profile.py`, `drop/drop_settings_profile.py`, `show/show_settings_profiles.py`
- `access.sql_security` — `tests/sql_security`, `tests/views`
- `engines.view.materialized` — `tests/views/materialized_view.py`
- `access.auth` — `tests/multiple_auth_methods`

## ldap/

- `access.auth.ldap` — `authentication/`, `external_user_directory/`, `role_mapping/`
- `access.role` — `role_mapping/`

## kerberos/

- `access.auth.kerberos`

## jwt_authentication/

- `access.auth.jwt`

## oauth/

- `access.auth.oauth`

## ssl_server/

CI splits the suite into parts 1, 2, and 3.

- `access.tls` — the suite
- `functions.table.url` — `tests/url_table_function` (part 1)
- `dictionaries.source.http` — `tests/dictionary` (part 2)
- `coordination.zookeeper` — `tests/zookeeper` (part 3)

## ssl_keeper/

- `access.tls` — `tests/sanity`, `tests/fips_ssl_140_3`

No workflow job starts this directory.

## aes_encryption/

- `functions.encryption.encrypt`
- `functions.encryption.decrypt`
- `functions.encryption.try_decrypt`
- `functions.encryption.aes_encrypt_mysql`
- `functions.encryption.aes_decrypt_mysql`

## part_moves_between_shards/

- `ddl.partition` — `tests/part_moves`, `tests/sanity`, `tests/deduplication`
- `ops.system.parts` — `tests/system_table`

## lts/

- `interfaces.clients` — `clickhouse_odbc`, `clickhouse_jdbc`, `clickhouse_driver`, `clickhouse_sqlalchemy`, `superset`, `grafana`, `dbeaver`, `dbeaver_ui`

## memory/

- `runtime.memory` — `tests/test_memory_leak`

## dns/

- `runtime.dns`

## Not a feature selection

`ontime_benchmark/` is a query benchmark against object storage. Do not select it for a feature.

`version/` checks the build version string. `example/` is a template. Neither covers a feature.

`integration/` is not a suite job in the regression workflow.
