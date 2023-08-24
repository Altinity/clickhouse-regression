# Parquet Performance

## ClickHouse Performance Test Program

Performance tests can be launched with `./perfomance.py` command. The program will generate a parquet file and run 
a set of queries on it using ClickHouse and DuckDB, collect runtime results from each query and export the 
results into a CSV file. Below you can see a [diagram](#performance-tests-diagram) demonstrating the flow of the process.

Default paths for ClickHouse and Duckdb binaries are `/usr/bin/clickhouse` and `/usr/bin/duckdb`.

*WARNING:* For clear runs `rm -rf _instances` should be used to delete all docker-compose volumes information.


### Performance Tests Diagram
```mermaid
graph TD
    B[Insert dataset from S3 bucket into ClickHouse]
    B --> C[Generate Parquet file]
    C --> D[Run queries on Parquet file using DuckDB]
    C --> E[Run queries on Parquet file using ClickHouse]
    D --> F[Collect runtime results from each query]
    E --> F
    F --> G[Export results into CSV]
```

## Running Tests and Program Settings

### Run Tests

*Example* to run tests on `x86` machine:

```shell
./performance.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:23.7.4.5-alpine --clickhouse-version 23.7.4.5 --duckdb-binary-path https://github.com/duckdb/duckdb/releases/download/v0.8.1/duckdb_cli-linux-amd64.zip 
```

*Example* to run tests on `ARM` machine:

```shell
./performance.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:23.7.4.5-alpine --clickhouse-version 23.7.4.5 --duckdb-binary-path https://github.com/duckdb/duckdb/releases/download/v0.8.1/duckdb_cli-linux-aarch64.zip 
```

### Program Settings

- `--duckdb-binary-path` path to duckdb binary, need to specify duckdb CLI binary download link from [duckdb website](https://duckdb.org/docs/installation/)
- `--from-year` and `--to-year` these settings determine the size of the dataset for the parquet file. (Default values are: from 1987 to 2022, the range results in a parquet file with 200 million rows)
- `--threads` determines the number of threads used in creating a parquet file with large dataset
- `--max-memory-usage` sets the maximum amount of RAM to use for running a query on a single server, 0 sets it to unlimited (values used in bytes)
- `--compression` determines the compression used for a generated parquet file (Default: snappy)
- `--filename` determines the name of the CSV file that contains the results of the test run