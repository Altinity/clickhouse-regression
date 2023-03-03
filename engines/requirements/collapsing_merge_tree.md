# SRS036 ClickHouse CollapsingMergeTree
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)


## Introduction

[CollapsingMergeTree] an engine that inherits from MergeTree and adds the logic of rows
collapsing to data parts merge algorithm. The engine is designed to asynchronously delete pairs of rows if all of the 
fields in a sorting key (ORDER BY) are equivalent except for the particular field Sign, which can have values of 
1 and -1. Rows without a pair are kept, leading to a significant reduction in storage volume and improved SELECT query 
efficiency. 



## Feature Diagram

Test feature diagram.

```mermaid

```

## Related Resources

**ClickHouse docs**

* https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-036.ClickHouse.CollapsingMergeTree
version: 1.0

[ClickHouse] SHALL support [CollapsingMergeTree]

### Blanc

#### RQ.SRS-036.ClickHouse.CollapsingMergeTree.Blanc
version: 1.0





[SRS]: #srs
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree/



