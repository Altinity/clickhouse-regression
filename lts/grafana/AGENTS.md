# Grafana suite — agent instructions

This suite tests the Altinity [clickhouse-grafana] datasource plugin
(`vertamedia-clickhouse-datasource`) in Grafana against a ClickHouse LTS image,
through a real browser. It follows the shared conventions in
[../AGENTS.md](../AGENTS.md), including the test-oracle rules; debugging is in
[../DEBUGGING.md](../DEBUGGING.md#grafana).

## How it works

`feature.py` starts ClickHouse, Grafana (with the plugin installed from its
GitHub release) and a Selenium Chrome node with Docker Compose. ClickHouse is
seeded by `configs/init_schema.sql`, and the datasources are provisioned from
`configs/provisioning/`. The tests drive Grafana through Selenium, and also
query Grafana's API from the logged-in browser session.

| File | Role |
|---|---|
| `configs/docker-compose.yml` | `clickhouse`, `grafana`, `selenium` services; ephemeral host ports |
| `configs/init_schema.sql` | `default.test_grafana`: 100 rows, one every 10 seconds back from startup |
| `configs/provisioning/datasources/` | `clickhouse` and `clickhouse-direct` (fixed uid) datasources |
| `configs/users.xml` | `default` user reachable from the Compose network |
| `steps/environment.py` | Compose up and teardown, log capture, health waits |
| `steps/ui.py` | Selenium and API steps: result cells, panel checks, `/api/ds/query` |
| `tests/login.py` | Log in, then confirm the session user through `/api/user` |
| `tests/datasource_query.py` | Explore queries: `SELECT version()` (one result cell) and a count (`c = 100`) |
| `tests/dashboard_panel.py` | Dashboard time-series panel with the time macros |
| `requirements/requirements.md` | SRS-102; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/grafana/*" --log test.log
```

Options: `--grafana-version` (default `13.2.2`) and `--grafana-plugin-version`
(default `3.4.9`).

## Rules

- **Read exact values from the element under test.** Explore results come
  from `[role='gridcell']` cells, never from page text. A dashboard panel is
  found by `data-testid Panel header <title>`, and every check is scoped to that
  panel. Don't wait for, or assert on, any `table` or `canvas` on the page.
- **Check panel data through the API as well.** The panel UI proves it drew
  something; `query_datasource()` runs the panel's own query through
  `/api/ds/query` and the test checks the data (bucket counts adding up to 100).
- **Fail on errors.** A visible `data-testid Alert error` in Explore, or a
  panel's `data-testid Panel status error`, fails the step with its text.
  Grafana keeps an empty, hidden error alert on the page, so check visibility
  and text.
- **Set the time column in `dateTimeColDataType`.** The plugin reads it for
  `$timeSeries`, `$timeFilter` and their `Ms` variants; with only `dateTimeCol`
  the macros expand to an empty column name. Build panel queries with
  `timeseries_target()`.
- **Put the macros in the SQL** of a test that claims to test them.
- **Compare the server version only when it is known.** Use
  `self.context.clickhouse_version`, which is `None` for moving tags such as
  `latest`.
- **Pin the Grafana version.** Selectors and page structure change between
  Grafana releases; `latest` made results depend on the day of the run.
- **Keep teardown bounded**: Compose calls go through `compose_down()` and
  `save_compose_logs()`, which write to files and time out, rather than
  capturing output through a pipe.

## Changing the Grafana or plugin version

1. Bring the stack up by hand with the new version (see
   [../DEBUGGING.md](../DEBUGGING.md#grafana)) and check the selectors used in
   `steps/ui.py` against the new pages.
2. Run the suite with `--grafana-version <version>`, then change the default in
   `lts/regression.py` and `feature.py`.
3. For a plugin version, check the release zip exists at the URL in
   `docker-compose.yml`; a failed install shows in `logs/grafana.log`.

## Adding a check

1. Add the requirement to `requirements/requirements.md` first, then regenerate
   `requirements.py`. A check without a requirement doesn't show in coverage,
   and a requirement without a check shows as untested.
2. Add a `@TestScenario` with `@Requirements(...)` to the matching module in
   `tests/`, and run it from that module's `feature()`. For a new module, load
   it in `feature.py`.
3. Build it from the existing steps in `steps/ui.py`: `open_explore_with_query`,
   `click_run_query` and `get_result_table` for Explore; `timeseries_target`,
   `create_dashboard_with_timeseries_panel`, `verify_panel_rendered` and
   `query_datasource` for dashboards. Take a screenshot at each UI step.
4. Assert exact values derived from `configs/init_schema.sql`. Its rows are
   relative to startup time, so use counts and bucket sizes, not timestamps.
5. For a new page or element, find its selector in a running stack first (see
   [../DEBUGGING.md](../DEBUGGING.md#grafana)), and scope it to the element
   under test.

## Before you finish

1. Run the suite: `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/grafana/*" --log test.log`.
   Check the new screenshots in `lts/_instances/grafana/screenshots/`.
2. Show that a new or changed check can fail. Run against the silent
   `<limit>3</limit>` image variant from
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): the Explore
   count and the dashboard check fail there, while login and the version check
   pass. A data check that still passes there proves nothing.
3. Check the coverage summary: every requirement satisfied, none unsatisfied.
4. Regenerate `requirements.py` if you changed `requirements.md`.
5. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/grafana/`:

- **A new or renamed option** (such as `--grafana-version`): add it to
  `lts_argparser` and `regression()` in `lts/regression.py`, pass it to this
  suite's `Feature` call, and document it under CLI Arguments in
  `lts/README.md` and in the CLI table in `lts/AGENTS.md`.
- **A longer run time**: raise the wait timeouts in `steps/environment.py` if
  startup is slower, and `timeout_minutes` of `grafana` (60 minutes) in
  `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under `lts/_instances/grafana/`,
  then add its pattern to `artifact_paths` in
  `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.
- **A new default version**: change it in both `lts/regression.py` and
  `feature.py`, and in `lts/README.md`.

## Evidence

`lts/_instances/grafana/`: `screenshots/*.png` (one per UI step),
`logs/clickhouse.log`, `logs/grafana.log`, `logs/selenium.log`,
`logs/compose-ps.log`, `logs/compose-down.log`. The folder is emptied at the
start of each run.

[clickhouse-grafana]: https://github.com/Altinity/clickhouse-grafana
