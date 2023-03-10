# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_035_ClickHouse_NewReplacingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [NewReplacingMergeTree] engine which allows insertion of duplicates by adding an extra\n'
        'sign column (possible values: -1 / 1) to the ReplacingMergeTree. The sign column is optional, but if enabled, the version \n'
        'column becomes mandatory. \n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL support all [ReplacingMergeTree] possibilities.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_General = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting \n'
        'key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a \n'
        'merge, which occurs in the background at an unknown time, and the system cannot be planned for. \n'
        'However, the `OPTIMIZE` query can be used to run an unscheduled merge.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.2.1.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_VersionColumn = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support a version column with a type of UInt*, Date, DateTime, or DateTime64.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.2.1.5'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_SelectionOfRows = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support merging, the engine must leave only one row from all the rows with the same \n'
        'sorting key. \n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.2.1.6'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_SelectionRules = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support selection rules: if a version column is specified, the engine must select the \n'
        'row with the maximum version. If no version column is specified, the engine must select the last row in the selection.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.2.1.7'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_TableCreation = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ReplacingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the \n'
        'ver column.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.2.1.8'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_CollapsingMergeTree = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL support all [CollapsingMergeTree] possibilities.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_DuplicateInsertions = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow duplicate insertions of rows.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.2.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_Update = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version. \n'
        'The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.3.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_Delete = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow deleting a row by inserting a row with (arbitrary) greater version and\n'
        '-1 sign. The replacing merge algorithm leaves only one row with sign = -1, and then it is filtered out.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.4.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_UpdateKeyColumns = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.5.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_RemoveDuplicates = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.6.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_BackwardCompatibility = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].\n'
        'This means that it should be an option when creating a table.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.7.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_VersionNumber = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two \n'
        'inserted rows have the same version number, the last inserted one is the one kept.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.8.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_HandlingDeletedData = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.\n'
        'The information of deleted data is needed for KPIs.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.9.1'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_NonFunctionalRequirements_Performance = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.10.2'
)

RQ_SRS_035_ClickHouse_NewReplacingMergeTree_NonFunctionalRequirements_Reliability = Requirement(
    name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[NewReplacingMergeTree] engine SHALL be reliable and not lose any data.\n'
        '\n'
        '\n'
        '\n'
        '[SRS]: #srs\n'
        '[NewReplacingMergeTree]: https://github.com/ClickHouse/ClickHouse/pull/41005\n'
        '[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/\n'
        '[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.10.4'
)

SRS035_ClickHouse_NewReplacingMergeTree = Specification(
    name='SRS035 ClickHouse NewReplacingMergeTree',
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
        Heading(name='Introduction', level=1, num='1'),
        Heading(name='Related Resources', level=1, num='2'),
        Heading(name='Terminology', level=1, num='3'),
        Heading(name='SRS', level=2, num='3.1'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree', level=2, num='4.1'),
        Heading(name='ReplacingMergeTree', level=2, num='4.2'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree', level=3, num='4.2.1'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General', level=4, num='4.2.1.1'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.DataDeduplication', level=4, num='4.2.1.2'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.OptimizeMerge', level=4, num='4.2.1.3'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.UniquenessOfRows', level=4, num='4.2.1.4'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn', level=4, num='4.2.1.5'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows', level=4, num='4.2.1.6'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules', level=4, num='4.2.1.7'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation', level=4, num='4.2.1.8'),
        Heading(name='CollapsingMergeTree', level=2, num='4.3'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree', level=3, num='4.3.1'),
        Heading(name='Duplicate Insertions', level=3, num='4.3.2'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions', level=4, num='4.3.2.1'),
        Heading(name='Update', level=3, num='4.3.3'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update', level=4, num='4.3.3.1'),
        Heading(name='Delete', level=3, num='4.3.4'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete', level=4, num='4.3.4.1'),
        Heading(name='Update Key Columns', level=3, num='4.3.5'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns', level=4, num='4.3.5.1'),
        Heading(name='Remove Duplicates', level=3, num='4.3.6'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates', level=4, num='4.3.6.1'),
        Heading(name='Backward Compatibility', level=3, num='4.3.7'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility', level=4, num='4.3.7.1'),
        Heading(name='Version Number', level=3, num='4.3.8'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber', level=4, num='4.3.8.1'),
        Heading(name='Handling Deleted Data', level=3, num='4.3.9'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData', level=4, num='4.3.9.1'),
        Heading(name='Non-Functional Requirements', level=3, num='4.3.10'),
        Heading(name='Performance', level=4, num='4.3.10.1'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance', level=4, num='4.3.10.2'),
        Heading(name='Reliability', level=4, num='4.3.10.3'),
        Heading(name='RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability', level=4, num='4.3.10.4'),
        ),
    requirements=(
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_General,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_VersionColumn,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_SelectionOfRows,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_SelectionRules,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_ReplacingMergeTree_TableCreation,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_CollapsingMergeTree,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_DuplicateInsertions,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_Update,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_Delete,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_UpdateKeyColumns,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_RemoveDuplicates,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_BackwardCompatibility,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_VersionNumber,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_HandlingDeletedData,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_NonFunctionalRequirements_Performance,
        RQ_SRS_035_ClickHouse_NewReplacingMergeTree_NonFunctionalRequirements_Reliability,
        ),
    content='''
# SRS035 ClickHouse NewReplacingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree](#rqsrs-035clickhousenewreplacingmergetree)
  * 4.2 [ReplacingMergeTree](#replacingmergetree)
    * 4.2.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetree)
      * 4.2.1.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreegeneral)
      * 4.2.1.2 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.DataDeduplication](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreedatadeduplication)
      * 4.2.1.3 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.OptimizeMerge](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeoptimizemerge)
      * 4.2.1.4 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.UniquenessOfRows](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeuniquenessofrows)
      * 4.2.1.5 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeversioncolumn)
      * 4.2.1.6 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeselectionofrows)
      * 4.2.1.7 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreeselectionrules)
      * 4.2.1.8 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation](#rqsrs-035clickhousenewreplacingmergetreereplacingmergetreetablecreation)
  * 4.3 [CollapsingMergeTree](#collapsingmergetree)
    * 4.3.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree](#rqsrs-035clickhousenewreplacingmergetreecollapsingmergetree)
    * 4.3.2 [Duplicate Insertions](#duplicate-insertions)
      * 4.3.2.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions](#rqsrs-035clickhousenewreplacingmergetreeduplicateinsertions)
    * 4.3.3 [Update](#update)
      * 4.3.3.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update](#rqsrs-035clickhousenewreplacingmergetreeupdate)
    * 4.3.4 [Delete](#delete)
      * 4.3.4.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete](#rqsrs-035clickhousenewreplacingmergetreedelete)
    * 4.3.5 [Update Key Columns](#update-key-columns)
      * 4.3.5.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns](#rqsrs-035clickhousenewreplacingmergetreeupdatekeycolumns)
    * 4.3.6 [Remove Duplicates](#remove-duplicates)
      * 4.3.6.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates](#rqsrs-035clickhousenewreplacingmergetreeremoveduplicates)
    * 4.3.7 [Backward Compatibility](#backward-compatibility)
      * 4.3.7.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility](#rqsrs-035clickhousenewreplacingmergetreebackwardcompatibility)
    * 4.3.8 [Version Number](#version-number)
      * 4.3.8.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber](#rqsrs-035clickhousenewreplacingmergetreeversionnumber)
    * 4.3.9 [Handling Deleted Data](#handling-deleted-data)
      * 4.3.9.1 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData](#rqsrs-035clickhousenewreplacingmergetreehandlingdeleteddata)
    * 4.3.10 [Non-Functional Requirements](#non-functional-requirements)
      * 4.3.10.1 [Performance](#performance)
      * 4.3.10.2 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-035clickhousenewreplacingmergetreenonfunctionalrequirementsperformance)
      * 4.3.10.3 [Reliability](#reliability)
      * 4.3.10.4 [RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-035clickhousenewreplacingmergetreenonfunctionalrequirementsreliability)


## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for 
[NewReplacingMergeTree] which allows for duplicate insertions and combines the capabilities of 
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

### RQ.SRS-035.ClickHouse.NewReplacingMergeTree
version: 1.0

[ClickHouse] SHALL support [NewReplacingMergeTree] engine which allows insertion of duplicates by adding an extra
sign column (possible values: -1 / 1) to the ReplacingMergeTree. The sign column is optional, but if enabled, the version 
column becomes mandatory. 

### ReplacingMergeTree

#### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree
version: 1.0

[NewReplacingMergeTree] engine SHALL support all [ReplacingMergeTree] possibilities.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.General
version: 1.0

[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting 
key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a 
merge, which occurs in the background at an unknown time, and the system cannot be planned for. 
However, the `OPTIMIZE` query can be used to run an unscheduled merge.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.DataDeduplication

[ReplacingMergeTree] engine SHALL support remove duplicate entries with the same sorting key value during a 
merge process.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.OptimizeMerge

[ReplacingMergeTree] engine SHALL support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process 
must occur in the background at an unknown time, and the system cannot be planned for.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.UniquenessOfRows

[ReplacingMergeTree] engine SHALL support uniqueness of rows determined by the `ORDER BY` table section, 
not PRIMARY KEY.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.VersionColumn
version: 1.0

[ReplacingMergeTree] engine SHALL support a version column with a type of UInt*, Date, DateTime, or DateTime64.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionOfRows
version: 1.0

[ReplacingMergeTree] engine SHALL support merging, the engine must leave only one row from all the rows with the same 
sorting key. 

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.SelectionRules
version: 1.0

[ReplacingMergeTree] engine SHALL support selection rules: if a version column is specified, the engine must select the 
row with the maximum version. If no version column is specified, the engine must select the last row in the selection.

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.ReplacingMergeTree.TableCreation
version: 1.0

[ReplacingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the 
ver column.

### CollapsingMergeTree

#### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.CollapsingMergeTree
version: 1.0

[NewReplacingMergeTree] engine SHALL support all [CollapsingMergeTree] possibilities.

#### Duplicate Insertions

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.DuplicateInsertions
version: 1.0

[NewReplacingMergeTree] engine SHALL allow duplicate insertions of rows.

#### Update

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Update
version: 1.0

[NewReplacingMergeTree] engine SHALL allow updating a row by inserting a row with (arbitrary) greater version. 
The replacing merge algorithm collapses all rows with the same key into one row with the greatest version.

#### Delete

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.Delete
version: 1.0

[NewReplacingMergeTree] engine SHALL allow deleting a row by inserting a row with (arbitrary) greater version and
-1 sign. The replacing merge algorithm leaves only one row with sign = -1, and then it is filtered out.

#### Update Key Columns

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.UpdateKeyColumns
version: 1.0

[NewReplacingMergeTree] engine SHALL allow updating key columns by deleting a row and inserting a new one.

#### Remove Duplicates

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.RemoveDuplicates
version: 1.0

[NewReplacingMergeTree] engine SHALL allow removing duplicates by using the "Replacing" merge algorithm.

#### Backward Compatibility

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.BackwardCompatibility
version: 1.0

[NewReplacingMergeTree] engine SHALL allow backward compatible with previous versions of the [ReplacingMergeTree].
This means that it should be an option when creating a table.

#### Version Number

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.VersionNumber
version: 1.0

[NewReplacingMergeTree] engine SHALL increase version no matter what the operation on the data was made. If two 
inserted rows have the same version number, the last inserted one is the one kept.

#### Handling Deleted Data

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.HandlingDeletedData
version: 1.0

[NewReplacingMergeTree] engine SHALL allow filter out deleted data when queried but not remove it from disk.
The information of deleted data is needed for KPIs.

#### Non-Functional Requirements

##### Performance

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[NewReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.

##### Reliability

##### RQ.SRS-035.ClickHouse.NewReplacingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[NewReplacingMergeTree] engine SHALL be reliable and not lose any data.



[SRS]: #srs
[NewReplacingMergeTree]: https://github.com/ClickHouse/ClickHouse/pull/41005
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/
'''
)
