---
name: export-partition
description: Run export partition tests in the s3 test suite. Use when the user wants to run export partition tests, test ALTER TABLE EXPORT PARTITION ID functionality, or test exporting MergeTree partitions to S3.
---

# Export Partition Test Suite

Run tests for the `ALTER TABLE ... EXPORT PARTITION ID ... TO TABLE` feature, which exports MergeTree partitions from local or replicated tables to S3 (or other destination) storage.

## Working Directory

All commands must be run from the `s3` directory:

```
cd clickhouse-regression/s3
```

## Command Format

```bash
./regression.py --storage minio --clickhouse <URL> --only "<test-path>"
```

## Required Options

- `--clickhouse <URL>` - URL to ClickHouse package (user must provide)
- `--storage minio` - Storage backend to use
- `--only "<test-path>"` - Test path pattern (must end with `*` to run all subtests)

## Optional Options

- `-l test.log` - Save test logs to a file

## Test Path Structure

```
/s3/minio/export tests/export partition/<feature>/*
```

The `*` wildcard is required to run all scenarios under a feature.

## Available Features

| Feature | Description |
|---------|-------------|
| `sanity` | Basic functionality (export setting, mismatched columns, schema compatibility) |
| `error handling` | Invalid cases: export to self, local table, pending mutations/patch parts |
| `kill` | KILL EXPORT PARTITION and cancellation behavior |
| `clusters and nodes` | Multi-node exports to same S3 destination |
| `shards` | Distributed/sharded tables with Distributed engine |
| `engines and volumes` | Different table engines and volume configurations |
| `datatypes` | Partition key types (Int, UInt, Date, DateTime, String, etc.) |
| `network` | Packet delay, loss, corruption, MinIO/ClickHouse interruptions |
| `concurrent actions` | INSERT, SELECT, OPTIMIZE, KILL, DELETE during exports |
| `system monitoring` | system.replicated_partition_exports, part_log, events |
| `schema evolution` | Source/destination schema compatibility over time |
| `parallel export partition` | Multiple EXPORT PARTITION operations in parallel |
| `alter destination during export` | ALTER destination table during export |
| `alter source timing` | ALTER source table before/during/after export |
| `replica failover` | Export with replica failover scenarios |
| `parallel inserts and selects` | INSERT/SELECT concurrent with export |
| `settings` | EXPORT PARTITION settings and combinations |
| `lightweight delete export partition` | Export with lightweight deletes |
| `lightweight update export partition` | Export with lightweight updates |
| `corrupted partitions` | Export behavior with corrupted partition data |

## Examples

Run all sanity tests:

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export partition/sanity/*"
```

Run all export partition tests with logging:

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export partition/*" -l test.log
```

Run a specific feature (e.g., datatypes):

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export partition/datatypes/*"
```

Run a single scenario (e.g., one scenario under sanity):

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export partition/sanity/export setting"
```

## Notes

- Export partition tests require ClickHouse Antalya build (25.8+); older versions skip the suite via xfail in `s3/regression.py`.
- The suite uses `allow_experimental_export_merge_tree_part=1` (set in `s3/tests/export_partition/feature.py`).
- Test code lives under `s3/tests/export_partition/` with shared steps in `s3/tests/export_partition/steps/`.
- Requirements are defined in `s3/requirements/export_partition.py` (SRS-016 ClickHouse Export Partition to S3).
