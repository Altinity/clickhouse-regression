# LTS Testing — Agent Guidelines

This document describes the test structure, conventions, and requirements for the
LTS (Long-Term Support) regression suites located under `lts/`.

## Folder Layout

Each target product has its own sub-directory that follows the canonical TestFlows
structure used across `altinity/clickhouse-regression` and `altinity/clickhouse-grafana`.

```
lts/
├── AGENT.md              # This file — conventions & guidelines
├── README.md             # Quick-start documentation
├── regression.py         # Top-level orchestrator (runs all sub-suites)
│
├── clickhouse-odbc/      # Driver / API tests
│   ├── __init__.py
│   ├── regression.py     # Entry point for the ODBC suite
│   ├── requirements/
│   │   ├── requirements.md   # Human-readable SRS document
│   │   └── requirements.py   # Auto-generated TestFlows Requirement objects
│   ├── steps/            # Reusable step functions (Given / When / Then)
│   │   └── __init__.py
│   ├── tests/            # Test scenarios
│   │   └── __init__.py
│   ├── configs/          # Infrastructure (Dockerfile, scripts, patches)
│   │   ├── Dockerfile
│   │   ├── runner.sh
│   │   └── diff.patch
│   └── ...
│
├── superset/             # Web UI tests (Apache Superset)
│   ├── __init__.py
│   ├── regression.py
│   ├── requirements/
│   │   ├── requirements.md
│   │   └── requirements.py
│   ├── steps/
│   │   └── __init__.py
│   ├── tests/
│   │   └── __init__.py
│   ├── configs/          # Infrastructure (Dockerfiles, bootstrap scripts, TLS certs)
│   │   ├── Dockerfile.clickhouse-connect
│   │   ├── Dockerfile.clickhouse-sqlalchemy
│   │   ├── bootstrap.sh
│   │   └── ...
│   └── ...
│
├── grafana/              # Web UI tests (Grafana plugin) — planned
│   └── ...
│
└── dbeaver/              # Desktop UI tests (DBeaver) — planned, semi-auto
    └── ...
```

## Test Structure Conventions

### 1. Requirements

Every test suite MUST have a `requirements/` folder containing:

- **`requirements.md`** — A human-readable Software Requirements Specification (SRS).
  Each requirement has a unique identifier following the pattern
  `RQ.SRS-<NNN>.<Product>.<Feature>`, a version, and a prose description.

- **`requirements.py`** — Auto-generated from the `.md` file via
  `tfs requirements generate`. Contains `Requirement` objects that test scenarios
  link back to. **Do not edit by hand.**

### 2. Requirement-to-Scenario Mapping

| Granularity | Mapping |
|---|---|
| Atomic requirement (single behaviour) | 1 requirement → 1 test scenario (ideal) |
| Higher-level requirement (feature area) | 1 requirement → 1 test feature/suite containing multiple scenarios |

Every `@TestScenario` SHOULD reference its requirement(s) via the `@Requirements` decorator:

```python
@TestScenario
@Requirements(RQ_SRS_100_ODBC_DataTypes_Int8("1.0"))
def int8(self, connection):
    """Verify Int8 read/write via ODBC."""
    ...
```

### 3. Steps

Place reusable step functions in the `steps/` directory. Steps represent
**Given / When / Then** actions that are shared across multiple scenarios.

```python
# steps/connection.py
from testflows.core import *

@TestStep(Given)
def odbc_connection(self, dsn="ClickHouse DSN (ANSI)"):
    """Create and return a PyODBC connection."""
    import pyodbc
    connection = pyodbc.connect(f"DSN={dsn}")
    yield connection
    connection.close()
```

For web UI suites (Grafana, Superset) the `steps/` folder typically mirrors the
UI page structure (e.g., `steps/login/`, `steps/dashboard/`, `steps/panel/`).

### 4. Test Scenarios

Test scenarios live in `tests/` and are organized by feature area.

```python
# tests/datatypes.py
from testflows.core import *
from requirements.requirements import *

@TestFeature
@Name("datatypes")
def feature(self, connection):
    """Test all supported ClickHouse data types via ODBC."""
    Scenario(run=int8)
    Scenario(run=int16)
    ...
```

### 5. regression.py (per suite)

Each sub-suite's `regression.py` is the entry point. It:

1. Defines an `argparser` for suite-specific CLI options
2. Declares `xfails` / `ffails` for known issues
3. Sets up infrastructure (Docker containers, services)
4. Imports and runs `Feature`/`Scenario` from `tests/`

```python
@TestModule
@ArgumentParser(my_argparser)
@XFails(xfails)
@FFails(ffails)
def regression(self, ...):
    Feature(run=datatypes_feature)
    Feature(run=connectivity_feature)
```

### 6. Top-level regression.py

The top-level `lts/regression.py` orchestrates all sub-suites so they can be
invoked with a single command:

```bash
python3 lts/regression.py --clickhouse docker://<image>
```

## Automation Approach per Target

| Target | Type | Approach |
|---|---|---|
| clickhouse-odbc | Driver / API | Fully automated — PyODBC + TestFlows |
| grafana | Web UI | Fully automated — Selenium / Playwright (see `altinity/clickhouse-grafana`) |
| superset | Web UI | Fully automated — Selenium / Playwright |
| dbeaver | Desktop UI | Semi-automated — agent-driven with possible manual verification steps |

## Running Tests

```bash
# Run all LTS suites
python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest

# Run only clickhouse-odbc
python3 lts/clickhouse-odbc/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest

# Run only superset
python3 lts/superset/regression.py --clickhouse docker://altinityinfra/clickhouse-server:latest
```
