# LTS Regression Suite

Runs integration tests for third-party tools against ClickHouse LTS builds.

## Sub-suites

| Suite | Target | Type | Status |
|---|---|---|---|
| `clickhouse_odbc/` | ClickHouse ODBC driver | Driver / API | Active |
| `superset/` | Apache Superset | Web UI | Active |
| `grafana/` | Altinity clickhouse-grafana plugin | Web UI | Active |

## Quick Start

There is a single `regression.py` at the top level. There are no per-suite
`regression.py` entry points — every sub-suite is loaded by the orchestrator
via `Feature(test=load("lts.<suite>.feature", "feature"))`.

```bash
# Run all LTS suites
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:0-25.8.16.10001.altinitytest

# Run only the clickhouse-odbc suite
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/clickhouse-odbc/*"

# Run only the superset suite
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/superset/*"

# Run only the grafana suite
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/grafana/*"
```

## CLI Arguments

### Common (from `helpers/argparser.argparser`)

- `--clickhouse docker://<image>:<tag>` — ClickHouse Docker image to test
  against. The `docker://` prefix is required for the orchestrator to forward
  the image to each sub-suite.
- All other common flags from `helpers/argparser.argparser` (logging,
  `--reuse-env`, `--cicd`, etc.) are accepted but most are no-ops here.

### clickhouse-odbc

- `--odbc-release <tag>` — clickhouse-odbc driver git tag (default
  `v1.2.1.20220905`).

### superset

- `--superset-version <version>` — Apache Superset version (default `4.1.1`).
- `--clickhouse-driver {clickhouse-connect,clickhouse-sqlalchemy}` —
  ClickHouse Python driver Superset is built with (default
  `clickhouse-connect`).

### grafana

- `--grafana-version <version>` — Grafana version (default `latest`).
- `--grafana-plugin-version <version>` — Altinity clickhouse-grafana plugin
  version (default `3.4.9`).

## Test Structure

See [AGENT.md](AGENT.md) for detailed conventions on requirements, test
scenarios, steps, and requirement-to-scenario mapping.

```
lts/
├── AGENT.md
├── README.md
├── regression.py             # Single, top-level orchestrator
├── clickhouse_odbc/
│   ├── feature.py            # @TestFeature loaded by regression.py
│   ├── requirements/         # SRS-100 (.md + generated .py)
│   ├── steps/                # Reusable Given/When/Then steps
│   ├── tests/                # @TestScenario / @TestFeature modules
│   └── configs/              # Dockerfile, runner.sh, diff.patch
├── superset/
│   ├── feature.py
│   ├── requirements/         # SRS-101
│   ├── steps/                # environment.py, ui.py (Selenium + REST API)
│   ├── tests/                # connection, sql_lab, charts, dashboards
│   └── configs/              # docker-compose.yml, Dockerfile.superset, TLS certs
└── grafana/
    ├── feature.py
    ├── requirements/         # SRS-102
    ├── steps/                # environment.py, ui.py
    ├── tests/                # login, datasource_query
    └── configs/              # docker-compose.yml, provisioning/, users.xml
```

## Output

- **clickhouse-odbc**: Test results in
  `lts/clickhouse_odbc/configs/PACKAGES/test.log` (and `test_detailed.log`
  when ctest produces it).
- **superset / grafana**: TestFlows output to stdout / log file. Selenium
  screenshots are written to `lts/<suite>/screenshots/`.
