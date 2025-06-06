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
