# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230315.1003122.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Parquet = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Parquet` data format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.1'
)

RQ_SRS_032_ClickHouse_Parquet_ClickHouseLocal = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the usage of `clickhouse-local` with `Parquet` data format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.2'
)

RQ_SRS_032_ClickHouse_Parquet_Encryption = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encryption',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support reading encrypted Parquet files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.3'
)

RQ_SRS_032_ClickHouse_Parquet_Chunks = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Chunks',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support chunked `Parquet` files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.1.4'
)

RQ_SRS_032_ClickHouse_Parquet_Compression_None = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Compression.None',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading or writing uncompressed Parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.5.1'
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading or writing Parquet files compressed using gzip.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.5.2'
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading or writing Parquet files compressed using brotli.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.5.3'
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4 = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading or writing Parquet files compressed using lz4.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.5.4'
)

RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading or writing Parquet files compressed using lz4_raw.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.5.5'
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support reading or writing Parquet files compressed using snapy.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.6.1'
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Lzo = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support reading or writing Parquet files compressed using lzo.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.6.2'
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Zstd = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support reading or writing Parquet files compressed using zstd.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.1.6.3'
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_Read = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.Read',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading the following Parquet data types:\n'
        'Parquet Decimal is currently not tested.\n'
        '\n'
        '\n'
        '| Parquet data type (INSERT)                    | ClickHouse data type                  |\n'
        '|-----------------------------------------------|---------------------------------------|\n'
        '| `BOOL`                                        | `Bool`                                |\n'
        '| `UINT8`, `BOOL`                               | `UInt8`                               |\n'
        '| `INT8`                                        | \t`Int8`/`Enum8`                       |\n'
        '| `UINT16`                                      | `UInt16`                              |\n'
        '| `INT16`                                       | `Int16`/`Enum16`                      |\n'
        '| `UINT32`                                      | `UInt32`                              |\n'
        '| `INT32`                                       | \t`Int32`                              |\n'
        '| `UINT64`                                      | `UInt64`                              |\n'
        '| `INT64`                                       | \t`Int64`                              |\n'
        '| `FLOAT`                                       | `Float32`                             |\n'
        '| `DOUBLE`                                      | \t`Float64`                            |\n'
        '| `DATE`                                        | \t`Date32`                             |\n'
        '| `TIME (ms)`                                   | \t`DateTime`                           |\n'
        '| `TIMESTAMP`, `TIME (us, ns)`                  | `DateTime64`                          |\n'
        '| `STRING`, `BINARY`                            | `String`                              |\n'
        '| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `FixedString`                         |\n'
        '| `DECIMAL`                                     | \t`Decimal`                            |\n'
        '| `LIST`                                        | `Array`                               |\n'
        '| `STRUCT`                                      | `Tuple`                               |\n'
        '| `MAP`                                         | `Map`                                 |\n'
        '| `UINT32`                                      | \t`IPv4`                               |\n'
        '| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                                |\n'
        '| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`/`UInt128`/`Int256`/`UInt256` |\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ReadNested = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNested',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse]  SHALL support reading nested: `Array`, `Tuple` and `Map` datatypes in parquet files.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.2'
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_ReadNullable = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNullable',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support reading `Nullable` datatypes in parquet files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.3'
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_Write = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.Write',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing the following datatypes to Parquet:\n'
        '\n'
        '\n'
        '| Parquet data type (SELECT) | ClickHouse data type                  |\n'
        '|----------------------------|---------------------------------------|\n'
        '| `BOOL`                     | `Bool`                                |\n'
        '| `UINT8`                    | `UInt8`                               |\n'
        '| `INT8`                     | `Int8`/`Enum8`                        |\n'
        '| `UINT16`                   | `UInt16`                              |\n'
        '| `INT16`                    | \t`Int16`/`Enum16`                     |\n'
        '| `UINT32`                   | \t`UInt32`                             |\n'
        '| `INT32`                    | \t`Int32`                              |\n'
        '| `UINT64`                   | \t`UInt64`                             |\n'
        '| `INT64`                    | `Int64`                               |\n'
        '| `FLOAT`                    | \t`Float32`                            |\n'
        '| `DOUBLE`                   | \t`Float64`                            |\n'
        '| `DATE`                     | `Date32`                              |\n'
        '| `UINT32`                   | \t`DateTime`                           |\n'
        '| `TIMESTAMP`                | \t`DateTime64`                         |\n'
        '| `BINARY`                   | \t`String`                             |\n'
        '| `FIXED_LENGTH_BYTE_ARRAY`  | `FixedString`                         |\n'
        '| `DECIMAL`                  | \t`Decimal`                            |\n'
        '| `LIST`                     | \t`Array`                              |\n'
        '| `STRUCT`                   | `Tuple`                               |\n'
        '| `MAP`                      | `Map`                                 |\n'
        '| `UINT32`                   | `IPv4`                                |\n'
        '| `FIXED_LENGTH_BYTE_ARRAY`  | \t`IPv6`                               |\n'
        '| `FIXED_LENGTH_BYTE_ARRAY`  | `Int128`/`UInt128`/`Int256`/`UInt256` |\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.4'
)

RQ_SRS_032_ClickHouse_Parquet_DataTypes_WriteNested = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.WriteNested',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writings nested: `Array`, `Tuple` and `Map` datatypes in parquet files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.5'
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support the following Parquet types:\n'
        '\n'
        '- `Time32`\n'
        '- `Fixed_Size_Binary`\n'
        '- `JSON`\n'
        '- `UUID`\n'
        '- `ENUM`\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ChunkedArray = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] MAY not support Parquet chunked arrays.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.2'
)

RQ_SRS_032_ClickHouse_Parquet_Insert = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to\n'
        'read data from Parquet files and insert data into tables or table functions.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.1'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Projections = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.Projections',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.2'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_SkipColumns = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.SkipColumns',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support skipping unexistent columns when reading from parquet files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.3'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_SkipValues = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.SkipValues',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support skipping unexistent values when reading from parquet files.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.4'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_AutoTypecast = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.AutoTypecast',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL automatically typecast parquet datatype based on the types in the target table.\\\n'
        '\n'
        'Example:\n'
        '\n'
        'When we take the following parquet file:\n'
        '\n'
        '```\n'
        '┌─path────────────────────────────────────────────────────────────┬─date───────┬──hits─┐\n'
        '│ Akiba_Hebrew_Academy                                            │ 2017-08-01 │   241 │\n'
        '│ 1980_Rugby_League_State_of_Origin_match                         │ 2017-07-01 │     2 │\n'
        '│ Column_of_Santa_Felicita,_Florence                              │ 2017-06-01 │    14 │\n'
        '└─────────────────────────────────────────────────────────────────┴────────────┴───────┘\n'
        '```\n'
        '\n'
        '```\n'
        '┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐\n'
        '│ path │ Nullable(String) │              │                    │         │                  │                │\n'
        '│ date │ Nullable(String) │              │                    │         │                  │                │\n'
        '│ hits │ Nullable(Int64)  │              │                    │         │                  │                │\n'
        '└──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘\n'
        '```\n'
        '\n'
        '\n'
        'Then create a table to import parquet data to:\n'
        '```sql\n'
        'CREATE TABLE sometable\n'
        '(\n'
        '    `path` String,\n'
        '    `date` Date,\n'
        '    `hits` UInt32\n'
        ')\n'
        'ENGINE = MergeTree\n'
        'ORDER BY (date, path)\n'
        '```\n'
        '\n'
        'Then import data using a FROM INFILE clause:\n'
        '\n'
        '\n'
        '```sql\n'
        'INSERT INTO sometable\n'
        "FROM INFILE 'data.parquet' FORMAT Parquet;\n"
        '```\n'
        '\n'
        'As a result ClickHouse automatically converted parquet `strings` (in the `date` column) to the `Date` type.\n'
        '\n'
        '\n'
        '```sql\n'
        'DESCRIBE TABLE sometable\n'
        '```\n'
        '\n'
        '```\n'
        '┌─name─┬─type───┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐\n'
        '│ path │ String │              │                    │         │                  │                │\n'
        '│ date │ Date   │              │                    │         │                  │                │\n'
        '│ hits │ UInt32 │              │                    │         │                  │                │\n'
        '└──────┴────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.5'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_ImportNested = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of\n'
        'nested structs into Nested tables.\\\n'
        'Default: `0`\n'
        '\n'
        '- `0` — Data can not be inserted into Nested columns as an array of structs.\n'
        '- `1` — Data can be inserted into Nested columns as an array of structs.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.4.6.1'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_CaseInsensitiveColumnMatching = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching\n'
        'Parquet and ClickHouse columns.\\\n'
        'Default: `false`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.4.6.2'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_AllowMissingColumns = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.\\\n'
        'Default: `false`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.4.6.3'
)

RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`\n'
        'to allow skipping unsupported types.\\\n'
        'Default: `false`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.4.6.4'
)

RQ_SRS_032_ClickHouse_Parquet_Select = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file.\n'
        '```bash\n'
        'clickhouse-client --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}\n'
        '```\n'
        'OR\n'
        '```bash\n'
        'clickhouse-local --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.1'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Outfile = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Outfile',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file using `OUTFILE` clause.\n'
        '\n'
        '```sql\n'
        'SELECT *\n'
        'FROM sometable\n'
        "INTO OUTFILE 'export.parquet'\n"
        'FORMAT Parquet\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.2'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Join = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Join',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT` query with a `JOIN` clause into a Parquet file.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.3'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Union = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Union',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT` query with a `UNION` clause into a Parquet file.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.4'
)

RQ_SRS_032_ClickHouse_Parquet_Select_View = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.View',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT * FROM {view_name}` query into a Parquet file.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.5'
)

RQ_SRS_032_ClickHouse_Parquet_Select_MaterializedView = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support writing output of `SELECT * FROM {mat_view_name}` query into a Parquet file.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.6'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_RowGroupSize = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.\\\n'
        'Default: `1000000`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.5.7.1'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsString = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.\\\n'
        'Default: `false`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.5.7.2'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsFixedByteArray = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsFixedByteArray',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `output_format_parquet_fixed_string_as_fixed_byte_array` to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns.\\\n'
        'Default: `true`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.5.7.3'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_ParquetVersion = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.ParquetVersion',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `output_format_parquet_version` to see the version of Parquet format used in output format.\\\n'
        'Default: `2.latest`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.5.7.4'
)

RQ_SRS_032_ClickHouse_Parquet_Select_Settings_CompressionMethod = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.CompressionMethod',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `output_format_parquet_compression_method` to see the compression method used in output Parquet format.\\\n'
        'Default: `lz4`\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.5.7.5'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `url` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.1'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `file` table function reading and writing Parquet format.\n'
        '\n'
        'Example:\n'
        '```sql\n'
        "SELECT * FROM file('data.parquet', Parquet)\n"
        '```\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.2'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_S3 = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.\n'
        '\n'
        '```sql\n'
        'SELECT *\n'
        "FROM gcs('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)\n"
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.3'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_JDBC = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.4'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_ODBC = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.5'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_HDFS = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.6'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_Remote = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.7'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_MySQL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.\n'
        '\n'
        'Example:\n'
        '\n'
        'Given we have a [ClickHouse] table with a `mysql` engine:\n'
        '```sql\n'
        'CREATE TABLE mysql_table1 (\n'
        '  id UInt64,\n'
        '  column1 String\n'
        ')\n'
        "ENGINE = MySQL('mysql-host.domain.com','db1','table1','mysql_clickhouse','Password123!')\n"
        '```\n'
        'We can write to a parquet file format with:\n'
        '\n'
        '```sql\n'
        'SELECT * FROM mysql_table1 INTO OUTFILE testTable.parquet FORMAT Parquet\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.8'
)

RQ_SRS_032_ClickHouse_Parquet_TableFunctions_PostgreSQL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.9'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_MergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `MergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.1'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplicatedMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `ReplicatedMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.2'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_ReplacingMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `ReplacingMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.3'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_SummingMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `SummingMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.4'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_AggregatingMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `AggregatingMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.5'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_CollapsingMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `CollapsingMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.6'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_VersionedCollapsingMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `VersionedCollapsingMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.7'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_MergeTree_GraphiteMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `GraphiteMergeTree` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.1.8'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_ODBC = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from an `ODBC` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.1'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_JDBC = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `JDBC` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.2'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MySQL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `MySQL` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.3'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_MongoDB = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `MongoDB` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.4'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_HDFS = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `HDFS` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.5'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_S3 = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from an `S3` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.6'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_Kafka = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `Kafka` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.7'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_EmbeddedRocksDB = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from an `EmbeddedRocksDB` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.8'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Integration_PostgreSQL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `PostgreSQL` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.2.9'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Memory = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `Memory` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.3.1'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Distributed = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `Distributed` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.3.2'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_Dictionary = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `Dictionary` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.3.3'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_File = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `File` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.3.4'
)

RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support Parquet format being writen into and read from a `URL` table engine.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.7.3.5'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL be accessed via `ParquetMetadata` argument.\n'
        '```sql\n'
        'SELECT * FROM file(data.parquet, ParquetMetadata) format PrettyJSONEachRow\n'
        '```\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.3.1'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_File = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.File',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support accessing parquet `file metadata`.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.3.2'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Column = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.Column',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support accessing parquet `column (chunk) metadata`.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.3.3'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_Header = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.Header',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support accessing parquet `page header metadata`.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.3.4'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_MissingMagicNumber = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error if the 4-byte magic number "PAR1" is missing from the parquet metadata.\n'
        '\n'
        'Example:\n'
        '\n'
        'When using hexeditor on the parquet file we alter the values of "PAR1" and change it to "PARQ".\n'
        '\n'
        'Then try to read that parquet file in [ClickHouse].\n'
        '\n'
        'We get an exception:  \n'
        '```\n'
        'exception. Code: 1001, type: parquet::ParquetInvalidOrCorruptedFileException, \n'
        'e.what() = Invalid: Parquet magic bytes not found in footer. \n'
        'Either the file is corrupted or this is not a parquet file.\n'
        '```\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.4.1'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptFile = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error when trying to access the corrupt `file` metadata. In this case the file metadata is corrupt, the file is lost.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.4.2'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumn = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error when trying to access the corrupt `column` metadata.In this case that column chunk is lost (but column chunks for this column in other row groups are okay).\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.4.3'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageHeader = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error when trying to access the corrupt `Page Header`. In this case the remaining pages in that chunk are lost.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.4.4'
)

RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageData = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL output an error when trying to access the corrupt `Page Data`. In this case that page is lost.\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.8.4.5'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_Plain = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.Plain',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Plain` encoded parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.9.4.1'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_RunLength = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.RunLength',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Run Length Encoding / Bit-Packing Hybrid` encoded parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.9.4.2'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_Delta = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.Delta',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Delta Encoding` encoded parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.9.4.3'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_DeltaLengthByteArray = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaLengthByteArray',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Delta-length byte array` encoded parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.9.4.4'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_DeltaStrings = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaStrings',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Delta Strings` encoded parquet files.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.9.4.5'
)

RQ_SRS_032_ClickHouse_Parquet_Encoding_ByteStreamSplit = Requirement(
    name='RQ.SRS-032.ClickHouse.Parquet.Encoding.ByteStreamSplit',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `Byte Stream Split` encoded parquet files.\n'
        '\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md \n'
        '[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md\n'
        '[Git]: https://git-scm.com/\n'
        '[GitHub]: https://github.com\n'
    ),
    link=None,
    level=4,
    num='4.9.4.6'
)

SRS032_ClickHouse_Parquet_Data_Format = Specification(
    name='SRS032 ClickHouse Parquet Data Format',
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
        Heading(name='Revision History', level=1, num='1'),
        Heading(name='Introduction', level=1, num='2'),
        Heading(name='Feature Diagram', level=1, num='3'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='General', level=2, num='4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet', level=3, num='4.1.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal', level=3, num='4.1.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encryption', level=3, num='4.1.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Chunks', level=3, num='4.1.4'),
        Heading(name='Compression', level=3, num='4.1.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Compression.None', level=4, num='4.1.5.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip', level=4, num='4.1.5.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli', level=4, num='4.1.5.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4', level=4, num='4.1.5.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw', level=4, num='4.1.5.5'),
        Heading(name='Unsupported Compression', level=3, num='4.1.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy', level=4, num='4.1.6.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo', level=4, num='4.1.6.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd', level=4, num='4.1.6.3'),
        Heading(name='Data Types', level=2, num='4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.Read', level=3, num='4.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNested', level=3, num='4.2.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNullable', level=3, num='4.2.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.Write', level=3, num='4.2.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.DataTypes.WriteNested', level=3, num='4.2.5'),
        Heading(name='Unsupported Parquet Types', level=2, num='4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes', level=3, num='4.3.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray', level=3, num='4.3.2'),
        Heading(name='INSERT', level=2, num='4.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert', level=3, num='4.4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.Projections', level=3, num='4.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.SkipColumns', level=3, num='4.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.SkipValues', level=3, num='4.4.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.AutoTypecast', level=3, num='4.4.5'),
        Heading(name='INSERT Settings', level=3, num='4.4.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested', level=4, num='4.4.6.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching', level=4, num='4.4.6.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns', level=4, num='4.4.6.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference', level=4, num='4.4.6.4'),
        Heading(name='SELECT', level=2, num='4.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select', level=3, num='4.5.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Outfile', level=3, num='4.5.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Join', level=3, num='4.5.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Union', level=3, num='4.5.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.View', level=3, num='4.5.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView', level=3, num='4.5.6'),
        Heading(name='SELECT Settings', level=3, num='4.5.7'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize', level=4, num='4.5.7.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString', level=4, num='4.5.7.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsFixedByteArray', level=4, num='4.5.7.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.ParquetVersion', level=4, num='4.5.7.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Select.Settings.CompressionMethod', level=4, num='4.5.7.5'),
        Heading(name='Table Functions', level=2, num='4.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL', level=3, num='4.6.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File', level=3, num='4.6.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3', level=3, num='4.6.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC', level=3, num='4.6.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC', level=3, num='4.6.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS', level=3, num='4.6.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote', level=3, num='4.6.7'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL', level=3, num='4.6.8'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL', level=3, num='4.6.9'),
        Heading(name='Table Engines', level=2, num='4.7'),
        Heading(name='MergeTree', level=3, num='4.7.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree', level=4, num='4.7.1.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree', level=4, num='4.7.1.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree', level=4, num='4.7.1.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree', level=4, num='4.7.1.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree', level=4, num='4.7.1.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree', level=4, num='4.7.1.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree', level=4, num='4.7.1.7'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree', level=4, num='4.7.1.8'),
        Heading(name='Integration Engines', level=3, num='4.7.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC', level=4, num='4.7.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC', level=4, num='4.7.2.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL', level=4, num='4.7.2.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB', level=4, num='4.7.2.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS', level=4, num='4.7.2.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3', level=4, num='4.7.2.6'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka', level=4, num='4.7.2.7'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB', level=4, num='4.7.2.8'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL', level=4, num='4.7.2.9'),
        Heading(name='Special Engines', level=3, num='4.7.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory', level=4, num='4.7.3.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed', level=4, num='4.7.3.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary', level=4, num='4.7.3.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File', level=4, num='4.7.3.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL', level=4, num='4.7.3.5'),
        Heading(name='Metadata', level=2, num='4.8'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata', level=4, num='4.8.3.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.File', level=4, num='4.8.3.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.Column', level=4, num='4.8.3.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.Header', level=4, num='4.8.3.4'),
        Heading(name='Error Recovery', level=3, num='4.8.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber', level=4, num='4.8.4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile', level=4, num='4.8.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn', level=4, num='4.8.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader', level=4, num='4.8.4.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData', level=4, num='4.8.4.5'),
        Heading(name='Encoding', level=2, num='4.9'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.Plain', level=4, num='4.9.4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.RunLength', level=4, num='4.9.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.Delta', level=4, num='4.9.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaLengthByteArray', level=4, num='4.9.4.4'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaStrings', level=4, num='4.9.4.5'),
        Heading(name='RQ.SRS-032.ClickHouse.Parquet.Encoding.ByteStreamSplit', level=4, num='4.9.4.6'),
        ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet,
        RQ_SRS_032_ClickHouse_Parquet_ClickHouseLocal,
        RQ_SRS_032_ClickHouse_Parquet_Encryption,
        RQ_SRS_032_ClickHouse_Parquet_Chunks,
        RQ_SRS_032_ClickHouse_Parquet_Compression_None,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Brotli,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4,
        RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4Raw,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Snappy,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Lzo,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedCompression_Zstd,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_Read,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ReadNested,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_ReadNullable,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_Write,
        RQ_SRS_032_ClickHouse_Parquet_DataTypes_WriteNested,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes,
        RQ_SRS_032_ClickHouse_Parquet_UnsupportedParquetTypes_ChunkedArray,
        RQ_SRS_032_ClickHouse_Parquet_Insert,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Projections,
        RQ_SRS_032_ClickHouse_Parquet_Insert_SkipColumns,
        RQ_SRS_032_ClickHouse_Parquet_Insert_SkipValues,
        RQ_SRS_032_ClickHouse_Parquet_Insert_AutoTypecast,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Insert_Settings_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_Select,
        RQ_SRS_032_ClickHouse_Parquet_Select_Outfile,
        RQ_SRS_032_ClickHouse_Parquet_Select_Join,
        RQ_SRS_032_ClickHouse_Parquet_Select_Union,
        RQ_SRS_032_ClickHouse_Parquet_Select_View,
        RQ_SRS_032_ClickHouse_Parquet_Select_MaterializedView,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsString,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_StringAsFixedByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_ParquetVersion,
        RQ_SRS_032_ClickHouse_Parquet_Select_Settings_CompressionMethod,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_TableFunctions_File,
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
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_File,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Column,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_Header,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_MissingMagicNumber,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptFile,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptColumn,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageHeader,
        RQ_SRS_032_ClickHouse_Parquet_Metadata_ErrorRecovery_CorruptPageData,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_Plain,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_RunLength,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_Delta,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_DeltaLengthByteArray,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_DeltaStrings,
        RQ_SRS_032_ClickHouse_Parquet_Encoding_ByteStreamSplit,
        ),
    content='''
# SRS032 ClickHouse Parquet Data Format
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Feature Diagram](#feature-diagram)
* 4 [Requirements](#requirements)
  * 4.1 [General](#general)
    * 4.1.1 [RQ.SRS-032.ClickHouse.Parquet](#rqsrs-032clickhouseparquet)
    * 4.1.2 [RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal](#rqsrs-032clickhouseparquetclickhouselocal)
    * 4.1.3 [RQ.SRS-032.ClickHouse.Parquet.Encryption](#rqsrs-032clickhouseparquetencryption)
    * 4.1.4 [RQ.SRS-032.ClickHouse.Parquet.Chunks](#rqsrs-032clickhouseparquetchunks)
    * 4.1.5 [Compression](#compression)
      * 4.1.5.1 [RQ.SRS-032.ClickHouse.Parquet.Compression.None](#rqsrs-032clickhouseparquetcompressionnone)
      * 4.1.5.2 [RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip](#rqsrs-032clickhouseparquetcompressiongzip)
      * 4.1.5.3 [RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli](#rqsrs-032clickhouseparquetcompressionbrotli)
      * 4.1.5.4 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4](#rqsrs-032clickhouseparquetcompressionlz4)
      * 4.1.5.5 [RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw](#rqsrs-032clickhouseparquetcompressionlz4raw)
    * 4.1.6 [Unsupported Compression](#unsupported-compression)
      * 4.1.6.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy](#rqsrs-032clickhouseparquetunsupportedcompressionsnappy)
      * 4.1.6.2 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo](#rqsrs-032clickhouseparquetunsupportedcompressionlzo)
      * 4.1.6.3 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd](#rqsrs-032clickhouseparquetunsupportedcompressionzstd)
  * 4.2 [Data Types](#data-types)
    * 4.2.1 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.Read](#rqsrs-032clickhouseparquetdatatypesread)
    * 4.2.2 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNested](#rqsrs-032clickhouseparquetdatatypesreadnested)
    * 4.2.3 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNullable](#rqsrs-032clickhouseparquetdatatypesreadnullable)
    * 4.2.4 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.Write](#rqsrs-032clickhouseparquetdatatypeswrite)
    * 4.2.5 [RQ.SRS-032.ClickHouse.Parquet.DataTypes.WriteNested](#rqsrs-032clickhouseparquetdatatypeswritenested)
  * 4.3 [Unsupported Parquet Types](#unsupported-parquet-types)
    * 4.3.1 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes](#rqsrs-032clickhouseparquetunsupportedparquettypes)
    * 4.3.2 [RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray](#rqsrs-032clickhouseparquetunsupportedparquettypeschunkedarray)
  * 4.4 [INSERT](#insert)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Parquet.Insert](#rqsrs-032clickhouseparquetinsert)
    * 4.4.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.Projections](#rqsrs-032clickhouseparquetinsertprojections)
    * 4.4.3 [RQ.SRS-032.ClickHouse.Parquet.Insert.SkipColumns](#rqsrs-032clickhouseparquetinsertskipcolumns)
    * 4.4.4 [RQ.SRS-032.ClickHouse.Parquet.Insert.SkipValues](#rqsrs-032clickhouseparquetinsertskipvalues)
    * 4.4.5 [RQ.SRS-032.ClickHouse.Parquet.Insert.AutoTypecast](#rqsrs-032clickhouseparquetinsertautotypecast)
    * 4.4.6 [INSERT Settings](#insert-settings)
      * 4.4.6.1 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested](#rqsrs-032clickhouseparquetinsertsettingsimportnested)
      * 4.4.6.2 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetinsertsettingscaseinsensitivecolumnmatching)
      * 4.4.6.3 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns](#rqsrs-032clickhouseparquetinsertsettingsallowmissingcolumns)
      * 4.4.6.4 [RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetinsertsettingsskipcolumnswithunsupportedtypesinschemainference)
  * 4.5 [SELECT](#select)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Parquet.Select](#rqsrs-032clickhouseparquetselect)
    * 4.5.2 [RQ.SRS-032.ClickHouse.Parquet.Select.Outfile](#rqsrs-032clickhouseparquetselectoutfile)
    * 4.5.3 [RQ.SRS-032.ClickHouse.Parquet.Select.Join](#rqsrs-032clickhouseparquetselectjoin)
    * 4.5.4 [RQ.SRS-032.ClickHouse.Parquet.Select.Union](#rqsrs-032clickhouseparquetselectunion)
    * 4.5.5 [RQ.SRS-032.ClickHouse.Parquet.Select.View](#rqsrs-032clickhouseparquetselectview)
    * 4.5.6 [RQ.SRS-032.ClickHouse.Parquet.Select.MaterializedView](#rqsrs-032clickhouseparquetselectmaterializedview)
    * 4.5.7 [SELECT Settings](#select-settings)
      * 4.5.7.1 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.RowGroupSize](#rqsrs-032clickhouseparquetselectsettingsrowgroupsize)
      * 4.5.7.2 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString](#rqsrs-032clickhouseparquetselectsettingsstringasstring)
      * 4.5.7.3 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsFixedByteArray](#rqsrs-032clickhouseparquetselectsettingsstringasfixedbytearray)
      * 4.5.7.4 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.ParquetVersion](#rqsrs-032clickhouseparquetselectsettingsparquetversion)
      * 4.5.7.5 [RQ.SRS-032.ClickHouse.Parquet.Select.Settings.CompressionMethod](#rqsrs-032clickhouseparquetselectsettingscompressionmethod)
  * 4.6 [Table Functions](#table-functions)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL](#rqsrs-032clickhouseparquettablefunctionsurl)
    * 4.6.2 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File](#rqsrs-032clickhouseparquettablefunctionsfile)
    * 4.6.3 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3](#rqsrs-032clickhouseparquettablefunctionss3)
    * 4.6.4 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.JDBC](#rqsrs-032clickhouseparquettablefunctionsjdbc)
    * 4.6.5 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.ODBC](#rqsrs-032clickhouseparquettablefunctionsodbc)
    * 4.6.6 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.HDFS](#rqsrs-032clickhouseparquettablefunctionshdfs)
    * 4.6.7 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.Remote](#rqsrs-032clickhouseparquettablefunctionsremote)
    * 4.6.8 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.MySQL](#rqsrs-032clickhouseparquettablefunctionsmysql)
    * 4.6.9 [RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL](#rqsrs-032clickhouseparquettablefunctionspostgresql)
  * 4.7 [Table Engines](#table-engines)
    * 4.7.1 [MergeTree](#mergetree)
      * 4.7.1.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree](#rqsrs-032clickhouseparquettableenginesmergetreemergetree)
      * 4.7.1.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplicatedmergetree)
      * 4.7.1.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreereplacingmergetree)
      * 4.7.1.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreesummingmergetree)
      * 4.7.1.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeaggregatingmergetree)
      * 4.7.1.6 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreecollapsingmergetree)
      * 4.7.1.7 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreeversionedcollapsingmergetree)
      * 4.7.1.8 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree](#rqsrs-032clickhouseparquettableenginesmergetreegraphitemergetree)
    * 4.7.2 [Integration Engines](#integration-engines)
      * 4.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquettableenginesintegrationodbc)
      * 4.7.2.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquettableenginesintegrationjdbc)
      * 4.7.2.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquettableenginesintegrationmysql)
      * 4.7.2.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquettableenginesintegrationmongodb)
      * 4.7.2.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquettableenginesintegrationhdfs)
      * 4.7.2.6 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.S3](#rqsrs-032clickhouseparquettableenginesintegrations3)
      * 4.7.2.7 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquettableenginesintegrationkafka)
      * 4.7.2.8 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquettableenginesintegrationembeddedrocksdb)
      * 4.7.2.9 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquettableenginesintegrationpostgresql)
    * 4.7.3 [Special Engines](#special-engines)
      * 4.7.3.1 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory](#rqsrs-032clickhouseparquettableenginesspecialmemory)
      * 4.7.3.2 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquettableenginesspecialdistributed)
      * 4.7.3.3 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquettableenginesspecialdictionary)
      * 4.7.3.4 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.File](#rqsrs-032clickhouseparquettableenginesspecialfile)
      * 4.7.3.5 [RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.URL](#rqsrs-032clickhouseparquettableenginesspecialurl)
  * 4.8 [Metadata](#metadata)
      * 4.8.3.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata](#rqsrs-032clickhouseparquetmetadataparquetmetadata)
      * 4.8.3.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.File](#rqsrs-032clickhouseparquetmetadatafile)
      * 4.8.3.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Column](#rqsrs-032clickhouseparquetmetadatacolumn)
      * 4.8.3.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.Header](#rqsrs-032clickhouseparquetmetadataheader)
    * 4.8.4 [Error Recovery](#error-recovery)
      * 4.8.4.1 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber](#rqsrs-032clickhouseparquetmetadataerrorrecoverymissingmagicnumber)
      * 4.8.4.2 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptfile)
      * 4.8.4.3 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptcolumn)
      * 4.8.4.4 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptpageheader)
      * 4.8.4.5 [RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData](#rqsrs-032clickhouseparquetmetadataerrorrecoverycorruptpagedata)
  * 4.9 [Encoding](#encoding)
      * 4.9.4.1 [RQ.SRS-032.ClickHouse.Parquet.Encoding.Plain](#rqsrs-032clickhouseparquetencodingplain)
      * 4.9.4.2 [RQ.SRS-032.ClickHouse.Parquet.Encoding.RunLength](#rqsrs-032clickhouseparquetencodingrunlength)
      * 4.9.4.3 [RQ.SRS-032.ClickHouse.Parquet.Encoding.Delta](#rqsrs-032clickhouseparquetencodingdelta)
      * 4.9.4.4 [RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaLengthByteArray](#rqsrs-032clickhouseparquetencodingdeltalengthbytearray)
      * 4.9.4.5 [RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaStrings](#rqsrs-032clickhouseparquetencodingdeltastrings)
      * 4.9.4.6 [RQ.SRS-032.ClickHouse.Parquet.Encoding.ByteStreamSplit](#rqsrs-032clickhouseparquetencodingbytestreamsplit)


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

![Generated using code in flowchart_code.md](parquet_flowchart.jpg)

Generated using code in flowchart_code.txt

## Requirements

### General

#### RQ.SRS-032.ClickHouse.Parquet
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

#### RQ.SRS-032.ClickHouse.Parquet.ClickHouseLocal
version: 1.0

[ClickHouse] SHALL support the usage of `clickhouse-local` with `Parquet` data format.

#### RQ.SRS-032.ClickHouse.Parquet.Encryption
version: 1.0

[ClickHouse] MAY not support reading encrypted Parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Chunks
version: 1.0

[ClickHouse] SHALL support chunked `Parquet` files.

#### Compression

##### RQ.SRS-032.ClickHouse.Parquet.Compression.None
version: 1.0

[ClickHouse] SHALL support reading or writing uncompressed Parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Gzip
version: 1.0

[ClickHouse] SHALL support reading or writing Parquet files compressed using gzip.

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Brotli
version: 1.0

[ClickHouse] SHALL support reading or writing Parquet files compressed using brotli.

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4
version: 1.0

[ClickHouse] SHALL support reading or writing Parquet files compressed using lz4.

##### RQ.SRS-032.ClickHouse.Parquet.Compression.Lz4Raw
version: 1.0

[ClickHouse] SHALL support reading or writing Parquet files compressed using lz4_raw.

#### Unsupported Compression

##### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Snappy
version: 1.0

[ClickHouse] MAY not support reading or writing Parquet files compressed using snapy.

##### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Lzo
version: 1.0

[ClickHouse] MAY not support reading or writing Parquet files compressed using lzo.

##### RQ.SRS-032.ClickHouse.Parquet.UnsupportedCompression.Zstd
version: 1.0

[ClickHouse] MAY not support reading or writing Parquet files compressed using zstd.

### Data Types

#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.Read
version:1.0

[ClickHouse] SHALL support reading the following Parquet data types:
Parquet Decimal is currently not tested.


| Parquet data type (INSERT)                    | ClickHouse data type                  |
|-----------------------------------------------|---------------------------------------|
| `BOOL`                                        | `Bool`                                |
| `UINT8`, `BOOL`                               | `UInt8`                               |
| `INT8`                                        | 	`Int8`/`Enum8`                       |
| `UINT16`                                      | `UInt16`                              |
| `INT16`                                       | `Int16`/`Enum16`                      |
| `UINT32`                                      | `UInt32`                              |
| `INT32`                                       | 	`Int32`                              |
| `UINT64`                                      | `UInt64`                              |
| `INT64`                                       | 	`Int64`                              |
| `FLOAT`                                       | `Float32`                             |
| `DOUBLE`                                      | 	`Float64`                            |
| `DATE`                                        | 	`Date32`                             |
| `TIME (ms)`                                   | 	`DateTime`                           |
| `TIMESTAMP`, `TIME (us, ns)`                  | `DateTime64`                          |
| `STRING`, `BINARY`                            | `String`                              |
| `STRING`, `BINARY`, `FIXED_LENGTH_BYTE_ARRAY` | `FixedString`                         |
| `DECIMAL`                                     | 	`Decimal`                            |
| `LIST`                                        | `Array`                               |
| `STRUCT`                                      | `Tuple`                               |
| `MAP`                                         | `Map`                                 |
| `UINT32`                                      | 	`IPv4`                               |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `IPv6`                                |
| `FIXED_LENGTH_BYTE_ARRAY`, `BINARY`           | `Int128`/`UInt128`/`Int256`/`UInt256` |


#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNested
version:1.0

[ClickHouse]  SHALL support reading nested: `Array`, `Tuple` and `Map` datatypes in parquet files.


#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.ReadNullable
version:1.0

[ClickHouse] SHALL support reading `Nullable` datatypes in parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.Write
version:1.0

[ClickHouse] SHALL support writing the following datatypes to Parquet:


| Parquet data type (SELECT) | ClickHouse data type                  |
|----------------------------|---------------------------------------|
| `BOOL`                     | `Bool`                                |
| `UINT8`                    | `UInt8`                               |
| `INT8`                     | `Int8`/`Enum8`                        |
| `UINT16`                   | `UInt16`                              |
| `INT16`                    | 	`Int16`/`Enum16`                     |
| `UINT32`                   | 	`UInt32`                             |
| `INT32`                    | 	`Int32`                              |
| `UINT64`                   | 	`UInt64`                             |
| `INT64`                    | `Int64`                               |
| `FLOAT`                    | 	`Float32`                            |
| `DOUBLE`                   | 	`Float64`                            |
| `DATE`                     | `Date32`                              |
| `UINT32`                   | 	`DateTime`                           |
| `TIMESTAMP`                | 	`DateTime64`                         |
| `BINARY`                   | 	`String`                             |
| `FIXED_LENGTH_BYTE_ARRAY`  | `FixedString`                         |
| `DECIMAL`                  | 	`Decimal`                            |
| `LIST`                     | 	`Array`                              |
| `STRUCT`                   | `Tuple`                               |
| `MAP`                      | `Map`                                 |
| `UINT32`                   | `IPv4`                                |
| `FIXED_LENGTH_BYTE_ARRAY`  | 	`IPv6`                               |
| `FIXED_LENGTH_BYTE_ARRAY`  | `Int128`/`UInt128`/`Int256`/`UInt256` |


#### RQ.SRS-032.ClickHouse.Parquet.DataTypes.WriteNested
version:1.0

[ClickHouse] SHALL support writings nested: `Array`, `Tuple` and `Map` datatypes in parquet files.

### Unsupported Parquet Types

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes
version:1.0

[ClickHouse] MAY not support the following Parquet types:

- `Time32`
- `Fixed_Size_Binary`
- `JSON`
- `UUID`
- `ENUM`

#### RQ.SRS-032.ClickHouse.Parquet.UnsupportedParquetTypes.ChunkedArray
version:1.0

[ClickHouse] MAY not support Parquet chunked arrays.

### INSERT

#### RQ.SRS-032.ClickHouse.Parquet.Insert
version: 1.0

[ClickHouse] SHALL support using `INSERT` query with `FROM INFILE {file_name}` and `FORMAT Parquet` clauses to
read data from Parquet files and insert data into tables or table functions.

#### RQ.SRS-032.ClickHouse.Parquet.Insert.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

#### RQ.SRS-032.ClickHouse.Parquet.Insert.SkipColumns
version: 1.0

[ClickHouse] SHALL support skipping unexistent columns when reading from parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Insert.SkipValues
version: 1.0

[ClickHouse] SHALL support skipping unexistent values when reading from parquet files.

#### RQ.SRS-032.ClickHouse.Parquet.Insert.AutoTypecast
version: 1.0


[ClickHouse] SHALL automatically typecast parquet datatype based on the types in the target table.\

Example:

When we take the following parquet file:

```
┌─path────────────────────────────────────────────────────────────┬─date───────┬──hits─┐
│ Akiba_Hebrew_Academy                                            │ 2017-08-01 │   241 │
│ 1980_Rugby_League_State_of_Origin_match                         │ 2017-07-01 │     2 │
│ Column_of_Santa_Felicita,_Florence                              │ 2017-06-01 │    14 │
└─────────────────────────────────────────────────────────────────┴────────────┴───────┘
```

```
┌─name─┬─type─────────────┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
│ path │ Nullable(String) │              │                    │         │                  │                │
│ date │ Nullable(String) │              │                    │         │                  │                │
│ hits │ Nullable(Int64)  │              │                    │         │                  │                │
└──────┴──────────────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘
```


Then create a table to import parquet data to:
```sql
CREATE TABLE sometable
(
    `path` String,
    `date` Date,
    `hits` UInt32
)
ENGINE = MergeTree
ORDER BY (date, path)
```

Then import data using a FROM INFILE clause:


```sql
INSERT INTO sometable
FROM INFILE 'data.parquet' FORMAT Parquet;
```

As a result ClickHouse automatically converted parquet `strings` (in the `date` column) to the `Date` type.


```sql
DESCRIBE TABLE sometable
```

```
┌─name─┬─type───┬─default_type─┬─default_expression─┬─comment─┬─codec_expression─┬─ttl_expression─┐
│ path │ String │              │                    │         │                  │                │
│ date │ Date   │              │                    │         │                  │                │
│ hits │ UInt32 │              │                    │         │                  │                │
└──────┴────────┴──────────────┴────────────────────┴─────────┴──────────────────┴────────────────┘
```

#### INSERT Settings

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables.\
Default: `0`

- `0` — Data can not be inserted into Nested columns as an array of structs.
- `1` — Data can be inserted into Nested columns as an array of structs.

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns.\
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.\
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Insert.Settings.SkipColumnsWithUnsupportedTypesInSchemaInference
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`
to allow skipping unsupported types.\
Default: `false`

### SELECT

#### RQ.SRS-032.ClickHouse.Parquet.Select
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file.
```bash
clickhouse-client --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}
```
OR
```bash
clickhouse-local --query="SELECT * FROM {some_table} FORMAT Parquet" > {some_file.pq}
```

#### RQ.SRS-032.ClickHouse.Parquet.Select.Outfile
version: 1.0

[ClickHouse] SHALL support writing output of `SELECT` query into a Parquet file using `OUTFILE` clause.

```sql
SELECT *
FROM sometable
INTO OUTFILE 'export.parquet'
FORMAT Parquet
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

[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.\
Default: `1000000`

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsString
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.\
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.StringAsFixedByteArray
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_fixed_string_as_fixed_byte_array` to use Parquet FIXED_LENGTH_BYTE_ARRAY type instead of Binary/String for FixedString columns.\
Default: `true`

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.ParquetVersion
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_version` to see the version of Parquet format used in output format.\
Default: `2.latest`

##### RQ.SRS-032.ClickHouse.Parquet.Select.Settings.CompressionMethod
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_compression_method` to see the compression method used in output Parquet format.\
Default: `lz4`

### Table Functions

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function reading and writing Parquet format.

Example:
```sql
SELECT * FROM file('data.parquet', Parquet)
```


#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.

```sql
SELECT *
FROM gcs('https://storage.googleapis.com/my-test-bucket-768/data.parquet', Parquet)
```

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

Example:

Given we have a [ClickHouse] table with a `mysql` engine:
```sql
CREATE TABLE mysql_table1 (
  id UInt64,
  column1 String
)
ENGINE = MySQL('mysql-host.domain.com','db1','table1','mysql_clickhouse','Password123!')
```
We can write to a parquet file format with:

```sql
SELECT * FROM mysql_table1 INTO OUTFILE testTable.parquet FORMAT Parquet
```

#### RQ.SRS-032.ClickHouse.Parquet.TableFunctions.PostgreSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.

### Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.MergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `MergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `ReplicatedMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `ReplacingMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.SummingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `SummingMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.AggregatingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `AggregatingMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `CollapsingMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.VersionedCollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `VersionedCollapsingMergeTree` table engine.

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.MergeTree.GraphiteMergeTree
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `GraphiteMergeTree` table engine.

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

##### RQ.SRS-032.ClickHouse.Parquet.TableEngines.Special.Memory
version: 1.0

[ClickHouse] SHALL support Parquet format being writen into and read from a `Memory` table engine.

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

### Metadata


##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ParquetMetadata
version: 1.0

[ClickHouse] SHALL be accessed via `ParquetMetadata` argument.
```sql
SELECT * FROM file(data.parquet, ParquetMetadata) format PrettyJSONEachRow
```


##### RQ.SRS-032.ClickHouse.Parquet.Metadata.File
version: 1.0

[ClickHouse] SHALL support accessing parquet `file metadata`.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Column
version: 1.0

[ClickHouse] SHALL support accessing parquet `column (chunk) metadata`.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.Header
version: 1.0

[ClickHouse] SHALL support accessing parquet `page header metadata`.


#### Error Recovery
##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.MissingMagicNumber
version: 1.0

[ClickHouse] SHALL output an error if the 4-byte magic number "PAR1" is missing from the parquet metadata.

Example:

When using hexeditor on the parquet file we alter the values of "PAR1" and change it to "PARQ".

Then try to read that parquet file in [ClickHouse].

We get an exception:  
```
exception. Code: 1001, type: parquet::ParquetInvalidOrCorruptedFileException, 
e.what() = Invalid: Parquet magic bytes not found in footer. 
Either the file is corrupted or this is not a parquet file.
```


##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptFile
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `file` metadata. In this case the file metadata is corrupt, the file is lost.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptColumn
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `column` metadata.In this case that column chunk is lost (but column chunks for this column in other row groups are okay).

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageHeader
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Header`. In this case the remaining pages in that chunk are lost.

##### RQ.SRS-032.ClickHouse.Parquet.Metadata.ErrorRecovery.CorruptPageData
version: 1.0

[ClickHouse] SHALL output an error when trying to access the corrupt `Page Data`. In this case that page is lost.


### Encoding
##### RQ.SRS-032.ClickHouse.Parquet.Encoding.Plain
version: 1.0

[ClickHouse] SHALL support `Plain` encoded parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Encoding.RunLength
version: 1.0

[ClickHouse] SHALL support `Run Length Encoding / Bit-Packing Hybrid` encoded parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Encoding.Delta
version: 1.0

[ClickHouse] SHALL support `Delta Encoding` encoded parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaLengthByteArray
version: 1.0

[ClickHouse] SHALL support `Delta-length byte array` encoded parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Encoding.DeltaStrings
version: 1.0

[ClickHouse] SHALL support `Delta Strings` encoded parquet files.

##### RQ.SRS-032.ClickHouse.Parquet.Encoding.ByteStreamSplit
version: 1.0

[ClickHouse] SHALL support `Byte Stream Split` encoded parquet files.

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md 
[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
'''
)
