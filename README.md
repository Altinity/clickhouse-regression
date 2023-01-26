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
* 5 [Running tests locally](#running-tests-locally)
  * 5.1 [Output Verbosity](#output-verbosity)
  * 5.2 [Running Only Selected Tests](#running-only-selected-tests)
  * 5.3 [How To Debug Why Test Failed](#how-to-debug-why-test-failed)
    * 5.3.1 [Step 1: find which tests failed](#step-1-find-which-tests-failed)
    * 5.3.2 [Step 2: download `test.log` that contains all raw messages](#step-2-download-testlog-that-contains-all-raw-messages)
    * 5.3.3 [Step 3: get messages for the failing test](#step-3-get-messages-for-the-failing-test)
    * 5.3.4 [Step 4: working with the `test.log`](#step-4-working-with-the-testlog)
  * 5.4 [Running S3 Suites](#running-s3-suites)
    * 5.4.1 [Minio](#minio)
    * 5.4.2 [AWS S3 Storage](#aws-s3-storage)
    * 5.4.3 [GCS (Google Cloud Storage)](#gcs-google-cloud-storage)
  * 5.5 [Running Tiered Storage Suites](#running-tiered-storage-suites)
    * 5.5.1 [Normal](#normal)
    * 5.5.2 [Running on Minio](#running-on-minio)
    * 5.5.3 [Running on AWS S3 Storage](#running-on-aws-s3-storage)
    * 5.5.4 [Running on GCS Storage](#running-on-gcs-storage)
    * 5.5.5 [Pausing In Tests](#pausing-in-tests)

## Supported environment

* [Ubuntu] 20.04
* [Python 3] >= 3.8
* [TestFlows] >= 1.9.4

## Prerequisites

* [Docker] [install](https://docs.docker.com/engine/install/)
* [Docker Compose] [install](https://docs.docker.com/compose/install/)
* [TestFlows] [install](https://testflows.com/handbook/#Installation) 

To install all necessary Python modules (incl. [TestFlows]), execute the following command:
`pip3 install -r pip_requirements.txt`

## Running CI/CD

### Running Only Specific Suites

Specify `only` variable to select running only specific suites

| Variable | | |
| --- | --- | ---  |
| `only` | `window_functions` | Window Functions suite |
| `only` | `aes_encryption` | AES Encryption Functions suite |
| `only` | `clickhouse_keeper` | ClickHouse Keeper suite |
| `only` | `datetime64_extended_range` | Extended DateTime64 suite |
| `only` | `disk_level_encryption` | Disk Level Encryption |
| `only` | `example` | Example suite |
| `only` | `extended_precision_data_types` | Extended Precision Data Types suite |
| `only` | `kafka` | Kafka suite |
| `only` | `kerberos` | Kerberos suite |
| `only` | `ldap` | LDAP suite |
| `only` | `lightweight_delete` | Lightweight Delete suite |
| `only` | `map_type` | Map Data Type suite |
| `only` | `parquet` | Parquet Data Type suite |
| `only` | `part_moves_between_shards` | Part Moves Between Shards suite |
| `only` | `s3` | All S3 (MinIO, AWS, GCS) suites |
| `only` | `s3_aws` | S3 AWS suite |
| `only` | `s3_gcs` | S3 GCS suite |
| `only` | `ssl_server` | SSL Server suite |
| `only` | `tiered_storage` | All Tiered Storage (Local Disk, MinIO, AWS, GCS) suites |
| `only` | `tiered_storage_aws` | Tiered Storage AWS suite |
| `only` | `tiered_storage_gcs` | Tiered Storage GCS suite |
| `only` | `window_functions` | Window Functions suite |
| `only` | `benchmark` | S3 Benchmak suite |

### Running from Docker image
When running the CI/CD pipeline, provide the following variables:  
Example values using `altinity/clickhouse-server:21.8.15.15.altinitystable`
| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `docker://altinity/clickhouse-server` |
| `Variable` | `version` | `21.8.15.15.altinitystable` |

### Running from Altinity repo
When running the CI/CD pipeline, provide the following variables:

| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `deb://builds.altinity.cloud/apt-repo/pool/main` |
| `Variable` | `version` | The version to use for tests. For example, `21.8.8.1.altinitystable` |

### Running from ClickHouse PR
Get the link to the deb package: PR -> ClickHouse build check (actions) -> Details -> copy link to a deb package.  
Break down the link into CI/CD variables:  
Example values using https://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release/clickhouse-client_22.7.1.1738_amd64.deb
| Variables | | |
| --- | --- | ---  |
| `Variable` | `package` | `deb://s3.amazonaws.com/clickhouse-builds/37882/f74618722585d507cf5fe6d9284cf32028c67716/package_release` NOTE: 'deb' instead of 'https' and no '/' on the end. |
| `Variable` | `version` | `22.7.1.1738` |
| `Variable` | `package_version_postfix` | By default `all` (supports older versions), specify `amd64` for newer PRs where all packages have `amd64` postfix. |

## Running CI/CD with CI/CD trigger
To run the CI/CD pipline you can use cicd-trigger.py
```./cicd-trigger.py```
with following options

```
-w --wait             Wait for pipeline to finish.
--package             Specify docker:// or deb:// package.
--version             Specify clickhouse version.
--package-postfix     Postfix of the clickhouse-server and clickhouse-client deb package.
--only                Select test suite to run.
--output              Tests stdout output style, default: 'classic'. Choices 'nice', 'classic', 'short', etc.
--parallel            Enable or disable running tests in parallel. Choices 'on', 'off'.
--token               Personal access token or private token with api access to the gitlab project, default: 'GITLAB_TOKEN' environment variable.
--options             Extra options that will be added to test run command.
--arch                Architecture to run the tests on, default: 'amd64'.
--branch              Specify which branch to run the tests on, default: 'main'.
--artifacts           Specify whether to upload artifacts internally or publically, default: 'internal'. Bucket for internal upload: 'altinity-internal-test-reports'. Bucket for public upload 'altinity-test-reports'.
```


## Running tests locally

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
### Output Verbosity

You can control verbosity of the output by specifying the output format with `-o` or `--output` option.
See `--help` for more details.

### Running Only Selected Tests

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

### How To Debug Why Test Failed

#### Step 1: find which tests failed

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

#### Step 2: download `test.log` that contains all raw messages

You need to download the `test.log` that contains all raw messages.

#### Step 3: get messages for the failing test

Once you know the name of the failing test and you have the `test.log` that contains all the raw messages
for all the tests, you can use `tfs show test messages` command. 

> You get the `tfs` command by installing [TestFlows]. 

For example,

```bash
cat test.log | tfs show test messages "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='SELECT', on=\('db0.table0', 'db0.\*', '\*.\*', 'tb0', '\*'\), allow_column=True, allow_introspection=False"
```

> Note: that characters that are treated as special in extended regular expressions need to be escaped. In this case
> we have to escape the `*`, `(`, and the `)` characters in the test name.

#### Step 4: working with the `test.log`

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

### Running S3 Suites

#### Minio

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

#### AWS S3 Storage

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

#### GCS (Google Cloud Storage)

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

### Running Tiered Storage Suites

#### Normal

Normal tiered storage suite does not require any variables to be provided.

From the regression directory, it can be run with the following command:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

#### Running on Minio

Minio tiered storage suite only requires that `--with-minio` is specified.

It can be run with the following command:
```bash
$ tiered_storage/regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-minio
```

#### Running on AWS S3 Storage

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

#### Running on GCS Storage

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

#### Pausing In Tests

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


[Python 3]: https://www.python.org/
[Ubuntu]: https://ubuntu.com/ 
[TestFlows]: https://testflows.com
[TestFlows Handbook]: https://testflows.com/handbook/
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
