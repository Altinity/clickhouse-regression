# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_03x_ClickHouse_ReplacingMergeTree = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support [ReplacingMergeTree] engine which allows to  remove duplicate entries with the same sorting \n"
        "key value (`ORDER BY` table section, not `PRIMARY KEY`) during a merge process. The deduplication occurs only during a \n"
        "merge, which occurs in the background at an unknown time, and the system cannot be planned for. \n"
        "However, the `OPTIMIZE` query can be used to run an unscheduled merge.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_DataDeduplication = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.DataDeduplication",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support remove duplicate entries with the same sorting key value during a \n"
        "merge process.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_OptimizeMerge = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.OptimizeMerge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support `OPTIMIZE` query which can be used to run an unscheduled merge as merge process \n"
        "must occur in the background at an unknown time, and the system cannot be planned for.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.3.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_UniquenessOfRows = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.UniquenessOfRows",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support uniqueness of rows determined by the `ORDER BY` table section, \n"
        "not PRIMARY KEY.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.4.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_VersionColumn = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.VersionColumn",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support a version column with a type of UInt*, Date, DateTime, or DateTime64.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.5.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_SelectionOfRows = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support merging, the engine must leave only one row from all the rows with the same \n"
        "sorting key. \n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.6.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_SelectionOfRows_SelectionRules = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows.SelectionRules",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support selection rules: if a version column is specified, the engine must select the \n"
        "row with the maximum version. If no version column is specified, the engine must select the last row in the selection.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.6.2.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_TableCreation = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.TableCreation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ReplacingMergeTree] engine shall support same clauses as when creating a MergeTree table, with the addition of the \n"
        "ver column.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.7.1",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Performance = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[NewReplacingMergeTree] engine shall allow handle large volumes of data efficiently.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.7.2.2",
)

RQ_SRS_03x_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Reliability = Requirement(
    name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[NewReplacingMergeTree] engine shall be reliable and not lose any data.\n"
        "\n"
        "\n"
        "\n"
        "[SRS]: #srs\n"
        "[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree/\n"
        "\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.7.2.4",
)

SRS03x_ClickHouse_ReplacingMergeTree = Specification(
    name="SRS03x ClickHouse ReplacingMergeTree",
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
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Feature Diagram", level=1, num="2"),
        Heading(name="Related Resources", level=1, num="3"),
        Heading(name="Terminology", level=1, num="4"),
        Heading(name="SRS", level=2, num="4.1"),
        Heading(name="Requirements", level=1, num="5"),
        Heading(name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree", level=2, num="5.1"),
        Heading(name="Data Deduplication", level=2, num="5.2"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.DataDeduplication",
            level=3,
            num="5.2.1",
        ),
        Heading(name="Optimize Merge", level=2, num="5.3"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.OptimizeMerge",
            level=3,
            num="5.3.1",
        ),
        Heading(name="UniquenessOfRows", level=2, num="5.4"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.UniquenessOfRows",
            level=3,
            num="5.4.1",
        ),
        Heading(name="VersionColumn", level=2, num="5.5"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.VersionColumn",
            level=3,
            num="5.5.1",
        ),
        Heading(name="SelectionOfRows", level=2, num="5.6"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows",
            level=3,
            num="5.6.1",
        ),
        Heading(name="SelectionRules", level=3, num="5.6.2"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.SelectionOfRows.SelectionRules",
            level=4,
            num="5.6.2.1",
        ),
        Heading(name="TableCreation", level=2, num="5.7"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.TableCreation",
            level=3,
            num="5.7.1",
        ),
        Heading(name="Non-Functional Requirements", level=3, num="5.7.2"),
        Heading(name="Performance", level=4, num="5.7.2.1"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Performance",
            level=4,
            num="5.7.2.2",
        ),
        Heading(name="Reliability", level=4, num="5.7.2.3"),
        Heading(
            name="RQ.SRS-03x.ClickHouse.ReplacingMergeTree.NonFunctionalRequirements.Reliability",
            level=4,
            num="5.7.2.4",
        ),
    ),
    requirements=(
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_DataDeduplication,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_OptimizeMerge,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_UniquenessOfRows,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_VersionColumn,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_SelectionOfRows,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_SelectionOfRows_SelectionRules,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_TableCreation,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Performance,
        RQ_SRS_03x_ClickHouse_ReplacingMergeTree_NonFunctionalRequirements_Reliability,
    ),
    content="""
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
""",
)
