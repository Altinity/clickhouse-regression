---
name: cicd-trigger
description: Trigger GitHub Actions workflows for ClickHouse regression tests. Use when the user wants to run CI/CD tests, trigger regression workflows, or check running workflow status.
---

# CI/CD Trigger

Trigger GitHub Actions workflows for running ClickHouse regression tests on x86 or ARM architectures.

## Working Directory

Run from the repository root:

```
cd clickhouse-regression
```

## Prerequisites

The user must have a GitHub personal access token with workflow scope. Set it via environment variable or pass explicitly:

```bash
export GITHUB_TOKEN="ghp_your_token"
```

## Command Format

```bash
python3 cicd-trigger.py [options]
```

## Required Options

- `--token <token>` - GitHub personal access token (or set `GITHUB_TOKEN` env variable)

## Common Options

| Option                | Description                                        | Default                                                           |
|-----------------------|----------------------------------------------------|-------------------------------------------------------------------|
| `--arch`              | Architecture: `x86` or `arm64`                     | `x86`                                                             |
| `--branch`            | Branch to run tests on                             | `main`                                                            |
| `--package`           | ClickHouse package URL (`docker://` or `https://`) | `docker://altinity/clickhouse-server:25.3.8.10042.altinitystable` |
| `--version`           | Expected ClickHouse version                        | `25.3.8.10042.altinitystable`                                     |
| `--flags`             | Test flags (see below)                             | `none`                                                            |
| `-s, --suite`         | Test suite to run (see below)                      | `all`                                                             |
| `-o, --output-format` | Output style: `classic`, `nice`, `fails`, etc.     | `classic`                                                         |
| `--ref`               | Commit SHA to checkout                             | Current branch                                                    |
| `--extra-args`        | Extra test program arguments                       | None                                                              |
| `--custom-run-name`   | Custom workflow run name                           | None                                                              |
| `--wait`              | Wait for workflow to finish                        | `False`                                                           |
| `--debug`             | Enable debug output                                | `False`                                                           |
| `--list-running`      | List running workflows and exit                    | `False`                                                           |

## Available Flags

- `none` - No special flags
- `--use-keeper` - Use ClickHouse Keeper
- `--with-analyzer` - Use new query analyzer
- `--use-keeper --with-analyzer` - Both Keeper and analyzer
- `--as-binary` - Run as binary
- `--thread-fuzzer` - Enable thread fuzzer
- Combinations of the above

## Available Test Suites

**Full regression:**
`all`, `all_aws`, `all_gcs`

**Core suites:**
`aes_encryption`, `aggregate_functions`, `atomic_insert`, `attach`, `base_58`, `data_types`, `datetime64_extended_range`, `disk_level_encryption`, `dns`, `engines`, `example`, `extended_precision_data_types`, `functions`, `lightweight_delete`, `memory`, `selects`, `session_timezone`, `settings`, `version`, `window_functions`

**Alter operations:**
`alter_all`, `alter_replace_partition`, `alter_attach_partition`, `alter_move_partition`

**Authentication/Security:**
`jwt_authentication`, `kerberos`, `ldap`, `oauth`, `rbac`, `ssl_server`

**ClickHouse Keeper:**
`clickhouse_keeper`, `clickhouse_keeper_failover`

**S3/Cloud storage:**
`s3_all`, `s3_aws`, `s3_azure`, `s3_gcs`, `s3_minio`, `export_part`, `export_partition`

**Tiered storage:**
`tiered_storage_all`, `tiered_storage_aws`, `tiered_storage_gcs`, `tiered_storage_local`, `tiered_storage_minio`

**Parquet:**
`parquet_all`, `parquet`, `parquet_minio`, `parquet_s3`, `parquet_native_v3`, `parquet_minio_native_v3`, `parquet_s3_native_v3`

**Benchmarks:**
`benchmark_all`, `benchmark_aws`, `benchmark_gcs`, `benchmark_minio`

**Other:**
`iceberg`, `kafka`, `key_value`, `part_moves_between_shards`, `swarms`, `hive_partitioning`

## Examples

Run the example test suite on x86:

```bash
python3 cicd-trigger.py --suite example
```

Run on ARM architecture:

```bash
python3 cicd-trigger.py --suite example --arch arm64
```

Run with ClickHouse Keeper enabled:

```bash
python3 cicd-trigger.py --suite s3_minio --flags "--use-keeper"
```

Run a specific ClickHouse version:

```bash
python3 cicd-trigger.py --suite example \
    --package docker://altinity/clickhouse-server:24.8.6.70.altinitystable \
    --version 24.8.6.70.altinitystable
```

Run on a feature branch and wait for completion:

```bash
python3 cicd-trigger.py --suite example --branch my-feature-branch --wait
```

Debug mode for troubleshooting:

```bash
python3 cicd-trigger.py --suite example --debug
```

List currently running workflows:

```bash
python3 cicd-trigger.py --list-running
```

Run with custom name:

```bash
python3 cicd-trigger.py --suite all --custom-run-name "Nightly regression"
```

Run specific tests with extra arguments:

```bash
python3 cicd-trigger.py --suite rbac --extra-args "--only '/rbac/views/*'"
```

Use explicit token:

```bash
python3 cicd-trigger.py --suite example --token "ghp_your_token"
```

## Output

On success, the script displays:
- Workflow trigger confirmation
- Link to GitHub Actions page
- Link to where logs will be uploaded after completion

## Notes

- The workflow runs on GitHub Actions self-hosted runners
- Logs are uploaded to `altinity-internal-test-reports` S3 bucket
- Use `--wait` to block until the workflow completes
- Use `--list-running` to check workflow status before triggering new runs
