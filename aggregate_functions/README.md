# ClickHouse Aggregate Functions Compatibility Tests

These tests are related to aggregate functions compatibility.

`compatibility.py`:

This test is related to issue https://github.com/ClickHouse/ClickHouse/issues/42916
and PR https://github.com/ClickHouse/ClickHouse/pull/43038 that fixes it.

This test checks the compatibility of the following functions:

* argMax
* argMin
* max
* min
* any
* singleValueOrNull

To run it, use:

`./regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.8.5.29 docker://clickhouse/clickhouse-server:22.8.6.71 https://s3.amazonaws.com/clickhouse-builds/43485/892762d482b8cc6a2ca9ae8ef8997d518ee89597/package_release/clickhouse-common-static_22.8.10.7_amd64.deb --only "/aggregate functions/compatibility/*"`

Where `docker://clickhouse/clickhouse-server:22.8.5.29` is a non-affected version,

`docker://clickhouse/clickhouse-server:22.8.6.71` is an affected version,

`https://s3.amazonaws.com/clickhouse-builds/43485/892762d482b8cc6a2ca9ae8ef8997d518ee89597/package_release/clickhouse-common-static_22.8.10.7_amd64.deb` is a version with a fix.


`compatibility_inf_nan.py`:

This test is related to broken compatibility of the following functions with inf and nan in argument:

* corrStableState
* covarPopStableState
* covarSampStableState

To run it, use:

`./regression.py --clickhouse-binary-path docker://clickhouse/clickhouse-server:22.7.1.2484 docker://clickhouse/clickhouse-server:22.8.9.24 --only "/aggregate functions/compatibility inf nan/*"`

Where `docker://clickhouse/clickhouse-server:22.7.1.2484` is a non-affected version,

`docker://clickhouse/clickhouse-server:22.8.9.24` is a version with a fix.

