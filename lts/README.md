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

# Run the upstream test suites of the client drivers, and the DBeaver checks
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
    --only "/lts/clickhouse-driver/*" "/lts/clickhouse-sqlalchemy/*" \
           "/lts/clickhouse-jdbc/*" "/lts/dbeaver/*"

# Run a single clickhouse-jdbc test class
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
    --only "/lts/clickhouse-jdbc/*" \
    --jdbc-maven-args "-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest -Dsurefire.failIfNoSpecifiedTests=false -Dfailsafe.failIfNoSpecifiedTests=false"
```

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
  results), on both Altinity and upstream images; later 0.9.x releases work.
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
├── AGENT.md
├── README.md
├── regression.py             # Single, top-level orchestrator
├── clickhouse_odbc/
│   ├── feature.py            # Calls lts.steps.upstream.run_upstream_tests
│   ├── requirements/         # SRS-100 (.md + generated .py)
│   └── configs/              # Dockerfile (cached build stage), runner.sh, diff.patch
├── superset/
│   ├── feature.py
│   ├── requirements/         # SRS-101
│   ├── steps/                # environment.py, ui.py (Selenium + REST API)
│   ├── tests/                # ui_smoke.py: driver, test connections, SQL Lab
│   └── configs/              # docker-compose.yml, Dockerfile.superset, TLS certs
├── grafana/
│   ├── feature.py
│   ├── requirements/         # SRS-102
│   ├── steps/                # environment.py, ui.py
│   ├── tests/                # login, datasource_query, panel_graph
│   └── configs/              # docker-compose.yml, provisioning/, users.xml
├── steps/                    # Shared: runner containers, JUnit XML reporting,
│   │                         # image parsing, Compose log capture
│   └── tests/                # Unit tests: python3 -m unittest discover -s lts/steps/tests -t .
├── clickhouse_driver/        # SRS-103
├── clickhouse_sqlalchemy/    # SRS-104
├── clickhouse_jdbc/          # SRS-105
└── dbeaver/                  # SRS-106
    ├── feature.py            # Calls lts.steps.upstream.run_upstream_tests
    ├── requirements/
    └── configs/              # Dockerfile, runner.sh, patches/ or Smoke.java
```

## Output

- **superset / grafana**: TestFlows output to stdout / log file. Selenium
  screenshots are written to `lts/<suite>/screenshots/`. Before teardown the
  logs of every Compose service are saved to `lts/_instances/<suite>/logs/`
  (`<service>.log` and `compose-ps.log`).
- **clickhouse-odbc, clickhouse-driver, clickhouse-sqlalchemy, clickhouse-jdbc,
  dbeaver**: every
  upstream test is reported as its own TestFlows scenario, for example
  `/lts/clickhouse-driver/tests/columns/test_datetime/DateTimeTimezonesTestCase/test_use_client_timezone`.
  The runner's build and test output and the JUnit XML are kept in
  `lts/_instances/<suite>/` (`logs/build.log`, `logs/test.log`, `junit.xml` or
  `reports/`). Each suite fails if fewer tests than its known count run, or if
  more are skipped than expected; the thresholds are in each `feature.py`.

When the suites move to CI, the artifacts need `lts/*/screenshots/*.png` and
`lts/_instances/**/*.xml` in addition to the existing `*.log` globs.
