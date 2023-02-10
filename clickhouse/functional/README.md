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

#### Base configs
Copy configs from ClickHouse/tests/configs to clickhouse-regression/clickhouse/functional/src
```
cp -Lr ClickHouse/tests/config ~/clickhouse-regression/clickhouse/functional/src/
```

#### Functional configs
Copy configs from ClickHouse/tests/configs to clickhouse-regression/clickhouse/functional/src
```
cp -r ClickHouse/programs/server/* ~/clickhouse-regression/clickhouse/configs/clickhouse/
```

### Copy the licence
```
cp ClickHouse/LICENSE ~/clickhouse-regression/clickhouse/functional/src/LICENSE
```
