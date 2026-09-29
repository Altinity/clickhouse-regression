# LTS Testing — Agent Guidelines

This document describes the test structure, conventions, and requirements for the
LTS (Long-Term Support) regression suites located under `lts/`.

## Folder Layout

There is a single `regression.py` at the top level that orchestrates all sub-suites.
Each sub-suite has a `feature.py` that is loaded via `Feature(test=load(...))` —
the same pattern used in `s3/` for `export_part` and `export_partition`.

Sub-suites do **not** have their own `regression.py`.

```
lts/
├── AGENTS.md                 # This file — conventions & guidelines
├── README.md                 # Quick-start documentation
├── __init__.py
├── regression.py             # Single entry point — loads all sub-suite features
│
├── clickhouse_odbc/          # ODBC driver tests (runs the driver's ctest targets)
│   ├── __init__.py
│   ├── feature.py            # Calls lts.steps.tool_tests.run_tool_tests
│   ├── configs/              # Dockerfile (cached build stage), runner.sh, diff.patch
│   └── requirements/
│       ├── requirements.md   # Human-readable SRS document
│       └── requirements.py   # Auto-generated TestFlows Requirement objects
│
├── superset/                 # Apache Superset integration tests
│   ├── __init__.py
│   ├── feature.py            # @TestFeature loaded by regression.py
│   ├── configs/              # docker-compose.yml, Dockerfile.superset, TLS certs
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile.superset
│   │   ├── config.xml
│   │   ├── default_user.xml
│   │   ├── server.crt / server.key / dhparam.pem
│   ├── requirements/
│   │   ├── requirements.md
│   │   └── requirements.py
│   ├── steps/
│   │   ├── environment.py    # Docker Compose setup/teardown + health checks
│   │   └── ui.py             # Selenium WebDriver helpers + REST seeding fixture
│   └── tests/
│       └── clickhouse_integration.py  # Driver, connections and SQL Lab checks
│                             # (login -> verify DB -> SQL Lab query, with
│                             #  screenshots saved to lts/_instances/superset/screenshots/)
│
└── grafana/                  # Altinity Grafana ClickHouse plugin tests
    ├── __init__.py
    ├── feature.py            # @TestFeature loaded by regression.py
    ├── configs/              # docker-compose.yml, provisioning, users.xml
    │   ├── docker-compose.yml
    │   ├── init_schema.sql
    │   ├── users.xml
    │   └── provisioning/datasources/clickhouse.yaml
    ├── requirements/
    │   ├── requirements.md
    │   └── requirements.py
    ├── steps/
    │   ├── environment.py    # Docker Compose setup/teardown + health checks
    │   └── ui.py             # Selenium-based UI interaction steps
    └── tests/
        └── login.py          # Grafana login scenario
```

## How It Works

### regression.py (the only entry point)

`lts/regression.py` resolves the ClickHouse Docker image from `--clickhouse`,
sets `self.context.clickhouse_image`, and loads each sub-suite feature:

```python
Feature(test=load("lts.clickhouse_odbc.feature", "feature"))(
    release=odbc_release,
)
Feature(test=load("lts.superset.feature", "feature"))(
    superset_version=superset_version,
    clickhouse_driver=clickhouse_driver,
)
Feature(test=load("lts.grafana.feature", "feature"))(
    grafana_version=grafana_version,
    grafana_plugin_version=grafana_plugin_version,
)
```

### Sub-suite feature.py

Each `feature.py` is a `@TestFeature`-decorated function that:
1. Sets up suite-specific context (configs dir, parameters)
2. Loads its test features via `Feature(run=load("lts.<suite>.tests.<module>", "feature"))`

This mirrors how `s3/tests/export_part/feature.py` works.

### Import Convention

All imports use full package paths from the repo root:

```python
from lts.clickhouse_odbc.requirements.requirements import ...
from lts.superset.requirements.requirements import ...
from lts.superset.steps.ui import ...
```

## Test Structure Conventions

### 1. Requirements

Every sub-suite MUST have a `requirements/` folder containing:

- **`requirements.md`** — Human-readable SRS. Each requirement has a unique
  identifier following `RQ.SRS-<NNN>.<Product>.<Feature>`, a version, and a
  prose description.

- **`requirements.py`** — Auto-generated via `tfs requirements generate`.
  Contains `Requirement` and `Specification` objects. **Do not edit by hand.**

### 2. Requirement-to-Scenario Mapping

Every `@TestScenario` SHOULD reference its requirement(s) via `@Requirements`:

```python
@TestScenario
@Requirements(RQ_SRS_102_Grafana_Login("1.0"))
def login_with_default_credentials(self):
    """Log in to Grafana with the default credentials."""
    ...
```

### 3. Steps

Reusable **Given / When / Then** step functions go in `steps/`. Steps are shared
across multiple scenarios within the same sub-suite.

### 4. Tests

Test files live in `tests/` and each expose a `@TestFeature` named `feature`
that groups related `@TestScenario` functions.

### 5. Sub-suites that run a tool's own test suite

`clickhouse_odbc`, `clickhouse_driver`, `clickhouse_sqlalchemy`,
`clickhouse_jdbc` and `dbeaver` have no `steps/` or `tests/`. Their `feature.py` calls
`lts.steps.tool_tests.run_tool_tests`, which:

1. builds `configs/` into a runner image (`--build-arg CLICKHOUSE_IMAGE=...`
   when the runner is based on the ClickHouse image);
2. runs it with `lts/_instances/<suite>` mounted as `/results`; the runner's
   `runner.sh` writes JUnit XML there and must not fail the container when
   tests fail;
3. reports every `<testcase>` as a scenario through
   `lts.steps.junit.report_junit_results`. The dotted class name becomes
   nested features, so `tests.test_x.SomeTestCase::test_y` is reported as
   `/lts/<suite>/tests/test_x/SomeTestCase/test_y`.

Known failures of these tests go into `xfails` in `lts/regression.py` using those
paths. Do not use `.` in an `xfails` pattern for a class name: TestFlows
replaces `.` in test names with a look-alike character, which is why class
names are split into features.

Rules for runners, each of which was a real hole:

- Start ClickHouse with the image's `/entrypoint.sh`, not `clickhouse server
  --daemon`. Without `--config-file` the server ignores `/etc/clickhouse-server`
  and runs with built-in defaults, so the image's configuration is not tested.
- Install every optional dependency the tool's tests use. Without `numpy` and
  `pandas`, 108 clickhouse-driver tests were silently skipped. Every run notes
  the skip reasons; read them.
- Exit with the test tool's exit code and pass the acceptable codes as
  `ok_exit_codes` (pytest `0, 1`; Maven with `-Dmaven.test.failure.ignore` `0`).
  A crashed or interrupted tool can leave partial JUnit XML in which everything
  passed.

Patches for the Python drivers live in `configs/patches/`. `<release>.series`
lists the patches for one release in order; a release without its own series
uses its minor line's, so `0.3.2` falls back to `0.3.series`.

### 6. Test oracles

Every one of these was a real false positive in this suite:

- Assert exact values read from the result component: Grafana Explore cells
  (`[role='gridcell']`), Superset SQL Lab cells (`.virtual-table-cell`), a
  panel's data through `/api/ds/query`. Never fall back to page or editor text:
  the SQL itself contains strings such as `DE` (in `ORDER`).
- Scope UI checks to the element under test (a panel found by its title), not
  to any `table` or `canvas` on the page, and fail on a visible error alert.
- Only compare versions that are known: `self.context.clickhouse_version` is
  `None` for moving tags such as `latest`.
- Do not `skip()` a scenario that carries requirements because it does not
  apply (e.g. native protocol with clickhouse-connect): a skip marks its
  requirements unsatisfied. Do not run it, and note why.
- Scope known failures: an `xfails` entry can take a `when` condition and a
  failure-message regex, `(Fail, reason, check_clickhouse_version(">=26.3"), r"...")`.
- Keep `requirements.md` the source of truth: regenerate `requirements.py`
  with `tfs requirements generate` after every change, and list untested
  features outside the requirements rather than as requirements.
- Prove a new check can fail: run it against a deliberately broken image, for
  example a `users.d` profile with `readonly=1` or `limit=3`.

Shared helpers have unit tests: `python3 -m unittest discover -s lts/steps/tests -t .`

[DEBUGGING.md](DEBUGGING.md) explains how to debug each suite. Update it when
you change how a suite runs or where it writes its output.

Each suite folder has an `AGENTS.md` with the rules specific to that suite:
how it works, what not to change and why, how to bump the tool version, known
behavior and evidence. Read it before changing the suite, and update it when
you change what the suite does.

## CLI Arguments

| Argument | Default | Description |
|---|---|---|
| `--clickhouse docker://<image>` | altinityinfra/clickhouse-server:... | ClickHouse image to test |
| `--odbc-release <tag>` | v1.2.1.20220905 | clickhouse-odbc git tag |
| `--superset-version <ver>` | 4.1.1 | Apache Superset version |
| `--clickhouse-driver <name>` | clickhouse-connect | Superset ClickHouse driver |
| `--grafana-version <ver>` | 13.2.2 | Grafana version |
| `--grafana-plugin-version <ver>` | 3.4.9 | Altinity clickhouse-grafana plugin version |
| `--clickhouse-driver-release <tag>` | 0.2.10 | clickhouse-driver (Python) git tag |
| `--sqlalchemy-release <tag>` | 0.3.2 | clickhouse-sqlalchemy git tag |
| `--jdbc-release <tag>` | v0.9.9 | clickhouse-java git tag (clickhouse-jdbc module) |
| `--jdbc-maven-args "<opts>"` | | Extra `mvn verify` options, e.g. one test class |
| `--dbeaver-version <tag>` | 26.2.1 | DBeaver CE tag whose bundled JDBC driver is used |

## Running Tests

```bash
# Run all LTS suites
python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest

# Run only clickhouse-odbc tests
python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/clickhouse-odbc/*"

# Run only superset tests
python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/superset/*"

# Run only grafana tests
python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest \
    --only "/lts/grafana/*"
```

## Adding a New Sub-suite

1. Create `lts/<new_suite>/` with `__init__.py`, `feature.py`, `configs/`,
   `requirements/`, and `steps/` and `tests/` unless the suite only runs the
   tool's own test suite (see "Sub-suites that run a tool's own test suite")
2. Write the SRS in `requirements/requirements.md` and generate
   `requirements.py` via `tfs requirements generate`
3. Implement `feature.py` as a `@TestFeature` that loads test modules
4. Add `Feature(test=load("lts.<new_suite>.feature", "feature"))(...)`
   to `lts/regression.py`
5. Add any new CLI arguments to `lts_argparser` in `regression.py`
