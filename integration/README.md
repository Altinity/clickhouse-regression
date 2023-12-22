# ClickHouse PyTest Integration Tests

[TestFlows](https://testflows.com) program to execute [ClickHouse PyTest integration tests](https://github.com/ClickHouse/ClickHouse/tree/master/tests/integration).

For example, you can execute all tests for ClickHouse source code at `~/ClickHouse` and locally build binaries at `~/ClickHouse/build/programs/` as follows:
 
```bash
./regression.py --root-dir ~/ClickHouse/ --binary ~/ClickHouse/build/programs/clickhouse --log test.log
```

## 🍊 Integration tests

ClickHouse PyTest integration tests are distributed as part of ClickHouse source code, therefore you need to checkout ClickHouse repository first.

```bash
git clone https://github.com/ClickHouse/ClickHouse.git
```

You can find the integration tests at

```bash
ls ClickHouse/tests/integration
```

## 🌀 ClickHouse binaries

Once you have the source code for the tests, you must either build ClickHouse binaries locally or specify the binary that you want to use for testing
using the `--binary` option. If you specify a path, it is assumed that the following files are present in the same directory:

* `clickhouse`
* `clickhouse-odbc-bridge`
* `clickhouse-library-bridge`

By default, `--binary` is set to `/usr/bin/clickhouse`.

However, you can also specify:

* either relative or absolute file path, for example:
  ```bash
  --binary ~/ClickHouse/build/programs/clickhouse
  ```
* http[s]://<url_to_binary_or_deb_package>, for example:
  ```bash
  --binary https://s3.amazonaws.com/altinity-build-artifacts/PRs/338/6ab51af598079c670627dd84f70bb90c63446ee0/package_aarch64/clickhouse-common-static_23.8.8.21.altinitystable_arm64.deb
  ```
* docker://<clickhouse/docker_image:tag>, for example:
  ```bash
  --binary docker://altinity/clickhouse-server:23.3.13.7.altinitystable
  ```

## 🏃 Running Tests

Tests list is dynamically collected unless `--tests` option is specified. All tests are executed
unless the `--slice`, which selects specific slice of tests from the tests list, or the `--part`, which breaks tests into parts and runs only the specified part,
options are specified. The `--slice` is applied first and then `--part` if any.

Tests are run in groups (`--group-size`, default: 100). Each group executes tests in parallel (`--in-parallel`, default: 10).
Any failed tests are retried (`retry-attempts`, default: 2), where each retry attempt runs remaining failed tests without any parallelism.
To prevent retrying massive test fails the `--max-failed-tests-to-retry` (default: 100) option limits the maximum number of failed tests to retry.

For example, let's run the first 10 tests (`--slice 0 10`) without skipping build, save and load images steps: 
```
./regression.py --root-dir ~/ClickHouse/ --binary ~/ClickHouse/build/programs/clickhouse --slice 0 10 -l test.log
```

| Test program flow will consist of the following main parts |
| -- |
| build images |
| save images to `docker/dockerd_volume_dir/images.tar` |
| start runner container and load images to `/var/lib/docker` where `docker/dockerd_volume_dir` is mounted |
| run the first 10 dynamically collect integration tests (the default group size is `100` so all tests are executed as part of the first group) |

```bash
✔ [ OK ] /regression/build images/build clickhouse∕s3-proxy:latest (2s 13ms)
✔ [ OK ] /regression/build images/build clickhouse∕integration-tests-runner:latest.base (2s 23ms)
✔ [ OK ] /regression/build images/build clickhouse∕python-bottle:latest (2s 20ms)
✔ [ OK ] /regression/build images/build clickhouse∕integration-helper:latest (2s 50ms)
✔ [ OK ] /regression/build images/build clickhouse∕mysql-golang-client:latest (2s 43ms)
✔ [ OK ] /regression/build images/build clickhouse∕dotnet-client:latest (2s 39ms)
✔ [ OK ] /regression/build images/build clickhouse∕postgresql-java-client:latest (2s 24ms)
✔ [ OK ] /regression/build images/build clickhouse∕test-base:latest (2s 27ms)
✔ [ OK ] /regression/build images/build clickhouse∕kerberos-kdc:latest (2s 36ms)
✔ [ OK ] /regression/build images/build clickhouse∕mysql-js-client:latest (2s 52ms)
✔ [ OK ] /regression/build images/build clickhouse∕mysql-java-client:latest (2s 60ms)
✔ [ OK ] /regression/build images/build clickhouse∕mysql-php-client:latest (2s 47ms)
✔ [ OK ] /regression/build images/build clickhouse∕nginx-dav:latest (2s 27ms)
✔ [ OK ] /regression/build images/build clickhouse∕kerberized-hadoop:latest (3s 13ms)
✔ [ OK ] /regression/build images/build clickhouse∕integration-tests-runner:latest (3s 28ms)
✔ [ OK ] /regression/build images/build clickhouse∕integration-test:latest (4s 14ms)
✔ [ OK ] /regression/build images (4s 22ms)
✔ [ OK ] /regression/save images (3m 15s)
✔ [ OK ] /regression/load saved images (24s 36ms)
✔ [ OK ] /regression/group/0/test_access_for_functions∕test.py::test_access_rights_for_function (1s 366ms)
✔ [ OK ] /regression/group/0/test_aggregation_memory_efficient∕test.py::test_remote (2s 941ms)
✔ [ OK ] /regression/group/0/test_access_for_functions∕test.py::test_ignore_obsolete_grant_on_database (5s 60ms)
✔ [ OK ] /regression/group/0/test_allowed_client_hosts∕test.py::test_allowed_host (2s 398ms)
✔ [ OK ] /regression/group/0/test_allowed_client_hosts∕test.py::test_denied_host (800ms)
✔ [ OK ] /regression/group/0/test_access_control_on_cluster∕test.py::test_access_control_on_cluster (2s 649ms)
✔ [ OK ] /regression/group/0/test_access_control_on_cluster∕test.py::test_grant_all_on_cluster (1s 493ms)
✔ [ OK ] /regression/group/0/test_MemoryTracking∕test.py::test_http (10s 389ms)
✔ [ OK ] /regression/group/0/test_MemoryTracking∕test.py::test_tcp_multiple_sessions (20s 951ms)
✔ [ OK ] /regression/group/0/test_MemoryTracking∕test.py::test_tcp_single_session (8s 835ms)
✔ [ OK ] /regression/group/0 (1m 21s)
✔ [ OK ] /regression/group (1m 21s)
✔ [ OK ] /regression (5m 17s)
```

## 🖼 Integration tests images

By default, all images needed for running integration tests are built locally and
saved as a tar file into the `docker/dockerd_volume_dir/images.tar` file.
This tar file is then used to preload images into the `/var/lib/docker` mounted inside the
runner's container.  The `/var/lib/docker` folder inside the container is mounted as `docker/dockerd_volume_dir` and is re-used between different runs.

## ☔ Custom `clickhouse/integration-tests-runner` image

The test program uses a custom `clickhouse/integration-tests-runner` image.
that uses the original `clickhouse/integration-tests-runner` image as the base (tagged as `latest.base`)
but adds extra packages. This custom image is defined in the `docker/runner` folder.

## ⌚ Skip building images

All images are build, saved and loaded by default for each test program run. However, after the images are build and
loaded into the `/docker/dockerd_volume_dir` you can specify `--skip-build-images` to skip these steps.

## 🌤 Program options

```
options:
  -h, --help                                      show this help message and exit

test arguments:
  --root-dir ROOT_DIR                             ClickHouse source root directory
  --binary BINARY                                 path to ClickHouse binary, default:
                                                  /usr/bin/clickhouse. The path can be
                                                  either:relative or absolute file path,
                                                  http[s]://<url_to_binary_or_deb_package>, or
                                                  docker://<clickhouse/docker_image:tag>
  --slice TESTS_SLICE TESTS_SLICE                 run specific slice of tests specified as '<start>
                                                  <end>', default: 0 -1
  --part PART PART                                run specific part of tests specified as '<part
                                                  number> <total number of parts>', default: 0 1
  --tests TESTS [TESTS ...]                       list of tests to run, default: collect all tests
                                                  automatically
  --deselect DESELECT [DESELECT ...]              list of tests to exclude from the tests list
  --retry-attempts RETRY_ATTEMPTS                 number of times to retry failed tests, default: 2
  --max-failed-tests-to-retry MAX_FAILED_TESTS_TO_RETRY
                                                  maximum number of failed tests to retry, default:
                                                  100
  --in-parallel IN_PARALLEL                       number of tests to be executed in parallel,
                                                  default: 10
  --analyzer                                      run tests with analyzer enabled
  --cleanup-containers                            remove all running containers on runner's test
                                                  session start
  --skip-build-images                             skip building all docker images inside the
                                                  ClickHouse/docker/test/integration folder
  --images-tag IMAGES_TAG                         tag to be used for all docker images or when
                                                  building them, default: latest
  --timeout TIMEOUT                               timeout in sec to wait for tests to complete,
                                                  default: none
  --group-timeout GROUP_TIMEOUT                   timeout in sec to wait for a group of tests to
                                                  complete, default: none
  --group-size GROUP_SIZE                         size of test group, default: 100
```
