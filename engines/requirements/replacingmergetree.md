# SRS03x ClickHouse ReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree](#rqsrs-03xclickhousereplacingmergetree)
  * 5.2 [Data Deduplication](#data-deduplication)
    * 5.2.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.DataDeduplication](#rqsrs-03xclickhousereplacingmergetreedatadeduplication)
  * 5.3 [Optimize Merge](#optimize-merge)
    * 5.3.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.OptimizeMerge](#rqsrs-03xclickhousereplacingmergetreeoptimizemerge)
  * 5.4 [UniquenessOfRows](#uniquenessofrows)
    * 5.4.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.UniquenessOfRows](#rqsrs-03xclickhousereplacingmergetreeuniquenessofrows)
  * 5.5 [VersionColumn](#versioncolumn)
    * 5.5.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.VersionColumn](#rqsrs-03xclickhousereplacingmergetreeversioncolumn)
  * 5.6 [SelectionOfRows](#selectionofrows)
    * 5.6.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows](#rqsrs-03xclickhousereplacingmergetreeselectionofrows)
    * 5.6.2 [SelectionRules](#selectionrules)
      * 5.6.2.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows.SelectionRules](#rqsrs-03xclickhousereplacingmergetreeselectionofrowsselectionrules)
  * 5.7 [TableCreation](#tablecreation)
    * 5.7.1 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.TableCreation](#rqsrs-03xclickhousereplacingmergetreetablecreation)
    * 5.7.2 [Non-Functional Requirements](#non-functional-requirements)
      * 5.7.2.1 [Performance](#performance)
      * 5.7.2.2 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-03xclickhousereplacingmergetreenonfunctionalrequirementsperformance)
      * 5.7.2.3 [Reliability](#reliability)
      * 5.7.2.4 [RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-03xclickhousereplacingmergetreenonfunctionalrequirementsreliability)


## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for 
[ReplacingMergeTree] is designed to remove duplicate entries with the same sorting key value (ORDER BY table section,
not PRIMARY KEY) and is suitable for clearing out duplicate data in the background in order to save space. 
However, it does not guarantee the absence of duplicates.



## Feature Diagram

Test feature diagram.

```mermaid

```

## Related Resources

**ClickHouse docs**

* https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-03x.ClickHouse.ReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting 
key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a 
merge, which occurs in the background at an unknown time, and the system cannot be planned for. 
However, the `OPTIMIZE` query can be used to run an unscheduled merge.

### Data Deduplication

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.DataDeduplication
version: 1.0

[ReplacingMergeTree] engine shall support remove duplicate entries with the same sorting key value during a 
merge process.

### Optimize Merge

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.OptimizeMerge
version: 1.0

[ReplacingMergeTree] engine shall support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process 
must occur in the background at an unknown time, and the system cannot be planned for.

### UniquenessOfRows

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.UniquenessOfRows
version: 1.0

[ReplacingMergeTree] engine shall support uniqueness of rows determined by the `ORDER BY` table section, 
not PRIMARY KEY.

### VersionColumn

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.VersionColumn
version: 1.0

[ReplacingMergeTree] engine shall support a version column with a type of UInt*, Date, DateTime, or DateTime64.

### SelectionOfRows

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows
version: 1.0

[ReplacingMergeTree] engine shall support merging, the engine must leave only one row from all the rows with the same 
sorting key. 

#### SelectionRules

##### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows.SelectionRules
version: 1.0

[ReplacingMergeTree] engine shall support selection rules: if a version column is specified, the engine must select the 
row with the maximum version. If no version column is specified, the engine must select the last row in the selection.

### TableCreation

#### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.TableCreation
version: 1.0

[ReplacingMergeTree] engine shall support same clauses as when creating a MergeTree table, with the addition of the 
ver column.

#### Non-Functional Requirements

##### Performance

##### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[NewReplacingMergeTree] engine shall allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[NewReplacingMergeTree] engine shall be reliable and not lose any data.



[SRS]: #srs
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/



