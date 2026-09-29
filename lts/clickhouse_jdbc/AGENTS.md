# clickhouse-jdbc suite — agent instructions

This suite tests the `clickhouse-jdbc` module of [clickhouse-java] against a
ClickHouse LTS image by running the module's own unit and integration tests.
It follows the shared conventions in [../AGENTS.md](../AGENTS.md); debugging is
in [../DEBUGGING.md](../DEBUGGING.md#clickhouse-jdbc).

## How it works

The runner is a Maven + JDK 17 container. It clones clickhouse-java at
`$RELEASE`, builds the module and runs `mvn verify` with
`-DclickhouseImage=<image under test>`. The integration tests then start
ClickHouse from that image themselves with Testcontainers, through the host's
Docker socket. Surefire (unit) and Failsafe (integration) XML is copied to
`reports/` and each testcase is reported under `/lts/clickhouse-jdbc/`, for
example `/lts/clickhouse-jdbc/jdbc/ClickHouseConnectionTest/testAutoCommit`.

| File | Role |
|---|---|
| `configs/Dockerfile` | Runner image: `maven:3.9-eclipse-temurin-17` |
| `configs/runner.sh` | Clones, builds, runs `mvn verify`, copies the XML reports |
| `feature.py` | Docker socket, host network, same-path work directory, Docker API version, Maven cache volume, test-count floor |
| `requirements/requirements.md` | SRS-105; regenerate `requirements.py` from it |

Run it, or one test class:

```bash
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/clickhouse-jdbc/*" --log test.log
python3 lts/regression.py --clickhouse docker://<image> --only "/lts/clickhouse-jdbc/*" --log test.log \
    --jdbc-maven-args "-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest -Dsurefire.failIfNoSpecifiedTests=false -Dfailsafe.failIfNoSpecifiedTests=false"
```

`--jdbc-release <tag>` selects the clickhouse-java tag (default `v0.9.9`).

## Rules

- **Mount the work directory at the same path** on the host and in the
  runner. Testcontainers bind-mounts test resources and `java.io.tmpdir` into
  the ClickHouse container, and the host's Docker daemon resolves those paths.
- **Keep `--network host` and `TESTCONTAINERS_HOST_OVERRIDE=localhost`** so the
  tests reach the ports Testcontainers maps on the host.
- **Keep passing the host's Docker API version.** clickhouse-java's
  Testcontainers defaults to API 1.32, which Docker Engine 29 and later reject.
- **Keep `-Dmaven.test.failure.ignore=true`** and exit with Maven's exit code:
  test failures are reported from the XML, and a non-zero exit then means Maven
  itself failed, for example a crashed test JVM.
- **Don't rely on Surefire reruns** (`rerunFailingTestsCount`): clickhouse-java
  uses TestNG, which Surefire does not rerun. Handle flaky tests with scoped
  xfails linked to an issue.
- **Name Maven options for the runner `JDBC_MAVEN_ARGS`**, never `MAVEN_ARGS`,
  which Maven 3.9 applies to every `mvn` call, including the build.

## Changing the clickhouse-java version

1. Run one class first with `--jdbc-release <tag>` and `--jdbc-maven-args`,
   then the whole module.
2. Compare the counts with the comment above `min_tests` in `feature.py`. The
   integration test count is what the release report quotes. Update
   `min_tests` and that comment if the counts change.

## Known behavior

- **v0.9.0 fails against 26.x servers** with `Magic is not correct - expect
  [-126]` in 8 of 9 `ClickHouseConnectionTest` tests, on both Altinity and
  `clickhouse/clickhouse-server` images. It passes on 25.8, and v0.9.9 passes
  on 26.3. The 26.3
  release report says 0.9.0 passed, but the manual script never checked out
  the tag.
- **A class whose setup fails** shows one failure and many skips: TestNG skips
  the tests that depend on the setup. Read the setup failure.

## Adding a check

clickhouse-java's own tests define what runs, so you don't write tests here:

- **A test fails because of a ClickHouse bug, or is flaky**: add a scoped xfail
  in `lts/regression.py` with the issue link, a `check_clickhouse_version()`
  condition and a failure-message pattern. Test paths look like
  `/lts/clickhouse-jdbc/jdbc/<Class>/<test>`.
- **Another clickhouse-java module** (for example `jdbc-v2` or `client-v2`):
  change `-pl` in both `mvn` calls in `configs/runner.sh`, copy that module's
  `target/*-reports/TEST-*.xml` in `finish()`, and set `strip_prefix` and
  `min_tests` in `feature.py` for the new count. Expect a longer run.

## Before you finish

1. Run the suite against the current LTS image, and against the previous LTS
   image if you changed a patch or an xfail:
   `python3 lts/regression.py --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest --only "/lts/clickhouse-jdbc/*" --log test.log`.
2. Compare the test, skip and xfail counts with the comment above `min_tests`
   in `feature.py`, and read the skip reasons the run notes. A new skip reason
   usually means a lost dependency.
3. For a new xfail, show that it matches only its cause: run against an image
   variant without the cause (for ClickHouse#108038, `async_insert=0`) and
   check that the test passes there.
4. If you changed the runner, check that a broken server still fails the
   suite. Use the image variants in
   [../DEBUGGING.md](../DEBUGGING.md#proving-that-a-check-can-fail): a read-only profile failed the integration setup; a silent `<limit>5</limit>` failed 4 tests.
5. If you touched `lts/steps/`, run `python3 -m unittest discover -s lts/steps/tests -t .`.
6. If you changed `requirements/requirements.md`, regenerate
   `requirements.py` with `tfs requirements generate`.
7. Update this file if a rule or known behavior changed.

## Keeping the rest in step

Some changes to this suite need matching changes outside `lts/clickhouse_jdbc/`:

- **A new or renamed option** (such as `--jdbc-release` or
  `--jdbc-maven-args`): add it to `lts_argparser` and `regression()` in
  `lts/regression.py`, pass it to this suite's `Feature` call, and document it
  under CLI Arguments in `lts/README.md` and in the CLI table in
  `lts/AGENTS.md`.
- **A longer run time**: raise `timeout` in `feature.py`, and `timeout_minutes`
  of `clickhouse_jdbc` (120 minutes) in `.github/workflows/run-lts.yml`.
- **A new kind of evidence file**: write it under
  `lts/_instances/clickhouse_jdbc/`, then add its pattern to `artifact_paths`
  in `.github/workflows/reusable-suite.yml` and to the `SUITE == lts` block of
  `.github/create_and_upload_logs.sh`. Otherwise CI silently doesn't upload it.
  List it under Evidence below and in the artifacts table of
  `lts/DEBUGGING.md`.
- **Changed commands, logs or failure messages**: update this suite's section
  of `lts/DEBUGGING.md`.
- **The Maven cache**: the `lts-maven-cache` volume is shared with the DBeaver
  suite; rename it in both `feature.py` files together.

## Evidence

`lts/_instances/clickhouse_jdbc/`: `reports/surefire-*.xml`,
`reports/failsafe-*.xml`, `logs/build.log`, `logs/test.log` (Maven output).
The `work/` directory is scratch space and is not collected.

[clickhouse-java]: https://github.com/ClickHouse/clickhouse-java
