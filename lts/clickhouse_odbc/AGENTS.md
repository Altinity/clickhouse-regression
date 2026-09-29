# clickhouse-odbc suite — agent instructions

This suite tests the [clickhouse-odbc] driver against a ClickHouse LTS image by
building the driver and running all of its ctest targets. It follows the shared
conventions in [../AGENT.md](../AGENT.md); debugging is in
[../DEBUGGING.md](../DEBUGGING.md#clickhouse-odbc).

## How it works

`configs/Dockerfile` has two stages. The `build` stage compiles the driver on
plain `ubuntu:22.04`, the same base as the ClickHouse image, so the build is
cached across ClickHouse images and only redone when `--odbc-release` or
`configs/diff.patch` changes. The final stage is the ClickHouse image plus the
runtime packages and the build tree. `runner.sh` starts ClickHouse and runs
every ctest target, and each target is reported as one scenario directly under
`/lts/clickhouse-odbc/`, for example `/lts/clickhouse-odbc/test․py-3-dsn-0`.

| File | Role |
|---|---|
| `configs/Dockerfile` | Cached build stage and runtime stage |
| `configs/runner.sh` | Starts ClickHouse, runs ctest with JUnit output |
| `configs/diff.patch` | Fixes to upstream tests, including the parametrized suite's xfail patterns |
| `feature.py` | Suite entry point: 28-target floor, SRS-100 requirements |
| `requirements/requirements.md` | SRS-100; regenerate `requirements.py` from it |

Run it:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/clickhouse-odbc/*" --log test.log
```

`--odbc-release <tag>` selects the driver tag (default `v1.2.1.20220905`).

## Rules

- **Run every ctest target.** Don't exclude targets with `ctest -E`: earlier
  filters hid the pyodbc datatype suite and four real driver integration tests
  (`*-nano-it-*`, which go through nanodbc but test the driver).
- **Install the test tools in the build stage**: `python3` with `pyodbc`,
  `perl` with `libdbd-odbc-perl`, and unixODBC's `isql`/`iusql`.
  `test/CMakeLists.txt` only registers those targets when it finds the tools
  at configure time. Fewer than 28 targets means one was missing.
- **Keep the build stage independent of the ClickHouse image.** Anything that
  depends on `CLICKHOUSE_IMAGE` belongs in the final stage, or every new image
  recompiles the driver.
- **Retry git operations** in the build stage and keep
  `git config --system protocol.version 0`. The build clones many nested
  submodules, and GitHub refuses protocol v2 from Ubuntu 22.04's git 2.34.
- **Write upstream xfail patterns with `:` for `.`**. The parametrized suite
  is a TestFlows run, and TestFlows replaces `.` in test names, so a pattern
  like `13.26` silently matches nothing. `diff.patch` fixes the patterns
  upstream shipped.
- **Start ClickHouse with `/entrypoint.sh`**, never `clickhouse server --daemon`.

## Changing the driver version

1. Run the suite with `--odbc-release <tag>`. The build stage recompiles once
   (about 4 minutes).
2. If `diff.patch` no longer applies, the build fails in `logs/build.log`.
   Rebase the patch on the new tag.
3. Check that all targets still run (the `Testing with:` block in
   `logs/build.log`) and update `min_tests` in `feature.py` if the number of
   targets changes.

## Known behavior

- **Float32 parameter check**: the parametrized suite's `datatypes/Float32`
  check selects a Float32 column with the Float64 parameter `13.26`, which
  ClickHouse correctly does not match. Upstream lists it as a known failure;
  it shows as XFail inside the parametrized target. It fails the same way on
  25.8.

## Adding a check

The driver's CMake project defines the ctest targets, so you don't write tests
here:

- **A test in the pyodbc parametrized suite needs a fix or a known failure**:
  change it in `configs/diff.patch`. Known failures go in the `xfails` of
  `test/parameterized/regression.py`, with `:` wherever the test name has `.`.
- **A target type is missing**: install the tool it needs in the build stage of
  `configs/Dockerfile` (and the runtime stage if it runs at test time), check
  the `Testing with:` block in `logs/build.log`, then raise `min_tests` in
  `feature.py`.
- **A target fails because of a ClickHouse bug**: add a scoped xfail in
  `lts/regression.py`. Targets are reported directly under
  `/lts/clickhouse-odbc/`; use `*` for the `.` in their names.

## Before you finish

1. Run the suite against the current LTS image, and against the previous LTS
   image if you changed a patch or an xfail:
   `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/clickhouse-odbc/*" --log test.log`.
2. Compare the test, skip and xfail counts with the comment above `min_tests`
   in `feature.py`, and read the skip reasons the run notes. A new skip reason
   usually means a lost dependency.
3. For a new xfail, show that it matches only its cause: run against an image
   variant without the cause (for ClickHouse#108038, `async_insert=0`) and
   check that the test passes there.
4. If you changed the runner, check that a broken server still fails the
   suite. Use the image variants in
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): a read-only profile failed 8 of 28 targets.
5. If you touched `lts/steps/`, run `python3 -m unittest discover -s lts/steps/tests -t .`.
6. If you changed `requirements/requirements.md`, regenerate
   `requirements.py` with `tfs requirements generate`.
7. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/clickhouse_odbc/`:

- **A new or renamed option** (such as `--odbc-release`): add it to
  `lts_argparser` and `regression()` in `lts/regression.py`, pass it to this
  suite's `Feature` call, and document it under CLI Arguments in
  `lts/README.md` and in the CLI table in `lts/AGENT.md`.
- **A longer run time**: raise `timeout` in `feature.py`, and `timeout_minutes`
  of `clickhouse_odbc` (90 minutes) in `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under
  `lts/_instances/clickhouse_odbc/`, then add its pattern to `artifact_paths`
  in `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.

## Evidence

`lts/_instances/clickhouse_odbc/`: `junit.xml`, `logs/build.log`,
`logs/test.log`, `logs/ctest-detailed.log` (full output of every target,
including the parametrized TestFlows runs), `logs/clickhouse-server.log`.

[clickhouse-odbc]: https://github.com/ClickHouse/clickhouse-odbc
