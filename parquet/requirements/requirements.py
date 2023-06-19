# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
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
    level=3,
    num="4.1.1",
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
    level=3,
    num="4.2.1",
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
    level=3,
    num="4.2.2",
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
    level=4,
    num="4.3.2.1",
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
    level=5,
    num="4.3.2.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes",
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
        ">For example,\n"
        ">\n"
        ">`Bool` -> `IPv6`\n"
        "\n"
        "| Parquet to ClickHouse supported Datatypes | ClickHouse Datatype Family        | alias_to Datatype | case_insensitive |\n"
        "|-------------------------------------------|-----------------------------------|-------------------|------------------|\n"
        "|                                           | `JSON`                            |                   | 1                |\n"
        "|                                           | `Polygon`                         |                   | 0                |\n"
        "|                                           | `Ring`                            |                   | 0                |\n"
        "|                                           | `Point`                           |                   | 0                |\n"
        "|                                           | `SimpleAggregateFunction`         |                   | 0                |\n"
        "|                                           | `IntervalQuarter`                 |                   | 0                |\n"
        "|                                           | `IntervalMonth`                   |                   | 0                |\n"
        "|                                           | `Int64`                           |                   | 0                |\n"
        "|                                           | `IntervalDay`                     |                   | 0                |\n"
        "|                                           | `IntervalHour`                    |                   | 0                |\n"
        "|                                           | `IPv4`                            |                   | 0                |\n"
        "|                                           | `IntervalSecond`                  |                   | 0                |\n"
        "|                                           | `LowCardinality`                  |                   | 0                |\n"
        "|                                           | `Int16`                           |                   | 0                |\n"
        "|                                           | `UInt256`                         |                   | 0                |\n"
        "|                                           | `AggregateFunction`               |                   | 0                |\n"
        "|                                           | `MultiPolygon`                    |                   | 0                |\n"
        "|                                           | `IPv6`                            |                   | 0                |\n"
        "|                                           | `Nothing`                         |                   | 0                |\n"
        "|                                           | `Decimal256`                      |                   | 1                |\n"
        "|                                           | `Tuple`                           |                   | 0                |\n"
        "|                                           | `Array`                           |                   | 0                |\n"
        "|                                           | `IntervalMicrosecond`             |                   | 0                |\n"
        "|                                           | `Bool`                            |                   | 1                |\n"
        "|                                           | `Enum16`                          |                   | 0                |\n"
        "|                                           | `IntervalMinute`                  |                   | 0                |\n"
        "|                                           | `FixedString`                     |                   | 0                |\n"
        "|                                           | `String`                          |                   | 0                |\n"
        "|                                           | `DateTime`                        |                   | 1                |\n"
        "|                                           | `Object`                          |                   | 0                |\n"
        "|                                           | `Map`                             |                   | 0                |\n"
        "|                                           | `UUID`                            |                   | 0                |\n"
        "|                                           | `Decimal64`                       |                   | 1                |\n"
        "|                                           | `Nullable`                        |                   | 0                |\n"
        "|                                           | `Enum`                            |                   | 1                |\n"
        "|                                           | `Int32`                           |                   | 0                |\n"
        "|                                           | `UInt8`                           |                   | 0                |\n"
        "|                                           | `Date`                            |                   | 1                |\n"
        "|                                           | `Decimal32`                       |                   | 1                |\n"
        "|                                           | `UInt128`                         |                   | 0                |\n"
        "|                                           | `Float64`                         |                   | 0                |\n"
        "|                                           | `Nested`                          |                   | 0                |\n"
        "|                                           | `UInt16`                          |                   | 0                |\n"
        "|                                           | `IntervalMillisecond`             |                   | 0                |\n"
        "|                                           | `Int128`                          |                   | 0                |\n"
        "|                                           | `Decimal128`                      |                   | 1                |\n"
        "|                                           | `Int8`                            |                   | 0                |\n"
        "|                                           | `Decimal`                         |                   | 1                |\n"
        "|                                           | `Int256`                          |                   | 0                |\n"
        "|                                           | `DateTime64`                      |                   | 1                |\n"
        "|                                           | `Enum8`                           |                   | 0                |\n"
        "|                                           | `DateTime32`                      |                   | 1                |\n"
        "|                                           | `Date32`                          |                   | 1                |\n"
        "|                                           | `IntervalWeek`                    |                   | 0                |\n"
        "|                                           | `UInt64`                          |                   | 0                |\n"
        "|                                           | `IntervalNanosecond`              |                   | 0                |\n"
        "|                                           | `IntervalYear`                    |                   | 0                |\n"
        "|                                           | `UInt32`                          |                   | 0                |\n"
        "|                                           | `Float32`                         |                   | 0                |\n"
        "|                                           | `bool`                            | `Bool`            | 1                |\n"
        "|                                           | `INET6`                           | `IPv6`            | 1                |\n"
        "|                                           | `INET4`                           | `IPv4`            | 1                |\n"
        "|                                           | `ENUM`                            | `Enum`            | 1                |\n"
        "|                                           | `BINARY`                          | `FixedString`     | 1                |\n"
        "|                                           | `GEOMETRY`                        | `String`          | 1                |\n"
        "|                                           | `NATIONAL CHAR VARYING`           | `String`          | 1                |\n"
        "|                                           | `BINARY VARYING`                  | `String`          | 1                |\n"
        "|                                           | `NCHAR LARGE OBJECT`              | `String`          | 1                |\n"
        "|                                           | `NATIONAL CHARACTER VARYING`      | `String`          | 1                |\n"
        "|                                           | `boolean`                         | `Bool`            | 1                |\n"
        "|                                           | `NATIONAL CHARACTER LARGE OBJECT` | `String`          | 1                |\n"
        "|                                           | `NATIONAL CHARACTER`              | `String`          | 1                |\n"
        "|                                           | `NATIONAL CHAR`                   | `String`          | 1                |\n"
        "|                                           | `CHARACTER VARYING`               | `String`          | 1                |\n"
        "|                                           | `LONGBLOB`                        | `String`          | 1                |\n"
        "|                                           | `TINYBLOB`                        | `String`          | 1                |\n"
        "|                                           | `MEDIUMTEXT`                      | `String`          | 1                |\n"
        "|                                           | `TEXT`                            | `String`          | 1                |\n"
        "|                                           | `VARCHAR2`                        | `String`          | 1                |\n"
        "|                                           | `CHARACTER LARGE OBJECT`          | `String`          | 1                |\n"
        "|                                           | `DOUBLE PRECISION`                | `Float64`         | 1                |\n"
        "|                                           | `LONGTEXT`                        | `String`          | 1                |\n"
        "|                                           | `NVARCHAR`                        | `String`          | 1                |\n"
        "|                                           | `INT1 UNSIGNED`                   | `UInt8`           | 1                |\n"
        "|                                           | `VARCHAR`                         | `String`          | 1                |\n"
        "|                                           | `CHAR VARYING`                    | `String`          | 1                |\n"
        "|                                           | `MEDIUMBLOB`                      | `String`          | 1                |\n"
        "|                                           | `NCHAR`                           | `String`          | 1                |\n"
        "|                                           | `VARBINARY`                       | `String`          | 1                |\n"
        "|                                           | `CHAR`                            | `String`          | 1                |\n"
        "|                                           | `SMALLINT UNSIGNED`               | `UInt16`          | 1                |\n"
        "|                                           | `TIMESTAMP`                       | `DateTime`        | 1                |\n"
        "|                                           | `FIXED`                           | `Decimal`         | 1                |\n"
        "|                                           | `TINYTEXT`                        | `String`          | 1                |\n"
        "|                                           | `NUMERIC`                         | `Decimal`         | 1                |\n"
        "|                                           | `DEC`                             | `Decimal`         | 1                |\n"
        "|                                           | `TIME`                            | `Int64`           | 1                |\n"
        "|                                           | `FLOAT`                           | `Float32`         | 1                |\n"
        "|                                           | `SET`                             | `UInt64`          | 1                |\n"
        "|                                           | `TINYINT UNSIGNED`                | `UInt8`           | 1                |\n"
        "|                                           | `INTEGER UNSIGNED`                | `UInt32`          | 1                |\n"
        "|                                           | `INT UNSIGNED`                    | `UInt32`          | 1                |\n"
        "|                                           | `CLOB`                            | `String`          | 1                |\n"
        "|                                           | `MEDIUMINT UNSIGNED`              | `UInt32`          | 1                |\n"
        "|                                           | `BLOB`                            | `String`          | 1                |\n"
        "|                                           | `REAL`                            | `Float32`         | 1                |\n"
        "|                                           | `SMALLINT`                        | `Int16`           | 1                |\n"
        "|                                           | `INTEGER SIGNED`                  | `Int32`           | 1                |\n"
        "|                                           | `NCHAR VARYING`                   | `String`          | 1                |\n"
        "|                                           | `INT SIGNED`                      | `Int32`           | 1                |\n"
        "|                                           | `TINYINT SIGNED`                  | `Int8`            | 1                |\n"
        "|                                           | `BIGINT SIGNED`                   | `Int64`           | 1                |\n"
        "|                                           | `BINARY LARGE OBJECT`             | `String`          | 1                |\n"
        "|                                           | `SMALLINT SIGNED`                 | `Int16`           | 1                |\n"
        "|                                           | `YEAR`                            | `UInt16`          | 1                |\n"
        "|                                           | `MEDIUMINT`                       | `Int32`           | 1                |\n"
        "|                                           | `INTEGER`                         | `Int32`           | 1                |\n"
        "|                                           | `INT1 SIGNED`                     | `Int8`            | 1                |\n"
        "|                                           | `BIT`                             | `UInt64`          | 1                |\n"
        "|                                           | `BIGINT UNSIGNED`                 | `UInt64`          | 1                |\n"
        "|                                           | `BYTEA`                           | `String`          | 1                |\n"
        "|                                           | `INT`                             | `Int32`           | 1                |\n"
        "|                                           | `SINGLE`                          | `Float32`         | 1                |\n"
        "|                                           | `MEDIUMINT SIGNED`                | `Int32`           | 1                |\n"
        "|                                           | `DOUBLE`                          | `Float64`         | 1                |\n"
        "|                                           | `INT1`                            | `Int8`            | 1                |\n"
        "|                                           | `CHAR LARGE OBJECT`               | `String`          | 1                |\n"
        "|                                           | `TINYINT`                         | `Int8`            | 1                |\n"
        "|                                           | `BIGINT`                          | `Int64`           | 1                |\n"
        "|                                           | `CHARACTER`                       | `String`          | 1                |\n"
        "|                                           | `BYTE`                            | `Int8`            | 1                |\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Import",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support importing the following Parquet data types:\n"
        "Parquet Decimal is currently not tested.\n"
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
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_DateUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.DateUTCAdjusted",
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
    level=5,
    num="4.3.3.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_TimestampUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimestampUTCAdjusted",
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
    level=5,
    num="4.3.3.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_TimeUTCAdjusted = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimeUTCAdjusted",
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
    level=5,
    num="4.3.3.3.3",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.NullValues",
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
    level=5,
    num="4.3.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nullable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nullable",
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
    level=5,
    num="4.3.3.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_LowCardinality = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.LowCardinality",
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
    level=5,
    num="4.3.3.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nested",
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
    level=5,
    num="4.3.3.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Unknown = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Unknown",
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
    level=5,
    num="4.3.3.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_Unsupported = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported",
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
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_Unsupported_ChunkedArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported.ChunkedArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet chunked arrays.\n" "\n"),
    link=None,
    level=4,
    num="4.3.4.2",
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
    level=5,
    num="4.3.4.3.1",
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
    level=5,
    num="4.3.4.4.1",
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
    level=5,
    num="4.3.4.5.1",
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
    level=5,
    num="4.3.4.6.1",
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
    level=5,
    num="4.3.4.7.1",
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
    level=5,
    num="4.3.4.8.1",
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
    level=4,
    num="4.3.5.1",
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
    level=4,
    num="4.3.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportNested",
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
    level=4,
    num="4.3.6.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support inserting arrays of nested structs from Parquet files into [ClickHouse] Nested columns when `input_format_parquet_import_nested` setting is set to `1`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.6.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_NotImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] Nested columns when\n"
        "`input_format_parquet_import_nested` setting is set to `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.6.4",
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
    level=4,
    num="4.3.6.5",
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
    level=4,
    num="4.3.6.6",
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
    level=4,
    num="4.3.7.1",
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
    level=5,
    num="4.3.8.1.1",
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
    level=5,
    num="4.3.8.2.1",
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
    level=5,
    num="4.3.8.3.1",
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
    level=5,
    num="4.3.8.4.1",
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
    level=5,
    num="4.3.8.5.1",
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
    num="4.3.8.7",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of\n"
        "nested structs into Nested tables. The default value SHALL be `0`.\n"
        "\n"
        "- `0` — Data can not be inserted into Nested columns as an array of structs.\n"
        "- `1` — Data can be inserted into Nested columns as an array of structs.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.9.1",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_CaseInsensitiveColumnMatching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching\n"
        "Parquet and ClickHouse columns. The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.9.2",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_AllowMissingColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.\n"
        "The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.9.3",
)

RQ_SRS_032_ClickHouse_Parquet_Import_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`\n"
        "to allow skipping unsupported types. The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.9.4",
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
    level=4,
    num="4.4.9.1",
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
    level=5,
    num="4.4.9.2.1",
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
    level=4,
    num="4.4.10.1",
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ExportNullable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ExportNullable",
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
    level=4,
    num="4.4.10.2",
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
    level=4,
    num="4.4.11.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nested",
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
    level=4,
    num="4.4.11.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_ChunkedColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.ChunkedColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support exporting chunked columns to Parquet files.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.4.12.1",
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
    level=3,
    num="4.4.13",
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
    level=3,
    num="4.4.14",
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
    num="4.4.15",
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
    num="4.4.16",
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
    level=5,
    num="4.4.17.1.1",
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
    level=5,
    num="4.4.17.2.1",
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
    level=5,
    num="4.4.17.3.1",
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
    level=5,
    num="4.4.17.4.1",
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
    level=5,
    num="4.4.17.5.1",
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
    num="4.4.17.7",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.\n"
        "The default value SHALL be `1000000`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.18.1",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.\n"
        "The default value SHALL be `0`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.18.2",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_StringAsFixedByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_fixed_string_as_fixed_byte_array` to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns. The default value SHALL be `1`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.18.3",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_ParquetVersion = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_version` to set the version of Parquet used in the output file.\n"
        "The default value SHALL be `2.latest`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.18.4",
)

RQ_SRS_032_ClickHouse_Parquet_Export_Settings_CompressionMethod = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_compression_method` to set the compression method used in the Parquet file.\n"
        "The default value SHALL be `lz4`.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.4.18.5",
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
    level=4,
    num="4.4.19.1",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support importing or exporting encrypted Parquet files.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
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
    level=3,
    num="4.6.1",
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
    level=4,
    num="4.7.1.1",
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
    level=4,
    num="4.7.2.1",
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
    level=4,
    num="4.7.3.1",
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
    level=4,
    num="4.7.4.1",
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
    level=4,
    num="4.7.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support importing or exporting Parquet files compressed using snapy.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.6.1.1",
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
    level=5,
    num="4.7.6.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Zstd = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support importing or exporting Parquet files compressed using zstd.\n"
        "\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.6.3.1",
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
    level=4,
    num="4.8.1.1",
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
    level=4,
    num="4.8.2.1",
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
    level=4,
    num="4.8.2.2",
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
        "FROM gcs('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.8.3.1",
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
    level=4,
    num="4.8.4.1",
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
    level=4,
    num="4.8.5.1",
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
    level=4,
    num="4.8.6.1",
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
    level=4,
    num="4.8.7.1",
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
    level=4,
    num="4.8.8.1",
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
    level=4,
    num="4.8.9.1",
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
    level=4,
    num="4.9.1.1",
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
    level=5,
    num="4.9.1.2.1",
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
    level=5,
    num="4.9.1.3.1",
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
    level=5,
    num="4.9.1.4.1",
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
    level=5,
    num="4.9.1.5.1",
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
    level=5,
    num="4.9.1.6.1",
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
    level=5,
    num="4.9.1.7.1",
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
    level=5,
    num="4.9.1.8.1",
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
    level=5,
    num="4.9.2.1.1",
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
    level=5,
    num="4.9.2.2.1",
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
    level=5,
    num="4.9.2.3.1",
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
    level=5,
    num="4.9.2.4.1",
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
    level=5,
    num="4.9.2.5.1",
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
    level=5,
    num="4.9.2.6.1",
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
    level=5,
    num="4.9.2.7.1",
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
    level=5,
    num="4.9.2.8.1",
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
    num="4.9.2.10",
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
    level=4,
    num="4.9.3.1",
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
    level=4,
    num="4.9.3.2",
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
    level=4,
    num="4.9.3.3",
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
    level=4,
    num="4.9.3.4",
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
    level=4,
    num="4.9.3.5",
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
    level=4,
    num="4.10.1.1",
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
    level=4,
    num="4.10.1.2",
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
    level=4,
    num="4.10.1.3",
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
    level=4,
    num="4.10.1.4",
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
    level=4,
    num="4.10.2.1",
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
    level=4,
    num="4.10.2.2",
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
    level=4,
    num="4.10.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_MissingMagicNumber = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber",
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
    level=3,
    num="4.11.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptFile = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile",
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
    level=3,
    num="4.11.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumn = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn",
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
    level=3,
    num="4.11.3",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageHeader = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader",
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
    level=3,
    num="4.11.4",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageData = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData",
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
    level=3,
    num="4.11.5",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues",
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
        "> \n"
    ),
    link=None,
    level=3,
    num="4.11.6",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Date = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Date",
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
    level=5,
    num="4.11.6.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Int = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Int",
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
    level=5,
    num="4.11.6.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_BigInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.BigInt",
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
    level=5,
    num="4.11.6.1.3",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_SmallInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.SmallInt",
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
    level=5,
    num="4.11.6.1.4",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TinyInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TinyInt",
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
    level=5,
    num="4.11.6.1.5",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UInt",
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
    level=5,
    num="4.11.6.1.6",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UBigInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UBigInt",
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
    level=5,
    num="4.11.6.1.7",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_USmallInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.USmallInt",
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
    level=5,
    num="4.11.6.1.8",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UTinyInt = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UTinyInt",
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
    level=5,
    num="4.11.6.1.9",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimestampUS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampUS",
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
    level=5,
    num="4.11.6.1.10",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimestampMS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampMS",
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
    level=5,
    num="4.11.6.1.11",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Bool = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Bool",
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
    level=5,
    num="4.11.6.1.12",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Float = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Float",
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
    level=5,
    num="4.11.6.1.13",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Double = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Double",
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
    level=5,
    num="4.11.6.1.14",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeMS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeMS",
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
    level=5,
    num="4.11.6.1.15",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeUS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeUS",
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
    level=5,
    num="4.11.6.1.16",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeNS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeNS",
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
    level=5,
    num="4.11.6.1.17",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_String = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.String",
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
    level=5,
    num="4.11.6.1.18",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Binary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Binary",
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
    level=5,
    num="4.11.6.1.19",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_FixedLengthByteArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.FixedLengthByteArray",
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
    level=5,
    num="4.11.6.1.20",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Decimal = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Decimal",
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
    level=5,
    num="4.11.6.1.21",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_List = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.List",
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
    level=5,
    num="4.11.6.1.22",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Struct = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Struct",
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
    level=5,
    num="4.11.6.1.23",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Map = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Map",
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
    level=5,
    num="4.11.6.1.24",
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptChecksum = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptChecksum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL output an error if the Parquet file's checksum is corrupted.\n"
        "\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/parquet/requirements/requirements.md\n"
        "[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/parquet/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=4,
    num="4.11.6.2",
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
        Heading(name="Feature Diagram", level=1, num="3"),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="Working With Parquet", level=2, num="4.1"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet", level=3, num="4.1.1"),
        Heading(name="Supported Parquet Versions", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.SupportedVersions", level=3, num="4.2.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal", level=3, num="4.2.2"
        ),
        Heading(name="Import from Parquet Files", level=2, num="4.3"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Import", level=4, num="4.3.2.1"),
        Heading(name="Auto Detect Parquet File When Importing", level=4, num="4.3.2.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat",
            level=5,
            num="4.3.2.2.1",
        ),
        Heading(name="Supported Datatypes", level=3, num="4.3.3"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.DataTypes", level=4, num="4.3.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Import",
            level=4,
            num="4.3.3.2",
        ),
        Heading(name="UTCAdjusted", level=4, num="4.3.3.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.DateUTCAdjusted",
            level=5,
            num="4.3.3.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimestampUTCAdjusted",
            level=5,
            num="4.3.3.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimeUTCAdjusted",
            level=5,
            num="4.3.3.3.3",
        ),
        Heading(name="Nullable", level=4, num="4.3.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.NullValues",
            level=5,
            num="4.3.3.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nullable",
            level=5,
            num="4.3.3.4.2",
        ),
        Heading(name="LowCardinality", level=4, num="4.3.3.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.LowCardinality",
            level=5,
            num="4.3.3.5.1",
        ),
        Heading(name="Nested", level=4, num="4.3.3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nested",
            level=5,
            num="4.3.3.6.1",
        ),
        Heading(name="UNKNOWN", level=4, num="4.3.3.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Unknown",
            level=5,
            num="4.3.3.7.1",
        ),
        Heading(name="Unsupported Datatypes", level=3, num="4.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported",
            level=4,
            num="4.3.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported.ChunkedArray",
            level=4,
            num="4.3.4.2",
        ),
        Heading(name="Projections", level=4, num="4.3.4.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Projections",
            level=5,
            num="4.3.4.3.1",
        ),
        Heading(name="Skip Columns", level=4, num="4.3.4.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns",
            level=5,
            num="4.3.4.4.1",
        ),
        Heading(name="Skip Values", level=4, num="4.3.4.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues",
            level=5,
            num="4.3.4.5.1",
        ),
        Heading(name="Auto Typecast", level=4, num="4.3.4.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast",
            level=5,
            num="4.3.4.6.1",
        ),
        Heading(name="Row Group Size", level=4, num="4.3.4.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize",
            level=5,
            num="4.3.4.7.1",
        ),
        Heading(name="Data Page Size", level=4, num="4.3.4.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize",
            level=5,
            num="4.3.4.8.1",
        ),
        Heading(name="Import Into New Table", level=3, num="4.3.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.NewTable", level=4, num="4.3.5.1"
        ),
        Heading(name="Import Nested Types", level=3, num="4.3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested",
            level=4,
            num="4.3.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportNested",
            level=4,
            num="4.3.6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested",
            level=4,
            num="4.3.6.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested",
            level=4,
            num="4.3.6.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested",
            level=4,
            num="4.3.6.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested",
            level=4,
            num="4.3.6.6",
        ),
        Heading(name="Import Chunked Columns", level=3, num="4.3.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns",
            level=4,
            num="4.3.7.1",
        ),
        Heading(name="Import Encoded", level=3, num="4.3.8"),
        Heading(name="Plain (Import)", level=4, num="4.3.8.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain",
            level=5,
            num="4.3.8.1.1",
        ),
        Heading(name="Run Length Encoding (Import)", level=4, num="4.3.8.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength",
            level=5,
            num="4.3.8.2.1",
        ),
        Heading(name="Delta (Import)", level=4, num="4.3.8.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta",
            level=5,
            num="4.3.8.3.1",
        ),
        Heading(name="Delta-length byte array (Import)", level=4, num="4.3.8.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray",
            level=5,
            num="4.3.8.4.1",
        ),
        Heading(name="Delta Strings (Import)", level=4, num="4.3.8.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings",
            level=5,
            num="4.3.8.5.1",
        ),
        Heading(name="Byte Stream Split (Import)", level=4, num="4.3.8.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit",
            level=4,
            num="4.3.8.7",
        ),
        Heading(name="Import Settings", level=3, num="4.3.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested",
            level=4,
            num="4.3.9.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching",
            level=4,
            num="4.3.9.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns",
            level=4,
            num="4.3.9.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
            level=4,
            num="4.3.9.4",
        ),
        Heading(name="Export from Parquet Files", level=2, num="4.4"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Export", level=4, num="4.4.9.1"),
        Heading(name="Auto Detect Parquet File When Exporting", level=4, num="4.4.9.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat",
            level=5,
            num="4.4.9.2.1",
        ),
        Heading(name="Supported Data types", level=3, num="4.4.10"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported",
            level=4,
            num="4.4.10.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.ExportNullable",
            level=4,
            num="4.4.10.2",
        ),
        Heading(name="Working With Nested Types Export", level=3, num="4.4.11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Nested", level=4, num="4.4.11.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nested",
            level=4,
            num="4.4.11.2",
        ),
        Heading(name="Exporting Chunked Columns", level=3, num="4.4.12"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.ChunkedColumns",
            level=4,
            num="4.4.12.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Export.Parquet.Join", level=3, num="4.4.13"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Union", level=3, num="4.4.14"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.View", level=3, num="4.4.15"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView",
            level=3,
            num="4.4.16",
        ),
        Heading(name="Export Encoded", level=3, num="4.4.17"),
        Heading(name="Plain (Export)", level=4, num="4.4.17.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain",
            level=5,
            num="4.4.17.1.1",
        ),
        Heading(name="Run Length Encoding (Export)", level=4, num="4.4.17.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength",
            level=5,
            num="4.4.17.2.1",
        ),
        Heading(name="Delta (Export)", level=4, num="4.4.17.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta",
            level=5,
            num="4.4.17.3.1",
        ),
        Heading(name="Delta-length byte array (Export)", level=4, num="4.4.17.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray",
            level=5,
            num="4.4.17.4.1",
        ),
        Heading(name="Delta Strings (Export)", level=4, num="4.4.17.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings",
            level=5,
            num="4.4.17.5.1",
        ),
        Heading(name="Byte Stream Split (Export)", level=4, num="4.4.17.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit",
            level=4,
            num="4.4.17.7",
        ),
        Heading(name="Export Settings", level=3, num="4.4.18"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize",
            level=4,
            num="4.4.18.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString",
            level=4,
            num="4.4.18.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray",
            level=4,
            num="4.4.18.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion",
            level=4,
            num="4.4.18.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod",
            level=4,
            num="4.4.18.5",
        ),
        Heading(name="Type Conversion", level=3, num="4.4.19"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction",
            level=4,
            num="4.4.19.1",
        ),
        Heading(name="Parquet Encryption", level=2, num="4.5"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Encryption", level=3, num="4.5.1"),
        Heading(name="DESCRIBE Parquet", level=2, num="4.6"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Structure", level=3, num="4.6.1"),
        Heading(name="Compression", level=2, num="4.7"),
        Heading(name="None", level=3, num="4.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.None",
            level=4,
            num="4.7.1.1",
        ),
        Heading(name="Gzip", level=3, num="4.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip",
            level=4,
            num="4.7.2.1",
        ),
        Heading(name="Brotli", level=3, num="4.7.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli",
            level=4,
            num="4.7.3.1",
        ),
        Heading(name="Lz4", level=3, num="4.7.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4", level=4, num="4.7.4.1"
        ),
        Heading(name="Lz4Raw", level=3, num="4.7.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw",
            level=4,
            num="4.7.5.1",
        ),
        Heading(name="Unsupported Compression", level=3, num="4.7.6"),
        Heading(name="Snappy", level=4, num="4.7.6.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy",
            level=5,
            num="4.7.6.1.1",
        ),
        Heading(name="Lzo", level=4, num="4.7.6.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo",
            level=5,
            num="4.7.6.2.1",
        ),
        Heading(name="Zstd", level=4, num="4.7.6.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd",
            level=5,
            num="4.7.6.3.1",
        ),
        Heading(name="Table Functions", level=2, num="4.8"),
        Heading(name="URL", level=3, num="4.8.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL",
            level=4,
            num="4.8.1.1",
        ),
        Heading(name="File", level=3, num="4.8.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File",
            level=4,
            num="4.8.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat",
            level=4,
            num="4.8.2.2",
        ),
        Heading(name="s3", level=3, num="4.8.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3",
            level=4,
            num="4.8.3.1",
        ),
        Heading(name="jdbc", level=3, num="4.8.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC",
            level=4,
            num="4.8.4.1",
        ),
        Heading(name="odbc", level=3, num="4.8.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC",
            level=4,
            num="4.8.5.1",
        ),
        Heading(name="hdfs", level=3, num="4.8.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS",
            level=4,
            num="4.8.6.1",
        ),
        Heading(name="remote", level=3, num="4.8.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote",
            level=4,
            num="4.8.7.1",
        ),
        Heading(name="mysql", level=3, num="4.8.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL",
            level=4,
            num="4.8.8.1",
        ),
        Heading(name="PostgreSQL", level=3, num="4.8.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL",
            level=4,
            num="4.8.9.1",
        ),
        Heading(name="Table Engines", level=2, num="4.9"),
        Heading(name="MergeTree", level=3, num="4.9.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree",
            level=4,
            num="4.9.1.1",
        ),
        Heading(name="ReplicatedMergeTree", level=4, num="4.9.1.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree",
            level=5,
            num="4.9.1.2.1",
        ),
        Heading(name="ReplacingMergeTree", level=4, num="4.9.1.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree",
            level=5,
            num="4.9.1.3.1",
        ),
        Heading(name="SummingMergeTree", level=4, num="4.9.1.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree",
            level=5,
            num="4.9.1.4.1",
        ),
        Heading(name="AggregatingMergeTree", level=4, num="4.9.1.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree",
            level=5,
            num="4.9.1.5.1",
        ),
        Heading(name="CollapsingMergeTree", level=4, num="4.9.1.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree",
            level=5,
            num="4.9.1.6.1",
        ),
        Heading(name="VersionedCollapsingMergeTree", level=4, num="4.9.1.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree",
            level=5,
            num="4.9.1.7.1",
        ),
        Heading(name="GraphiteMergeTree", level=4, num="4.9.1.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree",
            level=5,
            num="4.9.1.8.1",
        ),
        Heading(name="Integration Engines", level=3, num="4.9.2"),
        Heading(name="ODBC Engine", level=4, num="4.9.2.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC",
            level=5,
            num="4.9.2.1.1",
        ),
        Heading(name="JDBC Engine", level=4, num="4.9.2.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC",
            level=5,
            num="4.9.2.2.1",
        ),
        Heading(name="MySQL Engine", level=4, num="4.9.2.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL",
            level=5,
            num="4.9.2.3.1",
        ),
        Heading(name="MongoDB Engine", level=4, num="4.9.2.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB",
            level=5,
            num="4.9.2.4.1",
        ),
        Heading(name="HDFS Engine", level=4, num="4.9.2.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS",
            level=5,
            num="4.9.2.5.1",
        ),
        Heading(name="S3 Engine", level=4, num="4.9.2.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3",
            level=5,
            num="4.9.2.6.1",
        ),
        Heading(name="Kafka Engine", level=4, num="4.9.2.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka",
            level=5,
            num="4.9.2.7.1",
        ),
        Heading(name="EmbeddedRocksDB Engine", level=4, num="4.9.2.8"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB",
            level=5,
            num="4.9.2.8.1",
        ),
        Heading(name="PostgreSQL Engine", level=4, num="4.9.2.9"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL",
            level=4,
            num="4.9.2.10",
        ),
        Heading(name="Special Engines", level=3, num="4.9.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory",
            level=4,
            num="4.9.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed",
            level=4,
            num="4.9.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary",
            level=4,
            num="4.9.3.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File",
            level=4,
            num="4.9.3.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL",
            level=4,
            num="4.9.3.5",
        ),
        Heading(name="Metadata", level=2, num="4.10"),
        Heading(name="ParquetFormat", level=3, num="4.10.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat",
            level=4,
            num="4.10.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output",
            level=4,
            num="4.10.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content",
            level=4,
            num="4.10.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax",
            level=4,
            num="4.10.1.4",
        ),
        Heading(name="Metadata Types", level=3, num="4.10.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.File", level=4, num="4.10.2.1"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Column",
            level=4,
            num="4.10.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.Header",
            level=4,
            num="4.10.2.3",
        ),
        Heading(name="Error Recovery", level=2, num="4.11"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber",
            level=3,
            num="4.11.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile",
            level=3,
            num="4.11.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn",
            level=3,
            num="4.11.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader",
            level=3,
            num="4.11.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData",
            level=3,
            num="4.11.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues",
            level=3,
            num="4.11.6",
        ),
        Heading(name="List of Corrupt Column Values", level=4, num="4.11.6.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Date",
            level=5,
            num="4.11.6.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Int",
            level=5,
            num="4.11.6.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.BigInt",
            level=5,
            num="4.11.6.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.SmallInt",
            level=5,
            num="4.11.6.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TinyInt",
            level=5,
            num="4.11.6.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UInt",
            level=5,
            num="4.11.6.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UBigInt",
            level=5,
            num="4.11.6.1.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.USmallInt",
            level=5,
            num="4.11.6.1.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UTinyInt",
            level=5,
            num="4.11.6.1.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampUS",
            level=5,
            num="4.11.6.1.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampMS",
            level=5,
            num="4.11.6.1.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Bool",
            level=5,
            num="4.11.6.1.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Float",
            level=5,
            num="4.11.6.1.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Double",
            level=5,
            num="4.11.6.1.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeMS",
            level=5,
            num="4.11.6.1.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeUS",
            level=5,
            num="4.11.6.1.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeNS",
            level=5,
            num="4.11.6.1.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.String",
            level=5,
            num="4.11.6.1.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Binary",
            level=5,
            num="4.11.6.1.19",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.FixedLengthByteArray",
            level=5,
            num="4.11.6.1.20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Decimal",
            level=5,
            num="4.11.6.1.21",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.List",
            level=5,
            num="4.11.6.1.22",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Struct",
            level=5,
            num="4.11.6.1.23",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Map",
            level=5,
            num="4.11.6.1.24",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptChecksum",
            level=4,
            num="4.11.6.2",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet,
        RQ_SRS_032_ClickHouse_Parquet_SupportedVersions,
        RQ_SRS_032_ClickHouse_Parquet_ClickHouseLocal,
        RQ_SRS_032_ClickHouse_Parquet_Import,
        RQ_SRS_032_ClickHouse_Parquet_Import_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_Import,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_DateUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_TimestampUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_TimeUTCAdjusted,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_NullValues,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nullable,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_LowCardinality,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Nested,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportInto_Unknown,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_Unsupported,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_Unsupported_ChunkedArray,
        RQ_SRS_032_ClickHouse_Parquet_Import_Projections,
        RQ_SRS_032_ClickHouse_Parquet_Import_SkipColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_SkipValues,
        RQ_SRS_032_ClickHouse_Parquet_Import_AutoTypecast,
        RQ_SRS_032_ClickHouse_Parquet_Import_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Import_DataPageSize,
        RQ_SRS_032_ClickHouse_Parquet_Import_NewTable,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNested_NotImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_ArrayIntoNotNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Nested_NonArrayIntoNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_ChunkedColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Plain,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_RunLength,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Delta,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_DeltaStrings,
        RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_ByteStreamSplit,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Import_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_Export,
        RQ_SRS_032_ClickHouse_Parquet_Export_Outfile_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_Export_Datatypes_Supported,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ExportNullable,
        RQ_SRS_032_ClickHouse_Parquet_Export_Nested,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_Nested,
        RQ_SRS_032_ClickHouse_Parquet_Export_DataTypes_ChunkedColumns,
        RQ_SRS_032_ClickHouse_Export_Parquet_Join,
        RQ_SRS_032_ClickHouse_Parquet_Export_Union,
        RQ_SRS_032_ClickHouse_Parquet_Export_View,
        RQ_SRS_032_ClickHouse_Parquet_Export_Select_MaterializedView,
        RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Plain,
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
        RQ_SRS_032_ClickHouse_Parquet_Encryption,
        RQ_SRS_032_ClickHouse_Parquet_Structure,
        RQ_SRS_032_ClickHouse_Parquet_Compression_None,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Lzo,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Zstd,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File_AutoDetectParquetFileFormat,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgreSQL,
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
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadataFormat_Output,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_Content,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_File,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Column,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Header,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_MissingMagicNumber,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptFile,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumn,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageHeader,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageData,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Date,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Int,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_BigInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_SmallInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TinyInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UBigInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_USmallInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_UTinyInt,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimestampUS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimestampMS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Bool,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Float,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Double,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeMS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeUS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_TimeNS,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_String,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Binary,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_FixedLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Decimal,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_List,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Struct,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumnValues_Map,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptChecksum,
    ),
    content="""
# SRS032 ClickHouse Parquet Data Format
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Feature Diagram](#feature-diagram)
* 4 [Requirements](#requirements)
  * 4.1 [Working With Parquet](#working-with-parquet)
    * 4.1.1 [RQ.SRS-032.ClickHouse.Parquet](#rqsrs-032clickhouseparquet)
  * 4.2 [Supported Parquet Versions](#supported-parquet-versions)
    * 4.2.1 [RQ.SRS-032.ClickHouse.Parquet.SupportedVersions](#rqsrs-032clickhouseparquetsupportedversions)
    * 4.2.2 [RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal](#rqsrs-032clickhouseparquetclickhouselocal)
  * 4.3 [Import from Parquet Files](#import-from-parquet-files)
      * 4.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import](#rqsrs-032clickhouseparquetimport)
      * 4.3.2.2 [Auto Detect Parquet File When Importing](#auto-detect-parquet-file-when-importing)
        * 4.3.2.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquetimportautodetectparquetfileformat)
    * 4.3.3 [Supported Datatypes](#supported-datatypes)
      * 4.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes](#rqsrs-032clickhouseparquetdatatypes)
      * 4.3.3.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.Import](#rqsrs-032clickhouseparquetdatatypesimport)
      * 4.3.3.3 [UTCAdjusted](#utcadjusted)
        * 4.3.3.3.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.DateUTCAdjusted](#rqsrs-032clickhouseparquetdatatypesdateutcadjusted)
        * 4.3.3.3.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimestampUTCAdjusted](#rqsrs-032clickhouseparquetdatatypestimestamputcadjusted)
        * 4.3.3.3.3 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimeUTCAdjusted](#rqsrs-032clickhouseparquetdatatypestimeutcadjusted)
      * 4.3.3.4 [Nullable](#nullable)
        * 4.3.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.NullValues](#rqsrs-032clickhouseparquetdatatypesnullvalues)
        * 4.3.3.4.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nullable](#rqsrs-032clickhouseparquetdatatypesimportintonullable)
      * 4.3.3.5 [LowCardinality](#lowcardinality)
        * 4.3.3.5.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.LowCardinality](#rqsrs-032clickhouseparquetdatatypesimportintolowcardinality)
      * 4.3.3.6 [Nested](#nested)
        * 4.3.3.6.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nested](#rqsrs-032clickhouseparquetdatatypesimportintonested)
      * 4.3.3.7 [UNKNOWN](#unknown)
        * 4.3.3.7.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Unknown](#rqsrs-032clickhouseparquetdatatypesimportintounknown)
    * 4.3.4 [Unsupported Datatypes](#unsupported-datatypes)
      * 4.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported](#rqsrs-032clickhouseparquetdatatypesunsupported)
      * 4.3.4.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported.ChunkedArray](#rqsrs-032clickhouseparquetdatatypesunsupportedchunkedarray)
      * 4.3.4.3 [Projections](#projections)
        * 4.3.4.3.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Projections](#rqsrs-032clickhouseparquetimportprojections)
      * 4.3.4.4 [Skip Columns](#skip-columns)
        * 4.3.4.4.1 [RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns](#rqsrs-032clickhouseparquetimportskipcolumns)
      * 4.3.4.5 [Skip Values](#skip-values)
        * 4.3.4.5.1 [RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues](#rqsrs-032clickhouseparquetimportskipvalues)
      * 4.3.4.6 [Auto Typecast](#auto-typecast)
        * 4.3.4.6.1 [RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast](#rqsrs-032clickhouseparquetimportautotypecast)
      * 4.3.4.7 [Row Group Size](#row-group-size)
        * 4.3.4.7.1 [RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize](#rqsrs-032clickhouseparquetimportrowgroupsize)
      * 4.3.4.8 [Data Page Size](#data-page-size)
        * 4.3.4.8.1 [RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize](#rqsrs-032clickhouseparquetimportdatapagesize)
    * 4.3.5 [Import Into New Table](#import-into-new-table)
      * 4.3.5.1 [RQ.SRS-032.ClickHouse.Parquet.Import.NewTable](#rqsrs-032clickhouseparquetimportnewtable)
    * 4.3.6 [Import Nested Types](#import-nested-types)
      * 4.3.6.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested](#rqsrs-032clickhouseparquetimportnestedarrayintonested)
      * 4.3.6.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportNested](#rqsrs-032clickhouseparquetdatatypesimportnested)
      * 4.3.6.3 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested](#rqsrs-032clickhouseparquetimportnestedarrayintonestedimportnested)
      * 4.3.6.4 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested](#rqsrs-032clickhouseparquetimportnestedarrayintonestednotimportnested)
      * 4.3.6.5 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested](#rqsrs-032clickhouseparquetimportnestedarrayintonotnested)
      * 4.3.6.6 [RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested](#rqsrs-032clickhouseparquetimportnestednonarrayintonested)
    * 4.3.7 [Import Chunked Columns](#import-chunked-columns)
      * 4.3.7.1 [RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns](#rqsrs-032clickhouseparquetimportchunkedcolumns)
    * 4.3.8 [Import Encoded](#import-encoded)
      * 4.3.8.1 [Plain (Import)](#plain-import)
        * 4.3.8.1.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain](#rqsrs-032clickhouseparquetimportencodingplain)
      * 4.3.8.2 [Run Length Encoding (Import)](#run-length-encoding-import)
        * 4.3.8.2.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength](#rqsrs-032clickhouseparquetimportencodingrunlength)
      * 4.3.8.3 [Delta (Import)](#delta-import)
        * 4.3.8.3.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta](#rqsrs-032clickhouseparquetimportencodingdelta)
      * 4.3.8.4 [Delta-length byte array (Import)](#delta-length-byte-array-import)
        * 4.3.8.4.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray](#rqsrs-032clickhouseparquetimportencodingdeltalengthbytearray)
      * 4.3.8.5 [Delta Strings (Import)](#delta-strings-import)
        * 4.3.8.5.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings](#rqsrs-032clickhouseparquetimportencodingdeltastrings)
      * 4.3.8.6 [Byte Stream Split (Import)](#byte-stream-split-import)
      * 4.3.8.7 [RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit](#rqsrs-032clickhouseparquetimportencodingbytestreamsplit)
    * 4.3.9 [Import Settings](#import-settings)
      * 4.3.9.1 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested](#rqsrs-032clickhouseparquetimportsettingsimportnested)
      * 4.3.9.2 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetimportsettingscaseinsensitivecolumnmatching)
      * 4.3.9.3 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns](#rqsrs-032clickhouseparquetimportsettingsallowmissingcolumns)
      * 4.3.9.4 [RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetimportsettingsskipcolumnswithunsupportedtypesinschemainference)
  * 4.4 [Export from Parquet Files](#export-from-parquet-files)
      * 4.4.9.1 [RQ.SRS-032.ClickHouse.Parquet.Export](#rqsrs-032clickhouseparquetexport)
      * 4.4.9.2 [Auto Detect Parquet File When Exporting](#auto-detect-parquet-file-when-exporting)
        * 4.4.9.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquetexportoutfileautodetectparquetfileformat)
    * 4.4.10 [Supported Data types](#supported-data-types)
      * 4.4.10.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported](#rqsrs-032clickhouseparquetexportdatatypessupported)
      * 4.4.10.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ExportNullable](#rqsrs-032clickhouseparquetdatatypesexportnullable)
    * 4.4.11 [Working With Nested Types Export](#working-with-nested-types-export)
      * 4.4.11.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Nested](#rqsrs-032clickhouseparquetexportnested)
      * 4.4.11.2 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nested](#rqsrs-032clickhouseparquetexportdatatypesnested)
    * 4.4.12 [Exporting Chunked Columns](#exporting-chunked-columns)
      * 4.4.12.1 [RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.ChunkedColumns](#rqsrs-032clickhouseparquetexportdatatypeschunkedcolumns)
    * 4.4.13 [RQ.SRS-032.ClickHouse.Export.Parquet.Join](#rqsrs-032clickhouseexportparquetjoin)
    * 4.4.14 [RQ.SRS-032.ClickHouse.Parquet.Export.Union](#rqsrs-032clickhouseparquetexportunion)
    * 4.4.15 [RQ.SRS-032.ClickHouse.Parquet.Export.View](#rqsrs-032clickhouseparquetexportview)
    * 4.4.16 [RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView](#rqsrs-032clickhouseparquetexportselectmaterializedview)
    * 4.4.17 [Export Encoded](#export-encoded)
      * 4.4.17.1 [Plain (Export)](#plain-export)
        * 4.4.17.1.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain](#rqsrs-032clickhouseparquetexportencodingplain)
      * 4.4.17.2 [Run Length Encoding (Export)](#run-length-encoding-export)
        * 4.4.17.2.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength](#rqsrs-032clickhouseparquetexportencodingrunlength)
      * 4.4.17.3 [Delta (Export)](#delta-export)
        * 4.4.17.3.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta](#rqsrs-032clickhouseparquetexportencodingdelta)
      * 4.4.17.4 [Delta-length byte array (Export)](#delta-length-byte-array-export)
        * 4.4.17.4.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray](#rqsrs-032clickhouseparquetexportencodingdeltalengthbytearray)
      * 4.4.17.5 [Delta Strings (Export)](#delta-strings-export)
        * 4.4.17.5.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings](#rqsrs-032clickhouseparquetexportencodingdeltastrings)
      * 4.4.17.6 [Byte Stream Split (Export)](#byte-stream-split-export)
      * 4.4.17.7 [RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit](#rqsrs-032clickhouseparquetexportencodingbytestreamsplit)
    * 4.4.18 [Export Settings](#export-settings)
      * 4.4.18.1 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize](#rqsrs-032clickhouseparquetexportsettingsrowgroupsize)
      * 4.4.18.2 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString](#rqsrs-032clickhouseparquetexportsettingsstringasstring)
      * 4.4.18.3 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray](#rqsrs-032clickhouseparquetexportsettingsstringasfixedbytearray)
      * 4.4.18.4 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion](#rqsrs-032clickhouseparquetexportsettingsparquetversion)
      * 4.4.18.5 [RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod](#rqsrs-032clickhouseparquetexportsettingscompressionmethod)
    * 4.4.19 [Type Conversion](#type-conversion)
      * 4.4.19.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction](#rqsrs-032clickhouseparquetdatatypestypeconversionfunction)
  * 4.5 [Parquet Encryption](#parquet-encryption)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption](#rqsrs-032clickhouseparquetencryption)
  * 4.6 [DESCRIBE Parquet](#describe-parquet)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.Structure](#rqsrs-032clickhouseparquetstructure)
  * 4.7 [Compression](#compression)
    * 4.7.1 [None](#none)
      * 4.7.1.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.None](#rqsrs-032clickhouseparquetcompressionnone)
    * 4.7.2 [Gzip](#gzip)
      * 4.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip](#rqsrs-032clickhouseparquetcompressiongzip)
    * 4.7.3 [Brotli](#brotli)
      * 4.7.3.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli](#rqsrs-032clickhouseparquetcompressionbrotli)
    * 4.7.4 [Lz4](#lz4)
      * 4.7.4.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4](#rqsrs-032clickhouseparquetcompressionlz4)
    * 4.7.5 [Lz4Raw](#lz4raw)
      * 4.7.5.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw](#rqsrs-032clickhouseparquetcompressionlz4raw)
    * 4.7.6 [Unsupported Compression](#unsupported-compression)
      * 4.7.6.1 [Snappy](#snappy)
        * 4.7.6.1.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy](#rqsrs-032clickhouseparquetunsupportedcompressionsnappy)
      * 4.7.6.2 [Lzo](#lzo)
        * 4.7.6.2.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo](#rqsrs-032clickhouseparquetunsupportedcompressionlzo)
      * 4.7.6.3 [Zstd](#zstd)
        * 4.7.6.3.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd](#rqsrs-032clickhouseparquetunsupportedcompressionzstd)
  * 4.8 [Table Functions](#table-functions)
    * 4.8.1 [URL](#url)
      * 4.8.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL](#rqsrs-032clickhouseparquettablefunctionsurl)
    * 4.8.2 [File](#file)
      * 4.8.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File](#rqsrs-032clickhouseparquettablefunctionsfile)
      * 4.8.2.2 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat](#rqsrs-032clickhouseparquettablefunctionsfileautodetectparquetfileformat)
    * 4.8.3 [s3](#s3)
      * 4.8.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3](#rqsrs-032clickhouseparquettablefunctionss3)
    * 4.8.4 [jdbc](#jdbc)
      * 4.8.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC](#rqsrs-032clickhouseparquettablefunctionsjdbc)
    * 4.8.5 [odbc](#odbc)
      * 4.8.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC](#rqsrs-032clickhouseparquettablefunctionsodbc)
    * 4.8.6 [hdfs](#hdfs)
      * 4.8.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS](#rqsrs-032clickhouseparquettablefunctionshdfs)
    * 4.8.7 [remote](#remote)
      * 4.8.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote](#rqsrs-032clickhouseparquettablefunctionsremote)
    * 4.8.8 [mysql](#mysql)
      * 4.8.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL](#rqsrs-032clickhouseparquettablefunctionsmysql)
    * 4.8.9 [PostgreSQL](#postgresql)
      * 4.8.9.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL](#rqsrs-032clickhouseparquettablefunctionspostgresql)
  * 4.9 [Table Engines](#table-engines)
    * 4.9.1 [MergeTree](#mergetree)
      * 4.9.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree](#rqsrs-032clickhouseparquettableenginesmergetreemergetree)
      * 4.9.1.2 [ReplicatedMergeTree](#replicatedmergetree)
        * 4.9.1.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplicatedmergetree)
      * 4.9.1.3 [ReplacingMergeTree](#replacingmergetree)
        * 4.9.1.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplacingmergetree)
      * 4.9.1.4 [SummingMergeTree](#summingmergetree)
        * 4.9.1.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreesummingmergetree)
      * 4.9.1.5 [AggregatingMergeTree](#aggregatingmergetree)
        * 4.9.1.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeaggregatingmergetree)
      * 4.9.1.6 [CollapsingMergeTree](#collapsingmergetree)
        * 4.9.1.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreecollapsingmergetree)
      * 4.9.1.7 [VersionedCollapsingMergeTree](#versionedcollapsingmergetree)
        * 4.9.1.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeversionedcollapsingmergetree)
      * 4.9.1.8 [GraphiteMergeTree](#graphitemergetree)
        * 4.9.1.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreegraphitemergetree)
    * 4.9.2 [Integration Engines](#integration-engines)
      * 4.9.2.1 [ODBC Engine](#odbc-engine)
        * 4.9.2.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquettableenginesintegrationodbc)
      * 4.9.2.2 [JDBC Engine](#jdbc-engine)
        * 4.9.2.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquettableenginesintegrationjdbc)
      * 4.9.2.3 [MySQL Engine](#mysql-engine)
        * 4.9.2.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquettableenginesintegrationmysql)
      * 4.9.2.4 [MongoDB Engine](#mongodb-engine)
        * 4.9.2.4.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquettableenginesintegrationmongodb)
      * 4.9.2.5 [HDFS Engine](#hdfs-engine)
        * 4.9.2.5.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquettableenginesintegrationhdfs)
      * 4.9.2.6 [S3 Engine](#s3-engine)
        * 4.9.2.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3](#rqsrs-032clickhouseparquettableenginesintegrations3)
      * 4.9.2.7 [Kafka Engine](#kafka-engine)
        * 4.9.2.7.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquettableenginesintegrationkafka)
      * 4.9.2.8 [EmbeddedRocksDB Engine](#embeddedrocksdb-engine)
        * 4.9.2.8.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquettableenginesintegrationembeddedrocksdb)
      * 4.9.2.9 [PostgreSQL Engine](#postgresql-engine)
      * 4.9.2.10 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquettableenginesintegrationpostgresql)
    * 4.9.3 [Special Engines](#special-engines)
      * 4.9.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory](#rqsrs-032clickhouseparquettableenginesspecialmemory)
      * 4.9.3.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquettableenginesspecialdistributed)
      * 4.9.3.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquettableenginesspecialdictionary)
      * 4.9.3.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File](#rqsrs-032clickhouseparquettableenginesspecialfile)
      * 4.9.3.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL](#rqsrs-032clickhouseparquettableenginesspecialurl)
  * 4.10 [Metadata](#metadata)
    * 4.10.1 [ParquetFormat](#parquetformat)
      * 4.10.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat](#rqsrs-032clickhouseparquetmetadataparquetmetadataformat)
      * 4.10.1.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output](#rqsrs-032clickhouseparquetmetadataparquetmetadataformatoutput)
      * 4.10.1.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content](#rqsrs-032clickhouseparquetmetadataparquetmetadatacontent)
      * 4.10.1.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax](#rqsrs-032clickhouseparquetmetadataparquetmetadataminmax)
    * 4.10.2 [Metadata Types](#metadata-types)
      * 4.10.2.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.File](#rqsrs-032clickhouseparquetmetadatafile)
      * 4.10.2.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Column](#rqsrs-032clickhouseparquetmetadatacolumn)
      * 4.10.2.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Header](#rqsrs-032clickhouseparquetmetadataheader)
  * 4.11 [Error Recovery](#error-recovery)
    * 4.11.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber](#rqsrs-032clickhouseparquetmetadataerrorrecoverymissingmagicnumber)
    * 4.11.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptfile)
    * 4.11.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumn)
    * 4.11.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptpageheader)
    * 4.11.5 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptpagedata)
    * 4.11.6 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvalues)
      * 4.11.6.1 [List of Corrupt Column Values](#list-of-corrupt-column-values)
        * 4.11.6.1.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Date](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesdate)
        * 4.11.6.1.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Int](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesint)
        * 4.11.6.1.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.BigInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesbigint)
        * 4.11.6.1.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.SmallInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluessmallint)
        * 4.11.6.1.5 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TinyInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestinyint)
        * 4.11.6.1.6 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesuint)
        * 4.11.6.1.7 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UBigInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesubigint)
        * 4.11.6.1.8 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.USmallInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesusmallint)
        * 4.11.6.1.9 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UTinyInt](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesutinyint)
        * 4.11.6.1.10 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampUS](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestimestampus)
        * 4.11.6.1.11 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampMS](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestimestampms)
        * 4.11.6.1.12 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Bool](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesbool)
        * 4.11.6.1.13 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Float](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesfloat)
        * 4.11.6.1.14 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Double](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesdouble)
        * 4.11.6.1.15 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeMS](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestimems)
        * 4.11.6.1.16 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeUS](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestimeus)
        * 4.11.6.1.17 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeNS](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluestimens)
        * 4.11.6.1.18 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.String](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesstring)
        * 4.11.6.1.19 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Binary](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesbinary)
        * 4.11.6.1.20 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.FixedLengthByteArray](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesfixedlengthbytearray)
        * 4.11.6.1.21 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Decimal](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesdecimal)
        * 4.11.6.1.22 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.List](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvalueslist)
        * 4.11.6.1.23 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Struct](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesstruct)
        * 4.11.6.1.24 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Map](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumnvaluesmap)
      * 4.11.6.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptChecksum](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptchecksum)


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

## Feature Diagram

```mermaid
flowchart TB;
    subgraph Overhead[Parquet]
        direction TB;
        subgraph Sources[Source of data]
            direction TB;   
            MySQL

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
Input_settings --> ClickHouse -- Read From ClickHouse --> Output_settings --> Parquet_File_out
Parquet_File_in --> Corrupted
CorruptedNo --> Input_settings

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

## Requirements

### Working With Parquet

#### RQ.SRS-032.ClickHouse.Parquet
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

### Supported Parquet Versions

#### RQ.SRS-032.ClickHouse.Parquet.SupportedVersions
version: 1.0

[ClickHouse] SHALL support importing Parquet files with the following versions: `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.4.0`, `2.6.0`, `2.7.0`, `2.8.0`, `2.9.0`.

#### RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal
version: 1.0

[ClickHouse] SHALL support the usage of `clickhouse-local` with `Parquet` data format.

### Import from Parquet Files

##### RQ.SRS-032.ClickHouse.Parquet.Import
version: 1.0

[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to
read data from Parquet files and insert data into tables or table functions.

```sql
INSERT INTO sometable
FROM INFILE 'data.parquet' FORMAT Parquet;
```

##### Auto Detect Parquet File When Importing

###### RQ.SRS-032.ClickHouse.Parquet.Import.AutoDetectParquetFileFormat
version: 1.0

[ClickHouse] SHALL support automatically detecting Parquet file format based on 
when using INFILE clause without explicitly specifying the format setting.

```sql
INSERT INTO sometable
FROM INFILE 'data.parquet';
```

#### Supported Datatypes

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes
version: 1.0

[ClickHouse] SHALL support importing the Parquet files with the following datatypes and converting them into corresponding ClickHouse columns as described in the table.

The conversion MAY not be possible between some datatypes.
>
>For example,
>
>`Bool` -> `IPv6`

| Parquet to ClickHouse supported Datatypes | ClickHouse Datatype Family        | alias_to Datatype | case_insensitive |
|-------------------------------------------|-----------------------------------|-------------------|------------------|
|                                           | `JSON`                            |                   | 1                |
|                                           | `Polygon`                         |                   | 0                |
|                                           | `Ring`                            |                   | 0                |
|                                           | `Point`                           |                   | 0                |
|                                           | `SimpleAggregateFunction`         |                   | 0                |
|                                           | `IntervalQuarter`                 |                   | 0                |
|                                           | `IntervalMonth`                   |                   | 0                |
|                                           | `Int64`                           |                   | 0                |
|                                           | `IntervalDay`                     |                   | 0                |
|                                           | `IntervalHour`                    |                   | 0                |
|                                           | `IPv4`                            |                   | 0                |
|                                           | `IntervalSecond`                  |                   | 0                |
|                                           | `LowCardinality`                  |                   | 0                |
|                                           | `Int16`                           |                   | 0                |
|                                           | `UInt256`                         |                   | 0                |
|                                           | `AggregateFunction`               |                   | 0                |
|                                           | `MultiPolygon`                    |                   | 0                |
|                                           | `IPv6`                            |                   | 0                |
|                                           | `Nothing`                         |                   | 0                |
|                                           | `Decimal256`                      |                   | 1                |
|                                           | `Tuple`                           |                   | 0                |
|                                           | `Array`                           |                   | 0                |
|                                           | `IntervalMicrosecond`             |                   | 0                |
|                                           | `Bool`                            |                   | 1                |
|                                           | `Enum16`                          |                   | 0                |
|                                           | `IntervalMinute`                  |                   | 0                |
|                                           | `FixedString`                     |                   | 0                |
|                                           | `String`                          |                   | 0                |
|                                           | `DateTime`                        |                   | 1                |
|                                           | `Object`                          |                   | 0                |
|                                           | `Map`                             |                   | 0                |
|                                           | `UUID`                            |                   | 0                |
|                                           | `Decimal64`                       |                   | 1                |
|                                           | `Nullable`                        |                   | 0                |
|                                           | `Enum`                            |                   | 1                |
|                                           | `Int32`                           |                   | 0                |
|                                           | `UInt8`                           |                   | 0                |
|                                           | `Date`                            |                   | 1                |
|                                           | `Decimal32`                       |                   | 1                |
|                                           | `UInt128`                         |                   | 0                |
|                                           | `Float64`                         |                   | 0                |
|                                           | `Nested`                          |                   | 0                |
|                                           | `UInt16`                          |                   | 0                |
|                                           | `IntervalMillisecond`             |                   | 0                |
|                                           | `Int128`                          |                   | 0                |
|                                           | `Decimal128`                      |                   | 1                |
|                                           | `Int8`                            |                   | 0                |
|                                           | `Decimal`                         |                   | 1                |
|                                           | `Int256`                          |                   | 0                |
|                                           | `DateTime64`                      |                   | 1                |
|                                           | `Enum8`                           |                   | 0                |
|                                           | `DateTime32`                      |                   | 1                |
|                                           | `Date32`                          |                   | 1                |
|                                           | `IntervalWeek`                    |                   | 0                |
|                                           | `UInt64`                          |                   | 0                |
|                                           | `IntervalNanosecond`              |                   | 0                |
|                                           | `IntervalYear`                    |                   | 0                |
|                                           | `UInt32`                          |                   | 0                |
|                                           | `Float32`                         |                   | 0                |
|                                           | `bool`                            | `Bool`            | 1                |
|                                           | `INET6`                           | `IPv6`            | 1                |
|                                           | `INET4`                           | `IPv4`            | 1                |
|                                           | `ENUM`                            | `Enum`            | 1                |
|                                           | `BINARY`                          | `FixedString`     | 1                |
|                                           | `GEOMETRY`                        | `String`          | 1                |
|                                           | `NATIONAL CHAR VARYING`           | `String`          | 1                |
|                                           | `BINARY VARYING`                  | `String`          | 1                |
|                                           | `NCHAR LARGE OBJECT`              | `String`          | 1                |
|                                           | `NATIONAL CHARACTER VARYING`      | `String`          | 1                |
|                                           | `boolean`                         | `Bool`            | 1                |
|                                           | `NATIONAL CHARACTER LARGE OBJECT` | `String`          | 1                |
|                                           | `NATIONAL CHARACTER`              | `String`          | 1                |
|                                           | `NATIONAL CHAR`                   | `String`          | 1                |
|                                           | `CHARACTER VARYING`               | `String`          | 1                |
|                                           | `LONGBLOB`                        | `String`          | 1                |
|                                           | `TINYBLOB`                        | `String`          | 1                |
|                                           | `MEDIUMTEXT`                      | `String`          | 1                |
|                                           | `TEXT`                            | `String`          | 1                |
|                                           | `VARCHAR2`                        | `String`          | 1                |
|                                           | `CHARACTER LARGE OBJECT`          | `String`          | 1                |
|                                           | `DOUBLE PRECISION`                | `Float64`         | 1                |
|                                           | `LONGTEXT`                        | `String`          | 1                |
|                                           | `NVARCHAR`                        | `String`          | 1                |
|                                           | `INT1 UNSIGNED`                   | `UInt8`           | 1                |
|                                           | `VARCHAR`                         | `String`          | 1                |
|                                           | `CHAR VARYING`                    | `String`          | 1                |
|                                           | `MEDIUMBLOB`                      | `String`          | 1                |
|                                           | `NCHAR`                           | `String`          | 1                |
|                                           | `VARBINARY`                       | `String`          | 1                |
|                                           | `CHAR`                            | `String`          | 1                |
|                                           | `SMALLINT UNSIGNED`               | `UInt16`          | 1                |
|                                           | `TIMESTAMP`                       | `DateTime`        | 1                |
|                                           | `FIXED`                           | `Decimal`         | 1                |
|                                           | `TINYTEXT`                        | `String`          | 1                |
|                                           | `NUMERIC`                         | `Decimal`         | 1                |
|                                           | `DEC`                             | `Decimal`         | 1                |
|                                           | `TIME`                            | `Int64`           | 1                |
|                                           | `FLOAT`                           | `Float32`         | 1                |
|                                           | `SET`                             | `UInt64`          | 1                |
|                                           | `TINYINT UNSIGNED`                | `UInt8`           | 1                |
|                                           | `INTEGER UNSIGNED`                | `UInt32`          | 1                |
|                                           | `INT UNSIGNED`                    | `UInt32`          | 1                |
|                                           | `CLOB`                            | `String`          | 1                |
|                                           | `MEDIUMINT UNSIGNED`              | `UInt32`          | 1                |
|                                           | `BLOB`                            | `String`          | 1                |
|                                           | `REAL`                            | `Float32`         | 1                |
|                                           | `SMALLINT`                        | `Int16`           | 1                |
|                                           | `INTEGER SIGNED`                  | `Int32`           | 1                |
|                                           | `NCHAR VARYING`                   | `String`          | 1                |
|                                           | `INT SIGNED`                      | `Int32`           | 1                |
|                                           | `TINYINT SIGNED`                  | `Int8`            | 1                |
|                                           | `BIGINT SIGNED`                   | `Int64`           | 1                |
|                                           | `BINARY LARGE OBJECT`             | `String`          | 1                |
|                                           | `SMALLINT SIGNED`                 | `Int16`           | 1                |
|                                           | `YEAR`                            | `UInt16`          | 1                |
|                                           | `MEDIUMINT`                       | `Int32`           | 1                |
|                                           | `INTEGER`                         | `Int32`           | 1                |
|                                           | `INT1 SIGNED`                     | `Int8`            | 1                |
|                                           | `BIT`                             | `UInt64`          | 1                |
|                                           | `BIGINT UNSIGNED`                 | `UInt64`          | 1                |
|                                           | `BYTEA`                           | `String`          | 1                |
|                                           | `INT`                             | `Int32`           | 1                |
|                                           | `SINGLE`                          | `Float32`         | 1                |
|                                           | `MEDIUMINT SIGNED`                | `Int32`           | 1                |
|                                           | `DOUBLE`                          | `Float64`         | 1                |
|                                           | `INT1`                            | `Int8`            | 1                |
|                                           | `CHAR LARGE OBJECT`               | `String`          | 1                |
|                                           | `TINYINT`                         | `Int8`            | 1                |
|                                           | `BIGINT`                          | `Int64`           | 1                |
|                                           | `CHARACTER`                       | `String`          | 1                |
|                                           | `BYTE`                            | `Int8`            | 1                |


##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.Import
version:1.0

[ClickHouse] SHALL support importing the following Parquet data types:
Parquet Decimal is currently not tested.

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


##### UTCAdjusted

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.DateUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `DATE` Parquet datatype with `isAdjustedToUTC = true`.

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimestampUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `TIMESTAMP` Parquet datatype with `isAdjustedToUTC = true`.

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.TimeUTCAdjusted
version:1.0

[ClickHouse] SHALL support importing `TIME` Parquet datatype with `isAdjustedToUTC = true`.

##### Nullable

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.NullValues
version:1.0

[ClickHouse] SHALL support importing columns that have `Null` values in Parquet files. If the target [ClickHouse] column is not `Nullable` then the `Null` value should be converted to the default values for the target column datatype.

For example, if the target column has `Int32`, then the `Null` value will be replaced with `0`.

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nullable
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `Nullable` datatype columns.

##### LowCardinality

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.LowCardinality
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `LowCardinality` datatype columns.

##### Nested

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Nested
version:1.0

[ClickHouse] SHALL support importing Parquet files into target table's `Nested` datatype columns.

##### UNKNOWN

###### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportInto.Unknown
version:1.0

[ClickHouse] SHALL support importing Parquet files with `UNKNOWN` logical type.

The example as to why the Parquet might have an `UNKNOWN` types is as follows,

> Sometimes, when discovering the schema of existing data, values are always null and there's no type information. 
> The UNKNOWN type can be used to annotate a column that is always null. (Similar to Null type in Avro and Arrow)

#### Unsupported Datatypes

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported
version:1.0

[ClickHouse] MAY not support the following Parquet types:

- `Time32`
- `Fixed_Size_Binary`
- `JSON`
- `UUID`
- `ENUM`

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.Unsupported.ChunkedArray
version:1.0

[ClickHouse] MAY not support Parquet chunked arrays.

##### Projections

###### RQ.SRS-032.ClickHouse.Parquet.Import.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

##### Skip Columns

###### RQ.SRS-032.ClickHouse.Parquet.Import.SkipColumns
version: 1.0

[ClickHouse] SHALL support skipping unexistent columns when importing from Parquet files.

##### Skip Values

###### RQ.SRS-032.ClickHouse.Parquet.Import.SkipValues
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

##### Auto Typecast

###### RQ.SRS-032.ClickHouse.Parquet.Import.AutoTypecast
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

##### Row Group Size

###### RQ.SRS-032.ClickHouse.Parquet.Import.RowGroupSize
version: 1.0

[ClickHouse] SHALL support importing Parquet files with different Row Group Sizes.

As described in https://parquet.apache.org/docs/file-format/configurations/#row-group-size,

> We recommend large row groups (512MB - 1GB). Since an entire row group might need to be read, 
> we want it to completely fit on one HDFS block.

##### Data Page Size

###### RQ.SRS-032.ClickHouse.Parquet.Import.DataPageSize
version: 1.0

[ClickHouse] SHALL support importing Parquet files with different Data Page Sizes.

As described in https://parquet.apache.org/docs/file-format/configurations/#data-page--size,

> Note: for sequential scans, it is not expected to read a page at a time; this is not the IO chunk. We recommend 8KB for page sizes.


#### Import Into New Table

##### RQ.SRS-032.ClickHouse.Parquet.Import.NewTable
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

#### Import Nested Types

##### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested
version: 1.0

[ClickHouse] SHALL support importing nested columns from the Parquet file.

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ImportNested
version:1.0

[ClickHouse] SHALL support importing nested: `Array`, `Tuple` and `Map` datatypes from Parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.ImportNested
version: 1.0

[ClickHouse] SHALL support inserting arrays of nested structs from Parquet files into [ClickHouse] Nested columns when `input_format_parquet_import_nested` setting is set to `1`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNested.NotImportNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] Nested columns when
`input_format_parquet_import_nested` setting is set to `0`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.ArrayIntoNotNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert arrays of nested structs from Parquet files into [ClickHouse] not Nested columns.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Nested.NonArrayIntoNested
version: 1.0

[ClickHouse] SHALL return an error when trying to insert datatypes other than arrays of nested structs from Parquet files into [ClickHouse] Nested columns.

#### Import Chunked Columns

##### RQ.SRS-032.ClickHouse.Parquet.Import.ChunkedColumns
version: 1.0

[ClickHouse] SHALL support importing Parquet files with chunked columns.

#### Import Encoded

##### Plain (Import)

###### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Plain
version: 1.0

[ClickHouse] SHALL support importing `Plain` encoded Parquet files.

##### Run Length Encoding (Import)

###### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.RunLength
version: 1.0

[ClickHouse] SHALL support importing `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.

##### Delta (Import)

###### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.Delta
version: 1.0

[ClickHouse] SHALL support importing `Delta Encoding` encoded Parquet files.

##### Delta-length byte array (Import)

###### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaLengthByteArray
version: 1.0

[ClickHouse] SHALL support importing `Delta-length byte array` encoded Parquet files.

##### Delta Strings (Import)

###### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.DeltaStrings
version: 1.0

[ClickHouse] SHALL support importing `Delta Strings` encoded Parquet files.

##### Byte Stream Split (Import)

##### RQ.SRS-032.ClickHouse.Parquet.Import.Encoding.ByteStreamSplit
version: 1.0

[ClickHouse] SHALL support importing `Byte Stream Split` encoded Parquet files.

#### Import Settings

##### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables. The default value SHALL be `0`.

- `0` — Data can not be inserted into Nested columns as an array of structs.
- `1` — Data can be inserted into Nested columns as an array of structs.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns. The default value SHALL be `0`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.
The default value SHALL be `0`.

##### RQ.SRS-032.ClickHouse.Parquet.Import.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`
to allow skipping unsupported types. The default value SHALL be `0`.

### Export from Parquet Files

##### RQ.SRS-032.ClickHouse.Parquet.Export
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

##### Auto Detect Parquet File When Exporting

###### RQ.SRS-032.ClickHouse.Parquet.Export.Outfile.AutoDetectParquetFileFormat
version: 1.0


[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using OUTFILE clause without explicitly specifying the format setting.

```sql
SELECT *
FROM sometable
INTO OUTFILE 'export.parquet'
```

#### Supported Data types

##### RQ.SRS-032.ClickHouse.Parquet.Export.Datatypes.Supported
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

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ExportNullable
version:1.0

[ClickHouse] SHALL support exporting `Nullable` datatypes to Parquet files and `Nullable` datatypes that consist only of `Null`.

#### Working With Nested Types Export

##### RQ.SRS-032.ClickHouse.Parquet.Export.Nested
version: 1.0

[ClickHouse] SHALL support exporting nested columns to the Parquet file.

##### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.Nested
version:1.0

[ClickHouse] SHALL support exporting nested: `Array`, `Tuple` and `Map` datatypes to Parquet files.

#### Exporting Chunked Columns

##### RQ.SRS-032.ClickHouse.Parquet.Export.DataTypes.ChunkedColumns
version: 1.0

[ClickHouse] SHALL support exporting chunked columns to Parquet files.

#### RQ.SRS-032.ClickHouse.Export.Parquet.Join
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT` query with a `JOIN` clause into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Union
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT` query with a `UNION` clause into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Export.View
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT * FROM {view_name}` query into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Export.Select.MaterializedView
version: 1.0

[ClickHouse] SHALL support exporting output of `SELECT * FROM {mat_view_name}` query into a Parquet file.

#### Export Encoded

##### Plain (Export)

###### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Plain
version: 1.0

[ClickHouse] SHALL support exporting `Plain` encoded Parquet files.

##### Run Length Encoding (Export)

###### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.RunLength
version: 1.0

[ClickHouse] SHALL support exporting `Run Length Encoding / Bit-Packing Hybrid` encoded Parquet files.

##### Delta (Export)

###### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.Delta
version: 1.0

[ClickHouse] SHALL support exporting `Delta Encoding` encoded Parquet files.

##### Delta-length byte array (Export)

###### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaLengthByteArray
version: 1.0

[ClickHouse] SHALL support exporting `Delta-length byte array` encoded Parquet files.

##### Delta Strings (Export)

###### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.DeltaStrings
version: 1.0

[ClickHouse] SHALL support exporting `Delta Strings` encoded Parquet files.

##### Byte Stream Split (Export)

##### RQ.SRS-032.ClickHouse.Parquet.Export.Encoding.ByteStreamSplit
version: 1.0

[ClickHouse] SHALL support exporting `Byte Stream Split` encoded Parquet files.

#### Export Settings

##### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.RowGroupSize
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.
The default value SHALL be `1000000`.

##### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsString
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.
The default value SHALL be `0`.

##### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.StringAsFixedByteArray
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_fixed_string_as_fixed_byte_array` to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns. The default value SHALL be `1`.

##### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.ParquetVersion
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_version` to set the version of Parquet used in the output file.
The default value SHALL be `2.latest`.

##### RQ.SRS-032.ClickHouse.Parquet.Export.Settings.CompressionMethod
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_compression_method` to set the compression method used in the Parquet file.
The default value SHALL be `lz4`.

#### Type Conversion

##### RQ.SRS-032.ClickHouse.Parquet.DataTypes.TypeConversionFunction
version:1.0

[ClickHouse] SHALL support using type conversion functions when importing Parquet files.

For example,

```sql
SELECT
    n,
    toDateTime(time)
FROM file('time.parquet', Parquet);
```

### Parquet Encryption

#### RQ.SRS-032.ClickHouse.Parquet.Encryption
version: 1.0

[ClickHouse] MAY not support importing or exporting encrypted Parquet files.

### DESCRIBE Parquet

#### RQ.SRS-032.ClickHouse.Parquet.Structure
version: 1.0

[ClickHouse] SHALL support using `DESCRIBE TABLE` statement on the Parquet to read the file structure.

For example,

```sql
DESCRIBE TABLE file('data.parquet', Parquet)
```

### Compression

#### None

##### RQ.SRS-032.ClickHouse.Parquet.Compression.None
version: 1.0

[ClickHouse] SHALL support importing or exporting uncompressed Parquet files.

#### Gzip

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using gzip.

#### Brotli

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using brotli.

#### Lz4

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4.

#### Lz4Raw

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw
version: 1.0

[ClickHouse] SHALL support importing or exporting Parquet files compressed using lz4_raw.

#### Unsupported Compression

##### Snappy

###### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy
version: 1.0

[ClickHouse] MAY not support importing or exporting Parquet files compressed using snapy.

##### Lzo

###### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo
version: 1.0

[ClickHouse] MAY not support importing or exporting Parquet files compressed using lzo.

##### Zstd

###### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd
version: 1.0

[ClickHouse] MAY not support importing or exporting Parquet files compressed using zstd.


### Table Functions

#### URL

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function importing and exporting Parquet format.

#### File

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function importing and exporting Parquet format.

For example,

```sql
SELECT * FROM file('data.parquet', Parquet)
```

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File.AutoDetectParquetFileFormat
version: 1.0

[ClickHouse] SHALL support automatically detecting Parquet file format based on file extension when using `file()` function without explicitly specifying the format setting.

```sql
SELECT * FROM file('data.parquet')
```

#### s3

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function for import and exporting Parquet format.

For example,

```sql
SELECT *
FROM gcs('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)
```

#### jdbc

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function for import and exporting Parquet format.

#### odbc

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function for importing and exporting Parquet format.

#### hdfs

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function for importing and exporting Parquet format.

#### remote

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function for importing and exporting Parquet format.

#### mysql

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL
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

#### PostgreSQL

##### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function importing and exporting Parquet format.

### Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MergeTree` table engine.

##### ReplicatedMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplicatedMergeTree` table engine.

##### ReplacingMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `ReplacingMergeTree` table engine.

##### SummingMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `SummingMergeTree` table engine.

##### AggregatingMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `AggregatingMergeTree` table engine.

##### CollapsingMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `CollapsingMergeTree` table engine.

##### VersionedCollapsingMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `VersionedCollapsingMergeTree` table engine.

##### GraphiteMergeTree

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `GraphiteMergeTree` table engine.

#### Integration Engines

##### ODBC Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `ODBC` table engine.

##### JDBC Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `JDBC` table engine.

##### MySQL Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MySQL` table engine.

##### MongoDB Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `MongoDB` table engine.

##### HDFS Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `HDFS` table engine.

##### S3 Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `S3` table engine.

##### Kafka Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Kafka` table engine.

##### EmbeddedRocksDB Engine

###### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into an `EmbeddedRocksDB` table engine.

##### PostgreSQL Engine

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `PostgreSQL` table engine.

#### Special Engines

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Memory` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Distributed` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `Dictionary` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `File` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL
version: 1.0

[ClickHouse] SHALL support Parquet format being exported from and imported into a `URL` table engine.

### Metadata

Parquet files have three types of metadata

- file metadata
- column (chunk) metadata
- page header metadata

as described in https://parquet.apache.org/docs/file-format/metadata/.

#### ParquetFormat

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat
version: 1.0

[ClickHouse] SHALL support `ParquetMetadata` format to read metadata from Parquet files.

For example,

```sql
SELECT * FROM file(data.parquet, ParquetMetadata) format PrettyJSONEachRow
```

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadataFormat.Output
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

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.Content
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

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata.MinMax
version: 1.0

[ClickHouse] SHALL support Parquet files that have Min/Max values in the metadata and the files that are missing Min/Max values.

#### Metadata Types

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.File
version: 1.0

[ClickHouse] SHALL support accessing `File Metadata` in Parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Column
version: 1.0

[ClickHouse] SHALL support accessing `Column (Chunk) Metadata` in Parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Header
version: 1.0

[ClickHouse] SHALL support accessing `Page Header Metadata` in Parquet files.

### Error Recovery

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber
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

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `file` metadata.
In this case the file metadata is corrupt, the file is lost.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `column` metadata.
In this case that column chunk MAY be lost but column chunks for this column in other row groups SHALL be okay.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Header`.
In this case the remaining pages in that chunk SHALL be lost.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Data`.
In this case that page SHALL be lost.

#### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt column values.

Error message example,

> DB::Exception: Cannot extract table structure from Parquet format file.
> 
##### List of Corrupt Column Values

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Date
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `date` values.


###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Int
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Int` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.BigInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BigInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.SmallInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `SmallInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TinyInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TinyInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UBigInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UBigInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.USmallInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `USmallInt` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.UTinyInt
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `UTinyInt` values.


###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampUS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (us)` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimestampMS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `Timestamp (ms)` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Bool
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BOOL` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Float
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FLOAT` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Double
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DOUBLE` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeMS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ms)` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeUS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (us)` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.TimeNS
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `TIME (ns)` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.String
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRING` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Binary
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `BINARY` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.FixedLengthByteArray
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `FIXED_LENGTH_BYTE_ARRAY` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Decimal
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `DECIMAL` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.List
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `LIST` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Struct
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `STRUCT` values.

###### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumnValues.Map
version: 1.0

[ClickHouse] SHALL output an error when trying to import the Parquet files with corrupt `MAP` values.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptChecksum
version: 1.0

[ClickHouse] SHALL output an error if the Parquet file's checksum is corrupted.


[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/parquet/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
