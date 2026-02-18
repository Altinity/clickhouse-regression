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
├── AGENT.md                  # This file — conventions & guidelines
├── README.md                 # Quick-start documentation
├── __init__.py
├── regression.py             # Single entry point — loads all sub-suite features
│
├── clickhouse_odbc/          # ODBC driver tests
│   ├── __init__.py
│   ├── feature.py            # @TestFeature loaded by regression.py
│   ├── configs/              # Dockerfile, runner.sh, diff.patch
│   ├── requirements/
│   │   ├── requirements.md   # Human-readable SRS document
│   │   └── requirements.py   # Auto-generated TestFlows Requirement objects
│   ├── steps/
│   │   └── docker.py         # Given/When/Then steps for Docker operations
│   └── tests/
│       └── build_and_run.py  # @TestFeature with build/run/verify scenarios
│
├── superset/                 # Apache Superset integration tests
│   ├── __init__.py
│   ├── feature.py            # @TestFeature loaded by regression.py
│   ├── configs/              # Dockerfiles, bootstrap scripts, TLS certs
│   ├── requirements/
│   │   ├── requirements.md
│   │   └── requirements.py
│   ├── steps/
│   │   ├── environment.py    # Docker Compose setup/teardown
│   │   └── ui.py             # Selenium-based UI interaction steps
│   └── tests/
│       ├── connection.py     # Database connection scenarios
│       ├── sql_lab.py        # SQL Lab query/schema scenarios
│       ├── charts.py         # Chart creation scenarios
│       └── dashboards.py     # Dashboard creation/refresh scenarios
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
    odbc_release=odbc_release,
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
from lts.clickhouse_odbc.steps.docker import ...
from lts.superset.requirements.requirements import ...
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
@Requirements(RQ_SRS_100_ODBC_DriverBuild("1.0"))
def build_odbc_runner(self):
    """Build the ODBC runner Docker image."""
    ...
```

### 3. Steps

Reusable **Given / When / Then** step functions go in `steps/`. Steps are shared
across multiple scenarios within the same sub-suite.

### 4. Tests

Test files live in `tests/` and each expose a `@TestFeature` named `feature`
that groups related `@TestScenario` functions.

## CLI Arguments

| Argument | Default | Description |
|---|---|---|
| `--clickhouse docker://<image>` | altinityinfra/clickhouse-server:... | ClickHouse image to test |
| `--odbc-release <tag>` | v1.2.1.20220905 | clickhouse-odbc git tag |
| `--superset-version <ver>` | 4.1.1 | Apache Superset version |
| `--clickhouse-driver <name>` | clickhouse-connect | Superset ClickHouse driver |
| `--grafana-version <ver>` | latest | Grafana version |
| `--grafana-plugin-version <ver>` | 3.4.9 | Altinity clickhouse-grafana plugin version |

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
   `requirements/`, `steps/`, `tests/`
2. Write the SRS in `requirements/requirements.md` and generate
   `requirements.py` via `tfs requirements generate`
3. Implement `feature.py` as a `@TestFeature` that loads test modules
4. Add `Feature(test=load("lts.<new_suite>.feature", "feature"))(...)`
   to `lts/regression.py`
5. Add any new CLI arguments to `lts_argparser` in `regression.py`
