# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_HivePartitioning_Generic_Support = Requirement(
    name='RQ.HivePartitioning.Generic.Support',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form name=value) as virtual columns when accessing external data sources. This enables querying partitioned data without manual parsing of file paths.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.1.1'
)

RQ_HivePartitioning_Generic_EnableSetting = Requirement(
    name='RQ.HivePartitioning.Generic.EnableSetting',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL use support setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.1.2'
)

RQ_HivePartitioning_Generic_Pruning = Requirement(
    name='RQ.HivePartitioning.Generic.Pruning',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL only read the files from the partitions that satisfy filters when Hive-style partitioning is enabled and queries include filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.1.3'
)

RQ_HivePartitioning_Generic_Performance = Requirement(
    name='RQ.HivePartitioning.Generic.Performance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL execute queries with `use_hive_partitioning=1` faster than queries with `use_hive_partitioning=0` if some files from storage are pruned with `WHERE` clause.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.1.4'
)

RQ_HivePartitioning_VirtualColumns_Generic = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.Generic',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[Clickhouse] SHALL create virtual column for each partition key present in the file path with the same name as the partition key. \n'
        '\n'
        'For example, given a path segment /city=London/, a virtual column city will be provided with value "London" for all rows read from that directory.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.1'
)

RQ_HivePartitioning_VirtualColumns_ReadOnly = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.ReadOnly',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Virtual columns created by hive partitioning SHALL be read-only.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.2'
)

RQ_HivePartitioning_VirtualColumns_Appearance = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.Appearance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Virtual columns created by hive partitioning SHALL not appear in query output, when query does not select this queries.\n'
        '\n'
        'For example:\n'
        '`SELECT *` \n'
        'This query SHALL not return virtual columns.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.3'
)

RQ_HivePartitioning_VirtualColumns_Accessability = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.Accessability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Virtual columns created by hive partitioning SHALL be accessible in queries.\n'
        '\n'
        'For example:\n'
        "`SELECT date FROM s3(...) WHERE date='01-01-2020'`\n"
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.4'
)

RQ_HivePartitioning_VirtualColumns_InvalidPath = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.InvalidPath',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if path defined in query is invalid or storage does not contain defined files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.5'
)

RQ_HivePartitioning_VirtualColumns_NameConflict = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.NameConflict',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL not use virtual column if name of the virtual column matches with the name of table column.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.6'
)

RQ_HivePartitioning_VirtualColumns_HiveDisabled = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.HiveDisabled',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[Clickhouse] SHALL not create virtual column if `use_hive_partitioning` setting is disabled.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.7'
)

RQ_HivePartitioning_VirtualColumns_NonExistingKey = Requirement(
    name='RQ.HivePartitioning.VirtualColumns.NonExistingKey',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[Clickhouse] SHALL return `Unknown identifier` error if query refers to nonexisting partition key.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.2.8'
)

RQ_HivePartitioning_HivePartitionTypes_Generic = Requirement(
    name='RQ.HivePartitioning.HivePartitionTypes.Generic',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Partition values extracted from paths SHALL be treated as strings with no implicit type inference.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.3.1'
)

RQ_HivePartitioning_HivePartitionTypes_DefaultType = Requirement(
    name='RQ.HivePartitioning.HivePartitionTypes.DefaultType',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'Partition values extracted from paths SHALL have `LowCardinality(String)` type.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.3.2'
)

RQ_HivePartitioning_HivePartitionTypes_EmptyValue = Requirement(
    name='RQ.HivePartitioning.HivePartitionTypes.EmptyValue',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'The hive value SHALL be empty string if directory is missing a key.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.3.3'
)

RQ_HivePartitioning_Wildcards_Generic = Requirement(
    name='RQ.HivePartitioning.Wildcards.Generic',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support glob-style wildcards for hive partitioning.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.1'
)

RQ_HivePartitioning_Wildcards_SingleStar = Requirement(
    name='RQ.HivePartitioning.Wildcards.SingleStar',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `*` wildcard for hive partitioning. `*` wildcard SHALL match any sequence of characters except `/`.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.2'
)

RQ_HivePartitioning_Wildcards_DoubleStart = Requirement(
    name='RQ.HivePartitioning.Wildcards.DoubleStart',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `**` wildcard for hive partitioning. `**` wildcard SHALL match any sequence of characters including `/`.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.3'
)

RQ_HivePartitioning_Wildcards_QuestionMark = Requirement(
    name='RQ.HivePartitioning.Wildcards.QuestionMark',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `?` wildcard for hive partitioning. `?` wildcard SHALL match a single character except `/`.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.4'
)

RQ_HivePartitioning_Wildcards_List = Requirement(
    name='RQ.HivePartitioning.Wildcards.List',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `{a[, b][, c]...}` wildcard for hive partitioning. `{a[, b][, c]...}` wildcard SHALL match one of the listed options.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.5'
)

RQ_HivePartitioning_Wildcards_WrongList = Requirement(
    name='RQ.HivePartitioning.Wildcards.WrongList',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if one or more options in `{a[, b][, c]...}` are invalid or path does not exists.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.6'
)

RQ_HivePartitioning_Wildcards_Range = Requirement(
    name='RQ.HivePartitioning.Wildcards.Range',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `{N..M}` wildcard for hive partitioning. `{N..M}` wildcard SHALL match numbers in a range.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.7'
)

RQ_HivePartitioning_Wildcards_WrongRange = Requirement(
    name='RQ.HivePartitioning.Wildcards.WrongRange',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if one or more options in `{N..M}` are invalid or path does not exists.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.4.8'
)

RQ_HivePartitioning_TableFunction_S3 = Requirement(
    name='RQ.HivePartitioning.TableFunction.S3',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'The [s3] table function SHALL support Hive-style partitions for reading in the provided URL path. If the S3 path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions. For example, a query:\n'
        '\n'
        '```SQL\n'
        'SET use_hive_partitioning = 1;\n'
        'SELECT COUNT(*) \n'
        "FROM s3('s3://bucket/data/date=*/country=*/*.parquet', 'Parquet') \n"
        "WHERE country = 'Netherlands' AND date >= '2020-01-01';\n"
        '```\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.5.1'
)

RQ_HivePartitioning_TableFunction_S3Cluster = Requirement(
    name='RQ.HivePartitioning.TableFunction.S3Cluster',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'The [s3Cluster] table function SHALL equally support Hive-style partitioning for reading across a cluster. On each cluster node, the function SHALL interpret partition directories and prune files in the same manner as a local [s3] call. This ensures distributed querying of an S3-partitioned dataset is consistent and efficient, reading only the necessary partitions on each node.\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.5.2'
)

RQ_HivePartitioning_TableFunction_HDFS = Requirement(
    name='RQ.HivePartitioning.TableFunction.HDFS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'The [HDFS] table function SHALL support Hive-style partitions for reading in the provided URL path. If the path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions.\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='2.5.3'
)

RQ_HivePartitioning_TableEngines_S3 = Requirement(
    name='RQ.HivePartitioning.TableEngines.S3',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading from S3 table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.\n'
        '\n'
        '```SQL\n'
        'CREATE TABLE s3_engine_table(x Int64)\n'
        'ENGINE = S3(...)\n'
        'PARTITION BY date\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.6.1.1'
)

RQ_HivePartitioning_TableEngines_HDFS = Requirement(
    name='RQ.HivePartitioning.TableEngines.HDFS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading from HDFS table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.\n'
        '\n'
        '```SQL\n'
        'CREATE TABLE hdfs_sales(x Int64)\n'
        'ENGINE = HDFS(\n'
        "    'hdfs:///data/{date}/file.parquet', \n"
        "    'Parquet'\n"
        ')\n'
        'PARTITION BY date\n'
        '```\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.6.2.1'
)

RQ_HivePartitioning_TableEngines_Hive = Requirement(
    name='RQ.HivePartitioning.TableEngines.Hive',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading from Hive table engine with hive partitioning. Hive partitioning columns SHALL be defined in Hive Metastore.\n'
        '\n'
        '```SQL\n'
        'CREATE TABLE hive_table(x Int64)\n'
        'ENGINE = Hive(...) \n'
        '```\n'
        '\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.6.3.1'
)

RQ_HivePartitioning_HivePartitionWrites_S3 = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.S3',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support hive-style partition writes by using S3 table engine.\n'
        '\n'
        '\n'
        'For example:\n'
        '```SQL\n'
        'CREATE TABLE hive_writes(year UInt16, country String, x UInt8)\n'
        "ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy='hive')\n"
        'PARTITION BY (year, country);\n'
        '\n'
        'INSERT INTO hive_writes VALUES\n'
        "    (2022, 'USA', 1),\n"
        "    (2022, 'Canada', 2);\n"
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.1'
)

RQ_HivePartitioning_HivePartitionWrites_WrongEngine = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.WrongEngine',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if user tries to insert using hive-style partitions into table with not S3 Engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.2'
)

RQ_HivePartitioning_HivePartitionWrites_FileExist = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.FileExist',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL properly add data to the file if file already exists. This operation SHALL not delete or overwrite existing data.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.3'
)

RQ_HivePartitioning_HivePartitionWrites_MissingColumn = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.MissingColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if columns defined in the `PARTITION BY` clause is missing.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.4'
)

RQ_HivePartitioning_HivePartitionWrites_NullInColumn = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.NullInColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if columns defined in the `PARTITION BY` clause contains Null.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.5'
)

RQ_HivePartitioning_HivePartitionWrites_UnsupportedTypes = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if type of the column defined in the `PARTITION BY` clause can't be casted into string.\n"
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.6'
)

RQ_HivePartitioning_HivePartitionWrites_ReadOnlyBucket = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is read-only.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.7'
)

RQ_HivePartitioning_HivePartitionWrites_NonAccessibleBucket = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is not accessible.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.8'
)

RQ_HivePartitioning_HivePartitionWrites_ParallelInserts = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.ParallelInserts',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support parallel inserts into one file.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.9'
)

RQ_HivePartitioning_HivePartitionWrites_WriteFail = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.WriteFail',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL fail the insert and SHALL not leave partial data if any object write fails.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.1.10'
)

RQ_HivePartitioning_HivePartitionWrites_PartitionBy = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.PartitionBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL perform hive partition writes only if table engine definition contains `PARTITION BY` clause.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.2.1'
)

RQ_HivePartitioning_HivePartitionWrites_MissingPartitionBy = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if user tries to insert into table with S3 table engine without `PARTITION BY` clause.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.2.2'
)

RQ_HivePartitioning_HivePartitionWrites_PartitionKey = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.PartitionKey',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL create path containing {/key=value/} for all columns defined in `PARTITION BY` clause and file on this path on insert, if file does not exists.\n'
        'Inserted data SHALL be located in this file.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.2.3'
)

RQ_HivePartitioning_HivePartitionWritesSyntax_Generic = Requirement(
    name='RQ.HivePartitioning.HivePartitionWritesSyntax.Generic',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        'S3 table Engine SHALL have the following syntax:\n'
        '\n'
        '```SQL\n'
        'ENGINE = S3(path [, NOSIGN | aws_access_key_id, aws_secret_access_key,] format[, compression][, filename][, partition_stratagy][, hive_partition_strategy_write_partition_columns_into_files])\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.3.1'
)

RQ_HivePartitioning_HivePartitionWrites_PartitionStratagy = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `partition_stratagy` parameter for S3 engine that SHALL define if [ClickHouse] enables hive partition writes or no.\n'
        "[ClickHouse] SHALL support 'hive' and 'auto' values for this parameter. [ClickHouse] SHALL enable hive partition writes if it is set to 'hive' and disable if it is set to 'auto'.\n"
        "`partition_stratagy` SHALL be 'auto' by default.\n"
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.4.1'
)

RQ_HivePartitioning_HivePartitionWrites_PartitionStratagyWrongArgument = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `partition_stratagy` parameter neither set to 'auto' and 'hive'.\n"
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.4.2'
)

RQ_HivePartitioning_HivePartitionWrites_HivePartitionStrategyWritePartitionColumnsIntoFiles = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `hive_partition_strategy_write_partition_columns_into_files` parameter for S3 engine that SHALL define if [ClickHouse] writes partition columns into files or not.\n'
        '`hive_partition_strategy_write_partition_columns_into_files` SHALL be False by default.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.4.4'
)

RQ_HivePartitioning_HivePartitionWrites_HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if `hive_partition_strategy_write_partition_columns_into_files` parameter gets argument that cannot be casted to boolean.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.4.5'
)

RQ_HivePartitioning_HivePartitionWrites_Path = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.Path',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `path` parameter that defines path to the bucket for hive partition writes.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.5.1'
)

RQ_HivePartitioning_HivePartitionWrites_InvalidPath = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.InvalidPath',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if defined `path` is invalid or `path` points to a file with `partition_stratagy='hive'`.\n"
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.5.2'
)

RQ_HivePartitioning_HivePartitionWrites_Filename = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.Filename',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `filename` parameter that defines filename for hive partition writes.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.6.1'
)

RQ_HivePartitioning_HivePartitionWrites_InvalidFilename = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.InvalidFilename',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL return an error if defined `filename` is invalid or points to a directory.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.6.2'
)

RQ_HivePartitioning_HivePartitionWrites_NotDefinedFilename = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if defined `filename` parameter is not defined but `partition_stratagy` is set to 'hive'.\n"
        '\n'
    ),
    link=None,
    level=4,
    num='2.7.6.3'
)

RQ_HivePartitioning_HivePartitionWrites_S3EngineParameters = Requirement(
    name='RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not change behavior of the following parameters if `partition_stratagy` is set to 'hive':\n"
        '`aws_access_key_id`, `aws_secret_access_key`, `format`, `compression`.\n'
        '\n'
        '\n'
        '\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3\n'
        '[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster\n'
        '[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs\n'
    ),
    link=None,
    level=4,
    num='2.7.7.1'
)

SRS_045_Hive_Partitioning = Specification(
    name='SRS-045 Hive Partitioning',
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name='Introduction', level=1, num='1'),
        Heading(name='Requirements', level=1, num='2'),
        Heading(name='Generic Behavior', level=2, num='2.1'),
        Heading(name='RQ.HivePartitioning.Generic.Support', level=3, num='2.1.1'),
        Heading(name='RQ.HivePartitioning.Generic.EnableSetting', level=3, num='2.1.2'),
        Heading(name='RQ.HivePartitioning.Generic.Pruning', level=3, num='2.1.3'),
        Heading(name='RQ.HivePartitioning.Generic.Performance', level=3, num='2.1.4'),
        Heading(name='Virtual Columns', level=2, num='2.2'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.Generic', level=3, num='2.2.1'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.ReadOnly', level=3, num='2.2.2'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.Appearance', level=3, num='2.2.3'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.Accessability', level=3, num='2.2.4'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.InvalidPath', level=3, num='2.2.5'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.NameConflict', level=3, num='2.2.6'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.HiveDisabled', level=3, num='2.2.7'),
        Heading(name='RQ.HivePartitioning.VirtualColumns.NonExistingKey', level=3, num='2.2.8'),
        Heading(name='Hive Partition Types', level=2, num='2.3'),
        Heading(name='RQ.HivePartitioning.HivePartitionTypes.Generic', level=3, num='2.3.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionTypes.DefaultType', level=3, num='2.3.2'),
        Heading(name='RQ.HivePartitioning.HivePartitionTypes.EmptyValue', level=3, num='2.3.3'),
        Heading(name='Wildcards', level=2, num='2.4'),
        Heading(name='RQ.HivePartitioning.Wildcards.Generic', level=3, num='2.4.1'),
        Heading(name='RQ.HivePartitioning.Wildcards.SingleStar', level=3, num='2.4.2'),
        Heading(name='RQ.HivePartitioning.Wildcards.DoubleStart', level=3, num='2.4.3'),
        Heading(name='RQ.HivePartitioning.Wildcards.QuestionMark', level=3, num='2.4.4'),
        Heading(name='RQ.HivePartitioning.Wildcards.List', level=3, num='2.4.5'),
        Heading(name='RQ.HivePartitioning.Wildcards.WrongList', level=3, num='2.4.6'),
        Heading(name='RQ.HivePartitioning.Wildcards.Range', level=3, num='2.4.7'),
        Heading(name='RQ.HivePartitioning.Wildcards.WrongRange', level=3, num='2.4.8'),
        Heading(name='Supported Table Functions', level=2, num='2.5'),
        Heading(name='RQ.HivePartitioning.TableFunction.S3', level=3, num='2.5.1'),
        Heading(name='RQ.HivePartitioning.TableFunction.S3Cluster', level=3, num='2.5.2'),
        Heading(name='RQ.HivePartitioning.TableFunction.HDFS', level=3, num='2.5.3'),
        Heading(name='Supported Table Engines', level=2, num='2.6'),
        Heading(name='S3 Table Engine', level=3, num='2.6.1'),
        Heading(name='RQ.HivePartitioning.TableEngines.S3', level=4, num='2.6.1.1'),
        Heading(name='HDFS Table Engine', level=3, num='2.6.2'),
        Heading(name='RQ.HivePartitioning.TableEngines.HDFS', level=4, num='2.6.2.1'),
        Heading(name='Hive Table Engine', level=3, num='2.6.3'),
        Heading(name='RQ.HivePartitioning.TableEngines.Hive', level=4, num='2.6.3.1'),
        Heading(name='Hive Partition Writes', level=2, num='2.7'),
        Heading(name='Generic', level=3, num='2.7.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.S3', level=4, num='2.7.1.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.WrongEngine', level=4, num='2.7.1.2'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.FileExist', level=4, num='2.7.1.3'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.MissingColumn', level=4, num='2.7.1.4'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.NullInColumn', level=4, num='2.7.1.5'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes', level=4, num='2.7.1.6'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket', level=4, num='2.7.1.7'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket', level=4, num='2.7.1.8'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.ParallelInserts', level=4, num='2.7.1.9'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.WriteFail', level=4, num='2.7.1.10'),
        Heading(name='Partition By Clause For S3 Engine With Hive Partition Writes', level=3, num='2.7.2'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.PartitionBy', level=4, num='2.7.2.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy', level=4, num='2.7.2.2'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.PartitionKey', level=4, num='2.7.2.3'),
        Heading(name='Hive Partition Writes Syntax', level=3, num='2.7.3'),
        Heading(name='RQ.HivePartitioning.HivePartitionWritesSyntax.Generic', level=4, num='2.7.3.1'),
        Heading(name='Partition Stratagy Parameter', level=3, num='2.7.4'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy', level=4, num='2.7.4.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument', level=4, num='2.7.4.2'),
        Heading(name='Hive Partition Strategy Write Partition Columns Into Files Parameter', level=4, num='2.7.4.3'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles', level=4, num='2.7.4.4'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument', level=4, num='2.7.4.5'),
        Heading(name='Path Parameter', level=3, num='2.7.5'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.Path', level=4, num='2.7.5.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.InvalidPath', level=4, num='2.7.5.2'),
        Heading(name='Filename Parameter', level=3, num='2.7.6'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.Filename', level=4, num='2.7.6.1'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.InvalidFilename', level=4, num='2.7.6.2'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename', level=4, num='2.7.6.3'),
        Heading(name='S3 Engine Parameters', level=3, num='2.7.7'),
        Heading(name='RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters', level=4, num='2.7.7.1'),
        ),
    requirements=(
        RQ_HivePartitioning_Generic_Support,
        RQ_HivePartitioning_Generic_EnableSetting,
        RQ_HivePartitioning_Generic_Pruning,
        RQ_HivePartitioning_Generic_Performance,
        RQ_HivePartitioning_VirtualColumns_Generic,
        RQ_HivePartitioning_VirtualColumns_ReadOnly,
        RQ_HivePartitioning_VirtualColumns_Appearance,
        RQ_HivePartitioning_VirtualColumns_Accessability,
        RQ_HivePartitioning_VirtualColumns_InvalidPath,
        RQ_HivePartitioning_VirtualColumns_NameConflict,
        RQ_HivePartitioning_VirtualColumns_HiveDisabled,
        RQ_HivePartitioning_VirtualColumns_NonExistingKey,
        RQ_HivePartitioning_HivePartitionTypes_Generic,
        RQ_HivePartitioning_HivePartitionTypes_DefaultType,
        RQ_HivePartitioning_HivePartitionTypes_EmptyValue,
        RQ_HivePartitioning_Wildcards_Generic,
        RQ_HivePartitioning_Wildcards_SingleStar,
        RQ_HivePartitioning_Wildcards_DoubleStart,
        RQ_HivePartitioning_Wildcards_QuestionMark,
        RQ_HivePartitioning_Wildcards_List,
        RQ_HivePartitioning_Wildcards_WrongList,
        RQ_HivePartitioning_Wildcards_Range,
        RQ_HivePartitioning_Wildcards_WrongRange,
        RQ_HivePartitioning_TableFunction_S3,
        RQ_HivePartitioning_TableFunction_S3Cluster,
        RQ_HivePartitioning_TableFunction_HDFS,
        RQ_HivePartitioning_TableEngines_S3,
        RQ_HivePartitioning_TableEngines_HDFS,
        RQ_HivePartitioning_TableEngines_Hive,
        RQ_HivePartitioning_HivePartitionWrites_S3,
        RQ_HivePartitioning_HivePartitionWrites_WrongEngine,
        RQ_HivePartitioning_HivePartitionWrites_FileExist,
        RQ_HivePartitioning_HivePartitionWrites_MissingColumn,
        RQ_HivePartitioning_HivePartitionWrites_NullInColumn,
        RQ_HivePartitioning_HivePartitionWrites_UnsupportedTypes,
        RQ_HivePartitioning_HivePartitionWrites_ReadOnlyBucket,
        RQ_HivePartitioning_HivePartitionWrites_NonAccessibleBucket,
        RQ_HivePartitioning_HivePartitionWrites_ParallelInserts,
        RQ_HivePartitioning_HivePartitionWrites_WriteFail,
        RQ_HivePartitioning_HivePartitionWrites_PartitionBy,
        RQ_HivePartitioning_HivePartitionWrites_MissingPartitionBy,
        RQ_HivePartitioning_HivePartitionWrites_PartitionKey,
        RQ_HivePartitioning_HivePartitionWritesSyntax_Generic,
        RQ_HivePartitioning_HivePartitionWrites_PartitionStratagy,
        RQ_HivePartitioning_HivePartitionWrites_PartitionStratagyWrongArgument,
        RQ_HivePartitioning_HivePartitionWrites_HivePartitionStrategyWritePartitionColumnsIntoFiles,
        RQ_HivePartitioning_HivePartitionWrites_HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument,
        RQ_HivePartitioning_HivePartitionWrites_Path,
        RQ_HivePartitioning_HivePartitionWrites_InvalidPath,
        RQ_HivePartitioning_HivePartitionWrites_Filename,
        RQ_HivePartitioning_HivePartitionWrites_InvalidFilename,
        RQ_HivePartitioning_HivePartitionWrites_NotDefinedFilename,
        RQ_HivePartitioning_HivePartitionWrites_S3EngineParameters,
        ),
    content=r'''
# SRS-045 Hive Partitioning
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Requirements](#requirements)
    * 2.1 [Generic Behavior](#generic-behavior)
        * 2.1.1 [RQ.HivePartitioning.Generic.Support](#rqhivepartitioninggenericsupport)
        * 2.1.2 [RQ.HivePartitioning.Generic.EnableSetting](#rqhivepartitioninggenericenablesetting)
        * 2.1.3 [RQ.HivePartitioning.Generic.Pruning](#rqhivepartitioninggenericpruning)
        * 2.1.4 [RQ.HivePartitioning.Generic.Performance](#rqhivepartitioninggenericperformance)
    * 2.2 [Virtual Columns](#virtual-columns)
        * 2.2.1 [RQ.HivePartitioning.VirtualColumns.Generic](#rqhivepartitioningvirtualcolumnsgeneric)
        * 2.2.2 [RQ.HivePartitioning.VirtualColumns.ReadOnly](#rqhivepartitioningvirtualcolumnsreadonly)
        * 2.2.3 [RQ.HivePartitioning.VirtualColumns.Appearance](#rqhivepartitioningvirtualcolumnsappearance)
        * 2.2.4 [RQ.HivePartitioning.VirtualColumns.Accessability](#rqhivepartitioningvirtualcolumnsaccessability)
        * 2.2.5 [RQ.HivePartitioning.VirtualColumns.InvalidPath](#rqhivepartitioningvirtualcolumnsinvalidpath)
        * 2.2.6 [RQ.HivePartitioning.VirtualColumns.NameConflict](#rqhivepartitioningvirtualcolumnsnameconflict)
        * 2.2.7 [RQ.HivePartitioning.VirtualColumns.HiveDisabled](#rqhivepartitioningvirtualcolumnshivedisabled)
        * 2.2.8 [RQ.HivePartitioning.VirtualColumns.NonExistingKey](#rqhivepartitioningvirtualcolumnsnonexistingkey)
    * 2.3 [Hive Partition Types](#hive-partition-types)
        * 2.3.1 [RQ.HivePartitioning.HivePartitionTypes.Generic](#rqhivepartitioninghivepartitiontypesgeneric)
        * 2.3.2 [RQ.HivePartitioning.HivePartitionTypes.DefaultType](#rqhivepartitioninghivepartitiontypesdefaulttype)
        * 2.3.3 [RQ.HivePartitioning.HivePartitionTypes.EmptyValue](#rqhivepartitioninghivepartitiontypesemptyvalue)
    * 2.4 [Wildcards](#wildcards)
        * 2.4.1 [RQ.HivePartitioning.Wildcards.Generic](#rqhivepartitioningwildcardsgeneric)
        * 2.4.2 [RQ.HivePartitioning.Wildcards.SingleStar](#rqhivepartitioningwildcardssinglestar)
        * 2.4.3 [RQ.HivePartitioning.Wildcards.DoubleStart](#rqhivepartitioningwildcardsdoublestart)
        * 2.4.4 [RQ.HivePartitioning.Wildcards.QuestionMark](#rqhivepartitioningwildcardsquestionmark)
        * 2.4.5 [RQ.HivePartitioning.Wildcards.List](#rqhivepartitioningwildcardslist)
        * 2.4.6 [RQ.HivePartitioning.Wildcards.WrongList](#rqhivepartitioningwildcardswronglist)
        * 2.4.7 [RQ.HivePartitioning.Wildcards.Range](#rqhivepartitioningwildcardsrange)
        * 2.4.8 [RQ.HivePartitioning.Wildcards.WrongRange](#rqhivepartitioningwildcardswrongrange)
    * 2.5 [Supported Table Functions](#supported-table-functions)
        * 2.5.1 [RQ.HivePartitioning.TableFunction.S3](#rqhivepartitioningtablefunctions3)
        * 2.5.2 [RQ.HivePartitioning.TableFunction.S3Cluster](#rqhivepartitioningtablefunctions3cluster)
        * 2.5.3 [RQ.HivePartitioning.TableFunction.HDFS](#rqhivepartitioningtablefunctionhdfs)
    * 2.6 [Supported Table Engines](#supported-table-engines)
        * 2.6.1 [S3 Table Engine](#s3-table-engine)
            * 2.6.1.1 [RQ.HivePartitioning.TableEngines.S3](#rqhivepartitioningtableenginess3)
        * 2.6.2 [HDFS Table Engine](#hdfs-table-engine)
            * 2.6.2.1 [RQ.HivePartitioning.TableEngines.HDFS](#rqhivepartitioningtableengineshdfs)
        * 2.6.3 [Hive Table Engine](#hive-table-engine)
            * 2.6.3.1 [RQ.HivePartitioning.TableEngines.Hive](#rqhivepartitioningtableengineshive)
    * 2.7 [Hive Partition Writes](#hive-partition-writes)
        * 2.7.1 [Generic](#generic)
            * 2.7.1.1 [RQ.HivePartitioning.HivePartitionWrites.S3](#rqhivepartitioninghivepartitionwritess3)
            * 2.7.1.2 [RQ.HivePartitioning.HivePartitionWrites.WrongEngine](#rqhivepartitioninghivepartitionwriteswrongengine)
            * 2.7.1.3 [RQ.HivePartitioning.HivePartitionWrites.FileExist](#rqhivepartitioninghivepartitionwritesfileexist)
            * 2.7.1.4 [RQ.HivePartitioning.HivePartitionWrites.MissingColumn](#rqhivepartitioninghivepartitionwritesmissingcolumn)
            * 2.7.1.5 [RQ.HivePartitioning.HivePartitionWrites.NullInColumn](#rqhivepartitioninghivepartitionwritesnullincolumn)
            * 2.7.1.6 [RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes](#rqhivepartitioninghivepartitionwritesunsupportedtypes)
            * 2.7.1.7 [RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket](#rqhivepartitioninghivepartitionwritesreadonlybucket)
            * 2.7.1.8 [RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket](#rqhivepartitioninghivepartitionwritesnonaccessiblebucket)
            * 2.7.1.9 [RQ.HivePartitioning.HivePartitionWrites.ParallelInserts](#rqhivepartitioninghivepartitionwritesparallelinserts)
            * 2.7.1.10 [RQ.HivePartitioning.HivePartitionWrites.WriteFail](#rqhivepartitioninghivepartitionwriteswritefail)
        * 2.7.2 [Partition By Clause For S3 Engine With Hive Partition Writes](#partition-by-clause-for-s3-engine-with-hive-partition-writes)
            * 2.7.2.1 [RQ.HivePartitioning.HivePartitionWrites.PartitionBy](#rqhivepartitioninghivepartitionwritespartitionby)
            * 2.7.2.2 [RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy](#rqhivepartitioninghivepartitionwritesmissingpartitionby)
            * 2.7.2.3 [RQ.HivePartitioning.HivePartitionWrites.PartitionKey](#rqhivepartitioninghivepartitionwritespartitionkey)
        * 2.7.3 [Hive Partition Writes Syntax](#hive-partition-writes-syntax)
            * 2.7.3.1 [RQ.HivePartitioning.HivePartitionWritesSyntax.Generic](#rqhivepartitioninghivepartitionwritessyntaxgeneric)
        * 2.7.4 [Partition Stratagy Parameter](#partition-stratagy-parameter)
            * 2.7.4.1 [RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy](#rqhivepartitioninghivepartitionwritespartitionstratagy)
            * 2.7.4.2 [RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument](#rqhivepartitioninghivepartitionwritespartitionstratagywrongargument)
            * 2.7.4.3 [Hive Partition Strategy Write Partition Columns Into Files Parameter](#hive-partition-strategy-write-partition-columns-into-files-parameter)
            * 2.7.4.4 [RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles](#rqhivepartitioninghivepartitionwriteshivepartitionstrategywritepartitioncolumnsintofiles)
            * 2.7.4.5 [RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument](#rqhivepartitioninghivepartitionwriteshivepartitionstrategywritepartitioncolumnsintofileswrongargument)
        * 2.7.5 [Path Parameter](#path-parameter)
            * 2.7.5.1 [RQ.HivePartitioning.HivePartitionWrites.Path](#rqhivepartitioninghivepartitionwritespath)
            * 2.7.5.2 [RQ.HivePartitioning.HivePartitionWrites.InvalidPath](#rqhivepartitioninghivepartitionwritesinvalidpath)
        * 2.7.6 [Filename Parameter](#filename-parameter)
            * 2.7.6.1 [RQ.HivePartitioning.HivePartitionWrites.Filename](#rqhivepartitioninghivepartitionwritesfilename)
            * 2.7.6.2 [RQ.HivePartitioning.HivePartitionWrites.InvalidFilename](#rqhivepartitioninghivepartitionwritesinvalidfilename)
            * 2.7.6.3 [RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename](#rqhivepartitioninghivepartitionwritesnotdefinedfilename)
        * 2.7.7 [S3 Engine Parameters](#s3-engine-parameters)
            * 2.7.7.1 [RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters](#rqhivepartitioninghivepartitionwritess3engineparameters)


## Introduction

This document describes the requirements for the [ClickHouse] hive-style partitioning functionality. Hive-style partitioning refers to organizing files in a directory hierarchy where folder names encode column values (e.g. .../country=US/year=2021/file.parquet). [ClickHouse] provides functionality to read and write such partitioned data across various interfaces, including S3 and HDFS table functions and the Hive table engine. This allows users to query partitioned datasets efficiently by treating partition names as data columns and pruning unnecessary files. The following requirements describe the expected functionality and behavior for Hive-style partitioning support in [ClickHouse].


## Requirements

### Generic Behavior

#### RQ.HivePartitioning.Generic.Support
version: 1.0

[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form name=value) as virtual columns when accessing external data sources. This enables querying partitioned data without manual parsing of file paths.

#### RQ.HivePartitioning.Generic.EnableSetting
version: 1.0

[ClickHouse] SHALL use support setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.


#### RQ.HivePartitioning.Generic.Pruning
version: 1.0

[ClickHouse] SHALL only read the files from the partitions that satisfy filters when Hive-style partitioning is enabled and queries include filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.


#### RQ.HivePartitioning.Generic.Performance
version: 1.0

[ClickHouse] SHALL execute queries with `use_hive_partitioning=1` faster than queries with `use_hive_partitioning=0` if some files from storage are pruned with `WHERE` clause.






### Virtual Columns

#### RQ.HivePartitioning.VirtualColumns.Generic
version: 1.0

[Clickhouse] SHALL create virtual column for each partition key present in the file path with the same name as the partition key. 

For example, given a path segment /city=London/, a virtual column city will be provided with value "London" for all rows read from that directory.

#### RQ.HivePartitioning.VirtualColumns.ReadOnly
version: 1.0

Virtual columns created by hive partitioning SHALL be read-only.

#### RQ.HivePartitioning.VirtualColumns.Appearance
version: 1.0

Virtual columns created by hive partitioning SHALL not appear in query output, when query does not select this queries.

For example:
`SELECT *` 
This query SHALL not return virtual columns.

#### RQ.HivePartitioning.VirtualColumns.Accessability
version: 1.0

Virtual columns created by hive partitioning SHALL be accessible in queries.

For example:
`SELECT date FROM s3(...) WHERE date='01-01-2020'`

#### RQ.HivePartitioning.VirtualColumns.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error if path defined in query is invalid or storage does not contain defined files.

#### RQ.HivePartitioning.VirtualColumns.NameConflict
version: 1.0

[ClickHouse] SHALL not use virtual column if name of the virtual column matches with the name of table column.

#### RQ.HivePartitioning.VirtualColumns.HiveDisabled
version: 1.0

[Clickhouse] SHALL not create virtual column if `use_hive_partitioning` setting is disabled.


#### RQ.HivePartitioning.VirtualColumns.NonExistingKey
version: 1.0

[Clickhouse] SHALL return `Unknown identifier` error if query refers to nonexisting partition key.






### Hive Partition Types

#### RQ.HivePartitioning.HivePartitionTypes.Generic
version: 1.0

Partition values extracted from paths SHALL be treated as strings with no implicit type inference.

#### RQ.HivePartitioning.HivePartitionTypes.DefaultType
version: 1.0

Partition values extracted from paths SHALL have `LowCardinality(String)` type.

#### RQ.HivePartitioning.HivePartitionTypes.EmptyValue
version: 1.0

The hive value SHALL be empty string if directory is missing a key.






### Wildcards

#### RQ.HivePartitioning.Wildcards.Generic
version: 1.0

[ClickHouse] SHALL support glob-style wildcards for hive partitioning.

#### RQ.HivePartitioning.Wildcards.SingleStar
version: 1.0

[ClickHouse] SHALL support `*` wildcard for hive partitioning. `*` wildcard SHALL match any sequence of characters except `/`.

#### RQ.HivePartitioning.Wildcards.DoubleStart
version: 1.0

[ClickHouse] SHALL support `**` wildcard for hive partitioning. `**` wildcard SHALL match any sequence of characters including `/`.


#### RQ.HivePartitioning.Wildcards.QuestionMark
version: 1.0

[ClickHouse] SHALL support `?` wildcard for hive partitioning. `?` wildcard SHALL match a single character except `/`.


#### RQ.HivePartitioning.Wildcards.List
version: 1.0

[ClickHouse] SHALL support `{a[, b][, c]...}` wildcard for hive partitioning. `{a[, b][, c]...}` wildcard SHALL match one of the listed options.


#### RQ.HivePartitioning.Wildcards.WrongList
version: 1.0

[ClickHouse] SHALL return an error if one or more options in `{a[, b][, c]...}` are invalid or path does not exists.


#### RQ.HivePartitioning.Wildcards.Range
version: 1.0

[ClickHouse] SHALL support `{N..M}` wildcard for hive partitioning. `{N..M}` wildcard SHALL match numbers in a range.


#### RQ.HivePartitioning.Wildcards.WrongRange
version: 1.0

[ClickHouse] SHALL return an error if one or more options in `{N..M}` are invalid or path does not exists.







### Supported Table Functions

#### RQ.HivePartitioning.TableFunction.S3
version: 1.0

The [s3] table function SHALL support Hive-style partitions for reading in the provided URL path. If the S3 path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions. For example, a query:

```SQL
SET use_hive_partitioning = 1;
SELECT COUNT(*) 
FROM s3('s3://bucket/data/date=*/country=*/*.parquet', 'Parquet') 
WHERE country = 'Netherlands' AND date >= '2020-01-01';
```


#### RQ.HivePartitioning.TableFunction.S3Cluster
version: 1.0

The [s3Cluster] table function SHALL equally support Hive-style partitioning for reading across a cluster. On each cluster node, the function SHALL interpret partition directories and prune files in the same manner as a local [s3] call. This ensures distributed querying of an S3-partitioned dataset is consistent and efficient, reading only the necessary partitions on each node.



#### RQ.HivePartitioning.TableFunction.HDFS
version: 1.0

The [HDFS] table function SHALL support Hive-style partitions for reading in the provided URL path. If the path contains wildcard patterns corresponding to name=value directories and use_hive_partitioning is enabled, ClickHouse SHALL detect those patterns, expose corresponding virtual columns and prune not related to the query partitions.





### Supported Table Engines

#### S3 Table Engine

##### RQ.HivePartitioning.TableEngines.S3
version: 1.0

[ClickHouse] SHALL support reading from S3 table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.

```SQL
CREATE TABLE s3_engine_table(x Int64)
ENGINE = S3(...)
PARTITION BY date
```

#### HDFS Table Engine

##### RQ.HivePartitioning.TableEngines.HDFS
version: 1.0

[ClickHouse] SHALL support reading from HDFS table engine with hive partitioning. Hive partitioning columns SHALL be defined in PARTITION BY statement.

```SQL
CREATE TABLE hdfs_sales(x Int64)
ENGINE = HDFS(
    'hdfs:///data/{date}/file.parquet', 
    'Parquet'
)
PARTITION BY date
```


#### Hive Table Engine

##### RQ.HivePartitioning.TableEngines.Hive
version: 1.0

[ClickHouse] SHALL support reading from Hive table engine with hive partitioning. Hive partitioning columns SHALL be defined in Hive Metastore.

```SQL
CREATE TABLE hive_table(x Int64)
ENGINE = Hive(...) 
```





### Hive Partition Writes

#### Generic

##### RQ.HivePartitioning.HivePartitionWrites.S3
version: 1.0

[ClickHouse] SHALL support hive-style partition writes by using S3 table engine.


For example:
```SQL
CREATE TABLE hive_writes(year UInt16, country String, x UInt8)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy='hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2022, 'USA', 1),
    (2022, 'Canada', 2);
```

##### RQ.HivePartitioning.HivePartitionWrites.WrongEngine
version: 1.0

[ClickHouse] SHALL return an error if user tries to insert using hive-style partitions into table with not S3 Engine.

##### RQ.HivePartitioning.HivePartitionWrites.FileExist
version: 1.0

[ClickHouse] SHALL properly add data to the file if file already exists. This operation SHALL not delete or overwrite existing data.


##### RQ.HivePartitioning.HivePartitionWrites.MissingColumn
version: 1.0

[ClickHouse] SHALL return an error if columns defined in the `PARTITION BY` clause is missing.

##### RQ.HivePartitioning.HivePartitionWrites.NullInColumn
version: 1.0

[ClickHouse] SHALL return an error if columns defined in the `PARTITION BY` clause contains Null.

##### RQ.HivePartitioning.HivePartitionWrites.UnsupportedTypes
version: 1.0

[ClickHouse] SHALL return an error if type of the column defined in the `PARTITION BY` clause can't be casted into string.

##### RQ.HivePartitioning.HivePartitionWrites.ReadOnlyBucket
version: 1.0

[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is read-only.


##### RQ.HivePartitioning.HivePartitionWrites.NonAccessibleBucket
version: 1.0

[ClickHouse] SHALL return an error if bucket difined in S3 engine clause is not accessible.


##### RQ.HivePartitioning.HivePartitionWrites.ParallelInserts
version: 1.0

[ClickHouse] SHALL support parallel inserts into one file.

##### RQ.HivePartitioning.HivePartitionWrites.WriteFail
version: 1.0

[ClickHouse] SHALL fail the insert and SHALL not leave partial data if any object write fails.


#### Partition By Clause For S3 Engine With Hive Partition Writes

##### RQ.HivePartitioning.HivePartitionWrites.PartitionBy
version: 1.0

[ClickHouse] SHALL perform hive partition writes only if table engine definition contains `PARTITION BY` clause.


##### RQ.HivePartitioning.HivePartitionWrites.MissingPartitionBy
version: 1.0

[ClickHouse] SHALL return an error if user tries to insert into table with S3 table engine without `PARTITION BY` clause.


##### RQ.HivePartitioning.HivePartitionWrites.PartitionKey
version: 1.0

[ClickHouse] SHALL create path containing {/key=value/} for all columns defined in `PARTITION BY` clause and file on this path on insert, if file does not exists.
Inserted data SHALL be located in this file.


#### Hive Partition Writes Syntax

##### RQ.HivePartitioning.HivePartitionWritesSyntax.Generic
version: 1.0

S3 table Engine SHALL have the following syntax:

```SQL
ENGINE = S3(path [, NOSIGN | aws_access_key_id, aws_secret_access_key,] format[, compression][, filename][, partition_stratagy][, hive_partition_strategy_write_partition_columns_into_files])
```

#### Partition Stratagy Parameter

##### RQ.HivePartitioning.HivePartitionWrites.PartitionStratagy
version: 1.0

[ClickHouse] SHALL support `partition_stratagy` parameter for S3 engine that SHALL define if [ClickHouse] enables hive partition writes or no.
[ClickHouse] SHALL support 'hive' and 'auto' values for this parameter. [ClickHouse] SHALL enable hive partition writes if it is set to 'hive' and disable if it is set to 'auto'.
`partition_stratagy` SHALL be 'auto' by default.


##### RQ.HivePartitioning.HivePartitionWrites.PartitionStratagyWrongArgument
version: 1.0

[ClickHouse] SHALL return an error if `partition_stratagy` parameter neither set to 'auto' and 'hive'.


##### Hive Partition Strategy Write Partition Columns Into Files Parameter

##### RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFiles
version: 1.0

[ClickHouse] SHALL support `hive_partition_strategy_write_partition_columns_into_files` parameter for S3 engine that SHALL define if [ClickHouse] writes partition columns into files or not.
`hive_partition_strategy_write_partition_columns_into_files` SHALL be False by default.

##### RQ.HivePartitioning.HivePartitionWrites.HivePartitionStrategyWritePartitionColumnsIntoFilesWrongArgument
version: 1.0

[ClickHouse] SHALL return an error if `hive_partition_strategy_write_partition_columns_into_files` parameter gets argument that cannot be casted to boolean.

#### Path Parameter

##### RQ.HivePartitioning.HivePartitionWrites.Path
version: 1.0

[ClickHouse] SHALL support `path` parameter that defines path to the bucket for hive partition writes.

##### RQ.HivePartitioning.HivePartitionWrites.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error if defined `path` is invalid or `path` points to a file with `partition_stratagy='hive'`.

#### Filename Parameter

##### RQ.HivePartitioning.HivePartitionWrites.Filename
version: 1.0

[ClickHouse] SHALL support `filename` parameter that defines filename for hive partition writes.

##### RQ.HivePartitioning.HivePartitionWrites.InvalidFilename
version: 1.0

[ClickHouse] SHALL return an error if defined `filename` is invalid or points to a directory.

##### RQ.HivePartitioning.HivePartitionWrites.NotDefinedFilename
version: 1.0

[ClickHouse] SHALL return an error if defined `filename` parameter is not defined but `partition_stratagy` is set to 'hive'.

#### S3 Engine Parameters

##### RQ.HivePartitioning.HivePartitionWrites.S3EngineParameters
version: 1.0

[ClickHouse] SHALL not change behavior of the following parameters if `partition_stratagy` is set to 'hive':
`aws_access_key_id`, `aws_secret_access_key`, `format`, `compression`.



[ClickHouse]: https://clickhouse.com
[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3
[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster
[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs
'''
)
