# SRS036 ClickHouse CollapsingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree](#rqsrs-036clickhousecollapsingmergetree)
    * 4.1.1 [Parameters](#parameters)
      * 4.1.1.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters](#rqsrs-036clickhousecollapsingmergetreeparameters)
    * 4.1.2 [Collapsing Data](#collapsing-data)
      * 4.1.2.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData](#rqsrs-036clickhousecollapsingmergetreecollapsingdata)
    * 4.1.3 [Merge Algorithm](#merge-algorithm)
      * 4.1.3.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm](#rqsrs-036clickhousecollapsingmergetreemergealgorithm)
    * 4.1.4 [TableCreation](#tablecreation)
      * 4.1.4.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation](#rqsrs-036clickhousecollapsingmergetreetablecreation)
    * 4.1.5 [Non-Functional Requirements](#non-functional-requirements)
      * 4.1.5.1 [Performance](#performance)
        * 4.1.5.1.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance](#rqsrs-036clickhousecollapsingmergetreenonfunctionalrequirementsperformance)
      * 4.1.5.2 [Reliability](#reliability)
        * 4.1.5.2.1 [RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability](#rqsrs-036clickhousecollapsingmergetreenonfunctionalrequirementsreliability)


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

#### Parameters

##### RQ.SRS-036.ClickHouse.CollapsingMergeTree.Parameters
version: 1.0

[CollapsingMergeTree] engine SHALL support `Sign` column with the type of row: 1 is a "state" row,
-1 is a "cancel" row.

#### Collapsing Data

##### RQ.SRS-036.ClickHouse.CollapsingMergeTree.CollapsingData
version: 1.0

[CollapsingMergeTree] engine SHALL support writing the changes of an object sequentially using the particular column Sign.
If Sign = 1, it means that the row is a state of an object, while Sign = -1 means the cancellation of the state of an
object with the same attributes.

#### Merge Algorithm

##### RQ.SRS-036.ClickHouse.CollapsingMergeTree.MergeAlgorithm
version: 1.0

[CollapsingMergeTree] engine SHALL support adding of the logic of rows collapsing to data parts merge [Algorithm], 
which asynchronously deletes pairs of rows if all of the fields in a sorting key (ORDER BY) are equivalent except for 
the Sign column. Rows without a pair are kept. The engine significantly reduces the volume of storage and increases 
the efficiency of SELECT query.

#### TableCreation

##### RQ.SRS-036.ClickHouse.CollapsingMergeTree.TableCreation
version: 1.0

[CollapsingMergeTree] engine SHALL support same clauses as when creating a MergeTree table, with the addition of the 
`Sign` column.

#### Non-Functional Requirements

##### Performance

###### RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Performance
version: 1.0

[NewReplacingMergeTree] engine SHALL allow handle large volumes of data efficiently.

##### Reliability

###### RQ.SRS-036.ClickHouse.CollapsingMergeTree.NonFunctionalRequirements.Reliability
version: 1.0

[NewReplacingMergeTree] engine SHALL be reliable and not lose any data.

[SRS]: #srs
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/
[Algorithm]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/#table_engine-collapsingmergetree-collapsing-algorithm




