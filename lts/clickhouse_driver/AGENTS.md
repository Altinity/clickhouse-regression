# clickhouse-driver suite — agent instructions

This suite tests the [clickhouse-driver] Python package (native protocol)
against a ClickHouse LTS image by running the driver's own pytest suite. It
follows the shared conventions in [../AGENTS.md](../AGENTS.md); debugging is in
[../DEBUGGING.md](../DEBUGGING.md#clickhouse-driver).

## How it works

`feature.py` calls `lts.steps.tool_tests.run_tool_tests`, which builds
`configs/` into a runner image based on the ClickHouse image under test, runs
it, and reports each pytest test from `junit.xml` as a TestFlows scenario under
`/lts/clickhouse-driver/`, for example
`/lts/clickhouse-driver/tests/columns/test_datetime/DateTimeTimezonesTestCase/test_use_client_timezone`.

| File | Role |
|---|---|
| `configs/Dockerfile` | Runner image: the ClickHouse image plus git, Python and build tools; `TZ=Europe/Moscow` |
| `configs/runner.sh` | Starts ClickHouse, clones the driver at `$RELEASE`, applies patches, installs, runs pytest |
| `configs/patches/<release>.series` | Patches to apply to a release, in order |
| `configs/patches/*.patch` | Test-only fixes for server behavior changes |
| `feature.py` | Suite entry point: test-count floor and skip budget |
| `requirements/requirements.md` | SRS-103; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/clickhouse-driver/*" --log test.log
```

`--clickhouse-driver-release <tag>` selects the driver tag (default `0.2.10`).
It is not Superset's `--clickhouse-driver`.

## Rules

- **Keep `TZ=Europe/Moscow` in the Dockerfile.** The driver's datetime tests
  assume the server and client run in that timezone.
- **Start ClickHouse with `/entrypoint.sh`**, never `clickhouse server --daemon`,
  which ignores the image's configuration.
- **Keep `numpy` and `pandas` installed.** Without them 108 tests skip silently
  and the driver's NumPy/pandas support goes untested.
- **Pin every package `runner.sh` installs itself** (`cython`, `lz4`, `numpy`,
  `pandas`). The driver's `testsrequire.py` controls the rest.
- **Patches change test expectations only, never driver code.** Each patch must
  answer "what changed in the server", for example the `total_rows` in progress
  packets. A test that fails because of a ClickHouse bug gets an xfail, not a
  patch.
- **Patch both copies of a test.** Many tests exist twice, in `tests/` and in
  `tests/numpy/`; `diff-0.2.9-progress.patch` and
  `diff-0.2.9-numpy-progress.patch` are an example pair.
- **Scope xfails** in `lts/regression.py` by ClickHouse version and failure
  message, as the ClickHouse#108038 entries are.

## Changing the driver version

1. Run the suite with `--clickhouse-driver-release <new tag>`.
2. If a patch no longer applies, `logs/test.log` shows the failing `git apply`.
   Add `configs/patches/<new tag>.series`, listing the patches that still apply
   and any new ones. A release without its own series uses `<major.minor>.series`.
3. Compare the pytest summary with the counts in the comment above
   `min_tests` in `feature.py`. When they legitimately change, update
   `min_tests`, `max_skipped` and that comment.

## Known behavior

- **ClickHouse#108038**: six timezone tests fail on 26.3+ because `async_insert`
  is on by default and string datetime literals then ignore
  `use_client_time_zone`. They pass with `async_insert=0`. They are xfailed from
  26.3, and only when the failure message matches.
- **JSON**: `diff-26.3.patch` skips the four JSON tests on 25.11+, where
  ClickHouse removed `Object('json')` and the driver does not support the
  native `JSON` type yet.

## Adding a check

The driver's own pytest suite defines the tests, so you don't write tests
here. What you change is which tests run and how their results count:

- **A test fails because the server behaves differently, correctly**: patch
  the test's expectation in `configs/patches/`, add the patch to the release's
  `.series` file, and patch the `tests/numpy/` copy too if there is one.
- **A test fails because of a ClickHouse bug**: add a scoped xfail in
  `lts/regression.py` with the issue link, a `check_clickhouse_version()`
  condition and a failure-message pattern.
- **Tests are skipped for a missing dependency**: install and pin it in
  `configs/runner.sh`, then raise `min_tests` in `feature.py` to the new count.

## Before you finish

1. Run the suite against the current LTS image, and against the previous LTS
   image if you changed a patch or an xfail:
   `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/clickhouse-driver/*" --log test.log`.
2. Compare the test, skip and xfail counts with the comment above `min_tests`
   in `feature.py`, and read the skip reasons the run notes. A new skip reason
   usually means a lost dependency.
3. For a new xfail, show that it matches only its cause: run against an image
   variant without the cause (for ClickHouse#108038, `async_insert=0`) and
   check that the test passes there.
4. If you changed the runner, check that a broken server still fails the
   suite. Use the image variants in
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): a read-only profile (`<readonly>1</readonly>`) failed 452 tests; a silent `<limit>5</limit>` failed 45.
5. If you touched `lts/steps/`, run `python3 -m unittest discover -s lts/steps/tests -t .`.
6. If you changed `requirements/requirements.md`, regenerate
   `requirements.py` with `tfs requirements generate`.
7. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/clickhouse_driver/`:

- **A new or renamed option** (such as `--clickhouse-driver-release`): add it
  to `lts_argparser` and `regression()` in `lts/regression.py`, pass it to this
  suite's `Feature` call, and document it under CLI Arguments in
  `lts/README.md` and in the CLI table in `lts/AGENTS.md`.
- **A longer run time**: raise `timeout` in `feature.py`, and `timeout_minutes`
  of `clickhouse_driver` (60 minutes) in `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under
  `lts/_instances/clickhouse_driver/`, then add its pattern to `artifact_paths`
  in `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.

## Evidence

`lts/_instances/clickhouse_driver/`: `junit.xml`, `logs/build.log`,
`logs/test.log` (pytest output), `logs/clickhouse-server.log`.

[clickhouse-driver]: https://github.com/mymarilyn/clickhouse-driver
