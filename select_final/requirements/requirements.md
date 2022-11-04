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

