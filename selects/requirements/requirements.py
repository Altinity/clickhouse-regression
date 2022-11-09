# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_033_ClickHouse_SelectFinal_FinalModifier = Requirement(
    name="RQ.SRS-033.ClickHouse.SelectFinal.FinalModifier",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL fully merge the data before returning the result and thus performs all data\n"
        "transformations that happen during merges for the given table engine.\n"
        "(for example, to discard duplicates)\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.0.1",
)

RQ_SRS_033_ClickHouse_SelectFinal = Requirement(
    name="RQ.SRS-033.ClickHouse.SelectFinal",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support adding [FINAL modifier] clause to all [SELECT] queries\n"
        "for all table engines that support it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_SRS_033_ClickHouse_SelectFinal_ConfigSetting = Requirement(
    name="RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `apply_final_by_default` table config setting to enable [SELECT FINAL]\n"
        "when the setting is set to `1`.\n"
        "\n"
        "For example:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE table (...)\n"
        "Engine=ReplacingMergeTree\n"
        "SETTTING apply_final_by_default=1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.1",
)

RQ_SRS_033_ClickHouse_SelectFinal_SelectAutoFinalSetting = Requirement(
    name="RQ.SRS-033.ClickHouse.SelectFinal.SelectAutoFinalSetting",
    version="1.0",
    priority="1.0",
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `auto_final` table config setting to disable [SELECT FINAL]\n"
        "when the setting is set to `0`.\n"
        "\n"
        "```sql\n"
        "SELECT * FROM table; -- actually does SELECT * FROM table FINAL\n"
        "SELECT * FROM table SETTINGS auto_final=0; -- 1 by default, 0 - means ignore apply_final_by_default from merge tree.\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=3,
    num="4.2.2",
)

RQ_SRS_033_ClickHouse_SelectFinal_SupportedTableEngines = Requirement(
    name="RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support automatic [SELECT FINAL] for the following [MergeTree] table engines variants:\n"
        "\n"
        "* [MergeTree]\n"
        "* [ReplacingMergeTree]\n"
        "* [CollapsingMergeTree]\n"
        "* [VersionedCollapsingMergeTree]\n"
        "\n"
        "\n"
        "\n"
        "[SRS]: #srs\n"
        "[SELECT]: https://clickhouse.com/docs/en/sql-reference/statements/select/\n"
        "[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/\n"
        "[ReplacingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree\n"
        "[CollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/collapsingmergetree\n"
        "[VersionedCollapsingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/versionedcollapsingmergetree\n"
        "[FINAL modifier]: https://clickhouse.com/docs/en/sql-reference/statements/select/from/#final-modifier\n"
        "[SELECT FINAL]: #select-final\n"
        "[ClickHouse]: https://clickhouse.com\n"
        "\n"
    ),
    link=None,
    level=4,
    num="4.3.1.1",
)

SRS033_ClickHouse_Automatic_Final_Modifier_For_Select_Queries = Specification(
    name="SRS033 ClickHouse Automatic Final Modifier For Select Queries",
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
        Heading(name="Related Resources", level=1, num="2"),
        Heading(name="Terminology", level=1, num="3"),
        Heading(name="SRS", level=2, num="3.1"),
        Heading(name="Select Final", level=2, num="3.2"),
        Heading(name="FinalModifier", level=2, num="3.3"),
        Heading(
            name="RQ.SRS-033.ClickHouse.SelectFinal.FinalModifier",
            level=4,
            num="3.3.0.1",
        ),
        Heading(name="Requirements", level=1, num="4"),
        Heading(name="RQ.SRS-033.ClickHouse.SelectFinal", level=2, num="4.1"),
        Heading(name="Config Setting", level=2, num="4.2"),
        Heading(
            name="RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting", level=3, num="4.2.1"
        ),
        Heading(
            name="RQ.SRS-033.ClickHouse.SelectFinal.SelectAutoFinalSetting",
            level=3,
            num="4.2.2",
        ),
        Heading(name="Supported Table Engines", level=2, num="4.3"),
        Heading(name="MergeTree", level=3, num="4.3.1"),
        Heading(
            name="RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines",
            level=4,
            num="4.3.1.1",
        ),
    ),
    requirements=(
        RQ_SRS_033_ClickHouse_SelectFinal_FinalModifier,
        RQ_SRS_033_ClickHouse_SelectFinal,
        RQ_SRS_033_ClickHouse_SelectFinal_ConfigSetting,
        RQ_SRS_033_ClickHouse_SelectFinal_SelectAutoFinalSetting,
        RQ_SRS_033_ClickHouse_SelectFinal_SupportedTableEngines,
    ),
    content="""
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

## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/40945

## Terminology

### SRS

Software Requirements Specification

### Select Final

Automatic [FINAL Modifier] clause for [SELECT] queries.

### FinalModifier

##### RQ.SRS-033.ClickHouse.SelectFinal.FinalModifier
version: 1.0

[ClickHouse] SHALL fully merge the data before returning the result and thus performs all data
transformations that happen during merges for the given table engine.
(for example, to discard duplicates)

## Requirements

### RQ.SRS-033.ClickHouse.SelectFinal
version: 1.0

[ClickHouse] SHALL support adding [FINAL modifier] clause to all [SELECT] queries
for all table engines that support it.

### Config Setting

#### RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `apply_final_by_default` table config setting to enable [SELECT FINAL]
when the setting is set to `1`.

For example:

```sql
CREATE TABLE table (...)
Engine=ReplacingMergeTree
SETTTING apply_final_by_default=1
```

#### RQ.SRS-033.ClickHouse.SelectFinal.SelectAutoFinalSetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `auto_final` table config setting to disable [SELECT FINAL]
when the setting is set to `0`.

```sql
SELECT * FROM table; -- actually does SELECT * FROM table FINAL
SELECT * FROM table SETTINGS auto_final=0; -- 1 by default, 0 - means ignore apply_final_by_default from merge tree.
```

### Supported Table Engines

#### MergeTree

##### RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines
version: 1.0

[ClickHouse] SHALL support automatic [SELECT FINAL] for the following [MergeTree] table engines variants:

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
[SELECT FINAL]: #select-final
[ClickHouse]: https://clickhouse.com
""",
)
