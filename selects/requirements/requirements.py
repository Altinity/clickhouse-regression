# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.221103.1222218.
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
        '[ClickHouse] SHALL support adding [FINAL modifier] clause automatically to all [SELECT] queries\n'
        'for all table engines that support [FINAL modifier] and return the same result as if [FINAL modifier] clause\n'
        'was specified in the [SELECT] query explicitly.\n'
        '\n'
    ),
    link=None,
    level=2,
    num='5.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_CreateStatement = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]\n'
        'on all [SELECT] queries when the setting is value is set to `1`.\n'
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
    level=4,
    num='5.2.1.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ConfigFile = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ConfigFile',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support specifying `force_select_final` [MergeTree] table setting to enable automatic [FINAL modifier]\n'
        'on all MergeTree tables [SELECT] queries inside the XML configuration file.\n'
        '\n'
        'For example,\n'
        '\n'
        '```sql\n'
        '<clickhouse>\n'
        '    <merge_tree>\n'
        '        <force_select_final>1</force_select_final>\n'
        '    </merge_tree>\n'
        '</clickhouse>\n'
        '\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.2.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_IgnoreOnNotSupportedTableEngines = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL silently ignore `force_select_final` table engine setting for any table\n'
        "engine that doesn't support [FINAL modifier] clause.\n"
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.2.3.1'
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
        '* ReplacingMergeTree(version)\n'
        '* [CollapsingMergeTree(sign)]\n'
        '* AggregatingMergeTree\n'
        '* SummingMergeTree\n'
        '* [VersionedCollapsingMergeTree(sign,version)]\n'
        '\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.3.1.1'
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
        '* ReplicatedReplacingMergeTree(version)\n'
        '* ReplicatedCollapsingMergeTree(sign)\n'
        '* ReplicatedAggregatingMergeTree\n'
        '* ReplicatedSummingMergeTree\n'
        '* ReplicatedVersionedCollapsingMergeTree(sign,version)\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.3.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support the following table engines over tables that have automatic [FINAL modifier] clause enabled:\n'
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
    num='5.3.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support automatic [FINAL modifier] for any type of [SELECT] queries.\n'
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
    level=3,
    num='5.4.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] in any subquery that reads from a table that\n'
        'has automatic [FINAL modifier] enabled.\n'
        '\n'
        'For example,\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.2.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        '* INNER JOIN\n'
        '* LEFT OUTER JOIN\n'
        '* RIGHT OUTER JOIN\n'
        '* FULL OUTER JOIN\n'
        '* CROSS JOIN\n'
        '* LEFT SEMI JOIN and RIGHT SEMI JOIN\n'
        '* LEFT ANTI JOIN and RIGHT ANTI JOIN\n'
        '* LEFT ANY JOIN, RIGHT ANY JOIN and INNER ANY JOIN\n'
        '* ASOF JOIN and LEFT ASOF JOIN\n'
        '\n'
        'For example,\n'
        '```sql\n'
        'select count() from lhs inner join rhs on lhs.x = rhs.x;\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.3.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in [UNION] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        'For example,\n'
        '```sql\n'
        '\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.4.1'
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With = Requirement(
    name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support applying [FINAL modifier] for any table in subquery inside the [WITH] clause for which\n'
        'the automatic [FINAL modifier] is enabled.\n'
        '\n'
        'For example,\n'
        '```sql\n'
        '\n'
        '```\n'
        '\n'
        '[SRS]: #srs\n'
        '[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n'
        '[JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/join\n'
        '[UNION]: https://clickhouse.com/docs/en/sql-reference/statements/select/union\n'
        '[WITH]: https://clickhouse.com/docs/en/sql-reference/statements/select/with\n'
        '[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/\n'
        '[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree\n'
        '[CollapsingMergeTree(sign)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree\n'
        '[VersionedCollapsingMergeTree(sign,version)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree\n'
        '[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '\n'
    ),
    link=None,
    level=4,
    num='5.4.5.1'
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
        Heading(name='Create Statement', level=3, num='5.2.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement', level=4, num='5.2.1.1'),
        Heading(name='Configuration File', level=3, num='5.2.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ConfigFile', level=4, num='5.2.2.1'),
        Heading(name='Not Supported Table Engines', level=3, num='5.2.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines', level=4, num='5.2.3.1'),
        Heading(name='Supported Table Engines', level=2, num='5.3'),
        Heading(name='MergeTree', level=3, num='5.3.1'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree', level=4, num='5.3.1.1'),
        Heading(name='ReplicatedMergeTree', level=3, num='5.3.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree', level=4, num='5.3.2.1'),
        Heading(name='EnginesOverOtherEngines', level=3, num='5.3.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines', level=4, num='5.3.3.1'),
        Heading(name='Select Queries', level=2, num='5.4'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries', level=3, num='5.4.1'),
        Heading(name='Subquery', level=3, num='5.4.2'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery', level=4, num='5.4.2.1'),
        Heading(name='JOIN', level=3, num='5.4.3'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join', level=4, num='5.4.3.1'),
        Heading(name='UNION', level=3, num='5.4.4'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union', level=4, num='5.4.4.1'),
        Heading(name='WITH ', level=3, num='5.4.5'),
        Heading(name='RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With', level=4, num='5.4.5.1'),
        ),
    requirements=(
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_CreateStatement,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ConfigFile,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_IgnoreOnNotSupportedTableEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With,
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
    * 5.2.1 [Create Statement](#create-statement)
      * 5.2.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingcreatestatement)
    * 5.2.2 [Configuration File](#configuration-file)
      * 5.2.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ConfigFile](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingconfigfile)
    * 5.2.3 [Not Supported Table Engines](#not-supported-table-engines)
      * 5.2.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingignoreonnotsupportedtableengines)
  * 5.3 [Supported Table Engines](#supported-table-engines)
    * 5.3.1 [MergeTree](#mergetree)
      * 5.3.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesmergetree)
    * 5.3.2 [ReplicatedMergeTree](#replicatedmergetree)
      * 5.3.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesreplicatedmergetree)
    * 5.3.3 [EnginesOverOtherEngines](#enginesoverotherengines)
      * 5.3.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesenginesoverotherengines)
  * 5.4 [Select Queries](#select-queries)
    * 5.4.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries](#rqsrs-032clickhouseautomaticfinalmodifierselectqueries)
    * 5.4.2 [Subquery](#subquery)
      * 5.4.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubquery)
    * 5.4.3 [JOIN](#join)
      * 5.4.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoin)
    * 5.4.4 [UNION](#union)
      * 5.4.4.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesunion)
    * 5.4.5 [WITH ](#with-)
      * 5.4.5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieswith)

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

[ClickHouse] SHALL support adding [FINAL modifier] clause automatically to all [SELECT] queries
for all table engines that support [FINAL modifier] and return the same result as if [FINAL modifier] clause
was specified in the [SELECT] query explicitly.

### Table Engine Setting

#### Create Statement

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.CreateStatement
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]
on all [SELECT] queries when the setting is value is set to `1`.

For example,

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING force_select_final=1
```

#### Configuration File

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ConfigFile
version: 1.0 priority: 1.0

[ClickHouse] SHALL support specifying `force_select_final` [MergeTree] table setting to enable automatic [FINAL modifier]
on all MergeTree tables [SELECT] queries inside the XML configuration file.

For example,

```sql
<clickhouse>
    <merge_tree>
        <force_select_final>1</force_select_final>
    </merge_tree>
</clickhouse>

```

#### Not Supported Table Engines

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.IgnoreOnNotSupportedTableEngines
version: 1.0 priority: 1.0

[ClickHouse] SHALL silently ignore `force_select_final` table engine setting for any table
engine that doesn't support [FINAL modifier] clause.


### Supported Table Engines

#### MergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:

* [ReplacingMergeTree]
* ReplacingMergeTree(version)
* [CollapsingMergeTree(sign)]
* AggregatingMergeTree
* SummingMergeTree
* [VersionedCollapsingMergeTree(sign,version)]


#### ReplicatedMergeTree

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated 
[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) 
table engines variants:

* ReplicatedReplacingMergeTree
* ReplicatedReplacingMergeTree(version)
* ReplicatedCollapsingMergeTree(sign)
* ReplicatedAggregatingMergeTree
* ReplicatedSummingMergeTree
* ReplicatedVersionedCollapsingMergeTree(sign,version)

#### EnginesOverOtherEngines

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines
version: 1.0

[ClickHouse] SHALL support the following table engines over tables that have automatic [FINAL modifier] clause enabled:

* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)
* [Buffer](https://clickhouse.com/docs/en/engines/table-engines/special/buffer)
* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)
* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)


### Select Queries

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries
version: 1.0

[ClickHouse] SHALL support automatic [FINAL modifier] for any type of [SELECT] queries.

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

#### Subquery

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] in any subquery that reads from a table that
has automatic [FINAL modifier] enabled.

For example,

#### JOIN

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause for which
the automatic [FINAL modifier] is enabled.

* INNER JOIN
* LEFT OUTER JOIN
* RIGHT OUTER JOIN
* FULL OUTER JOIN
* CROSS JOIN
* LEFT SEMI JOIN and RIGHT SEMI JOIN
* LEFT ANTI JOIN and RIGHT ANTI JOIN
* LEFT ANY JOIN, RIGHT ANY JOIN and INNER ANY JOIN
* ASOF JOIN and LEFT ASOF JOIN

For example,
```sql
select count() from lhs inner join rhs on lhs.x = rhs.x;
```

#### UNION

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in [UNION] clause for which
the automatic [FINAL modifier] is enabled.

For example,
```sql

```

#### WITH 

##### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With
version: 1.0

[ClickHouse] SHALL support applying [FINAL modifier] for any table in subquery inside the [WITH] clause for which
the automatic [FINAL modifier] is enabled.

For example,
```sql

```

[SRS]: #srs
[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/
[JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/join
[UNION]: https://clickhouse.com/docs/en/sql-reference/statements/select/union
[WITH]: https://clickhouse.com/docs/en/sql-reference/statements/select/with
[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree
[CollapsingMergeTree(sign)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree
[VersionedCollapsingMergeTree(sign,version)]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree
[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier
[ClickHouse]: https://clickhouse.com
'''
)
