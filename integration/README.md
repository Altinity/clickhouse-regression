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
