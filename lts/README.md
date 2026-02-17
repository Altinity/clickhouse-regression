# LTS Regression Suite

Runs clickhouse-odbc tests against ClickHouse (e.g. LTS builds) in a Docker container.

## Quick start

```bash
python3 regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest
```

## Options

- `--clickhouse docker://<image>:<tag>` - ClickHouse Docker image to test against (default: altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest)
- `--odbc-release <tag>` - clickhouse-odbc driver version (default: v1.2.1.20220905)

## Output

Test results are written to `odbc/PACKAGES/test.log`.
