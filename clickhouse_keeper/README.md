# ClickHouse Keeper

## ClickHouse Keeper and Zookeeper Performance Test Program

Performance tests can be launched with `./perfomance.py` command.
It will start performance tests of all available coordination cluster configurations for local ClickHouse binary. Path 
to default ClickHouse binary is `/usr/bin/clickhouse`. 

*WARNING*:: `chown clickhouse:clickhouse /usr/bin/clickhouse`should be applied to work correctly with the default value.
Also, for clear runs `rm -rf _instances` should be used to delete all docker-compose volumes information.

**Available coordination cluster configurations:**

* ClickHouse Keeper (SSl and non-SSL)
  * mixed one node
  * mixed three node
  * standalone one node 
  * standalone three node
* ZooKeeper (non-SSL)
  * one node 
  * three node

*Example* to test Clickhouse Keeper only for `mixed one node` coordination cluster configuration for vanilla `22.8` ClickHouse version:

```commandline
./perfomance.py --only "/performance/keeper/mixed one node/*" --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

*Example* to test ZooKeeper only for `one node` coordination cluster configuration for vanilla `22.8` ClickHouse version:

```commandline
./perfomance.py --only "/performance/zookeeper/one node/*" --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

*Example* to test ZooKeeper only for `one node` coordination cluster configuration for vanilla `22.8` and `23.3` ClickHouse versions:

```commandline
./perfomance.py --only "/performance/zookeeper/one node/*" --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

Available configurations options for `--only`:

* `"/performance/keeper/mixed one node/*"`
* `"/performance/keeper/mixed three node/*"`
* `"/performance/keeper/standalone one node/*"`
* `"/performance/keeperstandalone three node/*"`
* `"/performance/zookeeper/one node/*"`
* `"/performance/zookeeper/three node/*"`

### Program Settings

* `--inserts` size of insert into table on one repetition (default: 200)
* `--repeats` number of repeats of inserting into the table (default: 4)
* `--one-node` disable all configuration cluster tests which is using 3-node configuration
* `--three-nodes` disable all configuration cluster tests which is using 1-node configuration
* `--results-file-name` allow to provide results file name manually (default: performance_{uid}.csv)
* `--clickhouse-binary-list` to test some special ClickHouse versions, can be applied several times
* `--test-to-end` to force the test program to continue running if any of the tests fail
* `-o classic` to hide additional logs information

*WARNING*: Mostly default values for `repeats` and `inserts` were tested. Some other combinations can put the
table in read only-mode which will lead the program to fail.

**Examples:**

1) The `--clickhouse-binary-list` setting can be applied to test some special ClickHouse versions, as in the example below.

*Example* to test all available coordination cluster with `23.3.5.10.altinitytest` ClickHouse version:
```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --test-to-end -o classic
```

To test more than one version of ClickHouse just add new `--clickhouse-binary-list`:

*Example* to test all available coordination cluster with `23.3.5.10.altinitytest` and vanilla `22.8` ClickHouse versions:

```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

2) The `--inserts` and `--repeats` settings can be applied to change the number of inserts and repeats f inserting into the table.

```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --inserts=10000 --repeats=1 --test-to-end -o classic
```

3) The `--results-file-name` setting can be applied to change the default report file name.

```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --results-file-name results --test-to-end -o classic
```

### Performance Test Scenario

The performance test scenario is based on inserting into a `bad` table (every row generates coordination cluster
transaction). It collects insert times and returns the minimum value. After that, it provides a `performance_reports/
perfomance_*.csv` file which contains a table with percentage increase values of all minimum values for all pairs of 
coordination cluster configurations. Also, it generates additional tables with comparison data:

* SSL vs non-SSL
* Zookeeper vs Keeper
* altinitystable vs all-others

**Table schema:**

```sql
CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name} (p UInt64, x UInt64) ENGINE = ReplicatedSummingMergeTree(
  '/clickhouse/tables/replicated/{shard}/{table_name}', 
  '{replica}'
) 
ORDER BY 
  tuple() PARTITION BY p SETTINGS in_memory_parts_enable_wal = 0, 
  min_bytes_for_wide_part = 104857600, 
  min_bytes_for_wide_part = 104857600, 
  parts_to_delay_insert = 1000000, 
  parts_to_throw_insert = 1000000, 
  max_parts_in_total = 1000000;
```

**Insert query:**

```sql
INSERT INTO {table_name} 
SELECT 
  rand(1)% 100, 
  rand(2) 
FROM 
  numbers({number_of_inserts}) SETTINGS max_block_size = 100, 
  min_insert_block_size_bytes = 1, 
  min_insert_block_size_rows = 1, 
  insert_deduplicate = 0, 
  max_threads = 128, 
  max_insert_threads = 128;
```

### Results Processing

As output, `performance_reports/perfomance_*.csv` file with a unique name will be created. This result file can be 
imported to `Google Sheets`, where `Format-->Conditional formatting-->Color scale` can be applied 
to all numeric cells to receive more readable output.

Color scale setting example:

<img src="readme_data/color_scale_settings.png" alt="color scale settings img">

Final output example:

<img src="readme_data/final_output.png" alt="final output img">

