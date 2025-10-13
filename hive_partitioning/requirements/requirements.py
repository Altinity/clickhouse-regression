# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_HivePartitioning_Support = Requirement(
    name="RQ.HivePartitioning.Support",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form `name=value`) as virtual columns when accessing external data sources. This enables querying partitioned data using partition columns directly, without requiring manual parsing of file paths.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning=1\n"
        "```\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/sales/date=2025-01-01/file1.parquet  \n"
        " - /data/sales/date=2025-01-02/file2.parquet  \n"
        " - /data/sales/date=2025-01-03/file3.parquet\n"
        "```\n"
        "\n"
        "In this example, date is a virtual column automatically extracted from directory names.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_HivePartitioning_EnableSetting = Requirement(
    name="RQ.HivePartitioning.EnableSetting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support session-scoped setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.\n"
        "\n"
        "```sql\n"
        "set use_hive_partitioning=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_HivePartitioning_Generic_Pruning = Requirement(
    name="RQ.HivePartitioning.Generic.Pruning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL only read files from partitions that satisfy query filters when Hive-style partitioning is enabled and the query includes filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.\n"
        "\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/sales/date=2025-01-01/file1.parquet  \n"
        " - /data/sales/date=2025-01-02/file2.parquet  \n"
        " - /data/sales/date=2025-01-03/file3.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning=1\n"
        "\n"
        "CREATE TABLE sales(...)\n"
        "Engine=S3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')\n"
        "\n"
        "SELECT * FROM sales WHERE date='2025-01-02'\n"
        "```\n"
        "\n"
        "In the example select SHALL read only the second file.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
)

RQ_HivePartitioning_Generic_Performance = Requirement(
    name="RQ.HivePartitioning.Generic.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL execute queries with `use_hive_partitioning = 1` faster than with `use_hive_partitioning = 0` when some files from storage are pruned using a `WHERE` clause on partition columns. This behavior is expected because Hive-style partitioning enables [ClickHouse] to skip irrelevant directories, reducing I/O and query execution time.\n"
        "\n"
        "\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/sales/date=2025-01-01/file1.parquet  \n"
        " - /data/sales/date=2025-01-02/file2.parquet  \n"
        " - /data/sales/date=2025-01-03/file3.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "-- Hive partition disabled\n"
        "SET use_hive_partitioning = 0;\n"
        "\n"
        "SELECT * FROM sales WHERE date = '2025-01-02';\n"
        "\n"
        "-- Hive partition enabled\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT * FROM sales WHERE date = '2025-01-02';\n"
        "```\n"
        "\n"
        "In this example, the second query (with pruning enabled) SHALL complete faster than the first one.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.4",
)

RQ_HivePartitioning_Generic_Encoding = Requirement(
    name="RQ.HivePartitioning.Generic.Encoding",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support URL-encoded values in Hive-style partition paths. \n"
        "Encoded characters in the `key=value` segments of the path SHALL be decoded before being exposed as virtual column values.\n"
        "For example:\n"
        "\n"
        "```\n"
        "Path: \n"
        "/city=New%20York/file.parquet\n"
        "```\n"
        "\n"
        "In this Example, [ClickHouse] SHALL recognize:\n"
        "\n"
        "key = 'city'\n"
        "\n"
        "value = 'New York' (decoded from %20)\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.5",
)

RQ_HivePartitioning_VirtualColumns = Requirement(
    name="RQ.HivePartitioning.VirtualColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL create a virtual column for each partition key present in the file path, using the same name as the partition key.  \n"
        "\n"
        "For example, given a path segment `/city=London/`, a virtual column `city` SHALL be available with the value `'London'` for all rows read from that directory.\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/trips/city=London/file1.parquet\n"
        " - /data/trips/city=Berlin/file2.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT DISTINCT city FROM trips ORDER BY city;\n"
        "```\n"
        "\n"
        "Expected output:\n"
        "```\n"
        "Berlin  \n"
        "London\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_HivePartitioning_VirtualColumns_ReadOnly = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.ReadOnly",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL treat virtual columns created by Hive-style partitioning as read-only. Any attempt to modify, insert into, or otherwise write to these columns SHALL result in an error.\n"
        "[ClickHouse] SHALL return the following error if a write operation targets a virtual column: `DB::Exception: Failed to check existence of a key`.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_HivePartitioning_VirtualColumns_Appearance = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.Appearance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not return virtual columns created by Hive-style partitioning in the query output unless they are explicitly selected.\n"
        "[Clickhouse] SHALL not return virtual columns for `DESCRIBE TABLE` query.\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/sales/city=London/file1.parquet\n"
        " - /data/sales/city=Berlin/file2.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT * FROM sales;\n"
        "```\n"
        "\n"
        "The city column SHALL NOT appear in the result set, because it was not selected explicitly.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.3",
)

RQ_HivePartitioning_VirtualColumns_Accessibility = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.Accessibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Virtual columns created by Hive-style partitioning SHALL be accessible in queries.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT date\n"
        "FROM s3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')\n"
        "WHERE date = '2020-01-01';\n"
        "```\n"
        "\n"
        "In this example, date is not a physical column in the file, but a virtual column automatically derived from the file path (e.g., /date=2020-01-01/).\n"
        "[ClickHouse] SHALL allow filtering and selecting by this column as part of query execution.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.4",
)

RQ_HivePartitioning_VirtualColumns_InvalidPath = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.InvalidPath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error  \n"
        "`DB::Exception: Failed to check existence of a key`  \n"
        "if the path defined in the query is invalid or the underlying storage does not contain the expected files.\n"
        "\n"
        "This includes cases such as:\n"
        "- The path does not exist.\n"
        "- The path does not conform to the Hive-style partitioning pattern (e.g., mismatched `key` or `value`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.5",
)

RQ_HivePartitioning_VirtualColumns_NameConflict = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.NameConflict",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL NOT use a virtual column if its name conflicts with the name of an existing table column.\n"
        "[ClickHouse] SHALL treat column names in this comparison as case-sensitive.\n"
        "This ensures that explicitly defined table columns always take precedence over virtual columns derived from partitioned paths.\n"
        "\n"
        "\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/events/date=2024-01-01/file1.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "CREATE TABLE events\n"
        "(\n"
        "    id UInt32,\n"
        "    date Date\n"
        ")\n"
        "ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');\n"
        "\n"
        "SELECT date FROM events WHERE id = 1;\n"
        "```\n"
        "In this example, the value of the date column SHALL come from the Parquet file, not from the path segment date=2024-01-01.\n"
        "The virtual column date SHALL be ignored due to the name conflict with the real column date in the schema.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.6",
)

RQ_HivePartitioning_VirtualColumns_HiveDisabled = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.HiveDisabled",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL NOT create virtual columns if the `use_hive_partitioning` setting is disabled.\n"
        "\n"
        "\n"
        "```\n"
        "SET use_hive_partitioning=0\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.7",
)

RQ_HivePartitioning_VirtualColumns_NonExistingKey = Requirement(
    name="RQ.HivePartitioning.VirtualColumns.NonExistingKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return `Unknown identifier` error if a query refers to nonexisting partition key.\n"
        "\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/events/date=2024-01-01/file1.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "CREATE TABLE events\n"
        "(\n"
        "    id UInt32,\n"
        ")\n"
        "ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');\n"
        "\n"
        "SELECT region FROM events\n"
        "```\n"
        "In this example, the virtual column region does not exist in the partitioned path or in the Parquet file schema.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.8",
)

RQ_HivePartitioning_HivePartitionValue = Requirement(
    name="RQ.HivePartitioning.HivePartitionValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Partition values extracted from Hive-style partitioned paths SHALL be treated as LowCardinality(String), with no implicit type inference during schema construction.\n"
        "\n"
        "This ensures that values such as '2024-01-01', '123', or 'true' are interpreted as string literals by default.\n"
        "[ClickHouse] SHALL allow these values to be explicitly cast by the user or automatically cast by the query engine if the query context requires it (e.g., in a WHERE clause comparing to a typed column).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_HivePartitioning_HivePartitionValue_EmptyValue = Requirement(
    name="RQ.HivePartitioning.HivePartitionValue.EmptyValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The partition value SHALL be an empty string (`''`) if a directory in the path is missing a value.\n"
        "\n"
        "For example:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /data/events/city=/file1.parquet\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT city FROM events;\n"
        "```\n"
        "\n"
        "In this example, select SHALL return ''.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_HivePartitioning_Wildcards = Requirement(
    name="RQ.HivePartitioning.Wildcards",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support glob-style wildcards when resolving paths in Hive-style partitioning.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_HivePartitioning_Wildcards_SingleStar = Requirement(
    name="RQ.HivePartitioning.Wildcards.SingleStar",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `*` wildcard in Hive-style partitioning.  \n"
        "The `*` wildcard SHALL match any sequence of characters excluding `/`.\n"
        "\n"
        "For example:\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/year=*/month=*/', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_HivePartitioning_Wildcards_DoubleStar = Requirement(
    name="RQ.HivePartitioning.Wildcards.DoubleStar",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `**` wildcard in Hive-style partitioning.  \n"
        "The `**` wildcard SHALL match any sequence of characters including `/`.\n"
        "\n"
        "for example:\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/**/file.parquet', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
)

RQ_HivePartitioning_Wildcards_QuestionMark = Requirement(
    name="RQ.HivePartitioning.Wildcards.QuestionMark",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `?` wildcard in Hive-style partitioning.  \n"
        "The `?` wildcard SHALL match a single character, excluding `/`.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/year=202?', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.4",
)

RQ_HivePartitioning_Wildcards_List = Requirement(
    name="RQ.HivePartitioning.Wildcards.List",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `{a[,b][,c]...}` wildcard syntax for Hive-style partitioning.  \n"
        "This wildcard SHALL match one of the listed values.\n"
        "\n"
        "\n"
        "For example\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/month={01,02,03}/', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.5",
)

RQ_HivePartitioning_Wildcards_WrongList = Requirement(
    name="RQ.HivePartitioning.Wildcards.WrongList",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if one or more paths specified in a `{a[,b]...}` list do not exist.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.6",
)

RQ_HivePartitioning_Wildcards_Range = Requirement(
    name="RQ.HivePartitioning.Wildcards.Range",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `{N..M}` numerical range wildcard in Hive-style partitioning.  \n"
        "This wildcard SHALL expand to all integers from `N` to `M` inclusive.\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/day={1..7}/', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.7",
)

RQ_HivePartitioning_Wildcards_WrongRange = Requirement(
    name="RQ.HivePartitioning.Wildcards.WrongRange",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if one or more values in the `{N..M}` range are invalid or the corresponding paths do not exist.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.8",
)

RQ_HivePartitioning_Wildcards_Escaping = Requirement(
    name="RQ.HivePartitioning.Wildcards.Escaping",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow escaping of wildcard characters (`*`, `?`, `{`, `}`) using a backslash (`\\`) for literal matching.\n"
        "\n"
        "Example:\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3('https://<bucket>/data/\\{special\\}/file.parquet', ...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.9",
)

RQ_HivePartitioning_TableFunction_S3 = Requirement(
    name="RQ.HivePartitioning.TableFunction.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hive-style partitioning with the `s3` table function when reading from the specified URL path.\n"
        "\n"
        "If the S3 path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:\n"
        "\n"
        "- Detect and interpret partition keys from the path.\n"
        "- Expose corresponding virtual columns.\n"
        "- Prune irrelevant partitions based on query filters.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT COUNT(*) \n"
        "FROM s3('s3://bucket/data/date=*/region=*/*.parquet', 'Parquet') \n"
        "WHERE region = 'EU' AND date >= '2022-01-01';\n"
        "```\n"
        "In this example, [ClickHouse] SHALL read only files matching the region='EU' and date >= '2022-01-01' filters,\n"
        "and expose date and region as virtual columns.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_HivePartitioning_TableFunction_S3Cluster = Requirement(
    name="RQ.HivePartitioning.TableFunction.S3Cluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hive-style partitioning with the `s3Cluster` table function when reading across a cluster.\n"
        "\n"
        "On each cluster node, the function SHALL:\n"
        "\n"
        "- Detect and interpret partition keys from the S3 path using `name=value` directory structure.\n"
        "- Expose corresponding virtual columns.\n"
        "- Prune irrelevant partitions based on query filters, just like the `s3` table function.\n"
        "\n"
        "This ensures that distributed querying of S3-partitioned datasets is consistent and efficient across all cluster nodes, reading only the necessary files per node.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT COUNT(*)\n"
        "FROM s3Cluster('my_cluster', 's3://bucket/data/date=*/region=*/*.parquet', 'Parquet')\n"
        "WHERE region = 'EU' AND date >= '2022-01-01';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_HivePartitioning_TableFunction_HDFS = Requirement(
    name="RQ.HivePartitioning.TableFunction.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hive-style partitioning with the `hdfs` table function when reading from the specified HDFS URL path.\n"
        "\n"
        "If the path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:\n"
        "\n"
        "- Detect and interpret partition keys from the directory structure.\n"
        "- Expose corresponding virtual columns.\n"
        "- Prune irrelevant partitions based on query filters.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "SELECT *\n"
        "FROM hdfs('hdfs://namenode/data/year=*/region=*/*.parquet', 'Parquet')\n"
        "WHERE region = 'US' AND year = '2023';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_HivePartitioning_TableEngines_S3 = Requirement(
    name="RQ.HivePartitioning.TableEngines.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading from the `S3` table engine with Hive-style partitioning.  \n"
        "Partitioning columns SHALL be explicitly defined in the `PARTITION BY` clause of the table definition.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "CREATE TABLE s3_engine_table\n"
        "(\n"
        "    x Int64\n"
        ")\n"
        "ENGINE = S3('https://<bucket>/data/{date}/file.parquet', 'access_key', 'secret_key', 'Parquet')\n"
        "PARTITION BY date;\n"
        "```\n"
        "In this example, [ClickHouse] SHALL extract the date value from the file path and expose it as a virtual column.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.1.1",
)

RQ_HivePartitioning_TableEngines_HDFS = Requirement(
    name="RQ.HivePartitioning.TableEngines.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading from the HDFS table engine with Hive-style partitioning.\n"
        "Partitioning columns SHALL be explicitly defined in the PARTITION BY clause.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "CREATE TABLE hdfs_sales\n"
        "(\n"
        "    x Int64\n"
        ")\n"
        "ENGINE = HDFS('hdfs:///data/{date}/file.parquet', 'Parquet')\n"
        "PARTITION BY date;\n"
        "```\n"
        "In this example, [ClickHouse] SHALL use the date segment from the path as a virtual partition column.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.2.1",
)

RQ_HivePartitioning_TableEngines_Hive = Requirement(
    name="RQ.HivePartitioning.TableEngines.Hive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading from the Hive table engine with Hive-style partitioning.\n"
        "Partitioning columns SHALL be defined in the Hive Metastore.\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 1;\n"
        "\n"
        "CREATE TABLE hive_table\n"
        "(\n"
        "    x Int64\n"
        ")\n"
        "ENGINE = Hive('thrift://metastore:9083', 'default', 'sales');\n"
        "```\n"
        "In this example, [ClickHouse] SHALL detect partition columns from the Hive Metastore schema\n"
        "and expose them as virtual columns during query execution.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.3.1",
)

RQ_HivePartitioning_Writes_S3 = Requirement(
    name="RQ.HivePartitioning.Writes.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hive-style partitioned writes using the `S3` table engine.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_writes\n"
        "(\n"
        "    year UInt16,\n"
        "    country String,\n"
        "    x UInt8\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY (year, country);\n"
        "\n"
        "INSERT INTO hive_writes VALUES\n"
        "    (2022, 'USA', 1),\n"
        "    (2022, 'Canada', 2);\n"
        "```\n"
        "\n"
        "In this example, [ClickHouse] SHALL write each row into a separate Hive-style partition path:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /year=2022/country=Germany/...\n"
        " - /year=2022/country=France/...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_HivePartitioning_Writes_PartitionStrategy = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionStrategy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `partition_strategy` parameter in the `S3` table engine definition. This parameter determines whether Hive-style partitioned writes are enabled.\n"
        "\n"
        "[ClickHouse] SHALL support the following values for `partition_strategy`:\n"
        "\n"
        "- `'hive'`: Enables Hive-style partitioned writes. Data will be written into partitioned paths based on the `PARTITION BY` clause (e.g., `/key=value/`).\n"
        "- `'auto'`: Disables Hive-style partitioning. Data will be written without creating Hive-style partition directories.\n"
        "\n"
        "If the `partition_strategy` parameter is not explicitly specified, it SHALL default to `'auto'`.\n"
        "\n"
        "\n"
        "```sql\n"
        "ENGINE = S3(s3_conn,..., partition_strategy='hive')\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.2.1",
)

RQ_HivePartitioning_Writes_PartitionStrategyWrongArgument = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Unknown partitioning style ` if the `partition_strategy` parameter is set to a value other than `'auto'` or `'hive'`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.2.2",
)

RQ_HivePartitioning_Writes_PartitionColumnsInDataFile = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `partition_columns_in_data_file` parameter in the `S3` table engine definition if `partition_strategy='hive'`.\n"
        "\n"
        "This parameter controls whether columns used in the `PARTITION BY` clause are also written into the data files.\n"
        "\n"
        "- If `partition_columns_in_data_file = true`, partition columns SHALL be included in the file.\n"
        "- If `partition_columns_in_data_file = false`, partition columns SHALL NOT be included in the file and are expected to be inferred from the path (e.g., `/key=value/`).\n"
        "\n"
        "By default, `partition_columns_in_data_file` SHALL be set to `false`.\n"
        "\n"
        "```sql\n"
        "ENGINE = S3(s3_conn,..., partition_columns_in_data_file=1)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.3.1",
)

RQ_HivePartitioning_Writes_PartitionColumnsInDataFileWithoutHivePartitionStrategy = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `partition_columns_in_data_file` is specified but `partition_strategy='auto'` or not defined.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.3.2",
)

RQ_HivePartitioning_Writes_PartitionColumnsInDataFileWrongArgument = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgument",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `partition_columns_in_data_file` parameter is assigned a value that cannot be interpreted as a Boolean.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.3.3",
)

RQ_HivePartitioning_Writes_Path = Requirement(
    name="RQ.HivePartitioning.Writes.Path",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `path` parameter in the `S3` table engine definition to specify the full bucket path used as the root for Hive-style partitioned writes.\n"
        "The `path` parameter SHALL define the S3 bucket and optional prefix under which partitioned files will be created. \n"
        "Partition subdirectories (e.g., `/key=value/`) and filenames defined by `filename` will be appended to this base path automatically.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.4.1",
)

RQ_HivePartitioning_Writes_InvalidPath = Requirement(
    name="RQ.HivePartitioning.Writes.InvalidPath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Invalid S3 key` if the defined `path` parameter is invalid in the context of Hive-style partitioning with the `S3` table engine.\n"
        "\n"
        "This includes cases where the `path`:\n"
        "\n"
        "- Is not a valid S3 URI.\n"
        "- Contains illegal characters.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.4.2",
)

RQ_HivePartitioning_Writes_Filename = Requirement(
    name="RQ.HivePartitioning.Writes.Filename",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `filename` parameter in the `S3` table engine definition to specify a directory that SHALL be prepended before all Hive-style partition directories.\n"
        "[ClickHouse] SHALL support this parameter only if `partition_strategy='hive'`.\n"
        "\n"
        "The full write path SHALL be constructed as:\n"
        "```\n"
        "<path>/<filename>/<key1>=<value1>/<key2>=<value2>/...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.5.1",
)

RQ_HivePartitioning_Writes_FilenameWithoutHivePartitionStrategy = Requirement(
    name="RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if `filename` is specified but `partition_strategy='auto'` or not defined.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.5.2",
)

RQ_HivePartitioning_Writes_NotDefinedFilename = Requirement(
    name="RQ.HivePartitioning.Writes.NotDefinedFilename",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL write partitioned data directly into the root `path` if the `filename` parameter is not defined and `partition_strategy` is set to `'hive'`.\n"
        "\n"
        "\n"
        "In this case, the write path SHALL be constructed as:\n"
        "\n"
        "```\n"
        "<path>//<key1>=<value1>/<key2>=<value2>/...\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.5.3",
)

RQ_HivePartitioning_Writes_S3EngineParameters = Requirement(
    name="RQ.HivePartitioning.Writes.S3EngineParameters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL NOT alter the behavior of the following S3 engine parameters when `partition_strategy` is set to `'hive'`:\n"
        "\n"
        "- `aws_access_key_id`\n"
        "- `aws_secret_access_key`\n"
        "- `format`\n"
        "- `compression`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.6.1",
)

RQ_HivePartitioning_Writes_UseHivePartitions = Requirement(
    name="RQ.HivePartitioning.Writes.UseHivePartitions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ignore the `use_hive_partitioning = 0` setting during write operations if `partition_strategy = 'hive'` is explicitly specified.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "SET use_hive_partitioning = 0;\n"
        "\n"
        "CREATE TABLE hive_writes\n"
        "(\n"
        "    year UInt16,\n"
        "    country String,\n"
        "    x UInt8\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY (year, country);\n"
        "\n"
        "INSERT INTO hive_writes VALUES\n"
        "    (2023, 'Germany', 10),\n"
        "    (2023, 'France', 20);\n"
        "```\n"
        "\n"
        "In this example,[ClickHouse] SHALL write the data into Hive-style partitioned paths:\n"
        "```\n"
        "Structure:\n"
        " - /year=2023/country=Germany/...\n"
        " - /year=2023/country=France/...\n"
        "```\n"
    ),
    link=None,
    level=3,
    num="8.6.2",
)

RQ_HivePartitioning_Writes_PartitionsParts = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionsParts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing data into multiple Hive-style partition paths when using the `S3` table engine with `partition_strategy = 'hive'`.\n"
        "\n"
        "This includes:\n"
        "- Writing rows to multiple partition paths within a single `INSERT`.\n"
        "- Writing to the same or different partitions across multiple `INSERT`s\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.7.1",
)

RQ_HivePartitioning_Writes_Expressions = Requirement(
    name="RQ.HivePartitioning.Writes.Expressions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if the `PARTITION BY` clause contains an expression, when using `partition_strategy = 'hive'`.\n"
        "\n"
        "Only column names are allowed in the `PARTITION BY` clause for Hive-style partitioning.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_invalid\n"
        "(\n"
        "    year UInt16,\n"
        "    month UInt8,\n"
        "    value UInt32\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY toString(year);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.8.1",
)

RQ_HivePartitioning_Writes_FileExist = Requirement(
    name="RQ.HivePartitioning.Writes.FileExist",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL append data by creating a new file in the existing partition directory when writing via the S3 table engine with partition_strategy = 'hive'.\n"
        "\n"
        "If a file already exists at the target partition path, [ClickHouse] SHALL create a new file alongside it, without deleting or overwriting existing content.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.9.1",
)

RQ_HivePartitioning_Writes_MissingColumn = Requirement(
    name="RQ.HivePartitioning.Writes.MissingColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error if any column defined in the `PARTITION BY` clause is missing from the table schema.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_sales\n"
        "(\n"
        "    year UInt16,\n"
        "    value UInt32\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY (year, country);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.10.1",
)

RQ_HivePartitioning_Writes_DefaultValue = Requirement(
    name="RQ.HivePartitioning.Writes.DefaultValue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL use the default value defined in the table schema for any partitioning column that is omitted during `INSERT`, when writing with `partition_strategy = 'hive'`.\n"
        "\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_sales\n"
        "(\n"
        "    year UInt16 DEFAULT 2023,\n"
        "    country String DEFAULT 'Unknown',\n"
        "    value UInt32\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY (year, country);\n"
        "\n"
        "INSERT INTO hive_sales (value) VALUES (100);\n"
        "```\n"
        "\n"
        "In this example, [ClickHouse] SHALL write to the following partition path:\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /year=2023/country=Unknown/file.parquet\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.11.1",
)

RQ_HivePartitioning_Writes_NullableDataType = Requirement(
    name="RQ.HivePartitioning.Writes.NullableDataType",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` \n"
        "if any column defined in the `PARTITION BY` clause is of a nullable data type when using `partition_strategy = 'hive'`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.12.1",
)

RQ_HivePartitioning_Writes_SupportedDataTypes = Requirement(
    name="RQ.HivePartitioning.Writes.SupportedDataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following data types for Hive-style partitioning during write operations (`partition_strategy = 'hive'`)\n"
        "if partition key satisfy all of the following conditions:\n"
        "\n"
        "- The value length SHALL be less than 1024 characters.\n"
        "- The value SHALL NOT contain special characters: `{}`, `\\`, `/`, `\"`, `'`, `*`, `?`.\n"
        "\n"
        "The following data types are supported as partition keys:\n"
        "\n"
        "| Data Type     | Supported |\n"
        "|---------------|-----------|\n"
        "| Int8          | ✅ Yes    |\n"
        "| Int16         | ✅ Yes    |\n"
        "| Int32         | ✅ Yes    |\n"
        "| Int64         | ✅ Yes    |\n"
        "| Int128        | ✅ Yes    |\n"
        "| Int256        | ✅ Yes    |\n"
        "| UInt8         | ✅ Yes    |\n"
        "| UInt16        | ✅ Yes    |\n"
        "| UInt32        | ✅ Yes    |\n"
        "| UInt64        | ✅ Yes    |\n"
        "| UInt128       | ✅ Yes    |\n"
        "| UInt256       | ✅ Yes    |\n"
        "| String        | ✅ Yes    |\n"
        "| FixedString(N)| ✅ Yes    |\n"
        "| Date          | ✅ Yes    |\n"
        "| Date32        | ✅ Yes    |\n"
        "| Time          | ✅ Yes    |\n"
        "| Time64(N)     | ✅ Yes    |\n"
        "| DateTime      | ✅ Yes    |\n"
        "| DateTime64(N) | ✅ Yes    |\n"
        "| Bool          | ✅ Yes    |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.13.1",
)

RQ_HivePartitioning_Writes_DataTypesUnsupported = Requirement(
    name="RQ.HivePartitioning.Writes.DataTypesUnsupported",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` \n"
        "if the data type of any column defined in the `PARTITION BY` clause is not included in the list of supported types for Hive-style partitioning.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.14.1",
)

RQ_HivePartitioning_Writes_ReadOnlyBucket = Requirement(
    name="RQ.HivePartitioning.Writes.ReadOnlyBucket",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`\n"
        "if bucket defined in S3 engine clause is read-only.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.15.1",
)

RQ_HivePartitioning_Writes_NonAccessibleBucket = Requirement(
    name="RQ.HivePartitioning.Writes.NonAccessibleBucket",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`\n"
        " if bucket defined in S3 engine clause is not accessible.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.16.1",
)

RQ_HivePartitioning_Writes_ParallelInserts = Requirement(
    name="RQ.HivePartitioning.Writes.ParallelInserts",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support parallel inserts into the same Hive-style partition when writing with the `S3` table engine and `partition_strategy = 'hive'`.\n"
        "\n"
        "Multiple concurrent `INSERT` operations targeting the same file or partition path SHALL succeed without data loss or corruption.\n"
        "\n"
        "[ClickHouse] SHALL support parallel inserts from different users.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.17.1",
)

RQ_HivePartitioning_Writes_WriteFail = Requirement(
    name="RQ.HivePartitioning.Writes.WriteFail",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not leave any partial data if writing to one or more objects fails during Hive-style partitioned writes.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.18.1",
)

RQ_HivePartitioning_Writes_PartitionBy = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionBy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL perform Hive-style partitioned writes only if the table definition includes a valid `PARTITION BY` clause.\n"
        "\n"
        "If the `PARTITION BY` clause is missing, and `partition_strategy = 'hive'` is specified, \n"
        "[ClickHouse] SHALL return an error `DB::Exception: Partition strategy hive can not be used without a PARTITION BY expression.`.\n"
        "\n"
        "This ensures that directory-based partitioning structure is explicitly defined and not left ambiguous.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_data\n"
        "(\n"
        "    year UInt16,\n"
        "    value UInt32\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'table', format = Parquet, partition_strategy = 'hive');\n"
        "```\n"
        "In this example, [ClickHouse] SHALL return an error.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="8.19.1",
)

RQ_HivePartitioning_Writes_PartitionKey = Requirement(
    name="RQ.HivePartitioning.Writes.PartitionKey",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL create a directory path of the form `/key=value/` for each column defined in the `PARTITION BY` clause when performing Hive-style partitioned writes.\n"
        "If the target file at the resulting path does not exist, it SHALL be created automatically.  \n"
        "Inserted data SHALL be written into that file.\n"
        "\n"
        "Partition keys may contain special characters that are safe for directory names (e.g., spaces, `-`, `_`, `%`), and these SHALL be properly encoded if required by the underlying filesystem or object storage.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE hive_orders\n"
        "(\n"
        "    region String,\n"
        "    year UInt16,\n"
        "    order_id UInt64\n"
        ")\n"
        "ENGINE = S3(s3_conn, filename = 'orders.parquet', format = Parquet, partition_strategy = 'hive')\n"
        "PARTITION BY (region, year);\n"
        "\n"
        "INSERT INTO hive_orders VALUES ('North-America', 2024, 1);\n"
        "```\n"
        "\n"
        "```\n"
        "Structure:\n"
        " - /region=North-America/year=2024/orders.parquet\n"
        "```\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3\n"
        "[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster\n"
        "[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs\n"
    ),
    link=None,
    level=3,
    num="8.19.2",
)

SRS_045_Hive_Partitioning = Specification(
    name="SRS-045 Hive Partitioning",
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
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Generic Behavior", level=1, num="2"),
        Heading(name="RQ.HivePartitioning.Support", level=2, num="2.1"),
        Heading(name="RQ.HivePartitioning.EnableSetting", level=2, num="2.2"),
        Heading(name="RQ.HivePartitioning.Generic.Pruning", level=2, num="2.3"),
        Heading(name="RQ.HivePartitioning.Generic.Performance", level=2, num="2.4"),
        Heading(name="RQ.HivePartitioning.Generic.Encoding", level=2, num="2.5"),
        Heading(name="Virtual Columns", level=1, num="3"),
        Heading(name="RQ.HivePartitioning.VirtualColumns", level=2, num="3.1"),
        Heading(name="RQ.HivePartitioning.VirtualColumns.ReadOnly", level=2, num="3.2"),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.Appearance", level=2, num="3.3"
        ),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.Accessibility", level=2, num="3.4"
        ),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.InvalidPath", level=2, num="3.5"
        ),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.NameConflict", level=2, num="3.6"
        ),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.HiveDisabled", level=2, num="3.7"
        ),
        Heading(
            name="RQ.HivePartitioning.VirtualColumns.NonExistingKey", level=2, num="3.8"
        ),
        Heading(name="Hive Partition Types Value", level=1, num="4"),
        Heading(name="RQ.HivePartitioning.HivePartitionValue", level=2, num="4.1"),
        Heading(
            name="RQ.HivePartitioning.HivePartitionValue.EmptyValue", level=2, num="4.2"
        ),
        Heading(name="Wildcards", level=1, num="5"),
        Heading(name="RQ.HivePartitioning.Wildcards", level=2, num="5.1"),
        Heading(name="RQ.HivePartitioning.Wildcards.SingleStar", level=2, num="5.2"),
        Heading(name="RQ.HivePartitioning.Wildcards.DoubleStar", level=2, num="5.3"),
        Heading(name="RQ.HivePartitioning.Wildcards.QuestionMark", level=2, num="5.4"),
        Heading(name="RQ.HivePartitioning.Wildcards.List", level=2, num="5.5"),
        Heading(name="RQ.HivePartitioning.Wildcards.WrongList", level=2, num="5.6"),
        Heading(name="RQ.HivePartitioning.Wildcards.Range", level=2, num="5.7"),
        Heading(name="RQ.HivePartitioning.Wildcards.WrongRange", level=2, num="5.8"),
        Heading(name="RQ.HivePartitioning.Wildcards.Escaping", level=2, num="5.9"),
        Heading(name="Supported Table Functions", level=1, num="6"),
        Heading(name="RQ.HivePartitioning.TableFunction.S3", level=2, num="6.1"),
        Heading(name="RQ.HivePartitioning.TableFunction.S3Cluster", level=2, num="6.2"),
        Heading(name="RQ.HivePartitioning.TableFunction.HDFS", level=2, num="6.3"),
        Heading(name="Supported Table Engines", level=1, num="7"),
        Heading(name="S3 Table Engine", level=2, num="7.1"),
        Heading(name="RQ.HivePartitioning.TableEngines.S3", level=3, num="7.1.1"),
        Heading(name="HDFS Table Engine", level=2, num="7.2"),
        Heading(name="RQ.HivePartitioning.TableEngines.HDFS", level=3, num="7.2.1"),
        Heading(name="Hive Table Engine", level=2, num="7.3"),
        Heading(name="RQ.HivePartitioning.TableEngines.Hive", level=3, num="7.3.1"),
        Heading(name="S3 Table Engine Writes", level=1, num="8"),
        Heading(name="RQ.HivePartitioning.Writes.S3", level=2, num="8.1"),
        Heading(name="Partition Strategy Parameter", level=2, num="8.2"),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionStrategy", level=3, num="8.2.1"
        ),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument",
            level=3,
            num="8.2.2",
        ),
        Heading(name="Partition Columns In Data File Parameter", level=2, num="8.3"),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFile",
            level=3,
            num="8.3.1",
        ),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy",
            level=3,
            num="8.3.2",
        ),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgument",
            level=3,
            num="8.3.3",
        ),
        Heading(name="Path Parameter", level=2, num="8.4"),
        Heading(name="RQ.HivePartitioning.Writes.Path", level=3, num="8.4.1"),
        Heading(name="RQ.HivePartitioning.Writes.InvalidPath", level=3, num="8.4.2"),
        Heading(name="Filename Parameter", level=2, num="8.5"),
        Heading(name="RQ.HivePartitioning.Writes.Filename", level=3, num="8.5.1"),
        Heading(
            name="RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy",
            level=3,
            num="8.5.2",
        ),
        Heading(
            name="RQ.HivePartitioning.Writes.NotDefinedFilename", level=3, num="8.5.3"
        ),
        Heading(name="S3 Engine Parameters", level=2, num="8.6"),
        Heading(
            name="RQ.HivePartitioning.Writes.S3EngineParameters", level=3, num="8.6.1"
        ),
        Heading(
            name="RQ.HivePartitioning.Writes.UseHivePartitions", level=3, num="8.6.2"
        ),
        Heading(name="Writes By Partitions And Parts", level=2, num="8.7"),
        Heading(
            name="RQ.HivePartitioning.Writes.PartitionsParts", level=3, num="8.7.1"
        ),
        Heading(name="Using Expressions In Partition By Clause", level=2, num="8.8"),
        Heading(name="RQ.HivePartitioning.Writes.Expressions", level=3, num="8.8.1"),
        Heading(name="Inserting Into Existing File", level=2, num="8.9"),
        Heading(name="RQ.HivePartitioning.Writes.FileExist", level=3, num="8.9.1"),
        Heading(name="Missing Partition By Column", level=2, num="8.10"),
        Heading(name="RQ.HivePartitioning.Writes.MissingColumn", level=3, num="8.10.1"),
        Heading(name="Using Default Value ", level=2, num="8.11"),
        Heading(name="RQ.HivePartitioning.Writes.DefaultValue", level=3, num="8.11.1"),
        Heading(name="Using Nullable Datatypes", level=2, num="8.12"),
        Heading(
            name="RQ.HivePartitioning.Writes.NullableDataType", level=3, num="8.12.1"
        ),
        Heading(name="Supported Data Types", level=2, num="8.13"),
        Heading(
            name="RQ.HivePartitioning.Writes.SupportedDataTypes", level=3, num="8.13.1"
        ),
        Heading(name="Unsupported Types", level=2, num="8.14"),
        Heading(
            name="RQ.HivePartitioning.Writes.DataTypesUnsupported",
            level=3,
            num="8.14.1",
        ),
        Heading(name="Using ReadOnly Bucket", level=2, num="8.15"),
        Heading(
            name="RQ.HivePartitioning.Writes.ReadOnlyBucket", level=3, num="8.15.1"
        ),
        Heading(name="Non-Accessible Bucket", level=2, num="8.16"),
        Heading(
            name="RQ.HivePartitioning.Writes.NonAccessibleBucket", level=3, num="8.16.1"
        ),
        Heading(name="Parallel Inserts", level=2, num="8.17"),
        Heading(
            name="RQ.HivePartitioning.Writes.ParallelInserts", level=3, num="8.17.1"
        ),
        Heading(name="Failing Write", level=2, num="8.18"),
        Heading(name="RQ.HivePartitioning.Writes.WriteFail", level=3, num="8.18.1"),
        Heading(name="Partition By Clause", level=2, num="8.19"),
        Heading(name="RQ.HivePartitioning.Writes.PartitionBy", level=3, num="8.19.1"),
        Heading(name="RQ.HivePartitioning.Writes.PartitionKey", level=3, num="8.19.2"),
    ),
    requirements=(
        RQ_HivePartitioning_Support,
        RQ_HivePartitioning_EnableSetting,
        RQ_HivePartitioning_Generic_Pruning,
        RQ_HivePartitioning_Generic_Performance,
        RQ_HivePartitioning_Generic_Encoding,
        RQ_HivePartitioning_VirtualColumns,
        RQ_HivePartitioning_VirtualColumns_ReadOnly,
        RQ_HivePartitioning_VirtualColumns_Appearance,
        RQ_HivePartitioning_VirtualColumns_Accessibility,
        RQ_HivePartitioning_VirtualColumns_InvalidPath,
        RQ_HivePartitioning_VirtualColumns_NameConflict,
        RQ_HivePartitioning_VirtualColumns_HiveDisabled,
        RQ_HivePartitioning_VirtualColumns_NonExistingKey,
        RQ_HivePartitioning_HivePartitionValue,
        RQ_HivePartitioning_HivePartitionValue_EmptyValue,
        RQ_HivePartitioning_Wildcards,
        RQ_HivePartitioning_Wildcards_SingleStar,
        RQ_HivePartitioning_Wildcards_DoubleStar,
        RQ_HivePartitioning_Wildcards_QuestionMark,
        RQ_HivePartitioning_Wildcards_List,
        RQ_HivePartitioning_Wildcards_WrongList,
        RQ_HivePartitioning_Wildcards_Range,
        RQ_HivePartitioning_Wildcards_WrongRange,
        RQ_HivePartitioning_Wildcards_Escaping,
        RQ_HivePartitioning_TableFunction_S3,
        RQ_HivePartitioning_TableFunction_S3Cluster,
        RQ_HivePartitioning_TableFunction_HDFS,
        RQ_HivePartitioning_TableEngines_S3,
        RQ_HivePartitioning_TableEngines_HDFS,
        RQ_HivePartitioning_TableEngines_Hive,
        RQ_HivePartitioning_Writes_S3,
        RQ_HivePartitioning_Writes_PartitionStrategy,
        RQ_HivePartitioning_Writes_PartitionStrategyWrongArgument,
        RQ_HivePartitioning_Writes_PartitionColumnsInDataFile,
        RQ_HivePartitioning_Writes_PartitionColumnsInDataFileWithoutHivePartitionStrategy,
        RQ_HivePartitioning_Writes_PartitionColumnsInDataFileWrongArgument,
        RQ_HivePartitioning_Writes_Path,
        RQ_HivePartitioning_Writes_InvalidPath,
        RQ_HivePartitioning_Writes_Filename,
        RQ_HivePartitioning_Writes_FilenameWithoutHivePartitionStrategy,
        RQ_HivePartitioning_Writes_NotDefinedFilename,
        RQ_HivePartitioning_Writes_S3EngineParameters,
        RQ_HivePartitioning_Writes_UseHivePartitions,
        RQ_HivePartitioning_Writes_PartitionsParts,
        RQ_HivePartitioning_Writes_Expressions,
        RQ_HivePartitioning_Writes_FileExist,
        RQ_HivePartitioning_Writes_MissingColumn,
        RQ_HivePartitioning_Writes_DefaultValue,
        RQ_HivePartitioning_Writes_NullableDataType,
        RQ_HivePartitioning_Writes_SupportedDataTypes,
        RQ_HivePartitioning_Writes_DataTypesUnsupported,
        RQ_HivePartitioning_Writes_ReadOnlyBucket,
        RQ_HivePartitioning_Writes_NonAccessibleBucket,
        RQ_HivePartitioning_Writes_ParallelInserts,
        RQ_HivePartitioning_Writes_WriteFail,
        RQ_HivePartitioning_Writes_PartitionBy,
        RQ_HivePartitioning_Writes_PartitionKey,
    ),
    content=r"""
# SRS-045 Hive Partitioning
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Generic Behavior](#generic-behavior)
    * 2.1 [RQ.HivePartitioning.Support](#rqhivepartitioningsupport)
    * 2.2 [RQ.HivePartitioning.EnableSetting](#rqhivepartitioningenablesetting)
    * 2.3 [RQ.HivePartitioning.Generic.Pruning](#rqhivepartitioninggenericpruning)
    * 2.4 [RQ.HivePartitioning.Generic.Performance](#rqhivepartitioninggenericperformance)
    * 2.5 [RQ.HivePartitioning.Generic.Encoding](#rqhivepartitioninggenericencoding)
* 3 [Virtual Columns](#virtual-columns)
    * 3.1 [RQ.HivePartitioning.VirtualColumns](#rqhivepartitioningvirtualcolumns)
    * 3.2 [RQ.HivePartitioning.VirtualColumns.ReadOnly](#rqhivepartitioningvirtualcolumnsreadonly)
    * 3.3 [RQ.HivePartitioning.VirtualColumns.Appearance](#rqhivepartitioningvirtualcolumnsappearance)
    * 3.4 [RQ.HivePartitioning.VirtualColumns.Accessibility](#rqhivepartitioningvirtualcolumnsaccessibility)
    * 3.5 [RQ.HivePartitioning.VirtualColumns.InvalidPath](#rqhivepartitioningvirtualcolumnsinvalidpath)
    * 3.6 [RQ.HivePartitioning.VirtualColumns.NameConflict](#rqhivepartitioningvirtualcolumnsnameconflict)
    * 3.7 [RQ.HivePartitioning.VirtualColumns.HiveDisabled](#rqhivepartitioningvirtualcolumnshivedisabled)
    * 3.8 [RQ.HivePartitioning.VirtualColumns.NonExistingKey](#rqhivepartitioningvirtualcolumnsnonexistingkey)
* 4 [Hive Partition Types Value](#hive-partition-types-value)
    * 4.1 [RQ.HivePartitioning.HivePartitionValue](#rqhivepartitioninghivepartitionvalue)
    * 4.2 [RQ.HivePartitioning.HivePartitionValue.EmptyValue](#rqhivepartitioninghivepartitionvalueemptyvalue)
* 5 [Wildcards](#wildcards)
    * 5.1 [RQ.HivePartitioning.Wildcards](#rqhivepartitioningwildcards)
    * 5.2 [RQ.HivePartitioning.Wildcards.SingleStar](#rqhivepartitioningwildcardssinglestar)
    * 5.3 [RQ.HivePartitioning.Wildcards.DoubleStar](#rqhivepartitioningwildcardsdoublestar)
    * 5.4 [RQ.HivePartitioning.Wildcards.QuestionMark](#rqhivepartitioningwildcardsquestionmark)
    * 5.5 [RQ.HivePartitioning.Wildcards.List](#rqhivepartitioningwildcardslist)
    * 5.6 [RQ.HivePartitioning.Wildcards.WrongList](#rqhivepartitioningwildcardswronglist)
    * 5.7 [RQ.HivePartitioning.Wildcards.Range](#rqhivepartitioningwildcardsrange)
    * 5.8 [RQ.HivePartitioning.Wildcards.WrongRange](#rqhivepartitioningwildcardswrongrange)
    * 5.9 [RQ.HivePartitioning.Wildcards.Escaping](#rqhivepartitioningwildcardsescaping)
* 6 [Supported Table Functions](#supported-table-functions)
    * 6.1 [RQ.HivePartitioning.TableFunction.S3](#rqhivepartitioningtablefunctions3)
    * 6.2 [RQ.HivePartitioning.TableFunction.S3Cluster](#rqhivepartitioningtablefunctions3cluster)
    * 6.3 [RQ.HivePartitioning.TableFunction.HDFS](#rqhivepartitioningtablefunctionhdfs)
* 7 [Supported Table Engines](#supported-table-engines)
    * 7.1 [S3 Table Engine](#s3-table-engine)
        * 7.1.1 [RQ.HivePartitioning.TableEngines.S3](#rqhivepartitioningtableenginess3)
    * 7.2 [HDFS Table Engine](#hdfs-table-engine)
        * 7.2.1 [RQ.HivePartitioning.TableEngines.HDFS](#rqhivepartitioningtableengineshdfs)
    * 7.3 [Hive Table Engine](#hive-table-engine)
        * 7.3.1 [RQ.HivePartitioning.TableEngines.Hive](#rqhivepartitioningtableengineshive)
* 8 [S3 Table Engine Writes](#s3-table-engine-writes)
    * 8.1 [RQ.HivePartitioning.Writes.S3](#rqhivepartitioningwritess3)
    * 8.2 [Partition Strategy Parameter](#partition-strategy-parameter)
        * 8.2.1 [RQ.HivePartitioning.Writes.PartitionStrategy](#rqhivepartitioningwritespartitionstrategy)
        * 8.2.2 [RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument](#rqhivepartitioningwritespartitionstrategywrongargument)
    * 8.3 [Partition Columns In Data File Parameter](#partition-columns-in-data-file-parameter)
        * 8.3.1 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFile](#rqhivepartitioningwritespartitioncolumnsindatafile)
        * 8.3.2 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy](#rqhivepartitioningwritespartitioncolumnsindatafilewithouthivepartitionstrategy)
        * 8.3.3 [RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgument](#rqhivepartitioningwritespartitioncolumnsindatafilewrongargument)
    * 8.4 [Path Parameter](#path-parameter)
        * 8.4.1 [RQ.HivePartitioning.Writes.Path](#rqhivepartitioningwritespath)
        * 8.4.2 [RQ.HivePartitioning.Writes.InvalidPath](#rqhivepartitioningwritesinvalidpath)
    * 8.5 [Filename Parameter](#filename-parameter)
        * 8.5.1 [RQ.HivePartitioning.Writes.Filename](#rqhivepartitioningwritesfilename)
        * 8.5.2 [RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy](#rqhivepartitioningwritesfilenamewithouthivepartitionstrategy)
        * 8.5.3 [RQ.HivePartitioning.Writes.NotDefinedFilename](#rqhivepartitioningwritesnotdefinedfilename)
    * 8.6 [S3 Engine Parameters](#s3-engine-parameters)
        * 8.6.1 [RQ.HivePartitioning.Writes.S3EngineParameters](#rqhivepartitioningwritess3engineparameters)
        * 8.6.2 [RQ.HivePartitioning.Writes.UseHivePartitions](#rqhivepartitioningwritesusehivepartitions)
    * 8.7 [Writes By Partitions And Parts](#writes-by-partitions-and-parts)
        * 8.7.1 [RQ.HivePartitioning.Writes.PartitionsParts](#rqhivepartitioningwritespartitionsparts)
    * 8.8 [Using Expressions In Partition By Clause](#using-expressions-in-partition-by-clause)
        * 8.8.1 [RQ.HivePartitioning.Writes.Expressions](#rqhivepartitioningwritesexpressions)
    * 8.9 [Inserting Into Existing File](#inserting-into-existing-file)
        * 8.9.1 [RQ.HivePartitioning.Writes.FileExist](#rqhivepartitioningwritesfileexist)
    * 8.10 [Missing Partition By Column](#missing-partition-by-column)
        * 8.10.1 [RQ.HivePartitioning.Writes.MissingColumn](#rqhivepartitioningwritesmissingcolumn)
    * 8.11 [Using Default Value ](#using-default-value-)
        * 8.11.1 [RQ.HivePartitioning.Writes.DefaultValue](#rqhivepartitioningwritesdefaultvalue)
    * 8.12 [Using Nullable Datatypes](#using-nullable-datatypes)
        * 8.12.1 [RQ.HivePartitioning.Writes.NullableDataType](#rqhivepartitioningwritesnullabledatatype)
    * 8.13 [Supported Data Types](#supported-data-types)
        * 8.13.1 [RQ.HivePartitioning.Writes.SupportedDataTypes](#rqhivepartitioningwritessupporteddatatypes)
    * 8.14 [Unsupported Types](#unsupported-types)
        * 8.14.1 [RQ.HivePartitioning.Writes.DataTypesUnsupported](#rqhivepartitioningwritesdatatypesunsupported)
    * 8.15 [Using ReadOnly Bucket](#using-readonly-bucket)
        * 8.15.1 [RQ.HivePartitioning.Writes.ReadOnlyBucket](#rqhivepartitioningwritesreadonlybucket)
    * 8.16 [Non-Accessible Bucket](#non-accessible-bucket)
        * 8.16.1 [RQ.HivePartitioning.Writes.NonAccessibleBucket](#rqhivepartitioningwritesnonaccessiblebucket)
    * 8.17 [Parallel Inserts](#parallel-inserts)
        * 8.17.1 [RQ.HivePartitioning.Writes.ParallelInserts](#rqhivepartitioningwritesparallelinserts)
    * 8.18 [Failing Write](#failing-write)
        * 8.18.1 [RQ.HivePartitioning.Writes.WriteFail](#rqhivepartitioningwriteswritefail)
    * 8.19 [Partition By Clause](#partition-by-clause)
        * 8.19.1 [RQ.HivePartitioning.Writes.PartitionBy](#rqhivepartitioningwritespartitionby)
        * 8.19.2 [RQ.HivePartitioning.Writes.PartitionKey](#rqhivepartitioningwritespartitionkey)


## Introduction

This document describes the requirements for the [ClickHouse] hive-style partitioning functionality. Hive-style partitioning refers to organizing files in a directory hierarchy where folder names encode column values (e.g. .../country=US/year=2021/file.parquet). [ClickHouse] provides functionality to read and write such partitioned data across various interfaces, including S3 and HDFS table functions and the Hive table engine. This allows users to query partitioned datasets efficiently by treating partition names as data columns and pruning unnecessary files. The following requirements describe the expected functionality and behavior for Hive-style partitioning support in [ClickHouse].

## Generic Behavior

### RQ.HivePartitioning.Support
version: 1.0

[ClickHouse] SHALL support interpreting Hive-style partitioned paths (subdirectories in the form `name=value`) as virtual columns when accessing external data sources. This enables querying partitioned data using partition columns directly, without requiring manual parsing of file paths.

For example:

```sql
SET use_hive_partitioning=1
```

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

In this example, date is a virtual column automatically extracted from directory names.

### RQ.HivePartitioning.EnableSetting
version: 1.0

[ClickHouse] SHALL support session-scoped setting `use_hive_partitioning` to toggle Hive-style partition recognition for file-based table engines and table functions. By default, in versions where it is disabled, users SHALL enable this setting to activate partition discovery.

```sql
set use_hive_partitioning=1
```

### RQ.HivePartitioning.Generic.Pruning
version: 1.0

[ClickHouse] SHALL only read files from partitions that satisfy query filters when Hive-style partitioning is enabled and the query includes filters on partition columns. In other words, partition pruning SHALL occur to avoid listing or scanning files in irrelevant directories. This behavior improves query performance by reducing I/O on external storage.

For example:

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

```sql
SET use_hive_partitioning=1

CREATE TABLE sales(...)
Engine=S3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')

SELECT * FROM sales WHERE date='2025-01-02'
```

In the example select SHALL read only the second file.

### RQ.HivePartitioning.Generic.Performance
version: 1.0

[ClickHouse] SHALL execute queries with `use_hive_partitioning = 1` faster than with `use_hive_partitioning = 0` when some files from storage are pruned using a `WHERE` clause on partition columns. This behavior is expected because Hive-style partitioning enables [ClickHouse] to skip irrelevant directories, reducing I/O and query execution time.


For example:

```
Structure:
 - /data/sales/date=2025-01-01/file1.parquet  
 - /data/sales/date=2025-01-02/file2.parquet  
 - /data/sales/date=2025-01-03/file3.parquet
```

```sql
-- Hive partition disabled
SET use_hive_partitioning = 0;

SELECT * FROM sales WHERE date = '2025-01-02';

-- Hive partition enabled
SET use_hive_partitioning = 1;

SELECT * FROM sales WHERE date = '2025-01-02';
```

In this example, the second query (with pruning enabled) SHALL complete faster than the first one.

### RQ.HivePartitioning.Generic.Encoding
version: 1.0

[ClickHouse] SHALL support URL-encoded values in Hive-style partition paths. 
Encoded characters in the `key=value` segments of the path SHALL be decoded before being exposed as virtual column values.
For example:

```
Path: 
/city=New%20York/file.parquet
```

In this Example, [ClickHouse] SHALL recognize:

key = 'city'

value = 'New York' (decoded from %20)


## Virtual Columns

### RQ.HivePartitioning.VirtualColumns
version: 1.0

[ClickHouse] SHALL create a virtual column for each partition key present in the file path, using the same name as the partition key.  

For example, given a path segment `/city=London/`, a virtual column `city` SHALL be available with the value `'London'` for all rows read from that directory.

```
Structure:
 - /data/trips/city=London/file1.parquet
 - /data/trips/city=Berlin/file2.parquet
```

```sql
SET use_hive_partitioning = 1;

SELECT DISTINCT city FROM trips ORDER BY city;
```

Expected output:
```
Berlin  
London
```

### RQ.HivePartitioning.VirtualColumns.ReadOnly
version: 1.0

[ClickHouse] SHALL treat virtual columns created by Hive-style partitioning as read-only. Any attempt to modify, insert into, or otherwise write to these columns SHALL result in an error.
[ClickHouse] SHALL return the following error if a write operation targets a virtual column: `DB::Exception: Failed to check existence of a key`.


### RQ.HivePartitioning.VirtualColumns.Appearance
version: 1.0

[ClickHouse] SHALL not return virtual columns created by Hive-style partitioning in the query output unless they are explicitly selected.
[Clickhouse] SHALL not return virtual columns for `DESCRIBE TABLE` query.
For example:

```
Structure:
 - /data/sales/city=London/file1.parquet
 - /data/sales/city=Berlin/file2.parquet
```

```sql
SET use_hive_partitioning = 1;

SELECT * FROM sales;
```

The city column SHALL NOT appear in the result set, because it was not selected explicitly.

### RQ.HivePartitioning.VirtualColumns.Accessibility
version: 1.0

Virtual columns created by Hive-style partitioning SHALL be accessible in queries.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT date
FROM s3('https://<bucket>/data/sales', 'access_key', 'secret_key', 'Parquet')
WHERE date = '2020-01-01';
```

In this example, date is not a physical column in the file, but a virtual column automatically derived from the file path (e.g., /date=2020-01-01/).
[ClickHouse] SHALL allow filtering and selecting by this column as part of query execution.


### RQ.HivePartitioning.VirtualColumns.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error  
`DB::Exception: Failed to check existence of a key`  
if the path defined in the query is invalid or the underlying storage does not contain the expected files.

This includes cases such as:
- The path does not exist.
- The path does not conform to the Hive-style partitioning pattern (e.g., mismatched `key` or `value`).

### RQ.HivePartitioning.VirtualColumns.NameConflict
version: 1.0

[ClickHouse] SHALL NOT use a virtual column if its name conflicts with the name of an existing table column.
[ClickHouse] SHALL treat column names in this comparison as case-sensitive.
This ensures that explicitly defined table columns always take precedence over virtual columns derived from partitioned paths.


For example:

```
Structure:
 - /data/events/date=2024-01-01/file1.parquet
```

```sql
SET use_hive_partitioning = 1;

CREATE TABLE events
(
    id UInt32,
    date Date
)
ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');

SELECT date FROM events WHERE id = 1;
```
In this example, the value of the date column SHALL come from the Parquet file, not from the path segment date=2024-01-01.
The virtual column date SHALL be ignored due to the name conflict with the real column date in the schema.

### RQ.HivePartitioning.VirtualColumns.HiveDisabled
version: 1.0

[ClickHouse] SHALL NOT create virtual columns if the `use_hive_partitioning` setting is disabled.


```
SET use_hive_partitioning=0
```

### RQ.HivePartitioning.VirtualColumns.NonExistingKey
version: 1.0

[ClickHouse] SHALL return `Unknown identifier` error if a query refers to nonexisting partition key.

For example:

```
Structure:
 - /data/events/date=2024-01-01/file1.parquet
```

```sql
SET use_hive_partitioning = 1;

CREATE TABLE events
(
    id UInt32,
)
ENGINE = S3('https://<bucket>/data/events', 'access_key', 'secret_key', 'Parquet');

SELECT region FROM events
```
In this example, the virtual column region does not exist in the partitioned path or in the Parquet file schema.


## Hive Partition Types Value

### RQ.HivePartitioning.HivePartitionValue
version: 1.0

Partition values extracted from Hive-style partitioned paths SHALL be treated as LowCardinality(String), with no implicit type inference during schema construction.

This ensures that values such as '2024-01-01', '123', or 'true' are interpreted as string literals by default.
[ClickHouse] SHALL allow these values to be explicitly cast by the user or automatically cast by the query engine if the query context requires it (e.g., in a WHERE clause comparing to a typed column).

### RQ.HivePartitioning.HivePartitionValue.EmptyValue
version: 1.0

The partition value SHALL be an empty string (`''`) if a directory in the path is missing a value.

For example:

```
Structure:
 - /data/events/city=/file1.parquet
```

```sql
SELECT city FROM events;
```

In this example, select SHALL return ''.


## Wildcards

### RQ.HivePartitioning.Wildcards
version: 1.0

[ClickHouse] SHALL support glob-style wildcards when resolving paths in Hive-style partitioning.


### RQ.HivePartitioning.Wildcards.SingleStar
version: 1.0

[ClickHouse] SHALL support the `*` wildcard in Hive-style partitioning.  
The `*` wildcard SHALL match any sequence of characters excluding `/`.

For example:
```sql
SELECT * FROM s3('https://<bucket>/data/year=*/month=*/', ...);
```

### RQ.HivePartitioning.Wildcards.DoubleStar
version: 1.0

[ClickHouse] SHALL support the `**` wildcard in Hive-style partitioning.  
The `**` wildcard SHALL match any sequence of characters including `/`.

for example:

```sql
SELECT * FROM s3('https://<bucket>/data/**/file.parquet', ...);
```

### RQ.HivePartitioning.Wildcards.QuestionMark
version: 1.0

[ClickHouse] SHALL support the `?` wildcard in Hive-style partitioning.  
The `?` wildcard SHALL match a single character, excluding `/`.

For example:

```sql
SELECT * FROM s3('https://<bucket>/data/year=202?', ...);
```

### RQ.HivePartitioning.Wildcards.List
version: 1.0

[ClickHouse] SHALL support the `{a[,b][,c]...}` wildcard syntax for Hive-style partitioning.  
This wildcard SHALL match one of the listed values.


For example
```sql
SELECT * FROM s3('https://<bucket>/data/month={01,02,03}/', ...);
```

### RQ.HivePartitioning.Wildcards.WrongList
version: 1.0

[ClickHouse] SHALL return an error if one or more paths specified in a `{a[,b]...}` list do not exist.

### RQ.HivePartitioning.Wildcards.Range
version: 1.0

[ClickHouse] SHALL support the `{N..M}` numerical range wildcard in Hive-style partitioning.  
This wildcard SHALL expand to all integers from `N` to `M` inclusive.

```sql
SELECT * FROM s3('https://<bucket>/data/day={1..7}/', ...);
```

### RQ.HivePartitioning.Wildcards.WrongRange
version: 1.0

[ClickHouse] SHALL return an error if one or more values in the `{N..M}` range are invalid or the corresponding paths do not exist.

### RQ.HivePartitioning.Wildcards.Escaping
version: 1.0

[ClickHouse] SHALL allow escaping of wildcard characters (`*`, `?`, `{`, `}`) using a backslash (`\`) for literal matching.

Example:

```sql
SELECT * FROM s3('https://<bucket>/data/\{special\}/file.parquet', ...);
```

## Supported Table Functions

### RQ.HivePartitioning.TableFunction.S3
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `s3` table function when reading from the specified URL path.

If the S3 path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:

- Detect and interpret partition keys from the path.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT COUNT(*) 
FROM s3('s3://bucket/data/date=*/region=*/*.parquet', 'Parquet') 
WHERE region = 'EU' AND date >= '2022-01-01';
```
In this example, [ClickHouse] SHALL read only files matching the region='EU' and date >= '2022-01-01' filters,
and expose date and region as virtual columns.

### RQ.HivePartitioning.TableFunction.S3Cluster
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `s3Cluster` table function when reading across a cluster.

On each cluster node, the function SHALL:

- Detect and interpret partition keys from the S3 path using `name=value` directory structure.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters, just like the `s3` table function.

This ensures that distributed querying of S3-partitioned datasets is consistent and efficient across all cluster nodes, reading only the necessary files per node.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT COUNT(*)
FROM s3Cluster('my_cluster', 's3://bucket/data/date=*/region=*/*.parquet', 'Parquet')
WHERE region = 'EU' AND date >= '2022-01-01';
```

### RQ.HivePartitioning.TableFunction.HDFS
version: 1.0

[ClickHouse] SHALL support Hive-style partitioning with the `hdfs` table function when reading from the specified HDFS URL path.

If the path contains wildcard patterns corresponding to `name=value` directories and `use_hive_partitioning` is enabled, [ClickHouse] SHALL:

- Detect and interpret partition keys from the directory structure.
- Expose corresponding virtual columns.
- Prune irrelevant partitions based on query filters.

For example:

```sql
SET use_hive_partitioning = 1;

SELECT *
FROM hdfs('hdfs://namenode/data/year=*/region=*/*.parquet', 'Parquet')
WHERE region = 'US' AND year = '2023';
```

## Supported Table Engines

### S3 Table Engine

#### RQ.HivePartitioning.TableEngines.S3
version: 1.0

[ClickHouse] SHALL support reading from the `S3` table engine with Hive-style partitioning.  
Partitioning columns SHALL be explicitly defined in the `PARTITION BY` clause of the table definition.

For example:

```sql
SET use_hive_partitioning = 1;

CREATE TABLE s3_engine_table
(
    x Int64
)
ENGINE = S3('https://<bucket>/data/{date}/file.parquet', 'access_key', 'secret_key', 'Parquet')
PARTITION BY date;
```
In this example, [ClickHouse] SHALL extract the date value from the file path and expose it as a virtual column.

### HDFS Table Engine

#### RQ.HivePartitioning.TableEngines.HDFS
version: 1.0

[ClickHouse] SHALL support reading from the HDFS table engine with Hive-style partitioning.
Partitioning columns SHALL be explicitly defined in the PARTITION BY clause.

For example:

```sql
SET use_hive_partitioning = 1;

CREATE TABLE hdfs_sales
(
    x Int64
)
ENGINE = HDFS('hdfs:///data/{date}/file.parquet', 'Parquet')
PARTITION BY date;
```
In this example, [ClickHouse] SHALL use the date segment from the path as a virtual partition column.

### Hive Table Engine

#### RQ.HivePartitioning.TableEngines.Hive
version: 1.0

[ClickHouse] SHALL support reading from the Hive table engine with Hive-style partitioning.
Partitioning columns SHALL be defined in the Hive Metastore.

```sql
SET use_hive_partitioning = 1;

CREATE TABLE hive_table
(
    x Int64
)
ENGINE = Hive('thrift://metastore:9083', 'default', 'sales');
```
In this example, [ClickHouse] SHALL detect partition columns from the Hive Metastore schema
and expose them as virtual columns during query execution.

## S3 Table Engine Writes

### RQ.HivePartitioning.Writes.S3
version: 1.0

[ClickHouse] SHALL support Hive-style partitioned writes using the `S3` table engine.

For example:

```sql
CREATE TABLE hive_writes
(
    year UInt16,
    country String,
    x UInt8
)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2022, 'USA', 1),
    (2022, 'Canada', 2);
```

In this example, [ClickHouse] SHALL write each row into a separate Hive-style partition path:

```
Structure:
 - /year=2022/country=Germany/...
 - /year=2022/country=France/...
```

### Partition Strategy Parameter

#### RQ.HivePartitioning.Writes.PartitionStrategy
version: 1.0

[ClickHouse] SHALL support the `partition_strategy` parameter in the `S3` table engine definition. This parameter determines whether Hive-style partitioned writes are enabled.

[ClickHouse] SHALL support the following values for `partition_strategy`:

- `'hive'`: Enables Hive-style partitioned writes. Data will be written into partitioned paths based on the `PARTITION BY` clause (e.g., `/key=value/`).
- `'auto'`: Disables Hive-style partitioning. Data will be written without creating Hive-style partition directories.

If the `partition_strategy` parameter is not explicitly specified, it SHALL default to `'auto'`.


```sql
ENGINE = S3(s3_conn,..., partition_strategy='hive')
```

#### RQ.HivePartitioning.Writes.PartitionStrategyWrongArgument
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Unknown partitioning style ` if the `partition_strategy` parameter is set to a value other than `'auto'` or `'hive'`.

### Partition Columns In Data File Parameter

#### RQ.HivePartitioning.Writes.PartitionColumnsInDataFile
version: 1.0

[ClickHouse] SHALL support the `partition_columns_in_data_file` parameter in the `S3` table engine definition if `partition_strategy='hive'`.

This parameter controls whether columns used in the `PARTITION BY` clause are also written into the data files.

- If `partition_columns_in_data_file = true`, partition columns SHALL be included in the file.
- If `partition_columns_in_data_file = false`, partition columns SHALL NOT be included in the file and are expected to be inferred from the path (e.g., `/key=value/`).

By default, `partition_columns_in_data_file` SHALL be set to `false`.

```sql
ENGINE = S3(s3_conn,..., partition_columns_in_data_file=1)
```

#### RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWithoutHivePartitionStrategy
version: 1.0

[ClickHouse] SHALL return an error if `partition_columns_in_data_file` is specified but `partition_strategy='auto'` or not defined.

#### RQ.HivePartitioning.Writes.PartitionColumnsInDataFileWrongArgument
version: 1.0

[ClickHouse] SHALL return an error if the `partition_columns_in_data_file` parameter is assigned a value that cannot be interpreted as a Boolean.

### Path Parameter

#### RQ.HivePartitioning.Writes.Path
version: 1.0

[ClickHouse] SHALL support the `path` parameter in the `S3` table engine definition to specify the full bucket path used as the root for Hive-style partitioned writes.
The `path` parameter SHALL define the S3 bucket and optional prefix under which partitioned files will be created. 
Partition subdirectories (e.g., `/key=value/`) and filenames defined by `filename` will be appended to this base path automatically.

#### RQ.HivePartitioning.Writes.InvalidPath
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Invalid S3 key` if the defined `path` parameter is invalid in the context of Hive-style partitioning with the `S3` table engine.

This includes cases where the `path`:

- Is not a valid S3 URI.
- Contains illegal characters.

### Filename Parameter

#### RQ.HivePartitioning.Writes.Filename
version: 1.0

[ClickHouse] SHALL support the `filename` parameter in the `S3` table engine definition to specify a directory that SHALL be prepended before all Hive-style partition directories.
[ClickHouse] SHALL support this parameter only if `partition_strategy='hive'`.

The full write path SHALL be constructed as:
```
<path>/<filename>/<key1>=<value1>/<key2>=<value2>/...
```

#### RQ.HivePartitioning.Writes.FilenameWithoutHivePartitionStrategy
version: 1.0

[ClickHouse] SHALL return an error if `filename` is specified but `partition_strategy='auto'` or not defined.

#### RQ.HivePartitioning.Writes.NotDefinedFilename
version: 1.0

[ClickHouse] SHALL write partitioned data directly into the root `path` if the `filename` parameter is not defined and `partition_strategy` is set to `'hive'`.


In this case, the write path SHALL be constructed as:

```
<path>//<key1>=<value1>/<key2>=<value2>/...
```

### S3 Engine Parameters

#### RQ.HivePartitioning.Writes.S3EngineParameters
version: 1.0

[ClickHouse] SHALL NOT alter the behavior of the following S3 engine parameters when `partition_strategy` is set to `'hive'`:

- `aws_access_key_id`
- `aws_secret_access_key`
- `format`
- `compression`

#### RQ.HivePartitioning.Writes.UseHivePartitions
version: 1.0

[ClickHouse] SHALL ignore the `use_hive_partitioning = 0` setting during write operations if `partition_strategy = 'hive'` is explicitly specified.

For example:

```sql
SET use_hive_partitioning = 0;

CREATE TABLE hive_writes
(
    year UInt16,
    country String,
    x UInt8
)
ENGINE = S3(s3_conn, filename = 'filename', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

INSERT INTO hive_writes VALUES
    (2023, 'Germany', 10),
    (2023, 'France', 20);
```

In this example,[ClickHouse] SHALL write the data into Hive-style partitioned paths:
```
Structure:
 - /year=2023/country=Germany/...
 - /year=2023/country=France/...
```
### Writes By Partitions And Parts

#### RQ.HivePartitioning.Writes.PartitionsParts
version: 1.0

[ClickHouse] SHALL support writing data into multiple Hive-style partition paths when using the `S3` table engine with `partition_strategy = 'hive'`.

This includes:
- Writing rows to multiple partition paths within a single `INSERT`.
- Writing to the same or different partitions across multiple `INSERT`s

### Using Expressions In Partition By Clause

#### RQ.HivePartitioning.Writes.Expressions
version: 1.0

[ClickHouse] SHALL return an error if the `PARTITION BY` clause contains an expression, when using `partition_strategy = 'hive'`.

Only column names are allowed in the `PARTITION BY` clause for Hive-style partitioning.

For example:

```sql
CREATE TABLE hive_invalid
(
    year UInt16,
    month UInt8,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY toString(year);
```

### Inserting Into Existing File

#### RQ.HivePartitioning.Writes.FileExist
version: 1.0

[ClickHouse] SHALL append data by creating a new file in the existing partition directory when writing via the S3 table engine with partition_strategy = 'hive'.

If a file already exists at the target partition path, [ClickHouse] SHALL create a new file alongside it, without deleting or overwriting existing content.

### Missing Partition By Column

#### RQ.HivePartitioning.Writes.MissingColumn
version: 1.0

[ClickHouse] SHALL return an error if any column defined in the `PARTITION BY` clause is missing from the table schema.

For example:

```sql
CREATE TABLE hive_sales
(
    year UInt16,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);
```

### Using Default Value 

#### RQ.HivePartitioning.Writes.DefaultValue
version: 1.0

[ClickHouse] SHALL use the default value defined in the table schema for any partitioning column that is omitted during `INSERT`, when writing with `partition_strategy = 'hive'`.


For example:

```sql
CREATE TABLE hive_sales
(
    year UInt16 DEFAULT 2023,
    country String DEFAULT 'Unknown',
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'file.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (year, country);

INSERT INTO hive_sales (value) VALUES (100);
```

In this example, [ClickHouse] SHALL write to the following partition path:

```
Structure:
 - /year=2023/country=Unknown/file.parquet
```

### Using Nullable Datatypes

#### RQ.HivePartitioning.Writes.NullableDataType
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` 
if any column defined in the `PARTITION BY` clause is of a nullable data type when using `partition_strategy = 'hive'`.

### Supported Data Types

#### RQ.HivePartitioning.Writes.SupportedDataTypes
version: 1.0

[ClickHouse] SHALL support the following data types for Hive-style partitioning during write operations (`partition_strategy = 'hive'`)
if partition key satisfy all of the following conditions:

- The value length SHALL be less than 1024 characters.
- The value SHALL NOT contain special characters: `{}`, `\`, `/`, `"`, `'`, `*`, `?`.

The following data types are supported as partition keys:

| Data Type     | Supported |
|---------------|-----------|
| Int8          | ✅ Yes    |
| Int16         | ✅ Yes    |
| Int32         | ✅ Yes    |
| Int64         | ✅ Yes    |
| Int128        | ✅ Yes    |
| Int256        | ✅ Yes    |
| UInt8         | ✅ Yes    |
| UInt16        | ✅ Yes    |
| UInt32        | ✅ Yes    |
| UInt64        | ✅ Yes    |
| UInt128       | ✅ Yes    |
| UInt256       | ✅ Yes    |
| String        | ✅ Yes    |
| FixedString(N)| ✅ Yes    |
| Date          | ✅ Yes    |
| Date32        | ✅ Yes    |
| Time          | ✅ Yes    |
| Time64(N)     | ✅ Yes    |
| DateTime      | ✅ Yes    |
| DateTime64(N) | ✅ Yes    |
| Bool          | ✅ Yes    |

### Unsupported Types

#### RQ.HivePartitioning.Writes.DataTypesUnsupported
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Hive partitioning supports only partition columns of types` 
if the data type of any column defined in the `PARTITION BY` clause is not included in the list of supported types for Hive-style partitioning.

### Using ReadOnly Bucket

#### RQ.HivePartitioning.Writes.ReadOnlyBucket
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`
if bucket defined in S3 engine clause is read-only.

### Non-Accessible Bucket

#### RQ.HivePartitioning.Writes.NonAccessibleBucket
version: 1.0

[ClickHouse] SHALL return an error `DB::Exception: Failed to check existence of a key`
 if bucket defined in S3 engine clause is not accessible.

### Parallel Inserts

#### RQ.HivePartitioning.Writes.ParallelInserts
version: 1.0

[ClickHouse] SHALL support parallel inserts into the same Hive-style partition when writing with the `S3` table engine and `partition_strategy = 'hive'`.

Multiple concurrent `INSERT` operations targeting the same file or partition path SHALL succeed without data loss or corruption.

[ClickHouse] SHALL support parallel inserts from different users.

### Failing Write

#### RQ.HivePartitioning.Writes.WriteFail
version: 1.0

[ClickHouse] SHALL not leave any partial data if writing to one or more objects fails during Hive-style partitioned writes.

### Partition By Clause

#### RQ.HivePartitioning.Writes.PartitionBy
version: 1.0

[ClickHouse] SHALL perform Hive-style partitioned writes only if the table definition includes a valid `PARTITION BY` clause.

If the `PARTITION BY` clause is missing, and `partition_strategy = 'hive'` is specified, 
[ClickHouse] SHALL return an error `DB::Exception: Partition strategy hive can not be used without a PARTITION BY expression.`.

This ensures that directory-based partitioning structure is explicitly defined and not left ambiguous.

For example:

```sql
CREATE TABLE hive_data
(
    year UInt16,
    value UInt32
)
ENGINE = S3(s3_conn, filename = 'table', format = Parquet, partition_strategy = 'hive');
```
In this example, [ClickHouse] SHALL return an error.

#### RQ.HivePartitioning.Writes.PartitionKey
version: 1.0

[ClickHouse] SHALL create a directory path of the form `/key=value/` for each column defined in the `PARTITION BY` clause when performing Hive-style partitioned writes.
If the target file at the resulting path does not exist, it SHALL be created automatically.  
Inserted data SHALL be written into that file.

Partition keys may contain special characters that are safe for directory names (e.g., spaces, `-`, `_`, `%`), and these SHALL be properly encoded if required by the underlying filesystem or object storage.

For example:

```sql
CREATE TABLE hive_orders
(
    region String,
    year UInt16,
    order_id UInt64
)
ENGINE = S3(s3_conn, filename = 'orders.parquet', format = Parquet, partition_strategy = 'hive')
PARTITION BY (region, year);

INSERT INTO hive_orders VALUES ('North-America', 2024, 1);
```

```
Structure:
 - /region=North-America/year=2024/orders.parquet
```

[ClickHouse]: https://clickhouse.com
[s3]: https://clickhouse.com/docs/sql-reference/table-functions/s3
[s3Cluster]: https://clickhouse.com/docs/sql-reference/table-functions/s3Cluster
[HDFS]: https://clickhouse.com/docs/sql-reference/table-functions/hdfs
""",
)
