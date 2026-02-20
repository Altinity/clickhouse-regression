# LTS Regression Suite

Runs integration tests for third-party tools against ClickHouse LTS builds.

## Sub-suites

| Suite | Target | Type | Status |
|---|---|---|---|
| `clickhouse-odbc/` | ClickHouse ODBC driver | Driver / API | Active |
| `superset/` | Apache Superset | Web UI | Active |
| `grafana/` | Grafana plugin | Web UI | Planned |
| `dbeaver/` | DBeaver | Desktop UI | Planned |

## Quick Start

```bash
# Run all LTS suites
python3 regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest

# Run only clickhouse-odbc
python3 regression.py --suite clickhouse-odbc --clickhouse docker://altinityinfra/clickhouse-server:latest

# Run only superset
python3 regression.py --suite superset --clickhouse docker://altinityinfra/clickhouse-server:latest

# Run a specific sub-suite directly
python3 clickhouse-odbc/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest
python3 superset/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest
```

## Options

### Common
- `--clickhouse docker://<image>:<tag>` — ClickHouse Docker image to test against
- `--suite {all,clickhouse-odbc,superset}` — Which sub-suite to run (default: `all`)

### clickhouse-odbc
- `--odbc-release <tag>` — clickhouse-odbc driver git tag (default: `v1.2.1.20220905`)

### superset
- `--superset-version <version>` — Apache Superset version (default: `4.1.1`)
- `--clickhouse-driver {clickhouse-connect,clickhouse-sqlalchemy}` — Python driver (default: `clickhouse-connect`)

## Test Structure

See [AGENT.md](AGENT.md) for detailed conventions on requirements, test scenarios,
steps, and requirement-to-scenario mapping.

```
lts/
├── AGENT.md
├── README.md
├── regression.py              # Top-level orchestrator
├── clickhouse-odbc/
│   ├── regression.py          # ODBC suite entry point
│   ├── requirements/          # SRS requirements (.md + .py)
│   ├── steps/                 # Reusable step functions
│   ├── tests/                 # Test scenarios
│   └── configs/               # Dockerfile, runner.sh, patches
└── superset/
    ├── regression.py          # Superset suite entry point
    ├── requirements/          # SRS requirements (.md + .py)
    ├── steps/                 # Reusable step functions (env + UI)
    ├── tests/                 # Test scenarios (connection, sql_lab, charts, dashboards)
    └── configs/               # Dockerfiles, bootstrap scripts, TLS certs
```

## Output

- **clickhouse-odbc**: Test results in `clickhouse-odbc/configs/PACKAGES/test.log`
- **superset**: TestFlows output to stdout/log file
