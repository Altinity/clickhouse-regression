# Superset suite — agent instructions

This suite tests [Apache Superset] with ClickHouse against a ClickHouse LTS
image: the ClickHouse driver loads, connections work over HTTP, HTTPS and the
native protocol, and SQL Lab returns the exact results in a real browser. It
follows the shared conventions in [../AGENTS.md](../AGENTS.md), including the
test-oracle rules; debugging is in [../DEBUGGING.md](../DEBUGGING.md#superset).

## How it works

`feature.py` builds a Superset image with one ClickHouse Python driver, then
starts ClickHouse (with TLS), Superset and a Selenium Chrome node with Docker
Compose. The connection checks use Superset's REST API; the SQL Lab check
drives the browser. One run tests one driver, selected with
`--clickhouse-driver`; CI runs the suite once per driver.

| File | Role |
|---|---|
| `configs/Dockerfile.superset` | `apache/superset` plus the pinned driver |
| `configs/docker-compose.yml` | `clickhouse`, `superset`, `selenium` services; ephemeral host ports |
| `configs/config.xml`, `server.crt`, `server.key`, `dhparam.pem` | ClickHouse HTTPS (8443) and secure native (9440) |
| `configs/default_user.xml` | `default` user reachable from the Compose network |
| `configs/init_schema.sql` | `lts.events`: 1000 rows, `country` from `number % 5`, `amount = number * 0.5` |
| `steps/environment.py` | Compose build, up and teardown, log capture, health waits |
| `steps/ui.py` | Selenium steps, REST API helpers, `check_database_connection()` |
| `tests/clickhouse_integration.py` | Driver engine, connection tests, SQL Lab exact rows |
| `requirements/requirements.md` | SRS-101; regenerate `requirements.py` from it |

Run it, once per driver:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/superset/*" \
    --clickhouse-driver clickhouse-connect --log test.log
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/superset/*" \
    --clickhouse-driver clickhouse-sqlalchemy --log test.log
```

`--superset-version` selects Superset (default `4.1.1`).

## Rules

- **Assert the exact SQL Lab rows.** The check reads `.virtual-table-cell`
  cells and compares them with `EXPECTED_ROWS`, which `init_schema.sql`
  determines. Never fall back to page or editor text: the SQL itself contains
  country codes, for example `DE` inside `ORDER`.
- **Keep `ORDER BY country`** in the SQL Lab query so the row order is fixed.
- **Fail on a visible SQL Lab error** (`[role='alert']` with text).
- **Test connections through `check_database_connection()`**, which calls
  `/api/v1/database/test_connection/`, the endpoint behind the Test Connection
  button. Check its result, not just that a connection was saved.
- **Use each driver's own URIs.** clickhouse-connect: `clickhousedb+connect://`,
  with `?secure=true&verify=false` on port 8443 for HTTPS; it has no native
  protocol. clickhouse-sqlalchemy: `clickhouse+http://`, HTTPS as
  `clickhouse+http://...:8443/...?protocol=https&verify=false` (there is no
  `clickhouse+https` scheme), native as `clickhouse+native://...:9000`.
- **Don't `skip()` a scenario that doesn't apply to the driver**: a skip marks
  its requirements unsatisfied. `feature()` in `tests/clickhouse_integration.py` doesn't run
  the native check for clickhouse-connect, and attaches the driver environment
  requirement to match the driver.
- **Pin the drivers** in `Dockerfile.superset` (`clickhouse-connect==1.3.0`,
  `clickhouse-sqlalchemy==0.2.9`). clickhouse-sqlalchemy 0.3 needs
  SQLAlchemy 2, which Superset 4.1 does not use.
- **Keep the SRS honest.** Schema explorer, charts and dashboards are listed
  under "Not Yet Covered" in `requirements.md`. Only move them into the
  requirements together with tests that check them.
- **Keep teardown bounded**: Compose calls go through `compose_down()` and
  `save_compose_logs()`, which write to files and time out.

## Changing the Superset version

1. Build and start the stack by hand with the new version (see
   [../DEBUGGING.md](../DEBUGGING.md#superset)) and check the selectors used in
   `steps/ui.py`, notably `.virtual-table-cell`, against the new SQL Lab.
2. Run the suite with `--superset-version <version>` for both drivers.
3. Superset 5.0 does not ship `clickhouse-connect`; `Dockerfile.superset`
   installs the driver, so that is covered, but check that the pinned driver
   versions still install.

## Adding a check

1. Add the requirement to `requirements/requirements.md` first, then regenerate
   `requirements.py`. To cover an item from "Not Yet Covered", move it into the
   requirements in the same change as its test.
2. Add a `@TestScenario` with `@Requirements(...)` to `tests/clickhouse_integration.py`, and
   run it from `feature()`. If it only applies to one driver, run it only for
   that driver there; don't `skip()` it.
3. Use the existing steps in `steps/ui.py`: `run_sql_in_editor` and
   `get_sql_lab_result_rows` for SQL Lab, `check_database_connection` and the
   `_http`/`_api_login` helpers for the REST API. Take a screenshot at each UI
   step.
4. Assert exact values derived from `configs/init_schema.sql`, as
   `EXPECTED_ROWS` does, and give queries an `ORDER BY`.
5. For a new page or element, find its selector in a running stack first (see
   [../DEBUGGING.md](../DEBUGGING.md#superset)).

## Before you finish

1. Run the suite once per driver:
   `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/superset/*" --clickhouse-driver clickhouse-connect --log test.log`,
   then with `--clickhouse-driver clickhouse-sqlalchemy`. Check the new
   screenshots in `lts/_instances/superset/screenshots/`.
2. Show that a new or changed check can fail. Run against the silent
   `<limit>3</limit>` image variant from
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): the SQL Lab
   check fails there, while the connection checks pass. A data check that
   still passes there proves nothing.
3. Check the coverage summary: nothing unsatisfied; untested only for the
   other driver's requirements.
4. Regenerate `requirements.py` if you changed `requirements.md`.
5. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/superset/`:

- **A new or renamed option** (such as `--superset-version` or
  `--clickhouse-driver`): add it to `lts_argparser` and `regression()` in
  `lts/regression.py`, pass it to this suite's `Feature` call, and document it
  under CLI Arguments in `lts/README.md` and in the CLI table in
  `lts/AGENTS.md`.
- **A longer run time**: raise `wait_for_superset`'s timeout in
  `steps/environment.py` if startup is slower, and `timeout_minutes` of
  `superset_clickhouse_connect` (60 minutes) and
  `superset_clickhouse_sqlalchemy` (60 minutes) in
  `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under `lts/_instances/superset/`,
  then add its pattern to `artifact_paths` in
  `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.
- **A new driver**: add it to `--clickhouse-driver`'s choices, to
  `DRIVER_ENGINES` in `tests/clickhouse_integration.py`, to `_sqlalchemy_uri()` in
  `steps/ui.py`, to `Dockerfile.superset`, and as a job in `run-lts.yml`.

## Evidence

`lts/_instances/superset/`: `screenshots/*.png` (one per UI step),
`logs/clickhouse.log`, `logs/superset.log`, `logs/selenium.log`,
`logs/compose-ps.log`, `logs/compose-down.log`. The folder is emptied at the
start of each run.

[Apache Superset]: https://superset.apache.org/
