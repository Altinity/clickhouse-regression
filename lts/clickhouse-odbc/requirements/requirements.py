# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.1.240306.1133530.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_100_ODBC_DriverBuild = Requirement(
    name="RQ.SRS-100.ODBC.DriverBuild",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The clickhouse-odbc driver SHALL be buildable from source against the target\n"
        "ClickHouse version and produce working shared libraries\n"
        "(`libclickhouseodbc.so`, `libclickhouseodbcw.so`).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.1.1",
)

RQ_SRS_100_ODBC_Connection = Requirement(
    name="RQ.SRS-100.ODBC.Connection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL successfully connect to a running ClickHouse server\n"
        "and execute a basic `SELECT 1` query.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1",
)

RQ_SRS_100_ODBC_Connection_DSN = Requirement(
    name="RQ.SRS-100.ODBC.Connection.DSN",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL support connection via both ANSI and Unicode DSN\n"
        "configurations.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.2",
)

RQ_SRS_100_ODBC_DataTypes_Int8 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int8` values including boundary\n"
        "values (-128, 0, 127).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.1",
)

RQ_SRS_100_ODBC_DataTypes_Int16 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int16` values including boundary\n"
        "values (-32768, 0, 32767).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.2",
)

RQ_SRS_100_ODBC_DataTypes_Int32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int32` values including boundary\n"
        "values (-2147483648, 0, 2147483647).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.3",
)

RQ_SRS_100_ODBC_DataTypes_Int64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Int64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Int64` values including boundary\n"
        "values.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.4",
)

RQ_SRS_100_ODBC_DataTypes_UInt8 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt8` values (0, 255).\n" "\n"
    ),
    link=None,
    level=4,
    num="3.3.5",
)

RQ_SRS_100_ODBC_DataTypes_UInt16 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt16` values (0, 65535).\n" "\n"
    ),
    link=None,
    level=4,
    num="3.3.6",
)

RQ_SRS_100_ODBC_DataTypes_UInt32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt32` values (0, 4294967295).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.7",
)

RQ_SRS_100_ODBC_DataTypes_UInt64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `UInt64` values (0, 18446744073709551615).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.8",
)

RQ_SRS_100_ODBC_DataTypes_Float32 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Float32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Float32` values including special\n"
        "values (inf, -inf, nan).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.9",
)

RQ_SRS_100_ODBC_DataTypes_Float64 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Float64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Float64` values including special\n"
        "values (inf, -inf, nan).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.10",
)

RQ_SRS_100_ODBC_DataTypes_Decimal = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Decimal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Decimal32`, `Decimal64`, and\n"
        "`Decimal128` values with configurable precision and scale.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.11",
)

RQ_SRS_100_ODBC_DataTypes_String = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.String",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `String` values including UTF-8,\n"
        "ASCII, and special characters.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.12",
)

RQ_SRS_100_ODBC_DataTypes_FixedString = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.FixedString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `FixedString(N)` values with\n"
        "proper null-byte padding.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.13",
)

RQ_SRS_100_ODBC_DataTypes_Date = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Date",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `Date` values.\n" "\n"),
    link=None,
    level=4,
    num="3.3.14",
)

RQ_SRS_100_ODBC_DataTypes_DateTime = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.DateTime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `DateTime` values.\n" "\n"
    ),
    link=None,
    level=4,
    num="3.3.15",
)

RQ_SRS_100_ODBC_DataTypes_Enum = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Enum",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly round-trip `Enum` values with both UTF-8\n"
        "and ASCII keys.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.16",
)

RQ_SRS_100_ODBC_DataTypes_UUID = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.UUID",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `UUID` values.\n" "\n"),
    link=None,
    level=4,
    num="3.3.17",
)

RQ_SRS_100_ODBC_DataTypes_IPv4 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.IPv4",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `IPv4` values.\n" "\n"),
    link=None,
    level=4,
    num="3.3.18",
)

RQ_SRS_100_ODBC_DataTypes_IPv6 = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.IPv6",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("The ODBC driver SHALL correctly round-trip `IPv6` values.\n" "\n"),
    link=None,
    level=4,
    num="3.3.19",
)

RQ_SRS_100_ODBC_DataTypes_Nullable = Requirement(
    name="RQ.SRS-100.ODBC.DataTypes.Nullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly handle `Nullable` variants of all supported\n"
        "data types, returning `None` for NULL values.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.20",
)

RQ_SRS_100_ODBC_ParameterizedQueries = Requirement(
    name="RQ.SRS-100.ODBC.ParameterizedQueries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL support parameterized queries (`?` placeholders) for\n"
        "all supported data types.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.4.1",
)

RQ_SRS_100_ODBC_ParameterizedQueries_Null = Requirement(
    name="RQ.SRS-100.ODBC.ParameterizedQueries.Null",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL correctly handle `NULL` parameter values in\n"
        "parameterized queries including with `isNull()` and `arrayReduce()` functions.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.4.2",
)

RQ_SRS_100_ODBC_Compatibility_LTS = Requirement(
    name="RQ.SRS-100.ODBC.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The ODBC driver SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.5.1",
)
