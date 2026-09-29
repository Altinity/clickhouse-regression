# Debugging LTS Suite Failures

This guide takes you from a red LTS run to a cause. Start with
[Every failure](#every-failure), which works for all seven suites, then go to
the section for the suite that failed. [Messages that fail a whole suite](#messages-that-fail-a-whole-suite)
explains failures that aren't a single test.

All commands run from the repository root. They use the 26.3 LTS image as an
example; use the image you're testing.

## Every failure

### 1. Rerun with a log

Pass `--log` so that you can query the result afterwards, and `--test-to-end`
so that one failure doesn't stop the remaining suites:

```bash
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
    --test-to-end --log test.log
```

### 2. Find what failed

```bash
tfs show fails test.log        # failed, errored and known (xfail) tests
tfs transform fails test.log   # the same, one line per test with the reason
tfs show totals test.log       # counts per test type
tfs show messages --log test.log '/lts/grafana/panel graph/explore count query'
```

`tfs show messages` prints every step of one test, including its notes, so
start with the first failing leaf test it names.

### 3. Rerun only what failed

```bash
python3 lts/regression.py \
    --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
    --only "/lts/clickhouse-driver/*" --log test.log
```

`--only` takes TestFlows test paths, down to a single test:
`"/lts/clickhouse-driver/tests/columns/test_datetime/*"` or
`"/lts/grafana/panel graph/*"`. For the suites that run a tool's own tests,
the runner still runs all of them, and `--only` selects which are reported.

TestFlows replaces `.`, `[` and `:` in test names with look-alike characters,
so use `*` for them in patterns: `/lts/clickhouse-odbc/test*py-3-dsn-0`, not
`/lts/clickhouse-odbc/test.py-3-dsn-0`. Copy paths from `tfs show fails` output
and replace those characters with `*`.

### 4. Read the artifacts

Each suite keeps its output in `lts/_instances/<suite>/`, which is replaced on
the next run of that suite:

| Suite | Files |
|---|---|
| clickhouse-odbc | `junit.xml`; `logs/build.log`, `logs/test.log`, `logs/ctest-detailed.log`, `logs/clickhouse-server.log` |
| clickhouse-driver, clickhouse-sqlalchemy | `junit.xml`; `logs/build.log`, `logs/test.log` (pytest output), `logs/clickhouse-server.log` |
| clickhouse-jdbc | `reports/surefire-*.xml`, `reports/failsafe-*.xml`; `logs/build.log`, `logs/test.log` (Maven output) |
| dbeaver | `junit.xml`; `logs/build.log`, `logs/test.log` (one `OK` or `FAIL` line per check, with the stack trace) |
| grafana, superset | `logs/<service>.log` for each Compose service, `logs/compose-ps.log`, `logs/compose-down.log`; `screenshots/*.png` |

`logs/build.log` is the runner image build. `logs/test.log` is everything the
runner container printed, which is where a failure before the tests shows up.

For a CI run, the same files are in the job's GitHub artifact,
`lts_<suite>-artifacts-x86_zookeeper`, and in the job's S3 report folder under
`lts/_instances/<suite>/`. The job log prints the report folder's URL.

### 5. Decide whose failure it is

A failure is one of three things: a ClickHouse problem, a test or tool
problem, or the environment. Two comparisons settle most cases:

- **Run the same suite against the previous LTS image.** A test that fails on
  both is not a regression in the new build.
- **Run it against the upstream image of the same version**, for example
  `clickhouse/clickhouse-server:26.3`. A test that fails on both is not
  specific to the Altinity build.

To test a suspected cause, build a variant of the image with one setting
changed and rerun. For example, to check whether `async_insert` causes a
failure:

```bash
mkdir -p /tmp/async0
cat > /tmp/async0/zz.xml <<'EOF'
<clickhouse><profiles><default><async_insert>0</async_insert></default></profiles></clickhouse>
EOF
printf 'FROM altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest\nCOPY zz.xml /etc/clickhouse-server/users.d/zz.xml\n' > /tmp/async0/Dockerfile
docker build -t lts-check:async0 /tmp/async0
python3 lts/regression.py --clickhouse docker://lts-check:async0 \
    --clickhouse-version 26.3.13.10001 --only "/lts/clickhouse-driver/*" --log test.log
```

Pass `--clickhouse-version` with a local image like this. The version comes
from the image tag otherwise, and `async0` has none.

## Messages that fail a whole suite

These come from the shared runner in `lts/steps/` rather than from one test.

| Message | What it means | What to do |
|---|---|---|
| `the runner wrote no JUnit XML (...), so the tests did not run` | The runner stopped before the tests: a clone, patch, install or server start failed. | The message ends with the tail of `logs/test.log`; the first error in it is the cause. |
| `the runner exited with code N, expected one of [...]` | The test tool itself failed: pytest exit 2 to 5, a Maven error such as a crashed test JVM, or ctest other than 0 or 8. Any JUnit XML is partial. | Read the end of `logs/test.log`. |
| `expected at least N tests, found M` | Fewer tests ran than the suite's known count, usually because a dependency is missing or discovery broke. | Check `logs/test.log` for collection errors. If a new tool release really has fewer tests, lower `min_tests` in the suite's `feature.py`. |
| `N upstream tests were skipped, more than the M expected` | More tests were skipped than the known budget. | The run notes the skip reasons, grouped by count, just before this message. A reason such as `Numpy package is not installed` means a dependency is missing from the runner. |
| `docker build of lts-<suite>-runner failed` | The runner image did not build. | Read `logs/build.log`. |
| `<image> is an Alpine image` | The runners need an Ubuntu-based ClickHouse image with `apt-get` and `/entrypoint.sh`. | Use the Ubuntu variant of the image. |
| `lts-<suite>-<pid> did not finish within Ns` | The runner hit the suite's timeout and was removed. | Read `logs/test.log` for where it stopped. |
| `fatal: could not read Username for 'https://github.com'` in `logs/test.log` or `logs/build.log` | GitHub refuses git protocol v2 from Ubuntu 22.04's git 2.34. | The runner Dockerfiles set `git config --system protocol.version 0`. Add the same line to any new runner built on Ubuntu 22.04. |

## Reproducing a runner by hand

The ODBC, clickhouse-driver, clickhouse-sqlalchemy, clickhouse-jdbc and
DBeaver suites each run one container, built from `lts/<suite>/configs/`, whose
`runner.sh` prepares and runs the tool's own tests. To work inside it, build the
image the way the suite does, then start it with a shell instead of the runner:

```bash
docker build --build-arg CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
    -t lts-clickhouse_driver-runner lts/clickhouse_driver/configs
mkdir -p lts/_instances/clickhouse_driver/logs
docker run --rm -it -e RELEASE=0.2.10 \
    -v "$PWD/lts/_instances/clickhouse_driver:/results" \
    --entrypoint bash lts-clickhouse_driver-runner
```

Inside the container, run everything in `runner.sh` except the test call. The
line `set +e` comes right before it in every runner except DBeaver's:

```bash
source <(sed '/^set +e/,$d' /runner.sh); set +ex
```

You are now in the cloned, patched and installed project, with ClickHouse
running from the image's own configuration. Run single tests from there.

The runner's environment differs per suite; the suite's `feature.py` is the
reference:

| Suite | Image tag | Build args | `docker run` options |
|---|---|---|---|
| clickhouse-odbc | `lts-clickhouse_odbc-runner` | `CLICKHOUSE_IMAGE`, `ODBC_RELEASE` | none |
| clickhouse-driver | `lts-clickhouse_driver-runner` | `CLICKHOUSE_IMAGE` | `-e RELEASE=0.2.10` |
| clickhouse-sqlalchemy | `lts-clickhouse_sqlalchemy-runner` | `CLICKHOUSE_IMAGE` | `-e RELEASE=0.3.2` |
| clickhouse-jdbc | `lts-clickhouse_jdbc-runner` | none | Needs the Docker socket, host networking and a work directory mounted at the same path; use `--jdbc-maven-args` instead (see [clickhouse-jdbc](#clickhouse-jdbc)) |
| dbeaver | `lts-dbeaver-runner` | `CLICKHOUSE_IMAGE` | `-e DRIVER_VERSION=0.10.0 -e HTTPCLIENT_VERSION=5.4.4 -v lts-maven-cache:/root/.m2` |

## clickhouse-odbc

The suite runs the driver's ctest targets and reports each target as one
scenario directly under `/lts/clickhouse-odbc/`, for example
`/lts/clickhouse-odbc/parametrized-regression․py-3-dsn-0` (select it with
`--only "/lts/clickhouse-odbc/parametrized-regression*py-3-dsn-0"`).
`logs/ctest-detailed.log` has the full output of every target.

- **A `parametrized-regression.py` target fails.** This target is itself a
  TestFlows run, one per DSN, covering data types and parameter binding. Search
  `logs/ctest-detailed.log` for its `Failing` section to find the inner test.
  Upstream's known failures are the `xfails` in
  `test/parameterized/regression.py`, extended in `configs/diff.patch`. Their
  patterns must use `:` wherever the test name contains `.`, for the reason in
  [step 3](#3-rerun-only-what-failed).
- **Fewer than 28 targets ran.** `test/CMakeLists.txt` adds the pyodbc, Perl and
  `isql` targets only if it finds those tools when the build stage configures
  the driver. The `Testing with:` block in `logs/build.log` shows what it found.
- **Rerun one target** in a [runner shell](#reproducing-a-runner-by-hand):

  ```bash
  cd /clickhouse-odbc/build
  ctest -N                                       # list the targets
  ctest -R 'parametrized-regression.py-3-dsn-0' --output-on-failure
  ```

  To run part of the parametrized suite directly:

  ```bash
  cd /clickhouse-odbc/test/parameterized
  DSN="ClickHouse DSN (ANSI)" python3 regression.py --only "/regression/parameterized/*/datatypes/Float32/*"
  ```

- **The build stage is cached** across ClickHouse images. It rebuilds only when
  `--odbc-release` or `configs/diff.patch` changes.

## clickhouse-driver

Each pytest test is one scenario, for example
`/lts/clickhouse-driver/tests/columns/test_datetime/DateTimeTimezonesTestCase/test_use_client_timezone`.

- **Rerun one test** in a [runner shell](#reproducing-a-runner-by-hand):

  ```bash
  python3 -m pytest -v tests/columns/test_datetime.py -k test_use_client_timezone
  ```

- **A known failure was not marked XFail.** The ClickHouse#108038 xfails in
  `lts/regression.py` apply only when the ClickHouse version is 26.3 or later
  *and* the failure message matches the bug. Check the `ClickHouse version:`
  note at the start of the run. With a moving tag such as `latest` the version
  is unknown and version-specific xfails don't apply; pass `--clickhouse-version`.
  If the message changed, the failure may have a different cause.
- **A patch fails to apply** after a driver release bump. `logs/test.log` shows
  the failing `git apply`. The patches for release `X.Y.Z` are listed in
  `configs/patches/X.Y.Z.series`, or `X.Y.series` if there's no exact match.
  Add a series file for the new release.

## clickhouse-sqlalchemy

Works like [clickhouse-driver](#clickhouse-driver), with `RELEASE=0.3.2` and the
pytest output in `logs/test.log`. The runner pins `asynch`, `alembic` and
`pytest-asyncio`. If a test fails right after one of those changed upstream,
compare the versions `pip` installed in `logs/test.log` with a passing run.

## clickhouse-jdbc

The suite runs the `clickhouse-jdbc` module tests of clickhouse-java. The
tests start ClickHouse themselves with Testcontainers, through the host's
Docker socket, from the image under test. Unit tests are reported from
`reports/surefire-*.xml` and integration tests from `reports/failsafe-*.xml`.

- **Rerun one test class** without a manual container:

  ```bash
  python3 lts/regression.py \
      --clickhouse docker://altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest \
      --only "/lts/clickhouse-jdbc/*" --log test.log \
      --jdbc-maven-args "-Dtest=ClickHouseConnectionTest -Dit.test=ClickHouseConnectionTest -Dsurefire.failIfNoSpecifiedTests=false -Dfailsafe.failIfNoSpecifiedTests=false"
  ```

  With `--jdbc-maven-args` the minimum test count and skip budget are relaxed.

- **One failure and many skips in a class.** A class's setup method failed,
  and TestNG skipped every test that depends on it. The setup failure is the
  one to read.
- **`Could not find a valid Docker environment`** or
  `client version 1.32 is too old`. Testcontainers could not talk to Docker.
  The suite passes the host's Docker API version to it; check the
  `host Docker API version:` note and that `/var/run/docker.sock` exists.
- **`Magic is not correct - expect [-126] but got [...]`**. The client could
  not decompress the server's response. clickhouse-jdbc v0.9.0 does this with
  26.x servers, while later 0.9.x releases work. Try another `--jdbc-release`
  and compare with the upstream image before calling it a ClickHouse bug.
- **Leftover containers.** Testcontainers' cleanup container removes its
  containers when Maven exits. If Maven was killed, remove them with
  `docker rm -f $(docker ps -aq --filter label=org.testcontainers)`. That filter
  also matches Testcontainers containers from any other project on the host.
- **Dependency problems.** Maven downloads go to the `lts-maven-cache` volume,
  shared with DBeaver. Run `docker volume rm lts-maven-cache` to start clean.

## dbeaver

`configs/Smoke.java` replays DBeaver's SQL through the JDBC driver that the
chosen DBeaver release bundles. The `Given` step notes which driver version
that is.

- **Read the first failed check.** `create dataset` makes the table that later
  checks use, so when it fails, most checks after it fail too.
  `logs/test.log` has each check's stack trace.
- **`DBeaver <version> has no ClickHouse plugin at <url>`.** No such DBeaver
  release tag, or the plugin moved. Check `--dbeaver-version`.
- **Rerun by hand.** DBeaver's runner has no `set +e` line, so drop the final
  `java` call instead:

  ```bash
  source <(sed '/^java /,$d' /runner.sh); set +ex
  java -cp "/drivers/*" /Smoke.java /results/junit.xml
  ```

  Edit `/Smoke.java` inside the container to try a change, then copy it back to
  `lts/dbeaver/configs/Smoke.java`.

## grafana

The suite runs Grafana, ClickHouse and Selenium with Docker Compose, and drives
Chrome through Selenium.

- **Look at the screenshots** in `lts/_instances/grafana/screenshots/`, taken at each step,
  and at `logs/grafana.log`. A plugin that failed to install or load shows up
  in `logs/grafana.log`.
- **Bring the stack up by hand** with the versions the suite uses:

  ```bash
  export CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest
  export GRAFANA_VERSION=13.2.2 GRAFANA_PLUGIN_VERSION=3.4.9 SELENIUM_VERSION=4.40.0
  docker compose -p grafana-debug -f lts/grafana/configs/docker-compose.yml up -d --wait
  docker compose -p grafana-debug port grafana 3000
  ```

  Open the printed port on `127.0.0.1` and log in as `admin`/`admin`. Remove the
  stack with `docker compose -p grafana-debug down -v`.

- **Check a query without the browser** through Grafana's query API, which is
  what a panel uses:

  ```bash
  curl -s -u admin:admin -H 'Content-Type: application/json' \
      http://127.0.0.1:<port>/api/ds/query -d '{"from": "now-24h", "to": "now", "queries": [{
        "refId": "A", "rawQuery": true, "format": "table",
        "query": "SELECT count() AS c FROM default.test_grafana",
        "datasource": {"type": "vertamedia-clickhouse-datasource", "uid": "clickhouse-direct"}}]}'
  ```

- **The time macros expand to an empty column** (`"" >= toDateTime(...)`). The
  plugin reads the timestamp column from `dateTimeColDataType`, not
  `dateTimeCol`. `timeseries_target()` in `steps/ui.py` sets it.
- **An element is not found after a Grafana upgrade.** The checks read
  Explore result cells (`[role='gridcell']`), the panel found by its
  `data-testid Panel header <title>` and its error marker
  (`data-testid Panel status error`). Open the page in the stack above, find
  the new markup, and update `steps/ui.py`.

## superset

The suite runs Superset, ClickHouse and Selenium with Docker Compose. One run
tests one driver, selected with `--clickhouse-driver`.

- **Look at the screenshots** in `lts/_instances/superset/screenshots/` and at
  `logs/superset.log`.
- **Bring the stack up by hand:**

  ```bash
  export CLICKHOUSE_IMAGE=altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest
  export SUPERSET_VERSION=4.1.1 CLICKHOUSE_PYTHON_DRIVER=clickhouse-connect SELENIUM_VERSION=4.40.0
  docker compose -p superset-debug -f lts/superset/configs/docker-compose.yml up -d --build
  docker compose -p superset-debug port superset 8088
  ```

  Superset takes a minute or two to become healthy. Open the printed port on
  `127.0.0.1` and log in as `admin`/`admin`. Remove the stack with
  `docker compose -p superset-debug down -v`.

- **A connection test fails.** The failure message includes Superset's HTTP
  response. `Could not load database driver` means the installed driver does
  not register that URI scheme. Only `clickhouse-sqlalchemy` has a native
  protocol driver, and its HTTPS URI is `clickhouse+http://...?protocol=https`.
  Try the same URI with **Test Connection** in the database form of the stack
  above.
- **The SQL Lab result differs.** The check compares the result grid cells
  (`.virtual-table-cell`) with the rows that `configs/init_schema.sql` produces.
  A visible SQL Lab error fails the step with its text.

## Watching the browser

Selenium's container runs a browser viewer, noVNC, on port 7900. To watch a
Grafana or Superset test, add `- "0:7900"` under the `selenium` service's
`ports` in the suite's `configs/docker-compose.yml`, run the suite, and open
the published port. The password is `secret`. Don't commit that change.

## Leftovers and hangs

- **Leftover containers.** Runner containers are named `lts-<suite>-<pid>` and
  Compose projects `grafana-lts-<pid>` and `superset-lts-<pid>`:

  ```bash
  docker ps -a --filter name=lts-
  docker compose ls --all
  docker compose -p grafana-lts-12345 down -v
  ```

- **A run hangs.** Setup and teardown commands have timeouts, and runners have
  per-suite timeouts, so a run should not hang. If one does, press Ctrl+C:
  Python prints where it was waiting.

## Proving that a check can fail

A new or changed check proves nothing until it has failed once. Run it against
an image that is broken in a way the check should notice. For example, a
profile setting that silently returns at most three rows from every query:

```bash
mkdir -p /tmp/limit3
cat > /tmp/limit3/zz.xml <<'EOF'
<clickhouse><profiles><default><limit>3</limit></default></profiles></clickhouse>
EOF
printf 'FROM altinityinfra/clickhouse-server:0-26.3.13.10001.altinitytest\nCOPY zz.xml /etc/clickhouse-server/users.d/zz.xml\n' > /tmp/limit3/Dockerfile
docker build -t lts-sabotage:limit3 /tmp/limit3
python3 lts/regression.py --clickhouse docker://lts-sabotage:limit3 \
    --clickhouse-version 26.3.13.10001 --test-to-end --log sabotage.log
```

Checks that read data should fail, and checks that don't, such as login,
should pass. `<readonly>1</readonly>` instead of `<limit>3</limit>` breaks every
write, which catches checks that ignore errors.
