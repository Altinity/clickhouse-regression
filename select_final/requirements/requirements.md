# SRS033 ClickHouse Automatic Final Modifier For Select Queries
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

