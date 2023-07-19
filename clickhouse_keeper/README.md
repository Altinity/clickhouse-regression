## ClickHouse Keeper/Zookeeper Performance Test Program

Performance tests can be launched with `./perfomance.py` command.
It will start performance tests of all [available coordination cluster]
configurations for local ClickHouse binary. Path to default ClickHouse binary is `/usr/bin/clickhouse`. (warning:
`chown clickhouse:clickhouse /usr/bin/clickhouse` should be applied to work correctly with the default value).

The performance test scenario is based on inserting into a `bad` table (every row generates coordination cluster
transaction). It collects insert times and returns the minimum value. After that, it provides a `performance_reports/
perfomance_*.csv` file which contains a table with [Percentage Increase](https://www.investopedia.com/terms/p/percentage-change.asp) 
values of all minimum values for all pairs of coordination cluster configurations. Also, it generates additional tables with comparison data:

* ssl vs non-ssl
* Zookeeper vs Keeper
* altinitystable vs all-others

Calculation example:

Formula for all tables is `(min_insert_time(row config)  - min_insert_time(column config)) * 100 / min_insert_time(column config)`



| config:  | Keeper   | Zookeeper |
|----------|----------|-----------|
| Keeper   | Result_1 | Result_2  |
| Zookeeper| Result_3 | Result_4  |

 (min_insert_time(Keeper) -  min_insert_time(Keeper)*100/ min_insert_time(Keeper)= Result_1

 (min_insert_time(Zookeeper) -  min_insert_time(Keeper))*100/ min_insert_time(Keeper)= Result_3

 (min_insert_time(Keeper) -  min_insert_time(Zookeeper)*100/ min_insert_time(Zookeeper)= Result_2

 (min_insert_time(Zookeeper) -  min_insert_time(Zookeeper))*100/ min_insert_time(Zookeeper)= Result_4

Table schema:

```commandline
CREATE TABLE IF NOT EXISTS {table_name} on CLUSTER {cluster_name} (p UInt64, x UInt64)
ENGINE = ReplicatedSummingMergeTree('/clickhouse/tables/replicated/{shard}/{table_name}', '{replica}')
ORDER BY tuple() 
PARTITION BY p 
SETTINGS 
 in_memory_parts_enable_wal=0,
 min_bytes_for_wide_part=104857600, 
 min_bytes_for_wide_part=104857600, 
 parts_to_delay_insert=1000000, 
 parts_to_throw_insert=1000000, 
 max_parts_in_total=1000000;
```

Insert query:

```commandline
INSERT INTO {table_name} SELECT rand(1)%100, rand(2) FROM numbers({number_of_inserts}) 
SETTINGS max_block_size=100, min_insert_block_size_bytes=1, min_insert_block_size_rows=1, 
insert_deduplicate=0, max_threads=128,max_insert_threads=128;
```

The program is based on [TestFlows](https://testflows.com/) framework. So `perfomance.py` can use all its
[possibilities](https://testflows.com/handbook/) (except `--clickhouse-binary-path`)

Most usefully are:

* `--test-to-end` to force the test program to continue running if any of the tests fail
* `-o classic` to hide additional logs information
* `--only "/coordination cluster/performance keeper/{available_coordination_cluster_configurations}/*"` to test only one of 
[available coordination cluster] configurations


Special `perfomance.py` settings are:

* `--clickhouse-binary-list` to test some special ClickHouse versions
* `--repeats` number of insert each tests scenario repeats (default: 4)
* `--inserts` number of inserts into table on one repeat (default: 200)
* `--one-node` disable all three nodes configuration cluster tests
* `--three-nodes` disable all one node configuration cluster tests
* `--results-file-name` allow to provide results file name manually (default: performance_{uid}.csv)

Mostly default values for `repeats` and `inserts` were tested, and they are stable. Some other combinations can put the
table in read only-mode that will interrupt the program run.

As output, `performance_reports/perfomance_*.csv` file with a unique name will be created. This result file can be 
imported to `Google Sheets`, where `Format-->Conditional formatting-->Color scale` can be applied 
to all numeric cells to receive more readable output.

Color scale setting example:

<img src="readme_data/color_scale_settings.png" alt="color scale settings img">

Final output example:

<img src="readme_data/final_output.png" alt="final output img">

### Examples

1) The `--clickhouse-binary-list` setting can be applied to test some special ClickHouse versions, as in the example below.

Example to test all [available coordination cluster] with `23.3.5.10.altinitytest` ClickHouse version:
```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --test-to-end -o classic
```

To test more than one version of ClickHouse just add new `--clickhouse-binary-list`:

Example to test all [available coordination cluster] with `23.3.5.10.altinitytest` and vanilla `22.8` ClickHouse versions:

```commandline
./perfomance.py --clickhouse-binary-list=docker://altinity/clickhouse-server:23.3.5.10.altinitytest --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

2) To test the only one coordination cluster configuration `--only` setting can be added.

Example to test Clickhouse Keeper `mixed one node` coordination cluster configuration for vanilla `22.8` ClickHouse version:

```commandline
./perfomance.py --only "/performance/keeper/mixed one node/*" --clickhouse-binary-list=docker://clickhouse/clickhouse-server:22.8 --test-to-end -o classic
```

Available options for `--only`:

* `"/performance/keeper/mixed one node/*"`
* `"/performance/keeper/mixed three node/*"`
* `"/performance/keeper/standalone one node/*"`
* `"/performance/keeperstandalone three node/*"`
* `"/performance/zookeeper/one node/*"`
* `"/performance/zookeeper/three node/*"`


# Available Coordination Clusters

Available coordination cluster configurations:

* ClickHouse Keeper
  * mixed one node (ssl/ non-ssl)
  * mixed three node (ssl/ non-ssl)
  * standalone one node (ssl/ non-ssl)
  * standalone three node (ssl/ non-ssl)
* ZooKeeper
  * one node (non-ssl)
  * three node (non-ssl)

[available coordination cluster]: #available-coordination-clusters