# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220810.1192506.
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

RQ_SRS_032_ClickHouse_Parquet_Insert_Projections = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Projections",
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
    num="4.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.ImportNested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of\n"
        "nested structs into Nested tables.\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_CaseInsensitiveColumnMatching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.CaseInsensitiveColumnMatching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching\n"
        "Parquet and ClickHouse columns.\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_AllowMissingColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.AllowMissingColumns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`\n"
        "to allow skipping unsupported types..Format\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.2.4",
)

RQ_SRS_032_ClickHouse_Parquet_InsertConversions = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.InsertConversions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet types to ClickHouse types in the following manner:\n"
        "\n"
        "Parquet | ClickHouse\n"
        "--- | ---\n"
        "UInt8 | UInt8\n"
        "Bool | UInt8\n"
        "Int8 | Int8\n"
        "UInt16 | UInt16\n"
        "UInt32 | UInt32\n"
        "UInt64 | UInt64\n"
        "Int16 | Int16\n"
        "Int32 | Int32\n"
        "Int64 | Int64\n"
        "Float | Float32\n"
        "Half_Float | Float32\n"
        "Double | Float64\n"
        "Date32 | Date\n"
        "Date64 | DateTime\n"
        "Timestamp | DateTime\n"
        "String | String\n"
        "Binary | String\n"
        "Decimal | Decimal128\n"
        "List | Array\n"
        "Struct | Tuple\n"
        "Map | Map\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_OutFormatParquet_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.RowGroupSize",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.\n"
        "Default: `1000000`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Settings_OutFormatParquet_StringAsString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.StringAsString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.3",
)

RQ_SRS_032_ClickHouse_Parquet_SelectConversions = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.SelectConversions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse types to Parquet types in the following manner:\n"
        "\n"
        "ClickHouse | Parquet\n"
        "--- | ---\n"
        "UInt8 | UInt8\n"
        "Int8 | Int8\n"
        "UInt16 | UInt16\n"
        "UInt32 | UInt32\n"
        "UInt64 | UInt64\n"
        "Int16 | Int16\n"
        "Int32 | Int32\n"
        "Int64 | Int64\n"
        "Float32 | Float\n"
        "Float64 | Double\n"
        "Date | UInt16\n"
        "DateTime | UInt32\n"
        "String | Binary\n"
        "Decimal128 | Decimal\n"
        "Array | List\n"
        "Tuple | Struct\n"
        "Map | Map\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Null = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Null",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Null and Nullable(type) data when inserting or selecting using Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Arrays = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support nested `arrays` in Parquet format.\n" "\n"
    ),
    link=None,
    level=3,
    num="4.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Tuple = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support nested `tuples` in Parquet format.\n" "\n"
    ),
    link=None,
    level=3,
    num="4.5.2",
)

RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Map = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support nested `maps` in Parquet format.\n" "\n"),
    link=None,
    level=3,
    num="4.5.3",
)

RQ_SRS_032_ClickHouse_Parquet_NestedTypes_LowCardinalityNullable = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support nesting LowCardinality and Nullable data types in any order.\n"
        "Example:\n"
        "LowCardinality(Nullable(String))\n"
        "Nullable(LowCradinality(String))\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.5.4",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_Time32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet `Time32` type.\n" "\n"),
    link=None,
    level=3,
    num="4.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_FixedSizeBinary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support Parquet `Fixed_Size_Binary` type.\n" "\n"
    ),
    link=None,
    level=3,
    num="4.6.2",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_JSON = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet `JSON` type.\n" "\n"),
    link=None,
    level=3,
    num="4.6.3",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_UUID = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet `UUID` type.\n" "\n"),
    link=None,
    level=3,
    num="4.6.4",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ENUM = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet `ENUM` type.\n" "\n"),
    link=None,
    level=3,
    num="4.6.5",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_Query = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.Query",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading and writing Parquet format from a command line query.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.7.1",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `url` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `file` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.JDBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.4",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.ODBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.5",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.6",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_Remote = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.Remote",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.7",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.MySQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.8",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_PostgeSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.PostgeSQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.9",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.ODBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `ODBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.JDBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from a `JDBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MySQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MySQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.3",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_MongoDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MongoDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MongoDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.4",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `HDFS` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.5",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `s3` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.6",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_Kafka = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.Kafka",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Kafka` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.7",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_EmbeddedRocksDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.EmbeddedRocksDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `EmbeddedRocksDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.8",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_PostgreSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.PostgreSQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `PostgreSQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.1.9",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_Distributed = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Distributed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Distributed` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Dictionary` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `File` table engine.\n"
        "\n"
    ),
    link=None,
    level=5,
    num="4.7.3.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being inserted into and selected from an `URL` table engine.\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md \n"
        "[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=5,
    num="4.7.3.2.4",
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
        Heading(name="General", level=2, num="4.1"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet", level=3, num="4.1.1"),
        Heading(name="INSERT", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Projections",
            level=3,
            num="4.2.1",
        ),
        Heading(name="INSERT Settings", level=3, num="4.2.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.ImportNested",
            level=4,
            num="4.2.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.CaseInsensitiveColumnMatching",
            level=4,
            num="4.2.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.AllowMissingColumns",
            level=4,
            num="4.2.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference",
            level=4,
            num="4.2.2.4",
        ),
        Heading(name="INSERT Conversions", level=3, num="4.2.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.InsertConversions",
            level=4,
            num="4.2.3.1",
        ),
        Heading(name="SELECT", level=2, num="4.3"),
        Heading(name="SELECT Settings", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.RowGroupSize",
            level=3,
            num="4.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.StringAsString",
            level=3,
            num="4.3.3",
        ),
        Heading(name="SELECT Conversions", level=3, num="4.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.SelectConversions",
            level=4,
            num="4.3.4.1",
        ),
        Heading(name="Null", level=2, num="4.4"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Null", level=3, num="4.4.1"),
        Heading(name="Nested Types", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays",
            level=3,
            num="4.5.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple", level=3, num="4.5.2"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map", level=3, num="4.5.3"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable",
            level=3,
            num="4.5.4",
        ),
        Heading(name="Unsupported Parquet Types", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32",
            level=3,
            num="4.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary",
            level=3,
            num="4.6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON",
            level=3,
            num="4.6.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID",
            level=3,
            num="4.6.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM",
            level=3,
            num="4.6.5",
        ),
        Heading(name="Sources", level=2, num="4.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.Query", level=3, num="4.7.1"
        ),
        Heading(name="Table Functions", level=3, num="4.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.URL",
            level=4,
            num="4.7.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.File",
            level=4,
            num="4.7.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.S3",
            level=4,
            num="4.7.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.JDBC",
            level=4,
            num="4.7.2.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.ODBC",
            level=4,
            num="4.7.2.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.HDFS",
            level=4,
            num="4.7.2.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.Remote",
            level=4,
            num="4.7.2.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.MySQL",
            level=4,
            num="4.7.2.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.PostgeSQL",
            level=4,
            num="4.7.2.9",
        ),
        Heading(name="Table Engines", level=3, num="4.7.3"),
        Heading(name="Integration Engines", level=4, num="4.7.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.ODBC",
            level=5,
            num="4.7.3.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.JDBC",
            level=5,
            num="4.7.3.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MySQL",
            level=5,
            num="4.7.3.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MongoDB",
            level=5,
            num="4.7.3.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.HDFS",
            level=5,
            num="4.7.3.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.S3",
            level=5,
            num="4.7.3.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.Kafka",
            level=5,
            num="4.7.3.1.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.EmbeddedRocksDB",
            level=5,
            num="4.7.3.1.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.PostgreSQL",
            level=5,
            num="4.7.3.1.9",
        ),
        Heading(name="Special Engines", level=4, num="4.7.3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Distributed",
            level=5,
            num="4.7.3.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Dictionary",
            level=5,
            num="4.7.3.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.File",
            level=5,
            num="4.7.3.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.URL",
            level=5,
            num="4.7.3.2.4",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Projections,
        RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Settings_InputFormatParquet_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_InsertConversions,
        RQ_SRS_032_ClickHouse_Parquet_Settings_OutFormatParquet_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Settings_OutFormatParquet_StringAsString,
        RQ_SRS_032_ClickHouse_Parquet_SelectConversions,
        RQ_SRS_032_ClickHouse_Parquet_Null,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Arrays,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Tuple,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Map,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_LowCardinalityNullable,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_Time32,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_FixedSizeBinary,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_JSON,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_UUID,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ENUM,
        RQ_SRS_032_ClickHouse_Parquet_Sources_Query,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_Remote,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableFunctions_PostgeSQL,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_MongoDB,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_S3,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_Kafka,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_EmbeddedRocksDB,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Integration_PostgreSQL,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_Distributed,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_File,
        RQ_SRS_032_ClickHouse_Parquet_Sources_TableEngines_Special_URL,
    ),
    content="""
# SRS032 ClickHouse Parquet Data Format
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Feature Diagram](#feature-diagram)
* 4 [Requirements](#requirements)
  * 4.1 [General](#general)
    * 4.1.1 [RQ.SRS-032.ClickHouse.Parquet](#rqsrs-032clickhouseparquet)
  * 4.2 [INSERT](#insert)
    * 4.2.1 [RQ.SRS-032.ClickHouse.Parquet.Insert.Projections](#rqsrs-032clickhouseparquetinsertprojections)
    * 4.2.2 [INSERT Settings](#insert-settings)
      * 4.2.2.1 [RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.ImportNested](#rqsrs-032clickhouseparquetsettingsinputformatparquetimportnested)
      * 4.2.2.2 [RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetsettingsinputformatparquetcaseinsensitivecolumnmatching)
      * 4.2.2.3 [RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.AllowMissingColumns](#rqsrs-032clickhouseparquetsettingsinputformatparquetallowmissingcolumns)
      * 4.2.2.4 [RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetsettingsinputformatparquetskipcolumnswithunsupportedtypesinschemainference)
    * 4.2.3 [INSERT Conversions](#insert-conversions)
      * 4.2.3.1 [RQ.SRS-032.ClickHouse.Parquet.InsertConversions](#rqsrs-032clickhouseparquetinsertconversions)
  * 4.3 [SELECT](#select)
    * 4.3.1 [SELECT Settings](#select-settings)
    * 4.3.2 [RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.RowGroupSize](#rqsrs-032clickhouseparquetsettingsoutformatparquetrowgroupsize)
    * 4.3.3 [RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.StringAsString](#rqsrs-032clickhouseparquetsettingsoutformatparquetstringasstring)
    * 4.3.4 [SELECT Conversions](#select-conversions)
      * 4.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.SelectConversions](#rqsrs-032clickhouseparquetselectconversions)
  * 4.4 [Null](#null)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Parquet.Null](#rqsrs-032clickhouseparquetnull)
  * 4.5 [Nested Types](#nested-types)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays](#rqsrs-032clickhouseparquetnestedtypesarrays)
    * 4.5.2 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple](#rqsrs-032clickhouseparquetnestedtypestuple)
    * 4.5.3 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map](#rqsrs-032clickhouseparquetnestedtypesmap)
    * 4.5.4 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable](#rqsrs-032clickhouseparquetnestedtypeslowcardinalitynullable)
  * 4.6 [Unsupported Parquet Types](#unsupported-parquet-types)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32](#rqsrs-032clickhouseparquetunsupportedparquettypestime32)
    * 4.6.2 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary](#rqsrs-032clickhouseparquetunsupportedparquettypesfixedsizebinary)
    * 4.6.3 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON](#rqsrs-032clickhouseparquetunsupportedparquettypesjson)
    * 4.6.4 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID](#rqsrs-032clickhouseparquetunsupportedparquettypesuuid)
    * 4.6.5 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM](#rqsrs-032clickhouseparquetunsupportedparquettypesenum)
  * 4.7 [Sources](#sources)
    * 4.7.1 [RQ.SRS-032.ClickHouse.Parquet.Sources.Query](#rqsrs-032clickhouseparquetsourcesquery)
    * 4.7.2 [Table Functions](#table-functions)
      * 4.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.URL](#rqsrs-032clickhouseparquetsourcestablefunctionsurl)
      * 4.7.2.2 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.File](#rqsrs-032clickhouseparquetsourcestablefunctionsfile)
      * 4.7.2.3 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.S3](#rqsrs-032clickhouseparquetsourcestablefunctionss3)
      * 4.7.2.4 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.JDBC](#rqsrs-032clickhouseparquetsourcestablefunctionsjdbc)
      * 4.7.2.5 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.ODBC](#rqsrs-032clickhouseparquetsourcestablefunctionsodbc)
      * 4.7.2.6 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.HDFS](#rqsrs-032clickhouseparquetsourcestablefunctionshdfs)
      * 4.7.2.7 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.Remote](#rqsrs-032clickhouseparquetsourcestablefunctionsremote)
      * 4.7.2.8 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.MySQL](#rqsrs-032clickhouseparquetsourcestablefunctionsmysql)
      * 4.7.2.9 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.PostgeSQL](#rqsrs-032clickhouseparquetsourcestablefunctionspostgesql)
    * 4.7.3 [Table Engines](#table-engines)
      * 4.7.3.1 [Integration Engines](#integration-engines)
        * 4.7.3.1.1 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquetsourcestableenginesintegrationodbc)
        * 4.7.3.1.2 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquetsourcestableenginesintegrationjdbc)
        * 4.7.3.1.3 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquetsourcestableenginesintegrationmysql)
        * 4.7.3.1.4 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquetsourcestableenginesintegrationmongodb)
        * 4.7.3.1.5 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquetsourcestableenginesintegrationhdfs)
        * 4.7.3.1.6 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.S3](#rqsrs-032clickhouseparquetsourcestableenginesintegrations3)
        * 4.7.3.1.7 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquetsourcestableenginesintegrationkafka)
        * 4.7.3.1.8 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquetsourcestableenginesintegrationembeddedrocksdb)
        * 4.7.3.1.9 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquetsourcestableenginesintegrationpostgresql)
      * 4.7.3.2 [Special Engines](#special-engines)
        * 4.7.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquetsourcestableenginesspecialdistributed)
        * 4.7.3.2.2 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquetsourcestableenginesspecialdictionary)
        * 4.7.3.2.3 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.File](#rqsrs-032clickhouseparquetsourcestableenginesspecialfile)
        * 4.7.3.2.4 [RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.URL](#rqsrs-032clickhouseparquetsourcestableenginesspecialurl)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `Parquet` data format in [ClickHouse].

## Feature Diagram

```mermaid
flowchart LR;
    subgraph Overhead[Parquet]
        direction LR;
        subgraph Sources[Storage]
            subgraph Funcs[Functions]
                direction LR;
                URL_func_in[URL]
                File_func_in[FILE]
                Query_func_in[Query]
                S3_func_in[S3]
                jdbc_func_in[JDBC]
                odbc_func_in[ODBC]
                hdfs_func_in[HDFS]
                remote_func_in[Remote]
                mysql_func_in[MySQL]
                postgresql_func_in[PostgresSQL]
            end

            subgraph Integration_Engines[Integration Engines]
                ODBC_eng_in[ODBC]
                jdbc_eng_in[JDBC]
                mysql_eng_in[MySQL]
                mongodb_eng_in[MongoDB]
                hdfs_eng_in[HDFS]
                s3_eng_in[S3]
                kafka_eng_in[Kafka]
                embeddedrocksDB_eng_in[EmbeddedRocksDB]
                RabbitMQ_eng_in[RabbitMQ]
                PostgreSQL_eng_in[PostgreSQL]
            end

            subgraph Special_Engines[Special Engines]
                distributed_eng_in[Distributed]
                dictionary_eng_in[Dictionary]
                file_eng_in[File]
                url_eng_in[URL]
            end
        end

        subgraph ClickHouse_Conversion[Input type > ClickHouse type > Select type]
            direction LR;
            subgraph Insert_types[INSERT]
                UInt8_in[UInt8]
                Bool_in[Bool]
                Int8_in[Int8]
                UInt16_in[UInt16]
                Int16_in[Int16]
                UInt32_in[UInt32]
                Int32_in[Int32]
                UInt64_in[UInt64]
                Int64_in[Int64]
                Float_in
                Half_Float_in
                Double_in
                Date32_in
                Date64_in
                Timestamp_in
                String_in
                Binary_in
                Decimal_in
                List_in
                Struct_in
                Map_in
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
                Float32_ch
                Float64_ch
                Date_ch
                DateTime_ch
                String_ch
                FixedString_ch
                Decimal128_ch
                Array_ch
                Tuple_ch
                Map_ch
            end

            subgraph Select_types[SELECT]
                UInt8_out[UInt8]
                Int8_out[Int8]
                UInt16_out[UInt16]
                Int16_out[Int16]
                UInt32_out[UInt32]
                Int32_out[Int32]
                UInt64_out[UInt64]
                Int64_out[Int64]
                Float_out
                Double_out
                Binary_out
                Decimal_out
                List_out
                Struct_out
                Map_out
            end

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

        end

        subgraph Input_settings[Input settings]
            direction LR
            import_nested
            case_insensitive_column_matching
            allow_missing_columns
            skip_columns_with_unsupported_types_in_schema_inference 
        end

        subgraph Output_settings[Output settings]
            direction LR
            row_group_size
            string_as_string
        end

        Sources --Write into ClickHouse--> Input_settings --> ClickHouse_Conversion --> Output_settings --Read From Clickhouse--> Sources
        
        subgraph Not_supported[Not Supported Types]
            direction LR
            Time32
            FIXED_SIZE_BINARY
            JSON
            UUID
            ENUM
        end

        subgraph Modifiers[Supported Modifiers]
            direction LR
            Nullable
            LowCardinality
        end
    end
```

## Requirements

### General

#### RQ.SRS-032.ClickHouse.Parquet
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

### INSERT

#### RQ.SRS-032.ClickHouse.Parquet.Insert.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

#### INSERT Settings

##### RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`
to allow skipping unsupported types..Format
Default: `false`

#### INSERT Conversions

##### RQ.SRS-032.ClickHouse.Parquet.InsertConversions
version:1.0

[ClickHouse] SHALL convert Parquet types to ClickHouse types in the following manner:

Parquet | ClickHouse
--- | ---
UInt8 | UInt8
Bool | UInt8
Int8 | Int8
UInt16 | UInt16
UInt32 | UInt32
UInt64 | UInt64
Int16 | Int16
Int32 | Int32
Int64 | Int64
Float | Float32
Half_Float | Float32
Double | Float64
Date32 | Date
Date64 | DateTime
Timestamp | DateTime
String | String
Binary | String
Decimal | Decimal128
List | Array
Struct | Tuple
Map | Map

### SELECT

#### SELECT Settings

#### RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.RowGroupSize
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.
Default: `1000000`

#### RQ.SRS-032.ClickHouse.Parquet.Settings.OutFormatParquet.StringAsString
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.
Default: `false`

#### SELECT Conversions

##### RQ.SRS-032.ClickHouse.Parquet.SelectConversions
version:1.0

[ClickHouse] SHALL convert ClickHouse types to Parquet types in the following manner:

ClickHouse | Parquet
--- | ---
UInt8 | UInt8
Int8 | Int8
UInt16 | UInt16
UInt32 | UInt32
UInt64 | UInt64
Int16 | Int16
Int32 | Int32
Int64 | Int64
Float32 | Float
Float64 | Double
Date | UInt16
DateTime | UInt32
String | Binary
Decimal128 | Decimal
Array | List
Tuple | Struct
Map | Map

### Null

#### RQ.SRS-032.ClickHouse.Parquet.Null
version:1.0

[ClickHouse] SHALL support Null and Nullable(type) data when inserting or selecting using Parquet format.

### Nested Types

#### RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays
version:1.0

[ClickHouse] SHALL support nested `arrays` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple
version:1.0

[ClickHouse] SHALL support nested `tuples` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map
version:1.0

[ClickHouse] SHALL support nested `maps` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable
version: 1.0

[ClickHouse] SHALL support nesting LowCardinality and Nullable data types in any order.
Example:
LowCardinality(Nullable(String))
Nullable(LowCradinality(String))

### Unsupported Parquet Types

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32
version:1.0

[ClickHouse] MAY not support Parquet `Time32` type.

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary
version:1.0

[ClickHouse] MAY not support Parquet `Fixed_Size_Binary` type.

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON
version:1.0

[ClickHouse] MAY not support Parquet `JSON` type.

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID
version:1.0

[ClickHouse] MAY not support Parquet `UUID` type.

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM
version:1.0

[ClickHouse] MAY not support Parquet `ENUM` type.

### Sources

#### RQ.SRS-032.ClickHouse.Parquet.Sources.Query
version: 1.0

[ClickHouse] SHALL support reading and writing Parquet format from a command line query.

#### Table Functions

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.MySQL
version: 1.0

[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Sources.TableFunctions.PostgeSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.

#### Table Engines

##### Integration Engines

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.ODBC
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `ODBC` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.JDBC
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `JDBC` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MySQL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MySQL` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.MongoDB
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MongoDB` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.HDFS
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `HDFS` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.S3
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `s3` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.Kafka
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Kafka` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.EmbeddedRocksDB
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `EmbeddedRocksDB` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Integration.PostgreSQL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `PostgreSQL` table engine.

##### Special Engines

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Distributed
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Distributed` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.Dictionary
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Dictionary` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.File
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `File` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Sources.TableEngines.Special.URL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `URL` table engine.

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md 
[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
