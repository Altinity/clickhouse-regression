# clickhouse-sqlalchemy suite — agent instructions

This suite tests the [clickhouse-sqlalchemy] SQLAlchemy dialect, with its
native, HTTP and asynch drivers, against a ClickHouse LTS image by running the
dialect's own pytest suite. It follows the shared conventions in
[../AGENTS.md](../AGENTS.md); debugging is in
[../DEBUGGING.md](../DEBUGGING.md#clickhouse-sqlalchemy).

## How it works

`feature.py` calls `lts.steps.tool_tests.run_tool_tests`, which builds
`configs/` into a runner image based on the ClickHouse image under test, runs
it, and reports each pytest test from `junit.xml` as a TestFlows scenario under
`/lts/clickhouse-sqlalchemy/`.

| File | Role |
|---|---|
| `configs/Dockerfile` | Runner image: the ClickHouse image plus git and Python; `TZ=Europe/Moscow` |
| `configs/runner.sh` | Starts ClickHouse, clones the dialect at `$RELEASE`, applies patches, pins test dependencies, runs pytest |
| `configs/patches/<major.minor>.series` | Patches for a release line: `0.2.series`, `0.3.series` |
| `configs/patches/*.patch` | Test fixes: 4-part version parsing, `alembic` pin, async soft close |
| `feature.py` | Suite entry point: test-count floor and skip budget |
| `requirements/requirements.md` | SRS-104; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/clickhouse-sqlalchemy/*" --log test.log
```

`--sqlalchemy-release <tag>` selects the dialect tag (default `0.3.2`).

## Rules

- **Keep the pins** in `runner.sh`: `asynch==0.2.5`, `alembic==1.11.1` and
  `pytest-asyncio==1.4.0`. The patched tests are known to work with them;
  newer releases have broken the suite before.
- **Always apply `diff-asynch-soft-close.patch`.** Without it the asynch tests
  fail on cursor cleanup ([xzkostyan/clickhouse-sqlalchemy#393]).
- **Start ClickHouse with `/entrypoint.sh`**, never `clickhouse server --daemon`,
  which ignores the image's configuration.
- **Patches change tests, never the dialect.** A test that fails because of a
  ClickHouse bug gets a scoped xfail in `lts/regression.py`, not a patch.

## Changing the dialect version

1. Run the suite with `--sqlalchemy-release <new tag>`.
2. A new release line (for example 0.4) needs its own
   `configs/patches/0.4.series`; a patch release uses its line's series.
3. Compare the pytest summary with the counts in the comment above
   `min_tests` in `feature.py`, and update `min_tests`, `max_skipped` and that
   comment if they legitimately change.

## Adding a check

The dialect's own pytest suite defines the tests, so you don't write tests
here. What you change is which tests run and how their results count:

- **A test fails because the server behaves differently, correctly**: patch
  the test's expectation in `configs/patches/` and add the patch to the release
  line's `.series` file.
- **A test fails because of a ClickHouse bug**: add a scoped xfail in
  `lts/regression.py` with the issue link, a `check_clickhouse_version()`
  condition and a failure-message pattern.
- **Tests are skipped for a missing dependency**: install and pin it in
  `configs/runner.sh`, then raise `min_tests` in `feature.py` to the new count.

## Before you finish

1. Run the suite against the current LTS image, and against the previous LTS
   image if you changed a patch or an xfail:
   `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/clickhouse-sqlalchemy/*" --log test.log`.
2. Compare the test, skip and xfail counts with the comment above `min_tests`
   in `feature.py`, and read the skip reasons the run notes. A new skip reason
   usually means a lost dependency.
3. For a new xfail, show that it matches only its cause: run against an image
   variant without the cause (for ClickHouse#108038, `async_insert=0`) and
   check that the test passes there.
4. If you changed the runner, check that a broken server still fails the
   suite. Use the image variants in
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): a read-only profile failed 397 tests; a silent `<limit>5</limit>` failed 6.
5. If you touched `lts/steps/`, run `python3 -m unittest discover -s lts/steps/tests -t .`.
6. If you changed `requirements/requirements.md`, regenerate
   `requirements.py` with `tfs requirements generate`.
7. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/clickhouse_sqlalchemy/`:

- **A new or renamed option** (such as `--sqlalchemy-release`): add it to
  `lts_argparser` and `regression()` in `lts/regression.py`, pass it to this
  suite's `Feature` call, and document it under CLI Arguments in
  `lts/README.md` and in the CLI table in `lts/AGENTS.md`.
- **A longer run time**: raise `timeout` in `feature.py`, and `timeout_minutes`
  of `clickhouse_sqlalchemy` (60 minutes) in `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under
  `lts/_instances/clickhouse_sqlalchemy/`, then add its pattern to
  `artifact_paths` in `.github/workflows/reusable-suite.yml` and to the `SUITE
  == lts` block of `.github/create_and_upload_logs.sh`. Otherwise CI silently
  doesn't upload it. List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.

## Evidence

`lts/_instances/clickhouse_sqlalchemy/`: `junit.xml`, `logs/build.log`,
`logs/test.log` (pytest output), `logs/clickhouse-server.log`.

[clickhouse-sqlalchemy]: https://github.com/xzkostyan/clickhouse-sqlalchemy
[xzkostyan/clickhouse-sqlalchemy#393]: https://github.com/xzkostyan/clickhouse-sqlalchemy/issues/393
