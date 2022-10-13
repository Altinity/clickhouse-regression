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

RQ_SRS_032_ClickHouse_Parquet_Null = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Null",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Null and Nullable(type) data when reading or writing Parquet format.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_Encryption = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Encryption",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support reading encrypted Parquet files.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.1.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Insert = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to\n"
        "read data from Parquet files and insert data into tables or table functions.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
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
    num="4.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.None",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading uncompressed Parquet files.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Gzip",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading Parquet files compressed using gzip.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Brotli",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading Parquet files compressed using brotli.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.3",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading Parquet files compressed using lz4.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.4",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4Raw",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading Parquet files compressed using lz4_raw.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.3.5",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Snappy = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Snappy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support reading Parquet files compressed using snapy.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Lzo = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Lzo",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support reading Parquet files compressed using lzo.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Zstd = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Zstd",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] MAY not support reading Parquet files compressed using zstd.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested",
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
    num="4.2.5.1",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_CaseInsensitiveColumnMatching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching",
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
    num="4.2.5.2",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_AllowMissingColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns",
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
    num="4.2.5.3",
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
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
    num="4.2.5.4",
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
    num="4.2.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Select = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file.\n"
        "```bash\n"
        'clickhouse-client --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}\n'
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.1",
)

RQ_SRS_032_ClickHouse_Parquet_Select_Join = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.Join",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing output of `SELECT` query with a `JOIN` clause into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.2",
)

RQ_SRS_032_ClickHouse_Parquet_Select_Union = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.Union",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing output of `SELECT` query with a `UNION` clause into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.3",
)

RQ_SRS_032_ClickHouse_Parquet_Select_View = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.View",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing output of `SELECT * FROM {view_name}` query into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.4",
)

RQ_SRS_032_ClickHouse_Parquet_Select_MaterializedView = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support writing output of `SELECT * FROM {mat_view_name}` query into a Parquet file.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.3.5",
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize",
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
    level=4,
    num="4.3.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString",
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
    level=4,
    num="4.3.6.2",
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
    num="4.3.7.1",
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
    num="4.4.1",
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
    num="4.4.2",
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
    num="4.4.3",
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
    num="4.4.4",
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
    num="4.5.1",
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
    num="4.5.2",
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
    num="4.5.3",
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
    num="4.5.4",
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
    num="4.5.5",
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ChunkedArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] MAY not support Parquet chunked arrays.\n" "\n"),
    link=None,
    level=3,
    num="4.5.6",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL",
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
    level=3,
    num="4.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File",
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
    level=3,
    num="4.6.2",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3",
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
    level=3,
    num="4.6.3",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC",
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
    level=3,
    num="4.6.4",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC",
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
    level=3,
    num="4.6.5",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS",
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
    level=3,
    num="4.6.6",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote",
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
    level=3,
    num="4.6.7",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL",
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
    level=3,
    num="4.6.8",
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgeSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgeSQL",
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
    level=3,
    num="4.6.9",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from an `ODBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `JDBC` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `MySQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.3",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MongoDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `MongoDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.4",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `HDFS` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.5",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from an `S3` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.6",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_Kafka = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `Kafka` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.7",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_EmbeddedRocksDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from an `EmbeddedRocksDB` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.8",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `PostgreSQL` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.1.9",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `Distributed` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `Dictionary` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `File` table engine.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.7.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Parquet format being writen into and read from a `URL` table engine.\n"
        "\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md \n"
        "[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md\n"
        "[Git]: https://git-scm.com/\n"
        "[GitHub]: https://github.com\n"
    ),
    link=None,
    level=4,
    num="4.7.2.4",
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
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Null", level=3, num="4.1.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Encryption", level=4, num="4.1.2.1"
        ),
        Heading(name="INSERT", level=2, num="4.2"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Insert", level=3, num="4.2.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Projections",
            level=3,
            num="4.2.2",
        ),
        Heading(name="Compression", level=3, num="4.2.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.None",
            level=4,
            num="4.2.3.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Gzip",
            level=4,
            num="4.2.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Brotli",
            level=4,
            num="4.2.3.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4",
            level=4,
            num="4.2.3.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4Raw",
            level=4,
            num="4.2.3.5",
        ),
        Heading(name="Unsupported Compression", level=3, num="4.2.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Snappy",
            level=4,
            num="4.2.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Lzo",
            level=4,
            num="4.2.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Zstd",
            level=4,
            num="4.2.4.3",
        ),
        Heading(name="INSERT Settings", level=3, num="4.2.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested",
            level=4,
            num="4.2.5.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching",
            level=4,
            num="4.2.5.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns",
            level=4,
            num="4.2.5.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference",
            level=4,
            num="4.2.5.4",
        ),
        Heading(name="INSERT Conversions", level=3, num="4.2.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.InsertConversions",
            level=4,
            num="4.2.6.1",
        ),
        Heading(name="SELECT", level=2, num="4.3"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Select", level=3, num="4.3.1"),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Select.Join", level=3, num="4.3.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Select.Union", level=3, num="4.3.3"
        ),
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Select.View", level=3, num="4.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView",
            level=3,
            num="4.3.5",
        ),
        Heading(name="SELECT Settings", level=3, num="4.3.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize",
            level=4,
            num="4.3.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString",
            level=4,
            num="4.3.6.2",
        ),
        Heading(name="SELECT Conversions", level=3, num="4.3.7"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.SelectConversions",
            level=4,
            num="4.3.7.1",
        ),
        Heading(name="Nested Types", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays",
            level=3,
            num="4.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple", level=3, num="4.4.2"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map", level=3, num="4.4.3"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable",
            level=3,
            num="4.4.4",
        ),
        Heading(name="Unsupported Parquet Types", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32",
            level=3,
            num="4.5.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary",
            level=3,
            num="4.5.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON",
            level=3,
            num="4.5.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID",
            level=3,
            num="4.5.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM",
            level=3,
            num="4.5.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray",
            level=3,
            num="4.5.6",
        ),
        Heading(name="Table Functions", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL",
            level=3,
            num="4.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File",
            level=3,
            num="4.6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3", level=3, num="4.6.3"
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC",
            level=3,
            num="4.6.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC",
            level=3,
            num="4.6.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS",
            level=3,
            num="4.6.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote",
            level=3,
            num="4.6.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL",
            level=3,
            num="4.6.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgeSQL",
            level=3,
            num="4.6.9",
        ),
        Heading(name="Table Engines", level=2, num="4.7"),
        Heading(name="Integration Engines", level=3, num="4.7.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC",
            level=4,
            num="4.7.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC",
            level=4,
            num="4.7.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL",
            level=4,
            num="4.7.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB",
            level=4,
            num="4.7.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS",
            level=4,
            num="4.7.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3",
            level=4,
            num="4.7.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka",
            level=4,
            num="4.7.1.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB",
            level=4,
            num="4.7.1.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL",
            level=4,
            num="4.7.1.9",
        ),
        Heading(name="Special Engines", level=3, num="4.7.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed",
            level=4,
            num="4.7.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary",
            level=4,
            num="4.7.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File",
            level=4,
            num="4.7.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL",
            level=4,
            num="4.7.2.4",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet,
        RQ_SRS_032_ClickHouse_Parquet_Null,
        RQ_SRS_032_ClickHouse_Parquet_Encryption,
        RQ_SRS_032_ClickHouse_Parquet_Insert,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Projections,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_None,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Gzip,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Brotli,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Compression_Lz4Raw,
        RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Snappy,
        RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Lzo,
        RQ_SRS_032_ClickHouse_Parquet_Insert_UnsupportedCompression_Zstd,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_InsertConversions,
        RQ_SRS_032_ClickHouse_Parquet_Select,
        RQ_SRS_032_ClickHouse_Parquet_Select_Join,
        RQ_SRS_032_ClickHouse_Parquet_Select_Union,
        RQ_SRS_032_ClickHouse_Parquet_Select_View,
        RQ_SRS_032_ClickHouse_Parquet_Select_MaterializedView,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsString,
        RQ_SRS_032_ClickHouse_Parquet_SelectConversions,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Arrays,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Tuple,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_Map,
        RQ_SRS_032_ClickHouse_Parquet_NestedTypes_LowCardinalityNullable,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_Time32,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_FixedSizeBinary,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_JSON,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_UUID,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ENUM,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ChunkedArray,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgeSQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MongoDB,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_Kafka,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_EmbeddedRocksDB,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File,
        RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL,
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
    * 4.1.2 [RQ.SRS-032.ClickHouse.Parquet.Null](#rqsrs-032clickhouseparquetnull)
      * 4.1.2.1 [RQ.SRS-032.ClickHouse.Parquet.Encryption](#rqsrs-032clickhouseparquetencryption)
  * 4.2 [INSERT](#insert)
    * 4.2.1 [RQ.SRS-032.ClickHouse.Parquet.Insert](#rqsrs-032clickhouseparquetinsert)
    * 4.2.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.Projections](#rqsrs-032clickhouseparquetinsertprojections)
    * 4.2.3 [Compression](#compression)
      * 4.2.3.1 [RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.None](#rqsrs-032clickhouseparquetinsertcompressionnone)
      * 4.2.3.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Gzip](#rqsrs-032clickhouseparquetinsertcompressiongzip)
      * 4.2.3.3 [RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Brotli](#rqsrs-032clickhouseparquetinsertcompressionbrotli)
      * 4.2.3.4 [RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4](#rqsrs-032clickhouseparquetinsertcompressionlz4)
      * 4.2.3.5 [RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4Raw](#rqsrs-032clickhouseparquetinsertcompressionlz4raw)
    * 4.2.4 [Unsupported Compression](#unsupported-compression)
      * 4.2.4.1 [RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Snappy](#rqsrs-032clickhouseparquetinsertunsupportedcompressionsnappy)
      * 4.2.4.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Lzo](#rqsrs-032clickhouseparquetinsertunsupportedcompressionlzo)
      * 4.2.4.3 [RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Zstd](#rqsrs-032clickhouseparquetinsertunsupportedcompressionzstd)
    * 4.2.5 [INSERT Settings](#insert-settings)
      * 4.2.5.1 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested](#rqsrs-032clickhouseparquetinsertsettingsimportnested)
      * 4.2.5.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetinsertsettingscaseinsensitivecolumnmatching)
      * 4.2.5.3 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns](#rqsrs-032clickhouseparquetinsertsettingsallowmissingcolumns)
      * 4.2.5.4 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetinsertsettingsskipcolumnswithunsupportedtypesinschemainference)
    * 4.2.6 [INSERT Conversions](#insert-conversions)
      * 4.2.6.1 [RQ.SRS-032.ClickHouse.Parquet.InsertConversions](#rqsrs-032clickhouseparquetinsertconversions)
  * 4.3 [SELECT](#select)
    * 4.3.1 [RQ.SRS-032.ClickHouse.Parquet.Select](#rqsrs-032clickhouseparquetselect)
    * 4.3.2 [RQ.SRS-032.ClickHouse.Parquet.Select.Join](#rqsrs-032clickhouseparquetselectjoin)
    * 4.3.3 [RQ.SRS-032.ClickHouse.Parquet.Select.Union](#rqsrs-032clickhouseparquetselectunion)
    * 4.3.4 [RQ.SRS-032.ClickHouse.Parquet.Select.View](#rqsrs-032clickhouseparquetselectview)
    * 4.3.5 [RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView](#rqsrs-032clickhouseparquetselectmaterializedview)
    * 4.3.6 [SELECT Settings](#select-settings)
      * 4.3.6.1 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize](#rqsrs-032clickhouseparquetselectsettingsrowgroupsize)
      * 4.3.6.2 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString](#rqsrs-032clickhouseparquetselectsettingsstringasstring)
    * 4.3.7 [SELECT Conversions](#select-conversions)
      * 4.3.7.1 [RQ.SRS-032.ClickHouse.Parquet.SelectConversions](#rqsrs-032clickhouseparquetselectconversions)
  * 4.4 [Nested Types](#nested-types)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Arrays](#rqsrs-032clickhouseparquetnestedtypesarrays)
    * 4.4.2 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Tuple](#rqsrs-032clickhouseparquetnestedtypestuple)
    * 4.4.3 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.Map](#rqsrs-032clickhouseparquetnestedtypesmap)
    * 4.4.4 [RQ.SRS-032.ClickHouse.Parquet.NestedTypes.LowCardinalityNullable](#rqsrs-032clickhouseparquetnestedtypeslowcardinalitynullable)
  * 4.5 [Unsupported Parquet Types](#unsupported-parquet-types)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.Time32](#rqsrs-032clickhouseparquetunsupportedparquettypestime32)
    * 4.5.2 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.FixedSizeBinary](#rqsrs-032clickhouseparquetunsupportedparquettypesfixedsizebinary)
    * 4.5.3 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.JSON](#rqsrs-032clickhouseparquetunsupportedparquettypesjson)
    * 4.5.4 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.UUID](#rqsrs-032clickhouseparquetunsupportedparquettypesuuid)
    * 4.5.5 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ENUM](#rqsrs-032clickhouseparquetunsupportedparquettypesenum)
    * 4.5.6 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray](#rqsrs-032clickhouseparquetunsupportedparquettypeschunkedarray)
  * 4.6 [Table Functions](#table-functions)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL](#rqsrs-032clickhouseparquettablefunctionsurl)
    * 4.6.2 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File](#rqsrs-032clickhouseparquettablefunctionsfile)
    * 4.6.3 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3](#rqsrs-032clickhouseparquettablefunctionss3)
    * 4.6.4 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC](#rqsrs-032clickhouseparquettablefunctionsjdbc)
    * 4.6.5 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC](#rqsrs-032clickhouseparquettablefunctionsodbc)
    * 4.6.6 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS](#rqsrs-032clickhouseparquettablefunctionshdfs)
    * 4.6.7 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote](#rqsrs-032clickhouseparquettablefunctionsremote)
    * 4.6.8 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL](#rqsrs-032clickhouseparquettablefunctionsmysql)
    * 4.6.9 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgeSQL](#rqsrs-032clickhouseparquettablefunctionspostgesql)
  * 4.7 [Table Engines](#table-engines)
    * 4.7.1 [Integration Engines](#integration-engines)
      * 4.7.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquettableenginesintegrationodbc)
      * 4.7.1.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquettableenginesintegrationjdbc)
      * 4.7.1.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquettableenginesintegrationmysql)
      * 4.7.1.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquettableenginesintegrationmongodb)
      * 4.7.1.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquettableenginesintegrationhdfs)
      * 4.7.1.6 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3](#rqsrs-032clickhouseparquettableenginesintegrations3)
      * 4.7.1.7 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquettableenginesintegrationkafka)
      * 4.7.1.8 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquettableenginesintegrationembeddedrocksdb)
      * 4.7.1.9 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquettableenginesintegrationpostgresql)
    * 4.7.2 [Special Engines](#special-engines)
      * 4.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquettableenginesspecialdistributed)
      * 4.7.2.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquettableenginesspecialdictionary)
      * 4.7.2.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File](#rqsrs-032clickhouseparquettableenginesspecialfile)
      * 4.7.2.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL](#rqsrs-032clickhouseparquettableenginesspecialurl)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `Parquet` data format in [ClickHouse].

## Feature Diagram

![Generated using code in flowchart_code.md](parquet_flowchart.jpg)

Generated using code in flowchart_code.md

## Requirements

### General

#### RQ.SRS-032.ClickHouse.Parquet
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

#### RQ.SRS-032.ClickHouse.Parquet.Null
version:1.0

[ClickHouse] SHALL support Null and Nullable(type) data when reading or writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Encryption
version: 1.0

[ClickHouse] MAY not support reading encrypted Parquet files.

### INSERT

#### RQ.SRS-032.ClickHouse.Parquet.Insert
version: 1.0

[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to
read data from Parquet files and insert data into tables or table functions.

#### RQ.SRS-032.ClickHouse.Parquet.Insert.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

#### Compression

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.None
version: 1.0

[ClickHouse] SHALL support reading uncompressed Parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Gzip
version: 1.0

[ClickHouse] SHALL support reading Parquet files compressed using gzip.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Brotli
version: 1.0

[ClickHouse] SHALL support reading Parquet files compressed using brotli.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4
version: 1.0

[ClickHouse] SHALL support reading Parquet files compressed using lz4.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Compression.Lz4Raw
version: 1.0

[ClickHouse] SHALL support reading Parquet files compressed using lz4_raw.

#### Unsupported Compression

##### RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Snappy
version: 1.0

[ClickHouse] MAY not support reading Parquet files compressed using snapy.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Lzo
version: 1.0

[ClickHouse] MAY not support reading Parquet files compressed using lzo.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.UnsupportedCompression.Zstd
version: 1.0

[ClickHouse] MAY not support reading Parquet files compressed using zstd.

#### INSERT Settings

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference
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

#### RQ.SRS-032.ClickHouse.Parquet.Select
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file.
```bash
clickhouse-client --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}
```

#### RQ.SRS-032.ClickHouse.Parquet.Select.Join
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT` query with a `JOIN` clause into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Select.Union
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT` query with a `UNION` clause into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Select.View
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT * FROM {view_name}` query into a Parquet file.

#### RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT * FROM {mat_view_name}` query into a Parquet file.

#### SELECT Settings

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.
Default: `1000000`

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString
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

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray
version:1.0

[ClickHouse] MAY not support Parquet chunked arrays.

### Table Functions

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL
version: 1.0

[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgeSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.

### Table Engines

#### Integration Engines

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from an `ODBC` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `JDBC` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `MySQL` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `MongoDB` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `HDFS` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from an `S3` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `Kafka` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from an `EmbeddedRocksDB` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `PostgreSQL` table engine.

#### Special Engines

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `Distributed` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `Dictionary` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `File` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `URL` table engine.

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md 
[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
