# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v1.9.220712.1163352.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_033_ClickHouse_SelectFinal = Requirement(
    name='RQ.SRS-033.ClickHouse.SelectFinal',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [auto FINAL ... SELECT]. Use case for this is \n'
        'migration from other databases and updates/deletes are mimicked by Collapsing/Replacing.\n'
        '\n'
        'Example:\n'
        '```sql\n'
        'CREATE TABLE table (... )\n'
        'Engine=ReplacingMergeTree\n'
        'SETTTING apply_final_by_default=1\n'
        '\n'
        'SELECT * FROM table; -- actually does SELECT * FROM table FINAL\n'
        '\n'
        'SELECT * FROM table SETTINGS auto_final=0; -- 1 by default, 0 - means ignore apply_final_by_default from merge tree.\n'
        '```\n'
        '\n'
    ),
    link=None,
    level=2,
    num='4.1'
)

RQ_SRS_033_ClickHouse_SelectFinal_ConfigSetting = Requirement(
    name='RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting',
    version='1.0',
    priority='1.0',
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support `apply_final_by_default` config setting to enable [auto FINAL ... SELECT].\n'
        '\n'
    ),
    link=None,
    level=3,
    num='4.2.1'
)

RQ_SRS_033_ClickHouse_SelectFinal_SupportedTableEngines_MergeTree = Requirement(
    name='RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines.MergeTree',
    version='1.0',
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        '[ClickHouse] SHALL support [auto FINAL ... SELECT] for current MergeTree table engines variants:\n'
        '\n'
        '* MergeTree\n'
        '* ReplacingMergeTree\n'
        '* CollapsingMergeTree\n'
        '* VersionedCollapsingMergeTree\n'
        '\n'
        '[SRS]: #srs\n'
        '[auto FINAL ... SELECT]: #auto-final-select\n'
        '[ClickHouse]: https://clickhouse.com\n'
        '\n'
    ),
    link=None,
    level=4,
    num='4.3.1.1'
)

SRS033_ClickHouse_Select_Final = Specification(
    name='SRS033 ClickHouse Select Final',
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
        Heading(name='Auto Final Select', level=2, num='3.2'),
        Heading(name='Requirements', level=1, num='4'),
        Heading(name='RQ.SRS-033.ClickHouse.SelectFinal', level=2, num='4.1'),
        Heading(name='Config Setting', level=2, num='4.2'),
        Heading(name='RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting', level=3, num='4.2.1'),
        Heading(name='Supported Table Engines', level=2, num='4.3'),
        Heading(name='Merge Tree', level=3, num='4.3.1'),
        Heading(name='RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines.MergeTree', level=4, num='4.3.1.1'),
        ),
    requirements=(
        RQ_SRS_033_ClickHouse_SelectFinal,
        RQ_SRS_033_ClickHouse_SelectFinal_ConfigSetting,
        RQ_SRS_033_ClickHouse_SelectFinal_SupportedTableEngines_MergeTree,
        ),
    content='''
# SRS033 ClickHouse Select Final
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Related Resources](#related-resources)
* 3 [Terminology](#terminology)
  * 3.1 [SRS](#srs)
  * 3.2 [Auto Final Select](#auto-final-select)
* 4 [Requirements](#requirements)
  * 4.1 [RQ.SRS-033.ClickHouse.SelectFinal](#rqsrs-033clickhouseselectfinal)
  * 4.2 [Config Setting](#config-setting)
    * 4.2.1 [RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting](#rqsrs-033clickhouseselectfinalconfigsetting)
  * 4.3 [Supported Table Engines](#supported-table-engines)
    * 4.3.1 [Merge Tree](#merge-tree)
      * 4.3.1.1 [RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines.MergeTree](#rqsrs-033clickhouseselectfinalsupportedtableenginesmergetree)



## Introduction

This software requirements specification covers requirements related to [ClickHouse] 
auto "SELECT ... FINAL" query support.

## Related Resources

* https://github.com/ClickHouse/ClickHouse/pull/40945

## Terminology

### SRS

Software Requirements Specification

### Auto Final Select

SELECT queries without adding FINAL to all the existing queries

## Requirements

### RQ.SRS-033.ClickHouse.SelectFinal
version: 1.0

[ClickHouse] SHALL support [auto FINAL ... SELECT]. Use case for this is 
migration from other databases and updates/deletes are mimicked by Collapsing/Replacing.

Example:
```sql
CREATE TABLE table (... )
Engine=ReplacingMergeTree
SETTTING apply_final_by_default=1

SELECT * FROM table; -- actually does SELECT * FROM table FINAL

SELECT * FROM table SETTINGS auto_final=0; -- 1 by default, 0 - means ignore apply_final_by_default from merge tree.
```

### Config Setting

#### RQ.SRS-033.ClickHouse.SelectFinal.ConfigSetting
version: 1.0 priority: 1.0

[ClickHouse] SHALL support `apply_final_by_default` config setting to enable [auto FINAL ... SELECT].

### Supported Table Engines

#### Merge Tree

##### RQ.SRS-033.ClickHouse.SelectFinal.SupportedTableEngines.MergeTree
version: 1.0

[ClickHouse] SHALL support [auto FINAL ... SELECT] for current MergeTree table engines variants:

* MergeTree
* ReplacingMergeTree
* CollapsingMergeTree
* VersionedCollapsingMergeTree

[SRS]: #srs
[auto FINAL ... SELECT]: #auto-final-select
[ClickHouse]: https://clickhouse.com
'''
)
