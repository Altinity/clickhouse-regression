# SRS035 ClickHouse NewReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree](#rqsrs-035clickhousenewreplacingmergetree)
  * 5.2 [ReplacingMergeTree](#replacingmergetree)
    * 5.2.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetree)
      * 5.2.1.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreegeneral)
      * 5.2.1.2 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.DataDeduplication](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreedatadeduplication)
      * 5.2.1.3 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.OptimizeMerge](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeoptimizemerge)
      * 5.2.1.4 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.UniquenessOfRows](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeuniquenessofrows)
      * 5.2.1.5 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeversioncolumn)
      * 5.2.1.6 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeselectionofrows)
      * 5.2.1.7 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeselectionrules)
      * 5.2.1.8 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreetablecreation)
  * 5.3 [CollapsingMergeTree](#collapsingmergetree)
    * 5.3.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree](#rqsrs-035clickhousenewreplacingmergetreecollapsingmergetree)
    * 5.3.2 [Duplicate Insertions](#duplicate-insertions)
      * 5.3.2.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions](#rqsrs-035clickhousenewreplacingmergetreeduplicateinsertions)
    * 5.3.3 [Update](#update)
      * 5.3.3.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update](#rqsrs-035clickhousenewreplacingmergetreeupdate)
    * 5.3.4 [Delete](#delete)
      * 5.3.4.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete](#rqsrs-035clickhousenewreplacingmergetreedelete)
    * 5.3.5 [Update Key Columns](#update-key-columns)
      * 5.3.5.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns](#rqsrs-035clickhousenewreplacingmergetreeupdatekeycolumns)
    * 5.3.6 [Remove Duplicates](#remove-duplicates)
      * 5.3.6.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates](#rqsrs-035clickhousenewreplacingmergetreeremoveduplicates)
    * 5.3.7 [Backward Compatibility](#backward-compatibility)
      * 5.3.7.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility](#rqsrs-035clickhousenewreplacingmergetreebackwardcompatibility)
    * 5.3.8 [Version Number](#version-number)
      * 5.3.8.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber](#rqsrs-035clickhousenewreplacingmergetreeversionnumber)
    * 5.3.9 [Handling Deleted Data](#handling-deleted-data)
      * 5.3.9.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData](#rqsrs-035clickhousenewreplacingmergetreehandlingdeleteddata)
    * 5.3.10 [Non-Functional Requirements](#non-functional-requirements)
      * 5.3.10.1 [Performance](#performance)
      * 5.3.10.2 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-035clickhousenewreplacingmergetreenonfunctionalrequirementsperformance)
      * 5.3.10.3 [Reliability](#reliability)
      * 5.3.10.4 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-035clickhousenewreplacingmergetreenonfunctionalrequirementsreliability)


## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for 
[NewReplacingMergeTree] which allows for duplicate insertions and combines the capabilities of 
[ReplacingMergeTree] and [CollapsingMergeTree].

[ReplacingMergeTree] is designed to remove duplicate entries with the same sorting key value (ORDER BY table section,
not PRIMARY KEY) and is suitable for clearing out duplicate data in the background in order to save space. 
However, it does not guarantee the absence of duplicates.


## Feature Diagram

Test feature diagram.

```mermaid

```

## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/41005

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-035.ClickHouse.NewReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [NewReplacingMergeTree] engine which allows insertion of duplicates by adding an extra
sign column (possible values: -1 / 1) to the ReplacingMergeTree. The sign column is optional, but if enabled, the version 
column becomes mandatory. 

### ReplacingMergeTree

#### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree
version: 1.0

[NewReplacingMergeTree] engine shall support all [ReplacingMergeTree] possibilities.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting 
key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a 
merge, which occurs in the background at an unknown time, and the system cannot be planned for. 
However, the `OPTIMIZE` query can be used to run an unscheduled merge.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.DataDeduplication

[ReplacingMergeTree] engine shall support remove duplicate entries with the same sorting key value during a 
merge process.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.OptimizeMerge

[ReplacingMergeTree] engine shall support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process 
must occur in the background at an unknown time, and the system cannot be planned for.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.UniquenessOfRows

[ReplacingMergeTree] engine shall support uniqueness of rows determined by the `ORDER BY` table section, 
not PRIMARY KEY.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn
version: 1.0

[ReplacingMergeTree] engine shall support a version column with a type of UInt*, Date, DateTime, or DateTime64.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows
version: 1.0

[ReplacingMergeTree] engine shall support merging, the engine must leave only one row from all the rows with the same 
sorting key. 

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules
version: 1.0

[ReplacingMergeTree] engine shall support selection rules: if a version column is specified, the engine must select the 
row with the maximum version. If no version column is specified, the engine must select the last row in the selection.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation
version: 1.0

[ReplacingMergeTree] engine shall support same clauses as when creating a MergeTree table, with the addition of the 
ver column.

### CollapsingMergeTree

#### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree
version: 1.0

[NewReplacingMergeTree] engine shall support all [CollapsingMergeTree] possibilities.

#### Duplicate Insertions

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions
version: 1.0

[NewReplacingMergeTree] engine shall allow duplicate insertions of rows.

#### Update

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update
version: 1.0

[NewReplacingMergeTree] engine shall allow updating a row by inserting a row with (arbitrary) greater version. 
The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.

#### Delete

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete
version: 1.0

[NewReplacingMergeTree] engine shall allow deleting a row by inserting a row with (arbitrary) greater version and
-1 sign. The replacing merge algorithm leaves only one row with sign = -1, and then it is filtered out.

#### Update Key Columns

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns
version: 1.0

[NewReplacingMergeTree] engine shall allow updating key columns by deleting a row and inserting a new one.

#### Remove Duplicates

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates
version: 1.0

[NewReplacingMergeTree] engine shall allow removing duplicates by using the "Replacing" merge algorithm.

#### Backward Compatibility

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility
version: 1.0

[NewReplacingMergeTree] engine shall allow backward compatible with previous versions of the [ReplacingMergeTree].
This means that it should be an option when creating a table.

#### Version Number

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber
version: 1.0

[NewReplacingMergeTree] engine shall increase version no matter what the operation on the data was made. If two 
inserted rows have the same version number, the last inserted one is the one kept.

#### Handling Deleted Data

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData
version: 1.0

[NewReplacingMergeTree] engine shall allow filter out deleted data when queried but not remove it from disk.
The information of deleted data is needed for KPIs.

#### Non-Functional Requirements

##### Performance

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[NewReplacingMergeTree] engine shall allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[NewReplacingMergeTree] engine shall be reliable and not lose any data.



[SRS]: #srs
[NewReplacingMergeTree]: https://github.com/ClickHouse/ClickHouse/pull/41005
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/


