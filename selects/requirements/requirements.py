# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_AutomaticFinalModifier = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support adding [FINAL modifier] clause to all [SELECT] queries\n'
        'for all table engines that support it.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='5.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `force_select_final` table config setting to enable automatic [FINAL modifier]\n'
        'when the setting is set to `1`.\n'
        '\n'
        'For example,\n'
        '\n'
        '```sql\n'
        'CREATE TABLE table (...)\n'
        'Engine=ReplacingMergeTree\n'
        'SETTTING force_select_final=1\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='5.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupport = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupport',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `force_select_final` table config setting when MergeTree table engine\n'
        "doesn't support FINAL.\n"
        '\n'
    ),
    link=None,
    level=3,
    num='5.2.2'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `auto_final` SELECT query setting to disable automatic [FINAL modifier].\n'
        '\n'
        'For example,\n'
        '\n'
        '```sql\n'
        'SELECT * FROM table; -- actually does SELECT * FROM table FINAL if SETTTING force_select_final=1\n'
        'SELECT * FROM table SETTINGS ignore_force_select_final=1; -- 0 by default, 1 - means ignore force_select_final\n'
        ' from merge tree.\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=3,
    num='5.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:\n'
        '\n'
        '* [ReplacingMergeTree]\n'
        '* [CollapsingMergeTree]\n'
        '* [VersionedCollapsingMergeTree]\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated \n'
        '[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) \n'
        'table engines variants:\n'
        '\n'
        '* ReplicatedReplacingMergeTree\n'
        '* ReplicatedCollapsingMergeTree\n'
        '* ReplicatedVersionedCollapsingMergeTree\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support engines that operate over other engines if they were created over supported\n'
        'MergeTree] table engines variants:\n'
        '\n'
        '* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)\n'
        '* [Buffer](https://clickhouse.com/docs/en/engines/table-engines/special/buffer)\n'
        '* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)\n'
        '* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with the same result \n'
        'as for manual [FINAL modifier]:\n'
        '\n'
        '```sql\n'
        '[WITH expr_list|(subquery)]\n'
        'SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list\n'
        '[FROM [db.]table | (subquery) | table_function] [FINAL]\n'
        '[SAMPLE sample_coeff]\n'
        '[ARRAY JOIN ...]\n'
        '[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)\n'
        '[PREWHERE expr]\n'
        '[WHERE expr]\n'
        '[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]\n'
        '[HAVING expr]\n'
        '[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]\n'
        '[LIMIT [offset_value, ]n BY columns]\n'
        '[LIMIT [n, ]m] [WITH TIES]\n'
        '[SETTINGS ...]\n'
        '[UNION  ...]\n'
        '[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]\n'
        '[FORMAT format]\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_JoinSelectQueries = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.JoinSelectQueries',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [JOIN] applying [FINAL modifier] to all\n'
        'tables which has `force_select_final=1` and disable it to them if this [SELECT] query has `SETTING`\n'
        '`ignore_force_select_final=1`.\n'
        '\n'
        '[SRS]: #srs\n'
        '[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n'
        '[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/\n'
        '[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree\n'
        '[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree\n'
        '[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree\n'
        '[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.5.2.1'
)

SRS032_ClickHouse_Automatic_Final_Modifier_For_Select_Queries = Specification(
    name='SRS032 ClickHouse Automatic Final Modifier For Select Queries',
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
        Heading(name='Feature Diagram', level=1, num='2'),
        Heading(name='Related Resources', level=1, num='3'),
        Heading(name='Terminology', level=1, num='4'),
        Heading(name='SRS', level=2, num='4.1'),
        Heading(name='Requirements', level=1, num='5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier', level=2, num='5.1'),
        Heading(name='Table Engine Setting', level=2, num='5.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting', level=3, num='5.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupport', level=3, num='5.2.2'),
        Heading(name='Select Query Setting', level=2, num='5.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting', level=3, num='5.3.1'),
        Heading(name='Supported Table Engines', level=2, num='5.4'),
        Heading(name='MergeTree', level=3, num='5.4.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree', level=4, num='5.4.1.1'),
        Heading(name='ReplicatedMergeTree', level=3, num='5.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree', level=4, num='5.4.2.1'),
        Heading(name='EnginesOverOtherEngines', level=3, num='5.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines', level=4, num='5.4.3.1'),
        Heading(name='Supported Select Queries', level=2, num='5.5'),
        Heading(name='SelectQueries', level=3, num='5.5.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries', level=4, num='5.5.1.1'),
        Heading(name='JoinSelectQueries', level=3, num='5.5.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.JoinSelectQueries', level=4, num='5.5.2.1'),
        ),
    requirements=(
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupport,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_JoinSelectQueries,
        ),
    content='''
# SRS032 ClickHouse Automatic Final Modifier For Select Queries
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier](#rqsrs-032clickhouseautomaticfinalmodifier)
  * 5.2 [Table Engine Setting](#table-engine-setting)
    * 5.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesetting)
    * 5.2.2 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupport](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingnotsupport)
  * 5.3 [Select Query Setting](#select-query-setting)
    * 5.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting](#rqsrs-032clickhouseautomaticfinalmodifierselectquerysetting)
  * 5.4 [Supported Table Engines](#supported-table-engines)
    * 5.4.1 [MergeTree](#mergetree)
      * 5.4.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesmergetree)
    * 5.4.2 [ReplicatedMergeTree](#replicatedmergetree)
      * 5.4.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesreplicatedmergetree)
    * 5.4.3 [EnginesOverOtherEngines](#enginesoverotherengines)
      * 5.4.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesenginesoverotherengines)
  * 5.5 [Supported Select Queries](#supported-select-queries)
    * 5.5.1 [SelectQueries](#selectqueries)
      * 5.5.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries](#rqsrs-032clickhouseautomaticfinalmodifierselectqueries)
    * 5.5.2 [JoinSelectQueries](#joinselectqueries)
      * 5.5.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.JoinSelectQueries](#rqsrs-032clickhouseautomaticfinalmodifierjoinselectqueries)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] support for automatically
adding [FINAL modifier] to all [SELECT] queries for a given table.

## Feature Diagram

Test feature diagram.

```mermaid
flowchart TB;

  classDef yellow fill:#ffff32,stroke:#323,stroke-width:4px,color:black;
  classDef yellow2 fill:#ffff32,stroke:#323,stroke-width:4px,color:red;
  classDef green fill:#00ff32,stroke:#323,stroke-width:4px,color:black;
  classDef red fill:red,stroke:#323,stroke-width:4px,color:black;
  classDef blue fill:blue,stroke:#323,stroke-width:4px,color:white;
  
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
        2A["force_select_final"]:::yellow
        3A["1"]:::blue
        4A["0"]:::blue
    end
    
    subgraph D["SELECT"]
        1D["SELECT"]:::green
        2D["ignore_force_select_final"]:::yellow
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

### RQ.SRS-032.ClickHouse.AutomaticFinalModifier
version: 1.0

[ClickHouse] SHALL support adding [FINAL modifier] clause to all [SELECT] queries
for all table engines that support it.

### Table Engine Setting

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table config setting to enable automatic [FINAL modifier]
when the setting is set to `1`.

For example,

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING force_select_final=1
```

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupport
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table config setting when MergeTree table engine
doesn't support FINAL.

### Select Query Setting

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `auto_final` SELECT query setting to disable automatic [FINAL modifier].

For example,

```sql
SELECT * FROM table; -- actually does SELECT * FROM table FINAL if SETTTING force_select_final=1
SELECT * FROM table SETTINGS ignore_force_select_final=1; -- 0 by default, 1 - means ignore force_select_final
 from merge tree.
```

### Supported Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:

* [ReplacingMergeTree]
* [CollapsingMergeTree]
* [VersionedCollapsingMergeTree]

#### ReplicatedMergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated 
[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) 
table engines variants:

* ReplicatedReplacingMergeTree
* ReplicatedCollapsingMergeTree
* ReplicatedVersionedCollapsingMergeTree

#### EnginesOverOtherEngines

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines
version: 1.0

[ClickHouse] SHALL support engines that operate over other engines if they were created over supported
MergeTree] table engines variants:

* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)
* [Buffer](https://clickhouse.com/docs/en/engines/table-engines/special/buffer)
* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)
* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)


### Supported Select Queries

#### SelectQueries

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with the same result 
as for manual [FINAL modifier]:

```sql
[WITH expr_list|(subquery)]
SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list
[FROM [db.]table | (subquery) | table_function] [FINAL]
[SAMPLE sample_coeff]
[ARRAY JOIN ...]
[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)
[PREWHERE expr]
[WHERE expr]
[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]
[HAVING expr]
[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]
[LIMIT [offset_value, ]n BY columns]
[LIMIT [n, ]m] [WITH TIES]
[SETTINGS ...]
[UNION  ...]
[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]
[FORMAT format]
```

#### JoinSelectQueries

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.JoinSelectQueries
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for [SELECT] queries with [JOIN] applying [FINAL modifier] to all
tables which has `force_select_final=1` and disable it to them if this [SELECT] query has `SETTING`
`ignore_force_select_final=1`.

[SRS]: #srs
[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree
[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree
[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier
[ClickHouse]: https://clickhouse.com
'''
)
