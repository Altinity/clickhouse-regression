## [Altinity] ClickHouse Regression Tests

This repository contains [Altinity] ClickHouse regression tests written using [TestFlows].

## Table of Contents

* 1 [Supported Environment](#supported-environment)
* 2 [How to Run Tests](#how-to-run-tests)
* 3 [What is TestFlows](#what-is-testflows)
* 4 [Running Tests Locally](#running-tests-locally)
  * 4.1 [Output Verbosity](#output-verbosity)
  * 4.2 [Running Only Selected Tests](#running-only-selected-tests)
  * 4.3 [Running S3 Suites](#running-s3-suites)
    * 4.3.1 [Minio](#minio)
    * 4.3.2 [AWS S3 Storage](#aws-s3-storage)
    * 4.3.3 [GCS (Google Cloud Storage)](#gcs-google-cloud-storage)
  * 4.4 [Running Tiered Storage Suites](#running-tiered-storage-suites)
    * 4.4.1 [Normal](#normal)
    * 4.4.2 [Running on Minio](#running-on-minio)
    * 4.4.3 [Running on AWS S3 Storage](#running-on-aws-s3-storage)
    * 4.4.4 [Running on GCS Storage](#running-on-gcs-storage)


## Supported Environment

* [Ubuntu] 20.04
* [Python 3] >= 3.8
* [TestFlows] >= 1.9.12

## How to Run Tests

Before running tests you need to install the following:

* [Docker] [install](https://docs.docker.com/engine/install/)
* [Docker Compose] [install](https://docs.docker.com/compose/install/)

To install all necessary Python modules (including [TestFlows]), execute the following command:

```bash
$ pip3 install -r pip_requirements.txt
```

## What is TestFlows

If you are interested to learn about [TestFlows] visit https://testflows.com where you can read the handbook https://testflows.com/handbook/.

## Running Tests Locally

You can run tests locally by passing `--clickhouse-binary-path` to the top level `regression.py` or
`cd` into any sub-folders to run suite specific `regression.py`.

* `--clickhouse-binary-path` specifies the path to the ClickHouse binary on the host machine that will be used during the regression
  run. You can also use docker image that should have `docker://` prefix.

For example, 

```bash
$ ./regression.py --clickhouse-binary-path /usr/bin/clickhouse
```

```bash
$ ./regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

> Note: you can pass `-h` or `--help` argument to the `regression.py` to see a help message.
>
> ```bash
> ./regression.py -h
> ```

> Note: make sure that the ClickHouse binary has correct permissions. 
> If you are using `/usr/bin/clickhouse` its owner and group is set to `root:root` by default 
> and it needs to be changed to `clickhouse:clickhouse`. You can change the owner and the group 
> using the following command:
> 
> ```bash
> sudo chown clickhouse:clickhouse /usr/bin/clickhouse
> ```

Using the default ClickHouse installation and its server binary at `/usr/bin/clickhouse`, you can run 
regressions locally using the following command.

```bash
python3 regression.py --clickhouse-binary-path "/usr/bin/clickhouse"
```

### Output Verbosity

You can control verbosity of the output by specifying the output format with `-o` or `--output` option.
See `--help` for more details.

### Running Only Selected Tests

You can run only the selected tests by passing `--only` option to the `regression.py`.

For example,

```bash
./regression.py --clickhouse-binary-path /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/*"
```

will execute all `rbac/syntax/grant privilege` tests.

If you want to run only a single test such as the `/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('*.*',), allow_introspection=False`,
 you can do it as follows:

```bash
./regression.py --clickhouse-binary-path /usr/bin/clickhouse --only "/clickhouse/rbac/syntax/grant privilege/grant privileges/privilege='KILL QUERY', on=('[*].[*]',), allow_introspection=False/*"
```

> Note that you need to surround special characters such as `*` with square brackets, for example `[*]`.

> Note that you need to end the filtering pattern with `/*` to run all the steps inside the test.

For more information, please see [Filtering](https://testflows.com/handbook/#Filtering) section in the [TestFlows Handbook].

### Running S3 Suites

#### Minio

Minio is the default test suite, but can be specificed using `--storage minio`.

Examples:

Explicit storage declaration:

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage minio
```

Utilizing default values:

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

You can also specify the minio uri (`--minio-uri`), root user (`--minio-root-user`), and root password (`--minio-root-password`). However, this is not necessary.

#### AWS S3 Storage

AWS storage suite requires a region (`--aws-s3-region`) and a bucket (`--aws-s3-bucket`) (the bucket must end with `/`), in addition to the key id and secret access key.
AWS storage can be specified using `--storage aws_s3`.

Environment variables:

```bash
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
$ export AWS_DEFAULT_REGION=
$ export S3_AMAZON_BUCKET=
```

Examples:

Passing AWS parameters on the command line

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws_s3_key_id [masked] --aws_s3_access_key [masked] --aws-s3-bucket [masked] --aws-s3-region [masked] --storage aws_s3
```

Using AWS parameters defined using environment variables

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage aws_s3
```

#### GCS (Google Cloud Storage)

GCS requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`), in addition to the s3 key id and secret access key.
GCS can be specified using `--storage gcs`.

Environment variables:

```bash
$ export GCS_URI=
$ export GCS_KEY_ID=
$ export GCS_KEY_SECRET=
```

Examples:

Passing GCS parameters on the command line:

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --storage gcs
```

Using GCS parameters defined using environment variables:

```bash
$ ./s3/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --storage gcs
```

### Running Tiered Storage Suites

#### Normal

Normal tiered storage suite does not require any variables to be provided.

From the regression directory, it can be run with the following command:

```bash
$ ./tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine
```

#### Running on Minio

Minio tiered storage suite only requires that `--with-minio` is specified.

It can be run with the following command:

```bash
$ ./tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-minio
```

#### Running on AWS S3 Storage

AWS S3 tiered storage requires an access key (`--aws-s3-access-key`), a key id (`--aws-s3-key-id`), and a uri (`--aws-s3-uri`). The uri must end with `/`.
These can be passed as environment variables. AWS S3 must be specified using `--with-s3amazon`.

Environment variables:

```bash
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
$ export S3_AMAZON_URI=
```

Examples:

Passing AWS parameters on the command line:

```bash
$ ./tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --aws-s3-key-id [masked] --aws-s3-access-key [masked] --aws-s3-uri [masked] --with-s3amazon
```

Using AWS parameters defined using environment variables:

```bash
$ ./tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3amazon
```

#### Running on GCS Storage

GCS tiered storage requires a gcs uri (`--gcs-uri`) (the uri must end with `/`), gcs key id (`--gcs-key-id`), and gcs key secret(`--gcs-key-secret`).
GCS can be specified using `--with-s3gcs`.

Environment  variables:

```bash
$ export GCS_URI=
$ export GCS_KEY_ID=
$ export GCS_KEY_SECRET=
```

Examples:

Passing GCS parameters on the command line:

```bash
$ tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --gcs-uri [masked] --gcs-key-id [masked] --gcs-key-secret [masked] --with-s3gcs
```

Using GCS parameters defined using environment variables:

```bash
$ ./tiered_storage/regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.3.6.5-alpine --with-s3gcs
```

[Altinity]: https://altinity.com
[Python 3]: https://www.python.org/
[Ubuntu]: https://ubuntu.com/ 
[TestFlows]: https://testflows.com
[TestFlows Handbook]: https://testflows.com/handbook/
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
