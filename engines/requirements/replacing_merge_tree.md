# SRS035 ClickHouse ReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree](#rqsrs-035clickhousereplacingmergetree)
    * 4.1.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree](#rqsrs-035clickhousereplacingmergetreeoldreplacingmergetree)
    * 4.1.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.General](#rqsrs-035clickhousereplacingmergetreegeneral)
    * 4.1.3 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication](#rqsrs-035clickhousereplacingmergetreedatadeduplication)
    * 4.1.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge](#rqsrs-035clickhousereplacingmergetreeoptimizemerge)
    * 4.1.5 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows](#rqsrs-035clickhousereplacingmergetreeuniquenessofrows)
    * 4.1.6 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn](#rqsrs-035clickhousereplacingmergetreeversioncolumn)
    * 4.1.7 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows](#rqsrs-035clickhousereplacingmergetreeselectionofrows)
    * 4.1.8 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules](#rqsrs-035clickhousereplacingmergetreeselectionrules)
    * 4.1.9 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation](#rqsrs-035clickhousereplacingmergetreetablecreation)
  * 4.2 [CollapsingMergeTree](#collapsingmergetree)
    * 4.2.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree](#rqsrs-035clickhousereplacingmergetreecollapsingmergetree)
  * 4.3 [Duplicate Insertions](#duplicate-insertions)
    * 4.3.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions](#rqsrs-035clickhousereplacingmergetreeduplicateinsertions)
  * 4.4 [Update](#update)
    * 4.4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update](#rqsrs-035clickhousereplacingmergetreeupdate)
  * 4.5 [Delete](#delete)
    * 4.5.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete](#rqsrs-035clickhousereplacingmergetreedelete)
    * 4.5.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled](#rqsrs-035clickhousereplacingmergetreedeletedisabled)
  * 4.6 [Update Key Columns](#update-key-columns)
    * 4.6.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns](#rqsrs-035clickhousereplacingmergetreeupdatekeycolumns)
  * 4.7 [Remove Duplicates](#remove-duplicates)
    * 4.7.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates](#rqsrs-035clickhousereplacingmergetreeremoveduplicates)
  * 4.8 [Backward Compatibility](#backward-compatibility)
    * 4.8.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility](#rqsrs-035clickhousereplacingmergetreebackwardcompatibility)
  * 4.9 [Version Number](#version-number)
    * 4.9.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber](#rqsrs-035clickhousereplacingmergetreeversionnumber)
  * 4.10 [Settings](#settings)
    * 4.10.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows](#rqsrs-035clickhousereplacingmergetreesettingscleandeletedrows)
    * 4.10.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled](#rqsrs-035clickhousereplacingmergetreesettingscleandeletedrowsdisabled)
  * 4.11 [Handling Deleted Data](#handling-deleted-data)
    * 4.11.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData](#rqsrs-035clickhousereplacingmergetreehandlingdeleteddata)
  * 4.12 [Errors](#errors)
    * 4.12.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType](#rqsrs-035clickhousereplacingmergetreeerrorswrongdatatype)
    * 4.12.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue](#rqsrs-035clickhousereplacingmergetreeerrorswrongdatavalue)
  * 4.13 [Non-Functional Requirements](#non-functional-requirements)
      * 4.13.2.1 [Performance](#performance)
      * 4.13.2.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsperformance)
      * 4.13.2.3 [Reliability](#reliability)
      * 4.13.2.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsreliability)


## Introduction

This software requirements specification covers requirements related to [ClickHouse] support from 23.2 new
[ReplacingMergeTree] which allows for duplicate insertions and combines the capabilities of 
[ReplacingMergeTree] and [CollapsingMergeTree].

[ReplacingMergeTree] is designed to remove duplicate entries with the same sorting key value (ORDER BY table section,
not PRIMARY KEY) and is suitable for clearing out duplicate data in the background in order to save space. 
However, it does not guarantee the absence of duplicates.


## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/41005
* https://kb.altinity.com/engines/mergetree-table-engine-family/replacingmergetree/

## Terminology

####SRS

Software Requirements Specification

## Requirements

### RQ.SRS-035.ClickHouse.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows insertion of duplicates by adding an extra
is_deleted column (possible values: 0 / 1) to the ReplacingMergeTree. The is_deleted column is optional, but if enabled, the version 
column becomes mandatory. 


#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree
version: 1.0

[ReplacingMergeTree] new engine version SHALL support all old [ReplacingMergeTree] possibilities.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.General
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting 
key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a 
merge, which occurs in the background at an unknown time, and the system cannot be planned for. 
However, the `OPTIMIZE` query can be used to run an unscheduled merge.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication

[ReplacingMergeTree] engine SHALL support remove duplicate entries with the same sorting key value during a 
merge process.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge

[ReplacingMergeTree] engine SHALL support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process 
must occur in the background at an unknown time, and the system cannot be planned for.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows

[ReplacingMergeTree] engine SHALL support uniqueness of rows determined by the `ORDER BY` table section, 
not PRIMARY KEY.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn
version: 1.0

[ReplacingMergeTree] engine SHALL support a version column with a type of UInt*, Date, DateTime, or DateTime64.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows
version: 1.0

[ReplacingMergeTree] engine SHALL support merging, the engine must leave only one row from all the rows with the same 
sorting key. 

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules
version: 1.0

[ReplacingMergeTree] engine SHALL support selection rules: if a version column is specified, the engine must select the 
row with the maximum version. If no version column is specified, the engine must select the last row in the selection.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation
version: 1.0

[ReplacingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the 
ver column.

### CollapsingMergeTree

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree
version: 1.0

[ReplacingMergeTree] new engine version SHALL support all [CollapsingMergeTree] possibilities.

### Duplicate Insertions

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions
version: 1.0

[ReplacingMergeTree] engine SHALL allow duplicate insertions of rows.

### Update

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version. 
The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.

### Delete

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete
version: 1.0

[ReplacingMergeTree] engine SHALL allow deleting a row by inserting a row with (arbitrary) greater version and
0 is_deleted parameter. The replacing merge algorithm leaves only one row with is_deleted = 0, and then it is filtered
out.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.DeleteDisabled
version: 1.0

[ReplacingMergeTree] engine SHALL not allow deleting a row if `is_deleted` parameter is not provided.

### Update Key Columns

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.

### Remove Duplicates

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates
version: 1.0

[ReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.

### Backward Compatibility

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility
version: 1.0

[ReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].
This means that it should be an option when creating a table.

### Version Number

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber
version: 1.0

[ReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two 
inserted rows have the same version number, the last inserted one is the one kept.

### Settings

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRows
version: 1.0

[ReplacingMergeTree] engine SHALL support `clean_deleted_rows` (possible values: 'Never' / 'Always') which allows 
to apply deletes without `FINAL` after merge operation (manually: `OPTIMIZE TABLE tble_name FINAL`) to all `SELECT` 
queries.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Settings.CleanDeletedRowsDisabled
version: 1.0

[ReplacingMergeTree] engine SHALL not support `clean_deleted_rows` if `is_deleted` parameter is not provided.


### Handling Deleted Data

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData
version: 1.0

[ReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.
The information of deleted data is needed for KPIs.

### Errors

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataType
version: 1.0

[ReplacingMergeTree] engine SHALL provide exception:

```CMD
Code: 169. DB::Exception: Received from localhost:9000. DB::Exception: is_deleted column (is_deleted) for 
storage ReplacingMergeTree must have type UInt8. Provided column of type String.. (BAD_TYPE_OF_FIELD)
```

when wrong data type was used for `is_deleted` column.

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.Errors.WrongDataValue
version: 1.0

[ReplacingMergeTree] engine SHALL provide exception:

```CMD
Code: 117. DB::Exception: Received from localhost:9000. DB::Exception: Incorrect data: is_deleted = 6 (must be 1 or 0)..
 (INCORRECT_DATA)
```

when other than 0 or 1 value was used in `is_deleted` column.

### Non-Functional Requirements

##### Performance

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[ReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[ReplacingMergeTree] engine SHALL be reliable and not lose any data.



[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/


