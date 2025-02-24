<img align=right style="width: 5em;" src="https://github.com/user-attachments/assets/1e97270f-7925-4cc2-8791-8d0cc77fe512">

<br>

# 🔬 Regression Tests for ClickHouse®

This directory contains integration tests written using 👽 [TestFlows] 🛸
that involves several ClickHouse instances, custom configs, ZooKeeper, etc.

##  🗓 Scheduled Regression Runs

Results for **the latest** scheduled workflow runs.

| ClickHouse Version              | Status                                                                                                                                                                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`head`**                      | [![Scheduled ClickHouse head](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-head.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-head.yml)                  |
| **`latest`**                    | [![Scheduled ClickHouse latest Regression](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-latest.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-latest.yml) |
| **`24.12`**                    | [![🗓 Scheduled ClickHouse 24.12](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-12.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-12.yml) |
| **`24.8`**                      | [![Scheduled ClickHouse 24.8 Regression](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-8.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-8.yml)       |
| **`24.3`**                      | [![Scheduled ClickHouse 24.3 Regression](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-3.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-24-3.yml)       |
| **`23.8`**                      | [![Scheduled ClickHouse 23.8](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-23-8.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-23-8.yml)                  |
| **`23.3`**                      | [![Scheduled ClickHouse 23.3](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-23-3.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-clickhouse-23-3.yml)                  |
| **`24.8.11.51285.altinitystable`**  | [![Scheduled Altinity 24.8](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-24-8.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-24-8.yml)                        |
| **`23.8.11.29.altinitystable`** | [![Scheduled Altinity 23.8](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-23-8.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-23-8.yml)                        |
| **`23.3.19.33.altinitystable`** | [![Scheduled Altinity 23.3](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-23-3.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-23-3.yml)                        |
| **`22.8.15.25.altinitystable`** | [![Scheduled Altinity 22.8](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-22-8.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-22-8.yml)                        |
| **`22.3.15.34.altinitystable`** | [![Scheduled Altinity 22.3](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-22-3.yml/badge.svg)](https://github.com/Altinity/clickhouse-regression/actions/workflows/scheduled-regression-altinity-22-3.yml)                        |

## 📅 Timetable of Scheduled Regression Runs

| Day           | latest & head | Every Other Version |
| ------------- | ------------- | ------------------- |
| **Sunday**    | ❌ No          | ❌ No                |
| **Monday**    | ❌ No          | ❌ No                |
| **Tuesday**   | **✅ Yes**     | ❌ No                |
| **Wednesday** | ❌ No          | ❌ No                |
| **Thursday**  | **✅ Yes**     | ❌ No                |
| **Friday**    | ❌ No          | ❌ No                |
| **Saturday**  | **✅ Yes**     | **✅ Yes**           |

## 🔍 Table of Contents

* 1 [Supported Environment](#supported-environment)
* 2 [Prerequisites](#prerequisites)
* 3 [Running CI/CD](#running-cicd)
  * 3.1 [Running Only Specific Suites](#running-only-specific-suites)
  * 3.2 [Running From Docker Image](#running-from-docker-image)
  * 3.3 [Running From Altinity Repo](#running-from-altinity-repo)
  * 3.4 [Running From ClickHouse PR](#running-from-clickhouse-pr)
* 4 [Running CI/CD With CI/CD Trigger](#running-cicd-with-cicd-trigger)
* 5 [CI/CD Secrets and Variables](#cicd-secrets-and-variables)
  * 5.1 [Variables](#variables)
  * 5.2 [Secrets](#secrets)
* 6 [Running Tests Locally](#running-tests-locally)
  * 6.1 [Output Verbosity](#output-verbosity)
  * 6.2 [Running Only Selected Tests](#running-only-selected-tests)
  * 6.3 [How To Debug Why Test Failed](#how-to-debug-why-test-failed)
    * 6.3.1 [Step 1: Find Which Tests Failed](#step-1-find-which-tests-failed)
    * 6.3.2 [Step 2: Download `test.log` That Contains All Raw Messages](#step-2-download-testlog-that-contains-all-raw-messages)
    * 6.3.3 [Step 3: Get Messages for the Failing Test](#step-3-get-messages-for-the-failing-test)
    * 6.3.4 [Step 4: Working With the `test.log`](#step-4-working-with-the-testlog)
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

## [Supported Environment](#table-of-contents)

* [Ubuntu] 22.04 / 24.04
* [Python 3] >= 3.10.12
* [Docker](https://docs.docker.com/engine/install/ubuntu/) >= Docker version 25.0.3, build 4debf41
* [Docker Compose] >= v2.23.1 (non-Python version)

## [Prerequisites](#table-of-contents)

### Docker

[Docker](https://docs.docker.com/engine/install/ubuntu/)

### Standalone `docker-compose`

Standalone `docker-compose` binary.

[Docker Compose](https://docs.docker.com/compose/install/standalone/)

For example,

#### x86_64

```bash
sudo curl -SL https://github.com/docker/compose/releases/download/v2.23.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Aarch64 (ARM64)

```bash
sudo curl -SL https://github.com/docker/compose/releases/download/v2.23.1/docker-compose-linux-aarch64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Python modules

To install all necessary Python modules (including [TestFlows]), execute the following command:

```bash
pip3 install -r requirements.txt
```

## [Running CI/CD](#table-of-contents)

### [Running Only Specific Suites](#table-of-contents)

Specify `suite` variable to select running only specific suites

| Variable | Name                            | Description                                             |
| -------- | ------------------------------- | ------------------------------------------------------- |
| `suite`  | `aes_encryption`                | AES Encryption suite                                    |
| `suite`  | `aggregate_functions`           | Aggregate Functions suite                               |
| `suite`  | `atomic_insert`                 | Atomic Insert suite                                     |
| `suite`  | `alter_all`                     | Full Alter suite                                        |
| `suite`  | `alter_replace_partition`       | Alter Replace Partition suite                           |
| `suite`  | `alter_attach_partition`        | Alter Replace Attach suite                              |
| `suite`  | `alter_move_partition`          | Alter Move Attach suite                                 |
| `suite`  | `base_58`                       | Base58 suite                                            |
| `suite`  | `benchmark_all`                 | All Ontime Benchmark (MinIO, AWS, GCS) suite            |
| `suite`  | `benchmark_aws`                 | Ontime Benchmark AWS suite                              |
| `suite`  | `benchmark_gcs`                 | Ontime Benchmark GCS suite                              |
| `suite`  | `benchmark_minio`               | Ontime Benchmark MinIO suite                            |
| `suite`  | `clickhouse_keeper`             | ClickHouse Keeper (No SSL and SSL FIPS) suite           |
| `suite`  | `data_types`                    | Data Types suite                                        |
| `suite`  | `datetime64_extended_range`     | Extended DateTime64 suite                               |
| `suite`  | `disk_level_encryption`         | Disk Level Encryption                                   |
| `suite`  | `dns`                           | DNS suite                                               |
| `suite`  | `engines`                       | Engines suite                                           |
| `suite`  | `example`                       | Example suite                                           |
| `suite`  | `extended_precision_data_types` | Extended Precision Data Types suite                     |
| `suite`  | `kafka`                         | Kafka suite                                             |
| `suite`  | `kerberos`                      | Kerberos suite                                          |
| `suite`  | `ldap`                          | LDAP suite                                              |
| `suite`  | `lightweight_delete`            | Lightweight Delete suite                                |  |
| `suite`  | `parquet_all`                   | Full Parquet Suite                                      |
| `suite`  | `parquet`                       | Parquet Data Type suite                                 |
| `suite`  | `parquet_minio`                 | Parquet MinIO suite                                     |
| `suite`  | `parquet_s3`                    | Parquet AWS S3 suite                                    |
| `suite`  | `part_moves_between_shards`     | Part Moves Between Shards suite                         |
| `suite`  | `rbac`                          | RBAC suite                                              |
| `suite`  | `s3_all`                        | All S3 (MinIO, AWS, GCS) suites                         |
| `suite`  | `s3_aws`                        | S3 AWS suite                                            |
| `suite`  | `s3_gcs`                        | S3 GCS suite                                            |
| `suite`  | `s3_minio`                      | S3 MinIO suite                                          |
| `suite`  | `selects`                       | Selects suite                                           |
| `suite`  | `session_timezone`              | Session Timezone suite                                  |
| `suite`  | `ssl_server`                    | SSL Server suite                                        |
| `suite`  | `tiered_storage_all`            | All Tiered Storage (Local Disk, MinIO, AWS, GCS) suites |
| `suite`  | `tiered_storage_aws`            | Tiered Storage AWS suite                                |
| `suite`  | `tiered_storage_gcs`            | Tiered Storage GCS suite                                |
| `suite`  | `tiered_storage_local`          | Tiered Storage Local suite                              |
| `suite`  | `tiered_storage_minio`          | Tiered Storage MinIO suite                              |
| `suite`  | `vfs_all`                       | Full VFS (MinIO, AWS, GCS) suite                        |
| `suite`  | `vfs_aws`                       | VFS AWS suite                                           |
| `suite`  | `vfs_gcs`                       | VFS GCS suite                                           |
| `suite`  | `vfs_minio`                     | VFS MinIO suite                                         |
| `suite`  | `window_functions`              | Window Functions suite                                  |

### [Running From Docker Image](#table-of-contents)
When running the CI/CD pipeline, provide the following variables:  
Example values using `altinity/clickhouse-server:21.8.15.15.altinitystable`
| Variables  |           |                                       |
| ---------- | --------- | ------------------------------------- |
| `Variable` | `package` | `docker://altinity/clickhouse-server` |
| `Variable` | `version` | `21.8.15.15.altinitystable`           |

### [Running From Altinity Repo](#table-of-contents)
When running the CI/CD pipeline, provide the following variables:

| Variables  |           |                                                                      |
| ---------- | --------- | -------------------------------------------------------------------- |
| `Variable` | `package` | `deb://builds.altinity.cloud/apt-repo/pool/main`                     |
| `Variable` | `version` | The version to use for tests. For example, `21.8.8.1.altinitystable` |

### [Running From ClickHouse PR](#table-of-contents)
Get the link to the deb package: PR -> ClickHouse build check (actions) -> Details -> copy link to a deb package.  
Break down the link into CI/CD variables:  
Example values using https://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release/clickhouse-client_22.7.1.1738_amd64.deb
| Variables  |                           |                                                                                                                                                                 |
| ---------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Variable` | `package`                 | `deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release` NOTE: 'deb' instead of 'https' and no '/' on the end. |
| `Variable` | `version`                 | `22.7.1.1738`                                                                                                                                                   |
| `Variable` | `package_version_postfix` | By default `all` (supports older versions), specify `amd64` for newer PRs where all packages have `amd64` postfix.                                              |

## [Running CI/CD With CI/CD Trigger](#table-of-contents)
To run the CI/CD pipline you can use cicd-trigger.py
```./cicd-trigger.py```
with following options

```
-w --wait             Wait for pipeline to finish.
--package             Specify docker:// or deb:// package.
--version             Specify clickhouse version.
--package-postfix     Postfix of the clickhouse-server and clickhouse-client deb package, default: 'amd64'. Choices 'amd64', 'all'.
--suite               Select test suite to run, default: 'all'. Choices "all", "aes_encryption", "aggregate_functions", "atomic_insert", "base_58", "clickhouse_keeper", "datetime64_extended_range", "disk_level_encryption", "dns", "example", "extended_precision_data_types", "kafka", "kerberos", "ldap", "lightweight_delete", "map_type", "parquet","parquet_minio", "parquet_s3", "part_moves_between_shards", "rbac", "s3", "s3_aws", "s3_gcs", "selects", "ssl_server", "tiered_storage", "tiered_storage_aws", "tiered_storage_gcs", "window_functions", "benchmark".
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
| Variable      | Purpose                                                     | Default |
| ------------- | ----------------------------------------------------------- | ------- |
| `PARALLEL`    | Specify whether to run tests within each suite in parallel. | 1       |
| `UPLOAD_LOGS` | Specify whether to upload logs.                             | 1       |

### [Secrets](#secrets)

The CI/CD has the following secrets:
| Secret                         | Purpose                                                   | Notes                                                            |
| ------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------------- |
| `AWS_ACCESS_KEY`               | AWS Secret Access Key for the bucket used during testing. |                                                                  |
| `AWS_KEY_ID`                   | AWS Access Key ID for the bucket used during testing.     |                                                                  |
| `AWS_BUCKET`                   | AWS Bucket used during testing.                           |                                                                  |
| `AWS_REGION`                   | AWS Region of the bucket used during testing.             |                                                                  |
| `GCS_KEY_ID`                   | GCS Key ID for the bucket used during testing.            |                                                                  |
| `GCS_KEY_SECRET`               | GCS Key Secret for the bucket used during testing.        |                                                                  |
| `GCS_URI`                      | GCS URI of the bucket used for testing.                   |                                                                  |
| `AWS_REPORT_KEY_ID`            | AWS Access Key ID for the report bucket.                  | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `AWS_REPORT_SECRET_ACCESS_KEY` | AWS Secret Access Key for the report bucket.              | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `AWS_REPORT_REGION`            | AWS Region of the report bucket.                          | The report buckets are hardcoded in `create_and_upload_logs.sh`. |
| `DOCKER_USERNAME`              | Docker username for login to prevent pull limit.          | Not necessary if running small amount of tests.                  |
| `DOCKER_PASSWORD`              | Docker password for login to prevent pull limit.          | Not necessary if running small amount of tests.                  |

## [Running Tests Locally](#table-of-contents)

You can run tests locally by passing `--local` and `--clickhouse` to the top level `regression.py` or
`cd` into any sub-folders to run suite-specific `regression.py`.

* `--local` specifies that regression will be run locally
* `--clickhouse` specifies a path to a ClickHouse package or binary that will be used during the regression
  run. You can also use a docker image using the `docker://` prefix.
  For example, `--clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine`
* `--base-os` specifies a docker image to install ClickHouse into when `--clickhouse` is not a docker image.
  Supported distributions are `altinityinfra/clickhouse-regression-multiarch:2.0` (default), `ubuntu`, and `alpine`.
  There is experimental support for `fedora` and `redhat/ubi9`.

> [!TIP]
> You can pass the `-h` or `--help` argument to the `regression.py` to see a help message.
>
> ```bash
> python3 regression.py -h
> ```

> [!IMPORTANT]
> Make sure that the ClickHouse binary has correct permissions. 
> If you are using `/usr/bin/clickhouse` its owner and group are set to `root:root` by default 
> and it needs to be changed to `clickhouse:clickhouse`. You can change the owner and the group 
> using the following command.
> 
> ```bash
> sudo chown clickhouse:clickhouse /usr/bin/clickhouse
> ```

> [!NOTE]
> If you need to restore the old behavior of copying binaries out of packages,
> instead of installing them, use the `--as-binary` flag.

Using the default ClickHouse installation and its server binary at `/usr/bin/clickhouse`, you can run 
regressions locally using the following command.

```bash
python3 regression.py --local --clickhouse "/usr/bin/clickhouse"
```
### [Output Verbosity](#table-of-contents)

You can control the verbosity of the output by specifying the output format with the `-o` or `--output` option.
See `--help` for more details.

### [Running Only Selected Tests](#table-of-contents)

You can run only the selected tests by passing the `--only` option to the `regression.py`.

For example,

```bash
./regression.py --local --clickhouse /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/*"
```

will execute all `rbac/syntax/grant privilege` tests.

If you want to run only a single test such as the `/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('*.*',), allow_introspection=False` you can do it as follows

```bash
./regression.py --local --clickhouse /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('[*].[*]',), allow_introspection=False/*"
```
> [!NOTE]
> * You need to surround special characters such as `*` with square brackets, for example `[*]`.
> * You need to end the filtering pattern with `/*` to run all the steps inside the test.

For more information, please see the [Filtering](https://testflows.com/handbook/#Filtering) section in the [TestFlows Handbook].

### [How To Debug Why Test Failed](#table-of-contents)

#### [Step 1: Find Which Tests Failed](#table-of-contents)

If the [TestFlows] check does not pass, you should look at the end of the `test_run.txt.out.log` to find the list
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

In this case, the failing test is

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

failed because the first fail gets "bubble-up" the test execution tree all the way to the top-level test which is the
`/clickhouse`.

#### [Step 2: Download `test.log` That Contains All Raw Messages](#table-of-contents)

You need to download the `test.log` that contains all raw messages.

#### [Step 3: Get Messages For The Failing Test](#table-of-contents)

Once you know the name of the failing test, and you have the `test.log` that contains all the raw messages
for all the tests, you can use `tfs show test messages` command. 

> You get the `tfs` command by installing [TestFlows]. 

For example,

```bash
cat test.log | tfs show test messages "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='SELECT', on=\('db0.table0', 'db0.\*', '\*.\*', 'tb0', '\*'\), allow_column=True, allow_introspection=False"
```
> [!NOTE]
> Characters that are treated as special in extended regular expressions need to be escaped. In this case
> we have to escape the `*`, `(`, and the `)` characters in the test name.

#### [Step 4: Working With the `test.log`](#table-of-contents)

You can use the `test.log` with many of the commands provided by the 
`tfs` utility. 

> See `tfs --help` for more information. 

For example, you can get a list of failing tests from the `test.log` using the
`tfs show fails` command as follows

```bash
cat test.log | tfs show fails
```

or get the results using the `tfs show results` command as follows

```bash
cat test.log | tfs show results
```

or you can transform the log to see only the new fails using the
`tfs transform fail --new` command as follows

```bash
cat test.log | tfs transform fails --new
```

### [Running S3 Suites](#table-of-contents)

#### [Minio](#table-of-contents)

Minio is the default test suite, but can be specified using `--storage minio`.

Examples:

Explicit storage declaration:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage minio
```

Utilizing default values:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

You can also specify the minio uri (`--minio-uri`), root user (`--minio-root-user`), and root password (`--minio-root-password`). However, this is not necessary.

#### [AWS S3 Storage](#table-of-contents)

Aws requires a region(`--aws-s3-region`) and a bucket(`--aws-s3-bucket`) (the bucket must end with `/`), in addition to the key id and secret access key.
Aws can be specified using `--storage aws_s3`.

Env variables:
```bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=
export S3_AMAZON_BUCKET=
```

Examples:

Inline:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws_s3_key_id [masked] --aws_s3_access_key [masked] --aws-s3-bucket [masked] --aws-s3-region [masked] --storage aws_s3
```
Env:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage aws_s3
```

#### [GCS (Google Cloud Storage)](#table-of-contents)

GCS requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`), in addition to the s3 key id and secret access key.
GCS can be specified using `--storage gcs`.

Env variables:
```bash
export GCS_URI=
export GCS_KEY_ID=
export GCS_KEY_SECRET=
```

Examples:

Inline:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --storage gcs
```
Env:
```bash
s3/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage gcs
```

### [Running Tiered Storage Suites](#table-of-contents)

#### [Normal](#table-of-contents)

Normal tiered storage suite does not require any variables to be provided.

From the regression directory, it can be run with the following command:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

#### [Running on Minio](#table-of-contents)

Minio tiered storage suite only requires that `--with-minio` is specified.

It can be run with the following command:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-minio
```

#### [Running on AWS S3 Storage](#table-of-contents)

AWS S3 tiered storage requires an access key (`--aws-s3-access-key`), a key id (`--aws-s3-key-id`), and a uri (`--aws-s3-uri`). The uri must end with `/`.
These can be passed as environment variables. AWS S3 must be specified using `--with-s3amazon`.

Env variables:
```bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export S3_AMAZON_URI=
```

Examples:

Inline:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws-s3-key-id [masked] --aws-s3-access-key [masked] --aws-s3-uri [masked] --with-s3amazon
```
Env:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3amazon
```

#### [Running on GCS Storage](#table-of-contents)

GCS tiered storage requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`).
GCS can be specified using `--with-s3gcs`.

Env variables:
```bash
export GCS_URI=
export GCS_KEY_ID=
export GCS_KEY_SECRET=
```

Examples:

Inline:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --with-s3gcs
```
Env:
```bash
tiered_storage/regression.py --local --clickhouse docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3gcs
```

#### [Pausing in Tests](#table-of-contents)

You can explicitly specify `PAUSE_BEFORE`, `PAUSE_AFTER`, `PAUSE_ON_PASS`, and `PAUSE_ON_FAIL` flags inside your test program.
For example,
```python
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

```python
@TestScenario
@Flags(PAUSE_BEFORE|PAUSE_AFTER) # pause before and after this test
def my_scenario(self):
    pass
```
 This can be used for getting access to the [Docker Compose] environment with conditions equal to cluster condition on the current step by executing standard [Docker Compose] commands ("ps", "exec" etc.) from the "*_env" folder. It allows us to make some manual checks/changes on dockers and continue test with new manually set conditions.

## [Running GitHub Actions](#table-of-contents)
To run GitHub actions, navigate to `Actions`, and select `Run CI/CD regression tests`. Inside the `Run workflow` dropdown menu specify the package, version, suite, and upload destination of artifacts.

Package: `docker://` or `https://` package specifier to use for tests. For example: 
* docker://altinity/clickhouse-server
* docker://clickhouse/clickhouse-server
* https://s3.amazonaws.com/altinity-build-artifacts/217/acf34c9fc6932aaf9af69425612070b50529f484/package_release/clickhouse-client_22.8.11.17.altinitystable_amd64.deb
 
Version: Version of clickhouse to use for tests. The test verifies that the node version matches the specified version. When the package option uses the `docker://` specifier then the version is the image tag. For example:
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
[Docker Compose]: https://docs.docker.com/compose/install/standalone/
