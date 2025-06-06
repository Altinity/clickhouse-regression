# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.240708.1162538.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Parquet = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support `Parquet` data format.\n" "\n"),
    link=None,
    level=2,
    num="5.1",
)

RQ_SRS_032_ClickHouse_Parquet_SupportedVersions = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.SupportedVersions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with the following versions: `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.4.0`, `2.6.0`, `2.7.0`, `2.8.0`, `2.9.0`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_SRS_032_ClickHouse_Parquet_ClickHouseLocal = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the usage of `clickhouse-local` with `Parquet` data format.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_SRS_032_ClickHouse_Parquet_Offsets = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Offsets",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting parquet files with offsets.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Offsets_MonotonicallyIncreasing = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Offsets.MonotonicallyIncreasing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting parquet files with monotonically increasing offsets.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="7.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Query_Cache = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Query.Cache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using the query cache functionality when working with the Parquet files.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to\n"
        "read data from Parquet files and insert data into tables or table functions.\n"
        "\n"
        "```sql\n"
        "INSERT INTO sometable\n"
        "FROM INFILE 'data.parquet' FORMAT Parquet;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_AutoDetectParquetFileFormat = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically detecting Parquet file format based on \n"
        "when using INFILE clause without explicitly specifying the format setting.\n"
        "\n"
        "```sql\n"
        "INSERT INTO sometable\n"
        "FROM INFILE 'data.parquet';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Glob = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Glob",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using glob patterns in file paths to import multiple Parquet files.\n"
        "\n"
        "> Multiple path components can have globs. For being processed file must exist and match to the whole path pattern (not only suffix or prefix).\n"
        ">\n"
        ">   - `*` — Substitutes any number of any characters except / including empty string.\n"
        ">   - `?` — Substitutes any single character.\n"
        ">   - `{some_string,another_string,yet_another_one}` — Substitutes any of strings 'some_string', 'another_string', 'yet_another_one'.\n"
        ">   - `{N..M}` — Substitutes any number in range from N to M including both borders.\n"
        ">   - `**` - Fetches all files inside the folder recursively.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Glob_MultiDirectory = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Glob.MultiDirectory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `{str1, ...}` globs across different directories when importing from the Parquet files. \n"
        "\n"
        "For example,\n"
        "\n"
        "> The following query will import both from a/1.parquet and b/2.parquet\n"
        "> \n"
        "> ```sql\n"
        "> SELECT\n"
        ">     *,\n"
        ">     _path,\n"
        ">     _file\n"
        "> FROM file('{a/1,b/2}.parquet', Parquet)\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Conversion = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Conversion",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing the Parquet files with the following datatypes and converting them into corresponding ClickHouse columns as described in the table.\n"
        "\n"
        "The conversion MAY not be possible between some datatypes.\n"
        ">\n"
        "> For example,\n"
        ">\n"
        "> `Bool` -> `IPv6`\n"
        "\n"
        "| Parquet to ClickHouse supported Datatypes     | ClickHouse Datatype Family        | alias_to Datatype | case_insensitive |\n"
        "|-----------------------------------------------|-----------------------------------|-------------------|------------------|\n"
        "|                                               | `JSON`                            |                   | 1                |\n"
        "|                                               | `Polygon`                         |                   | 0                |\n"
        "|                                               | `Ring`                            |                   | 0                |\n"
        "|                                               | `Point`                           |                   | 0                |\n"
        "|                                               | `SimpleAggregateFunction`         |                   | 0                |\n"
        "|                                               | `IntervalQuarter`                 |                   | 0                |\n"
        "|                                               | `IntervalMonth`                   |                   | 0                |\n"
        "| `INT64`                                       | `Int64`                           |                   | 0                |\n"
        "|                                               | `IntervalDay`                     |                   | 0                |\n"
        "|                                               | `IntervalHour`                    |                   | 0                |\n"
        "| `UINT32`                                      | `IPv4`                            |                   | 0                |\n"
        "|                                               | `IntervalSecond`                  |                   | 0                |\n"
        "|                                               | `LowCardinality`                  |                   | 0                |\n"
        "| `INT16`                                       | `Int16`                           |                   | 0                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `UInt256`                         |                   | 0                |\n"
        "|                                               | `AggregateFunction`               |                   | 0                |\n"
        "|                                               | `MultiPolygon`                    |                   | 0                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                            |                   | 0                |\n"
        "|                                               | `Nothing`                         |                   | 0                |\n"
        "|                                               | `Decimal256`                      |                   | 1                |\n"
        "| `STRUCT`                                      | `Tuple`                           |                   | 0                |\n"
        "| `LIST`                                        | `Array`                           |                   | 0                |\n"
        "|                                               | `IntervalMicrosecond`             |                   | 0                |\n"
        "|                                               | `Bool`                            |                   | 1                |\n"
        "| `INT16`                                       | `Enum16`                          |                   | 0                |\n"
        "|                                               | `IntervalMinute`                  |                   | 0                |\n"
        "|                                               | `FixedString`                     |                   | 0                |\n"
        "| `STRING`, `BINARY`                            | `String`                          |                   | 0                |\n"
        "| `TIME (ms)`                                   | `DateTime`                        |                   | 1                |\n"
        "|                                               | `Object`                          |                   | 0                |\n"
        "| `MAP`                                         | `Map`                             |                   | 0                |\n"
        "|                                               | `UUID`                            |                   | 0                |\n"
        "|                                               | `Decimal64`                       |                   | 1                |\n"
        "|                                               | `Nullable`                        |                   | 0                |\n"
        "|                                               | `Enum`                            |                   | 1                |\n"
        "| `INT32`                                       | `Int32`                           |                   | 0                |\n"
        "| `UINT8`, `BOOL`                               | `UInt8`                           |                   | 0                |\n"
        "|                                               | `Date`                            |                   | 1                |\n"
        "|                                               | `Decimal32`                       |                   | 1                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `UInt128`                         |                   | 0                |\n"
        "| `DOUBLE`                                      | `Float64`                         |                   | 0                |\n"
        "|                                               | `Nested`                          |                   | 0                |\n"
        "| `UINT16`                                      | `UInt16`                          |                   | 0                |\n"
        "|                                               | `IntervalMillisecond`             |                   | 0                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`                          |                   | 0                |\n"
        "|                                               | `Decimal128`                      |                   | 1                |\n"
        "| `INT8`                                        | `Int8`                            |                   | 0                |\n"
        "| `DECIMAL`                                     | `Decimal`                         |                   | 1                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int256`                          |                   | 0                |\n"
        "| `TIMESTAMP (ms, ns, us)`, `TIME (us, ns)`     | `DateTime64`                      |                   | 1                |\n"
        "| `INT8`                                        | `Enum8`                           |                   | 0                |\n"
        "|                                               | `DateTime32`                      |                   | 1                |\n"
        "| `DATE (ms, ns, us)`                           | `Date32`                          |                   | 1                |\n"
        "|                                               | `IntervalWeek`                    |                   | 0                |\n"
        "| `UINT64`                                      | `UInt64`                          |                   | 0                |\n"
        "|                                               | `IntervalNanosecond`              |                   | 0                |\n"
        "|                                               | `IntervalYear`                    |                   | 0                |\n"
        "| `UINT32`                                      | `UInt32`                          |                   | 0                |\n"
        "| `FLOAT`                                       | `Float32`                         |                   | 0                |\n"
        "| `BOOL`                                        | `bool`                            | `Bool`            | 1                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `INET6`                           | `IPv6`            | 1                |\n"
        "| `UINT32`                                      | `INET4`                           | `IPv4`            | 1                |\n"
        "|                                               | `ENUM`                            | `Enum`            | 1                |\n"
        "| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `BINARY`                          | `FixedString`     | 1                |\n"
        "| `STRING`, `BINARY`                            | `GEOMETRY`                        | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NATIONAL CHAR VARYING`           | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `BINARY VARYING`                  | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NCHAR LARGE OBJECT`              | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NATIONAL CHARACTER VARYING`      | `String`          | 1                |\n"
        "|                                               | `boolean`                         | `Bool`            | 1                |\n"
        "| `STRING`, `BINARY`                            | `NATIONAL CHARACTER LARGE OBJECT` | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NATIONAL CHARACTER`              | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NATIONAL CHAR`                   | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHARACTER VARYING`               | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `LONGBLOB`                        | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `TINYBLOB`                        | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `MEDIUMTEXT`                      | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `TEXT`                            | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `VARCHAR2`                        | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHARACTER LARGE OBJECT`          | `String`          | 1                |\n"
        "| `DOUBLE`                                      | `DOUBLE PRECISION`                | `Float64`         | 1                |\n"
        "| `STRING`, `BINARY`                            | `LONGTEXT`                        | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NVARCHAR`                        | `String`          | 1                |\n"
        "|                                               | `INT1 UNSIGNED`                   | `UInt8`           | 1                |\n"
        "| `STRING`, `BINARY`                            | `VARCHAR`                         | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHAR VARYING`                    | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `MEDIUMBLOB`                      | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `NCHAR`                           | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `VARBINARY`                       | `String`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHAR`                            | `String`          | 1                |\n"
        "| `UINT16`                                      | `SMALLINT UNSIGNED`               | `UInt16`          | 1                |\n"
        "| `TIME (ms)`                                   | `TIMESTAMP`                       | `DateTime`        | 1                |\n"
        "| `DECIMAL`                                     | `FIXED`                           | `Decimal`         | 1                |\n"
        "| `STRING`, `BINARY`                            | `TINYTEXT`                        | `String`          | 1                |\n"
        "| `DECIMAL`                                     | `NUMERIC`                         | `Decimal`         | 1                |\n"
        "| `DECIMAL`                                     | `DEC`                             | `Decimal`         | 1                |\n"
        "| `INT64`                                       | `TIME`                            | `Int64`           | 1                |\n"
        "| `FLOAT`                                       | `FLOAT`                           | `Float32`         | 1                |\n"
        "| `UINT64`                                      | `SET`                             | `UInt64`          | 1                |\n"
        "|                                               | `TINYINT UNSIGNED`                | `UInt8`           | 1                |\n"
        "| `UINT32`                                      | `INTEGER UNSIGNED`                | `UInt32`          | 1                |\n"
        "| `UINT32`                                      | `INT UNSIGNED`                    | `UInt32`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `CLOB`                            | `String`          | 1                |\n"
        "| `UINT32`                                      | `MEDIUMINT UNSIGNED`              | `UInt32`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `BLOB`                            | `String`          | 1                |\n"
        "| `FLOAT`                                       | `REAL`                            | `Float32`         | 1                |\n"
        "|                                               | `SMALLINT`                        | `Int16`           | 1                |\n"
        "| `INT32`                                       | `INTEGER SIGNED`                  | `Int32`           | 1                |\n"
        "| `STRING`, `BINARY`                            | `NCHAR VARYING`                   | `String`          | 1                |\n"
        "| `INT32`                                       | `INT SIGNED`                      | `Int32`           | 1                |\n"
        "|                                               | `TINYINT SIGNED`                  | `Int8`            | 1                |\n"
        "| `INT64`                                       | `BIGINT SIGNED`                   | `Int64`           | 1                |\n"
        "| `STRING`, `BINARY`                            | `BINARY LARGE OBJECT`             | `String`          | 1                |\n"
        "|                                               | `SMALLINT SIGNED`                 | `Int16`           | 1                |\n"
        "|                                               | `YEAR`                            | `UInt16`          | 1                |\n"
        "| `INT32`                                       | `MEDIUMINT`                       | `Int32`           | 1                |\n"
        "| `INT32`                                       | `INTEGER`                         | `Int32`           | 1                |\n"
        "|                                               | `INT1 SIGNED`                     | `Int8`            | 1                |\n"
        "| `UINT64`                                      | `BIT`                             | `UInt64`          | 1                |\n"
        "| `UINT64`                                      | `BIGINT UNSIGNED`                 | `UInt64`          | 1                |\n"
        "| `STRING`, `BINARY`                            | `BYTEA`                           | `String`          | 1                |\n"
        "| `INT32`                                       | `INT`                             | `Int32`           | 1                |\n"
        "| `FLOAT`                                       | `SINGLE`                          | `Float32`         | 1                |\n"
        "| `INT32`                                       | `MEDIUMINT SIGNED`                | `Int32`           | 1                |\n"
        "| `DOUBLE`                                      | `DOUBLE`                          | `Float64`         | 1                |\n"
        "|                                               | `INT1`                            | `Int8`            | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHAR LARGE OBJECT`               | `String`          | 1                |\n"
        "|                                               | `TINYINT`                         | `Int8`            | 1                |\n"
        "| `INT64`                                       | `BIGINT`                          | `Int64`           | 1                |\n"
        "| `STRING`, `BINARY`                            | `CHARACTER`                       | `String`          | 1                |\n"
        "|                                               | `BYTE`                            | `Int8`            | 1                |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing the following Parquet data types:\n"
        "\n"
        "| Parquet data type                             | ClickHouse data type                  |\n"
        "|-----------------------------------------------|---------------------------------------|\n"
        "| `BOOL`                                        | `Bool`                                |\n"
        "| `UINT8`, `BOOL`                               | `UInt8`                               |\n"
        "| `INT8`                                        | `Int8`/`Enum8`                        |\n"
        "| `UINT16`                                      | `UInt16`                              |\n"
        "| `INT16`                                       | `Int16`/`Enum16`                      |\n"
        "| `UINT32`                                      | `UInt32`                              |\n"
        "| `INT32`                                       | `Int32`                               |\n"
        "| `UINT64`                                      | `UInt64`                              |\n"
        "| `INT64`                                       | `Int64`                               |\n"
        "| `FLOAT`                                       | `Float32`                             |\n"
        "| `DOUBLE`                                      | `Float64`                             |\n"
        "| `DATE (ms, ns, us)`                           | `Date32`                              |\n"
        "| `TIME (ms)`                                   | `DateTime`                            |\n"
        "| `TIMESTAMP (ms, ns, us)`, `TIME (us, ns)`     | `DateTime64`                          |\n"
        "| `STRING`, `BINARY`                            | `String`                              |\n"
        "| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `FixedString`                         |\n"
        "| `DECIMAL`                                     | `Decimal`                             |\n"
        "| `LIST`                                        | `Array`                               |\n"
        "| `STRUCT`                                      | `Tuple`                               |\n"
        "| `MAP`                                         | `Map`                                 |\n"
        "| `UINT32`                                      | `IPv4`                                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                                |\n"
        "| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`/`UInt128`/`Int256`/`UInt256` |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BLOB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BLOB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing parquet files with `BLOB` content.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BOOL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BOOL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `BOOL` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.4",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `UINT8` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.5",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `INT8` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.6",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `UINT16` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.7",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `INT16` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.8",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `UINT32` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.9",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `INT32` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.10",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `UINT64` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.11",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `INT64` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.12",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FLOAT = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FLOAT",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `FLOAT` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.13",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DOUBLE",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DOUBLE` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.14",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DATE` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.15",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DATE (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.16",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_ns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DATE (ns)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.17",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_us = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.us",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DATE (us)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.18",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIME_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIME.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIME (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.19",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIMESTAMP (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.20",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIMESTAMP (ns)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.21",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_us = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.us",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIMESTAMP (us)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.22",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRING",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `STRING` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.23",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BINARY = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BINARY",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `BINARY` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.24",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `FIXED_LENGTH_BYTE_ARRAY` Parquet datatype.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.25",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray_FLOAT16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray.FLOAT16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with the `FIXED_LENGTH_BYTE_ARRAY` primitive\n"
        "type and the `FLOAT16` logical type.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.26",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DECIMAL` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.27",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL_Filter = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL.Filter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DECIMAL` Parquet datatype with specified filters.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.4.28",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_LIST = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.LIST",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `LIST` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.29",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_ARRAY = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.ARRAY",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `ARRAY` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.30",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRUCT",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `STRUCT` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="9.4.31",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.MAP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support importing `MAP` Parquet datatype.\n" "\n"),
    link=None,
    level=3,
    num="9.4.32",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_DateUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.DateUTCAdjusted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `DATE` Parquet datatype with `isAdjustedToUTC = true`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.33.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_TimestampUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimestampUTCAdjusted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIMESTAMP` Parquet datatype with `isAdjustedToUTC = true`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.33.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_TimeUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimeUTCAdjusted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `TIME` Parquet datatype with `isAdjustedToUTC = true`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.33.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.NullValues",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing columns that have `Null` values in Parquet files. If the target [ClickHouse] column is not `Nullable` then the `Null` value should be converted to the default values for the target column datatype.\n"
        "\n"
        "For example, if the target column has `Int32`, then the `Null` value will be replaced with `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.34.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Nullable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files into target table's `Nullable` datatype columns.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.34.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_LowCardinality = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.LowCardinality",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files into target table's `LowCardinality` datatype columns.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.35.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Nested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files into target table's `Nested` datatype columns.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.36.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Unknown = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Unknown",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with `UNKNOWN` logical type.\n"
        "\n"
        "The example as to why the Parquet might have an `UNKNOWN` types is as follows,\n"
        "\n"
        "> Sometimes, when discovering the schema of existing data, values are always null and there's no type information. \n"
        "> The UNKNOWN type can be used to annotate a column that is always null. (Similar to Null type in Avro and Arrow)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.4.37.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support the following Parquet types:\n"
        "\n"
        "- `Time32`\n"
        "- `Fixed_Size_Binary`\n"
        "- `JSON`\n"
        "- `UUID`\n"
        "- `ENUM`\n"
        "- `Null`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported_ChunkedArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported.ChunkedArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet chunked arrays.\n" "\n"),
    link=None,
    level=3,
    num="9.5.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_FilterPushdown = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support filter pushdown functionality when importing from the Parquet files.\n"
        "\n"
        "> The functionality should behave similar to https://drill.apache.org/docs/parquet-filter-pushdown/\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_FilterPushdown_MinMax_Operations = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown.MinMax.Operations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Supported Operations |\n"
        "|----------------------|\n"
        "| =                    |\n"
        "| !=                   |\n"
        "| >                    |\n"
        "| <                    |\n"
        "| >=                   |\n"
        "| <=                   |\n"
        "| IN                   |\n"
        "| NOT IN               |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.6.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Projections = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Projections",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_SkipColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support skipping unexistent columns when importing from Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_SkipValues = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support skipping unsupported values when import from Parquet files. When the values are being skipped, the inserted values SHALL be the default value for the corresponding column's datatype.\n"
        "\n"
        "For example, trying to insert `Null` values into the non-`Nullable` column.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE TestTable\n"
        "(\n"
        "    `path` String,\n"
        "    `date` Date,\n"
        "    `hits` UInt32\n"
        ")\n"
        "ENGINE = MergeTree\n"
        "ORDER BY (date, path);\n"
        "\n"
        "SELECT *\n"
        "FROM file(output.parquet);\n"
        "\n"
        "┌─path───┬─date───────┬─hits─┐\n"
        "│ /path1 │ 2021-06-01 │   10 │\n"
        "│ /path2 │ 2021-06-02 │    5 │\n"
        "│ ᴺᵁᴸᴸ   │ 2021-06-03 │    8 │\n"
        "└────────┴────────────┴──────┘\n"
        "\n"
        "INSERT INTO TestTable\n"
        "FROM INFILE 'output.parquet' FORMAT Parquet;\n"
        "\n"
        "SELECT *\n"
        "FROM TestTable;\n"
        "\n"
        "┌─path───┬───────date─┬─hits─┐\n"
        "│ /path1 │ 2021-06-01 │   10 │\n"
        "│ /path2 │ 2021-06-02 │    5 │\n"
        "│        │ 2021-06-03 │    8 │\n"
        "└────────┴────────────┴──────┘\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_AutoTypecast = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL automatically typecast parquet datatype based on the types in the target table.\n"
        "\n"
        "For example,\n"
        "\n"
        "> When we take the following Parquet file:\n"
        "> \n"
        "> ```\n"
        "> ┌─path────────────────────────────────────────────────────────────┬─date───────┬──hits─┐\n"
        "> │ Akiba_Hebrew_Academy                                            │ 2017-08-01 │   241 │\n"
        "> │ 1980_Rugby_League_State_of_Origin_match                         │ 2017-07-01 │     2 │\n"
        "> │ Column_of_Santa_Felicita,_Florence                              │ 2017-06-01 │    14 │\n"
        "> └─────────────────────────────────────────────────────────────────┴────────────┴───────┘\n"
        "> ```\n"
        "> \n"
        "> ```\n"
        "> ┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐\n"
        "> │ path │ Nullable(String) │              │                    │         │                  │                │\n"
        "> │ date │ Nullable(String) │              │                    │         │                  │                │\n"
        "> │ hits │ Nullable(Int64)  │              │                    │         │                  │                │\n"
        "> └──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘\n"
        "> ```\n"
        "> \n"
        "> \n"
        "> Then create a table to import parquet data to:\n"
        "> ```sql\n"
        "> CREATE TABLE sometable\n"
        "> (\n"
        ">     `path` String,\n"
        ">     `date` Date,\n"
        ">     `hits` UInt32\n"
        "> )\n"
        "> ENGINE = MergeTree\n"
        "> ORDER BY (date, path)\n"
        "> ```\n"
        "> \n"
        "> Then import data using a FROM INFILE clause:\n"
        "> \n"
        "> \n"
        "> ```sql\n"
        "> INSERT INTO sometable\n"
        "> FROM INFILE 'data.parquet' FORMAT Parquet;\n"
        "> ```\n"
        "> \n"
        "> As a result ClickHouse automatically converted parquet `strings` (in the `date` column) to the `Date` type.\n"
        "> \n"
        "> \n"
        "> ```sql\n"
        "> DESCRIBE TABLE sometable\n"
        "> ```\n"
        "> \n"
        "> ```\n"
        "> ┌─name─┬─type───┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐\n"
        "> │ path │ String │              │                    │         │                  │                │\n"
        "> │ date │ Date   │              │                    │         │                  │                │\n"
        "> │ hits │ UInt32 │              │                    │         │                  │                │\n"
        "> └──────┴────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.10.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with different Row Group Sizes.\n"
        "\n"
        "As described in https://parquet.apache.org/docs/file-format/configurations/#row-group-size,\n"
        "\n"
        "> We recommend large row groups (512MB - 1GB). Since an entire row group might need to be read, \n"
        "> we want it to completely fit on one HDFS block.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.11.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_DataPageSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with different Data Page Sizes.\n"
        "\n"
        "As described in https://parquet.apache.org/docs/file-format/configurations/#data-page--size,\n"
        "\n"
        "> Note: for sequential scans, it is not expected to read a page at a time; this is not the IO chunk. We recommend 8KB for page sizes.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.12.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_NewTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.NewTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support creating and populating tables directly from the Parquet files with table schema being auto-detected\n"
        "from file's structure.\n"
        "\n"
        "For example,\n"
        "\n"
        "> Since ClickHouse reads parquet file schema, we can create tables on the fly:\n"
        "> \n"
        "> ```sql\n"
        "> CREATE TABLE imported_from_parquet\n"
        "> ENGINE = MergeTree\n"
        "> ORDER BY tuple() AS\n"
        "> SELECT *\n"
        "> FROM file('data.parquet', Parquet)\n"
        "> ```\n"
        "> \n"
        "> This will automatically create and populate a table from a given parquet file:\n"
        "> \n"
        "> ```sql\n"
        "> DESCRIBE TABLE imported_from_parquet;\n"
        "> ```\n"
        "> ```\n"
        "> ┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐\n"
        "> │ path │ Nullable(String) │              │                    │         │                  │                │\n"
        "> │ date │ Nullable(String) │              │                    │         │                  │                │\n"
        "> │ hits │ Nullable(Int64)  │              │                    │         │                  │                │\n"
        "> └──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.13.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Performance_CountFromMetadata = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Performance.CountFromMetadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing the information about the number of rows from Parquet file directly from the metadata instead of going through the whole file.\n"
        "\n"
        "For example,\n"
        "\n"
        "> When running this query,\n"
        "> \n"
        "> ```sql\n"
        "> SELECT count(*)\n"
        "> FROM file('*.parquet', 'Parquet');\n"
        ">\n"
        "> ┌───count()─┐\n"
        "> │ 110000000 │\n"
        "> └───────────┘\n"
        "> \n"
        "> Elapsed: 1.365 sec.\n"
        "> ```\n"
        "> \n"
        "> The runtime should be around ~16ms instead of 1.365 sec.\n"
        ">\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.14.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Performance_ParallelProcessing = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Performance.ParallelProcessing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support process parallelization when importing from the parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.14.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing nested columns from the Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_Complex = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.Complex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing nested: `Array`, `Tuple` and `Map` datatypes from Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support inserting arrays of nested structs from Parquet files into [ClickHouse] Nested columns when the `input_format_parquet_import_nested` setting is set to `1`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_NotImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] Nested columns when the\n"
        "`input_format_parquet_import_nested` setting is set to `0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.4",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNotNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] not Nested columns.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.5",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_NonArrayIntoNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when trying to insert datatypes other than arrays of nested structs from Parquet files into [ClickHouse] Nested columns.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.15.6",
)

RQ_SRS_032_ClickHouse_Parquet_Import_ChunkedColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing Parquet files with chunked columns.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.16.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Plain` encoded Parquet files.\n" "\n"
    ),
    link=None,
    level=4,
    num="9.17.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Dictionary` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Delta = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Delta Encoding` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Delta-length byte array` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaStrings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Delta Strings` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_ByteStreamSplit = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing `Byte Stream Split` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.17.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `input_format_parquet_import_nested` setting to allow inserting arrays of\n"
        "nested structs into Nested column type. The default value SHALL be `0`.\n"
        "\n"
        "- `0` — Data can not be inserted into Nested columns as an array of structs.\n"
        "- `1` — Data can be inserted into Nested columns as an array of structs.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.18.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_CaseInsensitiveColumnMatching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `input_format_parquet_case_insensitive_column_matching` setting to ignore matching\n"
        "Parquet and ClickHouse columns. The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.18.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_AllowMissingColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `input_format_parquet_allow_missing_columns` setting to allow missing columns.\n"
        "The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.18.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference` \n"
        "setting to allow skipping unsupported types. The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.18.4",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using various libraries.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="9.19.1",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries.Pyarrow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using `Pyarrow`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.19.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries.PySpark",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using `PySpark`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.19.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries.Pandas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using `Pandas`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.19.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries_ParquetGO = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries.ParquetGO",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using `parquet-go`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.19.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Libraries_H2OAI = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Libraries.H2OAI",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files generated using `H2OAI`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="9.19.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `SELECT` query with either the `INTO OUTFILE {file_name}` or just `FORMAT Parquet` clauses to Export Parquet files. \n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM sometable\n"
        "INTO OUTFILE 'export.parquet'\n"
        "FORMAT Parquet\n"
        "```\n"
        "\n"
        "or\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM sometable\n"
        "FORMAT Parquet\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Outfile_AutoDetectParquetFileFormat = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using OUTFILE clause without explicitly specifying the format setting.\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM sometable\n"
        "INTO OUTFILE 'export.parquet'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting the following datatypes to Parquet:\n"
        "\n"
        "| ClickHouse data type                  | Parquet data type         |\n"
        "|---------------------------------------|---------------------------|\n"
        "| `Bool`                                | `BOOL`                    |\n"
        "| `UInt8`                               | `UINT8`                   |\n"
        "| `Int8`/`Enum8`                        | `INT8`                    |\n"
        "| `UInt16`                              | `UINT16`                  |\n"
        "| `Int16`/`Enum16`                      | `INT16`                   |\n"
        "| `UInt32`                              | `UINT32`                  |\n"
        "| `Int32`                               | `INT32`                   |\n"
        "| `UInt64`                              | `UINT64`                  |\n"
        "| `Int64`                               | `INT64`                   |\n"
        "| `Float32`                             | `FLOAT`                   |\n"
        "| `Float64`                             | `DOUBLE`                  |\n"
        "| `Date32`                              | `DATE`                    |\n"
        "| `DateTime`                            | `UINT32`                  |\n"
        "| `DateTime64`                          | `TIMESTAMP`               |\n"
        "| `String`                              | `BINARY`                  |\n"
        "| `FixedString`                         | `FIXED_LENGTH_BYTE_ARRAY` |\n"
        "| `Decimal`                             | `DECIMAL`                 |\n"
        "| `Array`                               | `LIST`                    |\n"
        "| `Tuple`                               | `STRUCT`                  |\n"
        "| `Map`                                 | `MAP`                     |\n"
        "| `IPv4`                                | `UINT32`                  |\n"
        "| `IPv6`                                | `FIXED_LENGTH_BYTE_ARRAY` |\n"
        "| `Int128`/`UInt128`/`Int256`/`UInt256` | `FIXED_LENGTH_BYTE_ARRAY` |\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BLOB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BLOB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting parquet files with `BLOB` content.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BOOL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BOOL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `BOOL` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.3",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `UINT8` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.4",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `INT8` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.5",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `UINT16` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.6",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `INT16` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.7",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `UINT32` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.8",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `INT32` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.9",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `UINT64` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.10",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `INT64` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.11",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FLOAT = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FLOAT",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `FLOAT` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.12",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DOUBLE",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DOUBLE` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.13",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DATE` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.14",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DATE (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.15",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_ns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DATE (ns)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.16",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_us = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.us",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DATE (us)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.17",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIME_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIME.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `TIME (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.18",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `TIMESTAMP (ms)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.19",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `TIMESTAMP (ns)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.20",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_us = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.us",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `TIMESTAMP (us)` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.21",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRING",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `STRING` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.22",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BINARY = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BINARY",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `BINARY` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.23",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FixedLengthByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `FIXED_LENGTH_BYTE_ARRAY` Parquet datatype.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.24",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DECIMAL` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.25",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL_Filter = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL.Filter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `DECIMAL` Parquet datatype with specified filters.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.26",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_LIST = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.LIST",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `LIST` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.27",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_ARRAY = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.ARRAY",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `ARRAY` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.28",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRUCT",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `STRUCT` Parquet datatype.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.3.29",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.MAP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support exporting `MAP` Parquet datatype.\n" "\n"),
    link=None,
    level=3,
    num="10.3.30",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Nullable` datatypes to Parquet files and `Nullable` datatypes that consist only of `Null`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.3.31",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Nested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Nested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting nested columns to the Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Nested_Complex = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Nested.Complex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting nested: `Array`, `Tuple` and `Map` datatypes to Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_ChunkedColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.ChunkedColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting chunked columns to Parquet files.\n" "\n"
    ),
    link=None,
    level=3,
    num="10.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting Parquet files with multiple row groups.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.6.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_MergeTreePart = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.MergeTreePart",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "  \n"
        "\n"
        "[ClickHouse] SHALL support moving data from a MergeTree part to a Parquet file. The process must handle large parts by \n"
        "processing them in MergeTree blocks, ensuring that each block is written as a RowGroup in the Parquet file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.6.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Settings_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Settings.RowGroupSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Settings                                     | Values                                         | Description                                                                                                                                                                                                                                                                       |\n"
        "|----------------------------------------------|------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n"
        "| `min_insert_block_size_rows`                 | `Positive integer (default: 1048449)` or `0`   | Sets the minimum number of rows in the block that can be inserted into a table by an INSERT query. Smaller-sized blocks are squashed into bigger ones.                                                                                                                            |\n"
        "| `min_insert_block_size_bytes`                | `Positive integer (default: 268402944)` or `0` | Sets the minimum number of bytes in the block which can be inserted into a table by an INSERT query. Smaller-sized blocks are squashed into bigger ones.                                                                                                                          |\n"
        "| `output_format_parquet_row_group_size`       | `Positive integer (default: 1000000)` or `0`   | Target row group size in rows.                                                                                                                                                                                                                                                    |\n"
        "| `output_format_parquet_row_group_size_bytes` | `Positive integer (default: 536870912)` or `0` | Target row group size in bytes, before compression.                                                                                                                                                                                                                               |\n"
        "| `output_format_parquet_parallel_encoding`    | `1` or `0`                                     | Do Parquet encoding in multiple threads. Requires `output_format_parquet_use_custom_encoder`.                                                                                                                                                                                     |\n"
        "| `max_threads`                                | `Positive integer (default: 4)` or `0`         | The maximum number of query processing threads, excluding threads for retrieving data from remote servers.                                                                                                                                                                        |\n"
        "| `max_insert_block_size`                      | `Positive integer (default: 1048449)` or `0`   | The size of blocks (in a count of rows) to form for insertion into a table.                                                                                                                                                                                                       |\n"
        "| `max_block_size`                             | `Positive integer (default: 65409)` or `0`     | indicates the recommended maximum number of rows to include in a single block when loading data from tables. Blocks the size of max_block_size are not always loaded from the table: if ClickHouse determines that less data needs to be retrieved, a smaller block is processed. |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.6.3.1",
)

RQ_SRS_032_ClickHouse_Export_Parquet_Join = Requirement(
    name="RQ.SRS-032.ClickHouse.Export.Parquet.Join",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting output of `SELECT` query with a `JOIN` clause into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.7.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Union = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Union",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting output of `SELECT` query with a `UNION` clause into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.7.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Union_Multiple = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Union.Multiple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting output of `SELECT` query with multiple `UNION` clauses used on the Parquet file.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM (SELECT * FROM file('file0001.parquet')\n"
        "UNION ALL SELECT * FROM file('file0001.parquet')\n"
        "UNION ALL SELECT * FROM file('file0001.parquet')\n"
        "UNION ALL SELECT * FROM file('file0001.parquet')\n"
        "UNION ALL SELECT * FROM file('file0001.parquet')\n"
        "...\n"
        "UNION ALL SELECT * FROM file('file0001.parquet')) LIMIT 10;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.7.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_View = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.View",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting output of `SELECT * FROM {view_name}` query into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.7.3",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Select_MaterializedView = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting output of `SELECT * FROM {mat_view_name}` query into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.7.4",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Plain` encoded Parquet files.\n" "\n"
    ),
    link=None,
    level=4,
    num="10.8.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Dictionary` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_RunLength = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Delta = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Delta Encoding` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Delta-length byte array` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaStrings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Delta Strings` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_ByteStreamSplit = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting `Byte Stream Split` encoded Parquet files.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="10.8.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `output_format_parquet_row_group_size` setting to specify row group size in rows.\n"
        "The default value SHALL be `1000000`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `output_format_parquet_string_as_string` setting to use Parquet String type instead of Binary.\n"
        "The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.9.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsFixedByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `output_format_parquet_fixed_string_as_fixed_byte_array` setting to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns. The default value SHALL be `1`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.9.3",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_ParquetVersion = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `output_format_parquet_version` setting to set the version of Parquet used in the output file.\n"
        "The default value SHALL be `2.latest`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.9.4",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_CompressionMethod = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying the `output_format_parquet_compression_method` setting to set the compression method used in the Parquet file.\n"
        "The default value SHALL be `lz4`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.9.5",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_TypeConversionFunction = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using type conversion functions when importing Parquet files.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    n,\n"
        "    toDateTime(time)\n"
        "FROM file('time.parquet', Parquet);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="10.10.1",
)

RQ_SRS_032_ClickHouse_Parquet_NativeReader = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NativeReader",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support usage of the Parquet native reader which enables direct reading of Parquet binary data into [ClickHouse] columns, bypassing the intermediate step of using the Apache Arrow library. This feature is controlled by the setting `input_format_parquet_use_native_reader`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('data.parquet', Parquet) SETTINGS input_format_parquet_use_native_reader = 1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_SRS_032_ClickHouse_Parquet_NativeReader_DataTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NativeReader.DataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading all existing Parquet data types when the native reader is enabled with `input_format_parquet_use_native_reader = 1`.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="11.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Hive = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Hive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support importing or exporting hive partitioned Parquet files.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting encrypted Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Column_Modular = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Modular",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with specific encrypted columns.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Column_Keys = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Keys",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files when different columns are encrypted with different keys.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCM = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCM",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with `AES-GCM` encryption algorithm.\n"
        "\n"
        "> The default algorithm AES-GCM provides full protection against tampering with data and metadata parts in Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCMCTR = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCMCTR",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with `AES-GCM-CTR`  encryption algorithm.\n"
        "\n"
        "> The alternative algorithm AES-GCM-CTR supports partial integrity protection of Parquet files. \n"
        "> Only metadata parts are protected against tampering, not data parts. \n"
        "> An advantage of this algorithm is that it has a lower throughput overhead compared to the AES-GCM algorithm.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with different parameters.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="13.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters_Algorythm = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Algorythm",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with `encryption.algorithm` parameter specified.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="13.4.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters_Plaintext_Footer = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Plaintext.Footer",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support importing or exporting Parquet files with `encryption.plaintext.footer` parameter specified.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="13.4.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_Structure = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Structure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `DESCRIBE TABLE` statement on the Parquet to read the file structure.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "DESCRIBE TABLE file('data.parquet', Parquet)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_None = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.None",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting uncompressed Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using gzip.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using brotli.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4_raw.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Hadoop = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Hadoop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using LZ4_HADOOP.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Snappy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using Snappy.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Zstd = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Compression.Zstd",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing or exporting Parquet files compressed using Zstd.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="15.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Lzo = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support importing or exporting Parquet files compressed using lzo.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="15.9.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `url` table function importing and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `file` table function importing and exporting Parquet format.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('data.parquet', Parquet)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File_AutoDetectParquetFileFormat = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using `file()` function without explicitly specifying the format setting.\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('data.parquet')\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `s3` table function for import and exporting Parquet format.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM s3('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3_HivePartitioning = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3.HivePartitioning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support detecting Hive partitioning when using the `s3` table function with `use_hive_partitioning` setting. That allows to use partition columns as virtual columns in the query.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * from s3('s3://data/path/date=*/country=*/code=*/*.parquet') where _date > '2020-01-01' and _country = 'Netherlands' and _code = 42;\n"
        "```\n"
        "\n"
        "> When setting use_hive_partitioning is set to 1, ClickHouse will detect \n"
        "> Hive-style partitioning in the path (/name=value/) and will allow to use partition columns as virtual columns in the query. These virtual columns will have the same names as in the partitioned path, but starting with _.\n"
        "> \n"
        "> Source: https://clickhouse.com/docs/en/sql-reference/table-functions/s3#hive-style-partitioning\n"
    ),
    link=None,
    level=4,
    num="16.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `jdbc` table function for import and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `odbc` table function for importing and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `hdfs` table function for importing and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `remote` table function for importing and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `mysql` table function for import and exporting Parquet format.\n"
        "\n"
        "For example,\n"
        "\n"
        "> Given we have a table with a `mysql` engine:\n"
        "> \n"
        "> ```sql\n"
        "> CREATE TABLE mysql_table1 (\n"
        ">   id UInt64,\n"
        ">   column1 String\n"
        "> )\n"
        "> ENGINE = MySQL('mysql-host.domain.com','db1','table1','mysql_clickhouse','Password123!')\n"
        "> ```\n"
        "> \n"
        "> We can Export from a Parquet file format with:\n"
        "> \n"
        "> ```sql\n"
        "> SELECT * FROM mysql_table1 INTO OUTFILE testTable.parquet FORMAT Parquet\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgreSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `postgresql` table function importing and exporting Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="16.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_ReadableExternalTable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.ReadableExternalTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY support Parquet format being exported from and imported into all table engines using `READABLE EXTERNAL TABLE`.\n"
        "\n"
        "For example,\n"
        "\n"
        "> ```sql\n"
        "> CREATE READABLE EXTERNAL TABLE table_name (\n"
        ">     key UInt32,\n"
        ">     value UInt32\n"
        "> ) LOCATION ('file://file_localtion/*.parquet')\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `MergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplicatedMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplacingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplacingMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_SummingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `SummingMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_AggregatingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `AggregatingMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_CollapsingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `CollapsingMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_VersionedCollapsingMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `VersionedCollapsingMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_GraphiteMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `GraphiteMergeTree` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.2.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into an `ODBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `JDBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `MySQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MongoDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `MongoDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `HDFS` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into an `S3` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_Kafka = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `Kafka` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_EmbeddedRocksDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into an `EmbeddedRocksDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `PostgreSQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="17.3.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `Memory` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `Distributed` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `Dictionary` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `File` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.4.4",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being exported from and imported into a `URL` table engine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="17.4.5",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing from Parquet files that utilize indexes.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="18.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_Page = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.Page",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support utilizing 'Page Index' of a parquet file in order to read data from the file more efficiently.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="18.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support utilizing 'Bloom Filter' of a parquet file in order to read data from the file more efficiently. In order to use Bloom filters, the `input_format_parquet_bloom_filter_push_down` setting SHALL be set to `true`.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "SELECT * FROM file('test.Parquet, Parquet) WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' SETTINGS input_format_parquet_bloom_filter_push_down=true\n"
        "```\n"
        "\n"
        "> A Bloom filter is a compact data structure that overapproximates a set. It can respond to membership \n"
        "> queries with either “definitely no” or “probably yes”, where the probability of false positives is configured when the filter is initialized. Bloom filters do not have false negatives.\n"
        "> \n"
        "> Because Bloom filters are small compared to dictionaries, they can be used for predicate pushdown even in columns with high cardinality and when space is at a premium.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="18.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Supported            | Unsupported |\n"
        "|----------------------|-------------|\n"
        "| FLOAT                | BOOLEAN     |\n"
        "| DOUBLE               | UUID        |\n"
        "| STRING               | BSON        |``\n"
        "| INT and UINT         | JSON        |\n"
        "| FIXED_LEN_BYTE_ARRAY | ARRAY       |\n"
        "|                      | MAP         |\n"
        "|                      | TUPLE       |\n"
        "|                      | ARRAY       |\n"
        "|                      | ENUM        |\n"
        "|                      | INTERVAL    |\n"
        "|                      | DECIMAL     |\n"
        "|                      | TIMESTAMP   |\n"
        "\n"
    ),
    link=None,
    level=4,
    num="18.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_Operators = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.Operators",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The following operators are supported when utilizing the Bloom filter applied on Parquet files:\n"
        "\n"
        "| Supported Operators |\n"
        "|---------------------|\n"
        "| =                   |\n"
        "| !=                  |\n"
        "| hasAny()            |\n"
        "| has()               |\n"
        "| IN                  |\n"
        "| NOT IN              |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="18.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes_Ignore_KeyColumnTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.KeyColumnTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL only consider the Parquet structure when utilizing Bloom filters from Parquet files and ignore the key column types.\n"
        "\n"
        "For example,\n"
        "    \n"
        "```sql\n"
        "select string_column from file('file.parquet', Parquet, 'string_column Decimal64(4, 2)') WHERE string_column = 'xyz' SETTINGS input_format_parquet_bloom_filter_push_down=true\n"
        "```\n"
        "\n"
        "[ClickHouse] SHALL utilize bloom filter and skip row groups despite the fact that `Decimal` values are not supported by ClickHouse Bloom filter implementation. \n"
        "This happens, because the real Parquet column type of `string_column` here is `String` which is supported by ClickHouse Bloom filter implementation.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="18.3.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes_Ignore_FieldTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.FieldTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL only consider the Parquet structure when utilizing Bloom filters from Parquet files and ignore the field types.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toDecimal(2, 4) SETTINGS input_format_parquet_bloom_filter_push_down=true\n"
        "```\n"
        "\n"
        "[ClickHouse] SHALL utilize bloom filter and skip row groups despite the fact that `Decimal` values are not supported by ClickHouse Bloom filter implementation. \n"
        "This happens, because the real Parquet column type of `xyz` here is `String` which is supported by ClickHouse Bloom filter implementation.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="18.3.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_DataTypes_Complex = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.DataTypes.Complex",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading data from a Parquet file that has row-groups with the Bloom Filter and complex datatype columns. This allows to decrease the query runtime for queries that include reading from a parquet file with `Array`, `Map` and `Tuple` datatypes.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="18.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ConsistentOutput_KeyColumnTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.KeyColumnTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the same output when reading data from a Parquet file with the query including key column type, both when `input_format_parquet_bloom_filter_push_down` is set to `true` and `false`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "select string_column from file('file.parquet', Parquet, 'string_column Int64') SETTINGS input_format_parquet_bloom_filter_push_down=true\n"
        "```\n"
        "\n"
        "and\n"
        "\n"
        "```sql\n"
        "select string_column from file('file.parquet', Parquet, 'string_column Int64') SETTINGS input_format_parquet_bloom_filter_push_down=false\n"
        "```\n"
        "\n"
        "SHALL have the same output.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="18.3.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ConsistentOutput_FieldTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.FieldTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the same output when reading data from a Parquet file with the query including field type, both when `input_format_parquet_bloom_filter_push_down` is set to `true` and `false`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toInt32(5) SETTINGS input_format_parquet_bloom_filter_push_down=true\n"
        "```\n"
        "\n"
        "and\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toInt32(5) SETTINGS input_format_parquet_bloom_filter_push_down=false\n"
        "``` \n"
        "\n"
        "SHALL have the same output.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="18.3.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Indexes_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Indexes.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support utilizing 'Dictionary' of a parquet file in order to read data from the file more efficiently.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="18.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Parquet files have three types of metadata\n"
        "\n"
        "- file metadata\n"
        "- column (chunk) metadata\n"
        "- page header metadata\n"
        "\n"
        "as described in https://parquet.apache.org/docs/file-format/metadata/.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="19.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `ParquetMetadata` format to read metadata from Parquet files.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM file(data.parquet, ParquetMetadata) format PrettyJSONEachRow\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat_Output = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support `ParquetMetadata` format as an output format and the `FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT` \n"
        "error SHALL be returned.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM file('writing_nullable_int8.parquet', 'ParquetMetadata')\n"
        "FORMAT ParquetMetadata\n"
        "\n"
        "Exception on client:\n"
        "Code: 399. DB::Exception: Code: 399. DB::Exception: Format ParquetMetadata is not suitable for output. (FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT) (version 23.5.1.2890 (official build)). (FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_Content = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse]'s ParquetMetadata format SHALL output the Parquet metadata in the following structure:\n"
        "\n"
        "> - num_columns - the number of columns\n"
        "> - num_rows - the total number of rows\n"
        "> - num_row_groups - the total number of row groups\n"
        "> - format_version - parquet format version, always 1.0 or 2.6\n"
        "> - total_uncompressed_size - total uncompressed bytes size of the data, calculated as the sum of total_byte_size from all row groups\n"
        "> - total_compressed_size - total compressed bytes size of the data, calculated as the sum of total_compressed_size from all row groups\n"
        "> - columns - the list of columns metadata with the next structure:\n"
        ">     - name - column name\n"
        ">     - path - column path (differs from name for nested column)\n"
        ">     - max_definition_level - maximum definition level\n"
        ">     - max_repetition_level - maximum repetition level\n"
        ">     - physical_type - column physical type\n"
        ">     - logical_type - column logical type\n"
        ">     - compression - compression used for this column\n"
        ">     - total_uncompressed_size - total uncompressed bytes size of the column, calculated as the sum of total_uncompressed_size of the column from all row groups\n"
        ">     - total_compressed_size - total compressed bytes size of the column, calculated as the sum of total_compressed_size of the column from all row groups\n"
        ">     - space_saved - percent of space saved by compression, calculated as (1 - total_compressed_size/total_uncompressed_size).\n"
        ">     - encodings - the list of encodings used for this column\n"
        "> - row_groups - the list of row groups metadata with the next structure:\n"
        ">     - num_columns - the number of columns in the row group\n"
        ">     - num_rows - the number of rows in the row group\n"
        ">     - total_uncompressed_size - total uncompressed bytes size of the row group\n"
        ">     - total_compressed_size - total compressed bytes size of the row group\n"
        ">     - columns - the list of column chunks metadata with the next structure:\n"
        ">        - name - column name\n"
        ">        - path - column path\n"
        ">        - total_compressed_size - total compressed bytes size of the column\n"
        ">        - total_uncompressed_size - total uncompressed bytes size of the row group\n"
        ">        - have_statistics - boolean flag that indicates if column chunk metadata contains column statistics\n"
        ">        - statistics - column chunk statistics (all fields are NULL if have_statistics = false) with the next structure:\n"
        ">            - num_values - the number of non-null values in the column chunk\n"
        ">            - null_count - the number of NULL values in the column chunk\n"
        ">            - distinct_count - the number of distinct values in the column chunk\n"
        ">            - min - the minimum value of the column chunk\n"
        ">            - max - the maximum column of the column chunk\n"
        "\n"
        "For example,\n"
        "\n"
        "> ```json\n"
        "> {\n"
        '>     "num_columns": "2",\n'
        '>     "num_rows": "100000",\n'
        '>     "num_row_groups": "2",\n'
        '>     "format_version": "2.6",\n'
        '>     "metadata_size": "577",\n'
        '>     "total_uncompressed_size": "282436",\n'
        '>     "total_compressed_size": "26633",\n'
        '>     "columns": [\n'
        ">         {\n"
        '>             "name": "number",\n'
        '>             "path": "number",\n'
        '>             "max_definition_level": "0",\n'
        '>             "max_repetition_level": "0",\n'
        '>             "physical_type": "INT32",\n'
        '>             "logical_type": "Int(bitWidth=16, isSigned=false)",\n'
        '>             "compression": "LZ4",\n'
        '>             "total_uncompressed_size": "133321",\n'
        '>             "total_compressed_size": "13293",\n'
        '>             "space_saved": "90.03%",\n'
        '>             "encodings": [\n'
        '>                 "RLE_DICTIONARY",\n'
        '>                 "PLAIN",\n'
        '>                 "RLE"\n'
        ">             ]\n"
        ">         },\n"
        ">         {\n"
        '>             "name": "concat(\'Hello\', toString(modulo(number, 1000)))",\n'
        '>             "path": "concat(\'Hello\', toString(modulo(number, 1000)))",\n'
        '>             "max_definition_level": "0",\n'
        '>             "max_repetition_level": "0",\n'
        '>             "physical_type": "BYTE_ARRAY",\n'
        '>             "logical_type": "None",\n'
        '>             "compression": "LZ4",\n'
        '>             "total_uncompressed_size": "149115",\n'
        '>             "total_compressed_size": "13340",\n'
        '>             "space_saved": "91.05%",\n'
        '>             "encodings": [\n'
        '>                 "RLE_DICTIONARY",\n'
        '>                 "PLAIN",\n'
        '>                 "RLE"\n'
        ">             ]\n"
        ">         }\n"
        ">     ],\n"
        '>     "row_groups": [\n'
        ">         {\n"
        '>             "num_columns": "2",\n'
        '>             "num_rows": "65409",\n'
        '>             "total_uncompressed_size": "179809",\n'
        '>             "total_compressed_size": "14163",\n'
        '>             "columns": [\n'
        ">                 {\n"
        '>                     "name": "number",\n'
        '>                     "path": "number",\n'
        '>                     "total_compressed_size": "7070",\n'
        '>                     "total_uncompressed_size": "85956",\n'
        '>                     "have_statistics": true,\n'
        '>                     "statistics": {\n'
        '>                         "num_values": "65409",\n'
        '>                         "null_count": "0",\n'
        '>                         "distinct_count": null,\n'
        '>                         "min": "0",\n'
        '>                         "max": "999"\n'
        ">                     }\n"
        ">                 },\n"
        ">                 {\n"
        '>                     "name": "concat(\'Hello\', toString(modulo(number, 1000)))",\n'
        '>                     "path": "concat(\'Hello\', toString(modulo(number, 1000)))",\n'
        '>                     "total_compressed_size": "7093",\n'
        '>                     "total_uncompressed_size": "93853",\n'
        '>                     "have_statistics": true,\n'
        '>                     "statistics": {\n'
        '>                         "num_values": "65409",\n'
        '>                         "null_count": "0",\n'
        '>                         "distinct_count": null,\n'
        '>                         "min": "Hello0",\n'
        '>                         "max": "Hello999"\n'
        ">                     }\n"
        ">                 }\n"
        ">             ]\n"
        ">         }\n"
        "> \n"
        ">     ]\n"
        "> }\n"
        "> ```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet files that have Min/Max values in the metadata and the files that are missing Min/Max values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.2.4",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_ExtraEntries = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.ExtraEntries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading from Parquet files that have extra entries in the metadata.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support accessing `File Metadata` in Parquet files.\n" "\n"
    ),
    link=None,
    level=3,
    num="19.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Column = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Column",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support accessing `Column (Chunk) Metadata` in Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Header = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Header",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support accessing `Page Header Metadata` in Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching the ListObjects to avoid repeated and expensive backend calls. This feature SHALL be controlled by the `use_object_storage_list_objects_cache` query setting.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    date,\n"
        "    count()\n"
        "FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/*/*.parquet', NOSIGN)\n"
        "WHERE (date >= '2025-01-01') AND (date <= '2025-01-31')\n"
        "GROUP BY date\n"
        "ORDER BY date ASC\n"
        "SETTINGS use_hive_partitioning = 1, use_object_storage_list_objects_cache = 1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_Settings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.Settings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Setting                                         | Type   | Description                                                                                   | Values                      |\n"
        "|-------------------------------------------------|--------|-----------------------------------------------------------------------------------------------|-----------------------------|\n"
        "| `object_storage_list_objects_cache_size`        | Server | Maximum size of ObjectStorage list objects cache in bytes. Zero means disabled.               | UInt64 (Default: 500000000) |\n"
        "| `object_storage_list_objects_cache_max_entries` | Server | Maximum size of ObjectStorage list objects cache in entries. Zero means disabled.             | UInt64 (Default: 1000)      |\n"
        "| `object_storage_list_objects_cache_ttl`         | Server | Time to live of records in ObjectStorage list objects cache in seconds. Zero means unlimited. | UInt64 (Default: 3600)      |\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.5.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_SameBucket = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.SameBucket",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL ensure that there are no collisions between different storage providers in scenarios where buckets with the same name containing the same directories exist in multiple object storage providers (e.g., AWS S3, GCS, etc.). Each storage provider's bucket SHALL be uniquely identified and handled independently to avoid conflicts.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.5.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_UserCredentials = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.UserCredentials",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not cache user credentials when caching the ListObjects. The credentials SHALL be passed to the object storage backend each time a request is made.\n"
        "\n"
        "For example, the correct behavior is:\n"
        "\n"
        "When we select the data with credentials for the first time and with `use_object_storage_list_objects_cache = 1` the query returns  the data and caches the ListObjects.\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM s3('http://localhost:11111/test/root/**.parquet', 'clickhous', 'clickhous')\n"
        "SETTINGS use_object_storage_list_objects_cache = 1\n"
        "\n"
        "\n"
        "   ┌─id─┐\n"
        "1. │  0 │\n"
        "2. │  1 │\n"
        "3. │  2 │\n"
        "4. │  3 │\n"
        "5. │  4 │\n"
        "   └────┘\n"
        "\n"
        "5 rows in set. Elapsed: 0.030 sec. \n"
        "```\n"
        "\n"
        "When we execute the same query but without credentials we SHALL get an exception.\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM s3('http://localhost:11111/test/root/**.parquet')\n"
        "SETTINGS use_object_storage_list_objects_cache = 1\n"
        "\n"
        "Query id: 0f2c41f5-7fc1-403f-964b-ad0fc8af9ba0\n"
        "\n"
        "\n"
        "Elapsed: 0.135 sec. \n"
        "\n"
        "Received exception from server (version 25.2.2):\n"
        "Code: 117. DB::Exception: Received from localhost:9000. DB::Exception: IOError: Code: 499. DB::Exception: The Access Key Id you provided does not exist in our records.: while reading key: root/{_partition_id}.parquet, from bucket: test. (S3_ERROR) (version 25.2.2.20000.altinityantalya): (in file/uri test/root/{_partition_id}.parquet): While executing ParquetBlockInputFormat: While executing S3(_table_function.s3)Source. (INCORRECT_DATA)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.5.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching [the whole metadata object](#rqsrs-032clickhouseparquetmetadataparquetmetadatacontent) when querying Parquet files stored in any type of remote object storage by using the \n"
        "`input_format_parquet_use_metadata_cache` query setting (disabled by default). The metadata caching SHALL allow faster query execution by avoiding the need to read the Parquet file’s metadata each time a query is executed.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(*)\n"
        "FROM s3(s3_url, filename = 'test.parquet', format = Parquet)\n"
        "SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
        "> [!NOTE]\n"
        "> For the input_format_parquet_use_metadata_cache setting to consistently work the following setting must be disabled: optimize_count_from_files=0, remote_filesystem_read_prefetch=0\n"
        "\n"
    ),
    link=None,
    level=3,
    num="19.6.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query when set from the profile settings for all nodes.\n"
        "\n"
        "For example, \n"
        "\n"
        "when the setting is set in the `users.xml` file for all nodes as:\n"
        "\n"
        "```xml\n"
        "<input_format_parquet_use_metadata_cache>1</input_format_parquet_use_metadata_cache>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings_InitiatorNode = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings.InitiatorNode",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query when set from the profile settings for the initiator node only.\n"
        "\n"
        "For example, \n"
        "\n"
        "when the setting is set in the `users.xml` file for the initiator node as:\n"
        "\n"
        "```xml\n"
        "<input_format_parquet_use_metadata_cache>1</input_format_parquet_use_metadata_cache>\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheEviction = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheEviction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL evict entries from the metadata cache when:\n"
        "\n"
        "* The total size of cached metadata exceeds `input_format_parquet_metadata_cache_max_entries` setting.\n"
        "\n"
        "The cache eviction SHALL be done in a Segmented Least Recently Used (SLRU) manner when the cache size limit is reached.\n"
        "\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `swarm` cluster by using the `input_format_parquet_use_metadata_cache` setting with `object_storage_cluster='swarm'` setting and `s3` function.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT hostName() AS host, count() \n"
        "FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet')\n"
        "GROUP BY host\n"
        "SETTINGS use_hive_partitioning=1, object_storage_cluster='swarm'\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_ReadWithS3Cluster = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.ReadWithS3Cluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `swarm` cluster by using the `input_format_parquet_use_metadata_cache` setting with `s3Cluster` function.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT hostName() AS host, * \n"
        "FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/**/**.parquet')\n"
        "SETTINGS use_hive_partitioning=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.5.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_NodeStops = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.NodeStops",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when a node in the swarm cluster stops during query execution as there are no retries implemented in swarm.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.5.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3` storage by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Azure = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Azure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Azure` storage by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_GoogleCloudStorage = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.GoogleCloudStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Google Cloud Storage` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MinIO = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MinIO",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `MinIO` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `HDFS` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Wasabi = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Wasabi",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Wasabi` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_DigitalOceanSpaces = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.DigitalOceanSpaces",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `DigitalOcean Spaces` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CephRADOSGateway = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CephRADOSGateway",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Ceph RADOS Gateway` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_YandexCloudObjectStorage = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.YandexCloudObjectStorage",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Yandex Cloud Object Storage` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CloudflareR2 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CloudflareR2",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Cloudflare R2` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.10.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AlibabaCloudOSS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AlibabaCloudOSS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Alibaba Cloud OSS` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.6.11.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3` engine or function by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
        "For example,\n"
        "\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM s3(s3_url, filename = 'test.parquet', format = Parquet)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3Cluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3Cluster` by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(*)\n"
        "FROM s3Cluster(s3_cluster_name, s3_url, filename = 'test.parquet', format = Parquet)\n"
        "SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_IcebergS3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.IcebergS3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `IcebergS3` engine or function including,`IcebergAzure`, `IcebergHDFS` and `IcebergLocal`, by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `URL` engine or function by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `File` engine or function by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `HDFS` engine or function by using the `input_format_parquet_use_metadata_cache` setting.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.7.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NotSuitedEngines = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NotSuitedEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL throw an error when trying to cache metadata when querying Parquet files stored in engines that are not suited for direct Parquet storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.8.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Invalidation = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Invalidation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL throw and error when the Parquet file is deleted from the object storage and we try to access the cache related to that file.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheClearing = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support clearing the Parquet metadata cache on a single node using the `SYSTEM DROP PARQUET METADATA CACHE` command.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.10.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheClearing_OnCluster = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing,OnCluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support clearing the Parquet metadata cache on all nodes in a cluster using the `SYSTEM DROP PARQUET METADATA CACHE ON CLUSTER {cluster_name}` command.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.10.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.ReadMetadataAfterCaching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading a given Parquet file's metadata once it has been cached.\n"
        "\n"
        "For example,\n"
        "\n"
        "If we run a query against a Parquet file once, when the metadata is cached, the following query SHALL return the metadata of the given Parquet file:\n"
        "\n"
        "```sql\n"
        "SELECT *\n"
        "FROM s3(s3_url, filename = 'test.parquet', format = ParquetMetadata)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.11.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HivePartitioning = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HivePartitioning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata when querying multiple Parquet files stored in object storage by using the `input_format_parquet_use_metadata_cache` and `use_hive_partitioning` setting.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT date, sum(output_count)\n"
        "FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/date=*/*.parquet', NOSIGN)\n"
        "WHERE date>='2024-01-01'\n"
        "GROUP BY date ORDER BY date\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.12.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Settings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Settings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "| Setting                                           | Values                          | Description                                                                         |\n"
        "|---------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------|\n"
        "| `input_format_parquet_use_metadata_cache`         | `true`/`false` (default: false) | Enable/disable caching of Parquet file metadata                                     |\n"
        "| `input_format_parquet_metadata_cache_max_entries` | `INT` (default: 500000000 bytes)           | Maximum number of file metadata objects to cache set from the server configuration. |\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.13.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AllSettings = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AllSettings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The following settings SHALL not cause any crashes in the system when used along with `input_format_parquet_use_metadata_cache`:\n"
        "\n"
        "| Setting                                                | Description                                                                                                                        |\n"
        "|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|\n"
        "| aggregation_in_order                                   | Enables partial aggregation in sort order if data is already sorted by GROUP BY keys.                                              |\n"
        "| aggregation_memory_efficient_merge_threads             | Number of threads used for external merges during aggregation when data is spilled to disk.                                        |\n"
        "| allow_ddl                                              | If disabled, DDL statements (CREATE, DROP, ALTER, etc.) are disallowed; typically set for read-only usage.                         |\n"
        "| allow_experimental_bigint_types                        | Enables the experimental Int128, Int256, UInt128, UInt256 types (in some newer versions).                                          |\n"
        "| allow_experimental_decimal_type                        | Enables the experimental extended Decimal types beyond standard Decimal(76, x).                                                    |\n"
        "| allow_experimental_map_type                            | Enables experimental Map data type usage in queries.                                                                               |\n"
        "| allow_experimental_object_type                         | Enables experimental Object data type usage in queries.                                                                            |\n"
        "| allow_experimental_window_functions                    | Allows usage of window functions in older releases when they were still marked experimental.                                       |\n"
        "| allow_introspection_functions                          | Allows special introspection/debugging functions (e.g. queryMemoryUsage()).                                                        |\n"
        "| allow_nullable_key                                     | Permits using nullable columns as keys in GROUP BY or JOIN operations.                                                             |\n"
        "| allow_suspicious_low_cardinality_types                 | Allows creating or querying LowCardinality columns in contexts that may be risky or unoptimized.                                   |\n"
        "| async_socket_for_remote                                | Enables asynchronous network I/O for distributed queries to improve performance under certain conditions.                          |\n"
        "| compile_aggregate_expressions                          | Tries to compile certain aggregate expressions to native code (requires ClickHouse built with LLVM).                               |\n"
        "| compile_expressions                                    | Attempts to compile complex expressions to native code via LLVM JIT for faster execution.                                          |\n"
        "| connect_timeout                                        | Timeout (seconds) for establishing connections (e.g., to remote shards in a distributed query).                                    |\n"
        "| custom_settings_prefix                                 | A prefix for custom (user-defined) settings to avoid naming conflicts with built-in settings.                                      |\n"
        "| database_atomic_wait_for_drop_and_detach_synchronously | Waits for asynchronous tasks (DROP/DETACH) in Atomic databases to finish.                                                          |\n"
        "| debug_allow_same_replica_for_distributed_queries       | Allows reading from the same replica multiple times in distributed queries (for debugging/diagnostics).                            |\n"
        "| dialect_type                                           | Chooses which SQL dialect to emulate (clickhouse, mysql, postgresql, etc.).                                                        |\n"
        "| distributed_aggregation_memory_efficient               | Improves memory usage for distributed aggregation by streaming partial results.                                                    |\n"
        "| force_index_by_date                                    | Requires a partition key or index by date to be used; otherwise the query fails.                                                   |\n"
        "| force_primary_key                                      | Requires usage of the primary key for query filtering; otherwise the query fails.                                                  |\n"
        "| format_csv_allow_double_quotes                         | When reading/writing CSV, whether double quotes are allowed to quote strings.                                                      |\n"
        "| format_csv_allow_single_quotes                         | When reading/writing CSV, whether single quotes are allowed to quote strings.                                                      |\n"
        "| format_csv_delimiter                                   | Delimiter character for CSV format (, by default).                                                                                 |\n"
        "| format_tsv_allow_single_quotes                         | Allows single quotes in TSV parsing (less common).                                                                                 |\n"
        "| group_by_overflow_mode                                 | Action if GROUP BY exceeds certain limits (e.g., throw, break).                                                                    |\n"
        "| group_by_two_level_threshold                           | Threshold of distinct keys at which ClickHouse switches to two-level aggregation.                                                  |\n"
        "| http_max_multipart_form_data_size                      | Maximum size for multipart/form-data HTTP requests (relevant if query input arrives this way).                                     |\n"
        "| http_receive_timeout                                   | HTTP server receive timeout (in seconds) for query data.                                                                           |\n"
        "| http_send_timeout                                      | HTTP server send timeout (in seconds) for sending results back to the client.                                                      |\n"
        "| input_format_allow_errors_num                          | Maximum number of parsing errors allowed in input before aborting.                                                                 |\n"
        "| input_format_allow_errors_ratio                        | Maximum ratio of parsing errors allowed (fraction of total rows) before aborting.                                                  |\n"
        "| input_format_csv_delimiter                             | Delimiter for CSV input (can be overridden per query).                                                                             |\n"
        "| input_format_csv_enum_detect_factor                    | Heuristic factor for detecting Enum from CSV input.                                                                                |\n"
        "| input_format_csv_enum_parsing_mode                     | Parsing mode for CSV Enum fields (string, auto, numeric, etc.).                                                                    |\n"
        "| input_format_defaults_for_omitted_fields               | Use default values if certain columns are missing from input.                                                                      |\n"
        "| input_format_import_nested_json                        | Allows parsing nested JSON structures in input.                                                                                    |\n"
        "| input_format_null_as_default                           | Treats NULL in incoming data as the default value for non-nullable columns.                                                        |\n"
        "| input_format_skip_unknown_fields                       | Skip fields in input that do not match any column definition.                                                                      |\n"
        "| join_algorithm                                         | Chooses join algorithm (auto, hash, partial_merge, etc.).                                                                          |\n"
        "| join_default_strictness                                | Default JOIN strictness if not specified (_`ANY                                                                                    |\n"
        "| join_use_nulls                                         | Use NULL in joined columns if no match (for left/full joins).                                                                      |\n"
        "| load_balancing                                         | Strategy for choosing replicas in a distributed query (random, nearest_hostname, etc.).                                            |\n"
        "| log_queries                                            | Enables or disables writing query info into system.query_log.                                                                      |\n"
        "| log_comment                                            | Additional string comment appended to query logs for identification.                                                               |\n"
        "| lookup_replica_priority                                | Whether to consider replica priority for distributed reads.                                                                        |\n"
        "| low_cardinality_allow_in_native_format                 | Allow storing LowCardinality columns in the native (optimized) format.                                                             |\n"
        "| max_ast_depth                                          | Maximum depth of the query’s AST (Abstract Syntax Tree).                                                                           |\n"
        "| max_ast_elements                                       | Maximum number of nodes/elements in the query’s AST.                                                                               |\n"
        "| max_bytes_before_external_group_by                     | Threshold (bytes) before partial GROUP BY is spilled to disk.                                                                      |\n"
        "| max_bytes_before_external_sort                         | Threshold (bytes) before partial sort is spilled to disk.                                                                          |\n"
        "| max_bytes_before_remerge_sort                          | Threshold for re-merging data on disk in external sorts.                                                                           |\n"
        "| max_bytes_in_dist_read                                 | Maximum bytes to read from each remote shard in a distributed query.                                                               |\n"
        "| max_bytes_in_join                                      | Maximum bytes in an in-memory JOIN state.                                                                                          |\n"
        "| max_bytes_to_read                                      | Maximum total bytes that can be read from storage during the query.                                                                |\n"
        "| max_csv_rows_to_read_for_schema_inference              | If using automatic schema inference from CSV, stops reading after this many rows for detection.                                    |\n"
        "| max_distributed_connections                            | Maximum number of connections to remote servers in distributed queries.                                                            |\n"
        "| max_execution_speed                                    | Maximum execution speed (rows/second). If exceeded, the query is paused or stopped depending on max_execution_speed_overflow_mode. |\n"
        "| max_execution_speed_overflow_mode                      | Action if the query exceeds max_execution_speed (throw, break, etc.).                                                              |\n"
        "| max_execution_time                                     | Maximum execution time in seconds. Query is aborted if exceeded (unless changed by the overflow mode).                             |\n"
        "| max_expanded_ast_elements                              | Limits expansions in the AST (e.g., from IN sets).                                                                                 |\n"
        "| max_insert_threads                                     | Maximum threads for INSERT SELECT queries.                                                                                         |\n"
        "| max_memory_usage                                       | Maximum memory usage per query.                                                                                                    |\n"
        "| max_memory_usage_for_all_queries                       | Maximum total memory usage for all queries on the server.                                                                          |\n"
        "| max_memory_usage_for_user                              | Maximum total memory usage for all queries by the current user.                                                                    |\n"
        "| max_parallel_replicas                                  | Maximum number of replicas to use in parallel for a query in a Distributed table.                                                  |\n"
        "| max_pipeline_depth                                     | Maximum execution pipeline depth.                                                                                                  |\n"
        "| max_query_size                                         | Maximum size of the query text in bytes.                                                                                           |\n"
        "| max_read_buffer_size                                   | Size (bytes) of the buffer used when reading from filesystem or network.                                                           |\n"
        "| max_result_bytes                                       | Maximum total size of the result (in bytes) returned by a query.                                                                   |\n"
        "| max_result_rows                                        | Maximum number of rows in the result set returned by a query.                                                                      |\n"
        "| max_rows_in_distinct                                   | Limit on the number of rows held in memory for SELECT DISTINCT.                                                                    |\n"
        "| max_rows_in_join                                       | Limit on the number of rows in a join hash table.                                                                                  |\n"
        "| max_rows_in_set                                        | Limit on the number of rows in a SET (for IN subqueries).                                                                          |\n"
        "| max_rows_in_table_function                             | Limit on rows read by table functions like s3, hdfs, or file.                                                                      |\n"
        "| max_rows_in_view                                       | Limit on rows that a VIEW can return.                                                                                              |\n"
        "| max_rows_to_group_by                                   | Limit on rows to process in GROUP BY before taking an overflow action.                                                             |\n"
        "| max_rows_to_read                                       | Limit on number of rows read from storage during the query.                                                                        |\n"
        "| memory_overflow_mode                                   | Action if max_memory_usage is exceeded (throw, break, etc.).                                                                       |\n"
        "| merge_tree_uniform_read_distribution                   | Distribute reads more evenly among parts for MergeTree tables if possible.                                                         |\n"
        "| min_execution_speed                                    | Minimum execution speed in rows/second; if slower after timeout_before_checking_execution_speed, it’s aborted/paused.              |\n"
        "| min_execution_speed_overflow_mode                      | Action if query falls below min_execution_speed.                                                                                   |\n"
        "| optimize_fuse_sum_count_avg                            | Tries to rewrite sequences of sum, count, avg into more optimal queries (e.g., combining aggregates).                              |\n"
        "| optimize_move_functions_out_of_any                     | Moves functions out of any(...) if possible to reduce overhead.                                                                    |\n"
        "| optimize_skip_unused_shards                            | Skip contacting shards if partition pruning or other conditions show no data is needed from them.                                  |\n"
        "| optimize_throw_if_suboptimal_plan                      | Throw an exception if the optimizer cannot generate a plan that is considered optimal (based on internal heuristics).              |\n"
        "| optimize_read_in_order                                 | Attempt to read in sorted order to avoid extra sorting if the query ORDER BY matches table sorting.                                |\n"
        '| output_format_json_escape_forward_slashes              | Whether to escape _"/_" in JSON output formats.                                                                                    |\n'
        "| output_format_json_quote_64bit_integers                | Whether to quote 64-bit integers in JSON output (to avoid losing precision in certain JS clients).                                 |\n"
        "| output_format_pretty_max_rows                          | Maximum number of rows printed in FORMAT Pretty.                                                                                   |\n"
        "| output_format_write_statistics                         | Controls whether to output query execution statistics in some formats.                                                             |\n"
        "| partial_merge_join_optimizations                       | Enables partial merge join (useful if both tables are large and sorted on join keys).                                              |\n"
        "| prefer_localhost_replica                               | Prefer reading from the local replica first in a replicated/distributed setup if available.                                        |\n"
        "| readonly                                               | If >0, disallows write operations (DDL/DML) – only SELECT. If >1, also disallows creating temporary tables, etc.                   |\n"
        "| send_logs_level                                        | Controls the verbosity of logs sent back to the client.                                                                            |\n"
        "| timeout_before_checking_execution_speed                | Time (seconds) after which ClickHouse checks if min_execution_speed is met.                                                        |\n"
        "| use_uncompressed_cache                                 | Enables the uncompressed cache for data, which can speed reads but uses more memory.                                               |\n"
        "| user_files_path                                        | Path where user can read files from or write files to (when using file table function, etc.).                                      |\n"
        "| wait_end_of_query                                      | When set, waits for the query to finish for all replicas in a Distributed table before returning (used in replication scenarios).  |\n"
        "| object_storage_cluster                                 |                                                                                                                                    |\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.14.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_Count = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.Count",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the following query:\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(*) FROM s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.15.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_MinMax = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.MinMax",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize min/max values from metadata.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3(s3_url, filename = 'test.parquet', format = Parquet) WHERE column1 > 1000 SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.15.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_BloomFilter = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.BloomFilter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize bloom filter.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM s3(s3_url, filename = 'test.parquet', format = Parquet) WHERE column1 = 'value' SETTINGS input_format_parquet_use_metadata_cache=1, input_format_parquet_bloom_filter=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.15.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_DistinctCount = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.DistinctCount",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize distinct count.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(DISTINCT column1) FROM s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.15.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_FileSchema = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.FileSchema",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that read the file schema.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "DESCRIBE s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.15.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MaxSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MaxSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support setting the maximum size of the metadata cache for Parquet files stored in object storage using the `input_format_parquet_metadata_cache_max_entries` (default value: 5000) setting. The setting must be set as a [ClickHouse] server configuration.\n"
        "If the number of cached metadata objects exceeds the maximum size, the exception SHALL be thrown.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.16.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SameNameDifferentLocation = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SameNameDifferentLocation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL be able to successfully read from the Parquet files with the same name but different locations when the metadata is cached.\n"
        "\n"
        "For example, if we have two files, `test.parquet` in `s3://bucket1/` and `test.parquet` in `s3://bucket2/`, the following query SHALL successfully read the data of the file after the metadata is cached:\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(*) FROM s3({s3_url}/bucket1, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1\n"
        "SELECT COUNT(*) FROM s3({s3_url}/bucket2, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.17.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HitsMissesCounter = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HitsMissesCounter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support counting the number of cache hits and misses when querying Parquet files stored in object storage.\n"
        "In order to get the number of cache hits and misses the following steps SHALL be taken:\n"
        "\n"
        "1. Use the `log_comment` setting.\n"
        "2. Query through the `system.log` using that `log_comment`.\n"
        "\n"
        "```sql\n"
        "SELECT COUNT(*)\n"
        "FROM s3(s3_conn, filename = 'test_03262_*', format = Parquet)\n"
        "SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "\n"
        "SELECT COUNT(*)\n"
        "FROM s3(s3_conn, filename = 'test_03262_*', format = Parquet)\n"
        "SETTINGS input_format_parquet_use_metadata_cache=1, log_comment='test_03262_parquet_metadata_cache';\n"
        "\n"
        "SYSTEM FLUSH LOGS;\n"
        "\n"
        "SELECT ProfileEvents['ParquetMetaDataCacheHits']\n"
        "FROM system.query_log\n"
        "where log_comment = 'test_03262_parquet_metadata_cache'\n"
        "AND type = 'QueryFinish'\n"
        "ORDER BY event_time desc\n"
        "LIMIT 1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.6.18.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_Join = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Join",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL cache the metadata of both files when joining two Parquet files stored in object storage.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    t1.id,\n"
        "    t2.value\n"
        "FROM s3(\n"
        "    'https://my-bucket.s3.amazonaws.com/path/to/first.parquet',\n"
        "    'Parquet',\n"
        "    'id UInt64, data String'\n"
        ") AS t1\n"
        "JOIN s3(\n"
        "    'https://my-bucket.s3.amazonaws.com/path/to/second.parquet',\n"
        "    'Parquet',\n"
        "    'id UInt64, value String'\n"
        ") AS t2\n"
        "    ON t1.id = t2.id SETTINGS input_format_parquet_use_metadata_cache=1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.19.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_Basic = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Basic",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    COUNT(*) AS total_rows\n"
        "FROM\n"
        "(\n"
        "    SELECT *\n"
        "    FROM s3Cluster(\n"
        "        s3_cluster_name,\n"
        "        s3_url,\n"
        "        'test.parquet',\n"
        "        'Parquet'\n"
        "    )\n"
        "    SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        ")\n"
        "WHERE some_column > 0;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.19.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_UnionAll = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionAll",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.\n"
        "    \n"
        "```sql\n"
        "SELECT 'first_file' AS source, COUNT(*) AS row_count\n"
        "FROM\n"
        "(\n"
        "    SELECT *\n"
        "    FROM s3Cluster(\n"
        "        s3_cluster_name,\n"
        "        s3_url,\n"
        "        'test.parquet',\n"
        "        'Parquet'\n"
        "    )\n"
        "    SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        ")\n"
        "WHERE some_column = 10\n"
        "\n"
        "UNION ALL\n"
        "\n"
        "SELECT 'second_file' AS source, COUNT(*) AS row_count\n"
        "FROM\n"
        "(\n"
        "    SELECT *\n"
        "    FROM s3Cluster(\n"
        "        s3_cluster_name,\n"
        "        s3_url,\n"
        "        'another_file.parquet',\n"
        "        'Parquet'\n"
        "    )\n"
        "    SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        ")\n"
        "WHERE some_column = 10;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.19.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_FilterAggregation = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.FilterAggregation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.\n"
        "\n"
        "```sql\n"
        "SELECT\n"
        "    region,\n"
        "    COUNT(*) AS count_per_region\n"
        "FROM\n"
        "(\n"
        "    SELECT\n"
        "        region,\n"
        "        user_id,\n"
        "        total_spent\n"
        "    FROM\n"
        "    (\n"
        "        SELECT *\n"
        "        FROM s3Cluster(\n"
        "            s3_cluster_name,\n"
        "            s3_url,\n"
        "            'test.parquet',\n"
        "            'Parquet'\n"
        "        )\n"
        "        SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        "    )\n"
        "    WHERE total_spent > 0\n"
        ") AS data_with_spent\n"
        "WHERE region != 'UNKNOWN'\n"
        "GROUP BY region\n"
        "ORDER BY count_per_region DESC;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.19.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_UnionJoin = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionJoin",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.\n"
        "\n"
        "```sql\n"
        "WITH\n"
        "transactions_all AS\n"
        "(\n"
        "    SELECT user_id, amount, event_date\n"
        "    FROM\n"
        "    (\n"
        "        SELECT user_id, amount, event_date\n"
        "        FROM s3Cluster(\n"
        "            s3_cluster_name,\n"
        "            s3_url,\n"
        "            'transactions_2024.parquet',\n"
        "            'Parquet'\n"
        "        )\n"
        "        SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        "        WHERE event_date < '2025-01-01'\n"
        "    )\n"
        "    UNION ALL\n"
        "    SELECT user_id, amount, event_date\n"
        "    FROM\n"
        "    (\n"
        "        SELECT user_id, amount, event_date\n"
        "        FROM s3Cluster(\n"
        "            s3_cluster_name,\n"
        "            s3_url,\n"
        "            'transactions_2025.parquet',\n"
        "            'Parquet'\n"
        "        )\n"
        "        SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        "        WHERE event_date >= '2025-01-01'\n"
        "    )\n"
        "),\n"
        "\n"
        "user_profiles AS\n"
        "(\n"
        "    SELECT user_id, region, signup_date\n"
        "    FROM s3Cluster(\n"
        "        s3_cluster_name,\n"
        "        s3_url,\n"
        "        'user_profiles.parquet',\n"
        "        'Parquet'\n"
        "    )\n"
        "    SETTINGS input_format_parquet_use_metadata_cache = 1\n"
        ")\n"
        "\n"
        "SELECT\n"
        "    p.user_id,\n"
        "    p.region,\n"
        "    SUM(t.amount) AS total_spent,\n"
        "    COUNT()       AS txn_count\n"
        "FROM transactions_all AS t\n"
        "JOIN user_profiles AS p ON t.user_id = p.user_id\n"
        "GROUP BY\n"
        "    p.user_id,\n"
        "    p.region\n"
        "ORDER BY total_spent DESC\n"
        "LIMIT 100;\n"
        "\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=5,
    num="19.6.19.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_ClickHouse = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ClickHouse",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata generated by [ClickHouse] when querying Parquet files stored in object storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.7.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_Parquetify = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.Parquetify",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata generated by [Parquetify](https://github.com/Altinity/parquet-regression/tree/main/parquetify) when querying Parquet files stored in object storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.7.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_DuckDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.DuckDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata generated by `DuckDB` when querying Parquet files stored in object storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.7.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_ApacheArrow = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ApacheArrow",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support caching metadata generated by `Apache Arrow` when querying Parquet files stored in object storage.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="19.7.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_MagicNumber = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.MagicNumber",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error if the 4-byte magic number "PAR1" is missing from the Parquet metadata.\n'
        "\n"
        "For example,\n"
        "\n"
        'When using hexeditor on the Parquet file we alter the values of "PAR1" and change it to "PARQ".\n'
        "then when we try to import that Parquet file to [ClickHouse] we SHALL get an exception:\n"
        "\n"
        "```\n"
        "exception. Code: 1001, type: parquet::ParquetInvalidOrCorruptedFileException,\n"
        "e.what() = Invalid: Parquet magic bytes not found in footer.\n"
        "Either the file is corrupted or this is not a Parquet file.\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.1",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to access the corrupt `file` metadata.\n"
        "In this case the file metadata is corrupt, the file is lost.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.2",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_Column = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Column",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to access the corrupt `column` metadata.\n"
        "In this case that column chunk MAY be lost but column chunks for this column in other row groups SHALL be okay.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.3",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_PageHeader = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageHeader",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to access the corrupt `Page Header`.\n"
        "In this case the remaining pages in that chunk SHALL be lost.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.4",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_PageData = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to access the corrupt `Page Data`.\n"
        "In this case that page SHALL be lost.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.5",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_Checksum = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Checksum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error if the Parquet file's checksum is corrupted.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.6",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to access the corrupt column values.\n"
        "\n"
        "Error message example,\n"
        "\n"
        "> DB::Exception: Cannot extract table structure from Parquet format file.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=2,
    num="20.7",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Date = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Date",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `date` values.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Int = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Int",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Int` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.2",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_BigInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.BigInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BigInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.3",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_SmallInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.SmallInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `SmallInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.4",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TinyInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TinyInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TinyInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.5",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.6",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UBigInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UBigInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UBigInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.7",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_USmallInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.USmallInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `USmallInt` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.8",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UTinyInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UTinyInt",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UTinyInt` values.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.9",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampUS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampUS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (us)` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.10",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampMS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampMS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (ms)` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.11",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Bool = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Bool",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BOOL` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.12",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Float = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Float",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FLOAT` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.13",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Double = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Double",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DOUBLE` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.14",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeMS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeMS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ms)` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.15",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeUS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeUS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (us)` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.16",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeNS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeNS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ns)` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.17",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_String = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.String",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRING` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.18",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Binary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Binary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BINARY` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.19",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_FixedLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.FixedLengthByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FIXED_LENGTH_BYTE_ARRAY` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.20",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Decimal = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Decimal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DECIMAL` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.21",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_List = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.List",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `LIST` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.22",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Struct = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Struct",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRUCT` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.23",
)

RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Map = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Map",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `MAP` values.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="20.7.24",
)

RQ_SRS_032_ClickHouse_Parquet_Interoperability_From_x86_To_ARM = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.x86.To.ARM",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting parquet files on `ARM` machine that were generated on `x86` machine.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="21.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Interoperability_From_ARM_To_x86 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.ARM.To.x86",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing and exporting parquet files on `x86` machine that were generated on `ARM` machine.\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/parquet/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/parquet/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=3,
    num="21.2.1",
)

SRS032_ClickHouse_Parquet_Data_Format = Specification(
    name="SRS032 ClickHouse Parquet Data Format",
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
        Heading(name="Revision History", level=1, num="1"),
        Heading(name="Introduction", level=1, num="2"),
        Heading(name="Test Schema", level=1, num="3"),
        Heading(name="Feature Diagram", level=1, num="4"),
        Heading(name="Working With Parquet", level=1, num="5"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet", level=2, num="5.1"),
        Heading(name="Supported Parquet Versions", level=1, num="6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.SupportedVersions", level=2, num="6.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal", level=2, num="6.2"
        ),
        Heading(name="Offsets", level=1, num="7"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Offsets", level=2, num="7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Offsets.MonotonicallyIncreasing",
            level=3,
            num="7.1.1",
        ),
        Heading(name="Query Cache", level=1, num="8"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Query.Cache", level=2, num="8.1"),
        Heading(name="Import from Parquet Files", level=1, num="9"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Import", level=2, num="9.1"),
        Heading(name="Auto Detect Parquet File When Importing", level=2, num="9.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat",
            level=3,
            num="9.2.1",
        ),
        Heading(name="Glob Patterns", level=2, num="9.3"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Import.Glob", level=3, num="9.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Glob.MultiDirectory",
            level=3,
            num="9.3.2",
        ),
        Heading(name="Supported Datatypes", level=2, num="9.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Conversion",
            level=3,
            num="9.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported",
            level=3,
            num="9.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BLOB",
            level=3,
            num="9.4.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BOOL",
            level=3,
            num="9.4.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT8",
            level=3,
            num="9.4.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT8",
            level=3,
            num="9.4.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT16",
            level=3,
            num="9.4.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT16",
            level=3,
            num="9.4.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT32",
            level=3,
            num="9.4.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT32",
            level=3,
            num="9.4.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT64",
            level=3,
            num="9.4.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT64",
            level=3,
            num="9.4.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FLOAT",
            level=3,
            num="9.4.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DOUBLE",
            level=3,
            num="9.4.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE",
            level=3,
            num="9.4.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ms",
            level=3,
            num="9.4.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ns",
            level=3,
            num="9.4.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.us",
            level=3,
            num="9.4.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIME.ms",
            level=3,
            num="9.4.19",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ms",
            level=3,
            num="9.4.20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ns",
            level=3,
            num="9.4.21",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.us",
            level=3,
            num="9.4.22",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRING",
            level=3,
            num="9.4.23",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BINARY",
            level=3,
            num="9.4.24",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray",
            level=3,
            num="9.4.25",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray.FLOAT16",
            level=3,
            num="9.4.26",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL",
            level=3,
            num="9.4.27",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL.Filter",
            level=3,
            num="9.4.28",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.LIST",
            level=3,
            num="9.4.29",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.ARRAY",
            level=3,
            num="9.4.30",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRUCT",
            level=3,
            num="9.4.31",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.MAP",
            level=3,
            num="9.4.32",
        ),
        Heading(name="UTCAdjusted", level=3, num="9.4.33"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.DateUTCAdjusted",
            level=4,
            num="9.4.33.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimestampUTCAdjusted",
            level=4,
            num="9.4.33.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimeUTCAdjusted",
            level=4,
            num="9.4.33.3",
        ),
        Heading(name="Nullable", level=3, num="9.4.34"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.NullValues",
            level=4,
            num="9.4.34.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nullable",
            level=4,
            num="9.4.34.2",
        ),
        Heading(name="LowCardinality", level=3, num="9.4.35"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.LowCardinality",
            level=4,
            num="9.4.35.1",
        ),
        Heading(name="Nested", level=3, num="9.4.36"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nested",
            level=4,
            num="9.4.36.1",
        ),
        Heading(name="UNKNOWN", level=3, num="9.4.37"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Unknown",
            level=4,
            num="9.4.37.1",
        ),
        Heading(name="Unsupported Datatypes", level=2, num="9.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported",
            level=3,
            num="9.5.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported.ChunkedArray",
            level=3,
            num="9.5.2",
        ),
        Heading(name="Filter Pushdown", level=2, num="9.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown",
            level=3,
            num="9.6.1",
        ),
        Heading(
            name="Supported Operations that utilize Min/Max Statistics",
            level=3,
            num="9.6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown.MinMax.Operations",
            level=4,
            num="9.6.2.1",
        ),
        Heading(name="Projections", level=2, num="9.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Projections",
            level=3,
            num="9.7.1",
        ),
        Heading(name="Skip Columns", level=2, num="9.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns",
            level=3,
            num="9.8.1",
        ),
        Heading(name="Skip Values", level=2, num="9.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues", level=3, num="9.9.1"
        ),
        Heading(name="Auto Typecast", level=2, num="9.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast",
            level=3,
            num="9.10.1",
        ),
        Heading(name="Row Group Size", level=2, num="9.11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize",
            level=3,
            num="9.11.1",
        ),
        Heading(name="Data Page Size", level=2, num="9.12"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize",
            level=3,
            num="9.12.1",
        ),
        Heading(name="Import Into New Table", level=2, num="9.13"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.NewTable", level=3, num="9.13.1"
        ),
        Heading(name="Performance", level=2, num="9.14"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Performance.CountFromMetadata",
            level=3,
            num="9.14.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Performance.ParallelProcessing",
            level=3,
            num="9.14.2",
        ),
        Heading(name="Import Nested Types", level=2, num="9.15"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested",
            level=3,
            num="9.15.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.Complex",
            level=3,
            num="9.15.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested",
            level=3,
            num="9.15.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested",
            level=3,
            num="9.15.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested",
            level=3,
            num="9.15.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested",
            level=3,
            num="9.15.6",
        ),
        Heading(name="Import Chunked Columns", level=2, num="9.16"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns",
            level=3,
            num="9.16.1",
        ),
        Heading(name="Import Encoded", level=2, num="9.17"),
        Heading(name="Plain (Import)", level=3, num="9.17.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain",
            level=4,
            num="9.17.1.1",
        ),
        Heading(name="Dictionary (Import)", level=3, num="9.17.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Dictionary",
            level=4,
            num="9.17.2.1",
        ),
        Heading(name="Run Length Encoding (Import)", level=3, num="9.17.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength",
            level=4,
            num="9.17.3.1",
        ),
        Heading(name="Delta (Import)", level=3, num="9.17.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta",
            level=4,
            num="9.17.4.1",
        ),
        Heading(name="Delta-length byte array (Import)", level=3, num="9.17.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray",
            level=4,
            num="9.17.5.1",
        ),
        Heading(name="Delta Strings (Import)", level=3, num="9.17.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings",
            level=4,
            num="9.17.6.1",
        ),
        Heading(name="Byte Stream Split (Import)", level=3, num="9.17.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit",
            level=4,
            num="9.17.7.1",
        ),
        Heading(name="Import Settings", level=2, num="9.18"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested",
            level=3,
            num="9.18.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching",
            level=3,
            num="9.18.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns",
            level=3,
            num="9.18.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
            level=3,
            num="9.18.4",
        ),
        Heading(name="Libraries", level=2, num="9.19"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Libraries", level=3, num="9.19.1"),
        Heading(name="Pyarrow", level=3, num="9.19.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Libraries.Pyarrow",
            level=4,
            num="9.19.2.1",
        ),
        Heading(name="PySpark", level=3, num="9.19.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Libraries.PySpark",
            level=4,
            num="9.19.3.1",
        ),
        Heading(name="Pandas", level=3, num="9.19.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Libraries.Pandas",
            level=4,
            num="9.19.4.1",
        ),
        Heading(name="parquet-go", level=3, num="9.19.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Libraries.ParquetGO",
            level=4,
            num="9.19.5.1",
        ),
        Heading(name="H2OAI", level=3, num="9.19.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Libraries.H2OAI",
            level=4,
            num="9.19.6.1",
        ),
        Heading(name="Export from Parquet Files", level=1, num="10"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Export", level=2, num="10.1"),
        Heading(name="Auto Detect Parquet File When Exporting", level=2, num="10.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat",
            level=3,
            num="10.2.1",
        ),
        Heading(name="Supported Data types", level=2, num="10.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported",
            level=3,
            num="10.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BLOB",
            level=3,
            num="10.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BOOL",
            level=3,
            num="10.3.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT8",
            level=3,
            num="10.3.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT8",
            level=3,
            num="10.3.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT16",
            level=3,
            num="10.3.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT16",
            level=3,
            num="10.3.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT32",
            level=3,
            num="10.3.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT32",
            level=3,
            num="10.3.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT64",
            level=3,
            num="10.3.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT64",
            level=3,
            num="10.3.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FLOAT",
            level=3,
            num="10.3.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DOUBLE",
            level=3,
            num="10.3.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE",
            level=3,
            num="10.3.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ms",
            level=3,
            num="10.3.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ns",
            level=3,
            num="10.3.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.us",
            level=3,
            num="10.3.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIME.ms",
            level=3,
            num="10.3.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ms",
            level=3,
            num="10.3.19",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ns",
            level=3,
            num="10.3.20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.us",
            level=3,
            num="10.3.21",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRING",
            level=3,
            num="10.3.22",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BINARY",
            level=3,
            num="10.3.23",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FixedLengthByteArray",
            level=3,
            num="10.3.24",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL",
            level=3,
            num="10.3.25",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL.Filter",
            level=3,
            num="10.3.26",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.LIST",
            level=3,
            num="10.3.27",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.ARRAY",
            level=3,
            num="10.3.28",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRUCT",
            level=3,
            num="10.3.29",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.MAP",
            level=3,
            num="10.3.30",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nullable",
            level=3,
            num="10.3.31",
        ),
        Heading(name="Working With Nested Types Export", level=2, num="10.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Nested", level=3, num="10.4.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Nested.Complex",
            level=3,
            num="10.4.2",
        ),
        Heading(name="Exporting Chunked Columns", level=2, num="10.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.ChunkedColumns",
            level=3,
            num="10.5.1",
        ),
        Heading(name="Multi-chunk Upload (Split to Rowgroups)", level=2, num="10.6"),
        Heading(name="Inserting Data Into Parquet Files", level=3, num="10.6.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Insert",
            level=4,
            num="10.6.1.1",
        ),
        Heading(name="Move from MergeTree Part to Parquet", level=3, num="10.6.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.MergeTreePart",
            level=4,
            num="10.6.2.1",
        ),
        Heading(
            name="Settings for Manipulating the Size of Row Groups",
            level=3,
            num="10.6.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Settings.RowGroupSize",
            level=4,
            num="10.6.3.1",
        ),
        Heading(name="Query Types", level=2, num="10.7"),
        Heading(name="JOIN", level=3, num="10.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Export.Parquet.Join", level=4, num="10.7.1.1"
        ),
        Heading(name="UNION", level=3, num="10.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Union", level=4, num="10.7.2.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Union.Multiple",
            level=4,
            num="10.7.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.View", level=3, num="10.7.3"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView",
            level=3,
            num="10.7.4",
        ),
        Heading(name="Export Encoded", level=2, num="10.8"),
        Heading(name="Plain (Export)", level=3, num="10.8.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain",
            level=4,
            num="10.8.1.1",
        ),
        Heading(name="Dictionary (Export)", level=3, num="10.8.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Dictionary",
            level=4,
            num="10.8.2.1",
        ),
        Heading(name="Run Length Encoding (Export)", level=3, num="10.8.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength",
            level=4,
            num="10.8.3.1",
        ),
        Heading(name="Delta (Export)", level=3, num="10.8.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta",
            level=4,
            num="10.8.4.1",
        ),
        Heading(name="Delta-length byte array (Export)", level=3, num="10.8.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray",
            level=4,
            num="10.8.5.1",
        ),
        Heading(name="Delta Strings (Export)", level=3, num="10.8.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings",
            level=4,
            num="10.8.6.1",
        ),
        Heading(name="Byte Stream Split (Export)", level=3, num="10.8.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit",
            level=4,
            num="10.8.7.1",
        ),
        Heading(name="Export Settings", level=2, num="10.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize",
            level=3,
            num="10.9.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString",
            level=3,
            num="10.9.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray",
            level=3,
            num="10.9.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion",
            level=3,
            num="10.9.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod",
            level=3,
            num="10.9.5",
        ),
        Heading(name="Type Conversion", level=2, num="10.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction",
            level=3,
            num="10.10.1",
        ),
        Heading(name="Native Reader", level=1, num="11"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.NativeReader", level=2, num="11.1"),
        Heading(name="Data Types Support", level=2, num="11.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NativeReader.DataTypes",
            level=3,
            num="11.2.1",
        ),
        Heading(name="Hive Partitioning", level=1, num="12"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Hive", level=2, num="12.1"),
        Heading(name="Parquet Encryption", level=1, num="13"),
        Heading(name="File Encryption", level=2, num="13.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.File", level=3, num="13.1.1"
        ),
        Heading(name="Column Encryption", level=2, num="13.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Modular",
            level=3,
            num="13.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Keys",
            level=3,
            num="13.2.2",
        ),
        Heading(name="Encryption Algorithms", level=2, num="13.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCM",
            level=3,
            num="13.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCMCTR",
            level=3,
            num="13.3.2",
        ),
        Heading(name="EncryptionParameters", level=2, num="13.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters",
            level=3,
            num="13.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Algorythm",
            level=4,
            num="13.4.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Plaintext.Footer",
            level=4,
            num="13.4.1.2",
        ),
        Heading(name="DESCRIBE Parquet", level=1, num="14"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Structure", level=2, num="14.1"),
        Heading(name="Compression", level=1, num="15"),
        Heading(name="None", level=2, num="15.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.None", level=3, num="15.1.1"
        ),
        Heading(name="Gzip", level=2, num="15.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip", level=3, num="15.2.1"
        ),
        Heading(name="Brotli", level=2, num="15.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli",
            level=3,
            num="15.3.1",
        ),
        Heading(name="Lz4", level=2, num="15.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4", level=3, num="15.4.1"
        ),
        Heading(name="Lz4Raw", level=2, num="15.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw",
            level=3,
            num="15.5.1",
        ),
        Heading(name="Lz4Hadoop", level=2, num="15.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Hadoop",
            level=3,
            num="15.6.1",
        ),
        Heading(name="Snappy", level=2, num="15.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Snappy",
            level=3,
            num="15.7.1",
        ),
        Heading(name="Zstd", level=2, num="15.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Zstd", level=3, num="15.8.1"
        ),
        Heading(name="Unsupported Compression", level=2, num="15.9"),
        Heading(name="Lzo", level=3, num="15.9.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo",
            level=4,
            num="15.9.1.1",
        ),
        Heading(name="Table Functions", level=1, num="16"),
        Heading(name="URL", level=2, num="16.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL",
            level=3,
            num="16.1.1",
        ),
        Heading(name="File", level=2, num="16.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File",
            level=3,
            num="16.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat",
            level=3,
            num="16.2.2",
        ),
        Heading(name="S3", level=2, num="16.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3",
            level=3,
            num="16.3.1",
        ),
        Heading(name="Detecting Hive Partitioning", level=3, num="16.3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3.HivePartitioning",
            level=4,
            num="16.3.2.1",
        ),
        Heading(name="JDBC", level=2, num="16.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC",
            level=3,
            num="16.4.1",
        ),
        Heading(name="ODBC", level=2, num="16.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC",
            level=3,
            num="16.5.1",
        ),
        Heading(name="HDFS", level=2, num="16.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS",
            level=3,
            num="16.6.1",
        ),
        Heading(name="Remote", level=2, num="16.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote",
            level=3,
            num="16.7.1",
        ),
        Heading(name="MySQL", level=2, num="16.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL",
            level=3,
            num="16.8.1",
        ),
        Heading(name="PostgreSQL", level=2, num="16.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL",
            level=3,
            num="16.9.1",
        ),
        Heading(name="Table Engines", level=1, num="17"),
        Heading(name="Readable External Table", level=2, num="17.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.ReadableExternalTable",
            level=3,
            num="17.1.1",
        ),
        Heading(name="MergeTree", level=2, num="17.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree",
            level=3,
            num="17.2.1",
        ),
        Heading(name="ReplicatedMergeTree", level=3, num="17.2.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree",
            level=4,
            num="17.2.2.1",
        ),
        Heading(name="ReplacingMergeTree", level=3, num="17.2.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree",
            level=4,
            num="17.2.3.1",
        ),
        Heading(name="SummingMergeTree", level=3, num="17.2.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree",
            level=4,
            num="17.2.4.1",
        ),
        Heading(name="AggregatingMergeTree", level=3, num="17.2.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree",
            level=4,
            num="17.2.5.1",
        ),
        Heading(name="CollapsingMergeTree", level=3, num="17.2.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree",
            level=4,
            num="17.2.6.1",
        ),
        Heading(name="VersionedCollapsingMergeTree", level=3, num="17.2.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree",
            level=4,
            num="17.2.7.1",
        ),
        Heading(name="GraphiteMergeTree", level=3, num="17.2.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree",
            level=4,
            num="17.2.8.1",
        ),
        Heading(name="Integration Engines", level=2, num="17.3"),
        Heading(name="ODBC Engine", level=3, num="17.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC",
            level=4,
            num="17.3.1.1",
        ),
        Heading(name="JDBC Engine", level=3, num="17.3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC",
            level=4,
            num="17.3.2.1",
        ),
        Heading(name="MySQL Engine", level=3, num="17.3.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL",
            level=4,
            num="17.3.3.1",
        ),
        Heading(name="MongoDB Engine", level=3, num="17.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB",
            level=4,
            num="17.3.4.1",
        ),
        Heading(name="HDFS Engine", level=3, num="17.3.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS",
            level=4,
            num="17.3.5.1",
        ),
        Heading(name="S3 Engine", level=3, num="17.3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3",
            level=4,
            num="17.3.6.1",
        ),
        Heading(name="Kafka Engine", level=3, num="17.3.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka",
            level=4,
            num="17.3.7.1",
        ),
        Heading(name="EmbeddedRocksDB Engine", level=3, num="17.3.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB",
            level=4,
            num="17.3.8.1",
        ),
        Heading(name="PostgreSQL Engine", level=3, num="17.3.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL",
            level=4,
            num="17.3.9.1",
        ),
        Heading(name="Special Engines", level=2, num="17.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory",
            level=3,
            num="17.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed",
            level=3,
            num="17.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary",
            level=3,
            num="17.4.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File",
            level=3,
            num="17.4.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL",
            level=3,
            num="17.4.5",
        ),
        Heading(name="Indexes", level=1, num="18"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Indexes", level=2, num="18.1"),
        Heading(name="Page", level=2, num="18.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.Page", level=3, num="18.2.1"
        ),
        Heading(name="Bloom Filter", level=2, num="18.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter",
            level=3,
            num="18.3.1",
        ),
        Heading(name="Parquet Column Types Support", level=3, num="18.3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes",
            level=4,
            num="18.3.2.1",
        ),
        Heading(name="Supported Operators", level=3, num="18.3.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.Operators",
            level=4,
            num="18.3.3.1",
        ),
        Heading(
            name="Only Considering Parquet Structure When Using Key Column Types",
            level=4,
            num="18.3.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.KeyColumnTypes",
            level=5,
            num="18.3.3.2.1",
        ),
        Heading(
            name="Only Considering Parquet Structure When Using Field Types",
            level=4,
            num="18.3.3.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.FieldTypes",
            level=5,
            num="18.3.3.3.1",
        ),
        Heading(
            name="Columns With Complex Datatypes That Have Bloom Filter Applied on Them",
            level=3,
            num="18.3.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.DataTypes.Complex",
            level=4,
            num="18.3.4.1",
        ),
        Heading(
            name="Consistent Output When Using Key Column Types", level=3, num="18.3.5"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.KeyColumnTypes",
            level=4,
            num="18.3.5.1",
        ),
        Heading(name="Consistent Output When Using Field Types", level=3, num="18.3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.FieldTypes",
            level=4,
            num="18.3.6.1",
        ),
        Heading(name="Dictionary", level=2, num="18.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Indexes.Dictionary",
            level=3,
            num="18.4.1",
        ),
        Heading(name="Metadata", level=1, num="19"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Metadata", level=2, num="19.1"),
        Heading(name="ParquetFormat", level=2, num="19.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat",
            level=3,
            num="19.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output",
            level=3,
            num="19.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content",
            level=3,
            num="19.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax",
            level=3,
            num="19.2.4",
        ),
        Heading(name="Extra Entries in Metadata", level=2, num="19.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.ExtraEntries",
            level=3,
            num="19.3.1",
        ),
        Heading(name="Metadata Types", level=2, num="19.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.File", level=3, num="19.4.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Column", level=3, num="19.4.2"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Header", level=3, num="19.4.3"
        ),
        Heading(name="Cache for ListObjects ", level=2, num="19.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects",
            level=3,
            num="19.5.1",
        ),
        Heading(name="Settings for Caching ListObjects", level=3, num="19.5.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.Settings",
            level=4,
            num="19.5.2.1",
        ),
        Heading(
            name="Caching ListObjects When the Same Bucket Exists in Different Storage Providers",
            level=3,
            num="19.5.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.SameBucket",
            level=4,
            num="19.5.3.1",
        ),
        Heading(name="Caching User Credentials", level=3, num="19.5.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.UserCredentials",
            level=4,
            num="19.5.4.1",
        ),
        Heading(name="Caching for Object Storage", level=2, num="19.6"),
        Heading(name="Test Schema For Metadata Caching", level=3, num="19.6.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage",
            level=3,
            num="19.6.2",
        ),
        Heading(name="Setting Propagation to All Nodes", level=3, num="19.6.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation",
            level=4,
            num="19.6.3.1",
        ),
        Heading(
            name="Propagate Settings to All Nodes When Set in the Profile (All Nodes)",
            level=4,
            num="19.6.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings",
            level=5,
            num="19.6.3.2.1",
        ),
        Heading(
            name="Propagate Settings to All Nodes When Set in the Profile (Initiator Node Only)",
            level=4,
            num="19.6.3.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings.InitiatorNode",
            level=5,
            num="19.6.3.3.1",
        ),
        Heading(name="Cache Eviction", level=3, num="19.6.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheEviction",
            level=4,
            num="19.6.4.1",
        ),
        Heading(name="Swarm", level=3, num="19.6.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm",
            level=4,
            num="19.6.5.1",
        ),
        Heading(name="Read With Swarm From S3Cluster", level=4, num="19.6.5.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.ReadWithS3Cluster",
            level=5,
            num="19.6.5.2.1",
        ),
        Heading(
            name="Swarm Node Stops During Query Execution", level=4, num="19.6.5.3"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.NodeStops",
            level=5,
            num="19.6.5.3.1",
        ),
        Heading(name="Object Storages", level=3, num="19.6.6"),
        Heading(name="S3 Storage", level=4, num="19.6.6.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.S3",
            level=5,
            num="19.6.6.1.1",
        ),
        Heading(name="Azure", level=4, num="19.6.6.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Azure",
            level=5,
            num="19.6.6.2.1",
        ),
        Heading(name="Google Cloud Storage", level=4, num="19.6.6.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.GoogleCloudStorage",
            level=5,
            num="19.6.6.3.1",
        ),
        Heading(name="MinIO", level=4, num="19.6.6.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MinIO",
            level=5,
            num="19.6.6.4.1",
        ),
        Heading(name="HDFS Storage", level=4, num="19.6.6.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HDFS",
            level=5,
            num="19.6.6.5.1",
        ),
        Heading(name="Wasabi", level=4, num="19.6.6.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Wasabi",
            level=5,
            num="19.6.6.6.1",
        ),
        Heading(name="DigitalOcean Spaces", level=4, num="19.6.6.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.DigitalOceanSpaces",
            level=5,
            num="19.6.6.7.1",
        ),
        Heading(name="Ceph RADOS Gateway", level=4, num="19.6.6.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CephRADOSGateway",
            level=5,
            num="19.6.6.8.1",
        ),
        Heading(name="Yandex Cloud Object Storage", level=4, num="19.6.6.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.YandexCloudObjectStorage",
            level=5,
            num="19.6.6.9.1",
        ),
        Heading(name="Cloudflare R2", level=4, num="19.6.6.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CloudflareR2",
            level=5,
            num="19.6.6.10.1",
        ),
        Heading(name="Alibaba Cloud OSS", level=4, num="19.6.6.11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AlibabaCloudOSS",
            level=5,
            num="19.6.6.11.1",
        ),
        Heading(
            name="All Functions and Engines That Can Store Parquet ",
            level=3,
            num="19.6.7",
        ),
        Heading(name="S3 Engine or Function", level=4, num="19.6.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3",
            level=5,
            num="19.6.7.1.1",
        ),
        Heading(name="S3Cluster", level=4, num="19.6.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3Cluster",
            level=5,
            num="19.6.7.2.1",
        ),
        Heading(name="IcebergS3 Engine or Function", level=4, num="19.6.7.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.IcebergS3",
            level=5,
            num="19.6.7.3.1",
        ),
        Heading(name="URL Engine or Function", level=4, num="19.6.7.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.URL",
            level=5,
            num="19.6.7.4.1",
        ),
        Heading(name="File Engine or Function", level=4, num="19.6.7.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.File",
            level=5,
            num="19.6.7.5.1",
        ),
        Heading(name="HDFS Engine or Function", level=4, num="19.6.7.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.HDFS",
            level=5,
            num="19.6.7.6.1",
        ),
        Heading(
            name="Trying To Cache Metadata When Using Engines Not Suited for Direct Parquet Storage",
            level=3,
            num="19.6.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NotSuitedEngines",
            level=4,
            num="19.6.8.1",
        ),
        Heading(name="Cache Invalidation", level=3, num="19.6.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Invalidation",
            level=4,
            num="19.6.9.1",
        ),
        Heading(name="Cache Clearing", level=3, num="19.6.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing",
            level=4,
            num="19.6.10.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing,OnCluster",
            level=4,
            num="19.6.10.2",
        ),
        Heading(
            name="Reading Metadata After Caching Is Completed", level=3, num="19.6.11"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.ReadMetadataAfterCaching",
            level=4,
            num="19.6.11.1",
        ),
        Heading(
            name="Caching When Reading From Hive Partitioned Parquet Files in Object Storage",
            level=3,
            num="19.6.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HivePartitioning",
            level=4,
            num="19.6.12.1",
        ),
        Heading(name="Caching Settings", level=3, num="19.6.13"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Settings",
            level=4,
            num="19.6.13.1",
        ),
        Heading(
            name="All Possible Settings That Can Be Used Along With Metadata Caching Settings",
            level=3,
            num="19.6.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AllSettings",
            level=4,
            num="19.6.14.1",
        ),
        Heading(
            name="Cases When Metadata Cache Speeds Up Query Execution",
            level=3,
            num="19.6.15",
        ),
        Heading(name="Count", level=4, num="19.6.15.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.Count",
            level=5,
            num="19.6.15.1.1",
        ),
        Heading(name="Min and Max", level=4, num="19.6.15.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.MinMax",
            level=5,
            num="19.6.15.2.1",
        ),
        Heading(name="Bloom Filter Caching", level=4, num="19.6.15.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.BloomFilter",
            level=5,
            num="19.6.15.3.1",
        ),
        Heading(name="Distinct Count", level=4, num="19.6.15.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.DistinctCount",
            level=5,
            num="19.6.15.4.1",
        ),
        Heading(name="File Schema", level=4, num="19.6.15.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.FileSchema",
            level=5,
            num="19.6.15.5.1",
        ),
        Heading(name="Maximum Size of Metadata Cache", level=3, num="19.6.16"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MaxSize",
            level=4,
            num="19.6.16.1",
        ),
        Heading(
            name="File With The Same Name But Different Location",
            level=3,
            num="19.6.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SameNameDifferentLocation",
            level=4,
            num="19.6.17.1",
        ),
        Heading(name="Hits and Misses Counter", level=3, num="19.6.18"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HitsMissesCounter",
            level=4,
            num="19.6.18.1",
        ),
        Heading(name="Nested Queries With Metadata Caching", level=3, num="19.6.19"),
        Heading(
            name="Join Two Parquet Files From an Object Storage",
            level=4,
            num="19.6.19.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Join",
            level=5,
            num="19.6.19.1.1",
        ),
        Heading(name="Basic Nested Subquery", level=4, num="19.6.19.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Basic",
            level=5,
            num="19.6.19.2.1",
        ),
        Heading(name="Union All with Nested Parquet Queries", level=4, num="19.6.19.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionAll",
            level=5,
            num="19.6.19.3.1",
        ),
        Heading(
            name="Nested Subquery with an Additional Filter and Aggregation",
            level=4,
            num="19.6.19.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.FilterAggregation",
            level=5,
            num="19.6.19.4.1",
        ),
        Heading(name="Combining a UNION with a JOIN", level=4, num="19.6.19.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionJoin",
            level=5,
            num="19.6.19.5.1",
        ),
        Heading(name="Deeply Nested JOIN", level=4, num="19.6.19.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.DeeplyNestedJoin",
            level=5,
            num="19.6.19.6.1",
        ),
        Heading(name="Cachable Metadata Types", level=2, num="19.7"),
        Heading(name="Metadata Generated by ClickHouse", level=3, num="19.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ClickHouse",
            level=4,
            num="19.7.1.1",
        ),
        Heading(name="Metadata Generated by Parquetify", level=3, num="19.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.Parquetify",
            level=4,
            num="19.7.2.1",
        ),
        Heading(name="Metadata Generated by DuckDB", level=3, num="19.7.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.DuckDB",
            level=4,
            num="19.7.3.1",
        ),
        Heading(name="Metadata Generated by Apache Arrow", level=3, num="19.7.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ApacheArrow",
            level=4,
            num="19.7.4.1",
        ),
        Heading(name="Error Recovery", level=1, num="20"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.MagicNumber",
            level=2,
            num="20.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.File",
            level=2,
            num="20.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Column",
            level=2,
            num="20.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageHeader",
            level=2,
            num="20.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageData",
            level=2,
            num="20.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Checksum",
            level=2,
            num="20.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values",
            level=2,
            num="20.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Date",
            level=3,
            num="20.7.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Int",
            level=3,
            num="20.7.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.BigInt",
            level=3,
            num="20.7.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.SmallInt",
            level=3,
            num="20.7.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TinyInt",
            level=3,
            num="20.7.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UInt",
            level=3,
            num="20.7.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UBigInt",
            level=3,
            num="20.7.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.USmallInt",
            level=3,
            num="20.7.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UTinyInt",
            level=3,
            num="20.7.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampUS",
            level=3,
            num="20.7.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampMS",
            level=3,
            num="20.7.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Bool",
            level=3,
            num="20.7.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Float",
            level=3,
            num="20.7.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Double",
            level=3,
            num="20.7.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeMS",
            level=3,
            num="20.7.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeUS",
            level=3,
            num="20.7.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeNS",
            level=3,
            num="20.7.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.String",
            level=3,
            num="20.7.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Binary",
            level=3,
            num="20.7.19",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.FixedLengthByteArray",
            level=3,
            num="20.7.20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Decimal",
            level=3,
            num="20.7.21",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.List",
            level=3,
            num="20.7.22",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Struct",
            level=3,
            num="20.7.23",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Map",
            level=3,
            num="20.7.24",
        ),
        Heading(name="Interoperability Between ARM and x86", level=1, num="21"),
        Heading(
            name="Importing and Exporting Parquet Files On ARM That Were Generated On x86 Machine",
            level=2,
            num="21.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.x86.To.ARM",
            level=3,
            num="21.1.1",
        ),
        Heading(
            name="Importing and Exporting Parquet Files On x86 That Were Generated On ARM Machine",
            level=2,
            num="21.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.ARM.To.x86",
            level=3,
            num="21.2.1",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet,
        RQ_SRS_032_ClickHouse_Parquet_SupportedVersions,
        RQ_SRS_032_ClickHouse_Parquet_ClickHouseLocal,
        RQ_SRS_032_ClickHouse_Parquet_Offsets,
        RQ_SRS_032_ClickHouse_Parquet_Offsets_MonotonicallyIncreasing,
        RQ_SRS_032_ClickHouse_Parquet_Query_Cache,
        RQ_SRS_032_ClickHouse_Parquet_Import,
        RQ_SRS_032_ClickHouse_Parquet_Import_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_Import_Glob,
        RQ_SRS_032_ClickHouse_Parquet_Import_Glob_MultiDirectory,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Conversion,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BLOB,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BOOL,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT8,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT8,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT16,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT16,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT32,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT32,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_UINT64,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_INT64,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FLOAT,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DOUBLE,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_ms,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_ns,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DATE_us,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIME_ms,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ms,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_ns,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_TIMESTAMP_us,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRING,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_BINARY,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_FixedLengthByteArray_FLOAT16,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_DECIMAL_Filter,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_LIST,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_ARRAY,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_STRUCT,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported_MAP,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_DateUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_TimestampUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_TimeUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_NullValues,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Nullable,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_LowCardinality,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Nested,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_ImportInto_Unknown,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Unsupported_ChunkedArray,
        RQ_SRS_032_ClickHouse_Parquet_Import_FilterPushdown,
        RQ_SRS_032_ClickHouse_Parquet_Import_FilterPushdown_MinMax_Operations,
        RQ_SRS_032_ClickHouse_Parquet_Import_Projections,
        RQ_SRS_032_ClickHouse_Parquet_Import_SkipColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_SkipValues,
        RQ_SRS_032_ClickHouse_Parquet_Import_AutoTypecast,
        RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataPageSize,
        RQ_SRS_032_ClickHouse_Parquet_Import_NewTable,
        RQ_SRS_032_ClickHouse_Parquet_Import_Performance_CountFromMetadata,
        RQ_SRS_032_ClickHouse_Parquet_Import_Performance_ParallelProcessing,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_Complex,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_NotImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNotNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_NonArrayIntoNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_ChunkedColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Delta,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaStrings,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_ByteStreamSplit,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_Libraries,
        RQ_SRS_032_ClickHouse_Parquet_Libraries_Pyarrow,
        RQ_SRS_032_ClickHouse_Parquet_Libraries_PySpark,
        RQ_SRS_032_ClickHouse_Parquet_Libraries_Pandas,
        RQ_SRS_032_ClickHouse_Parquet_Libraries_ParquetGO,
        RQ_SRS_032_ClickHouse_Parquet_Libraries_H2OAI,
        RQ_SRS_032_ClickHouse_Parquet_Export,
        RQ_SRS_032_ClickHouse_Parquet_Export_Outfile_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BLOB,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BOOL,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT8,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT8,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT16,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT16,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT32,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT32,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_UINT64,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_INT64,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FLOAT,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DOUBLE,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_ms,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_ns,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DATE_us,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIME_ms,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ms,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_ns,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_TIMESTAMP_us,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRING,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_BINARY,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_FixedLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_DECIMAL_Filter,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_LIST,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_ARRAY,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_STRUCT,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Supported_MAP,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nullable,
        RQ_SRS_032_ClickHouse_Parquet_Export_Nested,
        RQ_SRS_032_ClickHouse_Parquet_Export_Nested_Complex,
        RQ_SRS_032_ClickHouse_Parquet_Export_ChunkedColumns,
        RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Insert,
        RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_MergeTreePart,
        RQ_SRS_032_ClickHouse_Parquet_Export_MultiChunkUpload_Settings_RowGroupSize,
        RQ_SRS_032_ClickHouse_Export_Parquet_Join,
        RQ_SRS_032_ClickHouse_Parquet_Export_Union,
        RQ_SRS_032_ClickHouse_Parquet_Export_Union_Multiple,
        RQ_SRS_032_ClickHouse_Parquet_Export_View,
        RQ_SRS_032_ClickHouse_Parquet_Export_Select_MaterializedView,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_RunLength,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Delta,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_DeltaStrings,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_ByteStreamSplit,
        RQ_SRS_032_ClickHouse_Parquet_Export_Settings_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsString,
        RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsFixedByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Export_Settings_ParquetVersion,
        RQ_SRS_032_ClickHouse_Parquet_Export_Settings_CompressionMethod,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_TypeConversionFunction,
        RQ_SRS_032_ClickHouse_Parquet_NativeReader,
        RQ_SRS_032_ClickHouse_Parquet_NativeReader_DataTypes,
        RQ_SRS_032_ClickHouse_Parquet_Hive,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_File,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Column_Modular,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Column_Keys,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCM,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Algorithms_AESGCMCTR,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters_Algorythm,
        RQ_SRS_032_ClickHouse_Parquet_Encryption_Parameters_Plaintext_Footer,
        RQ_SRS_032_ClickHouse_Parquet_Structure,
        RQ_SRS_032_ClickHouse_Parquet_Compression_None,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Hadoop,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Snappy,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Zstd,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Lzo,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3_HivePartitioning,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgreSQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_ReadableExternalTable,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplacingMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_SummingMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_AggregatingMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_CollapsingMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_VersionedCollapsingMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_GraphiteMergeTree,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MongoDB,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_Kafka,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_EmbeddedRocksDB,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL,
        RQ_SRS_032_ClickHouse_Parquet_Indexes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_Page,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_Operators,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes_Ignore_KeyColumnTypes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ColumnTypes_Ignore_FieldTypes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_DataTypes_Complex,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ConsistentOutput_KeyColumnTypes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_ConsistentOutput_FieldTypes,
        RQ_SRS_032_ClickHouse_Parquet_Indexes_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_Metadata,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat_Output,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_Content,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_ExtraEntries,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_File,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Column,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Header,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_Settings,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_SameBucket,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Cache_ListObjects_UserCredentials,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SettingPropagation_ProfileSettings_InitiatorNode,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheEviction,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_ReadWithS3Cluster,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Swarm_NodeStops,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_S3,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Azure,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_GoogleCloudStorage,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MinIO,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Wasabi,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_DigitalOceanSpaces,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CephRADOSGateway,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_YandexCloudObjectStorage,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CloudflareR2,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AlibabaCloudOSS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_S3Cluster,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_IcebergS3,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_EnginesAndFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NotSuitedEngines,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Invalidation,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheClearing,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_CacheClearing_OnCluster,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_ReadMetadataAfterCaching,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HivePartitioning,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_Settings,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_AllSettings,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_Count,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_MinMax,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_BloomFilter,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_DistinctCount,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SpeedUpQueryExecution_FileSchema,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MaxSize,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_SameNameDifferentLocation,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_HitsMissesCounter,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_Join,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_Basic,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_UnionAll,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_FilterAggregation,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_NestedQueries_UnionJoin,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_ClickHouse,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_Parquetify,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_DuckDB,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Caching_ObjectStorage_MetadataTypes_ApacheArrow,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_MagicNumber,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_File,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_Column,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_PageHeader,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_PageData,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Metadata_Checksum,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Date,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Int,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_BigInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_SmallInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TinyInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UBigInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_USmallInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_UTinyInt,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampUS,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimestampMS,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Bool,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Float,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Double,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeMS,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeUS,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_TimeNS,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_String,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Binary,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_FixedLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Decimal,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_List,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Struct,
        RQ_SRS_032_ClickHouse_Parquet_ErrorRecovery_Corrupt_Values_Map,
        RQ_SRS_032_ClickHouse_Parquet_Interoperability_From_x86_To_ARM,
        RQ_SRS_032_ClickHouse_Parquet_Interoperability_From_ARM_To_x86,
    ),
    content=r"""
# SRS032 ClickHouse Parquet Data Format
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Test Schema](#test-schema)
* 4 [Feature Diagram](#feature-diagram)
* 5 [Working With Parquet](#working-with-parquet)
    * 5.1 [RQ.SRS-032.ClickHouse.Parquet](#rqsrs-032clickhouseparquet)
* 6 [Supported Parquet Versions](#supported-parquet-versions)
    * 6.1 [RQ.SRS-032.ClickHouse.Parquet.SupportedVersions](#rqsrs-032clickhouseparquetsupportedversions)
    * 6.2 [RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal](#rqsrs-032clickhouseparquetclickhouselocal)
* 7 [Offsets](#offsets)
    * 7.1 [RQ.SRS-032.ClickHouse.Parquet.Offsets](#rqsrs-032clickhouseparquetoffsets)
        * 7.1.1 [RQ.SRS-032.ClickHouse.Parquet.Offsets.MonotonicallyIncreasing](#rqsrs-032clickhouseparquetoffsetsmonotonicallyincreasing)
* 8 [Query Cache](#query-cache)
    * 8.1 [RQ.SRS-032.ClickHouse.Parquet.Query.Cache](#rqsrs-032clickhouseparquetquerycache)
* 9 [Import from Parquet Files](#import-from-parquet-files)
    * 9.1 [RQ.SRS-032.ClickHouse.Parquet.Import](#rqsrs-032clickhouseparquetimport)
    * 9.2 [Auto Detect Parquet File When Importing](#auto-detect-parquet-file-when-importing)
        * 9.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquetimportautodetectparquetfileformat)
    * 9.3 [Glob Patterns](#glob-patterns)
        * 9.3.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Glob](#rqsrs-032clickhouseparquetimportglob)
        * 9.3.2 [RQ.SRS-032.ClickHouse.Parquet.Import.Glob.MultiDirectory](#rqsrs-032clickhouseparquetimportglobmultidirectory)
    * 9.4 [Supported Datatypes](#supported-datatypes)
        * 9.4.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Conversion](#rqsrs-032clickhouseparquetimportdatatypesconversion)
        * 9.4.2 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported](#rqsrs-032clickhouseparquetimportdatatypessupported)
        * 9.4.3 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BLOB](#rqsrs-032clickhouseparquetimportdatatypessupportedblob)
        * 9.4.4 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BOOL](#rqsrs-032clickhouseparquetimportdatatypessupportedbool)
        * 9.4.5 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT8](#rqsrs-032clickhouseparquetimportdatatypessupporteduint8)
        * 9.4.6 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT8](#rqsrs-032clickhouseparquetimportdatatypessupportedint8)
        * 9.4.7 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT16](#rqsrs-032clickhouseparquetimportdatatypessupporteduint16)
        * 9.4.8 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT16](#rqsrs-032clickhouseparquetimportdatatypessupportedint16)
        * 9.4.9 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT32](#rqsrs-032clickhouseparquetimportdatatypessupporteduint32)
        * 9.4.10 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT32](#rqsrs-032clickhouseparquetimportdatatypessupportedint32)
        * 9.4.11 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT64](#rqsrs-032clickhouseparquetimportdatatypessupporteduint64)
        * 9.4.12 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT64](#rqsrs-032clickhouseparquetimportdatatypessupportedint64)
        * 9.4.13 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FLOAT](#rqsrs-032clickhouseparquetimportdatatypessupportedfloat)
        * 9.4.14 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DOUBLE](#rqsrs-032clickhouseparquetimportdatatypessupporteddouble)
        * 9.4.15 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE](#rqsrs-032clickhouseparquetimportdatatypessupporteddate)
        * 9.4.16 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ms](#rqsrs-032clickhouseparquetimportdatatypessupporteddatems)
        * 9.4.17 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ns](#rqsrs-032clickhouseparquetimportdatatypessupporteddatens)
        * 9.4.18 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.us](#rqsrs-032clickhouseparquetimportdatatypessupporteddateus)
        * 9.4.19 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIME.ms](#rqsrs-032clickhouseparquetimportdatatypessupportedtimems)
        * 9.4.20 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ms](#rqsrs-032clickhouseparquetimportdatatypessupportedtimestampms)
        * 9.4.21 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ns](#rqsrs-032clickhouseparquetimportdatatypessupportedtimestampns)
        * 9.4.22 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.us](#rqsrs-032clickhouseparquetimportdatatypessupportedtimestampus)
        * 9.4.23 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRING](#rqsrs-032clickhouseparquetimportdatatypessupportedstring)
        * 9.4.24 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BINARY](#rqsrs-032clickhouseparquetimportdatatypessupportedbinary)
        * 9.4.25 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray](#rqsrs-032clickhouseparquetimportdatatypessupportedfixedlengthbytearray)
        * 9.4.26 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray.FLOAT16](#rqsrs-032clickhouseparquetimportdatatypessupportedfixedlengthbytearrayfloat16)
        * 9.4.27 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL](#rqsrs-032clickhouseparquetimportdatatypessupporteddecimal)
        * 9.4.28 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL.Filter](#rqsrs-032clickhouseparquetimportdatatypessupporteddecimalfilter)
        * 9.4.29 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.LIST](#rqsrs-032clickhouseparquetimportdatatypessupportedlist)
        * 9.4.30 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.ARRAY](#rqsrs-032clickhouseparquetimportdatatypessupportedarray)
        * 9.4.31 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRUCT](#rqsrs-032clickhouseparquetimportdatatypessupportedstruct)
        * 9.4.32 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.MAP](#rqsrs-032clickhouseparquetimportdatatypessupportedmap)
        * 9.4.33 [UTCAdjusted](#utcadjusted)
            * 9.4.33.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.DateUTCAdjusted](#rqsrs-032clickhouseparquetimportdatatypesdateutcadjusted)
            * 9.4.33.2 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimestampUTCAdjusted](#rqsrs-032clickhouseparquetimportdatatypestimestamputcadjusted)
            * 9.4.33.3 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimeUTCAdjusted](#rqsrs-032clickhouseparquetimportdatatypestimeutcadjusted)
        * 9.4.34 [Nullable](#nullable)
            * 9.4.34.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.NullValues](#rqsrs-032clickhouseparquetimportdatatypesnullvalues)
            * 9.4.34.2 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nullable](#rqsrs-032clickhouseparquetimportdatatypesimportintonullable)
        * 9.4.35 [LowCardinality](#lowcardinality)
            * 9.4.35.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.LowCardinality](#rqsrs-032clickhouseparquetimportdatatypesimportintolowcardinality)
        * 9.4.36 [Nested](#nested)
            * 9.4.36.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nested](#rqsrs-032clickhouseparquetimportdatatypesimportintonested)
        * 9.4.37 [UNKNOWN](#unknown)
            * 9.4.37.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Unknown](#rqsrs-032clickhouseparquetimportdatatypesimportintounknown)
    * 9.5 [Unsupported Datatypes](#unsupported-datatypes)
        * 9.5.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported](#rqsrs-032clickhouseparquetimportdatatypesunsupported)
        * 9.5.2 [RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported.ChunkedArray](#rqsrs-032clickhouseparquetimportdatatypesunsupportedchunkedarray)
    * 9.6 [Filter Pushdown](#filter-pushdown)
        * 9.6.1 [RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown](#rqsrs-032clickhouseparquetimportfilterpushdown)
        * 9.6.2 [Supported Operations that utilize Min/Max Statistics](#supported-operations-that-utilize-minmax-statistics)
            * 9.6.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown.MinMax.Operations](#rqsrs-032clickhouseparquetimportfilterpushdownminmaxoperations)
    * 9.7 [Projections](#projections)
        * 9.7.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Projections](#rqsrs-032clickhouseparquetimportprojections)
    * 9.8 [Skip Columns](#skip-columns)
        * 9.8.1 [RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns](#rqsrs-032clickhouseparquetimportskipcolumns)
    * 9.9 [Skip Values](#skip-values)
        * 9.9.1 [RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues](#rqsrs-032clickhouseparquetimportskipvalues)
    * 9.10 [Auto Typecast](#auto-typecast)
        * 9.10.1 [RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast](#rqsrs-032clickhouseparquetimportautotypecast)
    * 9.11 [Row Group Size](#row-group-size)
        * 9.11.1 [RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize](#rqsrs-032clickhouseparquetimportrowgroupsize)
    * 9.12 [Data Page Size](#data-page-size)
        * 9.12.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize](#rqsrs-032clickhouseparquetimportdatapagesize)
    * 9.13 [Import Into New Table](#import-into-new-table)
        * 9.13.1 [RQ.SRS-032.ClickHouse.Parquet.Import.NewTable](#rqsrs-032clickhouseparquetimportnewtable)
    * 9.14 [Performance](#performance)
        * 9.14.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Performance.CountFromMetadata](#rqsrs-032clickhouseparquetimportperformancecountfrommetadata)
        * 9.14.2 [RQ.SRS-032.ClickHouse.Parquet.Import.Performance.ParallelProcessing](#rqsrs-032clickhouseparquetimportperformanceparallelprocessing)
    * 9.15 [Import Nested Types](#import-nested-types)
        * 9.15.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested](#rqsrs-032clickhouseparquetimportnestedarrayintonested)
        * 9.15.2 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.Complex](#rqsrs-032clickhouseparquetimportnestedcomplex)
        * 9.15.3 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested](#rqsrs-032clickhouseparquetimportnestedarrayintonestedimportnested)
        * 9.15.4 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested](#rqsrs-032clickhouseparquetimportnestedarrayintonestednotimportnested)
        * 9.15.5 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested](#rqsrs-032clickhouseparquetimportnestedarrayintonotnested)
        * 9.15.6 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested](#rqsrs-032clickhouseparquetimportnestednonarrayintonested)
    * 9.16 [Import Chunked Columns](#import-chunked-columns)
        * 9.16.1 [RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns](#rqsrs-032clickhouseparquetimportchunkedcolumns)
    * 9.17 [Import Encoded](#import-encoded)
        * 9.17.1 [Plain (Import)](#plain-import)
            * 9.17.1.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain](#rqsrs-032clickhouseparquetimportencodingplain)
        * 9.17.2 [Dictionary (Import)](#dictionary-import)
            * 9.17.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Dictionary](#rqsrs-032clickhouseparquetimportencodingdictionary)
        * 9.17.3 [Run Length Encoding (Import)](#run-length-encoding-import)
            * 9.17.3.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength](#rqsrs-032clickhouseparquetimportencodingrunlength)
        * 9.17.4 [Delta (Import)](#delta-import)
            * 9.17.4.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta](#rqsrs-032clickhouseparquetimportencodingdelta)
        * 9.17.5 [Delta-length byte array (Import)](#delta-length-byte-array-import)
            * 9.17.5.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray](#rqsrs-032clickhouseparquetimportencodingdeltalengthbytearray)
        * 9.17.6 [Delta Strings (Import)](#delta-strings-import)
            * 9.17.6.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings](#rqsrs-032clickhouseparquetimportencodingdeltastrings)
        * 9.17.7 [Byte Stream Split (Import)](#byte-stream-split-import)
            * 9.17.7.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit](#rqsrs-032clickhouseparquetimportencodingbytestreamsplit)
    * 9.18 [Import Settings](#import-settings)
        * 9.18.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested](#rqsrs-032clickhouseparquetimportsettingsimportnested)
        * 9.18.2 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetimportsettingscaseinsensitivecolumnmatching)
        * 9.18.3 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns](#rqsrs-032clickhouseparquetimportsettingsallowmissingcolumns)
        * 9.18.4 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetimportsettingsskipcolumnswithunsupportedtypesinschemainference)
    * 9.19 [Libraries](#libraries)
        * 9.19.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries](#rqsrs-032clickhouseparquetlibraries)
        * 9.19.2 [Pyarrow](#pyarrow)
            * 9.19.2.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries.Pyarrow](#rqsrs-032clickhouseparquetlibrariespyarrow)
        * 9.19.3 [PySpark](#pyspark)
            * 9.19.3.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries.PySpark](#rqsrs-032clickhouseparquetlibrariespyspark)
        * 9.19.4 [Pandas](#pandas)
            * 9.19.4.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries.Pandas](#rqsrs-032clickhouseparquetlibrariespandas)
        * 9.19.5 [parquet-go](#parquet-go)
            * 9.19.5.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries.ParquetGO](#rqsrs-032clickhouseparquetlibrariesparquetgo)
        * 9.19.6 [H2OAI](#h2oai)
            * 9.19.6.1 [RQ.SRS-032.ClickHouse.Parquet.Libraries.H2OAI](#rqsrs-032clickhouseparquetlibrariesh2oai)
* 10 [Export from Parquet Files](#export-from-parquet-files)
    * 10.1 [RQ.SRS-032.ClickHouse.Parquet.Export](#rqsrs-032clickhouseparquetexport)
    * 10.2 [Auto Detect Parquet File When Exporting](#auto-detect-parquet-file-when-exporting)
        * 10.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquetexportoutfileautodetectparquetfileformat)
    * 10.3 [Supported Data types](#supported-data-types)
        * 10.3.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported](#rqsrs-032clickhouseparquetexportdatatypessupported)
        * 10.3.2 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BLOB](#rqsrs-032clickhouseparquetexportdatatypessupportedblob)
        * 10.3.3 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BOOL](#rqsrs-032clickhouseparquetexportdatatypessupportedbool)
        * 10.3.4 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT8](#rqsrs-032clickhouseparquetexportdatatypessupporteduint8)
        * 10.3.5 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT8](#rqsrs-032clickhouseparquetexportdatatypessupportedint8)
        * 10.3.6 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT16](#rqsrs-032clickhouseparquetexportdatatypessupporteduint16)
        * 10.3.7 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT16](#rqsrs-032clickhouseparquetexportdatatypessupportedint16)
        * 10.3.8 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT32](#rqsrs-032clickhouseparquetexportdatatypessupporteduint32)
        * 10.3.9 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT32](#rqsrs-032clickhouseparquetexportdatatypessupportedint32)
        * 10.3.10 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT64](#rqsrs-032clickhouseparquetexportdatatypessupporteduint64)
        * 10.3.11 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT64](#rqsrs-032clickhouseparquetexportdatatypessupportedint64)
        * 10.3.12 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FLOAT](#rqsrs-032clickhouseparquetexportdatatypessupportedfloat)
        * 10.3.13 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DOUBLE](#rqsrs-032clickhouseparquetexportdatatypessupporteddouble)
        * 10.3.14 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE](#rqsrs-032clickhouseparquetexportdatatypessupporteddate)
        * 10.3.15 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ms](#rqsrs-032clickhouseparquetexportdatatypessupporteddatems)
        * 10.3.16 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ns](#rqsrs-032clickhouseparquetexportdatatypessupporteddatens)
        * 10.3.17 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.us](#rqsrs-032clickhouseparquetexportdatatypessupporteddateus)
        * 10.3.18 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIME.ms](#rqsrs-032clickhouseparquetexportdatatypessupportedtimems)
        * 10.3.19 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ms](#rqsrs-032clickhouseparquetexportdatatypessupportedtimestampms)
        * 10.3.20 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ns](#rqsrs-032clickhouseparquetexportdatatypessupportedtimestampns)
        * 10.3.21 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.us](#rqsrs-032clickhouseparquetexportdatatypessupportedtimestampus)
        * 10.3.22 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRING](#rqsrs-032clickhouseparquetexportdatatypessupportedstring)
        * 10.3.23 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BINARY](#rqsrs-032clickhouseparquetexportdatatypessupportedbinary)
        * 10.3.24 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FixedLengthByteArray](#rqsrs-032clickhouseparquetexportdatatypessupportedfixedlengthbytearray)
        * 10.3.25 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL](#rqsrs-032clickhouseparquetexportdatatypessupporteddecimal)
        * 10.3.26 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL.Filter](#rqsrs-032clickhouseparquetexportdatatypessupporteddecimalfilter)
        * 10.3.27 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.LIST](#rqsrs-032clickhouseparquetexportdatatypessupportedlist)
        * 10.3.28 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.ARRAY](#rqsrs-032clickhouseparquetexportdatatypessupportedarray)
        * 10.3.29 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRUCT](#rqsrs-032clickhouseparquetexportdatatypessupportedstruct)
        * 10.3.30 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.MAP](#rqsrs-032clickhouseparquetexportdatatypessupportedmap)
        * 10.3.31 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nullable](#rqsrs-032clickhouseparquetexportdatatypesnullable)
    * 10.4 [Working With Nested Types Export](#working-with-nested-types-export)
        * 10.4.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Nested](#rqsrs-032clickhouseparquetexportnested)
        * 10.4.2 [RQ.SRS-032.ClickHouse.Parquet.Export.Nested.Complex](#rqsrs-032clickhouseparquetexportnestedcomplex)
    * 10.5 [Exporting Chunked Columns](#exporting-chunked-columns)
        * 10.5.1 [RQ.SRS-032.ClickHouse.Parquet.Export.ChunkedColumns](#rqsrs-032clickhouseparquetexportchunkedcolumns)
    * 10.6 [Multi-chunk Upload (Split to Rowgroups)](#multi-chunk-upload-split-to-rowgroups)
        * 10.6.1 [Inserting Data Into Parquet Files](#inserting-data-into-parquet-files)
            * 10.6.1.1 [RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Insert](#rqsrs-032clickhouseparquetexportmultichunkuploadinsert)
        * 10.6.2 [Move from MergeTree Part to Parquet](#move-from-mergetree-part-to-parquet)
            * 10.6.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.MergeTreePart](#rqsrs-032clickhouseparquetexportmultichunkuploadmergetreepart)
        * 10.6.3 [Settings for Manipulating the Size of Row Groups](#settings-for-manipulating-the-size-of-row-groups)
            * 10.6.3.1 [RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Settings.RowGroupSize](#rqsrs-032clickhouseparquetexportmultichunkuploadsettingsrowgroupsize)
    * 10.7 [Query Types](#query-types)
        * 10.7.1 [JOIN](#join)
            * 10.7.1.1 [RQ.SRS-032.ClickHouse.Export.Parquet.Join](#rqsrs-032clickhouseexportparquetjoin)
        * 10.7.2 [UNION](#union)
            * 10.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Union](#rqsrs-032clickhouseparquetexportunion)
            * 10.7.2.2 [RQ.SRS-032.ClickHouse.Parquet.Export.Union.Multiple](#rqsrs-032clickhouseparquetexportunionmultiple)
        * 10.7.3 [RQ.SRS-032.ClickHouse.Parquet.Export.View](#rqsrs-032clickhouseparquetexportview)
        * 10.7.4 [RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView](#rqsrs-032clickhouseparquetexportselectmaterializedview)
    * 10.8 [Export Encoded](#export-encoded)
        * 10.8.1 [Plain (Export)](#plain-export)
            * 10.8.1.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain](#rqsrs-032clickhouseparquetexportencodingplain)
        * 10.8.2 [Dictionary (Export)](#dictionary-export)
            * 10.8.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Dictionary](#rqsrs-032clickhouseparquetexportencodingdictionary)
        * 10.8.3 [Run Length Encoding (Export)](#run-length-encoding-export)
            * 10.8.3.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength](#rqsrs-032clickhouseparquetexportencodingrunlength)
        * 10.8.4 [Delta (Export)](#delta-export)
            * 10.8.4.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta](#rqsrs-032clickhouseparquetexportencodingdelta)
        * 10.8.5 [Delta-length byte array (Export)](#delta-length-byte-array-export)
            * 10.8.5.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray](#rqsrs-032clickhouseparquetexportencodingdeltalengthbytearray)
        * 10.8.6 [Delta Strings (Export)](#delta-strings-export)
            * 10.8.6.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings](#rqsrs-032clickhouseparquetexportencodingdeltastrings)
        * 10.8.7 [Byte Stream Split (Export)](#byte-stream-split-export)
            * 10.8.7.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit](#rqsrs-032clickhouseparquetexportencodingbytestreamsplit)
    * 10.9 [Export Settings](#export-settings)
        * 10.9.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize](#rqsrs-032clickhouseparquetexportsettingsrowgroupsize)
        * 10.9.2 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString](#rqsrs-032clickhouseparquetexportsettingsstringasstring)
        * 10.9.3 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray](#rqsrs-032clickhouseparquetexportsettingsstringasfixedbytearray)
        * 10.9.4 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion](#rqsrs-032clickhouseparquetexportsettingsparquetversion)
        * 10.9.5 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod](#rqsrs-032clickhouseparquetexportsettingscompressionmethod)
    * 10.10 [Type Conversion](#type-conversion)
        * 10.10.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction](#rqsrs-032clickhouseparquetdatatypestypeconversionfunction)
* 11 [Native Reader](#native-reader)
    * 11.1 [RQ.SRS-032.ClickHouse.Parquet.NativeReader](#rqsrs-032clickhouseparquetnativereader)
    * 11.2 [Data Types Support](#data-types-support)
        * 11.2.1 [RQ.SRS-032.ClickHouse.Parquet.NativeReader.DataTypes](#rqsrs-032clickhouseparquetnativereaderdatatypes)
* 12 [Hive Partitioning](#hive-partitioning)
    * 12.1 [RQ.SRS-032.ClickHouse.Parquet.Hive](#rqsrs-032clickhouseparquethive)
* 13 [Parquet Encryption](#parquet-encryption)
    * 13.1 [File Encryption](#file-encryption)
        * 13.1.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption.File](#rqsrs-032clickhouseparquetencryptionfile)
    * 13.2 [Column Encryption](#column-encryption)
        * 13.2.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Modular](#rqsrs-032clickhouseparquetencryptioncolumnmodular)
        * 13.2.2 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Keys](#rqsrs-032clickhouseparquetencryptioncolumnkeys)
    * 13.3 [Encryption Algorithms](#encryption-algorithms)
        * 13.3.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCM](#rqsrs-032clickhouseparquetencryptionalgorithmsaesgcm)
        * 13.3.2 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCMCTR](#rqsrs-032clickhouseparquetencryptionalgorithmsaesgcmctr)
    * 13.4 [EncryptionParameters](#encryptionparameters)
        * 13.4.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters](#rqsrs-032clickhouseparquetencryptionparameters)
            * 13.4.1.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Algorythm](#rqsrs-032clickhouseparquetencryptionparametersalgorythm)
            * 13.4.1.2 [RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Plaintext.Footer](#rqsrs-032clickhouseparquetencryptionparametersplaintextfooter)
* 14 [DESCRIBE Parquet](#describe-parquet)
    * 14.1 [RQ.SRS-032.ClickHouse.Parquet.Structure](#rqsrs-032clickhouseparquetstructure)
* 15 [Compression](#compression)
    * 15.1 [None](#none)
        * 15.1.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.None](#rqsrs-032clickhouseparquetcompressionnone)
    * 15.2 [Gzip](#gzip)
        * 15.2.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip](#rqsrs-032clickhouseparquetcompressiongzip)
    * 15.3 [Brotli](#brotli)
        * 15.3.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli](#rqsrs-032clickhouseparquetcompressionbrotli)
    * 15.4 [Lz4](#lz4)
        * 15.4.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4](#rqsrs-032clickhouseparquetcompressionlz4)
    * 15.5 [Lz4Raw](#lz4raw)
        * 15.5.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw](#rqsrs-032clickhouseparquetcompressionlz4raw)
    * 15.6 [Lz4Hadoop](#lz4hadoop)
        * 15.6.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Hadoop](#rqsrs-032clickhouseparquetcompressionlz4hadoop)
    * 15.7 [Snappy](#snappy)
        * 15.7.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Snappy](#rqsrs-032clickhouseparquetcompressionsnappy)
    * 15.8 [Zstd](#zstd)
        * 15.8.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Zstd](#rqsrs-032clickhouseparquetcompressionzstd)
    * 15.9 [Unsupported Compression](#unsupported-compression)
        * 15.9.1 [Lzo](#lzo)
            * 15.9.1.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo](#rqsrs-032clickhouseparquetunsupportedcompressionlzo)
* 16 [Table Functions](#table-functions)
    * 16.1 [URL](#url)
        * 16.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL](#rqsrs-032clickhouseparquettablefunctionsurl)
    * 16.2 [File](#file)
        * 16.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File](#rqsrs-032clickhouseparquettablefunctionsfile)
        * 16.2.2 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquettablefunctionsfileautodetectparquetfileformat)
    * 16.3 [S3](#s3)
        * 16.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3](#rqsrs-032clickhouseparquettablefunctionss3)
        * 16.3.2 [Detecting Hive Partitioning](#detecting-hive-partitioning)
            * 16.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3.HivePartitioning](#rqsrs-032clickhouseparquettablefunctionss3hivepartitioning)
    * 16.4 [JDBC](#jdbc)
        * 16.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC](#rqsrs-032clickhouseparquettablefunctionsjdbc)
    * 16.5 [ODBC](#odbc)
        * 16.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC](#rqsrs-032clickhouseparquettablefunctionsodbc)
    * 16.6 [HDFS](#hdfs)
        * 16.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS](#rqsrs-032clickhouseparquettablefunctionshdfs)
    * 16.7 [Remote](#remote)
        * 16.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote](#rqsrs-032clickhouseparquettablefunctionsremote)
    * 16.8 [MySQL](#mysql)
        * 16.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL](#rqsrs-032clickhouseparquettablefunctionsmysql)
    * 16.9 [PostgreSQL](#postgresql)
        * 16.9.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL](#rqsrs-032clickhouseparquettablefunctionspostgresql)
* 17 [Table Engines](#table-engines)
    * 17.1 [Readable External Table](#readable-external-table)
        * 17.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.ReadableExternalTable](#rqsrs-032clickhouseparquettableenginesreadableexternaltable)
    * 17.2 [MergeTree](#mergetree)
        * 17.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree](#rqsrs-032clickhouseparquettableenginesmergetreemergetree)
        * 17.2.2 [ReplicatedMergeTree](#replicatedmergetree)
            * 17.2.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplicatedmergetree)
        * 17.2.3 [ReplacingMergeTree](#replacingmergetree)
            * 17.2.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplacingmergetree)
        * 17.2.4 [SummingMergeTree](#summingmergetree)
            * 17.2.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreesummingmergetree)
        * 17.2.5 [AggregatingMergeTree](#aggregatingmergetree)
            * 17.2.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeaggregatingmergetree)
        * 17.2.6 [CollapsingMergeTree](#collapsingmergetree)
            * 17.2.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreecollapsingmergetree)
        * 17.2.7 [VersionedCollapsingMergeTree](#versionedcollapsingmergetree)
            * 17.2.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeversionedcollapsingmergetree)
        * 17.2.8 [GraphiteMergeTree](#graphitemergetree)
            * 17.2.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreegraphitemergetree)
    * 17.3 [Integration Engines](#integration-engines)
        * 17.3.1 [ODBC Engine](#odbc-engine)
            * 17.3.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquettableenginesintegrationodbc)
        * 17.3.2 [JDBC Engine](#jdbc-engine)
            * 17.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquettableenginesintegrationjdbc)
        * 17.3.3 [MySQL Engine](#mysql-engine)
            * 17.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquettableenginesintegrationmysql)
        * 17.3.4 [MongoDB Engine](#mongodb-engine)
            * 17.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquettableenginesintegrationmongodb)
        * 17.3.5 [HDFS Engine](#hdfs-engine)
            * 17.3.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquettableenginesintegrationhdfs)
        * 17.3.6 [S3 Engine](#s3-engine)
            * 17.3.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3](#rqsrs-032clickhouseparquettableenginesintegrations3)
        * 17.3.7 [Kafka Engine](#kafka-engine)
            * 17.3.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquettableenginesintegrationkafka)
        * 17.3.8 [EmbeddedRocksDB Engine](#embeddedrocksdb-engine)
            * 17.3.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquettableenginesintegrationembeddedrocksdb)
        * 17.3.9 [PostgreSQL Engine](#postgresql-engine)
            * 17.3.9.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquettableenginesintegrationpostgresql)
    * 17.4 [Special Engines](#special-engines)
        * 17.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory](#rqsrs-032clickhouseparquettableenginesspecialmemory)
        * 17.4.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquettableenginesspecialdistributed)
        * 17.4.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquettableenginesspecialdictionary)
        * 17.4.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File](#rqsrs-032clickhouseparquettableenginesspecialfile)
        * 17.4.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL](#rqsrs-032clickhouseparquettableenginesspecialurl)
* 18 [Indexes](#indexes)
    * 18.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes](#rqsrs-032clickhouseparquetindexes)
    * 18.2 [Page](#page)
        * 18.2.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.Page](#rqsrs-032clickhouseparquetindexespage)
    * 18.3 [Bloom Filter](#bloom-filter)
        * 18.3.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter](#rqsrs-032clickhouseparquetindexesbloomfilter)
        * 18.3.2 [Parquet Column Types Support](#parquet-column-types-support)
            * 18.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes](#rqsrs-032clickhouseparquetindexesbloomfiltercolumntypes)
        * 18.3.3 [Supported Operators](#supported-operators)
            * 18.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.Operators](#rqsrs-032clickhouseparquetindexesbloomfilteroperators)
            * 18.3.3.2 [Only Considering Parquet Structure When Using Key Column Types](#only-considering-parquet-structure-when-using-key-column-types)
                * 18.3.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.KeyColumnTypes](#rqsrs-032clickhouseparquetindexesbloomfiltercolumntypesignorekeycolumntypes)
            * 18.3.3.3 [Only Considering Parquet Structure When Using Field Types](#only-considering-parquet-structure-when-using-field-types)
                * 18.3.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.FieldTypes](#rqsrs-032clickhouseparquetindexesbloomfiltercolumntypesignorefieldtypes)
        * 18.3.4 [Columns With Complex Datatypes That Have Bloom Filter Applied on Them](#columns-with-complex-datatypes-that-have-bloom-filter-applied-on-them)
            * 18.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.DataTypes.Complex](#rqsrs-032clickhouseparquetindexesbloomfilterdatatypescomplex)
        * 18.3.5 [Consistent Output When Using Key Column Types](#consistent-output-when-using-key-column-types)
            * 18.3.5.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.KeyColumnTypes](#rqsrs-032clickhouseparquetindexesbloomfilterconsistentoutputkeycolumntypes)
        * 18.3.6 [Consistent Output When Using Field Types](#consistent-output-when-using-field-types)
            * 18.3.6.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.FieldTypes](#rqsrs-032clickhouseparquetindexesbloomfilterconsistentoutputfieldtypes)
    * 18.4 [Dictionary](#dictionary)
        * 18.4.1 [RQ.SRS-032.ClickHouse.Parquet.Indexes.Dictionary](#rqsrs-032clickhouseparquetindexesdictionary)
* 19 [Metadata](#metadata)
    * 19.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata](#rqsrs-032clickhouseparquetmetadata)
    * 19.2 [ParquetFormat](#parquetformat)
        * 19.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat](#rqsrs-032clickhouseparquetmetadataparquetmetadataformat)
        * 19.2.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output](#rqsrs-032clickhouseparquetmetadataparquetmetadataformatoutput)
        * 19.2.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content](#rqsrs-032clickhouseparquetmetadataparquetmetadatacontent)
        * 19.2.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax](#rqsrs-032clickhouseparquetmetadataparquetmetadataminmax)
    * 19.3 [Extra Entries in Metadata](#extra-entries-in-metadata)
        * 19.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.ExtraEntries](#rqsrs-032clickhouseparquetmetadataparquetmetadataextraentries)
    * 19.4 [Metadata Types](#metadata-types)
        * 19.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.File](#rqsrs-032clickhouseparquetmetadatafile)
        * 19.4.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Column](#rqsrs-032clickhouseparquetmetadatacolumn)
        * 19.4.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Header](#rqsrs-032clickhouseparquetmetadataheader)
    * 19.5 [Cache for ListObjects ](#cache-for-listobjects-)
        * 19.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects](#rqsrs-032clickhouseparquetmetadatacachelistobjects)
        * 19.5.2 [Settings for Caching ListObjects](#settings-for-caching-listobjects)
            * 19.5.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.Settings](#rqsrs-032clickhouseparquetmetadatacachelistobjectssettings)
        * 19.5.3 [Caching ListObjects When the Same Bucket Exists in Different Storage Providers](#caching-listobjects-when-the-same-bucket-exists-in-different-storage-providers)
            * 19.5.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.SameBucket](#rqsrs-032clickhouseparquetmetadatacachelistobjectssamebucket)
        * 19.5.4 [Caching User Credentials](#caching-user-credentials)
            * 19.5.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.UserCredentials](#rqsrs-032clickhouseparquetmetadatacachelistobjectsusercredentials)
    * 19.6 [Caching for Object Storage](#caching-for-object-storage)
        * 19.6.1 [Test Schema For Metadata Caching](#test-schema-for-metadata-caching)
        * 19.6.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage](#rqsrs-032clickhouseparquetmetadatacachingobjectstorage)
        * 19.6.3 [Setting Propagation to All Nodes](#setting-propagation-to-all-nodes)
            * 19.6.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragesettingpropagation)
            * 19.6.3.2 [Propagate Settings to All Nodes When Set in the Profile (All Nodes)](#propagate-settings-to-all-nodes-when-set-in-the-profile-all-nodes)
                * 19.6.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragesettingpropagationprofilesettings)
            * 19.6.3.3 [Propagate Settings to All Nodes When Set in the Profile (Initiator Node Only)](#propagate-settings-to-all-nodes-when-set-in-the-profile-initiator-node-only)
                * 19.6.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings.InitiatorNode](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragesettingpropagationprofilesettingsinitiatornode)
        * 19.6.4 [Cache Eviction](#cache-eviction)
            * 19.6.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheEviction](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragecacheeviction)
        * 19.6.5 [Swarm](#swarm)
            * 19.6.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageswarm)
            * 19.6.5.2 [Read With Swarm From S3Cluster](#read-with-swarm-from-s3cluster)
                * 19.6.5.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.ReadWithS3Cluster](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageswarmreadwiths3cluster)
            * 19.6.5.3 [Swarm Node Stops During Query Execution](#swarm-node-stops-during-query-execution)
                * 19.6.5.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.NodeStops](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageswarmnodestops)
        * 19.6.6 [Object Storages](#object-storages)
            * 19.6.6.1 [S3 Storage](#s3-storage)
                * 19.6.6.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.S3](#rqsrs-032clickhouseparquetmetadatacachingobjectstorages3)
            * 19.6.6.2 [Azure](#azure)
                * 19.6.6.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Azure](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageazure)
            * 19.6.6.3 [Google Cloud Storage](#google-cloud-storage)
                * 19.6.6.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.GoogleCloudStorage](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragegooglecloudstorage)
            * 19.6.6.4 [MinIO](#minio)
                * 19.6.6.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MinIO](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageminio)
            * 19.6.6.5 [HDFS Storage](#hdfs-storage)
                * 19.6.6.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HDFS](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragehdfs)
            * 19.6.6.6 [Wasabi](#wasabi)
                * 19.6.6.6.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Wasabi](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragewasabi)
            * 19.6.6.7 [DigitalOcean Spaces](#digitalocean-spaces)
                * 19.6.6.7.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.DigitalOceanSpaces](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragedigitaloceanspaces)
            * 19.6.6.8 [Ceph RADOS Gateway](#ceph-rados-gateway)
                * 19.6.6.8.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CephRADOSGateway](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragecephradosgateway)
            * 19.6.6.9 [Yandex Cloud Object Storage](#yandex-cloud-object-storage)
                * 19.6.6.9.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.YandexCloudObjectStorage](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageyandexcloudobjectstorage)
            * 19.6.6.10 [Cloudflare R2](#cloudflare-r2)
                * 19.6.6.10.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CloudflareR2](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragecloudflarer2)
            * 19.6.6.11 [Alibaba Cloud OSS](#alibaba-cloud-oss)
                * 19.6.6.11.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AlibabaCloudOSS](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragealibabacloudoss)
        * 19.6.7 [All Functions and Engines That Can Store Parquet ](#all-functions-and-engines-that-can-store-parquet-)
            * 19.6.7.1 [S3 Engine or Function](#s3-engine-or-function)
                * 19.6.7.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionss3)
            * 19.6.7.2 [S3Cluster](#s3cluster)
                * 19.6.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3Cluster](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionss3cluster)
            * 19.6.7.3 [IcebergS3 Engine or Function](#icebergs3-engine-or-function)
                * 19.6.7.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.IcebergS3](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionsicebergs3)
            * 19.6.7.4 [URL Engine or Function](#url-engine-or-function)
                * 19.6.7.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.URL](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionsurl)
            * 19.6.7.5 [File Engine or Function](#file-engine-or-function)
                * 19.6.7.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.File](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionsfile)
            * 19.6.7.6 [HDFS Engine or Function](#hdfs-engine-or-function)
                * 19.6.7.6.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.HDFS](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageenginesandfunctionshdfs)
        * 19.6.8 [Trying To Cache Metadata When Using Engines Not Suited for Direct Parquet Storage](#trying-to-cache-metadata-when-using-engines-not-suited-for-direct-parquet-storage)
            * 19.6.8.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NotSuitedEngines](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenotsuitedengines)
        * 19.6.9 [Cache Invalidation](#cache-invalidation)
            * 19.6.9.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Invalidation](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageinvalidation)
        * 19.6.10 [Cache Clearing](#cache-clearing)
            * 19.6.10.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragecacheclearing)
            * 19.6.10.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing,OnCluster](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragecacheclearingoncluster)
        * 19.6.11 [Reading Metadata After Caching Is Completed](#reading-metadata-after-caching-is-completed)
            * 19.6.11.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.ReadMetadataAfterCaching](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragereadmetadataaftercaching)
        * 19.6.12 [Caching When Reading From Hive Partitioned Parquet Files in Object Storage](#caching-when-reading-from-hive-partitioned-parquet-files-in-object-storage)
            * 19.6.12.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HivePartitioning](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragehivepartitioning)
        * 19.6.13 [Caching Settings](#caching-settings)
            * 19.6.13.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Settings](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragesettings)
        * 19.6.14 [All Possible Settings That Can Be Used Along With Metadata Caching Settings](#all-possible-settings-that-can-be-used-along-with-metadata-caching-settings)
            * 19.6.14.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AllSettings](#rqsrs-032clickhouseparquetmetadatacachingobjectstorageallsettings)
        * 19.6.15 [Cases When Metadata Cache Speeds Up Query Execution](#cases-when-metadata-cache-speeds-up-query-execution)
            * 19.6.15.1 [Count](#count)
                * 19.6.15.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.Count](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragespeedupqueryexecutioncount)
            * 19.6.15.2 [Min and Max](#min-and-max)
                * 19.6.15.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.MinMax](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragespeedupqueryexecutionminmax)
            * 19.6.15.3 [Bloom Filter Caching](#bloom-filter-caching)
                * 19.6.15.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.BloomFilter](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragespeedupqueryexecutionbloomfilter)
            * 19.6.15.4 [Distinct Count](#distinct-count)
                * 19.6.15.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.DistinctCount](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragespeedupqueryexecutiondistinctcount)
            * 19.6.15.5 [File Schema](#file-schema)
                * 19.6.15.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.FileSchema](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragespeedupqueryexecutionfileschema)
        * 19.6.16 [Maximum Size of Metadata Cache](#maximum-size-of-metadata-cache)
            * 19.6.16.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MaxSize](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragemaxsize)
        * 19.6.17 [File With The Same Name But Different Location](#file-with-the-same-name-but-different-location)
            * 19.6.17.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SameNameDifferentLocation](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragesamenamedifferentlocation)
        * 19.6.18 [Hits and Misses Counter](#hits-and-misses-counter)
            * 19.6.18.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HitsMissesCounter](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragehitsmissescounter)
        * 19.6.19 [Nested Queries With Metadata Caching](#nested-queries-with-metadata-caching)
            * 19.6.19.1 [Join Two Parquet Files From an Object Storage](#join-two-parquet-files-from-an-object-storage)
                * 19.6.19.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Join](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesjoin)
            * 19.6.19.2 [Basic Nested Subquery](#basic-nested-subquery)
                * 19.6.19.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Basic](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesbasic)
            * 19.6.19.3 [Union All with Nested Parquet Queries](#union-all-with-nested-parquet-queries)
                * 19.6.19.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionAll](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesunionall)
            * 19.6.19.4 [Nested Subquery with an Additional Filter and Aggregation](#nested-subquery-with-an-additional-filter-and-aggregation)
                * 19.6.19.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.FilterAggregation](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesfilteraggregation)
            * 19.6.19.5 [Combining a UNION with a JOIN](#combining-a-union-with-a-join)
                * 19.6.19.5.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionJoin](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesunionjoin)
            * 19.6.19.6 [Deeply Nested JOIN](#deeply-nested-join)
                * 19.6.19.6.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.DeeplyNestedJoin](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragenestedqueriesdeeplynestedjoin)
    * 19.7 [Cachable Metadata Types](#cachable-metadata-types)
        * 19.7.1 [Metadata Generated by ClickHouse](#metadata-generated-by-clickhouse)
            * 19.7.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ClickHouse](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragemetadatatypesclickhouse)
        * 19.7.2 [Metadata Generated by Parquetify](#metadata-generated-by-parquetify)
            * 19.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.Parquetify](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragemetadatatypesparquetify)
        * 19.7.3 [Metadata Generated by DuckDB](#metadata-generated-by-duckdb)
            * 19.7.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.DuckDB](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragemetadatatypesduckdb)
        * 19.7.4 [Metadata Generated by Apache Arrow](#metadata-generated-by-apache-arrow)
            * 19.7.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ApacheArrow](#rqsrs-032clickhouseparquetmetadatacachingobjectstoragemetadatatypesapachearrow)
* 20 [Error Recovery](#error-recovery)
    * 20.1 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.MagicNumber](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatamagicnumber)
    * 20.2 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.File](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatafile)
    * 20.3 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Column](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatacolumn)
    * 20.4 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageHeader](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatapageheader)
    * 20.5 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageData](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatapagedata)
    * 20.6 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Checksum](#rqsrs-032clickhouseparqueterrorrecoverycorruptmetadatachecksum)
    * 20.7 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values](#rqsrs-032clickhouseparqueterrorrecoverycorruptvalues)
        * 20.7.1 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Date](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesdate)
        * 20.7.2 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Int](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesint)
        * 20.7.3 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.BigInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesbigint)
        * 20.7.4 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.SmallInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluessmallint)
        * 20.7.5 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TinyInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestinyint)
        * 20.7.6 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesuint)
        * 20.7.7 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UBigInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesubigint)
        * 20.7.8 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.USmallInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesusmallint)
        * 20.7.9 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UTinyInt](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesutinyint)
        * 20.7.10 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampUS](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestimestampus)
        * 20.7.11 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampMS](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestimestampms)
        * 20.7.12 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Bool](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesbool)
        * 20.7.13 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Float](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesfloat)
        * 20.7.14 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Double](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesdouble)
        * 20.7.15 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeMS](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestimems)
        * 20.7.16 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeUS](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestimeus)
        * 20.7.17 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeNS](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluestimens)
        * 20.7.18 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.String](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesstring)
        * 20.7.19 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Binary](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesbinary)
        * 20.7.20 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.FixedLengthByteArray](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesfixedlengthbytearray)
        * 20.7.21 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Decimal](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesdecimal)
        * 20.7.22 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.List](#rqsrs-032clickhouseparqueterrorrecoverycorruptvalueslist)
        * 20.7.23 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Struct](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesstruct)
        * 20.7.24 [RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Map](#rqsrs-032clickhouseparqueterrorrecoverycorruptvaluesmap)
* 21 [Interoperability Between ARM and x86](#interoperability-between-arm-and-x86)
    * 21.1 [Importing and Exporting Parquet Files On ARM That Were Generated On x86 Machine](#importing-and-exporting-parquet-files-on-arm-that-were-generated-on-x86-machine)
        * 21.1.1 [RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.x86.To.ARM](#rqsrs-032clickhouseparquetinteroperabilityfromx86toarm)
    * 21.2 [Importing and Exporting Parquet Files On x86 That Were Generated On ARM Machine](#importing-and-exporting-parquet-files-on-x86-that-were-generated-on-arm-machine)
        * 21.2.1 [RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.ARM.To.x86](#rqsrs-032clickhouseparquetinteroperabilityfromarmtox86)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `Parquet` data format in [ClickHouse].

The documentation used:
- https://clickhouse.com/docs/en/operations/settings/formats#parquet-format-settings
- https://clickhouse.com/docs/en/interfaces/formats#data-format-parquet
- https://clickhouse.com/docs/en/integrations/data-formats/parquet#importing-from-parquet
- https://parquet.apache.org/docs/

## Test Schema

```yaml
Parquet:
    Services:
      - Parquet File Format
      - ClickHouse Reading Parquet
      - ClickHouse Writing Parquet
    ParquetFileFormat:
      File:
        MagicNumber: "PAR1 (4 bytes)"
        Metadata:
          - version
          - schema:
              - type
              - type_length
              - repetition_type
              - name
              - num_children
              - converted_type
          - num_rows
          - row_groups
          - key_value_metadata:
                - key
                - value
        Datatypes:
          Physical:
            - BOOLEAN
            - INT32
            - INT64
            - INT96
            - FLOAT (IEEE 32-bit)
            - DOUBLE (IEEE 64-bit)
            - BYTE_ARRAY
            - FIXED_LEN_BYTE_ARRAY
          Logical:
            - STRING
            - ENUM
            - UUID
            - DOUBLE
            - UINT_8
            - UINT_16
            - UINT_32
            - UINT_64
            - INT_8
            - INT_16
            - INT_32
            - INT_64
            - MAP
            - LIST
            - DECIMAL (INT32)
            - DECIMAL (INT64)
            - DECIMAL (FIXED_LEN_BYTE_ARRAY)
            - DECIMAL (BYTE_ARRAY)
            - DATE
            - TIME
            - TIME_MILLIS
            - TIME_MICROS
            - TIMESTAMP
            - TIMESTAMP_MILLIS
            - TIMESTAMP_MICROS
            - INTERVAL
            - JSON
            - BSON
            - FLOAT16
            - UNKNOWN (always null)
        Compression:
            - UNCOMPRESSED
            - BROTLI
            - GZIP
            - LZ4 (deprecated)	
            - LZ4_RAW
            - LZO
            - SNAPPY
            - ZSTD
        Encodings:
            - PLAIN
            - PLAIN_DICTIONARY
            - RLE_DICTIONARY
            - RLE
            - BIT_PACKED (deprecated)	
            - DELTA_BINARY_PACKED
            - DELTA_LENGTH_BYTE_ARRAY
            - DELTA_BYTE_ARRAY
            - BYTE_STREAM_SPLIT
        Encryption:
            - AES_GCM_V1
            - AES_GCM_CTR_V1
        IfCorrupted:
          - The file is lost
      RowGroup:
        Metadata:
            - num_columns
            - num_rows
            - total_uncompressed_size
            - total_compressed_size
            - columns (the list of column chunks metadata with the next structure)
        IfCorrupted:
            - Only that row group is lost
      ColumnChunk:
        Metadata:
          - file_path
          - file_offset
          - column_metadata:
              - type
              - encodings
              - path_in_schema
              - codec
              - num_values
              - total_uncompressed_size
              - total_compressed_size
              - key_value_metadata:
                  - key
                  - value
              - data_page_offset
              - index_page_offset
              - dictionary_page_offset
        IfCorrupted:
          - Only that column chunk is lost (but column chunks for this column in other row groups are okay)
      PageHeader:
        Metadata:
            - type
            - uncompressed_page_size
            - compressed_page_size
            - crc
            - data_page_header:
                - num_values
                - encoding
                - definition_level_encoding
                - repetition_level_encoding
            - index_page_header
            - dictionary_page_header:
                - num_values
        IfCorrupted:
          - The remaining pages in that chunk are lost.
          - If the data within a page is corrupt, that page is lost
      FormatLevelFeatures:
        - xxxHash-based bloom filters
        - Bloom filter length
        - Statistics min_value, max_value
        - Page index
        - Page CRC32 checksum
        - Modular encryption
        - Size statistics 

    ClickHouseRead:
        functions:
          - file()
          - url() 
          - s3()
          - remote()
    
    ClickHouseWrite:
      - SELECT * FROM sometable INTO OUTFILE 'export.parquet' FORMAT Parquet

```

## Feature Diagram

```mermaid
flowchart TB;
    subgraph Overhead[Parquet]
        direction TB;
        subgraph Sources[Source of data]
            direction TB;   
            MySQL
            DuckDB

            subgraph Libraries[Parquet Libraries]
                direction LR;
                parquet-tools
                pyarrow
                parquet-cpp
                parquet-mr
                fastparquet
                pyspark
            end

            subgraph ClickHouse_source[ClickHouse]
                style ClickHouse_source fill:#fcbb30
                direction TB;   
                subgraph Select_query[SELECT]
                    style Select_query fill:#d9ead3
                    direction LR;
                    subgraph Select_sources[Sources]
                        direction TB;
                        subgraph Funcs_sel[Functions]
                            direction LR;
                            URL_func_sel[URL]
                            File_func_sel[FILE]
                            Query_func_sel[Query]
                            S3_func_sel[S3]
                            jdbc_func_sel[JDBC]
                            odbc_func_sel[ODBC]
                            hdfs_func_sel[HDFS]
                            remote_func_sel[Remote]
                            mysql_func_sel[MySQL]
                            postgresql_func_sel[PostgreSQL]
                        end

                        subgraph Integration_Engines_sel[Integration Engines]
                            direction LR;
                            ODBC_eng_sel[ODBC]
                            jdbc_eng_sel[JDBC]
                            mysql_eng_sel[MySQL]
                            mongodb_eng_sel[MongoDB]
                            hdfs_eng_sel[HDFS]
                            s3_eng_sel[S3]
                            kafka_eng_sel[Kafka]
                            embeddedrocksDB_eng_sel[EmbeddedRocksDB]
                            RabbitMQ_eng_sel[RabbitMQ]
                            PostgreSQL_eng_sel[PostgreSQL]
                        end

                        subgraph Special_Engines_sel[Special Engines]
                            direction LR;
                            distributed_eng_sel[Distributed]
                            dictionary_eng_sel[Dictionary]
                            file_eng_sel[File]
                            url_eng_sel[URL]
                            mat_view_sel[Materialized View]
                            merge_sel[Merge]
                            join_sel[Join]
                            view_sel[View]
                            memory_sel[Memory]
                            buffer_sel[Buffer]
                        end
                    end

                    subgraph Select_opt[Clauses]
                        JOIN_clause[JOIN]
                        Union_clause[UNION]
                    end
                end

                subgraph ClickHouse_write_direct[Writing into file directly]
                    direction LR;
                    s3_tb_write[S3 table function]
                    s3_en_write[S3 engine]
                    file_tb_write[File table function]
                    file_en_write[File engine]
                    hdfs_tb_write[HDFS table function]
                    hdfs_en_write[HDFS engine]
                    url_tb_write[URL table function]
                    url_en_write[URL engine]
                end
            end
        end

        subgraph Input_settings[Input settings]
            direction LR
            input_format_parquet_import_nested
            input_format_parquet_case_insensitive_column_matching
            input_format_parquet_allow_missing_columns
            input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference 
        end

        subgraph Output_settings[Output settings]
            direction LR
            output_format_parquet_row_group_size
            output_format_parquet_string_as_string
            output_format_parquet_fixed_string_as_fixed_byte_array
            output_format_parquet_version
            output_format_parquet_compression_method
        end

        subgraph Compression
            direction TB
            Uncompressed
            Snappy
            Gzip
            LZO
            Brotli
            LZ4
            ZSTD
            LZ4_RAW
        end

        subgraph Encryption
            direction LR
            AesGcmV1
            AesGcmCtrV1
        end

        subgraph Corrupted
            direction LR
            CorruptedYes[Yes]
            CorruptedNo[No]
        end

        subgraph Possible_Corruptions[Possible Corruptions]
            direction LR
            CorruptFile[Corrupt File]
            CorruptColumn[Corrupted Column]
            CorruptPageHeader[Corrupt Page Header]
            CorruptPageData[Corrupted Page Data]
            CorruptColumnValues[Corrupted Column Values]
        end

        subgraph Error
            direction LR
            Error_message[File is not inserted into ClickHouse. Error Message Is Shown.]
        end

        subgraph ClickHouse[ClickHouse]
            style ClickHouse fill:#fcbb30
            direction TB;
            subgraph Insert_query[INSERT Targets]
                style Insert_query fill:#ffb5b5
                direction TB;
                subgraph Funcs[Functions]
                    URL_func_in[URL]
                    File_func_in[FILE]
                    Query_func_in[Query]
                    S3_func_in[S3]
                    jdbc_func_in[JDBC]
                    odbc_func_in[ODBC]
                    hdfs_func_in[HDFS]
                    remote_func_in[Remote]
                    mysql_func_in[MySQL]
                    postgresql_func_in[PostgreSQL]
                end

                subgraph Integration_Engines[Integration Engines]
                    ODBC_eng[ODBC]
                    jdbc_eng[JDBC]
                    mysql_eng[MySQL]
                    mongodb_eng[MongoDB]
                    hdfs_eng[HDFS]
                    s3_eng[S3]
                    kafka_eng[Kafka]
                    embeddedrocksDB_eng[EmbeddedRocksDB]
                    RabbitMQ_eng[RabbitMQ]
                    PostgreSQL_eng[PostgreSQL]
                end

                subgraph Special_Engines[Special Engines]
                    distributed_eng[Distributed]
                    dictionary_eng[Dictionary]
                    file_eng[File]
                    url_eng[URL]
                    merge[Merge]
                    join[Join]
                    memory[Memory]
                    buffer[Buffer]
                end

            end
            subgraph ClickHouse_read_direct[Reading from file directly]
                s3_tb_read[S3 table function]
                s3_en_read[S3 engine]
                file_tb_read[File table function]
                file_en_read[File engine]
                hdfs_tb_read[HDFS table function]
                hdfs_en_read[HDFS engine]
                url_tb_read[URL table function]
                url_en_read[URL engine]
            end
        end

    Parquet_File_in[Parquet File]
    Parquet_File_out[Parquet File]

        subgraph PossibleCorruptions[Possible Corrupted Parquet Datatypes]
            direction LR;
                UInt8in[UInt8]
                Boolin[Bool]
                Int8in[Int8]
                UInt16in[UInt16]
                Int16in[Int16]
                UInt32in[UInt32]
                Int32in[Int32]
                UInt64in[UInt64]
                Int64in[Int64]
                Floatin[Float]
                HalfFloatin[Half Float]
                Doublein[Double]
                Date32in[Date32]
                Date64in[Date62]
                Timestampin[Timestamp]
                Stringin[String]
                Binaryin[Binary]
                Decimalin[Decimal]
                Listin[List]
                Structin[Struct]
                Mapin[Map]
            end

        subgraph TypeConversion[Parquet type > ClickHouse type > Parquet type]
            direction LR;
            subgraph Insert_types[Parquet]
                UInt8_in[UInt8]
                Bool_in[Bool]
                Int8_in[Int8]
                UInt16_in[UInt16]
                Int16_in[Int16]
                UInt32_in[UInt32]
                Int32_in[Int32]
                UInt64_in[UInt64]
                Int64_in[Int64]
                Float_in[Float]
                Half_Float_in[Half Float]
                Double_in[Double]
                Date32_in[Date32]
                Date64_in[Date62]
                Timestamp_in[Timestamp]
                String_in[String]
                Binary_in[Binary]
                Decimal_in[Decimal]
                List_in[List]
                Struct_in[Struct]
                Map_in[Map]
            end

            subgraph CH_types[ClickHouse]
                UInt8_ch[UInt8]
                Int8_ch[Int8]
                UInt16_ch[UInt16]
                Int16_ch[Int16]
                UInt32_ch[UInt32]
                Int32_ch[Int32]
                UInt64_ch[UInt64]
                Int64_ch[Int64]
                Float32_ch[Float32]
                Float64_ch[Float64]
                Date_ch[Date]
                DateTime_ch[DateTime]
                String_ch[String]
                FixedString_ch[FixedString]
                Decimal128_ch[Decimal128]
                Array_ch[Array]
                Tuple_ch[Tuple]
                Map_ch[Map]
            end

            subgraph Select_types[Parquet]
                UInt8_out[UInt8]
                Int8_out[Int8]
                UInt16_out[UInt16]
                Int16_out[Int16]
                UInt32_out[UInt32]
                Int32_out[Int32]
                UInt64_out[UInt64]
                Int64_out[Int64]
                Float_out[Float]
                Double_out[Double]
                Binary_out[Binary]
                Decimal_out[Decimal]
                List_out[List]
                Struct_out[Struct]
                Map_out[Map]
            end

            subgraph AutoConversions[Type Auto Conversion Based On The Target Table]
                direction LR
                Parquet_type[Parquet Datatype]
                ClickHouse_type[ClickHouse Datatype]
            end

            subgraph Modifiers[Supported Modifiers]
                direction LR
                Nullable
                LowCardinality
            end
        end
        subgraph Not_supported_by_ch[Parquet Types not supported by ClickHouse]
            direction LR
            Time32
            FIXED_SIZE_BINARY
            JSON
            UUID
            ENUM
            Chunked_arr[Chunked Array]
        end
    end


Sources --> Compression --> Encryption --> Parquet_File_in 
Parquet_File_in --> CorruptedYes
CorruptedYes --> Possible_Corruptions --> Error
Parquet_File_in --> CorruptedNo --Insert Into ClickHouse --> Input_settings --> ClickHouse -- Read From ClickHouse --> Output_settings --> Parquet_File_out
CorruptColumnValues --> PossibleCorruptions
ClickHouse_type --> Parquet_type --> ClickHouse_type


UInt8_in --> UInt8_ch --> UInt8_out
Bool_in --> UInt8_ch
Int8_in --> Int8_ch --> Int8_out
UInt16_in --> UInt16_ch --> UInt16_out
UInt32_in --> UInt32_ch --> UInt32_out
UInt64_in --> UInt64_ch --> UInt64_out
Int16_in --> Int16_ch --> Int16_out
Int32_in --> Int32_ch --> Int32_out
Int64_in --> Int64_ch --> Int64_out
Float_in --> Float32_ch --> Float_out
Half_Float_in --> Float32_ch
Double_in --> Float64_ch --> Double_out
Date32_in --> Date_ch --> UInt16_out
Date64_in --> DateTime_ch --> UInt32_out
Timestamp_in --> DateTime_ch
String_in --> String_ch --> Binary_out
Binary_in --> String_ch
Decimal_in --> Decimal128_ch --> Decimal_out
List_in --> Array_ch --> List_out
Struct_in --> Tuple_ch --> Struct_out
Map_in --> Map_ch --> Map_out
FixedString_ch --> Binary_out
```

## Working With Parquet

### RQ.SRS-032.ClickHouse.Parquet
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

## Supported Parquet Versions

### RQ.SRS-032.ClickHouse.Parquet.SupportedVersions
version: 1.0

[ClickHouse] SHALL support importing Parquet files with the following versions: `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.4.0`, `2.6.0`, `2.7.0`, `2.8.0`, `2.9.0`.

### RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal
version: 1.0

[ClickHouse] SHALL support the usage of `clickhouse-local` with `Parquet` data format.

## Offsets

### RQ.SRS-032.ClickHouse.Parquet.Offsets
version: 1.0

[ClickHouse] SHALL support importing and exporting parquet files with offsets.

#### RQ.SRS-032.ClickHouse.Parquet.Offsets.MonotonicallyIncreasing
version: 1.0

[ClickHouse] SHALL support importing and exporting parquet files with monotonically increasing offsets.

## Query Cache

### RQ.SRS-032.ClickHouse.Parquet.Query.Cache
version: 1.0

[ClickHouse] SHALL support using the query cache functionality when working with the Parquet files.

## Import from Parquet Files

### RQ.SRS-032.ClickHouse.Parquet.Import
version: 1.0

[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to
read data from Parquet files and insert data into tables or table functions.

```sql
INSERT INTO sometable
FROM INFILE 'data.parquet' FORMAT Parquet;
```

### Auto Detect Parquet File When Importing

#### RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat
version: 1.0

[ClickHouse] SHALL support automatically detecting Parquet file format based on 
when using INFILE clause without explicitly specifying the format setting.

```sql
INSERT INTO sometable
FROM INFILE 'data.parquet';
```

### Glob Patterns

#### RQ.SRS-032.ClickHouse.Parquet.Import.Glob
version: 1.0

[ClickHouse] SHALL support using glob patterns in file paths to import multiple Parquet files.

> Multiple path components can have globs. For being processed file must exist and match to the whole path pattern (not only suffix or prefix).
>
>   - `*` — Substitutes any number of any characters except / including empty string.
>   - `?` — Substitutes any single character.
>   - `{some_string,another_string,yet_another_one}` — Substitutes any of strings 'some_string', 'another_string', 'yet_another_one'.
>   - `{N..M}` — Substitutes any number in range from N to M including both borders.
>   - `**` - Fetches all files inside the folder recursively.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Glob.MultiDirectory
version: 1.0

[ClickHouse] SHALL support using `{str1, ...}` globs across different directories when importing from the Parquet files. 

For example,

> The following query will import both from a/1.parquet and b/2.parquet
> 
> ```sql
> SELECT
>     *,
>     _path,
>     _file
> FROM file('{a/1,b/2}.parquet', Parquet)
> ```

### Supported Datatypes

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Conversion
version: 1.0

[ClickHouse] SHALL support importing the Parquet files with the following datatypes and converting them into corresponding ClickHouse columns as described in the table.

The conversion MAY not be possible between some datatypes.
>
> For example,
>
> `Bool` -> `IPv6`

| Parquet to ClickHouse supported Datatypes     | ClickHouse Datatype Family        | alias_to Datatype | case_insensitive |
|-----------------------------------------------|-----------------------------------|-------------------|------------------|
|                                               | `JSON`                            |                   | 1                |
|                                               | `Polygon`                         |                   | 0                |
|                                               | `Ring`                            |                   | 0                |
|                                               | `Point`                           |                   | 0                |
|                                               | `SimpleAggregateFunction`         |                   | 0                |
|                                               | `IntervalQuarter`                 |                   | 0                |
|                                               | `IntervalMonth`                   |                   | 0                |
| `INT64`                                       | `Int64`                           |                   | 0                |
|                                               | `IntervalDay`                     |                   | 0                |
|                                               | `IntervalHour`                    |                   | 0                |
| `UINT32`                                      | `IPv4`                            |                   | 0                |
|                                               | `IntervalSecond`                  |                   | 0                |
|                                               | `LowCardinality`                  |                   | 0                |
| `INT16`                                       | `Int16`                           |                   | 0                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `UInt256`                         |                   | 0                |
|                                               | `AggregateFunction`               |                   | 0                |
|                                               | `MultiPolygon`                    |                   | 0                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                            |                   | 0                |
|                                               | `Nothing`                         |                   | 0                |
|                                               | `Decimal256`                      |                   | 1                |
| `STRUCT`                                      | `Tuple`                           |                   | 0                |
| `LIST`                                        | `Array`                           |                   | 0                |
|                                               | `IntervalMicrosecond`             |                   | 0                |
|                                               | `Bool`                            |                   | 1                |
| `INT16`                                       | `Enum16`                          |                   | 0                |
|                                               | `IntervalMinute`                  |                   | 0                |
|                                               | `FixedString`                     |                   | 0                |
| `STRING`, `BINARY`                            | `String`                          |                   | 0                |
| `TIME (ms)`                                   | `DateTime`                        |                   | 1                |
|                                               | `Object`                          |                   | 0                |
| `MAP`                                         | `Map`                             |                   | 0                |
|                                               | `UUID`                            |                   | 0                |
|                                               | `Decimal64`                       |                   | 1                |
|                                               | `Nullable`                        |                   | 0                |
|                                               | `Enum`                            |                   | 1                |
| `INT32`                                       | `Int32`                           |                   | 0                |
| `UINT8`, `BOOL`                               | `UInt8`                           |                   | 0                |
|                                               | `Date`                            |                   | 1                |
|                                               | `Decimal32`                       |                   | 1                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `UInt128`                         |                   | 0                |
| `DOUBLE`                                      | `Float64`                         |                   | 0                |
|                                               | `Nested`                          |                   | 0                |
| `UINT16`                                      | `UInt16`                          |                   | 0                |
|                                               | `IntervalMillisecond`             |                   | 0                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`                          |                   | 0                |
|                                               | `Decimal128`                      |                   | 1                |
| `INT8`                                        | `Int8`                            |                   | 0                |
| `DECIMAL`                                     | `Decimal`                         |                   | 1                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int256`                          |                   | 0                |
| `TIMESTAMP (ms, ns, us)`, `TIME (us, ns)`     | `DateTime64`                      |                   | 1                |
| `INT8`                                        | `Enum8`                           |                   | 0                |
|                                               | `DateTime32`                      |                   | 1                |
| `DATE (ms, ns, us)`                           | `Date32`                          |                   | 1                |
|                                               | `IntervalWeek`                    |                   | 0                |
| `UINT64`                                      | `UInt64`                          |                   | 0                |
|                                               | `IntervalNanosecond`              |                   | 0                |
|                                               | `IntervalYear`                    |                   | 0                |
| `UINT32`                                      | `UInt32`                          |                   | 0                |
| `FLOAT`                                       | `Float32`                         |                   | 0                |
| `BOOL`                                        | `bool`                            | `Bool`            | 1                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `INET6`                           | `IPv6`            | 1                |
| `UINT32`                                      | `INET4`                           | `IPv4`            | 1                |
|                                               | `ENUM`                            | `Enum`            | 1                |
| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `BINARY`                          | `FixedString`     | 1                |
| `STRING`, `BINARY`                            | `GEOMETRY`                        | `String`          | 1                |
| `STRING`, `BINARY`                            | `NATIONAL CHAR VARYING`           | `String`          | 1                |
| `STRING`, `BINARY`                            | `BINARY VARYING`                  | `String`          | 1                |
| `STRING`, `BINARY`                            | `NCHAR LARGE OBJECT`              | `String`          | 1                |
| `STRING`, `BINARY`                            | `NATIONAL CHARACTER VARYING`      | `String`          | 1                |
|                                               | `boolean`                         | `Bool`            | 1                |
| `STRING`, `BINARY`                            | `NATIONAL CHARACTER LARGE OBJECT` | `String`          | 1                |
| `STRING`, `BINARY`                            | `NATIONAL CHARACTER`              | `String`          | 1                |
| `STRING`, `BINARY`                            | `NATIONAL CHAR`                   | `String`          | 1                |
| `STRING`, `BINARY`                            | `CHARACTER VARYING`               | `String`          | 1                |
| `STRING`, `BINARY`                            | `LONGBLOB`                        | `String`          | 1                |
| `STRING`, `BINARY`                            | `TINYBLOB`                        | `String`          | 1                |
| `STRING`, `BINARY`                            | `MEDIUMTEXT`                      | `String`          | 1                |
| `STRING`, `BINARY`                            | `TEXT`                            | `String`          | 1                |
| `STRING`, `BINARY`                            | `VARCHAR2`                        | `String`          | 1                |
| `STRING`, `BINARY`                            | `CHARACTER LARGE OBJECT`          | `String`          | 1                |
| `DOUBLE`                                      | `DOUBLE PRECISION`                | `Float64`         | 1                |
| `STRING`, `BINARY`                            | `LONGTEXT`                        | `String`          | 1                |
| `STRING`, `BINARY`                            | `NVARCHAR`                        | `String`          | 1                |
|                                               | `INT1 UNSIGNED`                   | `UInt8`           | 1                |
| `STRING`, `BINARY`                            | `VARCHAR`                         | `String`          | 1                |
| `STRING`, `BINARY`                            | `CHAR VARYING`                    | `String`          | 1                |
| `STRING`, `BINARY`                            | `MEDIUMBLOB`                      | `String`          | 1                |
| `STRING`, `BINARY`                            | `NCHAR`                           | `String`          | 1                |
| `STRING`, `BINARY`                            | `VARBINARY`                       | `String`          | 1                |
| `STRING`, `BINARY`                            | `CHAR`                            | `String`          | 1                |
| `UINT16`                                      | `SMALLINT UNSIGNED`               | `UInt16`          | 1                |
| `TIME (ms)`                                   | `TIMESTAMP`                       | `DateTime`        | 1                |
| `DECIMAL`                                     | `FIXED`                           | `Decimal`         | 1                |
| `STRING`, `BINARY`                            | `TINYTEXT`                        | `String`          | 1                |
| `DECIMAL`                                     | `NUMERIC`                         | `Decimal`         | 1                |
| `DECIMAL`                                     | `DEC`                             | `Decimal`         | 1                |
| `INT64`                                       | `TIME`                            | `Int64`           | 1                |
| `FLOAT`                                       | `FLOAT`                           | `Float32`         | 1                |
| `UINT64`                                      | `SET`                             | `UInt64`          | 1                |
|                                               | `TINYINT UNSIGNED`                | `UInt8`           | 1                |
| `UINT32`                                      | `INTEGER UNSIGNED`                | `UInt32`          | 1                |
| `UINT32`                                      | `INT UNSIGNED`                    | `UInt32`          | 1                |
| `STRING`, `BINARY`                            | `CLOB`                            | `String`          | 1                |
| `UINT32`                                      | `MEDIUMINT UNSIGNED`              | `UInt32`          | 1                |
| `STRING`, `BINARY`                            | `BLOB`                            | `String`          | 1                |
| `FLOAT`                                       | `REAL`                            | `Float32`         | 1                |
|                                               | `SMALLINT`                        | `Int16`           | 1                |
| `INT32`                                       | `INTEGER SIGNED`                  | `Int32`           | 1                |
| `STRING`, `BINARY`                            | `NCHAR VARYING`                   | `String`          | 1                |
| `INT32`                                       | `INT SIGNED`                      | `Int32`           | 1                |
|                                               | `TINYINT SIGNED`                  | `Int8`            | 1                |
| `INT64`                                       | `BIGINT SIGNED`                   | `Int64`           | 1                |
| `STRING`, `BINARY`                            | `BINARY LARGE OBJECT`             | `String`          | 1                |
|                                               | `SMALLINT SIGNED`                 | `Int16`           | 1                |
|                                               | `YEAR`                            | `UInt16`          | 1                |
| `INT32`                                       | `MEDIUMINT`                       | `Int32`           | 1                |
| `INT32`                                       | `INTEGER`                         | `Int32`           | 1                |
|                                               | `INT1 SIGNED`                     | `Int8`            | 1                |
| `UINT64`                                      | `BIT`                             | `UInt64`          | 1                |
| `UINT64`                                      | `BIGINT UNSIGNED`                 | `UInt64`          | 1                |
| `STRING`, `BINARY`                            | `BYTEA`                           | `String`          | 1                |
| `INT32`                                       | `INT`                             | `Int32`           | 1                |
| `FLOAT`                                       | `SINGLE`                          | `Float32`         | 1                |
| `INT32`                                       | `MEDIUMINT SIGNED`                | `Int32`           | 1                |
| `DOUBLE`                                      | `DOUBLE`                          | `Float64`         | 1                |
|                                               | `INT1`                            | `Int8`            | 1                |
| `STRING`, `BINARY`                            | `CHAR LARGE OBJECT`               | `String`          | 1                |
|                                               | `TINYINT`                         | `Int8`            | 1                |
| `INT64`                                       | `BIGINT`                          | `Int64`           | 1                |
| `STRING`, `BINARY`                            | `CHARACTER`                       | `String`          | 1                |
|                                               | `BYTE`                            | `Int8`            | 1                |


#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported
version:1.0

[ClickHouse] SHALL support importing the following Parquet data types:

| Parquet data type                             | ClickHouse data type                  |
|-----------------------------------------------|---------------------------------------|
| `BOOL`                                        | `Bool`                                |
| `UINT8`, `BOOL`                               | `UInt8`                               |
| `INT8`                                        | `Int8`/`Enum8`                        |
| `UINT16`                                      | `UInt16`                              |
| `INT16`                                       | `Int16`/`Enum16`                      |
| `UINT32`                                      | `UInt32`                              |
| `INT32`                                       | `Int32`                               |
| `UINT64`                                      | `UInt64`                              |
| `INT64`                                       | `Int64`                               |
| `FLOAT`                                       | `Float32`                             |
| `DOUBLE`                                      | `Float64`                             |
| `DATE (ms, ns, us)`                           | `Date32`                              |
| `TIME (ms)`                                   | `DateTime`                            |
| `TIMESTAMP (ms, ns, us)`, `TIME (us, ns)`     | `DateTime64`                          |
| `STRING`, `BINARY`                            | `String`                              |
| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `FixedString`                         |
| `DECIMAL`                                     | `Decimal`                             |
| `LIST`                                        | `Array`                               |
| `STRUCT`                                      | `Tuple`                               |
| `MAP`                                         | `Map`                                 |
| `UINT32`                                      | `IPv4`                                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`/`UInt128`/`Int256`/`UInt256` |

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BLOB
version:1.0

[ClickHouse] SHALL support importing parquet files with `BLOB` content.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BOOL
version:1.0

[ClickHouse] SHALL support importing `BOOL` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT8
version:1.0

[ClickHouse] SHALL support importing `UINT8` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT8
version:1.0

[ClickHouse] SHALL support importing `INT8` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT16
version:1.0

[ClickHouse] SHALL support importing `UINT16` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT16
version:1.0

[ClickHouse] SHALL support importing `INT16` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT32
version:1.0

[ClickHouse] SHALL support importing `UINT32` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT32
version:1.0

[ClickHouse] SHALL support importing `INT32` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.UINT64
version:1.0

[ClickHouse] SHALL support importing `UINT64` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.INT64
version:1.0

[ClickHouse] SHALL support importing `INT64` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FLOAT
version:1.0

[ClickHouse] SHALL support importing `FLOAT` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DOUBLE
version:1.0

[ClickHouse] SHALL support importing `DOUBLE` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE
version:1.0

[ClickHouse] SHALL support importing `DATE` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ms
version:1.0

[ClickHouse] SHALL support importing `DATE (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.ns
version:1.0

[ClickHouse] SHALL support importing `DATE (ns)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DATE.us
version:1.0

[ClickHouse] SHALL support importing `DATE (us)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIME.ms
version:1.0

[ClickHouse] SHALL support importing `TIME (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ms
version:1.0

[ClickHouse] SHALL support importing `TIMESTAMP (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.ns
version:1.0

[ClickHouse] SHALL support importing `TIMESTAMP (ns)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.TIMESTAMP.us
version:1.0

[ClickHouse] SHALL support importing `TIMESTAMP (us)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRING
version:1.0

[ClickHouse] SHALL support importing `STRING` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.BINARY
version:1.0

[ClickHouse] SHALL support importing `BINARY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray
version:1.0

[ClickHouse] SHALL support importing `FIXED_LENGTH_BYTE_ARRAY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.FixedLengthByteArray.FLOAT16
version:1.0

[ClickHouse] SHALL support importing Parquet files with the `FIXED_LENGTH_BYTE_ARRAY` primitive
type and the `FLOAT16` logical type.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL
version:1.0

[ClickHouse] SHALL support importing `DECIMAL` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.DECIMAL.Filter
version:1.0

[ClickHouse] SHALL support importing `DECIMAL` Parquet datatype with specified filters.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.LIST
version:1.0

[ClickHouse] SHALL support importing `LIST` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.ARRAY
version:1.0

[ClickHouse] SHALL support importing `ARRAY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.STRUCT
version:1.0

[ClickHouse] SHALL support importing `STRUCT` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Supported.MAP
version:1.0

[ClickHouse] SHALL support importing `MAP` Parquet datatype.

#### UTCAdjusted

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.DateUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `DATE` Parquet datatype with `isAdjustedToUTC = true`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimestampUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `TIMESTAMP` Parquet datatype with `isAdjustedToUTC = true`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.TimeUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `TIME` Parquet datatype with `isAdjustedToUTC = true`.

#### Nullable

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.NullValues
version:1.0

[ClickHouse] SHALL support importing columns that have `Null` values in Parquet files. If the target [ClickHouse] column is not `Nullable` then the `Null` value should be converted to the default values for the target column datatype.

For example, if the target column has `Int32`, then the `Null` value will be replaced with `0`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nullable
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `Nullable` datatype columns.

#### LowCardinality

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.LowCardinality
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `LowCardinality` datatype columns.

#### Nested

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Nested
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `Nested` datatype columns.

#### UNKNOWN

##### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.ImportInto.Unknown
version:1.0

[ClickHouse] SHALL support importing Parquet files with `UNKNOWN` logical type.

The example as to why the Parquet might have an `UNKNOWN` types is as follows,

> Sometimes, when discovering the schema of existing data, values are always null and there's no type information. 
> The UNKNOWN type can be used to annotate a column that is always null. (Similar to Null type in Avro and Arrow)

### Unsupported Datatypes

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported
version:1.0

[ClickHouse] MAY not support the following Parquet types:

- `Time32`
- `Fixed_Size_Binary`
- `JSON`
- `UUID`
- `ENUM`
- `Null`

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataTypes.Unsupported.ChunkedArray
version:1.0

[ClickHouse] MAY not support Parquet chunked arrays.

### Filter Pushdown

#### RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown
version:1.0

[ClickHouse] MAY support filter pushdown functionality when importing from the Parquet files.

> The functionality should behave similar to https://drill.apache.org/docs/parquet-filter-pushdown/

#### Supported Operations that utilize Min/Max Statistics

##### RQ.SRS-032.ClickHouse.Parquet.Import.FilterPushdown.MinMax.Operations
version:1.0

| Supported Operations |
|----------------------|
| =                    |
| !=                   |
| >                    |
| <                    |
| >=                   |
| <=                   |
| IN                   |
| NOT IN               |


### Projections

#### RQ.SRS-032.ClickHouse.Parquet.Import.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

### Skip Columns

#### RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns
version: 1.0

[ClickHouse] SHALL support skipping unexistent columns when importing from Parquet files.

### Skip Values

#### RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues
version: 1.0

[ClickHouse] SHALL support skipping unsupported values when import from Parquet files. When the values are being skipped, the inserted values SHALL be the default value for the corresponding column's datatype.

For example, trying to insert `Null` values into the non-`Nullable` column.

```sql
CREATE TABLE TestTable
(
    `path` String,
    `date` Date,
    `hits` UInt32
)
ENGINE = MergeTree
ORDER BY (date, path);

SELECT *
FROM file(output.parquet);

┌─path───┬─date───────┬─hits─┐
│ /path1 │ 2021-06-01 │   10 │
│ /path2 │ 2021-06-02 │    5 │
│ ᴺᵁᴸᴸ   │ 2021-06-03 │    8 │
└────────┴────────────┴──────┘

INSERT INTO TestTable
FROM INFILE 'output.parquet' FORMAT Parquet;

SELECT *
FROM TestTable;

┌─path───┬───────date─┬─hits─┐
│ /path1 │ 2021-06-01 │   10 │
│ /path2 │ 2021-06-02 │    5 │
│        │ 2021-06-03 │    8 │
└────────┴────────────┴──────┘
```

### Auto Typecast

#### RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast
version: 1.0

[ClickHouse] SHALL automatically typecast parquet datatype based on the types in the target table.

For example,

> When we take the following Parquet file:
> 
> ```
> ┌─path────────────────────────────────────────────────────────────┬─date───────┬──hits─┐
> │ Akiba_Hebrew_Academy                                            │ 2017-08-01 │   241 │
> │ 1980_Rugby_League_State_of_Origin_match                         │ 2017-07-01 │     2 │
> │ Column_of_Santa_Felicita,_Florence                              │ 2017-06-01 │    14 │
> └─────────────────────────────────────────────────────────────────┴────────────┴───────┘
> ```
> 
> ```
> ┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
> │ path │ Nullable(String) │              │                    │         │                  │                │
> │ date │ Nullable(String) │              │                    │         │                  │                │
> │ hits │ Nullable(Int64)  │              │                    │         │                  │                │
> └──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘
> ```
> 
> 
> Then create a table to import parquet data to:
> ```sql
> CREATE TABLE sometable
> (
>     `path` String,
>     `date` Date,
>     `hits` UInt32
> )
> ENGINE = MergeTree
> ORDER BY (date, path)
> ```
> 
> Then import data using a FROM INFILE clause:
> 
> 
> ```sql
> INSERT INTO sometable
> FROM INFILE 'data.parquet' FORMAT Parquet;
> ```
> 
> As a result ClickHouse automatically converted parquet `strings` (in the `date` column) to the `Date` type.
> 
> 
> ```sql
> DESCRIBE TABLE sometable
> ```
> 
> ```
> ┌─name─┬─type───┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
> │ path │ String │              │                    │         │                  │                │
> │ date │ Date   │              │                    │         │                  │                │
> │ hits │ UInt32 │              │                    │         │                  │                │
> └──────┴────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘
> ```

### Row Group Size

#### RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize
version: 1.0

[ClickHouse] SHALL support importing Parquet files with different Row Group Sizes.

As described in https://parquet.apache.org/docs/file-format/configurations/#row-group-size,

> We recommend large row groups (512MB - 1GB). Since an entire row group might need to be read, 
> we want it to completely fit on one HDFS block.

### Data Page Size

#### RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize
version: 1.0

[ClickHouse] SHALL support importing Parquet files with different Data Page Sizes.

As described in https://parquet.apache.org/docs/file-format/configurations/#data-page--size,

> Note: for sequential scans, it is not expected to read a page at a time; this is not the IO chunk. We recommend 8KB for page sizes.


### Import Into New Table

#### RQ.SRS-032.ClickHouse.Parquet.Import.NewTable
version: 1.0

[ClickHouse] SHALL support creating and populating tables directly from the Parquet files with table schema being auto-detected
from file's structure.

For example,

> Since ClickHouse reads parquet file schema, we can create tables on the fly:
> 
> ```sql
> CREATE TABLE imported_from_parquet
> ENGINE = MergeTree
> ORDER BY tuple() AS
> SELECT *
> FROM file('data.parquet', Parquet)
> ```
> 
> This will automatically create and populate a table from a given parquet file:
> 
> ```sql
> DESCRIBE TABLE imported_from_parquet;
> ```
> ```
> ┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
> │ path │ Nullable(String) │              │                    │         │                  │                │
> │ date │ Nullable(String) │              │                    │         │                  │                │
> │ hits │ Nullable(Int64)  │              │                    │         │                  │                │
> └──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘
> ```

### Performance

#### RQ.SRS-032.ClickHouse.Parquet.Import.Performance.CountFromMetadata
version: 1.0

[ClickHouse] MAY support importing the information about the number of rows from Parquet file directly from the metadata instead of going through the whole file.

For example,

> When running this query,
> 
> ```sql
> SELECT count(*)
> FROM file('*.parquet', 'Parquet');
>
> ┌───count()─┐
> │ 110000000 │
> └───────────┘
> 
> Elapsed: 1.365 sec.
> ```
> 
> The runtime should be around ~16ms instead of 1.365 sec.
>

#### RQ.SRS-032.ClickHouse.Parquet.Import.Performance.ParallelProcessing
version: 1.0

[ClickHouse] SHALL support process parallelization when importing from the parquet files.

### Import Nested Types

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested
version: 1.0

[ClickHouse] SHALL support importing nested columns from the Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.Complex
version:1.0

[ClickHouse] SHALL support importing nested: `Array`, `Tuple` and `Map` datatypes from Parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested
version: 1.0

[ClickHouse] SHALL support inserting arrays of nested structs from Parquet files into [ClickHouse] Nested columns when the `input_format_parquet_import_nested` setting is set to `1`.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] Nested columns when the
`input_format_parquet_import_nested` setting is set to `0`.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] not Nested columns.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert datatypes other than arrays of nested structs from Parquet files into [ClickHouse] Nested columns.

### Import Chunked Columns

#### RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns
version: 1.0

[ClickHouse] SHALL support importing Parquet files with chunked columns.

### Import Encoded

#### Plain (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain
version: 1.0

[ClickHouse] SHALL support importing `Plain` encoded Parquet files.

#### Dictionary (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Dictionary
version: 1.0

[ClickHouse] SHALL support importing `Dictionary` encoded Parquet files.

#### Run Length Encoding (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength
version: 1.0

[ClickHouse] SHALL support importing `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.

#### Delta (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta
version: 1.0

[ClickHouse] SHALL support importing `Delta Encoding` encoded Parquet files.

#### Delta-length byte array (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray
version: 1.0

[ClickHouse] SHALL support importing `Delta-length byte array` encoded Parquet files.

#### Delta Strings (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings
version: 1.0

[ClickHouse] SHALL support importing `Delta Strings` encoded Parquet files.

#### Byte Stream Split (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit
version: 1.0

[ClickHouse] SHALL support importing `Byte Stream Split` encoded Parquet files.

### Import Settings

#### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying the `input_format_parquet_import_nested` setting to allow inserting arrays of
nested structs into Nested column type. The default value SHALL be `0`.

- `0` — Data can not be inserted into Nested columns as an array of structs.
- `1` — Data can be inserted into Nested columns as an array of structs.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying the `input_format_parquet_case_insensitive_column_matching` setting to ignore matching
Parquet and ClickHouse columns. The default value SHALL be `0`.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying the `input_format_parquet_allow_missing_columns` setting to allow missing columns.
The default value SHALL be `0`.

#### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference
version: 1.0

[ClickHouse] SHALL support specifying the `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference` 
setting to allow skipping unsupported types. The default value SHALL be `0`.

### Libraries

#### RQ.SRS-032.ClickHouse.Parquet.Libraries
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using various libraries.

#### Pyarrow

##### RQ.SRS-032.ClickHouse.Parquet.Libraries.Pyarrow
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using `Pyarrow`.

#### PySpark

##### RQ.SRS-032.ClickHouse.Parquet.Libraries.PySpark
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using `PySpark`.

#### Pandas

##### RQ.SRS-032.ClickHouse.Parquet.Libraries.Pandas
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using `Pandas`.

#### parquet-go

##### RQ.SRS-032.ClickHouse.Parquet.Libraries.ParquetGO
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using `parquet-go`.

#### H2OAI

##### RQ.SRS-032.ClickHouse.Parquet.Libraries.H2OAI
version: 1.0

[ClickHouse] SHALL support importing from Parquet files generated using `H2OAI`.

## Export from Parquet Files

### RQ.SRS-032.ClickHouse.Parquet.Export
version: 1.0

[ClickHouse] SHALL support using `SELECT` query with either the `INTO OUTFILE {file_name}` or just `FORMAT Parquet` clauses to Export Parquet files. 

For example,

```sql
SELECT *
FROM sometable
INTO OUTFILE 'export.parquet'
FORMAT Parquet
```

or

```sql
SELECT *
FROM sometable
FORMAT Parquet
```

### Auto Detect Parquet File When Exporting

#### RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat
version: 1.0


[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using OUTFILE clause without explicitly specifying the format setting.

```sql
SELECT *
FROM sometable
INTO OUTFILE 'export.parquet'
```

### Supported Data types

#### RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported
version:1.0

[ClickHouse] SHALL support exporting the following datatypes to Parquet:

| ClickHouse data type                  | Parquet data type         |
|---------------------------------------|---------------------------|
| `Bool`                                | `BOOL`                    |
| `UInt8`                               | `UINT8`                   |
| `Int8`/`Enum8`                        | `INT8`                    |
| `UInt16`                              | `UINT16`                  |
| `Int16`/`Enum16`                      | `INT16`                   |
| `UInt32`                              | `UINT32`                  |
| `Int32`                               | `INT32`                   |
| `UInt64`                              | `UINT64`                  |
| `Int64`                               | `INT64`                   |
| `Float32`                             | `FLOAT`                   |
| `Float64`                             | `DOUBLE`                  |
| `Date32`                              | `DATE`                    |
| `DateTime`                            | `UINT32`                  |
| `DateTime64`                          | `TIMESTAMP`               |
| `String`                              | `BINARY`                  |
| `FixedString`                         | `FIXED_LENGTH_BYTE_ARRAY` |
| `Decimal`                             | `DECIMAL`                 |
| `Array`                               | `LIST`                    |
| `Tuple`                               | `STRUCT`                  |
| `Map`                                 | `MAP`                     |
| `IPv4`                                | `UINT32`                  |
| `IPv6`                                | `FIXED_LENGTH_BYTE_ARRAY` |
| `Int128`/`UInt128`/`Int256`/`UInt256` | `FIXED_LENGTH_BYTE_ARRAY` |

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BLOB
version:1.0

[ClickHouse] SHALL support exporting parquet files with `BLOB` content.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BOOL
version:1.0

[ClickHouse] SHALL support exporting `BOOL` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT8
version:1.0

[ClickHouse] SHALL support exporting `UINT8` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT8
version:1.0

[ClickHouse] SHALL support exporting `INT8` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT16
version:1.0

[ClickHouse] SHALL support exporting `UINT16` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT16
version:1.0

[ClickHouse] SHALL support exporting `INT16` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT32
version:1.0

[ClickHouse] SHALL support exporting `UINT32` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT32
version:1.0

[ClickHouse] SHALL support exporting `INT32` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.UINT64
version:1.0

[ClickHouse] SHALL support exporting `UINT64` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.INT64
version:1.0

[ClickHouse] SHALL support exporting `INT64` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FLOAT
version:1.0

[ClickHouse] SHALL support exporting `FLOAT` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DOUBLE
version:1.0

[ClickHouse] SHALL support exporting `DOUBLE` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE
version:1.0

[ClickHouse] SHALL support exporting `DATE` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ms
version:1.0

[ClickHouse] SHALL support exporting `DATE (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.ns
version:1.0

[ClickHouse] SHALL support exporting `DATE (ns)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DATE.us
version:1.0

[ClickHouse] SHALL support exporting `DATE (us)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIME.ms
version:1.0

[ClickHouse] SHALL support exporting `TIME (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ms
version:1.0

[ClickHouse] SHALL support exporting `TIMESTAMP (ms)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.ns
version:1.0

[ClickHouse] SHALL support exporting `TIMESTAMP (ns)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.TIMESTAMP.us
version:1.0

[ClickHouse] SHALL support exporting `TIMESTAMP (us)` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRING
version:1.0

[ClickHouse] SHALL support exporting `STRING` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.BINARY
version:1.0

[ClickHouse] SHALL support exporting `BINARY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.FixedLengthByteArray
version:1.0

[ClickHouse] SHALL support exporting `FIXED_LENGTH_BYTE_ARRAY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL
version:1.0

[ClickHouse] SHALL support exporting `DECIMAL` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.DECIMAL.Filter
version:1.0

[ClickHouse] SHALL support exporting `DECIMAL` Parquet datatype with specified filters.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.LIST
version:1.0

[ClickHouse] SHALL support exporting `LIST` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.ARRAY
version:1.0

[ClickHouse] SHALL support exporting `ARRAY` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.STRUCT
version:1.0

[ClickHouse] SHALL support exporting `STRUCT` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Supported.MAP
version:1.0

[ClickHouse] SHALL support exporting `MAP` Parquet datatype.

#### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nullable
version:1.0

[ClickHouse] SHALL support exporting `Nullable` datatypes to Parquet files and `Nullable` datatypes that consist only of `Null`.

### Working With Nested Types Export

#### RQ.SRS-032.ClickHouse.Parquet.Export.Nested
version: 1.0

[ClickHouse] SHALL support exporting nested columns to the Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Nested.Complex
version:1.0

[ClickHouse] SHALL support exporting nested: `Array`, `Tuple` and `Map` datatypes to Parquet files.

### Exporting Chunked Columns

#### RQ.SRS-032.ClickHouse.Parquet.Export.ChunkedColumns
version: 1.0

[ClickHouse] SHALL support exporting chunked columns to Parquet files.

### Multi-chunk Upload (Split to Rowgroups)

#### Inserting Data Into Parquet Files

##### RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Insert
version: 1.0

[ClickHouse] SHALL support exporting Parquet files with multiple row groups.

#### Move from MergeTree Part to Parquet

##### RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.MergeTreePart
version: 1.0  

[ClickHouse] SHALL support moving data from a MergeTree part to a Parquet file. The process must handle large parts by 
processing them in MergeTree blocks, ensuring that each block is written as a RowGroup in the Parquet file.

#### Settings for Manipulating the Size of Row Groups

##### RQ.SRS-032.ClickHouse.Parquet.Export.MultiChunkUpload.Settings.RowGroupSize
version: 1.0

| Settings                                     | Values                                         | Description                                                                                                                                                                                                                                                                       |
|----------------------------------------------|------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `min_insert_block_size_rows`                 | `Positive integer (default: 1048449)` or `0`   | Sets the minimum number of rows in the block that can be inserted into a table by an INSERT query. Smaller-sized blocks are squashed into bigger ones.                                                                                                                            |
| `min_insert_block_size_bytes`                | `Positive integer (default: 268402944)` or `0` | Sets the minimum number of bytes in the block which can be inserted into a table by an INSERT query. Smaller-sized blocks are squashed into bigger ones.                                                                                                                          |
| `output_format_parquet_row_group_size`       | `Positive integer (default: 1000000)` or `0`   | Target row group size in rows.                                                                                                                                                                                                                                                    |
| `output_format_parquet_row_group_size_bytes` | `Positive integer (default: 536870912)` or `0` | Target row group size in bytes, before compression.                                                                                                                                                                                                                               |
| `output_format_parquet_parallel_encoding`    | `1` or `0`                                     | Do Parquet encoding in multiple threads. Requires `output_format_parquet_use_custom_encoder`.                                                                                                                                                                                     |
| `max_threads`                                | `Positive integer (default: 4)` or `0`         | The maximum number of query processing threads, excluding threads for retrieving data from remote servers.                                                                                                                                                                        |
| `max_insert_block_size`                      | `Positive integer (default: 1048449)` or `0`   | The size of blocks (in a count of rows) to form for insertion into a table.                                                                                                                                                                                                       |
| `max_block_size`                             | `Positive integer (default: 65409)` or `0`     | indicates the recommended maximum number of rows to include in a single block when loading data from tables. Blocks the size of max_block_size are not always loaded from the table: if ClickHouse determines that less data needs to be retrieved, a smaller block is processed. |


### Query Types

#### JOIN

##### RQ.SRS-032.ClickHouse.Export.Parquet.Join
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT` query with a `JOIN` clause into a Parquet file.

#### UNION

##### RQ.SRS-032.ClickHouse.Parquet.Export.Union
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT` query with a `UNION` clause into a Parquet file.

##### RQ.SRS-032.ClickHouse.Parquet.Export.Union.Multiple
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT` query with multiple `UNION` clauses used on the Parquet file.

For example,

```sql
SELECT * FROM (SELECT * FROM file('file0001.parquet')
UNION ALL SELECT * FROM file('file0001.parquet')
UNION ALL SELECT * FROM file('file0001.parquet')
UNION ALL SELECT * FROM file('file0001.parquet')
UNION ALL SELECT * FROM file('file0001.parquet')
...
UNION ALL SELECT * FROM file('file0001.parquet')) LIMIT 10;
```

#### RQ.SRS-032.ClickHouse.Parquet.Export.View
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT * FROM {view_name}` query into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT * FROM {mat_view_name}` query into a Parquet file.

### Export Encoded

#### Plain (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain
version: 1.0

[ClickHouse] SHALL support exporting `Plain` encoded Parquet files.

#### Dictionary (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Dictionary
version: 1.0

[ClickHouse] SHALL support exporting `Dictionary` encoded Parquet files.

#### Run Length Encoding (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength
version: 1.0

[ClickHouse] SHALL support exporting `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.

#### Delta (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta
version: 1.0

[ClickHouse] SHALL support exporting `Delta Encoding` encoded Parquet files.

#### Delta-length byte array (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray
version: 1.0

[ClickHouse] SHALL support exporting `Delta-length byte array` encoded Parquet files.

#### Delta Strings (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings
version: 1.0

[ClickHouse] SHALL support exporting `Delta Strings` encoded Parquet files.

#### Byte Stream Split (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit
version: 1.0

[ClickHouse] SHALL support exporting `Byte Stream Split` encoded Parquet files.

### Export Settings

#### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize
version: 1.0

[ClickHouse] SHALL support specifying the `output_format_parquet_row_group_size` setting to specify row group size in rows.
The default value SHALL be `1000000`.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString
version: 1.0

[ClickHouse] SHALL support specifying the `output_format_parquet_string_as_string` setting to use Parquet String type instead of Binary.
The default value SHALL be `0`.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray
version: 1.0

[ClickHouse] SHALL support specifying the `output_format_parquet_fixed_string_as_fixed_byte_array` setting to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns. The default value SHALL be `1`.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion
version: 1.0

[ClickHouse] SHALL support specifying the `output_format_parquet_version` setting to set the version of Parquet used in the output file.
The default value SHALL be `2.latest`.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod
version: 1.0

[ClickHouse] SHALL support specifying the `output_format_parquet_compression_method` setting to set the compression method used in the Parquet file.
The default value SHALL be `lz4`.

### Type Conversion

#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction
version:1.0

[ClickHouse] SHALL support using type conversion functions when importing Parquet files.

For example,

```sql
SELECT
    n,
    toDateTime(time)
FROM file('time.parquet', Parquet);
```

## Native Reader

### RQ.SRS-032.ClickHouse.Parquet.NativeReader
version: 1.0

[ClickHouse] SHALL support usage of the Parquet native reader which enables direct reading of Parquet binary data into [ClickHouse] columns, bypassing the intermediate step of using the Apache Arrow library. This feature is controlled by the setting `input_format_parquet_use_native_reader`.

For example,

```sql
SELECT * FROM file('data.parquet', Parquet) SETTINGS input_format_parquet_use_native_reader = 1;
```

### Data Types Support

#### RQ.SRS-032.ClickHouse.Parquet.NativeReader.DataTypes
version: 1.0

[ClickHouse] SHALL support reading all existing Parquet data types when the native reader is enabled with `input_format_parquet_use_native_reader = 1`.

## Hive Partitioning

### RQ.SRS-032.ClickHouse.Parquet.Hive
version: 1.0

[ClickHouse] MAY not support importing or exporting hive partitioned Parquet files.

## Parquet Encryption

### File Encryption

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.File
version: 1.0

[ClickHouse] MAY support importing or exporting encrypted Parquet files.

### Column Encryption

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Modular
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with specific encrypted columns.

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.Column.Keys
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files when different columns are encrypted with different keys.

### Encryption Algorithms

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCM
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with `AES-GCM` encryption algorithm.

> The default algorithm AES-GCM provides full protection against tampering with data and metadata parts in Parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.Algorithms.AESGCMCTR
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with `AES-GCM-CTR`  encryption algorithm.

> The alternative algorithm AES-GCM-CTR supports partial integrity protection of Parquet files. 
> Only metadata parts are protected against tampering, not data parts. 
> An advantage of this algorithm is that it has a lower throughput overhead compared to the AES-GCM algorithm.

### EncryptionParameters

#### RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with different parameters.

##### RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Algorythm
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with `encryption.algorithm` parameter specified.

##### RQ.SRS-032.ClickHouse.Parquet.Encryption.Parameters.Plaintext.Footer
version: 1.0

[ClickHouse] MAY support importing or exporting Parquet files with `encryption.plaintext.footer` parameter specified.

## DESCRIBE Parquet

### RQ.SRS-032.ClickHouse.Parquet.Structure
version: 1.0

[ClickHouse] SHALL support using `DESCRIBE TABLE` statement on the Parquet to read the file structure.

For example,

```sql
DESCRIBE TABLE file('data.parquet', Parquet)
```

## Compression

### None

#### RQ.SRS-032.ClickHouse.Parquet.Compression.None
version: 1.0

[ClickHouse] SHALL support importing or exporting uncompressed Parquet files.

### Gzip

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using gzip.

### Brotli

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using brotli.

### Lz4

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4.

### Lz4Raw

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4_raw.

### Lz4Hadoop

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Hadoop
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using LZ4_HADOOP.

### Snappy

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Snappy
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using Snappy.

### Zstd

#### RQ.SRS-032.ClickHouse.Parquet.Compression.Zstd
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using Zstd.

### Unsupported Compression

#### Lzo

##### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo
version: 1.0

[ClickHouse] MAY not support importing or exporting Parquet files compressed using lzo.

## Table Functions

### URL

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function importing and exporting Parquet format.

### File

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function importing and exporting Parquet format.

For example,

```sql
SELECT * FROM file('data.parquet', Parquet)
```

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat
version: 1.0

[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using `file()` function without explicitly specifying the format setting.

```sql
SELECT * FROM file('data.parquet')
```

### S3

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function for import and exporting Parquet format.

For example,

```sql
SELECT *
FROM s3('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)
```

#### Detecting Hive Partitioning

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3.HivePartitioning
version: 1.0

[ClickHouse] SHALL support detecting Hive partitioning when using the `s3` table function with `use_hive_partitioning` setting. That allows to use partition columns as virtual columns in the query.

For example,

```sql
SELECT * from s3('s3://data/path/date=*/country=*/code=*/*.parquet') where _date > '2020-01-01' and _country = 'Netherlands' and _code = 42;
```

> When setting use_hive_partitioning is set to 1, ClickHouse will detect 
> Hive-style partitioning in the path (/name=value/) and will allow to use partition columns as virtual columns in the query. These virtual columns will have the same names as in the partitioned path, but starting with _.
> 
> Source: https://clickhouse.com/docs/en/sql-reference/table-functions/s3#hive-style-partitioning
### JDBC

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function for import and exporting Parquet format.

### ODBC

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function for importing and exporting Parquet format.

### HDFS

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function for importing and exporting Parquet format.

### Remote

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function for importing and exporting Parquet format.

### MySQL

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL
version: 1.0

[ClickHouse] SHALL support `mysql` table function for import and exporting Parquet format.

For example,

> Given we have a table with a `mysql` engine:
> 
> ```sql
> CREATE TABLE mysql_table1 (
>   id UInt64,
>   column1 String
> )
> ENGINE = MySQL('mysql-host.domain.com','db1','table1','mysql_clickhouse','Password123!')
> ```
> 
> We can Export from a Parquet file format with:
> 
> ```sql
> SELECT * FROM mysql_table1 INTO OUTFILE testTable.parquet FORMAT Parquet
> ```

### PostgreSQL

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function importing and exporting Parquet format.

## Table Engines

### Readable External Table

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.ReadableExternalTable
version: 1.0

[ClickHouse] MAY support Parquet format being exported from and imported into all table engines using `READABLE EXTERNAL TABLE`.

For example,

> ```sql
> CREATE READABLE EXTERNAL TABLE table_name (
>     key UInt32,
>     value UInt32
> ) LOCATION ('file://file_localtion/*.parquet')
> ```

### MergeTree

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MergeTree` table engine.

#### ReplicatedMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplicatedMergeTree` table engine.

#### ReplacingMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplacingMergeTree` table engine.

#### SummingMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `SummingMergeTree` table engine.

#### AggregatingMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `AggregatingMergeTree` table engine.

#### CollapsingMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `CollapsingMergeTree` table engine.

#### VersionedCollapsingMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `VersionedCollapsingMergeTree` table engine.

#### GraphiteMergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `GraphiteMergeTree` table engine.

### Integration Engines

#### ODBC Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `ODBC` table engine.

#### JDBC Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `JDBC` table engine.

#### MySQL Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MySQL` table engine.

#### MongoDB Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MongoDB` table engine.

#### HDFS Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `HDFS` table engine.

#### S3 Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `S3` table engine.

#### Kafka Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Kafka` table engine.

#### EmbeddedRocksDB Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `EmbeddedRocksDB` table engine.

#### PostgreSQL Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `PostgreSQL` table engine.

### Special Engines

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Memory` table engine.

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Distributed` table engine.

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Dictionary` table engine.

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `File` table engine.

#### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `URL` table engine.

## Indexes

### RQ.SRS-032.ClickHouse.Parquet.Indexes
version: 1.0

[ClickHouse] SHALL support importing from Parquet files that utilize indexes.

### Page

#### RQ.SRS-032.ClickHouse.Parquet.Indexes.Page
version: 1.0

[ClickHouse] SHALL support utilizing 'Page Index' of a parquet file in order to read data from the file more efficiently.

### Bloom Filter

#### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter
version: 1.0

[ClickHouse] SHALL support utilizing 'Bloom Filter' of a parquet file in order to read data from the file more efficiently. In order to use Bloom filters, the `input_format_parquet_bloom_filter_push_down` setting SHALL be set to `true`.

For example,
```sql
SELECT * FROM file('test.Parquet, Parquet) WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' SETTINGS input_format_parquet_bloom_filter_push_down=true
```

> A Bloom filter is a compact data structure that overapproximates a set. It can respond to membership 
> queries with either “definitely no” or “probably yes”, where the probability of false positives is configured when the filter is initialized. Bloom filters do not have false negatives.
> 
> Because Bloom filters are small compared to dictionaries, they can be used for predicate pushdown even in columns with high cardinality and when space is at a premium.

#### Parquet Column Types Support

##### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes
version: 1.0

| Supported            | Unsupported |
|----------------------|-------------|
| FLOAT                | BOOLEAN     |
| DOUBLE               | UUID        |
| STRING               | BSON        |``
| INT and UINT         | JSON        |
| FIXED_LEN_BYTE_ARRAY | ARRAY       |
|                      | MAP         |
|                      | TUPLE       |
|                      | ARRAY       |
|                      | ENUM        |
|                      | INTERVAL    |
|                      | DECIMAL     |
|                      | TIMESTAMP   |

#### Supported Operators

##### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.Operators
version: 1.0

The following operators are supported when utilizing the Bloom filter applied on Parquet files:

| Supported Operators |
|---------------------|
| =                   |
| !=                  |
| hasAny()            |
| has()               |
| IN                  |
| NOT IN              |


##### Only Considering Parquet Structure When Using Key Column Types

###### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.KeyColumnTypes
version: 1.0

[ClickHouse] SHALL only consider the Parquet structure when utilizing Bloom filters from Parquet files and ignore the key column types.

For example,
    
```sql
select string_column from file('file.parquet', Parquet, 'string_column Decimal64(4, 2)') WHERE string_column = 'xyz' SETTINGS input_format_parquet_bloom_filter_push_down=true
```

[ClickHouse] SHALL utilize bloom filter and skip row groups despite the fact that `Decimal` values are not supported by ClickHouse Bloom filter implementation. 
This happens, because the real Parquet column type of `string_column` here is `String` which is supported by ClickHouse Bloom filter implementation.

##### Only Considering Parquet Structure When Using Field Types

###### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ColumnTypes.Ignore.FieldTypes
version: 1.0

[ClickHouse] SHALL only consider the Parquet structure when utilizing Bloom filters from Parquet files and ignore the field types.

For example,

```sql
SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toDecimal(2, 4) SETTINGS input_format_parquet_bloom_filter_push_down=true
```

[ClickHouse] SHALL utilize bloom filter and skip row groups despite the fact that `Decimal` values are not supported by ClickHouse Bloom filter implementation. 
This happens, because the real Parquet column type of `xyz` here is `String` which is supported by ClickHouse Bloom filter implementation.


#### Columns With Complex Datatypes That Have Bloom Filter Applied on Them

##### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.DataTypes.Complex
version: 1.0

[ClickHouse] SHALL support reading data from a Parquet file that has row-groups with the Bloom Filter and complex datatype columns. This allows to decrease the query runtime for queries that include reading from a parquet file with `Array`, `Map` and `Tuple` datatypes.

#### Consistent Output When Using Key Column Types

##### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.KeyColumnTypes
version: 1.0

[ClickHouse] SHALL provide the same output when reading data from a Parquet file with the query including key column type, both when `input_format_parquet_bloom_filter_push_down` is set to `true` and `false`.

For example,

```sql
select string_column from file('file.parquet', Parquet, 'string_column Int64') SETTINGS input_format_parquet_bloom_filter_push_down=true
```

and

```sql
select string_column from file('file.parquet', Parquet, 'string_column Int64') SETTINGS input_format_parquet_bloom_filter_push_down=false
```

SHALL have the same output.

#### Consistent Output When Using Field Types

##### RQ.SRS-032.ClickHouse.Parquet.Indexes.BloomFilter.ConsistentOutput.FieldTypes
version: 1.0

[ClickHouse] SHALL provide the same output when reading data from a Parquet file with the query including field type, both when `input_format_parquet_bloom_filter_push_down` is set to `true` and `false`.

For example,

```sql
SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toInt32(5) SETTINGS input_format_parquet_bloom_filter_push_down=true
```

and

```sql
SELECT * FROM file('file.parquet', Parquet) WHERE xyz = toInt32(5) SETTINGS input_format_parquet_bloom_filter_push_down=false
``` 

SHALL have the same output.

### Dictionary

#### RQ.SRS-032.ClickHouse.Parquet.Indexes.Dictionary
version: 1.0

[ClickHouse] SHALL support utilizing 'Dictionary' of a parquet file in order to read data from the file more efficiently.


## Metadata

### RQ.SRS-032.ClickHouse.Parquet.Metadata
version: 1.0

Parquet files have three types of metadata

- file metadata
- column (chunk) metadata
- page header metadata

as described in https://parquet.apache.org/docs/file-format/metadata/.

### ParquetFormat

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat
version: 1.0

[ClickHouse] SHALL support `ParquetMetadata` format to read metadata from Parquet files.

For example,

```sql
SELECT * FROM file(data.parquet, ParquetMetadata) format PrettyJSONEachRow
```

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output
version: 1.0

[ClickHouse] SHALL not support `ParquetMetadata` format as an output format and the `FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT` 
error SHALL be returned.

For example,

```sql
SELECT *
FROM file('writing_nullable_int8.parquet', 'ParquetMetadata')
FORMAT ParquetMetadata

Exception on client:
Code: 399. DB::Exception: Code: 399. DB::Exception: Format ParquetMetadata is not suitable for output. (FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT) (version 23.5.1.2890 (official build)). (FORMAT_IS_NOT_SUITABLE_FOR_OUTPUT)
```

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content
version: 1.0

[ClickHouse]'s ParquetMetadata format SHALL output the Parquet metadata in the following structure:

> - num_columns - the number of columns
> - num_rows - the total number of rows
> - num_row_groups - the total number of row groups
> - format_version - parquet format version, always 1.0 or 2.6
> - total_uncompressed_size - total uncompressed bytes size of the data, calculated as the sum of total_byte_size from all row groups
> - total_compressed_size - total compressed bytes size of the data, calculated as the sum of total_compressed_size from all row groups
> - columns - the list of columns metadata with the next structure:
>     - name - column name
>     - path - column path (differs from name for nested column)
>     - max_definition_level - maximum definition level
>     - max_repetition_level - maximum repetition level
>     - physical_type - column physical type
>     - logical_type - column logical type
>     - compression - compression used for this column
>     - total_uncompressed_size - total uncompressed bytes size of the column, calculated as the sum of total_uncompressed_size of the column from all row groups
>     - total_compressed_size - total compressed bytes size of the column, calculated as the sum of total_compressed_size of the column from all row groups
>     - space_saved - percent of space saved by compression, calculated as (1 - total_compressed_size/total_uncompressed_size).
>     - encodings - the list of encodings used for this column
> - row_groups - the list of row groups metadata with the next structure:
>     - num_columns - the number of columns in the row group
>     - num_rows - the number of rows in the row group
>     - total_uncompressed_size - total uncompressed bytes size of the row group
>     - total_compressed_size - total compressed bytes size of the row group
>     - columns - the list of column chunks metadata with the next structure:
>        - name - column name
>        - path - column path
>        - total_compressed_size - total compressed bytes size of the column
>        - total_uncompressed_size - total uncompressed bytes size of the row group
>        - have_statistics - boolean flag that indicates if column chunk metadata contains column statistics
>        - statistics - column chunk statistics (all fields are NULL if have_statistics = false) with the next structure:
>            - num_values - the number of non-null values in the column chunk
>            - null_count - the number of NULL values in the column chunk
>            - distinct_count - the number of distinct values in the column chunk
>            - min - the minimum value of the column chunk
>            - max - the maximum column of the column chunk

For example,

> ```json
> {
>     "num_columns": "2",
>     "num_rows": "100000",
>     "num_row_groups": "2",
>     "format_version": "2.6",
>     "metadata_size": "577",
>     "total_uncompressed_size": "282436",
>     "total_compressed_size": "26633",
>     "columns": [
>         {
>             "name": "number",
>             "path": "number",
>             "max_definition_level": "0",
>             "max_repetition_level": "0",
>             "physical_type": "INT32",
>             "logical_type": "Int(bitWidth=16, isSigned=false)",
>             "compression": "LZ4",
>             "total_uncompressed_size": "133321",
>             "total_compressed_size": "13293",
>             "space_saved": "90.03%",
>             "encodings": [
>                 "RLE_DICTIONARY",
>                 "PLAIN",
>                 "RLE"
>             ]
>         },
>         {
>             "name": "concat('Hello', toString(modulo(number, 1000)))",
>             "path": "concat('Hello', toString(modulo(number, 1000)))",
>             "max_definition_level": "0",
>             "max_repetition_level": "0",
>             "physical_type": "BYTE_ARRAY",
>             "logical_type": "None",
>             "compression": "LZ4",
>             "total_uncompressed_size": "149115",
>             "total_compressed_size": "13340",
>             "space_saved": "91.05%",
>             "encodings": [
>                 "RLE_DICTIONARY",
>                 "PLAIN",
>                 "RLE"
>             ]
>         }
>     ],
>     "row_groups": [
>         {
>             "num_columns": "2",
>             "num_rows": "65409",
>             "total_uncompressed_size": "179809",
>             "total_compressed_size": "14163",
>             "columns": [
>                 {
>                     "name": "number",
>                     "path": "number",
>                     "total_compressed_size": "7070",
>                     "total_uncompressed_size": "85956",
>                     "have_statistics": true,
>                     "statistics": {
>                         "num_values": "65409",
>                         "null_count": "0",
>                         "distinct_count": null,
>                         "min": "0",
>                         "max": "999"
>                     }
>                 },
>                 {
>                     "name": "concat('Hello', toString(modulo(number, 1000)))",
>                     "path": "concat('Hello', toString(modulo(number, 1000)))",
>                     "total_compressed_size": "7093",
>                     "total_uncompressed_size": "93853",
>                     "have_statistics": true,
>                     "statistics": {
>                         "num_values": "65409",
>                         "null_count": "0",
>                         "distinct_count": null,
>                         "min": "Hello0",
>                         "max": "Hello999"
>                     }
>                 }
>             ]
>         }
> 
>     ]
> }
> ```

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax
version: 1.0

[ClickHouse] SHALL support Parquet files that have Min/Max values in the metadata and the files that are missing Min/Max values.

### Extra Entries in Metadata

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.ExtraEntries
version: 1.0

[ClickHouse] SHALL support reading from Parquet files that have extra entries in the metadata.

### Metadata Types

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.File
version: 1.0

[ClickHouse] SHALL support accessing `File Metadata` in Parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.Column
version: 1.0

[ClickHouse] SHALL support accessing `Column (Chunk) Metadata` in Parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.Header
version: 1.0

[ClickHouse] SHALL support accessing `Page Header Metadata` in Parquet files.

### Cache for ListObjects 

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects
version: 1.0

[ClickHouse] SHALL support caching the ListObjects to avoid repeated and expensive backend calls. This feature SHALL be controlled by the `use_object_storage_list_objects_cache` query setting.

For example,

```sql
SELECT
    date,
    count()
FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/*/*.parquet', NOSIGN)
WHERE (date >= '2025-01-01') AND (date <= '2025-01-31')
GROUP BY date
ORDER BY date ASC
SETTINGS use_hive_partitioning = 1, use_object_storage_list_objects_cache = 1
```

#### Settings for Caching ListObjects

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.Settings
version: 1.0

| Setting                                         | Type   | Description                                                                                   | Values                      |
|-------------------------------------------------|--------|-----------------------------------------------------------------------------------------------|-----------------------------|
| `object_storage_list_objects_cache_size`        | Server | Maximum size of ObjectStorage list objects cache in bytes. Zero means disabled.               | UInt64 (Default: 500000000) |
| `object_storage_list_objects_cache_max_entries` | Server | Maximum size of ObjectStorage list objects cache in entries. Zero means disabled.             | UInt64 (Default: 1000)      |
| `object_storage_list_objects_cache_ttl`         | Server | Time to live of records in ObjectStorage list objects cache in seconds. Zero means unlimited. | UInt64 (Default: 3600)      |

#### Caching ListObjects When the Same Bucket Exists in Different Storage Providers

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.SameBucket
version: 1.0

[ClickHouse] SHALL ensure that there are no collisions between different storage providers in scenarios where buckets with the same name containing the same directories exist in multiple object storage providers (e.g., AWS S3, GCS, etc.). Each storage provider's bucket SHALL be uniquely identified and handled independently to avoid conflicts.

#### Caching User Credentials

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Cache.ListObjects.UserCredentials
version: 1.0

[ClickHouse] SHALL not cache user credentials when caching the ListObjects. The credentials SHALL be passed to the object storage backend each time a request is made.

For example, the correct behavior is:

When we select the data with credentials for the first time and with `use_object_storage_list_objects_cache = 1` the query returns  the data and caches the ListObjects.

```sql
SELECT *
FROM s3('http://localhost:11111/test/root/**.parquet', 'clickhous', 'clickhous')
SETTINGS use_object_storage_list_objects_cache = 1


   ┌─id─┐
1. │  0 │
2. │  1 │
3. │  2 │
4. │  3 │
5. │  4 │
   └────┘

5 rows in set. Elapsed: 0.030 sec. 
```

When we execute the same query but without credentials we SHALL get an exception.

```sql
SELECT *
FROM s3('http://localhost:11111/test/root/**.parquet')
SETTINGS use_object_storage_list_objects_cache = 1

Query id: 0f2c41f5-7fc1-403f-964b-ad0fc8af9ba0


Elapsed: 0.135 sec. 

Received exception from server (version 25.2.2):
Code: 117. DB::Exception: Received from localhost:9000. DB::Exception: IOError: Code: 499. DB::Exception: The Access Key Id you provided does not exist in our records.: while reading key: root/{_partition_id}.parquet, from bucket: test. (S3_ERROR) (version 25.2.2.20000.altinityantalya): (in file/uri test/root/{_partition_id}.parquet): While executing ParquetBlockInputFormat: While executing S3(_table_function.s3)Source. (INCORRECT_DATA)
```

### Caching for Object Storage

#### Test Schema For Metadata Caching

```yaml
Metadata Caching for Object Storage:
  Settings:
    - input_format_parquet_use_metadata_cache:
        type: query_settings
        values: true/false
        default: false
    - input_format_parquet_metadata_cache_max_entries:
        type: server_settings
        values: UInt64
        default: 500000000 (bytes)
  Engines And Functions That Can Store Parquet:
    - S3
    - S3Cluster
    - HDFS
    - IcebergS3
    - IcebergAzure
    - IcebergHDFS
    - IcebergLocal
    - URL
    - file
  Engines not suited for direct Parquet storage:
    - Dictionary
    - Distributed
    - Memory
    - PostgreSQL
    - MySQL
    - MongoDB
    - Kafka
    - EmbeddedRocksDB
    - JDBC
    - ODBC
  Remote Object Storages:
    - S3
    - Azure
    - Google Cloud Storage
    - MinIO
    - HDFS
    - Wasabi
    - DigitalOcean Spaces
    - Ceph RADOS Gateway
    - Yandex.Cloud Object Storage
    - Cloudflare R2
    - Alibaba Cloud OSS
  Files:
    - count: [one, many]
    - location: [same, different]
    - partitioning: [hive, custom]
    - name: [same, different]
  Actions:
    - delete file
    - read file:
        cache state:
          - cache miss so populate metadata cache
          - cache hit use metadata cache
        with glob:
          - file matches glob
          - file does not match glob
    - List all cached metadata files
  cases when metadata cache speeds up query execution:
    - Skip the read of the whole file:
        - SELECT COUNT()
        - Queries that utilize:
            - min/max
            - bloom filter
            - row count
        - DISTINCT COUNT
        - SELECT ... FROM file('file.parquet', ParquetMetadata)
        - DESCRIBE Parquet schema
    - Skip the read of some row groups:
        - SELECT COUNT()
        - Queries that utilize:
            - min/max
            - bloom filter
            - row count
        - DISTINCT COUNT
        - SELECT ... FROM file('file.parquet', ParquetMetadata)
        - DESCRIBE Parquet schema
  Query Types:
    - Regular Query
    - JOIN two parquet files
    - Basic Nested Subquery
    - Union All with Nested Parquet Queries
    - Join Two Parquet Subqueries from S3
    - Nested Subquery with an Additional Filter and Aggregation
    - Combining a UNION with a JOIN
  Metadata Types:
    - ClickHouse generated metadata
    - Metadata from the file generated outside ClickHouse:
        - Parquetify
        - DuckDB
        - Apache Arrow
        - External files for ClickHouse inc tests
  Use metadata cache along other settings:
    settings:
        - aggregation_in_order                                  
        - aggregation_memory_efficient_merge_threads            
        - allow_ddl                                             
        - allow_experimental_bigint_types                       
        - allow_experimental_decimal_type                       
        - allow_experimental_map_type                           
        - allow_experimental_object_type                        
        - allow_experimental_window_functions                   
        - allow_introspection_functions                         
        - allow_nullable_key                                    
        - allow_suspicious_low_cardinality_types                
        - async_socket_for_remote                               
        - compile_aggregate_expressions                         
        - compile_expressions                                   
        - connect_timeout                                       
        - custom_settings_prefix                                
        - database_atomic_wait_for_drop_and_detach_synchronously
        - debug_allow_same_replica_for_distributed_queries      
        - dialect_type                                          
        - distributed_aggregation_memory_efficient              
        - force_index_by_date                                   
        - force_primary_key                                     
        - format_csv_allow_double_quotes                        
        - format_csv_allow_single_quotes                        
        - format_csv_delimiter                                  
        - format_tsv_allow_single_quotes                        
        - group_by_overflow_mode                                
        - group_by_two_level_threshold                          
        - http_max_multipart_form_data_size                     
        - http_receive_timeout                                  
        - http_send_timeout                                     
        - input_format_allow_errors_num                         
        - input_format_allow_errors_ratio                       
        - input_format_csv_delimiter                            
        - input_format_csv_enum_detect_factor                   
        - input_format_csv_enum_parsing_mode                    
        - input_format_defaults_for_omitted_fields              
        - input_format_import_nested_json                       
        - input_format_null_as_default                          
        - input_format_skip_unknown_fields                      
        - join_algorithm                                        
        - join_default_strictness                               
        - join_use_nulls                                        
        - load_balancing                                        
        - log_queries                                           
        - log_comment                                           
        - lookup_replica_priority                               
        - low_cardinality_allow_in_native_format                
        - max_ast_depth                                         
        - max_ast_elements                                      
        - max_bytes_before_external_group_by                    
        - max_bytes_before_external_sort                        
        - max_bytes_before_remerge_sort                         
        - max_bytes_in_dist_read                                
        - max_bytes_in_join                                     
        - max_bytes_to_read                                     
        - max_csv_rows_to_read_for_schema_inference             
        - max_distributed_connections                           
        - max_execution_speed                                   
        - max_execution_speed_overflow_mode                     
        - max_execution_time                                    
        - max_expanded_ast_elements                             
        - max_insert_threads                                    
        - max_memory_usage                                      
        - max_memory_usage_for_all_queries                      
        - max_memory_usage_for_user                             
        - max_parallel_replicas                                 
        - max_pipeline_depth                                    
        - max_query_size                                        
        - max_read_buffer_size                                  
        - max_result_bytes                                      
        - max_result_rows                                       
        - max_rows_in_distinct                                  
        - max_rows_in_join                                      
        - max_rows_in_set                                       
        - max_rows_in_table_function                            
        - max_rows_in_view                                      
        - max_rows_to_group_by                                  
        - max_rows_to_read                                      
        - memory_overflow_mode                                  
        - merge_tree_uniform_read_distribution                  
        - min_execution_speed                                   
        - min_execution_speed_overflow_mode                     
        - optimize_fuse_sum_count_avg                           
        - optimize_move_functions_out_of_any                    
        - optimize_skip_unused_shards                           
        - optimize_throw_if_suboptimal_plan                     
        - optimize_read_in_order                                
        - output_format_json_escape_forward_slashes             
        - output_format_json_quote_64bit_integers               
        - output_format_pretty_max_rows                         
        - output_format_write_statistics                        
        - partial_merge_join_optimizations                      
        - prefer_localhost_replica                              
        - readonly                                              
        - send_logs_level                                       
        - timeout_before_checking_execution_speed               
        - use_uncompressed_cache                                
        - user_files_path                                       
        - wait_end_of_query
```

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage
version: 1.0

[ClickHouse] SHALL support caching [the whole metadata object](#rqsrs-032clickhouseparquetmetadataparquetmetadatacontent) when querying Parquet files stored in any type of remote object storage by using the 
`input_format_parquet_use_metadata_cache` query setting (disabled by default). The metadata caching SHALL allow faster query execution by avoiding the need to read the Parquet file’s metadata each time a query is executed.

For example,

```sql
SELECT COUNT(*)
FROM s3(s3_url, filename = 'test.parquet', format = Parquet)
SETTINGS input_format_parquet_use_metadata_cache=1;
```

> [!NOTE]
> For the input_format_parquet_use_metadata_cache setting to consistently work the following setting must be disabled: optimize_count_from_files=0, remote_filesystem_read_prefetch=0

#### Setting Propagation to All Nodes

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation
version: 1.0

[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query.

##### Propagate Settings to All Nodes When Set in the Profile (All Nodes)

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings
version: 1.0

[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query when set from the profile settings for all nodes.

For example, 

when the setting is set in the `users.xml` file for all nodes as:

```xml
<input_format_parquet_use_metadata_cache>1</input_format_parquet_use_metadata_cache>
```

##### Propagate Settings to All Nodes When Set in the Profile (Initiator Node Only)

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SettingPropagation.ProfileSettings.InitiatorNode
version: 1.0

[ClickHouse] SHALL propagate the `input_format_parquet_use_metadata_cache` setting to all nodes in a distributed query when set from the profile settings for the initiator node only.

For example, 

when the setting is set in the `users.xml` file for the initiator node as:

```xml
<input_format_parquet_use_metadata_cache>1</input_format_parquet_use_metadata_cache>
```

#### Cache Eviction

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheEviction
version: 1.0

[ClickHouse] SHALL evict entries from the metadata cache when:

* The total size of cached metadata exceeds `input_format_parquet_metadata_cache_max_entries` setting.

The cache eviction SHALL be done in a Segmented Least Recently Used (SLRU) manner when the cache size limit is reached.



#### Swarm

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `swarm` cluster by using the `input_format_parquet_use_metadata_cache` setting with `object_storage_cluster='swarm'` setting and `s3` function.

For example,

```sql
SELECT hostName() AS host, count() 
FROM s3('http://minio:9000/warehouse/data/data/**/**.parquet')
GROUP BY host
SETTINGS use_hive_partitioning=1, object_storage_cluster='swarm'
```

##### Read With Swarm From S3Cluster

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.ReadWithS3Cluster
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `swarm` cluster by using the `input_format_parquet_use_metadata_cache` setting with `s3Cluster` function.

For example,

```sql
SELECT hostName() AS host, * 
FROM s3Cluster('swarm', 'http://minio:9000/warehouse/data/data/**/**.parquet')
SETTINGS use_hive_partitioning=1
```

##### Swarm Node Stops During Query Execution

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Swarm.NodeStops
version: 1.0

[ClickHouse] SHALL output an error when a node in the swarm cluster stops during query execution as there are no retries implemented in swarm.

#### Object Storages

##### S3 Storage

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.S3
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3` storage by using the `input_format_parquet_use_metadata_cache` setting.

##### Azure

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Azure
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Azure` storage by using the `input_format_parquet_use_metadata_cache` setting.

##### Google Cloud Storage

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.GoogleCloudStorage
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Google Cloud Storage` by using the `input_format_parquet_use_metadata_cache` setting.

##### MinIO

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MinIO
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `MinIO` by using the `input_format_parquet_use_metadata_cache` setting.

##### HDFS Storage

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HDFS
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `HDFS` by using the `input_format_parquet_use_metadata_cache` setting.

##### Wasabi

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Wasabi
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Wasabi` by using the `input_format_parquet_use_metadata_cache` setting.

##### DigitalOcean Spaces

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.DigitalOceanSpaces
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `DigitalOcean Spaces` by using the `input_format_parquet_use_metadata_cache` setting.

##### Ceph RADOS Gateway

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CephRADOSGateway
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Ceph RADOS Gateway` by using the `input_format_parquet_use_metadata_cache` setting.

##### Yandex Cloud Object Storage

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.YandexCloudObjectStorage
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Yandex Cloud Object Storage` by using the `input_format_parquet_use_metadata_cache` setting.

##### Cloudflare R2

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CloudflareR2
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Cloudflare R2` by using the `input_format_parquet_use_metadata_cache` setting.

##### Alibaba Cloud OSS

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AlibabaCloudOSS
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `Alibaba Cloud OSS` by using the `input_format_parquet_use_metadata_cache` setting.

#### All Functions and Engines That Can Store Parquet 

##### S3 Engine or Function

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3` engine or function by using the `input_format_parquet_use_metadata_cache` setting.

For example,


```sql
SELECT *
FROM s3(s3_url, filename = 'test.parquet', format = Parquet)
```

##### S3Cluster

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.S3Cluster
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `S3Cluster` by using the `input_format_parquet_use_metadata_cache` setting.

For example,

```sql
SELECT COUNT(*)
FROM s3Cluster(s3_cluster_name, s3_url, filename = 'test.parquet', format = Parquet)
SETTINGS input_format_parquet_use_metadata_cache=1;
```

##### IcebergS3 Engine or Function

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.IcebergS3
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `IcebergS3` engine or function including,`IcebergAzure`, `IcebergHDFS` and `IcebergLocal`, by using the `input_format_parquet_use_metadata_cache` setting.

##### URL Engine or Function

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.URL
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `URL` engine or function by using the `input_format_parquet_use_metadata_cache` setting.

##### File Engine or Function

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.File
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `File` engine or function by using the `input_format_parquet_use_metadata_cache` setting.

##### HDFS Engine or Function

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.EnginesAndFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support caching metadata when querying Parquet files stored in `HDFS` engine or function by using the `input_format_parquet_use_metadata_cache` setting.

#### Trying To Cache Metadata When Using Engines Not Suited for Direct Parquet Storage

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NotSuitedEngines
version: 1.0

[ClickHouse] SHALL throw an error when trying to cache metadata when querying Parquet files stored in engines that are not suited for direct Parquet storage.

#### Cache Invalidation

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Invalidation
version: 1.0

[ClickHouse] SHALL throw and error when the Parquet file is deleted from the object storage and we try to access the cache related to that file.

#### Cache Clearing

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing
version: 1.0

[ClickHouse] SHALL support clearing the Parquet metadata cache on a single node using the `SYSTEM DROP PARQUET METADATA CACHE` command.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.CacheClearing,OnCluster
version: 1.0

[ClickHouse] SHALL support clearing the Parquet metadata cache on all nodes in a cluster using the `SYSTEM DROP PARQUET METADATA CACHE ON CLUSTER {cluster_name}` command.


#### Reading Metadata After Caching Is Completed

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.ReadMetadataAfterCaching
version: 1.0

[ClickHouse] SHALL support reading a given Parquet file's metadata once it has been cached.

For example,

If we run a query against a Parquet file once, when the metadata is cached, the following query SHALL return the metadata of the given Parquet file:

```sql
SELECT *
FROM s3(s3_url, filename = 'test.parquet', format = ParquetMetadata)
```

#### Caching When Reading From Hive Partitioned Parquet Files in Object Storage

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HivePartitioning
version: 1.0

[ClickHouse] SHALL support caching metadata when querying multiple Parquet files stored in object storage by using the `input_format_parquet_use_metadata_cache` and `use_hive_partitioning` setting.

For example,

```sql
SELECT date, sum(output_count)
FROM s3('s3://aws-public-blockchain/v1.0/btc/transactions/date=*/*.parquet', NOSIGN)
WHERE date>='2024-01-01'
GROUP BY date ORDER BY date
```

#### Caching Settings

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.Settings
version: 1.0

| Setting                                           | Values                          | Description                                                                         |
|---------------------------------------------------|---------------------------------|-------------------------------------------------------------------------------------|
| `input_format_parquet_use_metadata_cache`         | `true`/`false` (default: false) | Enable/disable caching of Parquet file metadata                                     |
| `input_format_parquet_metadata_cache_max_entries` | `INT` (default: 500000000 bytes)           | Maximum number of file metadata objects to cache set from the server configuration. |

#### All Possible Settings That Can Be Used Along With Metadata Caching Settings

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.AllSettings
version: 1.0

The following settings SHALL not cause any crashes in the system when used along with `input_format_parquet_use_metadata_cache`:

| Setting                                                | Description                                                                                                                        |
|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| aggregation_in_order                                   | Enables partial aggregation in sort order if data is already sorted by GROUP BY keys.                                              |
| aggregation_memory_efficient_merge_threads             | Number of threads used for external merges during aggregation when data is spilled to disk.                                        |
| allow_ddl                                              | If disabled, DDL statements (CREATE, DROP, ALTER, etc.) are disallowed; typically set for read-only usage.                         |
| allow_experimental_bigint_types                        | Enables the experimental Int128, Int256, UInt128, UInt256 types (in some newer versions).                                          |
| allow_experimental_decimal_type                        | Enables the experimental extended Decimal types beyond standard Decimal(76, x).                                                    |
| allow_experimental_map_type                            | Enables experimental Map data type usage in queries.                                                                               |
| allow_experimental_object_type                         | Enables experimental Object data type usage in queries.                                                                            |
| allow_experimental_window_functions                    | Allows usage of window functions in older releases when they were still marked experimental.                                       |
| allow_introspection_functions                          | Allows special introspection/debugging functions (e.g. queryMemoryUsage()).                                                        |
| allow_nullable_key                                     | Permits using nullable columns as keys in GROUP BY or JOIN operations.                                                             |
| allow_suspicious_low_cardinality_types                 | Allows creating or querying LowCardinality columns in contexts that may be risky or unoptimized.                                   |
| async_socket_for_remote                                | Enables asynchronous network I/O for distributed queries to improve performance under certain conditions.                          |
| compile_aggregate_expressions                          | Tries to compile certain aggregate expressions to native code (requires ClickHouse built with LLVM).                               |
| compile_expressions                                    | Attempts to compile complex expressions to native code via LLVM JIT for faster execution.                                          |
| connect_timeout                                        | Timeout (seconds) for establishing connections (e.g., to remote shards in a distributed query).                                    |
| custom_settings_prefix                                 | A prefix for custom (user-defined) settings to avoid naming conflicts with built-in settings.                                      |
| database_atomic_wait_for_drop_and_detach_synchronously | Waits for asynchronous tasks (DROP/DETACH) in Atomic databases to finish.                                                          |
| debug_allow_same_replica_for_distributed_queries       | Allows reading from the same replica multiple times in distributed queries (for debugging/diagnostics).                            |
| dialect_type                                           | Chooses which SQL dialect to emulate (clickhouse, mysql, postgresql, etc.).                                                        |
| distributed_aggregation_memory_efficient               | Improves memory usage for distributed aggregation by streaming partial results.                                                    |
| force_index_by_date                                    | Requires a partition key or index by date to be used; otherwise the query fails.                                                   |
| force_primary_key                                      | Requires usage of the primary key for query filtering; otherwise the query fails.                                                  |
| format_csv_allow_double_quotes                         | When reading/writing CSV, whether double quotes are allowed to quote strings.                                                      |
| format_csv_allow_single_quotes                         | When reading/writing CSV, whether single quotes are allowed to quote strings.                                                      |
| format_csv_delimiter                                   | Delimiter character for CSV format (, by default).                                                                                 |
| format_tsv_allow_single_quotes                         | Allows single quotes in TSV parsing (less common).                                                                                 |
| group_by_overflow_mode                                 | Action if GROUP BY exceeds certain limits (e.g., throw, break).                                                                    |
| group_by_two_level_threshold                           | Threshold of distinct keys at which ClickHouse switches to two-level aggregation.                                                  |
| http_max_multipart_form_data_size                      | Maximum size for multipart/form-data HTTP requests (relevant if query input arrives this way).                                     |
| http_receive_timeout                                   | HTTP server receive timeout (in seconds) for query data.                                                                           |
| http_send_timeout                                      | HTTP server send timeout (in seconds) for sending results back to the client.                                                      |
| input_format_allow_errors_num                          | Maximum number of parsing errors allowed in input before aborting.                                                                 |
| input_format_allow_errors_ratio                        | Maximum ratio of parsing errors allowed (fraction of total rows) before aborting.                                                  |
| input_format_csv_delimiter                             | Delimiter for CSV input (can be overridden per query).                                                                             |
| input_format_csv_enum_detect_factor                    | Heuristic factor for detecting Enum from CSV input.                                                                                |
| input_format_csv_enum_parsing_mode                     | Parsing mode for CSV Enum fields (string, auto, numeric, etc.).                                                                    |
| input_format_defaults_for_omitted_fields               | Use default values if certain columns are missing from input.                                                                      |
| input_format_import_nested_json                        | Allows parsing nested JSON structures in input.                                                                                    |
| input_format_null_as_default                           | Treats NULL in incoming data as the default value for non-nullable columns.                                                        |
| input_format_skip_unknown_fields                       | Skip fields in input that do not match any column definition.                                                                      |
| join_algorithm                                         | Chooses join algorithm (auto, hash, partial_merge, etc.).                                                                          |
| join_default_strictness                                | Default JOIN strictness if not specified (_`ANY                                                                                    |
| join_use_nulls                                         | Use NULL in joined columns if no match (for left/full joins).                                                                      |
| load_balancing                                         | Strategy for choosing replicas in a distributed query (random, nearest_hostname, etc.).                                            |
| log_queries                                            | Enables or disables writing query info into system.query_log.                                                                      |
| log_comment                                            | Additional string comment appended to query logs for identification.                                                               |
| lookup_replica_priority                                | Whether to consider replica priority for distributed reads.                                                                        |
| low_cardinality_allow_in_native_format                 | Allow storing LowCardinality columns in the native (optimized) format.                                                             |
| max_ast_depth                                          | Maximum depth of the query’s AST (Abstract Syntax Tree).                                                                           |
| max_ast_elements                                       | Maximum number of nodes/elements in the query’s AST.                                                                               |
| max_bytes_before_external_group_by                     | Threshold (bytes) before partial GROUP BY is spilled to disk.                                                                      |
| max_bytes_before_external_sort                         | Threshold (bytes) before partial sort is spilled to disk.                                                                          |
| max_bytes_before_remerge_sort                          | Threshold for re-merging data on disk in external sorts.                                                                           |
| max_bytes_in_dist_read                                 | Maximum bytes to read from each remote shard in a distributed query.                                                               |
| max_bytes_in_join                                      | Maximum bytes in an in-memory JOIN state.                                                                                          |
| max_bytes_to_read                                      | Maximum total bytes that can be read from storage during the query.                                                                |
| max_csv_rows_to_read_for_schema_inference              | If using automatic schema inference from CSV, stops reading after this many rows for detection.                                    |
| max_distributed_connections                            | Maximum number of connections to remote servers in distributed queries.                                                            |
| max_execution_speed                                    | Maximum execution speed (rows/second). If exceeded, the query is paused or stopped depending on max_execution_speed_overflow_mode. |
| max_execution_speed_overflow_mode                      | Action if the query exceeds max_execution_speed (throw, break, etc.).                                                              |
| max_execution_time                                     | Maximum execution time in seconds. Query is aborted if exceeded (unless changed by the overflow mode).                             |
| max_expanded_ast_elements                              | Limits expansions in the AST (e.g., from IN sets).                                                                                 |
| max_insert_threads                                     | Maximum threads for INSERT SELECT queries.                                                                                         |
| max_memory_usage                                       | Maximum memory usage per query.                                                                                                    |
| max_memory_usage_for_all_queries                       | Maximum total memory usage for all queries on the server.                                                                          |
| max_memory_usage_for_user                              | Maximum total memory usage for all queries by the current user.                                                                    |
| max_parallel_replicas                                  | Maximum number of replicas to use in parallel for a query in a Distributed table.                                                  |
| max_pipeline_depth                                     | Maximum execution pipeline depth.                                                                                                  |
| max_query_size                                         | Maximum size of the query text in bytes.                                                                                           |
| max_read_buffer_size                                   | Size (bytes) of the buffer used when reading from filesystem or network.                                                           |
| max_result_bytes                                       | Maximum total size of the result (in bytes) returned by a query.                                                                   |
| max_result_rows                                        | Maximum number of rows in the result set returned by a query.                                                                      |
| max_rows_in_distinct                                   | Limit on the number of rows held in memory for SELECT DISTINCT.                                                                    |
| max_rows_in_join                                       | Limit on the number of rows in a join hash table.                                                                                  |
| max_rows_in_set                                        | Limit on the number of rows in a SET (for IN subqueries).                                                                          |
| max_rows_in_table_function                             | Limit on rows read by table functions like s3, hdfs, or file.                                                                      |
| max_rows_in_view                                       | Limit on rows that a VIEW can return.                                                                                              |
| max_rows_to_group_by                                   | Limit on rows to process in GROUP BY before taking an overflow action.                                                             |
| max_rows_to_read                                       | Limit on number of rows read from storage during the query.                                                                        |
| memory_overflow_mode                                   | Action if max_memory_usage is exceeded (throw, break, etc.).                                                                       |
| merge_tree_uniform_read_distribution                   | Distribute reads more evenly among parts for MergeTree tables if possible.                                                         |
| min_execution_speed                                    | Minimum execution speed in rows/second; if slower after timeout_before_checking_execution_speed, it’s aborted/paused.              |
| min_execution_speed_overflow_mode                      | Action if query falls below min_execution_speed.                                                                                   |
| optimize_fuse_sum_count_avg                            | Tries to rewrite sequences of sum, count, avg into more optimal queries (e.g., combining aggregates).                              |
| optimize_move_functions_out_of_any                     | Moves functions out of any(...) if possible to reduce overhead.                                                                    |
| optimize_skip_unused_shards                            | Skip contacting shards if partition pruning or other conditions show no data is needed from them.                                  |
| optimize_throw_if_suboptimal_plan                      | Throw an exception if the optimizer cannot generate a plan that is considered optimal (based on internal heuristics).              |
| optimize_read_in_order                                 | Attempt to read in sorted order to avoid extra sorting if the query ORDER BY matches table sorting.                                |
| output_format_json_escape_forward_slashes              | Whether to escape _"/_" in JSON output formats.                                                                                    |
| output_format_json_quote_64bit_integers                | Whether to quote 64-bit integers in JSON output (to avoid losing precision in certain JS clients).                                 |
| output_format_pretty_max_rows                          | Maximum number of rows printed in FORMAT Pretty.                                                                                   |
| output_format_write_statistics                         | Controls whether to output query execution statistics in some formats.                                                             |
| partial_merge_join_optimizations                       | Enables partial merge join (useful if both tables are large and sorted on join keys).                                              |
| prefer_localhost_replica                               | Prefer reading from the local replica first in a replicated/distributed setup if available.                                        |
| readonly                                               | If >0, disallows write operations (DDL/DML) – only SELECT. If >1, also disallows creating temporary tables, etc.                   |
| send_logs_level                                        | Controls the verbosity of logs sent back to the client.                                                                            |
| timeout_before_checking_execution_speed                | Time (seconds) after which ClickHouse checks if min_execution_speed is met.                                                        |
| use_uncompressed_cache                                 | Enables the uncompressed cache for data, which can speed reads but uses more memory.                                               |
| user_files_path                                        | Path where user can read files from or write files to (when using file table function, etc.).                                      |
| wait_end_of_query                                      | When set, waits for the query to finish for all replicas in a Distributed table before returning (used in replication scenarios).  |
| object_storage_cluster                                 |                                                                                                                                    |

#### Cases When Metadata Cache Speeds Up Query Execution

##### Count

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.Count
version: 1.0

[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the following query:

```sql
SELECT COUNT(*) FROM s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;
```

##### Min and Max

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.MinMax
version: 1.0

[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize min/max values from metadata.

For example,

```sql
SELECT * FROM s3(s3_url, filename = 'test.parquet', format = Parquet) WHERE column1 > 1000 SETTINGS input_format_parquet_use_metadata_cache=1;
```

##### Bloom Filter Caching

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.BloomFilter
version: 1.0

[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize bloom filter.

For example,

```sql
SELECT * FROM s3(s3_url, filename = 'test.parquet', format = Parquet) WHERE column1 = 'value' SETTINGS input_format_parquet_use_metadata_cache=1, input_format_parquet_bloom_filter=1;
```

##### Distinct Count

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.DistinctCount
version: 1.0

[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that utilize distinct count.

For example,

```sql
SELECT COUNT(DISTINCT column1) FROM s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;
```

##### File Schema

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SpeedUpQueryExecution.FileSchema
version: 1.0

[ClickHouse] SHALL speed up the query execution when the metadata is cached for the object storage for the queries that read the file schema.

For example,

```sql
DESCRIBE s3(s3_url, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1;
```

#### Maximum Size of Metadata Cache

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MaxSize
version: 1.0

[ClickHouse] SHALL support setting the maximum size of the metadata cache for Parquet files stored in object storage using the `input_format_parquet_metadata_cache_max_entries` (default value: 5000) setting. The setting must be set as a [ClickHouse] server configuration.
If the number of cached metadata objects exceeds the maximum size, the exception SHALL be thrown.

#### File With The Same Name But Different Location

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.SameNameDifferentLocation
version: 1.0

[ClickHouse] SHALL be able to successfully read from the Parquet files with the same name but different locations when the metadata is cached.

For example, if we have two files, `test.parquet` in `s3://bucket1/` and `test.parquet` in `s3://bucket2/`, the following query SHALL successfully read the data of the file after the metadata is cached:

```sql
SELECT COUNT(*) FROM s3({s3_url}/bucket1, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1
SELECT COUNT(*) FROM s3({s3_url}/bucket2, filename = 'test.parquet', format = Parquet) SETTINGS input_format_parquet_use_metadata_cache=1
```

#### Hits and Misses Counter

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.HitsMissesCounter
version: 1.0

[ClickHouse] SHALL support counting the number of cache hits and misses when querying Parquet files stored in object storage.
In order to get the number of cache hits and misses the following steps SHALL be taken:

1. Use the `log_comment` setting.
2. Query through the `system.log` using that `log_comment`.

```sql
SELECT COUNT(*)
FROM s3(s3_conn, filename = 'test_03262_*', format = Parquet)
SETTINGS input_format_parquet_use_metadata_cache=1;

SELECT COUNT(*)
FROM s3(s3_conn, filename = 'test_03262_*', format = Parquet)
SETTINGS input_format_parquet_use_metadata_cache=1, log_comment='test_03262_parquet_metadata_cache';

SYSTEM FLUSH LOGS;

SELECT ProfileEvents['ParquetMetaDataCacheHits']
FROM system.query_log
where log_comment = 'test_03262_parquet_metadata_cache'
AND type = 'QueryFinish'
ORDER BY event_time desc
LIMIT 1;
```

#### Nested Queries With Metadata Caching

##### Join Two Parquet Files From an Object Storage

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Join
version: 1.0

[ClickHouse] SHALL cache the metadata of both files when joining two Parquet files stored in object storage.

For example,

```sql
SELECT
    t1.id,
    t2.value
FROM s3(
    'https://my-bucket.s3.amazonaws.com/path/to/first.parquet',
    'Parquet',
    'id UInt64, data String'
) AS t1
JOIN s3(
    'https://my-bucket.s3.amazonaws.com/path/to/second.parquet',
    'Parquet',
    'id UInt64, value String'
) AS t2
    ON t1.id = t2.id SETTINGS input_format_parquet_use_metadata_cache=1;
```

##### Basic Nested Subquery

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.Basic
version: 1.0

The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.

```sql
SELECT
    COUNT(*) AS total_rows
FROM
(
    SELECT *
    FROM s3Cluster(
        s3_cluster_name,
        s3_url,
        'test.parquet',
        'Parquet'
    )
    SETTINGS input_format_parquet_use_metadata_cache = 1
)
WHERE some_column > 0;
```

##### Union All with Nested Parquet Queries

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionAll
version: 1.0

The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.
    
```sql
SELECT 'first_file' AS source, COUNT(*) AS row_count
FROM
(
    SELECT *
    FROM s3Cluster(
        s3_cluster_name,
        s3_url,
        'test.parquet',
        'Parquet'
    )
    SETTINGS input_format_parquet_use_metadata_cache = 1
)
WHERE some_column = 10

UNION ALL

SELECT 'second_file' AS source, COUNT(*) AS row_count
FROM
(
    SELECT *
    FROM s3Cluster(
        s3_cluster_name,
        s3_url,
        'another_file.parquet',
        'Parquet'
    )
    SETTINGS input_format_parquet_use_metadata_cache = 1
)
WHERE some_column = 10;
```

##### Nested Subquery with an Additional Filter and Aggregation

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.FilterAggregation
version: 1.0

The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.

```sql
SELECT
    region,
    COUNT(*) AS count_per_region
FROM
(
    SELECT
        region,
        user_id,
        total_spent
    FROM
    (
        SELECT *
        FROM s3Cluster(
            s3_cluster_name,
            s3_url,
            'test.parquet',
            'Parquet'
        )
        SETTINGS input_format_parquet_use_metadata_cache = 1
    )
    WHERE total_spent > 0
) AS data_with_spent
WHERE region != 'UNKNOWN'
GROUP BY region
ORDER BY count_per_region DESC;
```

##### Combining a UNION with a JOIN

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.UnionJoin
version: 1.0

The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.

```sql
WITH
transactions_all AS
(
    SELECT user_id, amount, event_date
    FROM
    (
        SELECT user_id, amount, event_date
        FROM s3Cluster(
            s3_cluster_name,
            s3_url,
            'transactions_2024.parquet',
            'Parquet'
        )
        SETTINGS input_format_parquet_use_metadata_cache = 1
        WHERE event_date < '2025-01-01'
    )
    UNION ALL
    SELECT user_id, amount, event_date
    FROM
    (
        SELECT user_id, amount, event_date
        FROM s3Cluster(
            s3_cluster_name,
            s3_url,
            'transactions_2025.parquet',
            'Parquet'
        )
        SETTINGS input_format_parquet_use_metadata_cache = 1
        WHERE event_date >= '2025-01-01'
    )
),

user_profiles AS
(
    SELECT user_id, region, signup_date
    FROM s3Cluster(
        s3_cluster_name,
        s3_url,
        'user_profiles.parquet',
        'Parquet'
    )
    SETTINGS input_format_parquet_use_metadata_cache = 1
)

SELECT
    p.user_id,
    p.region,
    SUM(t.amount) AS total_spent,
    COUNT()       AS txn_count
FROM transactions_all AS t
JOIN user_profiles AS p ON t.user_id = p.user_id
GROUP BY
    p.user_id,
    p.region
ORDER BY total_spent DESC
LIMIT 100;

```

##### Deeply Nested JOIN

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.NestedQueries.DeeplyNestedJoin

The metadata caching SHALL not cause any crashes or exception in [ClickHouse] when using the `input_format_parquet_use_metadata_cache` setting with a deeply nested query.

```sql
SELECT
    final_join.user_id,
    final_join.order_total AS total_orders,
    extra_info.extra_field  AS extra_info_field
FROM
(
    SELECT
        branch_1.user_id,
        branch_1.order_total,
        branch_2.preference
    FROM
    (
        SELECT
            subA.user_id,
            subA.order_total + IFNULL(subA2.additional_value, 0) AS order_total
        FROM
        (
            SELECT
                user_id,
                sum(amount) AS order_total
            FROM s3Cluster(
                s3_cluster_name,
                s3_url,
                'orders_2025.parquet',
                'Parquet'
            )
            SETTINGS input_format_parquet_use_metadata_cache = 1
            WHERE event_date >= '2025-01-01'
            GROUP BY user_id
        ) AS subA
        LEFT JOIN
        (
            SELECT
                user_id,
                sum(value) AS additional_value
            FROM s3Cluster(
                s3_cluster_name,
                s3_url,
                'orders_extras_2025.parquet',
                'Parquet'
            )
            SETTINGS input_format_parquet_use_metadata_cache = 1
            WHERE extra_flag = 1
            GROUP BY user_id
        ) AS subA2
        ON subA.user_id = subA2.user_id
    ) AS branch_1
    JOIN
    (
        SELECT
            subB.user_id,
            subB.preference
        FROM
        (
            SELECT
                user_id,
                any(preference) AS preference
            FROM s3Cluster(
                s3_cluster_name,
                s3_url,
                'user_preferences.parquet',
                'Parquet'
            )
            SETTINGS input_format_parquet_use_metadata_cache = 1
            GROUP BY user_id
        ) AS subB
    ) AS branch_2
    ON branch_1.user_id = branch_2.user_id
) AS final_join
LEFT JOIN
(
    SELECT
        user_id,
        extra_field
    FROM s3Cluster(
        s3_cluster_name,
        s3_url,
        'user_extra_info.parquet',
        'Parquet'
    )
    SETTINGS input_format_parquet_use_metadata_cache = 1
) AS extra_info
ON final_join.user_id = extra_info.user_id
WHERE final_join.order_total > 100
ORDER BY final_join.order_total DESC
LIMIT 50;
```
### Cachable Metadata Types

#### Metadata Generated by ClickHouse

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ClickHouse
version: 1.0

[ClickHouse] SHALL support caching metadata generated by [ClickHouse] when querying Parquet files stored in object storage.

#### Metadata Generated by Parquetify

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.Parquetify
version: 1.0

[ClickHouse] SHALL support caching metadata generated by [Parquetify](https://github.com/Altinity/parquet-regression/tree/main/parquetify) when querying Parquet files stored in object storage.

#### Metadata Generated by DuckDB

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.DuckDB
version: 1.0

[ClickHouse] SHALL support caching metadata generated by `DuckDB` when querying Parquet files stored in object storage.

#### Metadata Generated by Apache Arrow

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Caching.ObjectStorage.MetadataTypes.ApacheArrow
version: 1.0

[ClickHouse] SHALL support caching metadata generated by `Apache Arrow` when querying Parquet files stored in object storage.

## Error Recovery

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.MagicNumber
version: 1.0

[ClickHouse] SHALL output an error if the 4-byte magic number "PAR1" is missing from the Parquet metadata.

For example,

When using hexeditor on the Parquet file we alter the values of "PAR1" and change it to "PARQ".
then when we try to import that Parquet file to [ClickHouse] we SHALL get an exception:

```
exception. Code: 1001, type: parquet::ParquetInvalidOrCorruptedFileException,
e.what() = Invalid: Parquet magic bytes not found in footer.
Either the file is corrupted or this is not a Parquet file.
```

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.File
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `file` metadata.
In this case the file metadata is corrupt, the file is lost.

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Column
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `column` metadata.
In this case that column chunk MAY be lost but column chunks for this column in other row groups SHALL be okay.

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageHeader
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Header`.
In this case the remaining pages in that chunk SHALL be lost.

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.PageData
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Data`.
In this case that page SHALL be lost.

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Metadata.Checksum
version: 1.0

[ClickHouse] SHALL output an error if the Parquet file's checksum is corrupted.

### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt column values.

Error message example,

> DB::Exception: Cannot extract table structure from Parquet format file.


#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Date
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `date` values.


#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Int
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Int` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.BigInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BigInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.SmallInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `SmallInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TinyInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TinyInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UBigInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UBigInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.USmallInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `USmallInt` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.UTinyInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UTinyInt` values.


#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampUS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (us)` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimestampMS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (ms)` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Bool
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BOOL` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Float
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FLOAT` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Double
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DOUBLE` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeMS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ms)` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeUS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (us)` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.TimeNS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ns)` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.String
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRING` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Binary
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BINARY` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.FixedLengthByteArray
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FIXED_LENGTH_BYTE_ARRAY` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Decimal
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DECIMAL` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.List
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `LIST` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Struct
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRUCT` values.

#### RQ.SRS-032.ClickHouse.Parquet.ErrorRecovery.Corrupt.Values.Map
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `MAP` values.

## Interoperability Between ARM and x86

### Importing and Exporting Parquet Files On ARM That Were Generated On x86 Machine

#### RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.x86.To.ARM
version: 1.0

[ClickHouse] SHALL support importing and exporting parquet files on `ARM` machine that were generated on `x86` machine.

### Importing and Exporting Parquet Files On x86 That Were Generated On ARM Machine

#### RQ.SRS-032.ClickHouse.Parquet.Interoperability.From.ARM.To.x86
version: 1.0

[ClickHouse] SHALL support importing and exporting parquet files on `x86` machine that were generated on `ARM` machine.

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/parquet/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
