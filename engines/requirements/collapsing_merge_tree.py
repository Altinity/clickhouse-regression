# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.230125.1024636.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_036_ClickHouse_CollapsingMergeTree = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [CollapsingMergeTree] an engine that inherits from MergeTree and adds the logic of rows\n'
        'collapsing to data parts merge algorithm. The engine is designed to asynchronously delete pairs of rows if all of the \n'
        'fields in a sorting key (ORDER BY) are equivalent except for the particular field Sign, which can have values of 1 and \n'
        '-1. Rows without a pair are kept, leading to a significant reduction in storage volume and improved SELECT query\n'
        'efficiency.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.1'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_Parameters = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL support `Sign` column with the type of row: 1 is a "state" row,\n'
        '-1 is a "cancel" row.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_CollapsingData = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL support writing the changes of an object sequentially using the particular column Sign.\n'
        'If Sign = 1, it means that the row is a state of an object, while Sign = -1 means the cancellation of the state of an\n'
        'object with the same attributes.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.3.1'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_MergeAlgorithm = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL support adding of the logic of rows collapsing to data parts merge [Algorithm], \n'
        'which asynchronously deletes pairs of rows if all of the fields in a sorting key (ORDER BY) are equivalent except for \n'
        'the Sign column. Rows without a pair are kept. The engine significantly reduces the volume of storage and increases \n'
        'the efficiency of SELECT query.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.4.1'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_TableCreation = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the \n'
        '`Sign` column.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.5.1'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_NonFunctionalRequirements_Performance = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL allow handle large volumes of data efficiently.\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.2'
)

RQ_SRS_036_ClickHouse_CollapsingMergeTree_NonFunctionalRequirements_Reliability = Requirement(
    name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[CollapsingMergeTree] engine SHALL be reliable and not lose any data.\n'
        '\n'
        '[SRS]: #srs\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/\n'
        '[Algorithm]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/#table_engine-collapsingmergetree-collapsing-algorithm\n'
        '\n'
        '\n'
        '\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.6.4'
)

SRS036_ClickHouse_CollapsingMergeTree = Specification(
    name='SRS036 ClickHouse CollapsingMergeTree',
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
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree', level=2, num='4.1'),
        Heading(name='Parameters', level=2, num='4.2'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters', level=3, num='4.2.1'),
        Heading(name='Collapsing Data', level=2, num='4.3'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData', level=3, num='4.3.1'),
        Heading(name='Merge Algorithm', level=2, num='4.4'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm', level=3, num='4.4.1'),
        Heading(name='TableCreation', level=2, num='4.5'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation', level=3, num='4.5.1'),
        Heading(name='Non-Functional Requirements', level=2, num='4.6'),
        Heading(name='Performance', level=3, num='4.6.1'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance', level=3, num='4.6.2'),
        Heading(name='Reliability', level=3, num='4.6.3'),
        Heading(name='RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability', level=3, num='4.6.4'),
        ),
    requirements=(
        RQ_SRS_036_ClickHouse_CollapsingMergeTree,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_Parameters,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_CollapsingData,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_MergeAlgorithm,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_TableCreation,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_NonFunctionalRequirements_Performance,
        RQ_SRS_036_ClickHouse_CollapsingMergeTree_NonFunctionalRequirements_Reliability,
        ),
    content='''
# SRS036 ClickHouse CollapsingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree](#rqsrs-036clickhousecollapsingmergetree)
  * 4.2 [Parameters](#parameters)
    * 4.2.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters](#rqsrs-036clickhousecollapsingmergetreeparameters)
  * 4.3 [Collapsing Data](#collapsing-data)
    * 4.3.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData](#rqsrs-036clickhousecollapsingmergetreecollapsingdata)
  * 4.4 [Merge Algorithm](#merge-algorithm)
    * 4.4.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm](#rqsrs-036clickhousecollapsingmergetreemergealgorithm)
  * 4.5 [TableCreation](#tablecreation)
    * 4.5.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation](#rqsrs-036clickhousecollapsingmergetreetablecreation)
  * 4.6 [Non-Functional Requirements](#non-functional-requirements)
    * 4.6.1 [Performance](#performance)
    * 4.6.2 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-036clickhousecollapsingmergetreenonfunctionalrequirementsperformance)
    * 4.6.3 [Reliability](#reliability)
    * 4.6.4 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-036clickhousecollapsingmergetreenonfunctionalrequirementsreliability)


## Introduction

[CollapsingMergeTree] an engine that inherits from MergeTree and adds the logic of rows
collapsing to data parts merge algorithm. The engine is designed to asynchronously delete pairs of rows if all of the 
fields in a sorting key (ORDER BY) are equivalent except for the particular field Sign, which can have values of 
1 and -1. Rows without a pair are kept, leading to a significant reduction in storage volume and improved SELECT query 
efficiency. 

## Related Resources

**ClickHouse docs**

* https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-036.ClickHouse.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support [CollapsingMergeTree] an engine that inherits from MergeTree and adds the logic of rows
collapsing to data parts merge algorithm. The engine is designed to asynchronously delete pairs of rows if all of the 
fields in a sorting key (ORDER BY) are equivalent except for the particular field Sign, which can have values of 1 and 
-1. Rows without a pair are kept, leading to a significant reduction in storage volume and improved SELECT query
efficiency.

### Parameters

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters
version: 1.0

[CollapsingMergeTree] engine SHALL support `Sign` column with the type of row: 1 is a "state" row,
-1 is a "cancel" row.

### Collapsing Data

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData
version: 1.0

[CollapsingMergeTree] engine SHALL support writing the changes of an object sequentially using the particular column Sign.
If Sign = 1, it means that the row is a state of an object, while Sign = -1 means the cancellation of the state of an
object with the same attributes.

### Merge Algorithm

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm
version: 1.0

[CollapsingMergeTree] engine SHALL support adding of the logic of rows collapsing to data parts merge [Algorithm], 
which asynchronously deletes pairs of rows if all of the fields in a sorting key (ORDER BY) are equivalent except for 
the Sign column. Rows without a pair are kept. The engine significantly reduces the volume of storage and increases 
the efficiency of SELECT query.

### TableCreation

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation
version: 1.0

[CollapsingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the 
`Sign` column.

### Non-Functional Requirements

#### Performance

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[CollapsingMergeTree] engine SHALL allow handle large volumes of data efficiently.

#### Reliability

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[CollapsingMergeTree] engine SHALL be reliable and not lose any data.

[SRS]: #srs
[ClickHouse]: https://clickhouse.com
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/
[Algorithm]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/#table_engine-collapsingmergetree-collapsing-algorithm
'''
)
