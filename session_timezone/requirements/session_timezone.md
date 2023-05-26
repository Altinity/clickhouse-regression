# QA-SRS037 ClickHouse Session Timezone

# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Feature Diagram](#feature-diagram)
* 3 [Related Resources](#related-resources)
* 4 [Terminology](#terminology)
  * 4.1 [SRS](#srs)
* 5 [Requirements](#requirements)
  * 5.1 [RQ.SRS-037.ClickHouse.SessionTimezone](#rqsrs-037clickhousesessiontimezone)

## Introduction

This software requirements specification covers requirements related to [ClickHouse] support of changing
default timezone with [session_timezone] setting.

## Feature Diagram

Test feature diagram.

```mermaid
flowchart TB;

  classDef yellow fill:#ffff32,stroke:#323,stroke-width:4px,color:black;
  classDef yellow2 fill:#ffff32,stroke:#323,stroke-width:4px,color:red;
  classDef green fill:#00ff32,stroke:#323,stroke-width:4px,color:black;
  classDef red fill:red,stroke:#323,stroke-width:4px,color:black;
  classDef blue fill:blue,stroke:#323,stroke-width:4px,color:white;
  
  subgraph O["'Session Timezone' Test Feature Diagram"]


    

  end
```
## Related Resources

**Pull Requests**

* https://github.com/ClickHouse/ClickHouse/pull/44149

## Terminology

### SRS

Software Requirements Specification

## Requirements

### RQ.SRS-037.ClickHouse.SessionTimezone
version: 1.0

[ClickHouse] SHALL support `session_timezone` setting. If it specified, sets an implicit timezone
(instead of default [timezone].
All DateTime/DateTime64 values (and/or functions results) that have no explicit timezone 
specified are treated as having this timezone instead of default.
A value of `''` (empty string) configures the session timezone to the server default timezone.

Examples:
zvonand marked this conversation as resolved.

```sql
SELECT timeZone(), serverTimezone() FORMAT TSV
Europe/Berlin	Europe/Berlin
```

```sql
SELECT timeZone(), serverTimezone() SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT TSV
Asia/Novosibirsk	Europe/Berlin
```

```sql
SELECT toDateTime64(toDateTime64('1999-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') SETTINGS session_timezone = 'America/Denver' FORMAT TSV
1999-12-13 07:23:23.123
```

:::warning
The way this setting affects parsing of Date or DateTime types may seem non-obvious, see example and explanation below:
:::

```sql
CREATE TABLE test_tz (`d` DateTime('UTC')) ENGINE = Memory AS SELECT toDateTime('2000-01-01 00:00:00', 'UTC');
SELECT *, timezone() FROM test_tz WHERE d = toDateTime('2000-01-01 00:00:00') SETTINGS session_timezone = 'Asia/Novosibirsk'
0 rows in set.
SELECT *, timezone() FROM test_tz WHERE d = '2000-01-01 00:00:00' SETTINGS session_timezone = 'Asia/Novosibirsk'
┌───────────────────d─┬─timezone()───────┐
│ 2000-01-01 00:00:00 │ Asia/Novosibirsk │
└─────────────────────┴──────────────────┘
```

This happens due to different parsing pipelines:
  - `toDateTime('2000-01-01 00:00:00')` creates a new DateTime in a usual way, and thus `session_timezone` setting from query context is applied.
  - `2000-01-01 00:00:00` is parsed to a DateTime inheriting type of `d` column, including DateTime's time zone, and `session_timezone` has no impact on this value.

Possible values:

-    Any timezone name from `system.time_zones`, e.g. `Europe/Berlin`, `UTC` or `Zulu`

Default value: `''`.



[SRS]: #srs
[session_timezone]: https://github.com/ClickHouse/ClickHouse/pull/44149
[ClickHouse]: https://clickhouse.com
[timezone]:https://clickhouse.com/docs/en/operations/server-configuration-parameters/settings#server_configuration_parameters-timezone
