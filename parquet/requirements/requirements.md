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
    * 4.2.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Insert.Projections](#rqsrs-032clickhouseparquetformatinsertprojections)
    * 4.2.2 [INSERT Settings](#insert-settings)
      * 4.2.2.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetimportnested)
      * 4.2.2.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetcaseinsensitivecolumnmatching)
      * 4.2.2.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetallowmissingcolumns)
      * 4.2.2.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference](#rqsrs-032clickhouseparquetformatsettingsinputformatparquetskipcolumnswithunsupportedtypesinschemainference)
    * 4.2.3 [INSERT Conversions](#insert-conversions)
      * 4.2.3.1 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt8ToUInt8](#rqsrs-032clickhouseparquetformatinsertconversionsuint8touint8)
      * 4.2.3.2 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BoolToUInt8](#rqsrs-032clickhouseparquetformatinsertconversionsbooltouint8)
      * 4.2.3.3 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int8ToInt8](#rqsrs-032clickhouseparquetformatinsertconversionsint8toint8)
      * 4.2.3.4 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt16ToUInt16](#rqsrs-032clickhouseparquetformatinsertconversionsuint16touint16)
      * 4.2.3.5 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int16ToInt16](#rqsrs-032clickhouseparquetformatinsertconversionsint16toint16)
      * 4.2.3.6 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt32ToUInt32](#rqsrs-032clickhouseparquetformatinsertconversionsuint32touint32)
      * 4.2.3.7 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int32ToInt32](#rqsrs-032clickhouseparquetformatinsertconversionsint32toint32)
      * 4.2.3.8 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.UInt64ToUInt64](#rqsrs-032clickhouseparquetformatinsertconversionsuint64touint64)
      * 4.2.3.9 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Int64ToInt64](#rqsrs-032clickhouseparquetformatinsertconversionsint64toint64)
      * 4.2.3.10 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.FloatToFloat32](#rqsrs-032clickhouseparquetformatinsertconversionsfloattofloat32)
      * 4.2.3.11 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.HalfFloatToFloat32](#rqsrs-032clickhouseparquetformatinsertconversionshalffloattofloat32)
      * 4.2.3.12 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DoubleToFloat64](#rqsrs-032clickhouseparquetformatinsertconversionsdoubletofloat64)
      * 4.2.3.13 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date32ToDate](#rqsrs-032clickhouseparquetformatinsertconversionsdate32todate)
      * 4.2.3.14 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.Date64ToDateTime](#rqsrs-032clickhouseparquetformatinsertconversionsdate64todatetime)
      * 4.2.3.15 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.TimeStampToDateTime](#rqsrs-032clickhouseparquetformatinsertconversionstimestamptodatetime)
      * 4.2.3.16 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StringToString](#rqsrs-032clickhouseparquetformatinsertconversionsstringtostring)
      * 4.2.3.17 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.BinaryToString](#rqsrs-032clickhouseparquetformatinsertconversionsbinarytostring)
      * 4.2.3.18 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.DecimalToDecimal](#rqsrs-032clickhouseparquetformatinsertconversionsdecimaltodecimal)
      * 4.2.3.19 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.ListToArray](#rqsrs-032clickhouseparquetformatinsertconversionslisttoarray)
      * 4.2.3.20 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.StructToTuple](#rqsrs-032clickhouseparquetformatinsertconversionsstructtotuple)
      * 4.2.3.21 [RQ.SRS-032.ClickHouse.Parquet.Format.InsertConversions.MapToMap](#rqsrs-032clickhouseparquetformatinsertconversionsmaptomap)
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
  * 4.4 [Null](#null)
    * 4.4.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Null](#rqsrs-032clickhouseparquetformatnull)
  * 4.5 [Nested Types](#nested-types)
    * 4.5.1 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays](#rqsrs-032clickhouseparquetformatnestedtypesarrays)
    * 4.5.2 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple](#rqsrs-032clickhouseparquetformatnestedtypestuple)
    * 4.5.3 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map](#rqsrs-032clickhouseparquetformatnestedtypesmap)
    * 4.5.4 [RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.LowCardinalityNullable](#rqsrs-032clickhouseparquetformatnestedtypeslowcardinalitynullable)
  * 4.6 [Unsupported Parquet Types](#unsupported-parquet-types)
    * 4.6.1 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32](#rqsrs-032clickhouseparquetformatunsupportedparquettypestime32)
    * 4.6.2 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary](#rqsrs-032clickhouseparquetformatunsupportedparquettypesfixedsizebinary)
    * 4.6.3 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON](#rqsrs-032clickhouseparquetformatunsupportedparquettypesjson)
    * 4.6.4 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID](#rqsrs-032clickhouseparquetformatunsupportedparquettypesuuid)
    * 4.6.5 [RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM](#rqsrs-032clickhouseparquetformatunsupportedparquettypesenum)
  * 4.7 [Sources](#sources)
    * 4.7.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query](#rqsrs-032clickhouseparquetformatsourcesquery)
    * 4.7.2 [Table Functions](#table-functions)
      * 4.7.2.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL](#rqsrs-032clickhouseparquetformatsourcestablefunctionsurl)
      * 4.7.2.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File](#rqsrs-032clickhouseparquetformatsourcestablefunctionsfile)
      * 4.7.2.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3](#rqsrs-032clickhouseparquetformatsourcestablefunctionss3)
      * 4.7.2.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC](#rqsrs-032clickhouseparquetformatsourcestablefunctionsjdbc)
      * 4.7.2.5 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC](#rqsrs-032clickhouseparquetformatsourcestablefunctionsodbc)
      * 4.7.2.6 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS](#rqsrs-032clickhouseparquetformatsourcestablefunctionshdfs)
      * 4.7.2.7 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote](#rqsrs-032clickhouseparquetformatsourcestablefunctionsremote)
      * 4.7.2.8 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL](#rqsrs-032clickhouseparquetformatsourcestablefunctionsmysql)
      * 4.7.2.9 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL](#rqsrs-032clickhouseparquetformatsourcestablefunctionspostgesql)
    * 4.7.3 [Table Engines](#table-engines)
      * 4.7.3.1 [Integration Engines](#integration-engines)
        * 4.7.3.1.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.ODBC](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationodbc)
        * 4.7.3.1.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.JDBC](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationjdbc)
        * 4.7.3.1.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MySQL](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationmysql)
        * 4.7.3.1.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.MongoDB](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationmongodb)
        * 4.7.3.1.5 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.HDFS](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationhdfs)
        * 4.7.3.1.6 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.S3](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrations3)
        * 4.7.3.1.7 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.Kafka](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationkafka)
        * 4.7.3.1.8 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.EmbeddedRocksDB](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationembeddedrocksdb)
        * 4.7.3.1.9 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Integration.PostgreSQL](#rqsrs-032clickhouseparquetformatsourcestableenginesintegrationpostgresql)
      * 4.7.3.2 [Special Engines](#special-engines)
        * 4.7.3.2.1 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Distributed](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialdistributed)
        * 4.7.3.2.2 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.Dictionary](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialdictionary)
        * 4.7.3.2.3 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.File](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialfile)
        * 4.7.3.2.4 [RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableEngines.Special.URL](#rqsrs-032clickhouseparquetformatsourcestableenginesspecialurl)


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

#### RQ.SRS-032.ClickHouse.Parquet.Format
version: 1.0

[ClickHouse] SHALL support `Parquet` data format.

### INSERT

#### RQ.SRS-032.ClickHouse.Parquet.Format.Insert.Projections
version: 1.0

[ClickHouse] SHALL support inserting parquet data into a table that has a projection on it.

#### INSERT Settings

##### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.ImportNested
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_import_nested` to allow inserting arrays of
nested structs into Nested tables.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.CaseInsensitiveColumnMatching
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_case_insensitive_column_matching` to ignore matching
Parquet and ClickHouse columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.AllowMissingColumns
version: 1.0

[ClickHouse] SHALL support specifying `input_format_parquet_allow_missing_columns` to allow missing columns.
Default: `false`

##### RQ.SRS-032.ClickHouse.Parquet.Format.Settings.InputFormatParquet.SkipColumnsWithUnsupportedTypesInSchemaInference
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

### Null

#### RQ.SRS-032.ClickHouse.Parquet.Format.Null
version:1.0

[ClickHouse] SHALL support Null and Nullable(type) data when inserting or selecting using Parquet format.

### Nested Types

#### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Arrays
version:1.0

[ClickHouse] SHALL support nested `arrays` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Tuple
version:1.0

[ClickHouse] SHALL support nested `tuples` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.Map
version:1.0

[ClickHouse] SHALL support nested `maps` in Parquet format.

#### RQ.SRS-032.ClickHouse.Parquet.Format.NestedTypes.LowCardinalityNullable
version: 1.0

[ClickHouse] SHALL support nesting LowCardinality and Nullable data types in any order.
Example:
LowCardinality(Nullable(String))
Nullable(LowCradinality(String))

### Unsupported Parquet Types

#### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.Time32
version:1.0

[ClickHouse] SHALL not support Parquet `Time32` type.

#### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.FixedSizeBinary
version:1.0

[ClickHouse] SHALL not support Parquet `Fixed_Size_Binary` type.

#### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.JSON
version:1.0

[ClickHouse] SHALL not support Parquet `JSON` type.

#### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.UUID
version:1.0

[ClickHouse] SHALL not support Parquet `UUID` type.

#### RQ.SRS-032.ClickHouse.Parquet.Format.UnsupportedParquetTypes.ENUM
version:1.0

[ClickHouse] SHALL not support Parquet `ENUM` type.

### Sources

#### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.Query
version: 1.0

[ClickHouse] SHALL support reading and writing Parquet format from a command line query.

#### Table Functions

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.URL
version: 1.0

[ClickHouse] SHALL support `url` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.File
version: 1.0

[ClickHouse] SHALL support `file` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.S3
version: 1.0

[ClickHouse] SHALL support `s3` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.JDBC
version: 1.0

[ClickHouse] SHALL support `jdbc` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.ODBC
version: 1.0

[ClickHouse] SHALL support `odbc` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.HDFS
version: 1.0

[ClickHouse] SHALL support `hdfs` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.Remote
version: 1.0

[ClickHouse] SHALL support `remote` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.MySQL
version: 1.0

[ClickHouse] SHALL support `mysql` table function reading and writing Parquet format.

##### RQ.SRS-032.ClickHouse.Parquet.Format.Sources.TableFunctions.PostgeSQL
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
