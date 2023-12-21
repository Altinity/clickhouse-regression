# ClickHouse PyTest Integration Tests

[TestFlows](https://testflows.com) program to execute [ClickHouse PyTest integration tests](https://github.com/ClickHouse/ClickHouse/tree/master/tests/integration).

For example,

Execute all regression tests against ClickHouse source code at `~/ClickHouse` and locally build binaries at `~/ClickHouse/build/programs/`.
 
```bash
./regression.py --root-dir ~/ClickHouse/ --binary ~/ClickHouse/build/programs/clickhouse --log test.log
```

By default, all images needed for running integration tests are built locally and
saved as a tar file into the `docker/dockerd_volume_dir/images.tar` file.
This tar file is then used to preload images into the `/var/lib/docker` mounted inside the
runner's container.  The `/var/lib/docker` folder inside the container is mounted as `docker/docker_volume_dir` and is re-used between different runs.

The test program uses a custom `clickhouse/integration-tests-runner` image.
that uses the original `clickhouse/integration-tests-runner` image as the base (tagged as `latest.base`)
but adds extra packages. This custom image is defined in the `docker/runner` folder.

## Program options

```bash
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
