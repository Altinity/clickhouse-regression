## ClickHouse stateless and stateful tests

### Copy the clickhouse-test
Copy clickhouse-test from ClickHouse/tests/clickhouse-test to clickhouse-regression/clickhouse/functional/src/clickhouse-test
```
cp ClickHouse/tests/clickhouse-test ~/clickhouse-regression/clickhouse/functional/src/clickhouse-test
```

### Copy the queries folder
Copy queries from ClickHouse/tests/queries to clickhouse-regression/clickhouse/functional/src
```
cp -r ClickHouse/tests/queries ~/clickhouse-regression/clickhouse/functional/src/
```

### Copy the configs
Copy configs from ClickHouse/tests/configs to clickhouse-regression/clickhouse/functional/src
```
cp -r ClickHouse/tests/config ~/clickhouse-regression/clickhouse/functional/src/
```

### Copy the licence
```
cp ClickHouse/LICENSE ~/clickhouse-regression/clickhouse/functional/src/LICENSE
```

### Copy the setup_minio.sh
Copy s3downloader from ClickHouse/docker/test/stateless/setup_minio.sh to clickhouse-regression/clickhouse/functional/src/setup_minio.sh
```
cp ClickHouse/docker/test/stateless/setup_minio.sh ~/clickhouse-regression/clickhouse/functional/src/setup_minio.sh
```

### Copy MOST of the stateless Dockerfile
Using the Dockerfile from ClickHouse/docker/test/stateless/Dockerfile in clickhouse-regression/clickhouse/functional/functional_env/Dockerfile,
but without the `run.sh` to run the tests using testflows instead.