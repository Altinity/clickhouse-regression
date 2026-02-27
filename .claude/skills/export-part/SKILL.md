---
name: export-part
description: Run export_part tests in the s3 test suite. Use when the user wants to run export part tests, test ALTER TABLE EXPORT PART functionality, or test exporting MergeTree parts to S3.
---

# Export Part Test Suite

Run tests for the `ALTER TABLE ... EXPORT PART` feature, which exports MergeTree parts from local tables to S3 storage.

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
/s3/minio/export tests/export part/<feature>/*
```

The `*` wildcard is required to run all scenarios under a feature.

## Available Features

| Feature | Description |
|---------|-------------|
| `sanity` | Basic functionality (settings, empty tables, wide/compact parts) |
| `error handling` | Invalid parts, disabled settings, corruption, pending mutations |
| `datatypes` | Partition key types (Int, UInt, Date, DateTime, String, etc.) |
| `columns` | ALIAS, MATERIALIZED, EPHEMERAL, DEFAULT, JSON, nested columns |
| `clusters nodes` | Multi-node exports to same S3 destination |
| `shards` | Distributed/sharded tables with Distributed engine |
| `engines volumes` | Different table engines and volume configurations |
| `network` | Packet delay, loss, corruption, MinIO/ClickHouse interruptions |
| `system monitoring` | Events, part log, duplicate policies, metrics, bandwidth |
| `concurrent alter` | ALTER operations before/during/after exports |
| `concurrent other` | INSERT, SELECT, OPTIMIZE, KILL, DELETE during exports |
| `pending mutations and patch parts` | Allowing exports with pending mutations |
| `rbac` | ALTER INSERT privilege requirements |
| `table functions` | Table function exports (explicit/inherited schema) |

## Examples

Run all column tests:

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export part/columns/*"
```

Run all sanity tests with logging:

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export part/sanity/*" -l test.log
```

Run all export part tests:

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export part/*"
```

Run a specific scenario (e.g., alias_columns under columns):

```bash
./regression.py --storage minio --clickhouse https://example.com/clickhouse.deb --only "/s3/minio/export tests/export part/columns/alias columns"
```
