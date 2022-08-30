# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_Parquet_Format = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format",
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

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_ImportNested = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested",
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
    level=3,
    num="4.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_CaseInsensitiveColumnMatching = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching",
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
    level=3,
    num="4.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_AllowMissingColumns = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns",
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
    level=3,
    num="4.2.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_SkipColumnsWithUnsupportedTypesInSchemaInference = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`\n"
        "to allow skipping unsupported types.\n"
        "Default: `false`\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt8ToUInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt8ToUInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `UInt8` to ClickHouse `UInt8` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_BoolToUInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BoolToUInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Bool` to ClickHouse `UInt8` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int8ToInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int8ToInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Int8` to ClickHouse `Int8` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt16ToUInt16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt16ToUInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `UInt16` to ClickHouse `UInt16` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int16ToInt16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int16ToInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Int16` to ClickHouse `Int16` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt32ToUInt32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt32ToUInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `UInt32` to ClickHouse `UInt32` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.6",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int32ToInt32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int32ToInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Int32` to ClickHouse `Int32` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.7",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt64ToUInt64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt64ToUInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `UInt64` to ClickHouse `UInt64` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.8",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int64ToInt64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int64ToInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Int64` to ClickHouse `Int64` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.9",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_FloatToFloat32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.FloatToFloat32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Float` to ClickHouse `Float32` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.10",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_HalfFloatToFloat32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.HalfFloatToFloat32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Half_Float` to ClickHouse `Float32` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.11",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_DoubleToFloat64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DoubleToFloat64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Double` to ClickHouse `Float64` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.12",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Date32ToDate = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date32ToDate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Date32` to ClickHouse `Date` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.13",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Date64ToDateTime = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date64ToDateTime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Date64` to ClickHouse `DateTime` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.14",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_TimeStampToDateTime = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.TimeStampToDateTime",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `TimeStamp` to ClickHouse `DateTime` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.15",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_StringToString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StringToString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `String` to ClickHouse `String` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.16",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_BinaryToString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BinaryToString",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Binary` to ClickHouse `String` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.17",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_DecimalToDecimal = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DecimalToDecimal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Decimal` to ClickHouse `Decimal` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.18",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_ListToArray = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.ListToArray",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `List` to ClickHouse `Array` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.19",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_StructToTuple = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StructToTuple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Struct` to ClickHouse `Tuple` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.20",
)

RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_MapToMap = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.MapToMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert Parquet `Map` to ClickHouse `Map` in Insert queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.2.6.21",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_OutFormatParquet_RowGroupSize = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.RowGroupSize",
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

RQ_SRS_032_ClickHouse_Parquet_Format_Settings_OutFormatParquet_StringAsString = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.StringAsString",
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

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt8ToUInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt8ToUInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `UInt8` to Parquet `UInt8` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_BoolToUInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.BoolToUInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Bool` to Parquet `UInt8` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int8ToInt8 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int8ToInt8",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Int8` to Parquet `Int8` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt16ToUInt16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt16ToUInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `UInt16` to Parquet `UInt16` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int16ToInt16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int16ToInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Int16` to Parquet `Int16` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt32ToUInt32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt32ToUInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `UInt32` to Parquet `UInt32` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.6",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int32ToInt32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int32ToInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Int32` to Parquet `Int32` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.7",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt64ToUInt64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt64ToUInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `UInt64` to Parquet `UInt64` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.8",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int64ToInt64 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int64ToInt64",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Int64` to Parquet `Int64` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.9",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Float32ToFloat = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float32ToFloat",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Float32` to Parquet `Float` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.10",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Float64ToDouble = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float64ToDouble",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Float64` to Parquet `Double` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.11",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DateToUInt16 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateToUInt16",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Date` to Parquet `UInt16` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.12",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DateTimeToUInt32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateTimeToUInt32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `DateTime` to Parquet `UInt32` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.13",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_StringToBinary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.StringToBinary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `String` to Parquet `Binary` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.14",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_FixedStringToBinary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.FixedStringToBinary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `FixedString` to Parquet `Binary` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.15",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DecimalToDecimal = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DecimalToDecimal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Decimal` to Parquet `Decimal` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.16",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_ArrayToList = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.ArrayToList",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Array` to Parquet `List` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.17",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_TupleToStruct = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.TupleToStruct",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Tuple` to Parquet `Struct` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.18",
)

RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_MapToMap = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.MapToMap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL convert ClickHouse `Map` to Parquet `Map` in Select queries.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.4.19",
)

RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Arrays = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support nested `arrays`.\n" "\n"),
    link=None,
    level=4,
    num="4.4.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Tuple = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support nested `tuples`.\n" "\n"),
    link=None,
    level=4,
    num="4.4.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Map = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL support nested `maps`.\n" "\n"),
    link=None,
    level=4,
    num="4.4.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_Time32 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL not support Parquet `Time32` type.\n" "\n"),
    link=None,
    level=4,
    num="4.5.4.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_FixedSizeBinary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support Parquet `Fixed_Size_Binary` type.\n" "\n"
    ),
    link=None,
    level=4,
    num="4.5.4.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_JSON = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL not support Parquet `JSON` type.\n" "\n"),
    link=None,
    level=4,
    num="4.5.4.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_UUID = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL not support Parquet `UUID` type.\n" "\n"),
    link=None,
    level=4,
    num="4.5.4.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_ENUM = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=("[ClickHouse] SHALL not support Parquet `ENUM` type.\n" "\n"),
    link=None,
    level=4,
    num="4.5.4.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_Query = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query",
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
    num="4.6.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL",
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
    num="4.6.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File",
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
    num="4.6.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3",
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
    num="4.6.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC",
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
    num="4.6.6",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC",
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
    num="4.6.7",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS",
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
    num="4.6.8",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_Remote = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote",
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
    num="4.6.9",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL",
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
    num="4.6.10",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_PostgeSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL",
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
    num="4.6.11",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_ODBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.ODBC",
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
    num="4.6.12.1.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_JDBC = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.JDBC",
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
    num="4.6.12.1.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_MySQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MySQL",
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
    num="4.6.12.1.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_MongoDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MongoDB",
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
    num="4.6.12.1.4",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_HDFS = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.HDFS",
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
    num="4.6.12.1.5",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_S3 = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.S3",
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
    num="4.6.12.1.6",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_Kafka = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.Kafka",
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
    num="4.6.12.1.7",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_EmbeddedRocksDB = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.EmbeddedRocksDB",
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
    num="4.6.12.1.8",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_PostgreSQL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.PostgreSQL",
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
    num="4.6.12.1.9",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_Distributed = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Distributed",
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
    num="4.6.12.2.1",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_Dictionary = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Dictionary",
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
    num="4.6.12.2.2",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_File = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.File",
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
    num="4.6.12.2.3",
)

RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_URL = Requirement(
    name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.URL",
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
    num="4.6.12.2.4",
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
        Heading(name="RQ.SRS-032.ClickHouse.Parquet.Format", level=3, num="4.1.1"),
        Heading(name="INSERT", level=2, num="4.2"),
        Heading(name="INSERT Settings", level=3, num="4.2.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested",
            level=3,
            num="4.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching",
            level=3,
            num="4.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns",
            level=3,
            num="4.2.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference",
            level=3,
            num="4.2.5",
        ),
        Heading(name="INSERT Conversions", level=3, num="4.2.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt8ToUInt8",
            level=4,
            num="4.2.6.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BoolToUInt8",
            level=4,
            num="4.2.6.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int8ToInt8",
            level=4,
            num="4.2.6.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt16ToUInt16",
            level=4,
            num="4.2.6.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int16ToInt16",
            level=4,
            num="4.2.6.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt32ToUInt32",
            level=4,
            num="4.2.6.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int32ToInt32",
            level=4,
            num="4.2.6.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt64ToUInt64",
            level=4,
            num="4.2.6.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int64ToInt64",
            level=4,
            num="4.2.6.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.FloatToFloat32",
            level=4,
            num="4.2.6.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.HalfFloatToFloat32",
            level=4,
            num="4.2.6.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DoubleToFloat64",
            level=4,
            num="4.2.6.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date32ToDate",
            level=4,
            num="4.2.6.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date64ToDateTime",
            level=4,
            num="4.2.6.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.TimeStampToDateTime",
            level=4,
            num="4.2.6.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StringToString",
            level=4,
            num="4.2.6.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BinaryToString",
            level=4,
            num="4.2.6.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DecimalToDecimal",
            level=4,
            num="4.2.6.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.ListToArray",
            level=4,
            num="4.2.6.19",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StructToTuple",
            level=4,
            num="4.2.6.20",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.MapToMap",
            level=4,
            num="4.2.6.21",
        ),
        Heading(name="SELECT", level=2, num="4.3"),
        Heading(name="SELECT Settings", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.RowGroupSize",
            level=3,
            num="4.3.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.StringAsString",
            level=3,
            num="4.3.3",
        ),
        Heading(name="SELECT Conversions", level=3, num="4.3.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt8ToUInt8",
            level=4,
            num="4.3.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.BoolToUInt8",
            level=4,
            num="4.3.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int8ToInt8",
            level=4,
            num="4.3.4.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt16ToUInt16",
            level=4,
            num="4.3.4.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int16ToInt16",
            level=4,
            num="4.3.4.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt32ToUInt32",
            level=4,
            num="4.3.4.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int32ToInt32",
            level=4,
            num="4.3.4.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt64ToUInt64",
            level=4,
            num="4.3.4.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int64ToInt64",
            level=4,
            num="4.3.4.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float32ToFloat",
            level=4,
            num="4.3.4.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float64ToDouble",
            level=4,
            num="4.3.4.11",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateToUInt16",
            level=4,
            num="4.3.4.12",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateTimeToUInt32",
            level=4,
            num="4.3.4.13",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.StringToBinary",
            level=4,
            num="4.3.4.14",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.FixedStringToBinary",
            level=4,
            num="4.3.4.15",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DecimalToDecimal",
            level=4,
            num="4.3.4.16",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.ArrayToList",
            level=4,
            num="4.3.4.17",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.TupleToStruct",
            level=4,
            num="4.3.4.18",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.MapToMap",
            level=4,
            num="4.3.4.19",
        ),
        Heading(name="Nested Types", level=2, num="4.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays",
            level=4,
            num="4.4.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple",
            level=4,
            num="4.4.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map",
            level=4,
            num="4.4.4.3",
        ),
        Heading(name="Unsupported Parquet Types", level=2, num="4.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32",
            level=4,
            num="4.5.4.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary",
            level=4,
            num="4.5.4.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON",
            level=4,
            num="4.5.4.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID",
            level=4,
            num="4.5.4.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM",
            level=4,
            num="4.5.4.5",
        ),
        Heading(name="Sources", level=2, num="4.6"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query",
            level=3,
            num="4.6.1",
        ),
        Heading(name="Table Functions", level=3, num="4.6.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL",
            level=3,
            num="4.6.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File",
            level=3,
            num="4.6.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3",
            level=3,
            num="4.6.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC",
            level=3,
            num="4.6.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC",
            level=3,
            num="4.6.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS",
            level=3,
            num="4.6.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote",
            level=3,
            num="4.6.9",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL",
            level=3,
            num="4.6.10",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL",
            level=3,
            num="4.6.11",
        ),
        Heading(name="Table Engines", level=3, num="4.6.12"),
        Heading(name="Integration Engines", level=4, num="4.6.12.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.ODBC",
            level=5,
            num="4.6.12.1.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.JDBC",
            level=5,
            num="4.6.12.1.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MySQL",
            level=5,
            num="4.6.12.1.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MongoDB",
            level=5,
            num="4.6.12.1.4",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.HDFS",
            level=5,
            num="4.6.12.1.5",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.S3",
            level=5,
            num="4.6.12.1.6",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.Kafka",
            level=5,
            num="4.6.12.1.7",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.EmbeddedRocksDB",
            level=5,
            num="4.6.12.1.8",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.PostgreSQL",
            level=5,
            num="4.6.12.1.9",
        ),
        Heading(name="Special Engines", level=4, num="4.6.12.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Distributed",
            level=5,
            num="4.6.12.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Dictionary",
            level=5,
            num="4.6.12.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.File",
            level=5,
            num="4.6.12.2.3",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.URL",
            level=5,
            num="4.6.12.2.4",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_Parquet_Format,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_ImportNested,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_CaseInsensitiveColumnMatching,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_AllowMissingColumns,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_InputFormatParquet_SkipColumnsWithUnsupportedTypesInSchemaInference,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt8ToUInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_BoolToUInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int8ToInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt16ToUInt16,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int16ToInt16,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt32ToUInt32,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int32ToInt32,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_UInt64ToUInt64,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Int64ToInt64,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_FloatToFloat32,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_HalfFloatToFloat32,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_DoubleToFloat64,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Date32ToDate,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_Date64ToDateTime,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_TimeStampToDateTime,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_StringToString,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_BinaryToString,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_DecimalToDecimal,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_ListToArray,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_StructToTuple,
        RQ_SRS_032_ClickHouse_Parquet_Format_InsertConversions_MapToMap,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_OutFormatParquet_RowGroupSize,
        RQ_SRS_032_ClickHouse_Parquet_Format_Settings_OutFormatParquet_StringAsString,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt8ToUInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_BoolToUInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int8ToInt8,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt16ToUInt16,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int16ToInt16,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt32ToUInt32,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int32ToInt32,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_UInt64ToUInt64,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Int64ToInt64,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Float32ToFloat,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_Float64ToDouble,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DateToUInt16,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DateTimeToUInt32,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_StringToBinary,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_FixedStringToBinary,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_DecimalToDecimal,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_ArrayToList,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_TupleToStruct,
        RQ_SRS_032_ClickHouse_Parquet_Format_SelectConversions_MapToMap,
        RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Arrays,
        RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Tuple,
        RQ_SRS_032_ClickHouse_Parquet_Format_NestedTypes_Map,
        RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_Time32,
        RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_FixedSizeBinary,
        RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_JSON,
        RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_UUID,
        RQ_SRS_032_ClickHouse_Parquet_Format_UnsupportedParquetTypes_ENUM,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_Query,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_URL,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_File,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_S3,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_Remote,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableFunctions_PostgeSQL,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_ODBC,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_JDBC,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_MySQL,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_MongoDB,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_HDFS,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_S3,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_Kafka,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_EmbeddedRocksDB,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Integration_PostgreSQL,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_Distributed,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_Dictionary,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_File,
        RQ_SRS_032_ClickHouse_Parquet_Format_Sources_TableEngines_Special_URL,
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
    * 4.1.1 [RQ.SRS-032.ClickHouse.Parquet.Format](#rqsrs-032clickhouseparquetformat)
  * 4.2 [INSERT](#insert)
    * 4.2.1 [INSERT Settings](#insert-settings)
    * 4.2.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetimportnested)
    * 4.2.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetcaseinsensitivecolumnmatching)
    * 4.2.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetallowmissingcolumns)
    * 4.2.5 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetskipcolumnswithunsupportedtypesinschemainference)
    * 4.2.6 [INSERT Conversions](#insert-conversions)
      * 4.2.6.1 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt8ToUInt8](#rqsrs-032clickhouseparquetformatinsertconversionsuint8touint8)
      * 4.2.6.2 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BoolToUInt8](#rqsrs-032clickhouseparquetformatinsertconversionsbooltouint8)
      * 4.2.6.3 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int8ToInt8](#rqsrs-032clickhouseparquetformatinsertconversionsint8toint8)
      * 4.2.6.4 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt16ToUInt16](#rqsrs-032clickhouseparquetformatinsertconversionsuint16touint16)
      * 4.2.6.5 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int16ToInt16](#rqsrs-032clickhouseparquetformatinsertconversionsint16toint16)
      * 4.2.6.6 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt32ToUInt32](#rqsrs-032clickhouseparquetformatinsertconversionsuint32touint32)
      * 4.2.6.7 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int32ToInt32](#rqsrs-032clickhouseparquetformatinsertconversionsint32toint32)
      * 4.2.6.8 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt64ToUInt64](#rqsrs-032clickhouseparquetformatinsertconversionsuint64touint64)
      * 4.2.6.9 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int64ToInt64](#rqsrs-032clickhouseparquetformatinsertconversionsint64toint64)
      * 4.2.6.10 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.FloatToFloat32](#rqsrs-032clickhouseparquetformatinsertconversionsfloattofloat32)
      * 4.2.6.11 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.HalfFloatToFloat32](#rqsrs-032clickhouseparquetformatinsertconversionshalffloattofloat32)
      * 4.2.6.12 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DoubleToFloat64](#rqsrs-032clickhouseparquetformatinsertconversionsdoubletofloat64)
      * 4.2.6.13 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date32ToDate](#rqsrs-032clickhouseparquetformatinsertconversionsdate32todate)
      * 4.2.6.14 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date64ToDateTime](#rqsrs-032clickhouseparquetformatinsertconversionsdate64todatetime)
      * 4.2.6.15 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.TimeStampToDateTime](#rqsrs-032clickhouseparquetformatinsertconversionstimestamptodatetime)
      * 4.2.6.16 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StringToString](#rqsrs-032clickhouseparquetformatinsertconversionsstringtostring)
      * 4.2.6.17 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BinaryToString](#rqsrs-032clickhouseparquetformatinsertconversionsbinarytostring)
      * 4.2.6.18 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DecimalToDecimal](#rqsrs-032clickhouseparquetformatinsertconversionsdecimaltodecimal)
      * 4.2.6.19 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.ListToArray](#rqsrs-032clickhouseparquetformatinsertconversionslisttoarray)
      * 4.2.6.20 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StructToTuple](#rqsrs-032clickhouseparquetformatinsertconversionsstructtotuple)
      * 4.2.6.21 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.MapToMap](#rqsrs-032clickhouseparquetformatinsertconversionsmaptomap)
  * 4.3 [SELECT](#select)
    * 4.3.1 [SELECT Settings](#select-settings)
    * 4.3.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.RowGroupSize](#rqsrs-032clickhouseparquetformatsettingsoutformatparquetrowgroupsize)
    * 4.3.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.StringAsString](#rqsrs-032clickhouseparquetformatsettingsoutformatparquetstringasstring)
    * 4.3.4 [SELECT Conversions](#select-conversions)
      * 4.3.4.1 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt8ToUInt8](#rqsrs-032clickhouseparquetformatselectconversionsuint8touint8)
      * 4.3.4.2 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.BoolToUInt8](#rqsrs-032clickhouseparquetformatselectconversionsbooltouint8)
      * 4.3.4.3 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int8ToInt8](#rqsrs-032clickhouseparquetformatselectconversionsint8toint8)
      * 4.3.4.4 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt16ToUInt16](#rqsrs-032clickhouseparquetformatselectconversionsuint16touint16)
      * 4.3.4.5 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int16ToInt16](#rqsrs-032clickhouseparquetformatselectconversionsint16toint16)
      * 4.3.4.6 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt32ToUInt32](#rqsrs-032clickhouseparquetformatselectconversionsuint32touint32)
      * 4.3.4.7 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int32ToInt32](#rqsrs-032clickhouseparquetformatselectconversionsint32toint32)
      * 4.3.4.8 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt64ToUInt64](#rqsrs-032clickhouseparquetformatselectconversionsuint64touint64)
      * 4.3.4.9 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int64ToInt64](#rqsrs-032clickhouseparquetformatselectconversionsint64toint64)
      * 4.3.4.10 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float32ToFloat](#rqsrs-032clickhouseparquetformatselectconversionsfloat32tofloat)
      * 4.3.4.11 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float64ToDouble](#rqsrs-032clickhouseparquetformatselectconversionsfloat64todouble)
      * 4.3.4.12 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateToUInt16](#rqsrs-032clickhouseparquetformatselectconversionsdatetouint16)
      * 4.3.4.13 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateTimeToUInt32](#rqsrs-032clickhouseparquetformatselectconversionsdatetimetouint32)
      * 4.3.4.14 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.StringToBinary](#rqsrs-032clickhouseparquetformatselectconversionsstringtobinary)
      * 4.3.4.15 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.FixedStringToBinary](#rqsrs-032clickhouseparquetformatselectconversionsfixedstringtobinary)
      * 4.3.4.16 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DecimalToDecimal](#rqsrs-032clickhouseparquetformatselectconversionsdecimaltodecimal)
      * 4.3.4.17 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.ArrayToList](#rqsrs-032clickhouseparquetformatselectconversionsarraytolist)
      * 4.3.4.18 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.TupleToStruct](#rqsrs-032clickhouseparquetformatselectconversionstupletostruct)
      * 4.3.4.19 [RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.MapToMap](#rqsrs-032clickhouseparquetformatselectconversionsmaptomap)
  * 4.4 [Nested Types](#nested-types)
      * 4.4.4.1 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays](#rqsrs-032clickhouseparquetformatnestedtypesarrays)
      * 4.4.4.2 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple](#rqsrs-032clickhouseparquetformatnestedtypestuple)
      * 4.4.4.3 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map](#rqsrs-032clickhouseparquetformatnestedtypesmap)
  * 4.5 [Unsupported Parquet Types](#unsupported-parquet-types)
      * 4.5.4.1 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32](#rqsrs-032clickhouseparquetformatunsupportedparquettypestime32)
      * 4.5.4.2 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary](#rqsrs-032clickhouseparquetformatunsupportedparquettypesfixedsizebinary)
      * 4.5.4.3 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON](#rqsrs-032clickhouseparquetformatunsupportedparquettypesjson)
      * 4.5.4.4 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID](#rqsrs-032clickhouseparquetformatunsupportedparquettypesuuid)
      * 4.5.4.5 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM](#rqsrs-032clickhouseparquetformatunsupportedparquettypesenum)
  * 4.6 [Sources](#sources)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query](#rqsrs-032clickhouseparquetformatsourcesquery)
    * 4.6.2 [Table Functions](#table-functions)
    * 4.6.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL](#rqsrs-032clickhouseparquetformatsourcestablefunctionsurl)
    * 4.6.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File](#rqsrs-032clickhouseparquetformatsourcestablefunctionsfile)
    * 4.6.5 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3](#rqsrs-032clickhouseparquetformatsourcestablefunctionss3)
    * 4.6.6 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC](#rqsrs-032clickhouseparquetformatsourcestablefunctionsjdbc)
    * 4.6.7 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC](#rqsrs-032clickhouseparquetformatsourcestablefunctionsodbc)
    * 4.6.8 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS](#rqsrs-032clickhouseparquetformatsourcestablefunctionshdfs)
    * 4.6.9 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote](#rqsrs-032clickhouseparquetformatsourcestablefunctionsremote)
    * 4.6.10 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL](#rqsrs-032clickhouseparquetformatsourcestablefunctionsmysql)
    * 4.6.11 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL](#rqsrs-032clickhouseparquetformatsourcestablefunctionspostgesql)
    * 4.6.12 [Table Engines](#table-engines)
      * 4.6.12.1 [Integration Engines](#integration-engines)
        * 4.6.12.1.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationodbc)
        * 4.6.12.1.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationjdbc)
        * 4.6.12.1.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationmysql)
        * 4.6.12.1.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationmongodb)
        * 4.6.12.1.5 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationhdfs)
        * 4.6.12.1.6 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.S3](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrations3)
        * 4.6.12.1.7 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationkafka)
        * 4.6.12.1.8 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationembeddedrocksdb)
        * 4.6.12.1.9 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationpostgresql)
      * 4.6.12.2 [Special Engines](#special-engines)
        * 4.6.12.2.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialdistributed)
        * 4.6.12.2.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialdictionary)
        * 4.6.12.2.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.File](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialfile)
        * 4.6.12.2.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.URL](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialurl)


## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for `Parquet` data format in [ClickHouse].

## Feature Diagram

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
                Int8_in[Int8]`
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

    end

## Requirements

### General

#### RQ.SRS-032.ClickHouse.Parquet.Format
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

### INSERT

#### INSERT Settings

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables.
Default: `false`

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns.
Default: `false`

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.
Default: `false`

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_skip_columns_with_unsupported_types_in_schema_inference`
to allow skipping unsupported types.
Default: `false`

#### INSERT Conversions

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt8ToUInt8
version:1.0

[ClickHouse] SHALL convert Parquet `UInt8` to ClickHouse `UInt8` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BoolToUInt8
version:1.0

[ClickHouse] SHALL convert Parquet `Bool` to ClickHouse `UInt8` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int8ToInt8
version:1.0

[ClickHouse] SHALL convert Parquet `Int8` to ClickHouse `Int8` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt16ToUInt16
version:1.0

[ClickHouse] SHALL convert Parquet `UInt16` to ClickHouse `UInt16` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int16ToInt16
version:1.0

[ClickHouse] SHALL convert Parquet `Int16` to ClickHouse `Int16` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt32ToUInt32
version:1.0

[ClickHouse] SHALL convert Parquet `UInt32` to ClickHouse `UInt32` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int32ToInt32
version:1.0

[ClickHouse] SHALL convert Parquet `Int32` to ClickHouse `Int32` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt64ToUInt64
version:1.0

[ClickHouse] SHALL convert Parquet `UInt64` to ClickHouse `UInt64` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int64ToInt64
version:1.0

[ClickHouse] SHALL convert Parquet `Int64` to ClickHouse `Int64` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.FloatToFloat32
version:1.0

[ClickHouse] SHALL convert Parquet `Float` to ClickHouse `Float32` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.HalfFloatToFloat32
version:1.0

[ClickHouse] SHALL convert Parquet `Half_Float` to ClickHouse `Float32` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DoubleToFloat64
version:1.0

[ClickHouse] SHALL convert Parquet `Double` to ClickHouse `Float64` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date32ToDate
version:1.0

[ClickHouse] SHALL convert Parquet `Date32` to ClickHouse `Date` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date64ToDateTime
version:1.0

[ClickHouse] SHALL convert Parquet `Date64` to ClickHouse `DateTime` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.TimeStampToDateTime
version:1.0

[ClickHouse] SHALL convert Parquet `TimeStamp` to ClickHouse `DateTime` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StringToString
version:1.0

[ClickHouse] SHALL convert Parquet `String` to ClickHouse `String` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BinaryToString
version:1.0

[ClickHouse] SHALL convert Parquet `Binary` to ClickHouse `String` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DecimalToDecimal
version:1.0

[ClickHouse] SHALL convert Parquet `Decimal` to ClickHouse `Decimal` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.ListToArray
version:1.0

[ClickHouse] SHALL convert Parquet `List` to ClickHouse `Array` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StructToTuple
version:1.0

[ClickHouse] SHALL convert Parquet `Struct` to ClickHouse `Tuple` in Insert queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.MapToMap
version:1.0

[ClickHouse] SHALL convert Parquet `Map` to ClickHouse `Map` in Insert queries.

### SELECT

#### SELECT Settings

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.RowGroupSize
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_row_group_size` row group size by row count.
Default: `1000000`

#### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.OutFormatParquet.StringAsString
version: 1.0

[ClickHouse] SHALL support specifying `output_format_parquet_string_as_string` to use Parquet String type instead of Binary.
Default: `false`

#### SELECT Conversions

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt8ToUInt8
version:1.0

[ClickHouse] SHALL convert ClickHouse `UInt8` to Parquet `UInt8` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.BoolToUInt8
version:1.0

[ClickHouse] SHALL convert ClickHouse `Bool` to Parquet `UInt8` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int8ToInt8
version:1.0

[ClickHouse] SHALL convert ClickHouse `Int8` to Parquet `Int8` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt16ToUInt16
version:1.0

[ClickHouse] SHALL convert ClickHouse `UInt16` to Parquet `UInt16` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int16ToInt16
version:1.0

[ClickHouse] SHALL convert ClickHouse `Int16` to Parquet `Int16` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt32ToUInt32
version:1.0

[ClickHouse] SHALL convert ClickHouse `UInt32` to Parquet `UInt32` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int32ToInt32
version:1.0

[ClickHouse] SHALL convert ClickHouse `Int32` to Parquet `Int32` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.UInt64ToUInt64
version:1.0

[ClickHouse] SHALL convert ClickHouse `UInt64` to Parquet `UInt64` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Int64ToInt64
version:1.0

[ClickHouse] SHALL convert ClickHouse `Int64` to Parquet `Int64` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float32ToFloat
version:1.0

[ClickHouse] SHALL convert ClickHouse `Float32` to Parquet `Float` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.Float64ToDouble
version:1.0

[ClickHouse] SHALL convert ClickHouse `Float64` to Parquet `Double` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateToUInt16
version:1.0

[ClickHouse] SHALL convert ClickHouse `Date` to Parquet `UInt16` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DateTimeToUInt32
version:1.0

[ClickHouse] SHALL convert ClickHouse `DateTime` to Parquet `UInt32` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.StringToBinary
version:1.0

[ClickHouse] SHALL convert ClickHouse `String` to Parquet `Binary` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.FixedStringToBinary
version:1.0

[ClickHouse] SHALL convert ClickHouse `FixedString` to Parquet `Binary` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.DecimalToDecimal
version:1.0

[ClickHouse] SHALL convert ClickHouse `Decimal` to Parquet `Decimal` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.ArrayToList
version:1.0

[ClickHouse] SHALL convert ClickHouse `Array` to Parquet `List` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.TupleToStruct
version:1.0

[ClickHouse] SHALL convert ClickHouse `Tuple` to Parquet `Struct` in Select queries.

##### RQ.SRS-032.ClickHouse.Parquet.Format.SelectConversions.MapToMap
version:1.0

[ClickHouse] SHALL convert ClickHouse `Map` to Parquet `Map` in Select queries.

### Nested Types

##### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays
version:1.0

[ClickHouse] SHALL support nested `arrays`.

##### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple
version:1.0

[ClickHouse] SHALL support nested `tuples`.

##### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map
version:1.0

[ClickHouse] SHALL support nested `maps`.

### Unsupported Parquet Types

##### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32
version:1.0

[ClickHouse] SHALL not support Parquet `Time32` type.

##### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary
version:1.0

[ClickHouse] SHALL not support Parquet `Fixed_Size_Binary` type.

##### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON
version:1.0

[ClickHouse] SHALL not support Parquet `JSON` type.

##### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID
version:1.0

[ClickHouse] SHALL not support Parquet `UUID` type.

##### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM
version:1.0

[ClickHouse] SHALL not support Parquet `ENUM` type.

### Sources

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query
version: 1.0

[ClickHouse] SHALL support reading and writing Parquet format from a command line query.

#### Table Functions

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL
version: 1.0

[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL
version: 1.0

[ClickHouse] SHALL support `postgresql` table function reading and writing Parquet format.

#### Table Engines

##### Integration Engines

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.ODBC
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `ODBC` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.JDBC
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `JDBC` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MySQL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MySQL` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MongoDB
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from a `MongoDB` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.HDFS
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `HDFS` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.S3
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `s3` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.Kafka
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Kafka` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.EmbeddedRocksDB
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `EmbeddedRocksDB` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.PostgreSQL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `PostgreSQL` table engine.

##### Special Engines

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Distributed
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Distributed` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Dictionary
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `Dictionary` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.File
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `File` table engine.

###### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.URL
version: 1.0

[ClickHouse] SHALL support Parquet format being inserted into and selected from an `URL` table engine.

[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/ClickHouse/ClickHouse/blob/master/tests/testflows/parquet/requirements/requirements.md 
[Revision History]: https://github.com/ClickHouse/ClickHouse/commits/master/tests/testflows/parquet/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
""",
)
