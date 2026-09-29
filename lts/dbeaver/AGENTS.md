# DBeaver suite — agent instructions

This suite checks that the ClickHouse JDBC driver bundled with [DBeaver]
Community Edition, and the SQL DBeaver sends, work against a ClickHouse LTS
image. DBeaver itself is not run. It follows the shared conventions in
[../AGENT.md](../AGENT.md); debugging is in
[../DEBUGGING.md](../DEBUGGING.md#dbeaver).

## How it works

`feature.py` reads the `clickhouse-jdbc` and `httpclient5` versions from the
DBeaver ClickHouse plugin's `plugin.xml` at the chosen DBeaver tag. The runner,
built on the ClickHouse image, resolves exactly those jars with Maven and runs
`configs/Smoke.java`. It replays what a user does in DBeaver: connect, create a
dataset, query it, browse the navigator, open a table and edit its data. It
writes one JUnit testcase per check, reported under `/lts/dbeaver/smoke/`.

| File | Role |
|---|---|
| `configs/Smoke.java` | The 18 checks, in order, with exact expected results |
| `configs/runner.sh` | Starts ClickHouse, resolves the driver jars, runs `Smoke.java` |
| `configs/Dockerfile` | Runner image: the ClickHouse image plus JDK 17 and Maven |
| `feature.py` | Reads the driver versions from DBeaver's `plugin.xml`, runs the checks |
| `requirements/requirements.md` | SRS-106; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/dbeaver/*" --log test.log
```

`--dbeaver-version <tag>` selects the DBeaver CE release (default `26.2.1`).

## Rules

- **Don't claim more than the suite tests.** It covers DBeaver's driver and
  SQL, not DBeaver's startup, plugins, dialogs or result grid. Keep the SRS
  title and the Compatibility requirement worded that way.
- **Copy SQL from the DBeaver plugin**, don't invent it. The navigator and
  statistics queries in `Smoke.java` come from
  `plugins/org.jkiss.dbeaver.ext.clickhouse` (`ClickhouseMetaModel`,
  `ClickhouseDataSource`, `ClickhouseSchema`, `ClickhouseTable`). When DBeaver
  changes them, update `Smoke.java` from the plugin source.
- **Create the dataset through the driver**, as a user does in DBeaver's SQL
  editor, not with `clickhouse-client`. That is what the manual DBeaver check
  did: create a dataset, then run queries such as `count()`.
- **Assert exact results.** Each query check compares with values derived from
  the seeded data (100 rows; `count(score)` is 80 because every fifth score is
  NULL). A check that only runs a query without comparing proves nothing.
- **Keep `create dataset` before the checks that use it**, and read the first
  failed check when several fail.
- **Keep the check count and `min_tests` in step.** `Smoke.java` always
  reports every check; `feature.py` expects 18.

## Changing the DBeaver version

Run the suite with `--dbeaver-version <tag>`. The `Given` step notes the driver
versions it found. An unknown tag fails with `has no ClickHouse plugin at
<url>`. A DBeaver release that switches drivers may need `runner.sh` to resolve
different artifacts.

## Adding a check

1. Add the check to `checks()` in `configs/Smoke.java`, after `create dataset`
   if it uses `lts_dbeaver.events`. Take the SQL from the DBeaver ClickHouse
   plugin source when DBeaver issues it.
2. Compare with an exact expected value, using `expect()` or `require()`.
   Derive it from the dataset created in `create dataset`, and say how in a
   comment when it isn't obvious.
3. Raise `min_tests` in `feature.py` to the new number of checks.
4. Add what the check covers to the list in `RQ.SRS-106.DBeaver.SmokeChecks` in
   `requirements/requirements.md`, then regenerate `requirements.py`.

## Before you finish

1. Run the suite: `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/dbeaver/*" --log test.log`.
   All checks pass, and `logs/test.log` has one `OK` line per check.
2. Show that a new or changed check can fail. Run against the silent
   `<limit>5</limit>` or `<limit>3</limit>` image variant from
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): data
   checks must fail there (9 of 18 did with `limit=5`). Use `<readonly>1</readonly>`
   for a check that writes (15 of 18 failed).
3. Regenerate `requirements.py` if you changed `requirements.md`.
4. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/dbeaver/`:

- **A new or renamed option** (such as `--dbeaver-version`): add it to
  `lts_argparser` and `regression()` in `lts/regression.py`, pass it to this
  suite's `Feature` call, and document it under CLI Arguments in
  `lts/README.md` and in the CLI table in `lts/AGENT.md`.
- **A longer run time**: raise `timeout` in `feature.py`, and `timeout_minutes`
  of `dbeaver` (60 minutes) in `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under `lts/_instances/dbeaver/`,
  then add its pattern to `artifact_paths` in
  `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.
- **The Maven cache**: the `lts-maven-cache` volume is shared with the
  clickhouse-jdbc suite; rename it in both `feature.py` files together.

## Evidence

`lts/_instances/dbeaver/`: `junit.xml`, `logs/build.log`, `logs/test.log` (one
`OK` or `FAIL` line per check, with stack traces), `logs/clickhouse-server.log`.

[DBeaver]: https://github.com/dbeaver/dbeaver
