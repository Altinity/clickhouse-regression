# LTS Regression Suite

Runs integration tests for third-party tools against ClickHouse LTS builds.

## Sub-suites

| Suite | Target | Type | Status |
|---|---|---|---|
| `clickhouse_odbc/` | ClickHouse ODBC driver | Upstream tests (ctest) | Active |
| `superset/` | Apache Superset | Web UI | Active |
| `grafana/` | Altinity clickhouse-grafana plugin | Web UI | Active |
| `clickhouse_driver/` | clickhouse-driver (Python, native protocol) | Upstream tests | Active |
| `clickhouse_sqlalchemy/` | clickhouse-sqlalchemy dialect | Upstream tests | Active |
| `clickhouse_jdbc/` | clickhouse-jdbc module of clickhouse-java | Upstream tests | Active |
| `dbeaver/` | JDBC driver bundled with DBeaver CE (DBeaver itself is not run) | Smoke checks | Active |

Tableau is still tested by hand.

The runners are x86-only for now, so run LTS suites on x86 hosts. They need an
Ubuntu-based ClickHouse image; Alpine images are rejected at startup.

Superset tests one driver per run (`--clickhouse-driver`); run it once per
driver to cover both.

## Prerequisites

- An x86_64 host with Docker, and Docker Compose: the `docker compose` plugin
  or the standalone `docker-compose` that CI installs.
- The Python packages in the repository's `requirements.txt`, including
  `testflows` and `selenium`.
- Network access to GitHub, PyPI, Maven Central and Docker Hub: the runners
  clone the tools and download their dependencies and images.
- For clickhouse-jdbc, access to `/var/run/docker.sock` for your user: the
  tests start ClickHouse containers themselves.

## Quick Start

To debug a failure, see [DEBUGGING.md](DEBUGGING.md). Each suite's own rules and
known behavior are in its `AGENTS.md`, for example
[grafana/AGENTS.md](grafana/AGENTS.md).

There is a single `regression.py` at the top level. There are no per-suite
`regression.py` entry points — every sub-suite is loaded by the orchestrator
via `Feature(test=load("lts.<suite>.feature", "feature"))`.

```bash
IMAGE=docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest

# Run all LTS suites; --test-to-end keeps going after a failing suite
python3 lts/regression.py --clickhouse $IMAGE --test-to-end --log test.log

# Run one suite
python3 lts/regression.py --clickhouse $IMAGE --only "/lts/grafana/*" --log test.log

# Run Superset with the other Python driver
python3 lts/regression.py --clickhouse $IMAGE --only "/lts/superset/*" \
    --clickhouse-driver clickhouse-sqlalchemy --log test.log

# Run several suites
python3 lts/regression.py --clickhouse $IMAGE --log test.log \
    --only "/lts/clickhouse-driver/*" "/lts/clickhouse-sqlalchemy/*" \
           "/lts/clickhouse-jdbc/*" "/lts/dbeaver/*"

# Run a single clickhouse-jdbc test class
python3 lts/regression.py --clickhouse $IMAGE --only "/lts/clickhouse-jdbc/*" --log test.log \
    --jdbc-maven-args "-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest -Dsurefire.failIfNoSpecifiedTests=false -Dfailsafe.failIfNoSpecifiedTests=false"
```

The `--only` paths for the suites are `/lts/clickhouse-odbc/*`,
`/lts/superset/*`, `/lts/grafana/*`, `/lts/clickhouse-driver/*`,
`/lts/clickhouse-sqlalchemy/*`, `/lts/clickhouse-jdbc/*` and `/lts/dbeaver/*`.

Always pass `--clickhouse`. Without it the suites fall back to an old 25.8 image.

The ClickHouse version, which gates version-specific xfails and the Grafana
version check, comes from `--clickhouse-version` or from the image tag
(`0-26.3.13.10001.altinitytest` gives `26.3.13.10001`). A moving tag such as
`latest` gives no version, so version-specific xfails do not apply.

## CLI Arguments

### Common (from `helpers/argparser.argparser`)

- `--clickhouse docker://<image>:<tag>` — ClickHouse Docker image to test
  against. The `docker://` prefix is required for the orchestrator to forward
  the image to each sub-suite.
- `--clickhouse-version <version>` — overrides the version taken from the
  image tag.
- The other common flags from `helpers/argparser.argparser` are accepted but
  ignored, because the LTS suites do not use the cluster helper: `--local`,
  `--as-binary`, `--base-os`, `--keeper`, `--zookeeper-version`,
  `--use-keeper`, `--stress`, `--collect-service-logs`, `--thread-fuzzer`,
  `--with-analyzer`, `--reuse-env` and `--cicd`. Service logs are always
  collected (see Output).

### clickhouse-odbc

- `--odbc-release <tag>` — clickhouse-odbc driver git tag (default
  `v1.2.1.20220905`). The driver is compiled once per tag in a Docker build
  stage that does not depend on the ClickHouse image (about 4 minutes); later
  runs, including against new ClickHouse images, reuse it and take about
  1.5 minutes. All 28 ctest targets run, including the pyodbc `parametrized`
  datatype suite, `test.py`, `test.pl` and the `isql`/`iusql` checks.

### superset

- `--superset-version <version>` — Apache Superset version (default `4.1.1`).
- `--clickhouse-driver {clickhouse-connect,clickhouse-sqlalchemy}` —
  ClickHouse Python driver Superset is built with (default
  `clickhouse-connect`).

### grafana

- `--grafana-version <version>` — Grafana version (default `13.2.2`, the version
  the suite was validated with).
- `--grafana-plugin-version <version>` — Altinity clickhouse-grafana plugin
  version (default `3.4.9`).

### clickhouse-driver

- `--clickhouse-driver-release <tag>` — clickhouse-driver git tag (default
  `0.2.10`). Not to be confused with Superset's `--clickhouse-driver`.

### clickhouse-sqlalchemy

- `--sqlalchemy-release <tag>` — clickhouse-sqlalchemy git tag (default `0.3.2`).

### clickhouse-jdbc

- `--jdbc-release <tag>` — clickhouse-java git tag (default `v0.9.9`). v0.9.0
  fails against 26.x servers (`Magic is not correct` while decompressing
  results), on both Altinity and upstream images; v0.9.9 passes.
- `--jdbc-maven-args "<options>"` — extra options for `mvn verify`, for example
  to run one test class.

### dbeaver

- `--dbeaver-version <tag>` — DBeaver CE release tag (default `26.2.1`). The
  checks use the clickhouse-jdbc and httpclient5 versions that this DBeaver
  release's ClickHouse plugin declares.

## Test Structure

See [AGENT.md](AGENT.md) for detailed conventions on requirements, test
scenarios, steps, and requirement-to-scenario mapping.

```
lts/
├── README.md                 # This file
├── AGENT.md                  # Conventions shared by all suites
├── DEBUGGING.md              # How to debug each suite's failures
├── regression.py             # Single, top-level orchestrator
├── steps/                    # Shared: runner containers, JUnit XML reporting,
│   │                         # image parsing, Compose setup, teardown and logs
│   └── tests/                # Unit tests: python3 -m unittest discover -s lts/steps/tests -t .
│
│   # Suites that run a tool's own tests in a runner container:
├── clickhouse_odbc/          # SRS-100
├── clickhouse_driver/        # SRS-103
├── clickhouse_sqlalchemy/    # SRS-104
├── clickhouse_jdbc/          # SRS-105
├── dbeaver/                  # SRS-106
│   ├── AGENTS.md             # Rules specific to the suite
│   ├── feature.py            # Calls lts.steps.upstream.run_upstream_tests
│   ├── requirements/         # SRS (.md + generated .py)
│   └── configs/              # Dockerfile, runner.sh, and patches/, diff.patch or Smoke.java
│
│   # Browser suites (Docker Compose + Selenium):
├── superset/                 # SRS-101
│   ├── AGENTS.md
│   ├── feature.py
│   ├── requirements/
│   ├── steps/                # environment.py (Compose), ui.py (Selenium + REST API)
│   ├── tests/                # ui_smoke.py: driver, test connections, SQL Lab
│   └── configs/              # docker-compose.yml, Dockerfile.superset,
│                             # init_schema.sql, TLS config and certificates
└── grafana/                  # SRS-102
    ├── AGENTS.md
    ├── feature.py
    ├── requirements/
    ├── steps/                # environment.py (Compose), ui.py (Selenium + API)
    ├── tests/                # login, datasource_query, panel_graph
    └── configs/              # docker-compose.yml, init_schema.sql,
                              # provisioning/, users.xml
```

The layout shown for `dbeaver/` is the same for the other four runner suites.

## Output

Each suite keeps its evidence in `lts/_instances/<suite>/`, named after the
suite folder, for example `lts/_instances/clickhouse_odbc/`.

- **grafana, superset**: screenshots of every UI step in `screenshots/`, and
  the logs of every Compose service, saved before teardown, in `logs/`
  (`<service>.log`, `compose-ps.log`, `compose-down.log`).
- **clickhouse-odbc, clickhouse-driver, clickhouse-sqlalchemy,
  clickhouse-jdbc, dbeaver**: every upstream test is reported as its own
  TestFlows scenario, for example
  `/lts/clickhouse-driver/tests/columns/test_datetime/DateTimeTimezonesTestCase/test_use_client_timezone`.
  The folder holds the JUnit XML (`junit.xml`, or `reports/` for
  clickhouse-jdbc) and the runner's `logs/build.log` and `logs/test.log`, plus
  `logs/clickhouse-server.log` for the suites that run ClickHouse in the
  runner and `logs/ctest-detailed.log` for clickhouse-odbc. Each suite fails if
  fewer tests than its known count run, or if more are skipped than expected;
  the thresholds are in each `feature.py`.

[DEBUGGING.md](DEBUGGING.md#4-read-the-artifacts) lists every file per suite.

Each run of a browser suite empties its `lts/_instances/<suite>/` first, so the
folder only holds the latest run's evidence.

## CI

Run the suites from GitHub Actions with the **🧰 Run LTS** workflow
(`.github/workflows/run-lts.yml`). Choose a ClickHouse image, and `all` or one
suite; `superset` runs once per Python driver. Each suite runs as its own job,
and uploads its evidence the same way as every other regression suite:

- the TestFlows `raw.log`, `report.html` and failure summaries, and the results
  database upload;
- the suite's `lts/_instances/<suite>/` logs, JUnit XML and screenshots, both to
  the S3 report folder and as the job's GitHub artifact. For clickhouse-odbc,
  for example, the folder is `.../lts/clickhouse-odbc/` and the artifact
  `lts_clickhouse_odbc-artifacts-x86_zookeeper`. Superset's are per driver:
  `.../lts/superset/clickhouse-connect/` and
  `lts_superset_clickhouse_connect-artifacts-x86_zookeeper`.

Use **extra_args** for tool versions, for example `--jdbc-release v0.9.8`. The
runners are x86-only, so the workflow has no architecture choice. Other
workflows can call it with `workflow_call`, for example for a scheduled LTS
run.
