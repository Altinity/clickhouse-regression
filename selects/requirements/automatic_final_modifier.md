# SRS033 ClickHouse Automatic Final Modifier For Select Queries
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
  * 3.2 [Select Final](#select-final)
  * 3.3 [FinalModifier](#finalmodifier)
      * 3.3.0.1 [RQ.SRS-033.ClickHouse.SelectFinal.FinalModifier](#rqsrs-033clickhouseselectfinalfinalmodifier)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-033.ClickHouse.SelectFinal](#rqsrs-033clickhouseselectfinal)
  * 4.2 [Config Setting](#config-setting)
    * 4.2.1 [RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting](#rqsrs-033clickhouseselectfinalconfigsetting)
    * 4.2.2 [RQ.SRS-033.ClickHouse.SelectFinal.SelectAutoFinalSetting](#rqsrs-033clickhouseselectfinalselectautofinalsetting)
  * 4.3 [Supported Table Engines](#supported-table-engines)
    * 4.3.1 [MergeTree](#mergetree)
      * 4.3.1.1 [RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines](#rqsrs-033clickhouseselectfinalsupportedtableengines)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for automatically
adding [FINAL modifier] to all [SELECT] queries for a given table.

## Feature Diagram

Test feature diagram.

```mermaid
flowchart TB;

  classDef yellow fill:#ffff33,stroke:#333,stroke-width:4px,color:black;
  classDef yellow2 fill:#ffff33,stroke:#333,stroke-width:4px,color:red;
  classDef green fill:#00ff33,stroke:#333,stroke-width:4px,color:black;
  classDef red fill:red,stroke:#333,stroke-width:4px,color:black;
  classDef blue fill:blue,stroke:#333,stroke-width:4px,color:white;
  
  subgraph O["'Select ... Final' Test Feature Diagram"]
  A-->C-->K-->D--"JOIN"-->F
  A-->E-->K

  1A---2A---3A
  2A---4A
  1D---2D---3D
  2D---4D
  1C---2C---3C---4C
  1E---2E---3E---4E
  1K---2K---3K---4K
  1F---2F---3F---4F
  
    subgraph A["Create table section"]

        1A["CREATE"]:::green
        2A["apply_final_by_default"]:::yellow
        3A["1"]:::blue
        4A["0"]:::blue
    end
    
    subgraph D["SELECT"]
        1D["SELECT"]:::green
        2D["auto_final"]:::yellow
        3D["1"]:::blue
        4D["0"]:::blue
    end
    
    subgraph C["Table ENGINES"]
        1C["MergeTree"]:::blue
        2C["ReplacingMergeTree"]:::blue
        3C["CollapsingMergeTree"]:::blue
        4C["VersionedCollapsingMergeTree"]:::blue
    end
    
    subgraph E["Replicated Table ENGINES"]
        1E["ReplicatedMergeTree"]:::blue
        2E["ReplicatedReplacingMergeTree"]:::blue
        3E["ReplicatedCollapsingMergeTree"]:::blue
        4E["ReplicatedVersionedCollapsingMergeTree"]:::blue
    end
      
    subgraph F["Some table"]
        1F["INNER"]:::green
        2F["LEFT"]:::green
        3F["RIGHT"]:::green
        4F["FULL"]:::green
    end
    
    subgraph K["Engines that operate over other engines"]
        1K["View"]:::yellow
        2K["Buffer"]:::yellow
        3K["Distributed"]:::yellow
        4K["MaterializedView"]:::yellow
    end

    

  end
```

## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/40945

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-033.ClickHouse.AutomaticFinalModifier
version: 1.0

[ClickHouse] SHALL support adding [FINAL modifier] clause to all [SELECT] queries
for all table engines that support it.

### Table Engine Setting

#### RQ.SRS-033.ClickHouse.AutomaticFinalModifier.TableEngineSetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `apply_final_by_default` table config setting to enable automatic [FINAL modifier]
when the setting is set to `1`.

For example,

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING apply_final_by_default=1
```

### Select Query Setting

#### RQ.SRS-033.ClickHouse.AutomaticFinalModifier.SelectQuerySetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `auto_final` SELECT query setting to either enable or disable automatic [FINAL modifier].

For example,

```sql
SELECT * FROM table; -- actually does SELECT * FROM table FINAL if SETTTING apply_final_by_default=1
SELECT * FROM table SETTINGS auto_final=0; -- 1 by default, 0 - means ignore apply_final_by_default from merge tree.
```

### Supported Table Engines

#### MergeTree

##### RQ.SRS-033.ClickHouse.AutomaticFinalModifier.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:

* [MergeTree]
* [ReplacingMergeTree]
* [CollapsingMergeTree]
* [VersionedCollapsingMergeTree]


[SRS]: #srs
[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree
[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree
[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier
[ClickHouse]: https://clickhouse.com

