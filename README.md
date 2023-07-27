## ClickHouse Tests in [TestFlows]

This directory contains integration tests written using [TestFlows] 
that involves several ClickHouse instances, custom configs, ZooKeeper, etc.

## Table of Contents

* 1 [Supported environment](#supported-environment)
* 2 [Prerequisites](#prerequisites)
* 3 [Running CI/CD](#running-cicd)
  * 3.1 [Running Only Specific Suites](#running-only-specific-suites)
  * 3.2 [Running from Docker image](#running-from-docker-image)
  * 3.3 [Running from Altinity repo](#running-from-altinity-repo)
  * 3.4 [Running from ClickHouse PR](#running-from-clickhouse-pr)
* 4 [Running CI/CD with CI/CD trigger](#running-cicd-with-cicd-trigger)
* 5 [CI/CD Secrets And Variables](#cicd-secrets-and-variables)
  * 5.1 [Variables](#variables)
  * 5.2 [Secrets](#secrets)
* 6 [Running tests locally](#running-tests-locally)
  * 6.1 [Output Verbosity](#output-verbosity)
  * 6.2 [Running Only Selected Tests](#running-only-selected-tests)
  * 6.3 [How To Debug Why Test Failed](#how-to-debug-why-test-failed)
    * 6.3.1 [Step 1: find which tests failed](#step-1-find-which-tests-failed)
    * 6.3.2 [Step 2: download `test.log` that contains all raw messages](#step-2-download-testlog-that-contains-all-raw-messages)
    * 6.3.3 [Step 3: get messages for the failing test](#step-3-get-messages-for-the-failing-test)
    * 6.3.4 [Step 4: working with the `test.log`](#step-4-working-with-the-testlog)
  * 6.4 [Running S3 Suites](#running-s3-suites)
    * 6.4.1 [Minio](#minio)
    * 6.4.2 [AWS S3 Storage](#aws-s3-storage)
    * 6.4.3 [GCS (Google Cloud Storage)](#gcs-google-cloud-storage)
  * 6.5 [Running Tiered Storage Suites](#running-tiered-storage-suites)
    * 6.5.1 [Normal](#normal)
    * 6.5.2 [Running on Minio](#running-on-minio)
    * 6.5.3 [Running on AWS S3 Storage](#running-on-aws-s3-storage)
    * 6.5.4 [Running on GCS Storage](#running-on-gcs-storage)
    * 6.5.5 [Pausing In Tests](#pausing-in-tests)
* 7 [Running GitHub Actions](#running-github-actions)

## [Supported environment](#table-of-contents)

* [Ubuntu] 22.04
* [Python 3] >= 3.8
* [TestFlows] >= 1.9.51
* [Docker Compose] == 1.29.2

## [Prerequisites](#table-of-contents)

* [Docker](https://docs.docker.com/engine/install/)

To install all necessary Python modules (including [TestFlows] and [Docker Compose]), execute the following command:

```bash
pip3 install -r pip_requirements.txt
```

## [Running CI/CD](#table-of-contents)

### [Running Only Specific Suites](#table-of-contents)

Specify `suite` variable to select running only specific suites

| Variable | | |
| --- | --- | ---  |
| `suite` | `window_functions` | Window Functions suite |
| `suite` | `aes_encryption` | AES Encryption Functions suite |
| `suite` | `clickhouse_keeper` | ClickHouse Keeper suite |
| `suite` | `datetime64_extended_range` | Extended DateTime64 suite |
| `suite` | `disk_level_encryption` | Disk Level Encryption |
| `suite` | `example` | Example suite |
| `suite` | `extended_precision_data_types` | Extended Precision Data Types suite |
| `suite` | `kafka` | Kafka suite |
| `suite` | `kerberos` | Kerberos suite |
| `suite` | `ldap` | LDAP suite |
| `suite` | `lightweight_delete` | Lightweight Delete suite |
| `suite` | `map_type` | Map Data Type suite |
| `suite` | `parquet` | Parquet Data Type suite |
| `suite` | `parquet_minio` | Parquet MinIO suite |
| `suite` | `parquet_s3` | Parquet AWS S3 suite |
| `suite` | `part_moves_between_shards` | Part Moves Between Shards suite |
| `suite` | `s3` | All S3 (MinIO, AWS, GCS) suites |
| `suite` | `s3_aws` | S3 AWS suite |
| `suite` | `s3_gcs` | S3 GCS suite |
| `suite` | `ssl_server` | SSL Server suite |
| `suite` | `tiered_storage` | All Tiered Storage (Local Disk, MinIO, AWS, GCS) suites |
| `suite` | `tiered_storage_aws` | Tiered Storage AWS suite |
| `suite` | `tiered_storage_gcs` | Tiered Storage GCS suite |
| `suite` | `window_functions` | Window Functions suite |
| `suite` | `benchmark` | S3 Benchmak suite |

### [Running from Docker image](#table-of-contents)
When running the CI/CD pipeline, provide the following variables:  
Example values using `altinity/clickhouse-server:21.8.15.15.altinitystable`
| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `docker://altinity/clickhouse-server` |
| `Variable` | `version` | `21.8.15.15.altinitystable` |

### [Running from Altinity repo](#table-of-contents)
When running the CI/CD pipeline, provide the following variables:

| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `deb://builds.altinity.cloud/apt-repo/pool/main` |
| `Variable` | `version` | The version to use for tests. For example, `21.8.8.1.altinitystable` |

### [Running from ClickHouse PR](#table-of-contents)
Get the link to the deb package: PR -> ClickHouse build check (actions) -> Details -> copy link to a deb package.  
Break down the link into CI/CD variables:  
Example values using https://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release/clickhouse-client_22.7.1.1738_amd64.deb
| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release` NOTE: 'deb' instead of 'https' and no '/' on the end. |
| `Variable` | `version` | `22.7.1.1738` |
| `Variable` | `package_version_postfix` | By default `all` (supports older versions), specify `amd64` for newer PRs where all packages have `amd64` postfix. |

## [Running CI/CD with CI/CD trigger](#table-of-contents)
To run the CI/CD pipline you can use cicd-trigger.py
```./cicd-trigger.py```
with following options

```
-w --wait             Wait for pipeline to finish.
--package             Specify docker:// or deb:// package.
--version             Specify clickhouse version.
--package-postfix     Postfix of the clickhouse-server and clickhouse-client deb package, default: 'amd64'. Choices 'amd64', 'all'.
--suite               Select test suite to run, default: 'all'. Choices "all", "aes_encryption", "aggregate_functions", "atomic_insert", "base_58", "clickhouse_keeper", "datetime64_extended_range", "disk_level_encryption", "dns", "example", "extended_precision_data_types", "kafka", "kerberos", "ldap", "lightweight_delete", "map_type", "parquet", "part_moves_between_shards", "rbac", "s3", "s3_aws", "s3_gcs", "selects", "ssl_server", "tiered_storage", "tiered_storage_aws", "tiered_storage_gcs", "window_functions", "benchmark".
--output              Tests stdout output style, default: 'classic'. Choices 'nice', 'classic', 'short', etc.
--parallel            Enable or disable running tests in parallel, default: 'on'. Choices 'on', 'off'.
--token               Personal access token or private token with api access to the gitlab project, default: 'GITLAB_TOKEN' environment variable.
--options             Extra options that will be added to test run command.
--arch                Architecture to run the tests on, default: 'amd64'. Choices 'amd64', 'arm64'.
--branch              Specify which branch to run the tests on, default: 'main'.
--artifacts           Specify whether to upload artifacts internally or publically, default: 'internal'. Choices 'internal', 'public'. Bucket for internal upload: 'altinity-internal-test-reports'. Bucket for public upload 'altinity-test-reports'.
--debug               Enable script running in debug mode, default: 'False'. Choices 'True', 'False'.
```

## [CI/CD Secrets And Variables](#cicd-secrets-and-variables)

### [Variables](#variables)

The CI/CD has the following variables:
| Variable | Purpose | Default |
| --- | --- | ---  |
| `PARALLEL` | Specify whether to run tests within each suite in parallel. | 1 | 
| `UPLOAD_LOGS` | Specify whether to upload logs. | 1 |

### [Secrets](#secrets)

The CI/CD has the following secrets:
| Secret | Purpose | Notes |
| --- | --- | --- |
| `AWS_ACCESS_KEY` | AWS Secret Access Key for the bucket used during testing. |   |
| `AWS_KEY_ID` | AWS Access Key ID for the bucket used during testing. | |
| `AWS_BUCKET` | AWS Bucket used during testing. | |
| `AWS_REGION` | AWS Region of the bucket used during testing. | |
| `GCS_KEY_ID` | GCS Key ID for the bucket used during testing. | |
| `GCS_KEY_SECRET` | GCS Key Secret for the bucket used during testing. | |
| `GCS_URI` | GCS URI of the bucket used for testing. | |
| `AWS_REPORT_KEY_ID` | AWS Access Key ID for the report bucket. | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `AWS_REPORT_SECRET_ACCESS_KEY` | AWS Secret Access Key for the report bucket. | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `AWS_REPORT_REGION` | AWS Region of the report bucket. | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `DOCKER_USERNAME` | Docker username for login to prevent pull limit. | Not necessary if running small amount of tests. |
| `DOCKER_PASSWORD` | Docker password for login to prevent pull limit. | Not necessary if running small amount of tests. |

## [Running tests locally](#table-of-contents)

You can run tests locally by passing `--local` and `--clickhouse-binary-path` to the top level `regression.py` or
`cd` into any sub-folders to run suite specific `regression.py`.

* `--local` specifies that regression will be run locally
* `--clickhouse-binary-path` specifies the path to the ClickHouse binary on the host machine that will be used during the regression
  run. You can also use docker image that should have `docker://` prefix.
  For example, `--clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine`

> Note: you can pass `-h` or `--help` argument to the `regression.py` to see a help message.
>
> ```bash
> python3 regression.py -h
> ```

> Note: make sure that the ClickHouse binary has correct permissions. 
> If you are using `/usr/bin/clickhouse` its owner and group is set to `root:root` by default 
> and it needs to be changed to `clickhouse:clickhouse`. You can change the owner and the group 
> using the following command.
> 
> ```bash
> sudo chown clickhouse:clickhouse /usr/bin/clickhouse
> ```

Using the default ClickHouse installation and its server binary at `/usr/bin/clickhouse`, you can run 
regressions locally using the following command.

```bash
python3 regression.py --local --clickhouse-binary-path "/usr/bin/clickhouse"
```
### [Output Verbosity](#table-of-contents)

You can control verbosity of the output by specifying the output format with `-o` or `--output` option.
See `--help` for more details.

### [Running Only Selected Tests](#table-of-contents)

You can run only the selected tests by passing `--only` option to the `regression.py`.

For example,

```bash
./regression.py --local --clickhouse-binary-path /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/*"
```

will execute all `rbac/syntax/grant privilege` tests.

If you want to run only a single test such as the `/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('*.*',), allow_introspection=False` you can do it as follows

```bash
./regression.py --local --clickhouse-binary-path /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('[*].[*]',), allow_introspection=False/*"
```

> Note that you need to surround special characters such as `*` with square brackets, for example `[*]`.

> Note that you need to end the filtering pattern with `/*` to run all the steps inside the test.

For more information, please see [Filtering](https://testflows.com/handbook/#Filtering) section in the [TestFlows Handbook].

### [How To Debug Why Test Failed](#table-of-contents)

#### [Step 1: find which tests failed](#table-of-contents)

If [TestFlows] check does not pass you should look at the end of the `test_run.txt.out.log` to find the list
of failing tests. For example,

```bash
clickhouse_testflows_tests_volume
Start tests
➤ Dec 02,2020 22:22:24 /clickhouse
...
Failing

✘ [ Fail ] /clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='SELECT', on=('db0.table0', 'db0.*', '*.*', 'tb0', '*'), allow_column=True, allow_introspection=False
✘ [ Fail ] /clickhouse/rbac/syntax/grant privilege/grant privileges
✘ [ Fail ] /clickhouse/rbac/syntax/grant privilege
✘ [ Fail ] /clickhouse/rbac/syntax
✘ [ Fail ] /clickhouse/rbac
✘ [ Fail ] /clickhouse
```

In this case the failing test is

```
/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='SELECT', on=('db0.table0', 'db0.*', '*.*', 'tb0', '*'), allow_column=True, allow_introspection=False
```

while the others

```
✘ [ Fail ] /clickhouse/rbac/syntax/grant privilege/grant privileges
✘ [ Fail ] /clickhouse/rbac/syntax/grant privilege
✘ [ Fail ] /clickhouse/rbac/syntax
✘ [ Fail ] /clickhouse/rbac
✘ [ Fail ] /clickhouse
```

failed because the first fail gets "bubble-up" the test execution tree all the way to the top level test which is the
`/clickhouse`.

#### [Step 2: download `test.log` that contains all raw messages](#table-of-contents)

You need to download the `test.log` that contains all raw messages.

#### [Step 3: get messages for the failing test](#table-of-contents)

Once you know the name of the failing test and you have the `test.log` that contains all the raw messages
for all the tests, you can use `tfs show test messages` command. 

> You get the `tfs` command by installing [TestFlows]. 

For example,

```bash
cat test.log | tfs show test messages "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='SELECT', on=\('db0.table0', 'db0.\*', '\*.\*', 'tb0', '\*'\), allow_column=True, allow_introspection=False"
```

> Note: that characters that are treated as special in extended regular expressions need to be escaped. In this case
> we have to escape the `*`, `(`, and the `)` characters in the test name.

#### [Step 4: working with the `test.log`](#table-of-contents)

You can use the `test.log` with many of the commands provided by the 
`tfs` utility. 

> See `tfs --help` for more information. 

For example, you can get a list of failing tests from the `test.log` using the
`tfs show fails` command as follows

```bash
$ cat test.log | tfs show fails
```

or get the results using the `tfs show results` command as follows

```bash
$ cat test.log | tfs show results
```

or you can transform the log to see only the new fails using the
`tfs transform fail --new` command as follows

```bash
$ cat test.log | tfs transform fails --new
```

### [Running S3 Suites](#table-of-contents)

#### [Minio](#table-of-contents)

Minio is the default test suite, but can be specificed using `--storage minio`.

Examples:

Explicit storage declaration:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage minio
```

Utilizing default values:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

You can also specify the minio uri (`--minio-uri`), root user (`--minio-root-user`), and root password (`--minio-root-password`). However, this is not necessary.

#### [AWS S3 Storage](#table-of-contents)

Aws requires a region(`--aws-s3-region`) and a bucket(`--aws-s3-bucket`) (the bucket must end with `/`), in addition to the key id and secret access key.
Aws can be specified using `--storage aws_s3`.

Env variables:
```bash
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
$ export AWS_DEFAULT_REGION=
$ export S3_AMAZON_BUCKET=
```

Examples:

Inline:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws_s3_key_id [masked] --aws_s3_access_key [masked] --aws-s3-bucket [masked] --aws-s3-region [masked] --storage aws_s3
```
Env:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage aws_s3
```

#### [GCS (Google Cloud Storage)](#table-of-contents)

GCS requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`), in addition to the s3 key id and secret access key.
GCS can be specified using `--storage gcs`.

Env variables:
```bash
$ export GCS_URI=
$ export GCS_KEY_ID=
$ export GCS_KEY_SECRET=
```

Examples:

Inline:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --storage gcs
```
Env:
```bash
$ s3/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage gcs
```

### [Running Tiered Storage Suites](#table-of-contents)

#### [Normal](#table-of-contents)

Normal tiered storage suite does not require any variables to be provided.

From the regression directory, it can be run with the following command:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

#### [Running on Minio](#table-of-contents)

Minio tiered storage suite only requires that `--with-minio` is specified.

It can be run with the following command:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-minio
```

#### [Running on AWS S3 Storage](#table-of-contents)

AWS S3 tiered storage requires an access key (`--aws-s3-access-key`), a key id (`--aws-s3-key-id`), and a uri (`--aws-s3-uri`). The uri must end with `/`.
These can be passed as environment variables. AWS S3 must be specified using `--with-s3amazon`.

Env variables:
```bash
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
$ export S3_AMAZON_URI=
```

Examples:

Inline:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws-s3-key-id [masked] --aws-s3-access-key [masked] --aws-s3-uri [masked] --with-s3amazon
```
Env:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3amazon
```

#### [Running on GCS Storage](#table-of-contents)

GCS tiered storage requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`).
GCS can be specified using `--with-s3gcs`.

Env variables:
```bash
$ export GCS_URI=
$ export GCS_KEY_ID=
$ export GCS_KEY_SECRET=
```

Examples:

Inline:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --with-s3gcs
```
Env:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3gcs
```

#### [Pausing in Tests](#table-of-contents)

You can explicitly specify `PAUSE_BEFORE`, `PAUSE_AFTER`, `PAUSE_ON_PASS` and `PAUSE_ON_FAIL` flags inside your test program.
For example,
```bash
with Test("my test"):
    with Step("my step 1", flags=PAUSE_BEFORE):
        note("my step 1")
    
    with Step("my step 2", flags=PAUSE_AFTER):
        note("my step 2")

    with Step("my step 2", flags=PAUSE_ON_PASS):
        note("my step 2")
        
    with Step("my step 2", flags=PAUSE_ON_FAIL):
        note("my step 2")
```
For decorated tests `Flags` decorator can be used to set these flags.

```bash
@TestScenario
@Flags(PAUSE_BEFORE|PAUSE_AFTER) # pause before and after this test
def my_scenario(self):
    pass
```
 This can be used for getting access to [Docker Compose] environment with condition equal to cluster condition on current step by executing standard [Docker Compose] commands ("ps", "exec" etc.) from "*_env" folder. It allows to make some manual checks/changes on dockers and continue test with new manually set conditions.

## [Running GitHub Actions](#table-of-contents)
To run GitHub actions, navigate to `Actions`, select `Run CI/CD regression tests`. Inside `Run workflow` dropdown menu specify the package, version, suite and upload destination of artifacts.

Package: `docker://` or `https://` package specifier to use for tests. For example: 
* docker://altinity/clickhouse-server
* docker://clickhouse/clickhouse-server
* https://s3.amazonaws.com/altinity-build-artifacts/217/acf34c9fc6932aaf9af69425612070b50529f484/package_release/clickhouse-client_22.8.11.17.altinitystable_amd64.deb
 
Version: Version of clickhouse to use for tests. The test verifies that node version matches specified version. When package option uses `docker://` specifier then the version is the image tag. For example:
 * 22.3.9.19-alpine
 * 22.3.8.40.altinitystable
 * latest
 
Suite: Which suite to run. Default runs all suites.
 
Artifacts: Specify whether to upload to internal or public s3 bucket. 'altinity-internal-test-reports' for internal upload, 'altinity-test-reports' for public.

[Python 3]: https://www.python.org/
[Ubuntu]: https://ubuntu.com/ 
[TestFlows]: https://testflows.com
[TestFlows Handbook]: https://testflows.com/handbook/
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
