# SRS035 ClickHouse ReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree](#rqsrs-035clickhousereplacingmergetree)
  * 4.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree](#rqsrs-035clickhousereplacingmergetreeoldreplacingmergetree)
    * 4.2.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.General](#rqsrs-035clickhousereplacingmergetreegeneral)
    * 4.2.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DataDeduplication](#rqsrs-035clickhousereplacingmergetreedatadeduplication)
    * 4.2.3 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.OptimizeMerge](#rqsrs-035clickhousereplacingmergetreeoptimizemerge)
    * 4.2.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UniquenessOfRows](#rqsrs-035clickhousereplacingmergetreeuniquenessofrows)
    * 4.2.5 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionColumn](#rqsrs-035clickhousereplacingmergetreeversioncolumn)
    * 4.2.6 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionOfRows](#rqsrs-035clickhousereplacingmergetreeselectionofrows)
    * 4.2.7 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.SelectionRules](#rqsrs-035clickhousereplacingmergetreeselectionrules)
    * 4.2.8 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.TableCreation](#rqsrs-035clickhousereplacingmergetreetablecreation)
  * 4.3 [CollapsingMergeTree](#collapsingmergetree)
    * 4.3.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.CollapsingMergeTree](#rqsrs-035clickhousereplacingmergetreecollapsingmergetree)
  * 4.4 [Duplicate Insertions](#duplicate-insertions)
    * 4.4.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.DuplicateInsertions](#rqsrs-035clickhousereplacingmergetreeduplicateinsertions)
  * 4.5 [Update](#update)
    * 4.5.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Update](#rqsrs-035clickhousereplacingmergetreeupdate)
  * 4.6 [Delete](#delete)
    * 4.6.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.Delete](#rqsrs-035clickhousereplacingmergetreedelete)
  * 4.7 [Update Key Columns](#update-key-columns)
    * 4.7.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns](#rqsrs-035clickhousereplacingmergetreeupdatekeycolumns)
  * 4.8 [Remove Duplicates](#remove-duplicates)
    * 4.8.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates](#rqsrs-035clickhousereplacingmergetreeremoveduplicates)
    * 4.8.2 [Backward Compatibility](#backward-compatibility)
      * 4.8.2.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility](#rqsrs-035clickhousereplacingmergetreebackwardcompatibility)
  * 4.9 [Version Number](#version-number)
    * 4.9.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber](#rqsrs-035clickhousereplacingmergetreeversionnumber)
    * 4.9.2 [Handling Deleted Data](#handling-deleted-data)
      * 4.9.2.1 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData](#rqsrs-035clickhousereplacingmergetreehandlingdeleteddata)
    * 4.9.3 [Non-Functional Requirements](#non-functional-requirements)
      * 4.9.3.1 [Performance](#performance)
      * 4.9.3.2 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsperformance)
      * 4.9.3.3 [Reliability](#reliability)
      * 4.9.3.4 [RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-035clickhousereplacingmergetreenonfunctionalrequirementsreliability)


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

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-035.ClickHouse.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows insertion of duplicates by adding an extra
sign column (possible values: -1 / 1) to the ReplacingMergeTree. The sign column is optional, but if enabled, the version 
column becomes mandatory. 


### RQ.SRS-035.ClickHouse.ReplacingMergeTree.OldReplacingMergeTree
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
-1 sign. The replacing merge algorithm leaves only one row with sign = -1, and then it is filtered out.

### Update Key Columns

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.UpdateKeyColumns
version: 1.0

[ReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.

### Remove Duplicates

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.RemoveDuplicates
version: 1.0

[ReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.

#### Backward Compatibility

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.BackwardCompatibility
version: 1.0

[ReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].
This means that it should be an option when creating a table.

### Version Number

#### RQ.SRS-035.ClickHouse.ReplacingMergeTree.VersionNumber
version: 1.0

[ReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two 
inserted rows have the same version number, the last inserted one is the one kept.

#### Handling Deleted Data

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.HandlingDeletedData
version: 1.0

[ReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.
The information of deleted data is needed for KPIs.

#### Non-Functional Requirements

##### Performance

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[ReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-035.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[ReplacingMergeTree] engine SHALL be reliable and not lose any data.



[SRS]: #srs
[NewReplacingMergeTree]: https://github.com/ClickHouse/ClickHouse/pull/41005
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/


