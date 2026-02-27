# Github Actions Utilities and Database

## Scripts

- `setup.sh` installs dependencies and configures runners
- `add_link_to_logs.sh` echos the storage paths of reports and logs for the suite
- `create_and_upload_logs.sh` Converts raw Testflows log to text formats and uploads to S3 and database.
- `upload_results_to_database` Uploads test results to a database.

## Results Database

### Connecting
To connect to the results database, see the instructions for `Clickhouse Regression DB User` in the company vault.
Don't forget that the table is not in the `default` database.

### Useful Query Tricks

Return only suite-level results

```sql
WHERE test_name NOT LIKE '/%/%'
```

Extract suite name from test name

```sql
SELECT splitByChar('/', test_name)[2] as suite
```

Extract run config from report URL

```sql
SELECT splitByString('/testflows/',report_url)[2] AS test_config
```

Extract run identifier from report URL

```sql
SELECT splitByString('thread_fuzzer/', report_url)[2] as job_name
-- or
SELECT splitByString('thread_fuzzer/', test_config)[2] as job_name
```

### Basic Queries

#### All versions tested recently

```sql
SELECT DISTINCT clickhouse_version from clickhouse_regression_results WHERE start_time > today() - INTERVAL 1 WEEK;
```

#### All packages tested recently

```sql
SELECT DISTINCT clickhouse_package from clickhouse_regression_results WHERE start_time > today() - INTERVAL 1 WEEK;
```

### Summary Queries

#### Suites that failed recently, simple version
This offers a quick view of which suites and versions need attention.

```sql
SELECT
    formatDateTime(start_time,
    '%F') AS run_date,
    test_name,
    "result",
    clickhouse_version,
    any(job_url)
FROM
    clickhouse_regression_results
WHERE
    test_name NOT LIKE '/%/%'
    AND "result" != 'OK'
    AND "result" != 'Skip'
    AND start_time > today() - INTERVAL 1 DAY
GROUP BY
    run_date,
    test_name,
    "result",
    clickhouse_version
ORDER BY
    run_date DESC,
    test_name,
    clickhouse_version DESC;
```

#### Suites that failed recently, advanced version
This offers a quick view of which suites and versions need attention.
It uses groupArray to compact the table when used with a desktop client.

```sql
SELECT
    formatDateTime(start_time,
    '%F') AS run_date,
    test_name,
    groupArray("result"),
    groupArray(clickhouse_version),
    groupArray(job_url)
FROM
    clickhouse_regression_results
WHERE
    test_name NOT LIKE '/%/%'
    AND "result" != 'OK'
    AND "result" != 'Skip'
    AND start_time > today() - INTERVAL 1 DAY
GROUP BY
    run_date,
    test_name
ORDER BY
    run_date DESC,
    test_name;
```

#### Counts of recent test fails by suite
Summarize suite stability.

```sql
SELECT
    splitByChar('/',
    test_name)[2] as suite,
    sum(result = 'OK') as OK,
    sum(result = 'Fail') as Fail,
    sum(result = 'XFail') + sum(result = 'XError') as XFail,
    sum(result = 'Skip') as Skip
FROM
    clickhouse_regression_results
WHERE
    start_time > today() - INTERVAL 1 WEEK
GROUP BY
    suite
ORDER BY
    Fail DESC
```

#### Summary of job run times

```sql
SELECT
    splitByString('thread_fuzzer/', report_url)[2] as job_name,
    max(start_time) AS most_recent_start,
    round(median(test_duration_ms) / 3600000,2) AS median_hours
FROM
    clickhouse_regression_results
WHERE
    test_name NOT LIKE '/%/%'
    AND start_time > today() - INTERVAL 2 WEEK
GROUP BY
    job_name
ORDER BY
    job_name
```

#### Details of run times by config and version

```sql
SELECT
    clickhouse_version,
    max(start_time) AS most_recent_start,
    round(median(test_duration_ms) / 3600000,
    2) AS median_hours,
    splitByString('/testflows/',report_url)[2] AS test_config,
    splitByString('thread_fuzzer/', test_config)[2] as job_name
FROM
    clickhouse_regression_results
WHERE
    test_name NOT LIKE '/%/%'
    AND start_time > today() - INTERVAL 2 WEEK
GROUP BY
    test_config, clickhouse_version
ORDER BY
    job_name, test_config
```

### Specific Queries
Edit as required before using

#### Results for a specific test and version
Use to find out when a test started to fail on a given release. Note the use of clickhouse_package instead of clickhouse_version, version is an optional argument and doesn’t exist for the head release.

```sql
SELECT
    clickhouse_version,
    clickhouse_package,
    test_name,
    “result”,
    start_time,
    architecture,
    with_analyzer,
    result_message
FROM
    clickhouse_regression_results
WHERE
    clickhouse_package LIKE '%24.3%'
    AND test_name LIKE '/s3/minio/invalid table function/invalid path'
ORDER BY
    start_time DESC
```

#### Fails for a specific test
This query can help isolate if fails are specific to a version, architecture, or flag.

```sql
SELECT
    clickhouse_version,
    clickhouse_package,
    test_name,
    “result”,
    start_time,
    architecture,
    with_analyzer,
    result_message
FROM
    clickhouse_regression_results
WHERE
    `result` != 'OK'
    AND test_name LIKE '/s3/minio/invalid table function/invalid path'
ORDER BY
    start_time DESC
```
