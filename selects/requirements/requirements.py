# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_032_ClickHouse_AutomaticFinalModifier = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding [FINAL modifier] clause automatically to all [SELECT] queries\n"
        "for all table engines that support [FINAL modifier] and return the same result as if [FINAL modifier] clause\n"
        "was specified in the [SELECT] query explicitly.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ForceSelectFinal = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinal",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]\n"
        "on all [SELECT] queries when the setting is value is set to `1`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "CREATE TABLE table (...)\n"
        "Engine=ReplacingMergeTree\n"
        "SETTTING force_select_final=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ForceSelectFinalGlobal = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinalGlobal",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]\n"
        "on all MergeTree tables [SELECT] queries when the setting is value is set to `1` globally. [ClickHouse] should silently\n"
        "ignore it if option unavailable to current type of engine.\n"
        "\n"
        "Config example,\n"
        "\n"
        "```sql\n"
        "<clickhouse>\n"
        "    <merge_tree>\n"
        "        <force_select_final>1</force_select_final>\n"
        "    </merge_tree>\n"
        "</clickhouse>\n"
        "\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.2",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupported = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupported",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL not support `force_select_final` table engine setting and silently ignore it for any MergeTree table\n"
        "engine that doesn't support [FINAL modifier] clause.\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.2.3",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting_IgnoreForceSelectFinal = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting.IgnoreForceSelectFinal",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `ignore_force_select_final` [SELECT] query setting to disable automatic [FINAL modifier]\n"
        "if the table has `force_select_final` setting set to `1`.\n"
        "\n"
        "For example,\n"
        "\n"
        "```sql\n"
        "SELECT * FROM table; -- actually does SELECT * FROM table FINAL if SETTTING force_select_final=1\n"
        "SELECT * FROM table SETTINGS ignore_force_select_final=1; -- 0 by default, 1 - means ignore force_select_final\n"
        " from merge tree.\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.3.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatic [FINAL modifier] for the following [MergeTree] table engines variants:\n"
        "\n"
        "* [ReplacingMergeTree]\n"
        "* [CollapsingMergeTree]\n"
        "* [VersionedCollapsingMergeTree]\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.4.1.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatic [FINAL modifier] for the following replicated \n"
        "[ReplicatedMergeTree](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication) \n"
        "table engines variants:\n"
        "\n"
        "* ReplicatedReplacingMergeTree\n"
        "* ReplicatedCollapsingMergeTree\n"
        "* ReplicatedVersionedCollapsingMergeTree\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.4.2.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the following table engines over tables that have automatic [FINAL modifier] clause enabled:\n"
        "\n"
        "* [View](https://clickhouse.com/docs/en/engines/table-engines/special/view)\n"
        "* [Buffer](https://clickhouse.com/docs/en/engines/table-engines/special/buffer)\n"
        "* [Distributed](https://clickhouse.com/docs/en/engines/table-engines/special/distributed)\n"
        "* [MaterializedView](https://clickhouse.com/docs/en/engines/table-engines/special/materializedview)\n"
        "\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.4.3.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatic [FINAL modifier] for any type of [SELECT] queries.\n"
        "\n"
        "```sql\n"
        "[WITH expr_list|(subquery)]\n"
        "SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list\n"
        "[FROM [db.]table | (subquery) | table_function] [FINAL]\n"
        "[SAMPLE sample_coeff]\n"
        "[ARRAY JOIN ...]\n"
        "[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)\n"
        "[PREWHERE expr]\n"
        "[WHERE expr]\n"
        "[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]\n"
        "[HAVING expr]\n"
        "[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]\n"
        "[LIMIT [offset_value, ]n BY columns]\n"
        "[LIMIT [n, ]m] [WITH TIES]\n"
        "[SETTINGS ...]\n"
        "[UNION  ...]\n"
        "[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]\n"
        "[FORMAT format]\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="5.5.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support applying [FINAL modifier] in any subquery that reads from a table that\n"
        "has automatic [FINAL modifier] enabled.\n"
        "\n"
        "For example,\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.5.2.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support applying [FINAL modifier] for any table in [JOIN] clause for which\n"
        "the automatic [FINAL modifier] is enabled.\n"
        "\n"
        "* INNER JOIN\n"
        "* LEFT OUTER JOIN\n"
        "* RIGHT OUTER JOIN\n"
        "* FULL OUTER JOIN\n"
        "* CROSS JOIN\n"
        "* LEFT SEMI JOIN and RIGHT SEMI JOIN\n"
        "* LEFT ANTI JOIN and RIGHT ANTI JOIN\n"
        "* LEFT ANY JOIN, RIGHT ANY JOIN and INNER ANY JOIN\n"
        "* ASOF JOIN and LEFT ASOF JOIN\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "select count() from lhs inner join rhs on lhs.x = rhs.x;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.5.3.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support applying [FINAL modifier] for any table in [UNION] clause for which\n"
        "the automatic [FINAL modifier] is enabled.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.5.4.1",
)

RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With = Requirement(
    name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support applying [FINAL modifier] for any table in subquery inside the [WITH] clause for which\n"
        "the automatic [FINAL modifier] is enabled.\n"
        "\n"
        "For example,\n"
        "```sql\n"
        "\n"
        "```\n"
        "\n"
        "[SRS]: #srs\n"
        "[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n"
        "[JOIN]: https://clickhouse.com/docs/en/sql-reference/statements/select/join\n"
        "[UNION]: https://clickhouse.com/docs/en/sql-reference/statements/select/union\n"
        "[WITH]: https://clickhouse.com/docs/en/sql-reference/statements/select/with\n"
        "[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/\n"
        "[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree\n"
        "[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree\n"
        "[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree\n"
        "[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
    ),
    link=None,
    level=4,
    num="5.5.5.1",
)

SRS032_ClickHouse_Automatic_Final_Modifier_For_Select_Queries = Specification(
    name="SRS032 ClickHouse Automatic Final Modifier For Select Queries",
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
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier", level=2, num="5.1"
        ),
        Heading(name="Table Engine Setting", level=2, num="5.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinal",
            level=3,
            num="5.2.1",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinalGlobal",
            level=3,
            num="5.2.2",
        ),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupported",
            level=3,
            num="5.2.3",
        ),
        Heading(name="Select Query Setting", level=2, num="5.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting.IgnoreForceSelectFinal",
            level=3,
            num="5.3.1",
        ),
        Heading(name="Supported Table Engines", level=2, num="5.4"),
        Heading(name="MergeTree", level=3, num="5.4.1"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree",
            level=4,
            num="5.4.1.1",
        ),
        Heading(name="ReplicatedMergeTree", level=3, num="5.4.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree",
            level=4,
            num="5.4.2.1",
        ),
        Heading(name="EnginesOverOtherEngines", level=3, num="5.4.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines",
            level=4,
            num="5.4.3.1",
        ),
        Heading(name="Select Queries", level=2, num="5.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries",
            level=3,
            num="5.5.1",
        ),
        Heading(name="Subquery", level=3, num="5.5.2"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery",
            level=4,
            num="5.5.2.1",
        ),
        Heading(name="JOIN", level=3, num="5.5.3"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join",
            level=4,
            num="5.5.3.1",
        ),
        Heading(name="UNION", level=3, num="5.5.4"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union",
            level=4,
            num="5.5.4.1",
        ),
        Heading(name="WITH ", level=3, num="5.5.5"),
        Heading(
            name="RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With",
            level=4,
            num="5.5.5.1",
        ),
    ),
    requirements=(
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ForceSelectFinal,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSetting_ForceSelectFinalGlobal,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_TableEngineSettingNotSupported,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQuerySetting_IgnoreForceSelectFinal,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_MergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_ReplicatedMergeTree,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SupportedTableEngines_EnginesOverOtherEngines,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Subquery,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Join,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_Union,
        RQ_SRS_032_ClickHouse_AutomaticFinalModifier_SelectQueries_With,
    ),
    content="""
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
    * 5.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinal](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingforceselectfinal)
    * 5.2.2 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinalGlobal](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingforceselectfinalglobal)
    * 5.2.3 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupported](#rqsrs-032clickhouseautomaticfinalmodifiertableenginesettingnotsupported)
  * 5.3 [Select Query Setting](#select-query-setting)
    * 5.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting.IgnoreForceSelectFinal](#rqsrs-032clickhouseautomaticfinalmodifierselectquerysettingignoreforceselectfinal)
  * 5.4 [Supported Table Engines](#supported-table-engines)
    * 5.4.1 [MergeTree](#mergetree)
      * 5.4.1.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.MergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesmergetree)
    * 5.4.2 [ReplicatedMergeTree](#replicatedmergetree)
      * 5.4.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.ReplicatedMergeTree](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesreplicatedmergetree)
    * 5.4.3 [EnginesOverOtherEngines](#enginesoverotherengines)
      * 5.4.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SupportedTableEngines.EnginesOverOtherEngines](#rqsrs-032clickhouseautomaticfinalmodifiersupportedtableenginesenginesoverotherengines)
  * 5.5 [Select Queries](#select-queries)
    * 5.5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries](#rqsrs-032clickhouseautomaticfinalmodifierselectqueries)
    * 5.5.2 [Subquery](#subquery)
      * 5.5.2.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Subquery](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriessubquery)
    * 5.5.3 [JOIN](#join)
      * 5.5.3.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Join](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesjoin)
    * 5.5.4 [UNION](#union)
      * 5.5.4.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.Union](#rqsrs-032clickhouseautomaticfinalmodifierselectqueriesunion)
    * 5.5.5 [WITH ](#with-)
      * 5.5.5.1 [RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQueries.With](#rqsrs-032clickhouseautomaticfinalmodifierselectquerieswith)

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

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinal
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]
on all [SELECT] queries when the setting is value is set to `1`.

For example,

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING force_select_final=1
```

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSetting.ForceSelectFinalGlobal
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `force_select_final` table engine setting to enable automatic [FINAL modifier]
on all MergeTree tables [SELECT] queries when the setting is value is set to `1` globally. [ClickHouse] should silently
ignore it if option unavailable to current type of engine.

Config example,

```sql
<clickhouse>
    <merge_tree>
        <force_select_final>1</force_select_final>
    </merge_tree>
</clickhouse>

```

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.TableEngineSettingNotSupported
version: 1.0 priority: 1.0

[ClickHouse] SHALL not support `force_select_final` table engine setting and silently ignore it for any MergeTree table
engine that doesn't support [FINAL modifier] clause.

### Select Query Setting

#### RQ.SRS-032.ClickHouse.AutomaticFinalModifier.SelectQuerySetting.IgnoreForceSelectFinal
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `ignore_force_select_final` [SELECT] query setting to disable automatic [FINAL modifier]
if the table has `force_select_final` setting set to `1`.

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
[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree
[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree
[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier
[ClickHouse]: https://clickhouse.com
""",
)
